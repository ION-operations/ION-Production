/**
 * Agent Monitor
 * 
 * Monitors Cursor Background Agents via HTTP API (not CLI)
 * Integrates with bulletproof messaging for status updates
 */

import { MessageRouter } from '../messaging/router';
import { createEnvelope } from '../messaging/envelope';
import * as vscode from 'vscode';

export interface AgentRun {
    run_id: string;
    task_file: string;
    repo_path: string;
    branch?: string;
    max_runtime_hours?: number;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    created_at: number;
    started_at?: number;
    completed_at?: number;
    current_step?: number;
    total_steps?: number;
    last_command?: string;
    output?: string[];
    summary?: string; // API provides summary text
}

export interface AgentStatus {
    run_id: string;
    status: AgentRun['status'];
    current_step?: number;
    total_steps?: number;
    last_command?: string;
    output?: string[];
    exit_code?: number;
    summary?: {
        steps_completed: number;
        tests_passed?: number;
        files_changed?: number;
    };
}

export class AgentMonitor {
    private router: MessageRouter;
    private activeRuns: Map<string, AgentRun> = new Map();
    private statusIntervals: Map<string, NodeJS.Timeout> = new Map();
    private cursorApiKey: string | null = null;
    private cursorApiUrl: string = 'https://api.cursor.com/v0'; // Fixed: use /v0 (not /v1)
    private webhookUrl: string | null = null;

    constructor(
        router: MessageRouter,
        options: {
            cursorApiKey?: string;
            cursorApiUrl?: string;
            webhookUrl?: string;
        } = {}
    ) {
        this.router = router;
        this.cursorApiKey = options.cursorApiKey || null;
        this.cursorApiUrl = options.cursorApiUrl || 'https://api.cursor.com/v0'; // Fixed: use /v0 (not /v1)
        this.webhookUrl = options.webhookUrl || null;
    }

    /**
     * Smart agent start - automatically chooses Cloud API or CLI based on repoPath
     * 
     * - If repoPath is GitHub URL → Uses Cloud API
     * - If repoPath is local path → Uses CLI Agent
     * - Tries to detect GitHub URL from git remote if local path provided
     */
    async startAgentSmart(params: {
        prompt: string;
        repoPath: string;  // Can be GitHub URL or local path
        branch?: string;
        maxRuntimeHours?: number;
        taskFile?: string;  // Optional: for Cloud API
    }): Promise<{
        runId: string;
        method: 'cloud' | 'local';
    }> {
        const { repoPath, prompt, branch, maxRuntimeHours, taskFile } = params;

        // Check if it's already a GitHub URL
        if (repoPath.startsWith('https://github.com/')) {
            // Use Cloud API
            if (!this.cursorApiKey) {
                throw new Error('Cursor API key not configured. Required for Cloud Agents API.');
            }
            if (!taskFile) {
                throw new Error('taskFile required for Cloud Agents API');
            }
            
            const runId = await this.startAgent({
                taskFile,
                repoPath,  // GitHub URL
                branch,
                maxRuntimeHours
            });
            
            return {
                runId,
                method: 'cloud'
            };
        }

        // Try to get GitHub URL from git remote
        try {
            const githubUrl = await this.getGitHubUrl(repoPath);
            
            // Found GitHub URL - use Cloud API
            if (githubUrl.startsWith('https://github.com/')) {
                if (!this.cursorApiKey) {
                    // Fall back to CLI if no API key
                    const result = await this.startLocalAgent({
                        prompt,
                        repoPath
                    });
                    return {
                        runId: result.threadId,
                        method: 'local'
                    };
                }
                
                if (!taskFile) {
                    throw new Error('taskFile required for Cloud Agents API');
                }
                
                const runId = await this.startAgent({
                    taskFile,
                    repoPath: githubUrl,  // Use GitHub URL
                    branch,
                    maxRuntimeHours
                });
                
                return {
                    runId,
                    method: 'cloud'
                };
            }
        } catch (error) {
            // No GitHub URL found or error - use CLI
            console.log('No GitHub URL detected, using CLI agent:', error);
        }

        // Fall back to CLI Agent for local repos
        const result = await this.startLocalAgent({
            prompt,
            repoPath  // Local path
        });
        
        return {
            runId: result.threadId,
            method: 'local'
        };
    }

    /**
     * Start a background agent run
     * Uses Cursor Background Agent API (HTTP, not CLI)
     * 
     * ⚠️ IMPORTANT: This API requires GitHub repository URLs!
     * - The `source.repository` field MUST be a GitHub URL
     * - Local file paths like "C:\Users\...\project" will NOT work
     * - Use `startLocalAgent()` for local repositories instead
     */
    async startAgent(params: {
        taskFile: string;
        repoPath: string;  // ⚠️ Must be GitHub URL for Cloud API!
        branch?: string;
        maxRuntimeHours?: number;
    }): Promise<string> {
        const { taskFile, repoPath, branch, maxRuntimeHours } = params;

        if (!this.cursorApiKey) {
            throw new Error('Cursor API key not configured');
        }

        // Create run via Cursor Background Agent API
        // Endpoint: POST /v0/agents
        const response = await fetch(`${this.cursorApiUrl}/agents`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.cursorApiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: {
                    text: `Execute task from ${taskFile}`
                },
                source: {
                    repository: await this.getGitHubUrl(repoPath),
                    ref: branch || 'main'
                },
                target: {
                    branchName: branch || `agent/${Date.now()}`,
                    autoCreatePr: false
                },
                webhook: this.webhookUrl ? {
                    url: this.webhookUrl
                } : undefined
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: response.statusText }));
            throw new Error(`Failed to start agent: ${error.message || response.statusText}`);
        }

        const agentResponse = await response.json();
        // API returns: { id, name, status, source, target, createdAt }
        const run: AgentRun = {
            run_id: agentResponse.id,
            task_file: taskFile,
            repo_path: repoPath,
            branch: branch,
            status: this.mapStatus(agentResponse.status),
            created_at: new Date(agentResponse.createdAt).getTime()
        };
        this.activeRuns.set(run.run_id, run);

        // Send started event via bulletproof messaging
        await this.router.route(createEnvelope(
            'event',
            'agent.started',
            'ext->ui',
            {
                run_id: run.run_id,
                task_file: taskFile,
                branch: branch
            }
        ));

        // Start polling status
        this.startStatusPolling(run.run_id);

        return run.run_id;
    }

    /**
     * Stop an agent run
     */
    async stopAgent(runId: string): Promise<void> {
        if (!this.cursorApiKey) {
            throw new Error('Cursor API key not configured');
        }

        // Cancel run via Cursor Background Agent API
        // Endpoint: DELETE /v0/agents/{id}
        const response = await fetch(`${this.cursorApiUrl}/agents/${runId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${this.cursorApiKey}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`Failed to stop agent: ${error.message || response.statusText}`);
        }

        // Stop polling
        this.stopStatusPolling(runId);

        // Send stopped event
        await this.router.route(createEnvelope(
            'event',
            'agent.stopped',
            'ext->ui',
            { run_id: runId }
        ));

        this.activeRuns.delete(runId);
    }

    /**
     * Get agent status
     */
    async getAgentStatus(runId: string): Promise<AgentStatus | null> {
        if (!this.cursorApiKey) {
            return null;
        }

        try {
            // Endpoint: GET /v0/agents/{id}
            const response = await fetch(`${this.cursorApiUrl}/agents/${runId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.cursorApiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                return null;
            }

            const agentResponse = await response.json();
            // API returns: { id, name, status, source, target, summary, createdAt }
            const run: AgentRun = {
                run_id: agentResponse.id,
                task_file: '', // Not in API response
                repo_path: agentResponse.source?.repository || '',
                branch: agentResponse.target?.branchName,
                status: this.mapStatus(agentResponse.status),
                created_at: new Date(agentResponse.createdAt).getTime(),
                summary: agentResponse.summary
            };
            this.activeRuns.set(runId, run);

            return {
                run_id: run.run_id,
                status: run.status,
                current_step: run.current_step,
                total_steps: run.total_steps,
                last_command: run.last_command,
                output: run.output,
                summary: run.summary ? {
                    steps_completed: 0, // API doesn't provide this
                    tests_passed: 0,
                    files_changed: 0
                } : undefined
            };
        } catch (error) {
            console.error('Failed to get agent status:', error);
            return null;
        }
    }

    /**
     * Get all active runs
     */
    async getAllActiveRuns(): Promise<AgentRun[]> {
        return Array.from(this.activeRuns.values());
    }

    /**
     * Start polling status for a run
     */
    private startStatusPolling(runId: string): void {
        // Poll every 5 seconds
        const interval = setInterval(async () => {
            const status = await this.getAgentStatus(runId);
            
            if (!status) {
                // Run not found or error
                this.stopStatusPolling(runId);
                return;
            }

            // Send status update via bulletproof messaging
            await this.router.route(createEnvelope(
                'event',
                'agent.status',
                'ext->ui',
                status
            ));

            // Check if completed
            if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
                this.stopStatusPolling(runId);
                
                // Send completion event
                await this.router.route(createEnvelope(
                    'event',
                    'agent.complete',
                    'ext->ui',
                    {
                        run_id: runId,
                        status: status.status,
                        exit_code: status.exit_code,
                        summary: status.summary
                    }
                ));
            }
        }, 5000);

        this.statusIntervals.set(runId, interval);
    }

    /**
     * Stop polling status for a run
     */
    private stopStatusPolling(runId: string): void {
        const interval = this.statusIntervals.get(runId);
        if (interval) {
            clearInterval(interval);
            this.statusIntervals.delete(runId);
        }
    }

    /**
     * Handle webhook event from Cursor Background Agent API
     */
    async handleWebhookEvent(event: any): Promise<void> {
        const { run_id, type, data } = event;

        switch (type) {
            case 'agent.output':
                // Stream output
                await this.router.route(createEnvelope(
                    'event',
                    'agent.output',
                    'ext->ui',
                    {
                        run_id,
                        stream: data.stream || 'stdout',
                        data: data.output
                    }
                ));
                break;

            case 'agent.checkpoint':
                // Checkpoint created
                await this.router.route(createEnvelope(
                    'event',
                    'agent.checkpoint',
                    'ext->ui',
                    {
                        run_id,
                        checkpoint: data.checkpoint
                    }
                ));
                break;

            case 'agent.status':
                // Status update
                await this.router.route(createEnvelope(
                    'event',
                    'agent.status',
                    'ext->ui',
                    {
                        run_id,
                        status: data.status,
                        current_step: data.current_step,
                        total_steps: data.total_steps
                    }
                ));
                break;

            case 'agent.complete':
                // Agent completed
                this.stopStatusPolling(run_id);
                await this.router.route(createEnvelope(
                    'event',
                    'agent.complete',
                    'ext->ui',
                    {
                        run_id,
                        status: data.status,
                        exit_code: data.exit_code,
                        summary: data.summary
                    }
                ));
                break;

            case 'agent.error':
                // Agent error
                await this.router.route(createEnvelope(
                    'event',
                    'agent.error',
                    'ext->ui',
                    {
                        run_id,
                        error: data.error
                    }
                ));
                break;
        }
    }

    /**
     * Force checkpoint
     */
    async checkpoint(runId: string): Promise<void> {
        if (!this.cursorApiKey) {
            throw new Error('Cursor API key not configured');
        }

        // Note: Checkpoint endpoint not in official API docs - may need to use followup instead
        // Endpoint: POST /v0/agents/{id}/followup (for now)
        const response = await fetch(`${this.cursorApiUrl}/agents/${runId}/followup`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.cursorApiKey}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: {
                    text: 'Create checkpoint now'
                }
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`Failed to checkpoint: ${error.message || response.statusText}`);
        }
    }

    /**
     * Get metrics
     */
    async getMetrics(): Promise<{
        active_runs: number;
        runs: Array<{
            run_id: string;
            status: string;
            runtime_hours: number;
            steps_completed: number;
        }>;
    }> {
        const runs = await this.getAllActiveRuns();
        
        return {
            active_runs: runs.filter(r => r.status === 'running').length,
            runs: runs.map(r => ({
                run_id: r.run_id,
                status: r.status,
                runtime_hours: r.started_at 
                    ? (Date.now() - r.started_at) / (1000 * 60 * 60)
                    : 0,
                steps_completed: r.current_step || 0
            }))
        };
    }

    /**
     * Start a LOCAL agent run (alternative to Cloud API)
     * Uses cursor-agent CLI which works with local repositories
     * 
     * ✅ Use this for local repos that aren't on GitHub
     * ✅ Runs on your machine, not Cursor's servers
     */
    async startLocalAgent(params: {
        prompt: string;
        repoPath: string;  // ✅ Local path works here!
        options?: {
            outputFormat?: 'json' | 'text';
            timeout?: number;
        };
    }): Promise<{
        threadId: string;
        output: string;
    }> {
        const { execSync } = require('child_process');
        const { prompt, repoPath, options = {} } = params;
        const { outputFormat = 'json', timeout = 300000 } = options;

        try {
            const command = `cursor-agent --print --output-format ${outputFormat} "${prompt}"`;
            const output = execSync(command, {
                cwd: repoPath,
                encoding: 'utf-8',
                timeout: timeout,
                maxBuffer: 10 * 1024 * 1024 // 10MB
            });

            // Parse output if JSON
            if (outputFormat === 'json') {
                return {
                    threadId: `local-${Date.now()}`,
                    output: JSON.parse(output)
                };
            }

            return {
                threadId: `local-${Date.now()}`,
                output: output
            };
        } catch (error: any) {
            throw new Error(`Failed to start local agent: ${error.message}`);
        }
    }

    /**
     * Get GitHub URL from local repo path
     * For now, assumes repo is already a GitHub URL or needs to be configured
     */
    private async getGitHubUrl(repoPath: string): Promise<string> {
        // If already a GitHub URL, return it
        if (repoPath.startsWith('https://github.com/')) {
            return repoPath;
        }
        
        // Try to get remote URL from git config
        try {
            const { execSync } = require('child_process');
            const remoteUrl = execSync('git config --get remote.origin.url', { 
                cwd: repoPath,
                encoding: 'utf-8'
            }).trim();
            
            // Convert git@github.com:user/repo.git to https://github.com/user/repo
            if (remoteUrl.startsWith('git@github.com:')) {
                return remoteUrl.replace('git@github.com:', 'https://github.com/').replace('.git', '');
            }
            
            return remoteUrl;
        } catch (error) {
            // Fallback: assume repo path should be GitHub URL
            throw new Error(`Cannot determine GitHub URL for ${repoPath}. Please provide full GitHub repository URL.`);
        }
    }

    /**
     * Map API status to our internal status
     */
    private mapStatus(apiStatus: string): AgentRun['status'] {
        // API statuses: CREATING, RUNNING, FINISHED, etc.
        const statusMap: Record<string, AgentRun['status']> = {
            'CREATING': 'pending',
            'RUNNING': 'running',
            'FINISHED': 'completed',
            'FAILED': 'failed',
            'CANCELLED': 'cancelled'
        };
        
        return statusMap[apiStatus] || 'pending';
    }

    /**
     * Cleanup
     */
    dispose(): void {
        // Stop all polling
        for (const [runId, interval] of this.statusIntervals.entries()) {
            clearInterval(interval);
        }
        this.statusIntervals.clear();
        this.activeRuns.clear();
    }
}

