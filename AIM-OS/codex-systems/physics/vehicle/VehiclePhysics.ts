/**
 * Vehicle Physics System
 * Arcade/simulation hybrid with raycast wheels
 * 
 * Features:
 * - Raycast suspension
 * - Pacejka tire model (simplified)
 * - Engine/transmission simulation
 * - Differential (open/locked/limited slip)
 * - Aerodynamics (drag, downforce)
 */

import * as THREE from 'three';

export interface VehicleConfig {
  // Chassis
  mass: number;                    // kg
  centerOfMass: THREE.Vector3;     // Local offset
  inertia: THREE.Vector3;          // Moment of inertia
  
  // Engine
  maxRPM: number;
  idleRPM: number;
  maxTorque: number;               // Nm
  torqueCurve: number[];           // Torque at each RPM point
  
  // Transmission
  gearRatios: number[];            // Including reverse [R, 1, 2, 3, 4, 5, ...]
  finalDriveRatio: number;
  shiftTime: number;               // Seconds
  
  // Differential
  diffType: 'open' | 'locked' | 'lsd';
  lsdPreload: number;              // For LSD
  lsdRatio: number;                // For LSD
  
  // Aerodynamics
  dragCoefficient: number;
  frontalArea: number;             // m²
  downforceCoefficient: number;
  
  // Wheels
  wheels: WheelConfig[];
  
  // Controls
  steeringSensitivity: number;
  maxSteerAngle: number;           // Degrees
}

export interface WheelConfig {
  // Position relative to chassis
  position: THREE.Vector3;
  
  // Suspension
  suspensionRestLength: number;    // m
  suspensionStiffness: number;     // N/m
  suspensionDamping: number;       // Ns/m
  suspensionTravel: number;        // m (max compression)
  
  // Wheel
  radius: number;                  // m
  width: number;                   // m
  mass: number;                    // kg
  
  // Tire (Pacejka-like parameters)
  frictionCoefficient: number;
  slipAnglePeak: number;           // Degrees
  slipRatioPeak: number;           // 0-1
  
  // Drive/Steering
  isDriven: boolean;
  isSteered: boolean;
  steerMultiplier: number;         // 1 for front, -0.1 for rear (optional rear steer)
}

export interface WheelState {
  // Runtime state
  suspensionLength: number;
  suspensionVelocity: number;
  wheelRotation: number;           // Radians
  wheelAngularVelocity: number;    // rad/s
  slipRatio: number;
  slipAngle: number;
  
  // Forces
  suspensionForce: number;
  longitudinalForce: number;
  lateralForce: number;
  
  // Contact
  isGrounded: boolean;
  contactPoint: THREE.Vector3;
  contactNormal: THREE.Vector3;
  groundVelocity: THREE.Vector3;
}

export const DEFAULT_VEHICLE_CONFIG: VehicleConfig = {
  mass: 1500,
  centerOfMass: new THREE.Vector3(0, -0.3, 0),
  inertia: new THREE.Vector3(2000, 3000, 1000),
  
  maxRPM: 7000,
  idleRPM: 800,
  maxTorque: 400,
  torqueCurve: [0.3, 0.5, 0.7, 0.9, 1.0, 0.95, 0.85, 0.7],
  
  gearRatios: [-3.5, 3.5, 2.2, 1.5, 1.1, 0.9, 0.75],
  finalDriveRatio: 3.7,
  shiftTime: 0.2,
  
  diffType: 'lsd',
  lsdPreload: 50,
  lsdRatio: 0.5,
  
  dragCoefficient: 0.35,
  frontalArea: 2.2,
  downforceCoefficient: 0.3,
  
  wheels: [],
  
  steeringSensitivity: 2.0,
  maxSteerAngle: 35
};

export class VehiclePhysics {
  private config: VehicleConfig;
  private wheelStates: WheelState[] = [];
  
  // Chassis state
  public position = new THREE.Vector3();
  public rotation = new THREE.Quaternion();
  public velocity = new THREE.Vector3();
  public angularVelocity = new THREE.Vector3();
  
  // Engine state
  private engineRPM: number = 800;
  private currentGear: number = 1;  // 0 = reverse, 1+ = forward gears
  private isShifting: boolean = false;
  private shiftTimer: number = 0;
  
  // Input state (0 to 1)
  private throttle: number = 0;
  private brake: number = 0;
  private steering: number = 0;     // -1 to 1
  private handbrake: number = 0;
  
  // Temp vectors
  private readonly _v1 = new THREE.Vector3();
  private readonly _v2 = new THREE.Vector3();
  private readonly _v3 = new THREE.Vector3();
  private readonly _q1 = new THREE.Quaternion();
  private readonly _m1 = new THREE.Matrix4();

  constructor(config: Partial<VehicleConfig> = {}) {
    this.config = { ...DEFAULT_VEHICLE_CONFIG, ...config };
    
    // Initialize wheel states
    for (const wheel of this.config.wheels) {
      this.wheelStates.push({
        suspensionLength: wheel.suspensionRestLength,
        suspensionVelocity: 0,
        wheelRotation: 0,
        wheelAngularVelocity: 0,
        slipRatio: 0,
        slipAngle: 0,
        suspensionForce: 0,
        longitudinalForce: 0,
        lateralForce: 0,
        isGrounded: false,
        contactPoint: new THREE.Vector3(),
        contactNormal: new THREE.Vector3(0, 1, 0),
        groundVelocity: new THREE.Vector3()
      });
    }
  }

  /**
   * Set input controls
   */
  public setInput(throttle: number, brake: number, steering: number, handbrake: number = 0): void {
    this.throttle = THREE.MathUtils.clamp(throttle, 0, 1);
    this.brake = THREE.MathUtils.clamp(brake, 0, 1);
    this.steering = THREE.MathUtils.clamp(steering, -1, 1);
    this.handbrake = THREE.MathUtils.clamp(handbrake, 0, 1);
  }

  /**
   * Shift gear up
   */
  public shiftUp(): void {
    if (this.isShifting) return;
    if (this.currentGear < this.config.gearRatios.length - 1) {
      this.isShifting = true;
      this.shiftTimer = this.config.shiftTime;
      this.currentGear++;
    }
  }

  /**
   * Shift gear down
   */
  public shiftDown(): void {
    if (this.isShifting) return;
    if (this.currentGear > 0) {
      this.isShifting = true;
      this.shiftTimer = this.config.shiftTime;
      this.currentGear--;
    }
  }

  /**
   * Main physics update
   * @param dt Delta time in seconds
   * @param raycaster Function to raycast (point, direction) => {hit, distance, normal}
   */
  public update(
    dt: number,
    raycaster: (origin: THREE.Vector3, direction: THREE.Vector3) => {
      hit: boolean;
      distance: number;
      normal: THREE.Vector3;
      point: THREE.Vector3;
    }
  ): void {
    // Clamp dt
    dt = Math.min(dt, 1 / 30);
    
    // Update shift timer
    if (this.isShifting) {
      this.shiftTimer -= dt;
      if (this.shiftTimer <= 0) {
        this.isShifting = false;
      }
    }
    
    // Get chassis transform matrix
    this._m1.makeRotationFromQuaternion(this.rotation);
    
    // Local axes
    const forward = new THREE.Vector3(0, 0, 1).applyQuaternion(this.rotation);
    const right = new THREE.Vector3(1, 0, 0).applyQuaternion(this.rotation);
    const up = new THREE.Vector3(0, 1, 0).applyQuaternion(this.rotation);
    
    // ============ WHEEL FORCES ============
    const totalForce = new THREE.Vector3();
    const totalTorque = new THREE.Vector3();
    
    // Calculate engine torque
    const engineTorque = this.calculateEngineTorque();
    
    for (let i = 0; i < this.config.wheels.length; i++) {
      const wheelConfig = this.config.wheels[i];
      const wheelState = this.wheelStates[i];
      
      // Wheel world position
      const wheelPos = wheelConfig.position.clone().applyQuaternion(this.rotation).add(this.position);
      
      // Raycast down from wheel
      const rayOrigin = wheelPos.clone();
      const rayDir = up.clone().negate();
      const maxDist = wheelConfig.suspensionRestLength + wheelConfig.suspensionTravel + wheelConfig.radius;
      
      const rayResult = raycaster(rayOrigin, rayDir);
      
      if (rayResult.hit && rayResult.distance <= maxDist) {
        wheelState.isGrounded = true;
        wheelState.contactPoint.copy(rayResult.point);
        wheelState.contactNormal.copy(rayResult.normal);
        
        // Suspension compression
        const compressionDist = maxDist - rayResult.distance;
        const newSuspensionLength = wheelConfig.suspensionRestLength - compressionDist + wheelConfig.radius;
        
        // Suspension velocity
        wheelState.suspensionVelocity = (newSuspensionLength - wheelState.suspensionLength) / dt;
        wheelState.suspensionLength = newSuspensionLength;
        
        // Suspension force (spring + damper)
        const springForce = (wheelConfig.suspensionRestLength - wheelState.suspensionLength) * 
                           wheelConfig.suspensionStiffness;
        const damperForce = -wheelState.suspensionVelocity * wheelConfig.suspensionDamping;
        wheelState.suspensionForce = Math.max(0, springForce + damperForce);
        
        // Ground velocity at contact point
        const wheelVel = this.getVelocityAtPoint(wheelPos);
        
        // Project velocity onto ground plane
        const groundRight = right.clone();
        const groundForward = forward.clone();
        groundRight.sub(rayResult.normal.clone().multiplyScalar(groundRight.dot(rayResult.normal))).normalize();
        groundForward.sub(rayResult.normal.clone().multiplyScalar(groundForward.dot(rayResult.normal))).normalize();
        
        // Apply steering
        if (wheelConfig.isSteered) {
          const steerAngle = this.steering * this.config.maxSteerAngle * wheelConfig.steerMultiplier;
          const steerRad = THREE.MathUtils.degToRad(steerAngle);
          this._q1.setFromAxisAngle(rayResult.normal, steerRad);
          groundForward.applyQuaternion(this._q1);
          groundRight.applyQuaternion(this._q1);
        }
        
        // Longitudinal velocity (forward/backward)
        const longVel = wheelVel.dot(groundForward);
        
        // Lateral velocity (sideways)
        const latVel = wheelVel.dot(groundRight);
        
        // Wheel rotation velocity
        const wheelLinearVel = wheelState.wheelAngularVelocity * wheelConfig.radius;
        
        // Slip ratio (longitudinal slip)
        const slipRatio = this.calculateSlipRatio(longVel, wheelLinearVel);
        wheelState.slipRatio = slipRatio;
        
        // Slip angle (lateral slip)
        const slipAngle = Math.atan2(latVel, Math.abs(longVel) + 0.1);
        wheelState.slipAngle = slipAngle;
        
        // Tire forces (simplified Pacejka)
        const normalLoad = wheelState.suspensionForce;
        const maxFriction = normalLoad * wheelConfig.frictionCoefficient;
        
        // Longitudinal force (traction/braking)
        const longForce = this.calculateLongitudinalForce(slipRatio, maxFriction, wheelConfig);
        wheelState.longitudinalForce = longForce;
        
        // Lateral force (cornering)
        const latForce = this.calculateLateralForce(slipAngle, maxFriction, wheelConfig);
        wheelState.lateralForce = latForce;
        
        // Apply forces to chassis
        const forcePoint = wheelPos.clone();
        
        // Longitudinal force along wheel direction
        this._v1.copy(groundForward).multiplyScalar(longForce);
        totalForce.add(this._v1);
        this.addTorqueFromForce(this._v1, forcePoint, totalTorque);
        
        // Lateral force perpendicular to wheel
        this._v2.copy(groundRight).multiplyScalar(-latForce);
        totalForce.add(this._v2);
        this.addTorqueFromForce(this._v2, forcePoint, totalTorque);
        
        // Suspension force along normal
        this._v3.copy(rayResult.normal).multiplyScalar(wheelState.suspensionForce);
        totalForce.add(this._v3);
        this.addTorqueFromForce(this._v3, forcePoint, totalTorque);
        
        // Update wheel rotation
        const driveWheelTorque = wheelConfig.isDriven && !this.isShifting ? engineTorque / 2 : 0;
        const brakeTorque = this.brake * 3000 * wheelConfig.radius;
        const handbrakeTorque = this.handbrake * 5000 * wheelConfig.radius;
        
        const wheelTorque = driveWheelTorque - brakeTorque - handbrakeTorque - 
                           longForce * wheelConfig.radius * 0.1;
        const wheelInertia = wheelConfig.mass * wheelConfig.radius * wheelConfig.radius;
        
        wheelState.wheelAngularVelocity += (wheelTorque / wheelInertia) * dt;
        wheelState.wheelRotation += wheelState.wheelAngularVelocity * dt;
        
      } else {
        wheelState.isGrounded = false;
        wheelState.suspensionForce = 0;
        wheelState.longitudinalForce = 0;
        wheelState.lateralForce = 0;
        wheelState.suspensionLength = wheelConfig.suspensionRestLength;
        
        // Spin wheel down when airborne
        wheelState.wheelAngularVelocity *= 0.99;
        wheelState.wheelRotation += wheelState.wheelAngularVelocity * dt;
      }
    }
    
    // ============ AERODYNAMICS ============
    const speed = this.velocity.length();
    const speedSq = speed * speed;
    
    // Drag force (opposes velocity)
    const dragForce = 0.5 * 1.225 * this.config.dragCoefficient * 
                      this.config.frontalArea * speedSq;
    if (speed > 0.1) {
      this._v1.copy(this.velocity).normalize().multiplyScalar(-dragForce);
      totalForce.add(this._v1);
    }
    
    // Downforce (pushes down)
    const downforce = 0.5 * 1.225 * this.config.downforceCoefficient * 
                     this.config.frontalArea * speedSq;
    totalForce.y -= downforce;
    
    // ============ GRAVITY ============
    totalForce.y -= this.config.mass * 9.81;
    
    // ============ INTEGRATION ============
    // Linear
    const acceleration = totalForce.divideScalar(this.config.mass);
    this.velocity.addScaledVector(acceleration, dt);
    this.position.addScaledVector(this.velocity, dt);
    
    // Angular
    const angularAccel = totalTorque.clone().divide(this.config.inertia);
    this.angularVelocity.addScaledVector(angularAccel, dt);
    
    // Apply angular velocity to rotation
    const rotationDelta = this.angularVelocity.clone().multiplyScalar(dt);
    const deltaQuat = new THREE.Quaternion().setFromEuler(
      new THREE.Euler(rotationDelta.x, rotationDelta.y, rotationDelta.z)
    );
    this.rotation.multiply(deltaQuat);
    this.rotation.normalize();
    
    // Damping
    this.velocity.multiplyScalar(0.999);
    this.angularVelocity.multiplyScalar(0.98);
    
    // Update engine RPM based on wheel speed
    this.updateEngineRPM();
  }

  private calculateEngineTorque(): number {
    if (this.isShifting) return 0;
    
    const gearRatio = this.config.gearRatios[this.currentGear];
    const totalRatio = gearRatio * this.config.finalDriveRatio;
    
    // Normalize RPM to torque curve index
    const rpmNorm = (this.engineRPM - this.config.idleRPM) / 
                   (this.config.maxRPM - this.config.idleRPM);
    const curveIdx = Math.min(
      this.config.torqueCurve.length - 1,
      Math.max(0, Math.floor(rpmNorm * this.config.torqueCurve.length))
    );
    const torqueMultiplier = this.config.torqueCurve[curveIdx] || 0.5;
    
    return this.throttle * this.config.maxTorque * torqueMultiplier * totalRatio;
  }

  private calculateSlipRatio(groundSpeed: number, wheelSpeed: number): number {
    const eps = 0.1;
    if (Math.abs(groundSpeed) < eps && Math.abs(wheelSpeed) < eps) {
      return 0;
    }
    
    const denom = Math.max(Math.abs(groundSpeed), Math.abs(wheelSpeed));
    return (wheelSpeed - groundSpeed) / denom;
  }

  private calculateLongitudinalForce(slipRatio: number, maxFriction: number, wheel: WheelConfig): number {
    // Simplified Pacejka magic formula
    const B = 10;
    const C = 1.9;
    const D = maxFriction;
    const E = 0.97;
    
    const x = slipRatio * 100; // Scale for formula
    return D * Math.sin(C * Math.atan(B * x - E * (B * x - Math.atan(B * x))));
  }

  private calculateLateralForce(slipAngle: number, maxFriction: number, wheel: WheelConfig): number {
    // Simplified Pacejka magic formula
    const B = 8;
    const C = 1.65;
    const D = maxFriction;
    const E = 0.97;
    
    const x = THREE.MathUtils.radToDeg(slipAngle);
    return D * Math.sin(C * Math.atan(B * x - E * (B * x - Math.atan(B * x))));
  }

  private getVelocityAtPoint(point: THREE.Vector3): THREE.Vector3 {
    const r = point.clone().sub(this.position);
    return this.velocity.clone().add(
      new THREE.Vector3().crossVectors(this.angularVelocity, r)
    );
  }

  private addTorqueFromForce(force: THREE.Vector3, point: THREE.Vector3, torque: THREE.Vector3): void {
    const r = point.clone().sub(this.position).sub(
      this.config.centerOfMass.clone().applyQuaternion(this.rotation)
    );
    torque.add(new THREE.Vector3().crossVectors(r, force));
  }

  private updateEngineRPM(): void {
    // Calculate average driven wheel speed
    let totalWheelSpeed = 0;
    let drivenCount = 0;
    
    for (let i = 0; i < this.config.wheels.length; i++) {
      if (this.config.wheels[i].isDriven) {
        totalWheelSpeed += Math.abs(this.wheelStates[i].wheelAngularVelocity);
        drivenCount++;
      }
    }
    
    if (drivenCount > 0) {
      const avgWheelSpeed = totalWheelSpeed / drivenCount;
      const wheelRadius = this.config.wheels[0].radius;
      const gearRatio = this.config.gearRatios[this.currentGear];
      const totalRatio = Math.abs(gearRatio) * this.config.finalDriveRatio;
      
      const calculatedRPM = (avgWheelSpeed * totalRatio * 60) / (2 * Math.PI);
      this.engineRPM = THREE.MathUtils.clamp(
        calculatedRPM,
        this.config.idleRPM,
        this.config.maxRPM
      );
    }
    
    // Rev limiter bounce
    if (this.engineRPM >= this.config.maxRPM * 0.98) {
      this.engineRPM = this.config.maxRPM * 0.95;
    }
  }

  // ============ PUBLIC API ============

  public getSpeed(): number {
    return this.velocity.length() * 3.6; // km/h
  }

  public getEngineRPM(): number {
    return this.engineRPM;
  }

  public getCurrentGear(): number {
    return this.currentGear;
  }

  public getWheelState(index: number): WheelState | undefined {
    return this.wheelStates[index];
  }

  public setPosition(pos: THREE.Vector3): void {
    this.position.copy(pos);
  }

  public setRotation(rot: THREE.Quaternion): void {
    this.rotation.copy(rot);
  }

  public reset(): void {
    this.velocity.set(0, 0, 0);
    this.angularVelocity.set(0, 0, 0);
    this.engineRPM = this.config.idleRPM;
    this.currentGear = 1;
    
    for (const state of this.wheelStates) {
      state.wheelAngularVelocity = 0;
      state.wheelRotation = 0;
    }
  }
}

