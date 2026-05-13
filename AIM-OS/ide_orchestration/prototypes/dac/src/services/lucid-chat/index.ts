/**
 * Lucid Chat API Services - Main Export
 */

export * from './base/BaseAPIService'
export * from './base/APIClient'
export * from './base/types'

// 3D Services
export * from './threeD/MeshyService'
export * from './threeD/PentopixService'
export * from './threeD/ThreeDService'

// Audio Services
export * from './audio/ElevenLabsService'
export * from './audio/AudioService'

// LLM Services
export * from './llm/MinimaxService'
export * from './llm/LLMService'
export * from './llm/AdvancedLLMService'

// APOE Orchestration
export * from './orchestration'

// Search Services
export * from './search'

// Reasoning Services
export * from './reasoning'

// Research Services
export * from './research'

// Agent Services
export * from './agents'

// Memory Services
export * from './memory'

// Test utilities
export * from './test'

// TODO: Add other services as they're implemented
// export * from './image/ImageGenerationService'
// export * from './video/VideoService'
// etc.

