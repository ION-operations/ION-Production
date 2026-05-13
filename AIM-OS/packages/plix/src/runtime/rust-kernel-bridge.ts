/**
 * Rust Kernel Bridge - HTTP Client
 * 
 * TypeScript client for Rust kernel HTTP API
 * Phase 1: Real System Integration
 */

import type { QAddrLiteral } from '../models/quaternion-types';

/**
 * Kernel Bridge HTTP Client
 * 
 * Implements KernelBridge interface using HTTP API
 */
export class RustKernelBridge implements KernelBridge {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:8080/api/kernel/v1') {
    this.baseUrl = baseUrl;
  }
  
  /**
   * Execute place syscall
   */
  async place(
    actorQAddr: QAddrLiteral,
    entityId: string,
    qaddr: QAddrLiteral,
    position: any,
    orientation?: any
  ): Promise<{ success: boolean; errors: string[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/syscall/place`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actor_qaddr: this.qaddrToRequest(actorQAddr),
          entity_id: entityId,
          entity_state: {
            qaddr: this.qaddrToRequest(qaddr),
            pose: this.poseToRequest(position, orientation),
          },
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          errors: [`HTTP ${response.status}: ${errorText}`],
        };
      }
      
      const result = await response.json();
      
      if (!result.success && result.error) {
        return {
          success: false,
          errors: [result.error],
        };
      }
      
      return {
        success: result.success,
        errors: [],
      };
    } catch (error: any) {
      return {
        success: false,
        errors: [`Network error: ${error.message}`],
      };
    }
  }
  
  /**
   * Execute move syscall
   */
  async move(
    actorQAddr: QAddrLiteral,
    entityId: string,
    deltaPose: any
  ): Promise<{ success: boolean; newQAddr?: QAddrLiteral; errors: string[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/syscall/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          actor_qaddr: this.qaddrToRequest(actorQAddr),
          entity_id: entityId,
          delta_pose: this.dualQuatToRequest(deltaPose),
          current_time: Date.now() / 1000.0, // Current time in seconds
        }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          errors: [`HTTP ${response.status}: ${errorText}`],
        };
      }
      
      const result = await response.json();
      
      if (!result.success && result.error) {
        return {
          success: false,
          errors: [result.error],
        };
      }
      
      return {
        success: result.success,
        newQAddr: result.new_qaddr ? this.qaddrFromResponse(result.new_qaddr) : undefined,
        errors: [],
      };
    } catch (error: any) {
      return {
        success: false,
        errors: [`Network error: ${error.message}`],
      };
    }
  }
  
  /**
   * Execute sense syscall
   */
  async sense(
    actorQAddr: QAddrLiteral,
    region?: any,
    filters?: any[]
  ): Promise<{ entities: string[]; errors: string[] }> {
    try {
      const requestBody: any = {
        actor_qaddr: this.qaddrToRequest(actorQAddr),
      };
      
      if (region) {
        requestBody.region = {
          center: {
            x: region.center?.x || 0.0,
            y: region.center?.y || 0.0,
            z: region.center?.z || 0.0,
            tau: region.center?.tau || Date.now() / 1000.0,
          },
          radius: region.radius || 5.0,
        };
      }
      
      if (filters && filters.length > 0) {
        const filter = filters[0];
        requestBody.filters = {
          orbital_class: filter.orbital_class,
          min_n: filter.min_n,
          max_n: filter.max_n,
        };
      }
      
      const response = await fetch(`${this.baseUrl}/syscall/sense`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        return {
          entities: [],
          errors: [`HTTP ${response.status}: ${errorText}`],
        };
      }
      
      const result = await response.json();
      
      if (!result.success && result.error) {
        return {
          entities: [],
          errors: [result.error],
        };
      }
      
      return {
        entities: result.entities.map((e: any) => e.entity_id),
        errors: [],
      };
    } catch (error: any) {
      return {
        entities: [],
        errors: [`Network error: ${error.message}`],
      };
    }
  }
  
  /**
   * Execute emit syscall
   */
  async emit(
    actorQAddr: QAddrLiteral,
    event: string,
    effect?: any
  ): Promise<{ success: boolean; errors: string[] }> {
    try {
      const requestBody: any = {
        actor_qaddr: this.qaddrToRequest(actorQAddr),
        event: event,
      };
      
      if (effect?.field_deltas) {
        requestBody.field_deltas = {
          kappa: effect.field_deltas.kappa || 0.0,
          lambda: effect.field_deltas.lambda || 0.0,
          rho: effect.field_deltas.rho || 0.0,
        };
      }
      
      const response = await fetch(`${this.baseUrl}/syscall/emit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        return {
          success: false,
          errors: [`HTTP ${response.status}: ${errorText}`],
        };
      }
      
      const result = await response.json();
      
      if (!result.success && result.error) {
        return {
          success: false,
          errors: [result.error],
        };
      }
      
      return {
        success: result.success,
        errors: [],
      };
    } catch (error: any) {
      return {
        success: false,
        errors: [`Network error: ${error.message}`],
      };
    }
  }
  
  /**
   * Helper: Convert QAddrLiteral to HTTP request format
   */
  private qaddrToRequest(qaddr: QAddrLiteral): any {
    return {
      n: qaddr.n,
      l: qaddr.l,
      m: qaddr.m || 0,
      s: qaddr.s,
      morton_key: qaddr.morton_key || 0,
      s3_bin: qaddr.s3_bin || 0,
    };
  }
  
  /**
   * Helper: Convert HTTP response to QAddrLiteral
   */
  private qaddrFromResponse(qaddr: any): QAddrLiteral {
    return {
      type: 'qaddr',
      n: qaddr.n,
      l: qaddr.l,
      m: qaddr.m,
      s: qaddr.s,
      morton_key: qaddr.morton_key,
      s3_bin: qaddr.s3_bin,
    };
  }
  
  /**
   * Helper: Convert position/orientation to pose request
   */
  private poseToRequest(position: any, orientation?: any): any {
    // Convert position to Vec4
    const translation = {
      w: 0.0,
      x: position.x || 0.0,
      y: position.y || 0.0,
      z: position.z || 0.0,
    };
    
    // Convert orientation to quaternion
    let rotation = { w: 1.0, x: 0.0, y: 0.0, z: 0.0 };
    if (orientation) {
      if (orientation.type === 'quat') {
        rotation = {
          w: orientation.w || 1.0,
          x: orientation.x || 0.0,
          y: orientation.y || 0.0,
          z: orientation.z || 0.0,
        };
      } else if (orientation.type === 'angle_axis') {
        // Convert angle-axis to quaternion
        const angle = orientation.angle || 0.0;
        const axis = orientation.axis || { x: 0.0, y: 0.0, z: 1.0 };
        const halfAngle = angle / 2.0;
        const s = Math.sin(halfAngle);
        rotation = {
          w: Math.cos(halfAngle),
          x: axis.x * s,
          y: axis.y * s,
          z: axis.z * s,
        };
      }
    }
    
    return {
      rotation: rotation,
      translation: translation,
    };
  }
  
  /**
   * Helper: Convert delta pose to dual quaternion request
   */
  private dualQuatToRequest(deltaPose: any): any {
    if (deltaPose.type === 'dualquat') {
      return {
        rotation: {
          w: deltaPose.rotation?.w || 1.0,
          x: deltaPose.rotation?.x || 0.0,
          y: deltaPose.rotation?.y || 0.0,
          z: deltaPose.rotation?.z || 0.0,
        },
        translation: {
          w: deltaPose.translation?.w || 0.0,
          x: deltaPose.translation?.x || 0.0,
          y: deltaPose.translation?.y || 0.0,
          z: deltaPose.translation?.z || 0.0,
        },
      };
    } else if (deltaPose.type === 'screw_motion') {
      // Convert screw motion to dual quaternion
      const angle = deltaPose.angle || 0.0;
      const axis = deltaPose.screw_axis || { x: 0.0, y: 0.0, z: 1.0 };
      const translation = deltaPose.t || { x: 0.0, y: 0.0, z: 0.0 };
      
      const halfAngle = angle / 2.0;
      const s = Math.sin(halfAngle);
      const rotation = {
        w: Math.cos(halfAngle),
        x: axis.x * s,
        y: axis.y * s,
        z: axis.z * s,
      };
      
      return {
        rotation: rotation,
        translation: {
          w: 0.0,
          x: translation.x || 0.0,
          y: translation.y || 0.0,
          z: translation.z || 0.0,
        },
      };
    }
    
    // Default: identity
    return {
      rotation: { w: 1.0, x: 0.0, y: 0.0, z: 0.0 },
      translation: { w: 0.0, x: 0.0, y: 0.0, z: 0.0 },
    };
  }
}

import type { KernelBridge } from './quaternion-runtime';

// Export for use in runtime
export { RustKernelBridge };

