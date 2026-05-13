/**
 * VIF Service - Verifiable Intelligence Framework integration
 */

import { AIMOSClient } from '../client'
import {
  VIFTrackConfidenceParams,
  VIFTrackConfidenceResult,
} from '../types'

/**
 * VIF Service for confidence tracking and witness creation
 */
export class VIFService {
  constructor(private client: AIMOSClient) {}

  /**
   * Track confidence and create VIF witness
   * 
   * @param params Track confidence parameters
   * @returns Witness ID, confidence band, and κ-gate status
   */
  async trackConfidence(params: VIFTrackConfidenceParams): Promise<VIFTrackConfidenceResult> {
    const result = await this.client.executeTool('track_confidence', {
      task: params.task,
      confidence: params.confidence,
      ...(params.model_id && { model_id: params.model_id }),
      ...(params.task_criticality && { task_criticality: params.task_criticality }),
    })

    return {
      witness_id: result.witness_id || result.id,
      confidence_band: result.confidence_band || result.band,
      kappa_gate_passed: result.kappa_gate_passed ?? result.passed ?? true,
      created_at: result.created_at || new Date().toISOString(),
    }
  }
}

