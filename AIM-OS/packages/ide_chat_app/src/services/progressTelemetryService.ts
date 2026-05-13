// Fallback data if JSON file can't be loaded
const DEFAULT_PREDICTIVE_METRICS: ProgressTelemetrySnapshot = {
  description: 'Default progress telemetry',
  last_updated: new Date().toISOString(),
  notes: 'Using fallback data',
  phases: {}
}

export interface PhasePrediction {
  percent_complete: number
  remaining_tasks: number
  eta_days: number
  velocity_tasks_per_day?: number
}

export interface ProgressTelemetrySnapshot {
  description?: string
  last_updated?: string
  notes?: string
  phases: Record<string, PhasePrediction>
}

/**
 * Lightweight service that surfaces the current predictive metrics generated
 * by the orchestrator CLI. For prototype purposes we simply import the latest
 * JSON artifact; when wiring to a backend this module becomes the integration
 * point.
 */
const DEFAULT_DAEMON_URL =
  (import.meta as any)?.env?.VITE_LUCID_DAEMON_URL ?? 'http://localhost:5000'

class ProgressTelemetryService {
  private baseUrl = DEFAULT_DAEMON_URL
  private cachedMetrics: ProgressTelemetrySnapshot | null = null

  async getSnapshot(): Promise<ProgressTelemetrySnapshot> {
    try {
      const response = await fetch(`${this.baseUrl}/api/telemetry/progress`)
      if (!response.ok) {
        throw new Error(`Telemetry endpoint returned ${response.status}`)
      }
      return (await response.json()) as ProgressTelemetrySnapshot
    } catch (error) {
      console.warn('Falling back to local predictive metrics snapshot:', error)
      
      // Try to load the JSON file dynamically
      if (!this.cachedMetrics) {
        try {
          const metricsModule = await import('./predictive_metrics.json')
          this.cachedMetrics = (metricsModule.default || metricsModule) as ProgressTelemetrySnapshot
        } catch (importError) {
          console.warn('Could not load predictive_metrics.json, using default:', importError)
          this.cachedMetrics = DEFAULT_PREDICTIVE_METRICS
        }
      }
      
      return this.cachedMetrics
    }
  }
}

export const progressTelemetryService = new ProgressTelemetryService()
