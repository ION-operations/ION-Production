# Backend API - System Indexes

## Overview

The System Index Browser Panel requires a backend API endpoint to load `system.index.lucid.json5` files. This document describes the expected API contract.

## Endpoints

### GET `/api/system-indexes`

Load all system indexes from the repository.

**Request:**
```
GET http://localhost:5001/api/system-indexes
Content-Type: application/json
```

**Response:**
```json
{
  "success": true,
  "indexes": [
    {
      "systemId": "cmc.contextMemoryCore",
      "humanName": "Context Memory Core - Bitemporal Memory Substrate",
      "version": "v0.1",
      "status": "production",
      "layer": 1,
      "intent": {
        "purpose": "Provide persistent, bitemporal memory substrate...",
        "must_not_regress": [...],
        "why_it_exists": "..."
      },
      "classification": {...},
      "internalNodes": [...],
      "connections": [...],
      "lineage": {...},
      ...
    },
    ...
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to load system indexes: ..."
}
```

### GET `/api/system-indexes/:systemId`

Load a specific system index by ID.

**Request:**
```
GET http://localhost:5001/api/system-indexes/cmc.contextMemoryCore
Content-Type: application/json
```

**Response:**
```json
{
  "success": true,
  "index": {
    "systemId": "cmc.contextMemoryCore",
    ...
  }
}
```

## Implementation Notes

1. **File Location:** System index files are located at:
   - `knowledge_architecture/systems/{system}/system.index.lucid.json5`

2. **JSON5 Parsing:** The backend should parse JSON5 files (which support comments, trailing commas, etc.) and return standard JSON.

3. **Caching:** The frontend service caches responses for 5 minutes. The backend may also implement caching.

4. **Error Handling:** If the API is unavailable, the frontend falls back to mock data for development.

## Example Backend Implementation (Node.js/Express)

```typescript
import express from 'express'
import { readFileSync, readdirSync, statSync } from 'fs'
import { join } from 'path'
import JSON5 from 'json5'

const app = express()

// Load all system indexes
app.get('/api/system-indexes', async (req, res) => {
  try {
    const systemsDir = join(process.cwd(), 'knowledge_architecture', 'systems')
    const indexes: any[] = []

    // Recursively find all system.index.lucid.json5 files
    const findSystemIndexes = (dir: string) => {
      const entries = readdirSync(dir, { withFileTypes: true })
      
      for (const entry of entries) {
        const fullPath = join(dir, entry.name)
        
        if (entry.isDirectory()) {
          findSystemIndexes(fullPath)
        } else if (entry.name === 'system.index.lucid.json5') {
          try {
            const content = readFileSync(fullPath, 'utf-8')
            const parsed = JSON5.parse(content)
            indexes.push(parsed)
          } catch (err) {
            console.warn(`Failed to parse ${fullPath}:`, err)
          }
        }
      }
    }

    findSystemIndexes(systemsDir)
    
    res.json({
      success: true,
      indexes
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})

// Load specific system index
app.get('/api/system-indexes/:systemId', async (req, res) => {
  try {
    const { systemId } = req.params
    const systemsDir = join(process.cwd(), 'knowledge_architecture', 'systems')
    
    // Find the system index file
    const findSystemIndex = (dir: string): string | null => {
      const entries = readdirSync(dir, { withFileTypes: true })
      
      for (const entry of entries) {
        const fullPath = join(dir, entry.name)
        
        if (entry.isDirectory()) {
          const found = findSystemIndex(fullPath)
          if (found) return found
        } else if (entry.name === 'system.index.lucid.json5') {
          try {
            const content = readFileSync(fullPath, 'utf-8')
            const parsed = JSON5.parse(content)
            if (parsed.systemId === systemId) {
              return fullPath
            }
          } catch (err) {
            // Continue searching
          }
        }
      }
      return null
    }

    const filePath = findSystemIndex(systemsDir)
    
    if (!filePath) {
      return res.status(404).json({
        success: false,
        error: `System index not found: ${systemId}`
      })
    }

    const content = readFileSync(filePath, 'utf-8')
    const parsed = JSON5.parse(content)
    
    res.json({
      success: true,
      index: parsed
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
  }
})
```

## Integration with Command Server

If the command server (`http://localhost:5001`) already exists, add these endpoints to it. The SystemIndexService is already configured to use `http://localhost:5001` as the base URL.

## Testing

You can test the API endpoints using curl:

```bash
# Get all system indexes
curl http://localhost:5001/api/system-indexes

# Get specific system index
curl http://localhost:5001/api/system-indexes/cmc.contextMemoryCore
```

## Frontend Fallback

If the API is unavailable, the frontend will:
1. Log a warning to the console
2. Use mock data for development
3. Display an error message if mock data is also unavailable

This ensures the panel remains functional during development even without a backend.

