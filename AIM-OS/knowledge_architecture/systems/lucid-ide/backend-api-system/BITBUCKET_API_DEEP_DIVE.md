---
id: "bitbucket_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Bitbucket API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Bitbucket API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["bitbucket", "git", "code", "api-integration", "deep-dive"]
---

# Bitbucket API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Bitbucket API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://developer.atlassian.com/cloud/bitbucket/rest

---

## 🎯 **BITBUCKET API OVERVIEW**

Bitbucket provides Git and repository management APIs:
- **Repositories** - Repository management
- **Pull Requests** - Pull request management
- **Commits** - Commit history
- **Branches** - Branch management
- **Files** - File operations
- **Issues** - Issue tracking
- **Pipelines** - CI/CD pipelines
- **Webhooks** - Webhook management
- **Users** - User management
- **Workspaces** - Workspace management

**Key Features:**
- Comprehensive Git operations
- CI/CD pipeline integration
- OAuth 2.0 authentication
- Webhooks support
- Atlassian integration

---

## 🔐 **AUTHENTICATION**

**Method:** OAuth 2.0 or App Password

**Header (OAuth 2.0):**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Header (App Password):**
```
Authorization: Basic base64(username:app_password)
```

**OAuth 2.0 Flow:**
1. Register OAuth consumer
2. Get authorization → Get access token
3. Use access token for API calls

**Base URL:**
```
https://api.bitbucket.org/2.0
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Get Repository**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}`

**Purpose:** Get repository information

**Response:**

```typescript
interface BitbucketRepository {
  scm: 'git'
  website: string | null
  has_wiki: boolean
  uuid: string
  links: {
    watchers: { href: string }
    branches: { href: string }
    tags: { href: string }
    commits: { href: string }
    clone: Array<{ href: string, name: string }>
    self: { href: string }
    source: { href: string }
    html: { href: string }
    avatar: { href: string }
    hooks: { href: string }
    forks: { href: string }
    downloads: { href: string }
    pullrequests: { href: string }
  }
  fork_policy: 'allow_forks' | 'no_public_forks' | 'no_forks'
  full_name: string
  name: string
  project: {
    key: string
    type: string
    uuid: string
    name: string
    links: {
      self: { href: string }
      html: { href: string }
      avatar: { href: string }
    }
  }
  language: string
  created_on: string
  mainbranch: {
    type: string
    name: string
  }
  workspace: {
    type: string
    uuid: string
    name: string
    slug: string
    is_private: boolean
    created_on: string
    updated_on: string
    links: {
      avatar: { href: string }
      html: { href: string }
      self: { href: string }
    }
  }
  has_issues: boolean
  owner: {
    display_name: string
    uuid: string
    links: {
      self: { href: string }
      avatar: { href: string }
      html: { href: string }
    }
    type: string
    nickname: string
    account_id: string
  }
  updated_on: string
  size: number
  type: string
  slug: string
  is_private: boolean
  description: string
}
```

---

### **2. List Repository Files**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src/{commit}/{path}`

**Purpose:** List repository files

**Query Parameters:**

```typescript
interface BitbucketListFilesRequest {
  q?: string                        // Search query
  format?: 'meta' | 'rendered'
  max_depth?: number
  pagelen?: number
  page?: number
}
```

---

### **3. Get File**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src/{commit}/{path}`

**Purpose:** Get file contents

**Query Parameters:**

```typescript
interface BitbucketGetFileRequest {
  format?: 'meta' | 'rendered'
}
```

**Response:**

```typescript
interface BitbucketFileResponse {
  path: string
  type: 'commit_file' | 'commit_directory'
  size?: number
  mimetype?: string
  links: {
    self: { href: string }
    meta?: { href: string }
  }
  commit?: {
    type: string
    hash: string
    date: string
    author: {
      raw: string
      type: string
      user: {
        display_name: string
        uuid: string
        links: {
          self: { href: string }
          avatar: { href: string }
          html: { href: string }
        }
        type: string
        nickname: string
        account_id: string
      }
    }
    message: string
    parents: Array<{
      hash: string
      type: string
      links: {
        self: { href: string }
        html: { href: string }
      }
    }>
    links: {
      self: { href: string }
      html: { href: string }
    }
  }
  content?: string                  // File content (if format=rendered)
}
```

---

### **4. Create/Update File**

**Endpoint:** `POST https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src`

**Purpose:** Create or update file

**Request:** Multipart form data

**Parameters:**

```typescript
interface BitbucketCreateFileRequest {
  message: string                   // Required: Commit message
  branch?: string                    // Branch name
  author?: string                    // Author email
  parents?: string                   // Parent commit SHA
  files: {
    [filePath: string]: string        // File path -> content
  }
}
```

---

### **5. List Pull Requests**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests`

**Purpose:** List pull requests

**Query Parameters:**

```typescript
interface BitbucketPullRequestsRequest {
  state?: 'OPEN' | 'MERGED' | 'DECLINED' | 'SUPERSEDED'
  q?: string                        // Search query
  sort?: '-updated_on' | 'updated_on' | '-created_on' | 'created_on'
  pagelen?: number
  page?: number
}
```

**Response:**

```typescript
interface BitbucketPullRequestsResponse {
  pagelen: number
  values: Array<{
    id: number
    title: string
    description: string
    state: 'OPEN' | 'MERGED' | 'DECLINED' | 'SUPERSEDED'
    author: {
      display_name: string
      uuid: string
      links: {
        self: { href: string }
        avatar: { href: string }
        html: { href: string }
      }
      type: string
      nickname: string
      account_id: string
    }
    source: {
      branch: {
        name: string
      }
      commit: {
        hash: string
        type: string
        links: {
          self: { href: string }
          html: { href: string }
        }
      }
      repository: {
        type: string
        full_name: string
        links: {
          self: { href: string }
          html: { href: string }
          avatar: { href: string }
        }
        name: string
        uuid: string
      }
    }
    destination: {
      branch: {
        name: string
      }
      commit: {
        hash: string
        type: string
        links: {
          self: { href: string }
          html: { href: string }
        }
      }
      repository: {
        type: string
        full_name: string
        links: {
          self: { href: string }
          html: { href: string }
          avatar: { href: string }
        }
        name: string
        uuid: string
      }
    }
    merge_commit: {
      hash: string
      type: string
      links: {
        self: { href: string }
        html: { href: string }
      }
    } | null
    participants: Array<{
      type: string
      user: {
        display_name: string
        uuid: string
        links: {
          self: { href: string }
          avatar: { href: string }
          html: { href: string }
        }
        type: string
        nickname: string
        account_id: string
      }
      role: 'REVIEWER' | 'PARTICIPANT'
      approved: boolean
      state: 'approved' | 'changes_requested' | 'null'
      participated_on: string
    }>
    reviewers: Array<{
      display_name: string
      uuid: string
      links: {
        self: { href: string }
        avatar: { href: string }
        html: { href: string }
      }
      type: string
      nickname: string
      account_id: string
    }>
    close_source_branch: boolean
    closed_by: {
      display_name: string
      uuid: string
      links: {
        self: { href: string }
        avatar: { href: string }
        html: { href: string }
      }
      type: string
      nickname: string
      account_id: string
    } | null
    reason: string
    created_on: string
    updated_on: string
    links: {
      self: { href: string }
      html: { href: string }
      commits: { href: string }
      approve: { href: string }
      decline: { href: string }
      diff: { href: string }
      diffstat: { href: string }
      merge: { href: string }
      comments: { href: string }
      activity: { href: string }
      patch: { href: string }
    }
    summary: {
      raw: string
      markup: 'markdown' | 'creole' | 'plain'
      html: string
      type: string
    }
  }>
  page: number
  size: number
}
```

---

### **6. Create Pull Request**

**Endpoint:** `POST https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests`

**Purpose:** Create pull request

**Request Body:**

```typescript
interface BitbucketCreatePullRequestRequest {
  title: string                     // Required
  source: {
    branch: {
      name: string                  // Required
    }
    repository: {
      full_name: string            // Required
    }
  }
  destination: {
    branch: {
      name: string                  // Required
    }
  }
  description?: string
  close_source_branch?: boolean
  reviewers?: Array<{
    uuid: string
  }>
}
```

---

### **7. List Commits**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/commits`

**Purpose:** List commits

**Query Parameters:**

```typescript
interface BitbucketCommitsRequest {
  include?: string                  // Comma-separated: 'branch', 'tags'
  exclude?: string                  // Branch/tag to exclude
  pagelen?: number
  page?: number
}
```

---

### **8. Get Commit**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/commit/{sha}`

**Purpose:** Get commit details

---

### **9. List Pipelines**

**Endpoint:** `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pipelines/`

**Purpose:** List CI/CD pipelines

**Query Parameters:**

```typescript
interface BitbucketPipelinesRequest {
  page?: number
  pagelen?: number
  sort?: '-created_on' | 'created_on'
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Browse Repository**

1. User enters workspace/repo
2. Get repository info
3. List repository files
4. Navigate directories
5. View file contents

### **Workflow 2: Create Pull Request**

1. User creates branch
2. Makes changes
3. Create pull request
4. Configure reviewers
5. Submit → Create PR
6. Display PR

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 60 requests/hour (unauthenticated)
- Higher limits with authentication

**Paid Tier:**
- Higher limits
- Varies by plan

---

## 💰 **PRICING**

**Free Tier:**
- Public repositories: Free
- Private repositories: Free (limited users)

**Paid Tier:**
- Bitbucket Premium: $3/user/month
- Bitbucket Standard: $6/user/month

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Repository Browser Panel**

**Repository Input:**
- Workspace/repo input
- Repository info display

**File Tree:**
- Directory tree view
- File list
- File preview

**File Viewer:**
- Syntax highlighting
- Line numbers
- Copy button

### **Pull Requests Panel**

**PR List:**
- PR cards
- Status badges
- Source/target branches
- Reviewers

**Create PR Form:**
- Source branch selector
- Target branch selector
- Title input
- Description editor
- Reviewer selector
- Submit button

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class BitbucketService extends BaseAPIService {
  constructor(accessToken?: string) {
    super('bitbucket', 'https://api.bitbucket.org/2.0', accessToken)
  }

  async getRepository(workspace: string, repoSlug: string): Promise<APIResponse<BitbucketRepository>>
  async listFiles(workspace: string, repoSlug: string, commit: string, path?: string, options?: BitbucketListFilesRequest): Promise<APIResponse<any>>
  async getFile(workspace: string, repoSlug: string, commit: string, path: string, options?: BitbucketGetFileRequest): Promise<APIResponse<BitbucketFileResponse>>
  async createFile(workspace: string, repoSlug: string, request: BitbucketCreateFileRequest): Promise<APIResponse<any>>
  async listPullRequests(workspace: string, repoSlug: string, options?: BitbucketPullRequestsRequest): Promise<APIResponse<BitbucketPullRequestsResponse>>
  async createPullRequest(workspace: string, repoSlug: string, request: BitbucketCreatePullRequestRequest): Promise<APIResponse<any>>
  async listCommits(workspace: string, repoSlug: string, options?: BitbucketCommitsRequest): Promise<APIResponse<any>>
  async getCommit(workspace: string, repoSlug: string, sha: string): Promise<APIResponse<any>>
  async listPipelines(workspace: string, repoSlug: string, options?: BitbucketPipelinesRequest): Promise<APIResponse<any>>
  
  // Helper methods
  parseRepoUrl(url: string): { workspace: string, repoSlug: string } | null
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- OAuth 2.0 authentication
- File tree rendering
- Syntax highlighting

**Estimated Implementation Time:**
- Service layer: 8-10 hours
- Repository browser: 6-8 hours
- File viewer: 4-6 hours
- Pull Requests UI: 6-8 hours
- Testing: 4-6 hours
- **Total: 28-38 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

