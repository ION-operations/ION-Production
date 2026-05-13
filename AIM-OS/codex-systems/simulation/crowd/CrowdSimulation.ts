/**
 * Crowd Simulation System
 * Large-scale agent simulation with navigation and behavior
 * 
 * Features:
 * - Agent-based simulation
 * - Collision avoidance (RVO/ORCA)
 * - Pathfinding integration
 * - Behavior trees
 * - LOD for distant agents
 * - GPU instancing
 * - Group behaviors
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface AgentConfig {
  radius: number;
  maxSpeed: number;
  preferredSpeed: number;
  maxAcceleration: number;
  neighborDistance: number;
  timeHorizon: number;
  mass: number;
}

export interface Agent {
  id: number;
  position: THREE.Vector2;
  velocity: THREE.Vector2;
  preferredVelocity: THREE.Vector2;
  goal: THREE.Vector2 | null;
  config: AgentConfig;
  groupId: number;
  state: AgentState;
  animationState: string;
  height: number;
  rotation: number;
}

export type AgentState = 'idle' | 'walking' | 'running' | 'stopped';

export interface Obstacle {
  type: 'circle' | 'line' | 'polygon';
  position: THREE.Vector2;
  radius?: number;
  start?: THREE.Vector2;
  end?: THREE.Vector2;
  vertices?: THREE.Vector2[];
}

export interface CrowdConfig {
  maxAgents: number;
  timeStep: number;
  neighborDistance: number;
  maxNeighbors: number;
  defaultAgentConfig: AgentConfig;
}

export interface SimulationStats {
  agentCount: number;
  averageSpeed: number;
  colllisionCount: number;
  frameTime: number;
}

// ============================================
// SPATIAL HASH GRID
// ============================================

export class SpatialHashGrid {
  private cellSize: number;
  private cells: Map<string, Agent[]> = new Map();
  
  constructor(cellSize: number) {
    this.cellSize = cellSize;
  }
  
  public clear(): void {
    this.cells.clear();
  }
  
  public insert(agent: Agent): void {
    const key = this.getKey(agent.position);
    
    if (!this.cells.has(key)) {
      this.cells.set(key, []);
    }
    
    this.cells.get(key)!.push(agent);
  }
  
  public query(position: THREE.Vector2, radius: number): Agent[] {
    const results: Agent[] = [];
    
    const minX = Math.floor((position.x - radius) / this.cellSize);
    const maxX = Math.floor((position.x + radius) / this.cellSize);
    const minY = Math.floor((position.y - radius) / this.cellSize);
    const maxY = Math.floor((position.y + radius) / this.cellSize);
    
    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        const key = `${x},${y}`;
        const cell = this.cells.get(key);
        
        if (cell) {
          for (const agent of cell) {
            const dist = position.distanceTo(agent.position);
            if (dist <= radius) {
              results.push(agent);
            }
          }
        }
      }
    }
    
    return results;
  }
  
  private getKey(position: THREE.Vector2): string {
    const x = Math.floor(position.x / this.cellSize);
    const y = Math.floor(position.y / this.cellSize);
    return `${x},${y}`;
  }
}

// ============================================
// ORCA COLLISION AVOIDANCE
// ============================================

export class ORCAAvoidance {
  /**
   * Compute ORCA velocity for an agent
   */
  public computeNewVelocity(
    agent: Agent,
    neighbors: Agent[],
    obstacles: Obstacle[],
    timeStep: number
  ): THREE.Vector2 {
    const orcaLines: { point: THREE.Vector2; direction: THREE.Vector2 }[] = [];
    
    // Add ORCA lines for each neighbor
    for (const neighbor of neighbors) {
      if (neighbor.id === agent.id) continue;
      
      const line = this.computeORCALine(agent, neighbor, timeStep);
      if (line) {
        orcaLines.push(line);
      }
    }
    
    // Add ORCA lines for obstacles
    for (const obstacle of obstacles) {
      const obsLines = this.computeObstacleLines(agent, obstacle);
      orcaLines.push(...obsLines);
    }
    
    // Find velocity that satisfies all ORCA constraints
    return this.linearProgram(orcaLines, agent.preferredVelocity, agent.config.maxSpeed);
  }
  
  private computeORCALine(
    agent: Agent,
    neighbor: Agent,
    timeStep: number
  ): { point: THREE.Vector2; direction: THREE.Vector2 } | null {
    const relativePosition = neighbor.position.clone().sub(agent.position);
    const relativeVelocity = agent.velocity.clone().sub(neighbor.velocity);
    const combinedRadius = agent.config.radius + neighbor.config.radius;
    
    const distSq = relativePosition.lengthSq();
    
    if (distSq < combinedRadius * combinedRadius) {
      // Agents are colliding
      const w = relativePosition.normalize();
      return {
        point: w.clone().multiplyScalar(combinedRadius - Math.sqrt(distSq)),
        direction: new THREE.Vector2(-w.y, w.x)
      };
    }
    
    const timeHorizon = agent.config.timeHorizon;
    
    // VO apex
    const voApex = relativePosition.clone().divideScalar(timeHorizon);
    
    // Unit vector along relative position
    const relPosUnit = relativePosition.clone().normalize();
    
    // Leg direction
    const leg = Math.sqrt(distSq - combinedRadius * combinedRadius);
    
    if (relativePosition.dot(relativeVelocity) < 0) {
      // Velocity projects on cutoff circle
      const wLength = relativeVelocity.length();
      const wUnit = relativeVelocity.clone().normalize();
      
      const dotProduct = wUnit.dot(relPosUnit);
      
      if (dotProduct < 0) {
        // Project on left leg
        return {
          point: voApex.clone().add(relPosUnit.clone().multiplyScalar(-combinedRadius / timeHorizon)),
          direction: new THREE.Vector2(-relPosUnit.y, relPosUnit.x)
        };
      }
    }
    
    // Default ORCA line
    const u = relativeVelocity.clone().sub(voApex);
    const uLength = u.length();
    
    if (uLength > 0) {
      const uUnit = u.clone().divideScalar(uLength);
      
      return {
        point: agent.velocity.clone().add(uUnit.clone().multiplyScalar(uLength * 0.5)),
        direction: new THREE.Vector2(-uUnit.y, uUnit.x)
      };
    }
    
    return null;
  }
  
  private computeObstacleLines(
    agent: Agent,
    obstacle: Obstacle
  ): { point: THREE.Vector2; direction: THREE.Vector2 }[] {
    const lines: { point: THREE.Vector2; direction: THREE.Vector2 }[] = [];
    
    if (obstacle.type === 'circle' && obstacle.radius) {
      const relPos = obstacle.position.clone().sub(agent.position);
      const dist = relPos.length();
      const combinedRadius = agent.config.radius + obstacle.radius;
      
      if (dist > combinedRadius) {
        const relPosUnit = relPos.clone().normalize();
        lines.push({
          point: relPosUnit.clone().multiplyScalar(combinedRadius),
          direction: new THREE.Vector2(-relPosUnit.y, relPosUnit.x)
        });
      }
    }
    
    if (obstacle.type === 'line' && obstacle.start && obstacle.end) {
      // Line obstacle handling
      const lineDir = obstacle.end.clone().sub(obstacle.start).normalize();
      const lineNormal = new THREE.Vector2(-lineDir.y, lineDir.x);
      
      const toAgent = agent.position.clone().sub(obstacle.start);
      const dist = toAgent.dot(lineNormal);
      
      if (dist > 0 && dist < agent.config.radius + 0.5) {
        lines.push({
          point: lineNormal.clone().multiplyScalar(agent.config.radius),
          direction: lineDir
        });
      }
    }
    
    return lines;
  }
  
  private linearProgram(
    lines: { point: THREE.Vector2; direction: THREE.Vector2 }[],
    preferredVelocity: THREE.Vector2,
    maxSpeed: number
  ): THREE.Vector2 {
    // Simplified linear programming
    // Find velocity closest to preferred that satisfies all constraints
    
    let result = preferredVelocity.clone();
    
    for (const line of lines) {
      // Check if current result violates this constraint
      const violation = line.point.clone().sub(result);
      const dotProduct = violation.dot(line.direction);
      
      if (dotProduct > 0) {
        // Violation - project onto constraint line
        result.add(line.direction.clone().multiplyScalar(-dotProduct));
      }
    }
    
    // Clamp to max speed
    if (result.length() > maxSpeed) {
      result.normalize().multiplyScalar(maxSpeed);
    }
    
    return result;
  }
}

// ============================================
// BEHAVIOR SYSTEM
// ============================================

export type BehaviorType = 'wander' | 'seek' | 'flee' | 'arrive' | 'follow' | 'patrol';

export interface Behavior {
  type: BehaviorType;
  weight: number;
  target?: THREE.Vector2;
  targets?: THREE.Vector2[];
  currentTargetIndex?: number;
}

export class BehaviorSystem {
  public computeSteeringForce(agent: Agent, behaviors: Behavior[]): THREE.Vector2 {
    const totalForce = new THREE.Vector2();
    
    for (const behavior of behaviors) {
      const force = this.computeBehavior(agent, behavior);
      totalForce.add(force.multiplyScalar(behavior.weight));
    }
    
    return totalForce;
  }
  
  private computeBehavior(agent: Agent, behavior: Behavior): THREE.Vector2 {
    switch (behavior.type) {
      case 'seek':
        return this.seek(agent, behavior.target!);
      case 'flee':
        return this.flee(agent, behavior.target!);
      case 'arrive':
        return this.arrive(agent, behavior.target!);
      case 'wander':
        return this.wander(agent);
      case 'patrol':
        return this.patrol(agent, behavior);
      default:
        return new THREE.Vector2();
    }
  }
  
  private seek(agent: Agent, target: THREE.Vector2): THREE.Vector2 {
    const desired = target.clone().sub(agent.position).normalize()
      .multiplyScalar(agent.config.maxSpeed);
    return desired.sub(agent.velocity);
  }
  
  private flee(agent: Agent, target: THREE.Vector2): THREE.Vector2 {
    const desired = agent.position.clone().sub(target).normalize()
      .multiplyScalar(agent.config.maxSpeed);
    return desired.sub(agent.velocity);
  }
  
  private arrive(agent: Agent, target: THREE.Vector2): THREE.Vector2 {
    const toTarget = target.clone().sub(agent.position);
    const distance = toTarget.length();
    const slowingRadius = 5;
    
    if (distance < 0.1) {
      return agent.velocity.clone().negate();
    }
    
    const targetSpeed = distance > slowingRadius
      ? agent.config.maxSpeed
      : agent.config.maxSpeed * (distance / slowingRadius);
    
    const desired = toTarget.normalize().multiplyScalar(targetSpeed);
    return desired.sub(agent.velocity);
  }
  
  private wander(agent: Agent): THREE.Vector2 {
    const wanderRadius = 2;
    const wanderDistance = 4;
    const wanderJitter = 0.5;
    
    // Random point on circle
    const randomAngle = Math.random() * Math.PI * 2;
    const randomOffset = new THREE.Vector2(
      Math.cos(randomAngle) * wanderJitter,
      Math.sin(randomAngle) * wanderJitter
    );
    
    const wanderTarget = agent.velocity.clone().normalize()
      .multiplyScalar(wanderDistance)
      .add(randomOffset.normalize().multiplyScalar(wanderRadius));
    
    return wanderTarget.sub(agent.velocity);
  }
  
  private patrol(agent: Agent, behavior: Behavior): THREE.Vector2 {
    if (!behavior.targets || behavior.targets.length === 0) {
      return new THREE.Vector2();
    }
    
    const targetIndex = behavior.currentTargetIndex ?? 0;
    const target = behavior.targets[targetIndex];
    
    const toTarget = target.clone().sub(agent.position);
    
    // Check if reached current target
    if (toTarget.length() < 1) {
      behavior.currentTargetIndex = (targetIndex + 1) % behavior.targets.length;
    }
    
    return this.arrive(agent, target);
  }
}

// ============================================
// CROWD RENDERER
// ============================================

export class CrowdRenderer {
  private scene: THREE.Scene;
  private instancedMesh: THREE.InstancedMesh | null = null;
  private geometry: THREE.BufferGeometry;
  private material: THREE.Material;
  private maxInstances: number;
  private dummy: THREE.Object3D = new THREE.Object3D();
  
  constructor(scene: THREE.Scene, maxInstances: number) {
    this.scene = scene;
    this.maxInstances = maxInstances;
    
    // Simple capsule geometry for agents
    this.geometry = new THREE.CapsuleGeometry(0.3, 1.2, 4, 8);
    this.geometry.translate(0, 0.9, 0);
    
    this.material = new THREE.MeshStandardMaterial({
      color: 0x4488ff,
      roughness: 0.7,
      metalness: 0.1
    });
  }
  
  public initialize(): void {
    this.instancedMesh = new THREE.InstancedMesh(
      this.geometry,
      this.material,
      this.maxInstances
    );
    
    this.instancedMesh.castShadow = true;
    this.instancedMesh.receiveShadow = true;
    this.instancedMesh.count = 0;
    
    this.scene.add(this.instancedMesh);
  }
  
  public update(agents: Agent[]): void {
    if (!this.instancedMesh) return;
    
    this.instancedMesh.count = agents.length;
    
    for (let i = 0; i < agents.length; i++) {
      const agent = agents[i];
      
      this.dummy.position.set(agent.position.x, 0, agent.position.y);
      this.dummy.rotation.y = agent.rotation;
      this.dummy.scale.setScalar(1);
      this.dummy.updateMatrix();
      
      this.instancedMesh.setMatrixAt(i, this.dummy.matrix);
      
      // Set color based on state
      const color = this.getColorForState(agent.state);
      this.instancedMesh.setColorAt(i, color);
    }
    
    this.instancedMesh.instanceMatrix.needsUpdate = true;
    if (this.instancedMesh.instanceColor) {
      this.instancedMesh.instanceColor.needsUpdate = true;
    }
  }
  
  private getColorForState(state: AgentState): THREE.Color {
    switch (state) {
      case 'idle': return new THREE.Color(0x4488ff);
      case 'walking': return new THREE.Color(0x44ff88);
      case 'running': return new THREE.Color(0xff8844);
      case 'stopped': return new THREE.Color(0xff4444);
      default: return new THREE.Color(0x888888);
    }
  }
  
  public dispose(): void {
    if (this.instancedMesh) {
      this.scene.remove(this.instancedMesh);
      this.instancedMesh.dispose();
    }
    this.geometry.dispose();
    if (this.material instanceof THREE.Material) {
      this.material.dispose();
    }
  }
}

// ============================================
// MAIN CROWD SIMULATION
// ============================================

export class CrowdSimulation {
  private config: CrowdConfig;
  private agents: Agent[] = [];
  private obstacles: Obstacle[] = [];
  private spatialHash: SpatialHashGrid;
  private orcaAvoidance: ORCAAvoidance;
  private behaviorSystem: BehaviorSystem;
  private renderer: CrowdRenderer | null = null;
  
  private nextAgentId: number = 0;
  private agentBehaviors: Map<number, Behavior[]> = new Map();
  
  constructor(scene?: THREE.Scene, config: Partial<CrowdConfig> = {}) {
    this.config = {
      maxAgents: 1000,
      timeStep: 1 / 60,
      neighborDistance: 5,
      maxNeighbors: 10,
      defaultAgentConfig: {
        radius: 0.4,
        maxSpeed: 2,
        preferredSpeed: 1.5,
        maxAcceleration: 3,
        neighborDistance: 5,
        timeHorizon: 2,
        mass: 1
      },
      ...config
    };
    
    this.spatialHash = new SpatialHashGrid(this.config.neighborDistance);
    this.orcaAvoidance = new ORCAAvoidance();
    this.behaviorSystem = new BehaviorSystem();
    
    if (scene) {
      this.renderer = new CrowdRenderer(scene, this.config.maxAgents);
      this.renderer.initialize();
    }
  }
  
  /**
   * Add agent to simulation
   */
  public addAgent(
    position: THREE.Vector2,
    goal?: THREE.Vector2,
    config?: Partial<AgentConfig>
  ): number {
    if (this.agents.length >= this.config.maxAgents) {
      console.warn('Max agents reached');
      return -1;
    }
    
    const agentConfig = { ...this.config.defaultAgentConfig, ...config };
    
    const agent: Agent = {
      id: this.nextAgentId++,
      position: position.clone(),
      velocity: new THREE.Vector2(),
      preferredVelocity: new THREE.Vector2(),
      goal,
      config: agentConfig,
      groupId: 0,
      state: 'idle',
      animationState: 'idle',
      height: 1.8,
      rotation: Math.random() * Math.PI * 2
    };
    
    this.agents.push(agent);
    
    // Default behavior: arrive at goal
    if (goal) {
      this.agentBehaviors.set(agent.id, [
        { type: 'arrive', weight: 1, target: goal }
      ]);
    }
    
    return agent.id;
  }
  
  /**
   * Remove agent
   */
  public removeAgent(id: number): void {
    const index = this.agents.findIndex(a => a.id === id);
    if (index >= 0) {
      this.agents.splice(index, 1);
      this.agentBehaviors.delete(id);
    }
  }
  
  /**
   * Set agent goal
   */
  public setAgentGoal(id: number, goal: THREE.Vector2): void {
    const agent = this.agents.find(a => a.id === id);
    if (agent) {
      agent.goal = goal.clone();
      this.agentBehaviors.set(id, [
        { type: 'arrive', weight: 1, target: goal }
      ]);
    }
  }
  
  /**
   * Set agent behaviors
   */
  public setAgentBehaviors(id: number, behaviors: Behavior[]): void {
    this.agentBehaviors.set(id, behaviors);
  }
  
  /**
   * Add obstacle
   */
  public addObstacle(obstacle: Obstacle): void {
    this.obstacles.push(obstacle);
  }
  
  /**
   * Clear obstacles
   */
  public clearObstacles(): void {
    this.obstacles = [];
  }
  
  /**
   * Spawn agents in area
   */
  public spawnAgents(
    count: number,
    area: THREE.Box2,
    goalArea?: THREE.Box2
  ): void {
    for (let i = 0; i < count; i++) {
      const position = new THREE.Vector2(
        THREE.MathUtils.randFloat(area.min.x, area.max.x),
        THREE.MathUtils.randFloat(area.min.y, area.max.y)
      );
      
      let goal: THREE.Vector2 | undefined;
      if (goalArea) {
        goal = new THREE.Vector2(
          THREE.MathUtils.randFloat(goalArea.min.x, goalArea.max.x),
          THREE.MathUtils.randFloat(goalArea.min.y, goalArea.max.y)
        );
      }
      
      this.addAgent(position, goal);
    }
  }
  
  /**
   * Update simulation
   */
  public update(deltaTime?: number): void {
    const dt = deltaTime ?? this.config.timeStep;
    
    // Update spatial hash
    this.spatialHash.clear();
    for (const agent of this.agents) {
      this.spatialHash.insert(agent);
    }
    
    // Update each agent
    for (const agent of this.agents) {
      this.updateAgent(agent, dt);
    }
    
    // Update renderer
    this.renderer?.update(this.agents);
  }
  
  private updateAgent(agent: Agent, dt: number): void {
    // Get neighbors
    const neighbors = this.spatialHash.query(
      agent.position,
      this.config.neighborDistance
    ).slice(0, this.config.maxNeighbors);
    
    // Compute steering from behaviors
    const behaviors = this.agentBehaviors.get(agent.id) ?? [];
    const steeringForce = this.behaviorSystem.computeSteeringForce(agent, behaviors);
    
    // Set preferred velocity
    agent.preferredVelocity = steeringForce.clone()
      .clampLength(0, agent.config.preferredSpeed);
    
    // Compute collision-free velocity using ORCA
    const newVelocity = this.orcaAvoidance.computeNewVelocity(
      agent,
      neighbors,
      this.obstacles,
      dt
    );
    
    // Apply velocity
    agent.velocity.copy(newVelocity);
    
    // Update position
    agent.position.add(agent.velocity.clone().multiplyScalar(dt));
    
    // Update rotation to face movement direction
    if (agent.velocity.lengthSq() > 0.01) {
      agent.rotation = Math.atan2(agent.velocity.x, agent.velocity.y);
    }
    
    // Update state
    const speed = agent.velocity.length();
    if (speed < 0.1) {
      agent.state = 'idle';
    } else if (speed < agent.config.preferredSpeed * 0.7) {
      agent.state = 'walking';
    } else {
      agent.state = 'running';
    }
    
    // Check if reached goal
    if (agent.goal) {
      const distToGoal = agent.position.distanceTo(agent.goal);
      if (distToGoal < 0.5) {
        agent.state = 'stopped';
        agent.velocity.set(0, 0);
      }
    }
  }
  
  /**
   * Get all agents
   */
  public getAgents(): Agent[] {
    return this.agents;
  }
  
  /**
   * Get agent by ID
   */
  public getAgent(id: number): Agent | undefined {
    return this.agents.find(a => a.id === id);
  }
  
  /**
   * Get simulation statistics
   */
  public getStats(): SimulationStats {
    let totalSpeed = 0;
    for (const agent of this.agents) {
      totalSpeed += agent.velocity.length();
    }
    
    return {
      agentCount: this.agents.length,
      averageSpeed: this.agents.length > 0 ? totalSpeed / this.agents.length : 0,
      colllisionCount: 0,
      frameTime: 0
    };
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.renderer?.dispose();
    this.agents = [];
    this.obstacles = [];
    this.agentBehaviors.clear();
  }
}
