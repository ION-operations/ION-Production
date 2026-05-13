/**
 * ═══════════════════════════════════════════════════════════════
 * GitHub Context Service
 * 
 * Fetches repository file trees and content from GitHub's API
 * for injection into the AI provider context pipeline.
 * 
 * Works without authentication for public repos.
 * Supports optional GitHub PAT for private repos via env var.
 * ═══════════════════════════════════════════════════════════════
 */

// ─── Types ───

export interface GitHubRepo {
    owner: string;
    repo: string;
    branch: string;
    url: string;
}

export interface GitHubTreeItem {
    path: string;
    type: 'blob' | 'tree';
    size: number;
    sha: string;
}

export interface GitHubFileContent {
    path: string;
    content: string;
    size: number;
    encoding: string;
    sha: string;
}

export interface RepoContext {
    repo: GitHubRepo;
    files: { path: string; content: string; tokens: number; sizeBytes: number }[];
    totalTokens: number;
    totalBytes: number;
}

// ─── Config ───

const GITHUB_API = 'https://api.github.com';
const MAX_FILE_SIZE = 500_000; // 500KB max per file
const CODE_EXTENSIONS = new Set([
    'ts', 'tsx', 'js', 'jsx', 'py', 'rs', 'go', 'java', 'c', 'cpp', 'h', 'hpp',
    'cs', 'rb', 'php', 'swift', 'kt', 'scala', 'r', 'sql', 'sh', 'bash', 'zsh',
    'md', 'txt', 'json', 'yaml', 'yml', 'toml', 'cfg', 'ini', 'env',
    'css', 'scss', 'less', 'html', 'xml', 'svg',
    'dockerfile', 'makefile', 'cmake',
]);

// ─── Helpers ───

function getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'AIM-OS-JOC',
    };
    // Optional PAT for private repos (set in env)
    const token = typeof window !== 'undefined'
        ? localStorage.getItem('github_pat')
        : null;
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

/** Parse a GitHub URL into owner/repo/branch */
export function parseGitHubUrl(url: string): GitHubRepo | null {
    // Handle: https://github.com/owner/repo
    // Handle: https://github.com/owner/repo/tree/branch
    // Handle: owner/repo shorthand
    const patterns = [
        /github\.com\/([^/]+)\/([^/]+?)(?:\.git)?(?:\/tree\/([^/]+))?$/,
        /^([^/]+)\/([^/]+)$/,
    ];

    for (const pattern of patterns) {
        const match = url.trim().match(pattern);
        if (match) {
            return {
                owner: match[1],
                repo: match[2],
                branch: match[3] || 'main',
                url: `https://github.com/${match[1]}/${match[2]}`,
            };
        }
    }
    return null;
}

// ─── API Methods ───

/** Fetch the full file tree of a repository (recursive) */
export async function getRepoTree(repo: GitHubRepo): Promise<GitHubTreeItem[]> {
    const response = await fetch(
        `${GITHUB_API}/repos/${repo.owner}/${repo.repo}/git/trees/${repo.branch}?recursive=1`,
        { headers: getHeaders() }
    );

    if (!response.ok) {
        if (response.status === 404) {
            // Try 'master' branch as fallback
            if (repo.branch === 'main') {
                const fallback = { ...repo, branch: 'master' };
                const retry = await fetch(
                    `${GITHUB_API}/repos/${fallback.owner}/${fallback.repo}/git/trees/master?recursive=1`,
                    { headers: getHeaders() }
                );
                if (retry.ok) {
                    const data = await retry.json();
                    return (data.tree || []).filter((item: any) => item.type === 'blob');
                }
            }
            throw new Error(`Repository not found: ${repo.owner}/${repo.repo}`);
        }
        throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return (data.tree || [])
        .filter((item: any) => item.type === 'blob')
        .map((item: any) => ({
            path: item.path,
            type: item.type,
            size: item.size || 0,
            sha: item.sha,
        }));
}

/** Fetch the content of a single file */
export async function getFileContent(repo: GitHubRepo, path: string): Promise<GitHubFileContent> {
    const response = await fetch(
        `${GITHUB_API}/repos/${repo.owner}/${repo.repo}/contents/${path}?ref=${repo.branch}`,
        { headers: getHeaders() }
    );

    if (!response.ok) {
        throw new Error(`Failed to fetch ${path}: ${response.status}`);
    }

    const data = await response.json();

    // GitHub returns base64-encoded content
    const content = data.encoding === 'base64'
        ? atob(data.content.replace(/\n/g, ''))
        : data.content;

    return {
        path: data.path,
        content,
        size: data.size,
        encoding: data.encoding,
        sha: data.sha,
    };
}

/** Filter tree to code-relevant files only */
export function filterCodeFiles(tree: GitHubTreeItem[]): GitHubTreeItem[] {
    return tree.filter(item => {
        // Skip files that are too large
        if (item.size > MAX_FILE_SIZE) return false;

        // Skip common non-code paths
        const lowerPath = item.path.toLowerCase();
        if (lowerPath.includes('node_modules/')) return false;
        if (lowerPath.includes('.git/')) return false;
        if (lowerPath.includes('dist/')) return false;
        if (lowerPath.includes('build/')) return false;
        if (lowerPath.includes('vendor/')) return false;
        if (lowerPath.includes('.min.')) return false;
        if (lowerPath.includes('package-lock.json')) return false;
        if (lowerPath.includes('yarn.lock')) return false;
        if (lowerPath.includes('pnpm-lock.yaml')) return false;

        // Check extension
        const ext = item.path.split('.').pop()?.toLowerCase() || '';
        const basename = item.path.split('/').pop()?.toLowerCase() || '';

        // Allow extensionless config files
        if (['dockerfile', 'makefile', '.gitignore', '.env'].includes(basename)) return true;

        return CODE_EXTENSIONS.has(ext);
    });
}

/** Fetch multiple files and build a context bundle */
export async function fetchRepoContext(
    repo: GitHubRepo,
    filePaths: string[],
    maxTotalTokens: number = 50000
): Promise<RepoContext> {
    const files: RepoContext['files'] = [];
    let totalTokens = 0;

    for (const path of filePaths) {
        if (totalTokens >= maxTotalTokens) break;

        try {
            const file = await getFileContent(repo, path);
            const tokens = Math.ceil(file.content.length / 4);

            // Skip if this file would exceed token budget
            if (totalTokens + tokens > maxTotalTokens) continue;

            files.push({
                path: file.path,
                content: file.content,
                tokens,
                sizeBytes: file.size,
            });
            totalTokens += tokens;
        } catch (err) {
            console.warn(`[GitHub] Skipping ${path}:`, err);
        }
    }

    return {
        repo,
        files,
        totalTokens,
        totalBytes: files.reduce((sum, f) => sum + f.sizeBytes, 0),
    };
}

/** Quick utility: fetch repo structure summary */
export async function getRepoSummary(repoUrl: string): Promise<{
    repo: GitHubRepo;
    totalFiles: number;
    codeFiles: number;
    languages: Record<string, number>;
    topDirectories: string[];
}> {
    const repo = parseGitHubUrl(repoUrl);
    if (!repo) throw new Error(`Invalid GitHub URL: ${repoUrl}`);

    const tree = await getRepoTree(repo);
    const codeFiles = filterCodeFiles(tree);

    // Count languages by extension
    const languages: Record<string, number> = {};
    for (const file of codeFiles) {
        const ext = file.path.split('.').pop()?.toLowerCase() || 'other';
        languages[ext] = (languages[ext] || 0) + 1;
    }

    // Get top-level directories
    const dirs = new Set<string>();
    for (const file of tree) {
        const parts = file.path.split('/');
        if (parts.length > 1) dirs.add(parts[0]);
    }

    return {
        repo,
        totalFiles: tree.length,
        codeFiles: codeFiles.length,
        languages,
        topDirectories: Array.from(dirs).sort(),
    };
}
