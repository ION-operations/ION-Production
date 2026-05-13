---
id: "sourcegraph_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Sourcegraph API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Sourcegraph API capabilities - code search and intelligence platform"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["sourcegraph", "code-search", "intelligence", "api-integration", "deep-dive"]
---

# Sourcegraph API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Sourcegraph API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://docs.sourcegraph.com/api

---

## 🎯 **SOURCEGRAPH API OVERVIEW**

Sourcegraph provides code search and intelligence:
- **Code Search** - Advanced code search
- **Symbol Search** - Find symbols
- **Repository Search** - Search repositories
- **Code Intelligence** - Code navigation
- **Batch Changes** - Batch operations
- **Insights** - Code insights

**Key Features:**
- Advanced code search
- Symbol navigation
- Code intelligence
- Repository management
- Free tier available

---

## 🔐 **AUTHENTICATION**

**Method:** Bearer Token (Access Token)

**Header:**
```
Authorization: token YOUR_ACCESS_TOKEN
```

**Token Management:**
- Obtain from: Sourcegraph Settings → Access Tokens
- Store securely: `SOURCEGRAPH_TOKEN`

**Base URL:**
```
https://sourcegraph.com/.api/graphql
```
or self-hosted:
```
https://your-sourcegraph-instance.com/.api/graphql
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Code Search (GraphQL)**

**Query:**

```graphql
query Search($query: String!) {
  search(query: $query) {
    results {
      results {
        __typename
        ... on FileMatch {
          file {
            path
            url
          }
          lineMatches {
            lineNumber
            offsetAndLengths
            preview
          }
        }
        ... on Repository {
          name
          url
        }
      }
    }
  }
}
```

**Variables:**

```typescript
interface SourcegraphSearchVariables {
  query: string                     // Required: Search query
}
```

**Search Query Syntax:**
- `repo:owner/repo` - Filter by repository
- `file:path` - Filter by file path
- `lang:language` - Filter by language
- `type:symbol` - Search symbols
- `type:file` - Search files
- `type:repo` - Search repositories
- `content:"text"` - Search content
- `case:yes` - Case sensitive
- `case:no` - Case insensitive

---

### **2. Symbol Search**

**Query:**

```graphql
query SymbolSearch($query: String!) {
  search(query: $query, patternType: regexp) {
    results {
      results {
        ... on FileMatch {
          file {
            path
            url
          }
          symbols {
            name
            kind
            location {
              url
              range {
                start {
                  line
                  character
                }
                end {
                  line
                  character
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

### **3. Repository Search**

**Query:**

```graphql
query RepositorySearch($query: String!) {
  search(query: $query, patternType: literal) {
    results {
      results {
        ... on Repository {
          name
          url
          description
          createdAt
          updatedAt
        }
      }
    }
  }
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Code Search**

1. User enters search query
2. Configure filters
3. Submit → Display results
4. Click result → View code

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- Limited requests

**Paid Tier:**
- Higher limits

---

## 💰 **PRICING**

**Free Tier:**
- Limited search
- Free forever

**Paid Tier:**
- Sourcegraph Team: $25/user/month
- Sourcegraph Enterprise: Custom pricing

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Code Search Panel**

**Search Input:**
- Query input
- Filter buttons
- Query builder

**Results Display:**
- File matches
- Line matches with preview
- Repository matches
- Symbol matches

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class SourcegraphService extends BaseAPIService {
  constructor(accessToken?: string, baseURL: string = 'https://sourcegraph.com/.api/graphql') {
    super('sourcegraph', baseURL, accessToken)
  }

  protected getDefaultHeaders(): Record<string, string> {
    return {
      'Authorization': `token ${this.apiKey}`,
      'Content-Type': 'application/json',
    }
  }

  async search(query: string): Promise<APIResponse<any>>
  async searchSymbols(query: string): Promise<APIResponse<any>>
  async searchRepositories(query: string): Promise<APIResponse<any>>
  
  // GraphQL helper
  async graphql(query: string, variables?: Record<string, any>): Promise<APIResponse<any>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- GraphQL client
- Code search result rendering
- Syntax highlighting

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- Search UI: 8-10 hours
- Results display: 6-8 hours
- Testing: 4-6 hours
- **Total: 24-32 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

