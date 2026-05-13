/**
 * AIM-OS SDK Usage Examples
 */

import { AIMOSClient } from './client'

// Example 1: Basic initialization
const aimos = new AIMOSClient({
  commandServerUrl: 'http://localhost:5001',
  appId: 'my-app',
  appToken: 'your-token' // Optional
})

// Example 2: Store memory
async function storeMemory() {
  const result = await aimos.cmc.store({
    content: 'This is a memory I want to store',
    modality: 'text',
    tags: { category: 'example', importance: 0.8 },
    metadata: { source: 'my-app' }
  })
  
  console.log('Stored memory:', result.atom_id)
}

// Example 3: Retrieve memories
async function retrieveMemories() {
  const result = await aimos.cmc.retrieve({
    query: 'search query',
    limit: 10,
    tags: { category: 'example' }
  })
  
  console.log('Found memories:', result.results.length)
  result.results.forEach(memory => {
    console.log(`- ${memory.node.content} (score: ${memory.score})`)
  })
}

// Example 4: Track confidence
async function trackConfidence() {
  const result = await aimos.vif.trackConfidence({
    task: 'data-processing',
    confidence: 0.85,
    model_id: 'gpt-4-turbo',
    task_criticality: 'important'
  })
  
  console.log(`Confidence tracked: ${result.confidence_band} (κ-gate: ${result.kappa_gate_passed})`)
}

// Example 5: Register application
async function registerApp() {
  const app = await aimos.apps.register({
    app_name: 'My App',
    app_type: 'web',
    app_version: '1.0.0',
    aimos_integration: {
      required_services: ['cmc', 'vif'],
      optional_services: ['seg'],
      capabilities: {
        exposes_api: true,
        exposes_ui: true
      }
    }
  })
  
  console.log(`App registered: ${app.id} (${app.name})`)
  
  // Deploy app
  await app.deploy({ environment: 'production' })
  
  // Start app
  await app.start()
}

// Example 6: Register panel
async function registerPanel() {
  await aimos.panels.register({
    id: 'my-panel',
    name: 'My Panel',
    location: 'right',
    section: 'top',
    lazy_load: true,
    component: 'MyPanel',
    icon: 'MyIcon',
    default_size: 300,
    min_size: 200,
    max_size: 800
  })
  
  console.log('Panel registered')
}

// Example 7: Publish and subscribe to events
async function eventExample() {
  // Publish event
  await aimos.events.publish({
    type: 'user_action',
    data: { action: 'button_clicked', button: 'save' },
    target_apps: ['all']
  })
  
  // Subscribe to events
  await aimos.events.subscribe('user_action', (event) => {
    console.log('Event received:', event.data)
  })
}

// Example 8: List all apps
async function listApps() {
  const apps = await aimos.apps.list()
  console.log(`Found ${apps.length} apps:`)
  apps.forEach(app => {
    console.log(`- ${app.name} (${app.status})`)
  })
}

// Example 9: Get app by ID
async function getApp() {
  const app = await aimos.apps.getById('app-id-123')
  if (app) {
    console.log(`App found: ${app.name}`)
    const metrics = await app.getMetrics()
    console.log('Metrics:', metrics)
  } else {
    console.log('App not found')
  }
}

// Example 10: Create APOE plan
async function createPlan() {
  const result = await aimos.apoe.createPlan({
    acl_code: `
      role researcher {
        step analyze {
          tool: "analyze_data"
        }
      }
    `,
    context: { dataset: 'my-data' }
  })
  
  console.log(`Plan created: ${result.plan_id}`)
}

// Example 11: Synthesize knowledge
async function synthesizeKnowledge() {
  const result = await aimos.seg.synthesize({
    topics: ['machine learning', 'neural networks'],
    depth: 3
  })
  
  console.log(`Synthesis complete: ${result.synthesis.entities.length} entities`)
}

