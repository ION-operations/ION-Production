/**
 * APOE Service - Atomic Provenance Orchestration Engine integration
 */

import { AIMOSClient } from '../client'
import {
  APOECreatePlanParams,
  APOECreatePlanResult,
} from '../types'

/**
 * APOE Service for execution plan creation and orchestration
 */
export class APOEService {
  constructor(private client: AIMOSClient) {}

  /**
   * Create APOE execution plan from ACL code
   * 
   * @param params Create plan parameters
   * @returns Plan ID and compiled plan structure
   */
  async createPlan(params: APOECreatePlanParams): Promise<APOECreatePlanResult> {
    const result = await this.client.executeTool('create_plan', {
      acl_code: params.acl_code,
      ...(params.context && { context: params.context }),
    })

    return {
      plan_id: result.plan_id || result.id,
      plan: result.plan || result,
    }
  }
}

