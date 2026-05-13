---
id: "leetcode_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "LeetCode API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of LeetCode API capabilities - coding problems and solutions"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["leetcode", "coding-problems", "competitive-programming", "api-integration", "deep-dive"]
---

# LeetCode API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of LeetCode API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://leetcode.com/api (unofficial, reverse-engineered)

---

## 🎯 **LEETCODE API OVERVIEW**

LeetCode provides coding problems and solutions:
- **Problems** - Get problem details
- **Submissions** - Submit solutions
- **User Stats** - User statistics
- **Contests** - Contest information
- **Discuss** - Discussion threads

**Key Features:**
- Coding problems
- Solution submission
- User statistics
- Contest data
- Note: Unofficial API (reverse-engineered)

---

## 🔐 **AUTHENTICATION**

**Method:** Session Cookie or CSRF Token

**Header:**
```
Cookie: LEETCODE_SESSION=YOUR_SESSION
csrftoken: YOUR_CSRF_TOKEN
```

**Session Management:**
- Login via browser
- Extract session cookie
- Store securely: `LEETCODE_SESSION`, `LEETCODE_CSRF_TOKEN`

**Base URL:**
```
https://leetcode.com/api
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Get Problems**

**Endpoint:** `GET https://leetcode.com/api/problems/all/`

**Purpose:** List all problems

**Response:**

```typescript
interface LeetCodeProblemsResponse {
  stat_status_pairs: Array<{
    stat: {
      question_id: number
      question__title: string
      question__title_slug: string
      question__hide: boolean
      total_acs: number
      total_submitted: number
      frontend_question_id: number
      is_new_question: boolean
    }
    status: string | null
    difficulty: {
      level: 1 | 2 | 3        // 1=Easy, 2=Medium, 3=Hard
    }
    paid_only: boolean
    is_favor: boolean
    frequency: number
    progress: number
  }>
}
```

---

### **2. Get Problem**

**Endpoint:** `POST https://leetcode.com/graphql`

**Query:**

```graphql
query getQuestionDetail($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
    titleSlug
    content
    difficulty
    likes
    dislikes
    isLiked
    similarQuestions
    contributors {
      username
      profileUrl
      avatarUrl
    }
    topicTags {
      name
      slug
    }
    codeSnippets {
      lang
      langSlug
      code
    }
    stats
    hints
    solution {
      id
      canSeeDetail
      paidOnly
    }
    status
    sampleTestCase
    exampleTestcases
    metadata
    enableRunCode
    enableTestMode
    enableDebugger
    envInfo
    metaData
    judgerAvailable
    judgeType
    mysqlSchemas
    codeSnippets
    enableSubmit
    submitUrl
    testUrl
    runtimeInfo
    libraryUrl
    adminUrl
  }
}
```

---

### **3. Submit Solution**

**Endpoint:** `POST https://leetcode.com/problems/{titleSlug}/submit/`

**Request Body:**

```typescript
interface LeetCodeSubmitRequest {
  lang: string                     // Language (e.g., 'python3', 'java', 'cpp')
  question_id: string
  typed_code: string                // Solution code
  test_mode: boolean
  judge_type: string
}
```

---

### **4. Get Submission Status**

**Endpoint:** `GET https://leetcode.com/submissions/detail/{submission_id}/check/`

**Purpose:** Check submission status

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Browse Problems**

1. User selects difficulty/tags
2. List problems
3. Click problem → View details
4. View problem description
5. Submit solution

---

## ⚡ **RATE LIMITS**

**Unofficial API:**
- Rate limits apply
- Use responsibly

---

## 💰 **PRICING**

**Free:**
- Access to problems
- Limited submissions

**Premium:**
- LeetCode Premium: $35/month
- More features

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Problems Panel**

**Filter:**
- Difficulty selector
- Tag selector
- Search input

**Problem List:**
- Problem cards
- Difficulty badges
- Tags
- Acceptance rate

**Problem View:**
- Problem description
- Code editor
- Test cases
- Submit button

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class LeetCodeService extends BaseAPIService {
  constructor(sessionCookie?: string, csrfToken?: string) {
    super('leetcode', 'https://leetcode.com/api', sessionCookie)
    this.csrfToken = csrfToken
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'Cookie': `LEETCODE_SESSION=${this.apiKey}`,
      'csrftoken': this.csrfToken || '',
      'Content-Type': 'application/json',
    }
  }

  async getProblems(): Promise<APIResponse<LeetCodeProblemsResponse>>
  async getProblem(titleSlug: string): Promise<APIResponse<any>>
  async submitSolution(titleSlug: string, request: LeetCodeSubmitRequest): Promise<APIResponse<any>>
  async getSubmissionStatus(submissionId: string): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- Session management
- GraphQL client
- Code editor integration

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Problems UI: 6-8 hours
- Problem view: 8-10 hours
- Submission handling: 4-6 hours
- Testing: 4-6 hours
- **Total: 28-38 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Note:** Unofficial API - may change without notice  
**Last Updated:** 2025-01-27

