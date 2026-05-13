# AIM-OS SDK

TypeScript SDK for AIM-OS Application Integration Protocol (AIP).

## Installation

```bash
npm install @aimos/sdk
```

## Quick Start

```typescript
import { AIMOSClient } from '@aimos/sdk'

const aimos = new AIMOSClient({
  commandServerUrl: 'http://localhost:5001',
  appId: 'my-app',
  appToken: 'your-token' // Optional, for authenticated requests
})

// Store memory
await aimos.cmc.store({
  content: 'My memory data',
  modality: 'text',
  tags: { category: 'example' }
})

// Retrieve memories
const memories = await aimos.cmc.retrieve({
  query: 'search query',
  limit: 10
})

// Track confidence
await aimos.vif.trackConfidence({
  task: 'my-task',
  confidence: 0.85
})
```

## Documentation

See `knowledge_architecture/systems/lucid-ide/backend-api-system/AIMOS_APP_INTEGRATION_PROTOCOL_CONSOLIDATED.md` for complete protocol documentation.

