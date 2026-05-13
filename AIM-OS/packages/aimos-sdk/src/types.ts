/**
 * Type definitions for AIM-OS SDK
 */

/**
 * Configuration for AIMOSClient
 */
export interface AIMOSClientConfig {
  /** Command Server URL (default: http://localhost:5001) */
  commandServerUrl?: string
  /** App ID (optional, for authenticated requests) */
  appId?: string
  /** App token (optional, for authenticated requests) */
  appToken?: string
}

/**
 * App Manifest structure
 */
export interface AppManifest {
  app_id?: string
  app_name: string
  app_type: 'ide' | 'web' | 'mobile' | 'cli' | 'service'
  app_version: string
  aimos_integration: {
    required_services: string[]
    optional_services?: string[]
    capabilities?: {
      provides_memory?: boolean
      provides_verification?: boolean
      provides_orchestration?: boolean
      exposes_api?: boolean
      exposes_ui?: boolean
    }
    ui_integration?: {
      panels?: PanelDefinition[]
    }
    resource_requirements?: {
      estimated_memory_mb?: number
      estimated_cpu_percent?: number
      requires_persistent_storage?: boolean
      requires_network_access?: boolean
    }
  }
  dependencies?: {
    aimos_core?: string
    other_apps?: string[]
  }
}

/**
 * Panel Definition structure
 */
export interface PanelDefinition {
  id: string
  name: string
  location: 'left' | 'right' | 'bottom' | 'main'
  section?: 'top' | 'bottom'
  lazy_load?: boolean
  component: string
  icon?: string
  default_size?: number
  min_size?: number
  max_size?: number
}

/**
 * CMC Store Parameters
 */
export interface CMCStoreParams {
  content: string
  modality?: 'text' | 'code' | 'event' | 'tool' | 'cross_model'
  tags?: Record<string, number>
  metadata?: Record<string, any>
  embedding?: number[]
}

/**
 * CMC Retrieve Parameters
 */
export interface CMCRetrieveParams {
  query: string
  limit?: number
  modality?: string
  tags?: Record<string, number>
}

/**
 * CMC Retrieve Result
 */
export interface CMCRetrieveResult {
  results: Array<{
    node: {
      id: string
      level: 'document' | 'paragraph' | 'sentence'
      content: string
      summary?: string
    }
    score: number
    confidence: number
  }>
}

/**
 * VIF Track Confidence Parameters
 */
export interface VIFTrackConfidenceParams {
  task: string
  confidence: number
  model_id?: string
  task_criticality?: 'critical' | 'important' | 'routine' | 'low_stakes'
}

/**
 * VIF Track Confidence Result
 */
export interface VIFTrackConfidenceResult {
  witness_id: string
  confidence_band: 'A' | 'B' | 'C'
  kappa_gate_passed: boolean
  created_at: string
}

/**
 * APOE Create Plan Parameters
 */
export interface APOECreatePlanParams {
  acl_code: string
  context?: Record<string, any>
}

/**
 * APOE Create Plan Result
 */
export interface APOECreatePlanResult {
  plan_id: string
  plan: {
    roles: any[]
    steps: any[]
    gates: any[]
  }
}

/**
 * SEG Synthesize Parameters
 */
export interface SEGSynthesizeParams {
  topics: string[]
  depth?: number
}

/**
 * SEG Synthesize Result
 */
export interface SEGSynthesizeResult {
  synthesis: {
    entities: any[]
    relations: any[]
    contradictions: any[]
    confidence: number
  }
}

/**
 * Application Registration Result
 */
export interface AppRegistrationResult {
  success: boolean
  application?: {
    app_id: string
    app_name: string
    app_type: string
    status: string
    created_at: string
  }
  atom_id?: string
  error?: string
}

/**
 * Application Data
 */
export interface ApplicationData {
  app_id: string
  app_name: string
  app_type: string
  status: 'created' | 'deployed' | 'running' | 'stopped'
  created_at: string
  config?: any
  dependencies?: string[]
}

/**
 * Event Publish Parameters
 */
export interface EventPublishParams {
  type: string
  data: any
  target_apps?: string[]
}

/**
 * Command Server Response
 */
export interface CommandServerResponse {
  success: boolean
  tool?: string
  result?: any
  error?: string
}

