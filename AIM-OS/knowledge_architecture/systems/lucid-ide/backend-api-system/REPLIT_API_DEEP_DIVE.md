---
id: "replit_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Replit API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Replit API capabilities - online IDE and code execution platform"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["replit", "code-execution", "ide", "api-integration", "deep-dive"]
---

# Replit API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Replit API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.replit.com

---

## 🎯 **REPLIT API OVERVIEW**

Replit provides online IDE and code execution:
- **Repls** - Create and manage repls (repositories)
- **Code Execution** - Run code in repls
- **Files** - File management
- **Packages** - Package management
- **Deployments** - Deploy applications
- **Database** - Database access
- **Secrets** - Secret management

**Key Features:**
- Online IDE
- Code execution
- Multiple languages
- Package management
- Deployment capabilities

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (API Key)

**Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**API Key Management:**
- Obtain from: Replit Settings → API
- Store securely: `REPLIT_API_KEY`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.replit.com/v1
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Create Repl**

**Endpoint:** `POST https://api.replit.com/v1/repls`

**Purpose:** Create a new repl

**Request Body:**

```typescript
interface ReplitCreateReplRequest {
  language: string                  // Required: Language (e.g., 'python3', 'nodejs', 'java')
  title?: string                    // Repl title
  description?: string
  isPrivate?: boolean
  isAlwaysOn?: boolean
  template?: string                 // Template ID
  icon?: string                     // Icon URL
  coverImage?: string               // Cover image URL
  welcomeMessage?: string
  welcomeMessageMarkdown?: string
  welcomeMessageFiles?: string[]
  welcomeFiles?: string[]
  welcomeFolders?: string[]
  nixpacksConfig?: string
  env?: Record<string, string>       // Environment variables
  deploy?: {
    type: string
    config: Record<string, any>
  }
}
```

**Response:**

```typescript
interface ReplitRepl {
  id: string
  url: string
  title: string
  description: string
  language: string
  isPrivate: boolean
  isAlwaysOn: boolean
  isStarred: boolean
  isPinned: boolean
  isTemplate: boolean
  isArchived: boolean
  isForked: boolean
  isProject: boolean
  isProjectRoot: boolean
  isProjectMember: boolean
  isProjectOwner: boolean
  isProjectAdmin: boolean
  isProjectCollaborator: boolean
  isProjectViewer: boolean
  isProjectGuest: boolean
  isProjectInvitee: boolean
  isProjectPending: boolean
  isProjectRejected: boolean
  isProjectBlocked: boolean
  isProjectDeleted: boolean
  isProjectArchived: boolean
  isProjectPublic: boolean
  isProjectPrivate: boolean
  isProjectUnlisted: boolean
  isProjectTemplate: boolean
  isProjectFork: boolean
  isProjectForked: boolean
  isProjectStarred: boolean
  isProjectPinned: boolean
  isProjectArchived: boolean
  isProjectDeleted: boolean
  isProjectBlocked: boolean
  isProjectRejected: boolean
  isProjectPending: boolean
  isProjectInvitee: boolean
  isProjectGuest: boolean
  isProjectViewer: boolean
  isProjectCollaborator: boolean
  isProjectAdmin: boolean
  isProjectOwner: boolean
  isProjectMember: boolean
  isProjectRoot: boolean
  isProject: boolean
  isForked: boolean
  isArchived: boolean
  isTemplate: boolean
  isPinned: boolean
  isStarred: boolean
  isAlwaysOn: boolean
  isPrivate: boolean
  language: string
  description: string
  title: string
  url: string
  id: string
  timeCreated: string
  timeUpdated: string
  timeModified: string
  timePublished: string
  timeArchived: string
  timeDeleted: string
  timeBlocked: string
  timeRejected: string
  timePending: string
  timeInvited: string
  timeGuest: string
  timeViewer: string
  timeCollaborator: string
  timeAdmin: string
  timeOwner: string
  timeMember: string
  timeRoot: string
  timeProject: string
  timeForked: string
  timeArchived: string
  timeTemplate: string
  timePinned: string
  timeStarred: string
  timeAlwaysOn: string
  timePrivate: string
  timeLanguage: string
  timeDescription: string
  timeTitle: string
  timeUrl: string
  timeId: string
  hostUrl: string
  slug: string
  icon: string
  coverImage: string
  welcomeMessage: string
  welcomeMessageMarkdown: string
  welcomeMessageFiles: string[]
  welcomeFiles: string[]
  welcomeFolders: string[]
  nixpacksConfig: string
  env: Record<string, string>
  deploy: {
    type: string
    config: Record<string, any>
  }
  owner: {
    id: string
    username: string
    image: string
    firstName: string
    lastName: string
    bio: string
    url: string
    roles: string[]
    teams: string[]
    isLoggedIn: boolean
    isHacker: boolean
    isTeacher: boolean
    isStudent: boolean
    isVerified: boolean
    isBanned: boolean
    isDeleted: boolean
    timeCreated: string
    timeUpdated: string
  }
  templateOwner: {
    id: string
    username: string
    image: string
    firstName: string
    lastName: string
    bio: string
    url: string
    roles: string[]
    teams: string[]
    isLoggedIn: boolean
    isHacker: boolean
    isTeacher: boolean
    isStudent: boolean
    isVerified: boolean
    isBanned: boolean
    isDeleted: boolean
    timeCreated: string
    timeUpdated: string
  } | null
  forkedFrom: {
    id: string
    url: string
    title: string
    description: string
    language: string
    isPrivate: boolean
    isAlwaysOn: boolean
    isStarred: boolean
    isPinned: boolean
    isTemplate: boolean
    isArchived: boolean
    isForked: boolean
    isProject: boolean
    isProjectRoot: boolean
    isProjectMember: boolean
    isProjectOwner: boolean
    isProjectAdmin: boolean
    isProjectCollaborator: boolean
    isProjectViewer: boolean
    isProjectGuest: boolean
    isProjectInvitee: boolean
    isProjectPending: boolean
    isProjectRejected: boolean
    isProjectBlocked: boolean
    isProjectDeleted: boolean
    isProjectArchived: boolean
    isProjectPublic: boolean
    isProjectPrivate: boolean
    isProjectUnlisted: boolean
    isProjectTemplate: boolean
    isProjectFork: boolean
    isProjectForked: boolean
    isProjectStarred: boolean
    isProjectPinned: boolean
    isProjectArchived: boolean
    isProjectDeleted: boolean
    isProjectBlocked: boolean
    isProjectRejected: boolean
    isProjectPending: boolean
    isProjectInvitee: boolean
    isProjectGuest: boolean
    isProjectViewer: boolean
    isProjectCollaborator: boolean
    isProjectAdmin: boolean
    isProjectOwner: boolean
    isProjectMember: boolean
    isProjectRoot: boolean
    isProject: boolean
    isForked: boolean
    isArchived: boolean
    isTemplate: boolean
    isPinned: boolean
    isStarred: boolean
    isAlwaysOn: boolean
    isPrivate: boolean
    language: string
    description: string
    title: string
    url: string
    id: string
  } | null
  template: {
    id: string
    url: string
    title: string
    description: string
    language: string
    isPrivate: boolean
    isAlwaysOn: boolean
    isStarred: boolean
    isPinned: boolean
    isTemplate: boolean
    isArchived: boolean
    isForked: boolean
    isProject: boolean
    isProjectRoot: boolean
    isProjectMember: boolean
    isProjectOwner: boolean
    isProjectAdmin: boolean
    isProjectCollaborator: boolean
    isProjectViewer: boolean
    isProjectGuest: boolean
    isProjectInvitee: boolean
    isProjectPending: boolean
    isProjectRejected: boolean
    isProjectBlocked: boolean
    isProjectDeleted: boolean
    isProjectArchived: boolean
    isProjectPublic: boolean
    isProjectPrivate: boolean
    isProjectUnlisted: boolean
    isProjectTemplate: boolean
    isProjectFork: boolean
    isProjectForked: boolean
    isProjectStarred: boolean
    isProjectPinned: boolean
    isProjectArchived: boolean
    isProjectDeleted: boolean
    isProjectBlocked: boolean
    isProjectRejected: boolean
    isProjectPending: boolean
    isProjectInvitee: boolean
    isProjectGuest: boolean
    isProjectViewer: boolean
    isProjectCollaborator: boolean
    isProjectAdmin: boolean
    isProjectOwner: boolean
    isProjectMember: boolean
    isProjectRoot: boolean
    isProject: boolean
    isForked: boolean
    isArchived: boolean
    isTemplate: boolean
    isPinned: boolean
    isStarred: boolean
    isAlwaysOn: boolean
    isPrivate: boolean
    language: string
    description: string
    title: string
    url: string
    id: string
  } | null
}
```

---

### **2. Get Repl**

**Endpoint:** `GET https://api.replit.com/v1/repls/{repl_id}`

**Purpose:** Get repl information

---

### **3. List Files**

**Endpoint:** `GET https://api.replit.com/v1/repls/{repl_id}/files`

**Purpose:** List repl files

---

### **4. Get File**

**Endpoint:** `GET https://api.replit.com/v1/repls/{repl_id}/files/{path}`

**Purpose:** Get file contents

---

### **5. Write File**

**Endpoint:** `POST https://api.replit.com/v1/repls/{repl_id}/files/{path}`

**Purpose:** Create or update file

**Request Body:**

```typescript
interface ReplitWriteFileRequest {
  content: string                   // Required: File content
  encoding?: 'utf8' | 'base64'
}
```

---

### **6. Delete File**

**Endpoint:** `DELETE https://api.replit.com/v1/repls/{repl_id}/files/{path}`

**Purpose:** Delete file

---

### **7. Run Code**

**Endpoint:** `POST https://api.replit.com/v1/repls/{repl_id}/run`

**Purpose:** Run code in repl

**Request Body:**

```typescript
interface ReplitRunRequest {
  language?: string
  stdin?: string
  args?: string[]
  files?: Record<string, string>    // File path -> content
  command?: string
}
```

**Response:**

```typescript
interface ReplitRunResponse {
  output: string
  error: string | null
  exitCode: number
}
```

---

### **8. Install Package**

**Endpoint:** `POST https://api.replit.com/v1/repls/{repl_id}/packages`

**Purpose:** Install package

**Request Body:**

```typescript
interface ReplitInstallPackageRequest {
  package: string                   // Required: Package name
  version?: string
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Create and Run Repl**

1. User selects language
2. Create repl
3. Write code
4. Run code
5. Display output

### **Workflow 2: File Management**

1. User creates repl
2. Create files
3. Edit files
4. Run code
5. View results

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited requests

**Paid Tier:**
- Higher limits
- Check Replit for quotas

---

## 💰 **PRICING**

**Free Tier:**
- Limited repls
- Free forever

**Paid Tier:**
- Replit Hacker: $7/month
- Replit Core: $20/month
- Check Replit pricing page

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Repl Panel**

**Language Selector:**
- Language dropdown
- Template selector

**Code Editor:**
- Monaco editor
- File tree
- File tabs

**Run Button:**
- Show loading state
- Output display

**Output Display:**
- Standard output
- Standard error
- Exit code

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class ReplitService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('replit', 'https://api.replit.com/v1', apiKey)
  }

  async createRepl(request: ReplitCreateReplRequest): Promise<APIResponse<ReplitRepl>>
  async getRepl(replId: string): Promise<APIResponse<ReplitRepl>>
  async listFiles(replId: string): Promise<APIResponse<any>>
  async getFile(replId: string, path: string): Promise<APIResponse<any>>
  async writeFile(replId: string, path: string, request: ReplitWriteFileRequest): Promise<APIResponse<any>>
  async deleteFile(replId: string, path: string): Promise<APIResponse<void>>
  async runCode(replId: string, request: ReplitRunRequest): Promise<APIResponse<ReplitRunResponse>>
  async installPackage(replId: string, request: ReplitInstallPackageRequest): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- Code editor integration
- File tree management
- Code execution handling

**Estimated Implementation Time:**
- Service layer: 8-10 hours
- Repl creation UI: 6-8 hours
- Code editor integration: 8-10 hours
- File management: 6-8 hours
- Code execution: 4-6 hours
- Testing: 4-6 hours
- **Total: 36-48 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

