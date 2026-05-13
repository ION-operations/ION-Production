/**
 * Animation State Machine System
 * Hierarchical state machine for character animation
 * 
 * Features:
 * - State transitions with conditions
 * - Blend trees (1D, 2D)
 * - Animation layers
 * - Cross-fade transitions
 * - State behaviors (enter/exit/update)
 * - Sub-state machines
 * - Trigger/bool/float parameters
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export type ParameterType = 'float' | 'int' | 'bool' | 'trigger';

export interface Parameter {
  name: string;
  type: ParameterType;
  value: number | boolean;
}

export type ConditionOperator = 'greater' | 'less' | 'equals' | 'notEquals' | 'greaterOrEqual' | 'lessOrEqual';

export interface Condition {
  parameter: string;
  operator: ConditionOperator;
  threshold: number | boolean;
}

export interface Transition {
  id: string;
  fromState: string;
  toState: string;
  conditions: Condition[];
  duration: number;
  hasExitTime: boolean;
  exitTime: number;  // 0-1 normalized
  offset: number;    // Start position in target state
  interruptible: boolean;
}

export interface AnimationClipInfo {
  name: string;
  clip: THREE.AnimationClip;
  speed: number;
  loop: boolean;
  weight: number;
}

export interface StateConfig {
  name: string;
  animation?: AnimationClipInfo;
  blendTree?: BlendTree;
  transitions: Transition[];
  behaviors: StateBehavior[];
  isDefault?: boolean;
}

export interface BlendTreeNode {
  type: 'clip' | '1d' | '2d' | 'direct';
  animation?: AnimationClipInfo;
  children?: BlendTreeChild[];
  parameter?: string;
  parameterX?: string;
  parameterY?: string;
}

export interface BlendTreeChild {
  node: BlendTreeNode;
  threshold?: number;       // For 1D
  position?: THREE.Vector2; // For 2D
  weight?: number;          // For direct
}

export interface BlendTree {
  root: BlendTreeNode;
}

export interface StateBehavior {
  onEnter?: () => void;
  onUpdate?: (dt: number) => void;
  onExit?: () => void;
}

export interface LayerConfig {
  name: string;
  weight: number;
  blendMode: 'override' | 'additive';
  avatarMask?: string[];  // Bone names to include
  defaultState: string;
}

// ============================================
// BLEND TREE EVALUATOR
// ============================================

export class BlendTreeEvaluator {
  private mixer: THREE.AnimationMixer;
  private parameters: Map<string, Parameter>;
  
  constructor(mixer: THREE.AnimationMixer, parameters: Map<string, Parameter>) {
    this.mixer = mixer;
    this.parameters = parameters;
  }
  
  /**
   * Evaluate blend tree and return weighted animations
   */
  public evaluate(tree: BlendTree): Map<THREE.AnimationAction, number> {
    const weights = new Map<THREE.AnimationAction, number>();
    this.evaluateNode(tree.root, weights, 1.0);
    return weights;
  }
  
  private evaluateNode(
    node: BlendTreeNode,
    weights: Map<THREE.AnimationAction, number>,
    parentWeight: number
  ): void {
    switch (node.type) {
      case 'clip':
        if (node.animation) {
          const action = this.mixer.clipAction(node.animation.clip);
          const currentWeight = weights.get(action) || 0;
          weights.set(action, currentWeight + parentWeight);
        }
        break;
        
      case '1d':
        this.evaluate1D(node, weights, parentWeight);
        break;
        
      case '2d':
        this.evaluate2D(node, weights, parentWeight);
        break;
        
      case 'direct':
        this.evaluateDirect(node, weights, parentWeight);
        break;
    }
  }
  
  private evaluate1D(
    node: BlendTreeNode,
    weights: Map<THREE.AnimationAction, number>,
    parentWeight: number
  ): void {
    if (!node.children || !node.parameter) return;
    
    const param = this.parameters.get(node.parameter);
    if (!param || typeof param.value !== 'number') return;
    
    const value = param.value;
    const sortedChildren = [...node.children].sort(
      (a, b) => (a.threshold ?? 0) - (b.threshold ?? 0)
    );
    
    // Find the two nodes to blend between
    let lowChild = sortedChildren[0];
    let highChild = sortedChildren[sortedChildren.length - 1];
    
    for (let i = 0; i < sortedChildren.length - 1; i++) {
      const current = sortedChildren[i];
      const next = sortedChildren[i + 1];
      
      if (value >= (current.threshold ?? 0) && value <= (next.threshold ?? 0)) {
        lowChild = current;
        highChild = next;
        break;
      }
    }
    
    // Calculate blend factor
    const lowThreshold = lowChild.threshold ?? 0;
    const highThreshold = highChild.threshold ?? 0;
    
    let blend = 0;
    if (highThreshold !== lowThreshold) {
      blend = (value - lowThreshold) / (highThreshold - lowThreshold);
    }
    
    // Clamp blend
    blend = Math.max(0, Math.min(1, blend));
    
    // Apply weights
    this.evaluateNode(lowChild.node, weights, parentWeight * (1 - blend));
    this.evaluateNode(highChild.node, weights, parentWeight * blend);
  }
  
  private evaluate2D(
    node: BlendTreeNode,
    weights: Map<THREE.AnimationAction, number>,
    parentWeight: number
  ): void {
    if (!node.children || !node.parameterX || !node.parameterY) return;
    
    const paramX = this.parameters.get(node.parameterX);
    const paramY = this.parameters.get(node.parameterY);
    if (!paramX || !paramY) return;
    if (typeof paramX.value !== 'number' || typeof paramY.value !== 'number') return;
    
    const point = new THREE.Vector2(paramX.value as number, paramY.value as number);
    
    // Calculate weights using barycentric coordinates or nearest neighbor
    // For simplicity, using distance-based weighting
    let totalWeight = 0;
    const childWeights: number[] = [];
    
    for (const child of node.children) {
      const childPos = child.position ?? new THREE.Vector2(0, 0);
      const distance = point.distanceTo(childPos);
      const weight = distance === 0 ? 1000 : 1 / distance;
      childWeights.push(weight);
      totalWeight += weight;
    }
    
    // Normalize and apply
    for (let i = 0; i < node.children.length; i++) {
      const normalizedWeight = childWeights[i] / totalWeight;
      this.evaluateNode(node.children[i].node, weights, parentWeight * normalizedWeight);
    }
  }
  
  private evaluateDirect(
    node: BlendTreeNode,
    weights: Map<THREE.AnimationAction, number>,
    parentWeight: number
  ): void {
    if (!node.children) return;
    
    for (const child of node.children) {
      const childWeight = child.weight ?? 0;
      this.evaluateNode(child.node, weights, parentWeight * childWeight);
    }
  }
}

// ============================================
// ANIMATION STATE
// ============================================

export class AnimationState {
  public readonly name: string;
  public readonly config: StateConfig;
  
  private mixer: THREE.AnimationMixer;
  private action: THREE.AnimationAction | null = null;
  private blendTreeEvaluator: BlendTreeEvaluator | null = null;
  private activeActions: Map<THREE.AnimationAction, number> = new Map();
  private normalizedTime: number = 0;
  private isPlaying: boolean = false;
  
  constructor(
    config: StateConfig,
    mixer: THREE.AnimationMixer,
    parameters: Map<string, Parameter>
  ) {
    this.name = config.name;
    this.config = config;
    this.mixer = mixer;
    
    if (config.animation) {
      this.action = mixer.clipAction(config.animation.clip);
      this.action.setLoop(
        config.animation.loop ? THREE.LoopRepeat : THREE.LoopOnce,
        Infinity
      );
      this.action.clampWhenFinished = !config.animation.loop;
      this.action.timeScale = config.animation.speed;
    }
    
    if (config.blendTree) {
      this.blendTreeEvaluator = new BlendTreeEvaluator(mixer, parameters);
    }
  }
  
  public enter(offset: number = 0): void {
    this.isPlaying = true;
    this.normalizedTime = offset;
    
    // Call behavior callbacks
    for (const behavior of this.config.behaviors) {
      behavior.onEnter?.();
    }
    
    if (this.action) {
      this.action.reset();
      this.action.time = offset * this.action.getClip().duration;
      this.action.play();
    }
    
    // Start blend tree actions
    if (this.blendTreeEvaluator && this.config.blendTree) {
      this.activeActions = this.blendTreeEvaluator.evaluate(this.config.blendTree);
      for (const [action] of this.activeActions) {
        action.reset();
        action.time = offset * action.getClip().duration;
        action.play();
      }
    }
  }
  
  public exit(): void {
    this.isPlaying = false;
    
    // Call behavior callbacks
    for (const behavior of this.config.behaviors) {
      behavior.onExit?.();
    }
  }
  
  public update(dt: number, parameters: Map<string, Parameter>): void {
    if (!this.isPlaying) return;
    
    // Update normalized time
    if (this.action) {
      const duration = this.action.getClip().duration;
      this.normalizedTime = (this.action.time % duration) / duration;
    }
    
    // Call behavior callbacks
    for (const behavior of this.config.behaviors) {
      behavior.onUpdate?.(dt);
    }
    
    // Update blend tree weights
    if (this.blendTreeEvaluator && this.config.blendTree) {
      const newWeights = this.blendTreeEvaluator.evaluate(this.config.blendTree);
      
      // Update action weights
      for (const [action, weight] of newWeights) {
        action.setEffectiveWeight(weight);
        if (!this.activeActions.has(action)) {
          action.play();
        }
      }
      
      // Stop actions no longer needed
      for (const [action] of this.activeActions) {
        if (!newWeights.has(action)) {
          action.stop();
        }
      }
      
      this.activeActions = newWeights;
    }
  }
  
  public getNormalizedTime(): number {
    return this.normalizedTime;
  }
  
  public getWeight(): number {
    return this.action?.getEffectiveWeight() ?? 1.0;
  }
  
  public setWeight(weight: number): void {
    if (this.action) {
      this.action.setEffectiveWeight(weight);
    }
    
    for (const [action] of this.activeActions) {
      action.setEffectiveWeight(weight);
    }
  }
  
  public stop(): void {
    this.action?.stop();
    for (const [action] of this.activeActions) {
      action.stop();
    }
  }
}

// ============================================
// ANIMATION LAYER
// ============================================

export class AnimationLayer {
  public readonly name: string;
  public weight: number;
  public blendMode: 'override' | 'additive';
  
  private states: Map<string, AnimationState> = new Map();
  private currentState: AnimationState | null = null;
  private previousState: AnimationState | null = null;
  private transitionProgress: number = 1;
  private transitionDuration: number = 0;
  private activeTransition: Transition | null = null;
  private defaultStateName: string;
  private parameters: Map<string, Parameter>;
  
  constructor(
    config: LayerConfig,
    mixer: THREE.AnimationMixer,
    parameters: Map<string, Parameter>
  ) {
    this.name = config.name;
    this.weight = config.weight;
    this.blendMode = config.blendMode;
    this.defaultStateName = config.defaultState;
    this.parameters = parameters;
  }
  
  public addState(state: AnimationState): void {
    this.states.set(state.name, state);
    
    if (state.config.isDefault || state.name === this.defaultStateName) {
      this.currentState = state;
      state.enter();
    }
  }
  
  public update(dt: number): void {
    // Handle transition
    if (this.transitionProgress < 1 && this.activeTransition) {
      this.transitionProgress += dt / this.transitionDuration;
      this.transitionProgress = Math.min(1, this.transitionProgress);
      
      // Update weights
      if (this.previousState) {
        this.previousState.setWeight((1 - this.transitionProgress) * this.weight);
      }
      if (this.currentState) {
        this.currentState.setWeight(this.transitionProgress * this.weight);
      }
      
      // Complete transition
      if (this.transitionProgress >= 1) {
        this.previousState?.stop();
        this.previousState?.exit();
        this.previousState = null;
        this.activeTransition = null;
      }
    }
    
    // Update current state
    this.currentState?.update(dt, this.parameters);
    this.previousState?.update(dt, this.parameters);
    
    // Check for transitions
    if (this.currentState && !this.activeTransition) {
      this.checkTransitions();
    }
  }
  
  private checkTransitions(): void {
    if (!this.currentState) return;
    
    for (const transition of this.currentState.config.transitions) {
      // Check exit time
      if (transition.hasExitTime) {
        if (this.currentState.getNormalizedTime() < transition.exitTime) {
          continue;
        }
      }
      
      // Check conditions
      if (this.evaluateConditions(transition.conditions)) {
        this.startTransition(transition);
        break;
      }
    }
  }
  
  private evaluateConditions(conditions: Condition[]): boolean {
    for (const condition of conditions) {
      const param = this.parameters.get(condition.parameter);
      if (!param) return false;
      
      const value = param.value;
      
      // Handle trigger specially
      if (param.type === 'trigger') {
        if (value !== true) return false;
        continue;
      }
      
      // Evaluate condition
      let result = false;
      switch (condition.operator) {
        case 'greater':
          result = value > condition.threshold;
          break;
        case 'less':
          result = value < condition.threshold;
          break;
        case 'equals':
          result = value === condition.threshold;
          break;
        case 'notEquals':
          result = value !== condition.threshold;
          break;
        case 'greaterOrEqual':
          result = value >= condition.threshold;
          break;
        case 'lessOrEqual':
          result = value <= condition.threshold;
          break;
      }
      
      if (!result) return false;
    }
    
    return true;
  }
  
  private startTransition(transition: Transition): void {
    const targetState = this.states.get(transition.toState);
    if (!targetState) return;
    
    this.previousState = this.currentState;
    this.currentState = targetState;
    this.activeTransition = transition;
    this.transitionDuration = transition.duration;
    this.transitionProgress = 0;
    
    // Enter new state
    targetState.enter(transition.offset);
    
    // Reset triggers used in this transition
    for (const condition of transition.conditions) {
      const param = this.parameters.get(condition.parameter);
      if (param?.type === 'trigger') {
        param.value = false;
      }
    }
  }
  
  public forceState(stateName: string): void {
    const state = this.states.get(stateName);
    if (!state) return;
    
    this.previousState?.stop();
    this.previousState?.exit();
    this.currentState?.stop();
    this.currentState?.exit();
    
    this.currentState = state;
    this.previousState = null;
    this.activeTransition = null;
    this.transitionProgress = 1;
    
    state.enter();
    state.setWeight(this.weight);
  }
  
  public getCurrentState(): string | null {
    return this.currentState?.name ?? null;
  }
  
  public isInTransition(): boolean {
    return this.transitionProgress < 1;
  }
}

// ============================================
// MAIN ANIMATION STATE MACHINE
// ============================================

export class AnimationStateMachine {
  private mixer: THREE.AnimationMixer;
  private parameters: Map<string, Parameter> = new Map();
  private layers: Map<string, AnimationLayer> = new Map();
  
  constructor(target: THREE.Object3D) {
    this.mixer = new THREE.AnimationMixer(target);
  }
  
  // ========== PARAMETERS ==========
  
  public addParameter(name: string, type: ParameterType, defaultValue: number | boolean = 0): void {
    this.parameters.set(name, {
      name,
      type,
      value: defaultValue
    });
  }
  
  public setFloat(name: string, value: number): void {
    const param = this.parameters.get(name);
    if (param && param.type === 'float') {
      param.value = value;
    }
  }
  
  public setInt(name: string, value: number): void {
    const param = this.parameters.get(name);
    if (param && param.type === 'int') {
      param.value = Math.round(value);
    }
  }
  
  public setBool(name: string, value: boolean): void {
    const param = this.parameters.get(name);
    if (param && param.type === 'bool') {
      param.value = value;
    }
  }
  
  public setTrigger(name: string): void {
    const param = this.parameters.get(name);
    if (param && param.type === 'trigger') {
      param.value = true;
    }
  }
  
  public resetTrigger(name: string): void {
    const param = this.parameters.get(name);
    if (param && param.type === 'trigger') {
      param.value = false;
    }
  }
  
  public getFloat(name: string): number {
    return this.parameters.get(name)?.value as number ?? 0;
  }
  
  public getBool(name: string): boolean {
    return this.parameters.get(name)?.value as boolean ?? false;
  }
  
  // ========== LAYERS ==========
  
  public addLayer(config: LayerConfig): AnimationLayer {
    const layer = new AnimationLayer(config, this.mixer, this.parameters);
    this.layers.set(config.name, layer);
    return layer;
  }
  
  public getLayer(name: string): AnimationLayer | undefined {
    return this.layers.get(name);
  }
  
  public setLayerWeight(name: string, weight: number): void {
    const layer = this.layers.get(name);
    if (layer) {
      layer.weight = weight;
    }
  }
  
  // ========== STATES ==========
  
  public addState(layerName: string, config: StateConfig): void {
    const layer = this.layers.get(layerName);
    if (!layer) {
      console.warn(`Layer "${layerName}" not found`);
      return;
    }
    
    const state = new AnimationState(config, this.mixer, this.parameters);
    layer.addState(state);
  }
  
  public forceState(layerName: string, stateName: string): void {
    this.layers.get(layerName)?.forceState(stateName);
  }
  
  // ========== UPDATE ==========
  
  public update(deltaTime: number): void {
    // Update all layers
    for (const layer of this.layers.values()) {
      layer.update(deltaTime);
    }
    
    // Update mixer
    this.mixer.update(deltaTime);
  }
  
  // ========== UTILITIES ==========
  
  public getMixer(): THREE.AnimationMixer {
    return this.mixer;
  }
  
  public getCurrentState(layerName: string = 'Base'): string | null {
    return this.layers.get(layerName)?.getCurrentState() ?? null;
  }
  
  public isInTransition(layerName: string = 'Base'): boolean {
    return this.layers.get(layerName)?.isInTransition() ?? false;
  }
  
  /**
   * Create a simple locomotion blend tree
   */
  public static createLocomotionBlendTree(
    idleClip: THREE.AnimationClip,
    walkClip: THREE.AnimationClip,
    runClip: THREE.AnimationClip
  ): BlendTree {
    return {
      root: {
        type: '1d',
        parameter: 'Speed',
        children: [
          {
            threshold: 0,
            node: {
              type: 'clip',
              animation: { name: 'Idle', clip: idleClip, speed: 1, loop: true, weight: 1 }
            }
          },
          {
            threshold: 0.5,
            node: {
              type: 'clip',
              animation: { name: 'Walk', clip: walkClip, speed: 1, loop: true, weight: 1 }
            }
          },
          {
            threshold: 1.0,
            node: {
              type: 'clip',
              animation: { name: 'Run', clip: runClip, speed: 1, loop: true, weight: 1 }
            }
          }
        ]
      }
    };
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.mixer.stopAllAction();
    this.parameters.clear();
    this.layers.clear();
  }
}

