/**
 * Motion Matching Animation System
 * Next-generation animation technique for character locomotion
 * 
 * Features:
 * - Pose matching via feature vectors
 * - Trajectory prediction
 * - KD-tree for fast search
 * - Inertial blending
 * - Root motion handling
 * - Responsive to input
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export interface MotionFeature {
  // Trajectory (future positions/directions)
  trajectoryPositions: THREE.Vector3[];  // N future points
  trajectoryDirections: THREE.Vector3[]; // N future facing directions
  
  // Pose
  leftFootPosition: THREE.Vector3;
  rightFootPosition: THREE.Vector3;
  leftFootVelocity: THREE.Vector3;
  rightFootVelocity: THREE.Vector3;
  hipVelocity: THREE.Vector3;
  
  // Additional features
  speed: number;
  facing: THREE.Vector3;
}

export interface MotionFrame {
  time: number;
  clipIndex: number;
  frameIndex: number;
  features: MotionFeature;
  rootPosition: THREE.Vector3;
  rootRotation: THREE.Quaternion;
  pose: Float32Array;  // Bone transforms
}

export interface MotionClip {
  name: string;
  frames: MotionFrame[];
  duration: number;
  frameRate: number;
  isLooping: boolean;
  tags: string[];
}

export interface MotionDatabase {
  clips: MotionClip[];
  frames: MotionFrame[];
  featureWeights: FeatureWeights;
  kdTree: KDTree | null;
}

export interface FeatureWeights {
  trajectoryPosition: number;
  trajectoryDirection: number;
  footPosition: number;
  footVelocity: number;
  hipVelocity: number;
}

export interface MatchResult {
  frame: MotionFrame;
  cost: number;
  needsTransition: boolean;
}

export interface TrajectoryPoint {
  position: THREE.Vector3;
  direction: THREE.Vector3;
  time: number;
}

// ============================================
// KD-TREE FOR FAST MATCHING
// ============================================

interface KDNode {
  frame: MotionFrame;
  featureVector: number[];
  left: KDNode | null;
  right: KDNode | null;
  splitDimension: number;
}

export class KDTree {
  private root: KDNode | null = null;
  private dimensions: number;
  
  constructor(frames: MotionFrame[], dimensions: number) {
    this.dimensions = dimensions;
    
    if (frames.length > 0) {
      const frameData = frames.map(f => ({
        frame: f,
        featureVector: this.extractFeatureVector(f.features)
      }));
      
      this.root = this.buildTree(frameData, 0);
    }
  }
  
  private buildTree(data: { frame: MotionFrame; featureVector: number[] }[], depth: number): KDNode | null {
    if (data.length === 0) return null;
    
    const dimension = depth % this.dimensions;
    
    // Sort by current dimension
    data.sort((a, b) => a.featureVector[dimension] - b.featureVector[dimension]);
    
    const median = Math.floor(data.length / 2);
    
    return {
      frame: data[median].frame,
      featureVector: data[median].featureVector,
      left: this.buildTree(data.slice(0, median), depth + 1),
      right: this.buildTree(data.slice(median + 1), depth + 1),
      splitDimension: dimension
    };
  }
  
  public findNearest(query: number[], k: number = 1): { frame: MotionFrame; distance: number }[] {
    const results: { frame: MotionFrame; distance: number }[] = [];
    
    if (!this.root) return results;
    
    this.searchNearest(this.root, query, k, results);
    
    return results.sort((a, b) => a.distance - b.distance).slice(0, k);
  }
  
  private searchNearest(
    node: KDNode | null,
    query: number[],
    k: number,
    results: { frame: MotionFrame; distance: number }[]
  ): void {
    if (!node) return;
    
    const distance = this.calculateDistance(query, node.featureVector);
    
    // Add to results
    if (results.length < k) {
      results.push({ frame: node.frame, distance });
      results.sort((a, b) => a.distance - b.distance);
    } else if (distance < results[results.length - 1].distance) {
      results[results.length - 1] = { frame: node.frame, distance };
      results.sort((a, b) => a.distance - b.distance);
    }
    
    // Determine which subtree to search first
    const splitValue = node.featureVector[node.splitDimension];
    const queryValue = query[node.splitDimension];
    
    const nearSubtree = queryValue < splitValue ? node.left : node.right;
    const farSubtree = queryValue < splitValue ? node.right : node.left;
    
    // Search near subtree
    this.searchNearest(nearSubtree, query, k, results);
    
    // Check if we need to search far subtree
    const splitDistance = Math.abs(queryValue - splitValue);
    if (results.length < k || splitDistance < results[results.length - 1].distance) {
      this.searchNearest(farSubtree, query, k, results);
    }
  }
  
  private calculateDistance(a: number[], b: number[]): number {
    let sum = 0;
    for (let i = 0; i < Math.min(a.length, b.length); i++) {
      const diff = a[i] - b[i];
      sum += diff * diff;
    }
    return Math.sqrt(sum);
  }
  
  private extractFeatureVector(features: MotionFeature): number[] {
    const vector: number[] = [];
    
    // Trajectory positions
    for (const pos of features.trajectoryPositions) {
      vector.push(pos.x, pos.y, pos.z);
    }
    
    // Trajectory directions
    for (const dir of features.trajectoryDirections) {
      vector.push(dir.x, dir.z);  // Only horizontal
    }
    
    // Foot positions
    vector.push(
      features.leftFootPosition.x,
      features.leftFootPosition.y,
      features.leftFootPosition.z,
      features.rightFootPosition.x,
      features.rightFootPosition.y,
      features.rightFootPosition.z
    );
    
    // Velocities
    vector.push(
      features.leftFootVelocity.x,
      features.leftFootVelocity.y,
      features.leftFootVelocity.z,
      features.rightFootVelocity.x,
      features.rightFootVelocity.y,
      features.rightFootVelocity.z,
      features.hipVelocity.x,
      features.hipVelocity.y,
      features.hipVelocity.z
    );
    
    return vector;
  }
}

// ============================================
// TRAJECTORY GENERATOR
// ============================================

export class TrajectoryGenerator {
  private trajectoryLength: number;
  private trajectoryInterval: number;
  
  private history: TrajectoryPoint[] = [];
  private maxHistoryLength: number = 10;
  
  constructor(trajectoryLength: number = 5, trajectoryInterval: number = 0.2) {
    this.trajectoryLength = trajectoryLength;
    this.trajectoryInterval = trajectoryInterval;
  }
  
  /**
   * Generate desired trajectory from input
   */
  public generateTrajectory(
    currentPosition: THREE.Vector3,
    currentDirection: THREE.Vector3,
    inputDirection: THREE.Vector3,
    inputSpeed: number,
    deltaTime: number
  ): TrajectoryPoint[] {
    const trajectory: TrajectoryPoint[] = [];
    
    // Blend current direction with input
    const blendFactor = 0.3;
    const targetDirection = inputDirection.lengthSq() > 0.01
      ? inputDirection.clone().normalize()
      : currentDirection.clone();
    
    let position = currentPosition.clone();
    let direction = currentDirection.clone();
    
    for (let i = 0; i < this.trajectoryLength; i++) {
      const time = (i + 1) * this.trajectoryInterval;
      
      // Smoothly blend towards target direction
      direction.lerp(targetDirection, blendFactor);
      direction.normalize();
      
      // Move along trajectory
      const velocity = direction.clone().multiplyScalar(inputSpeed);
      position = position.clone().add(velocity.clone().multiplyScalar(this.trajectoryInterval));
      
      trajectory.push({
        position: position.clone(),
        direction: direction.clone(),
        time
      });
    }
    
    // Store in history
    this.history.unshift({
      position: currentPosition.clone(),
      direction: currentDirection.clone(),
      time: 0
    });
    
    if (this.history.length > this.maxHistoryLength) {
      this.history.pop();
    }
    
    return trajectory;
  }
  
  /**
   * Get trajectory as feature vectors
   */
  public trajectoryToFeature(trajectory: TrajectoryPoint[], rootPosition: THREE.Vector3): {
    positions: THREE.Vector3[];
    directions: THREE.Vector3[];
  } {
    const positions: THREE.Vector3[] = [];
    const directions: THREE.Vector3[] = [];
    
    for (const point of trajectory) {
      // Convert to local space relative to current root
      const localPos = point.position.clone().sub(rootPosition);
      positions.push(localPos);
      directions.push(point.direction.clone());
    }
    
    return { positions, directions };
  }
}

// ============================================
// INERTIAL BLENDER
// ============================================

export class InertialBlender {
  private blendDuration: number;
  private blendTime: number = 0;
  private isBlending: boolean = false;
  
  private sourcePose: Float32Array | null = null;
  private sourceVelocity: Float32Array | null = null;
  private targetPose: Float32Array | null = null;
  
  constructor(blendDuration: number = 0.2) {
    this.blendDuration = blendDuration;
  }
  
  /**
   * Start blending to new pose
   */
  public startBlend(
    currentPose: Float32Array,
    currentVelocity: Float32Array,
    targetPose: Float32Array
  ): void {
    this.sourcePose = currentPose.slice();
    this.sourceVelocity = currentVelocity.slice();
    this.targetPose = targetPose.slice();
    this.blendTime = 0;
    this.isBlending = true;
  }
  
  /**
   * Update blend and return interpolated pose
   */
  public update(deltaTime: number, currentTargetPose: Float32Array): Float32Array {
    if (!this.isBlending || !this.sourcePose || !this.sourceVelocity) {
      return currentTargetPose;
    }
    
    this.blendTime += deltaTime;
    
    if (this.blendTime >= this.blendDuration) {
      this.isBlending = false;
      return currentTargetPose;
    }
    
    const t = this.blendTime / this.blendDuration;
    
    // Cubic Hermite interpolation for smooth blending
    const t2 = t * t;
    const t3 = t2 * t;
    
    // Hermite basis functions
    const h00 = 2 * t3 - 3 * t2 + 1;
    const h10 = t3 - 2 * t2 + t;
    const h01 = -2 * t3 + 3 * t2;
    const h11 = t3 - t2;
    
    const result = new Float32Array(currentTargetPose.length);
    
    for (let i = 0; i < result.length; i++) {
      const p0 = this.sourcePose[i];
      const m0 = this.sourceVelocity[i] * this.blendDuration;
      const p1 = currentTargetPose[i];
      const m1 = 0;  // Assume zero velocity at target
      
      result[i] = h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1;
    }
    
    return result;
  }
  
  public isActive(): boolean {
    return this.isBlending;
  }
}

// ============================================
// MOTION DATABASE BUILDER
// ============================================

export class MotionDatabaseBuilder {
  private clips: MotionClip[] = [];
  private featureWeights: FeatureWeights = {
    trajectoryPosition: 1.0,
    trajectoryDirection: 1.0,
    footPosition: 0.75,
    footVelocity: 1.0,
    hipVelocity: 1.0
  };
  
  /**
   * Add animation clip to database
   */
  public addClip(
    name: string,
    clip: THREE.AnimationClip,
    skeleton: THREE.Skeleton,
    tags: string[] = [],
    isLooping: boolean = true
  ): void {
    const frames = this.extractFrames(clip, skeleton);
    
    this.clips.push({
      name,
      frames,
      duration: clip.duration,
      frameRate: 30,  // Assuming 30fps
      isLooping,
      tags
    });
  }
  
  private extractFrames(clip: THREE.AnimationClip, skeleton: THREE.Skeleton): MotionFrame[] {
    const frames: MotionFrame[] = [];
    const frameRate = 30;
    const frameCount = Math.ceil(clip.duration * frameRate);
    
    for (let i = 0; i < frameCount; i++) {
      const time = i / frameRate;
      
      // Extract pose at this time
      const pose = this.samplePoseAtTime(clip, skeleton, time);
      
      // Extract features (simplified - real implementation needs proper bone tracking)
      const features = this.extractFeatures(pose, time);
      
      frames.push({
        time,
        clipIndex: this.clips.length,
        frameIndex: i,
        features,
        rootPosition: new THREE.Vector3(),
        rootRotation: new THREE.Quaternion(),
        pose
      });
    }
    
    // Compute velocities
    this.computeVelocities(frames);
    
    return frames;
  }
  
  private samplePoseAtTime(
    clip: THREE.AnimationClip,
    skeleton: THREE.Skeleton,
    time: number
  ): Float32Array {
    const boneCount = skeleton.bones.length;
    const pose = new Float32Array(boneCount * 7);  // position (3) + quaternion (4)
    
    // Sample each track
    for (let i = 0; i < boneCount; i++) {
      const bone = skeleton.bones[i];
      
      pose[i * 7] = bone.position.x;
      pose[i * 7 + 1] = bone.position.y;
      pose[i * 7 + 2] = bone.position.z;
      pose[i * 7 + 3] = bone.quaternion.x;
      pose[i * 7 + 4] = bone.quaternion.y;
      pose[i * 7 + 5] = bone.quaternion.z;
      pose[i * 7 + 6] = bone.quaternion.w;
    }
    
    return pose;
  }
  
  private extractFeatures(pose: Float32Array, time: number): MotionFeature {
    // Simplified feature extraction
    return {
      trajectoryPositions: [
        new THREE.Vector3(0, 0, 0.2),
        new THREE.Vector3(0, 0, 0.4),
        new THREE.Vector3(0, 0, 0.6),
        new THREE.Vector3(0, 0, 0.8),
        new THREE.Vector3(0, 0, 1.0)
      ],
      trajectoryDirections: [
        new THREE.Vector3(0, 0, 1),
        new THREE.Vector3(0, 0, 1),
        new THREE.Vector3(0, 0, 1),
        new THREE.Vector3(0, 0, 1),
        new THREE.Vector3(0, 0, 1)
      ],
      leftFootPosition: new THREE.Vector3(-0.1, 0, 0),
      rightFootPosition: new THREE.Vector3(0.1, 0, 0),
      leftFootVelocity: new THREE.Vector3(),
      rightFootVelocity: new THREE.Vector3(),
      hipVelocity: new THREE.Vector3(),
      speed: 0,
      facing: new THREE.Vector3(0, 0, 1)
    };
  }
  
  private computeVelocities(frames: MotionFrame[]): void {
    const dt = 1 / 30;  // Assuming 30fps
    
    for (let i = 1; i < frames.length; i++) {
      const prev = frames[i - 1];
      const curr = frames[i];
      
      curr.features.leftFootVelocity = curr.features.leftFootPosition.clone()
        .sub(prev.features.leftFootPosition)
        .divideScalar(dt);
      
      curr.features.rightFootVelocity = curr.features.rightFootPosition.clone()
        .sub(prev.features.rightFootPosition)
        .divideScalar(dt);
    }
    
    // First frame copies from second
    if (frames.length > 1) {
      frames[0].features.leftFootVelocity.copy(frames[1].features.leftFootVelocity);
      frames[0].features.rightFootVelocity.copy(frames[1].features.rightFootVelocity);
    }
  }
  
  /**
   * Build the final database with KD-tree
   */
  public build(): MotionDatabase {
    // Collect all frames
    const allFrames: MotionFrame[] = [];
    for (const clip of this.clips) {
      allFrames.push(...clip.frames);
    }
    
    // Build KD-tree
    const featureDimensions = 5 * 3 + 5 * 2 + 6 + 9;  // trajectory + feet + velocities
    const kdTree = new KDTree(allFrames, featureDimensions);
    
    return {
      clips: this.clips,
      frames: allFrames,
      featureWeights: this.featureWeights,
      kdTree
    };
  }
}

// ============================================
// MAIN MOTION MATCHING SYSTEM
// ============================================

export class MotionMatchingSystem {
  private database: MotionDatabase;
  private trajectoryGenerator: TrajectoryGenerator;
  private inertialBlender: InertialBlender;
  
  private currentFrame: MotionFrame | null = null;
  private currentPose: Float32Array | null = null;
  private poseVelocity: Float32Array | null = null;
  
  private rootPosition: THREE.Vector3 = new THREE.Vector3();
  private rootRotation: THREE.Quaternion = new THREE.Quaternion();
  
  private searchInterval: number = 0.1;  // Search every 100ms
  private timeSinceLastSearch: number = 0;
  
  constructor(database: MotionDatabase) {
    this.database = database;
    this.trajectoryGenerator = new TrajectoryGenerator();
    this.inertialBlender = new InertialBlender();
    
    // Initialize with first frame
    if (database.frames.length > 0) {
      this.currentFrame = database.frames[0];
      this.currentPose = this.currentFrame.pose.slice();
      this.poseVelocity = new Float32Array(this.currentPose.length);
    }
  }
  
  /**
   * Update motion matching
   */
  public update(
    inputDirection: THREE.Vector3,
    inputSpeed: number,
    deltaTime: number
  ): { pose: Float32Array; rootPosition: THREE.Vector3; rootRotation: THREE.Quaternion } | null {
    if (!this.currentFrame || !this.currentPose) {
      return null;
    }
    
    // Generate desired trajectory
    const currentDirection = new THREE.Vector3(0, 0, 1).applyQuaternion(this.rootRotation);
    const trajectory = this.trajectoryGenerator.generateTrajectory(
      this.rootPosition,
      currentDirection,
      inputDirection,
      inputSpeed,
      deltaTime
    );
    
    // Periodic search for best matching frame
    this.timeSinceLastSearch += deltaTime;
    
    if (this.timeSinceLastSearch >= this.searchInterval) {
      this.timeSinceLastSearch = 0;
      
      const match = this.findBestMatch(trajectory);
      
      if (match && match.needsTransition) {
        // Start blend to new frame
        this.inertialBlender.startBlend(
          this.currentPose,
          this.poseVelocity!,
          match.frame.pose
        );
        this.currentFrame = match.frame;
      }
    }
    
    // Advance current animation
    const clip = this.database.clips[this.currentFrame.clipIndex];
    let nextFrameIndex = this.currentFrame.frameIndex + 1;
    
    if (nextFrameIndex >= clip.frames.length) {
      if (clip.isLooping) {
        nextFrameIndex = 0;
      } else {
        nextFrameIndex = clip.frames.length - 1;
      }
    }
    
    const nextFrame = clip.frames[nextFrameIndex];
    
    // Blend or use direct pose
    let outputPose: Float32Array;
    if (this.inertialBlender.isActive()) {
      outputPose = this.inertialBlender.update(deltaTime, nextFrame.pose);
    } else {
      outputPose = nextFrame.pose;
    }
    
    // Update pose velocity
    if (this.poseVelocity && this.currentPose) {
      for (let i = 0; i < outputPose.length; i++) {
        this.poseVelocity[i] = (outputPose[i] - this.currentPose[i]) / deltaTime;
      }
    }
    
    this.currentPose = outputPose;
    this.currentFrame = nextFrame;
    
    // Update root motion
    this.updateRootMotion(nextFrame, deltaTime);
    
    return {
      pose: outputPose,
      rootPosition: this.rootPosition.clone(),
      rootRotation: this.rootRotation.clone()
    };
  }
  
  private findBestMatch(trajectory: TrajectoryPoint[]): MatchResult | null {
    if (!this.database.kdTree || !this.currentFrame) {
      return null;
    }
    
    // Build query feature
    const { positions, directions } = this.trajectoryGenerator.trajectoryToFeature(
      trajectory,
      this.rootPosition
    );
    
    const queryFeature: MotionFeature = {
      trajectoryPositions: positions,
      trajectoryDirections: directions,
      leftFootPosition: this.currentFrame.features.leftFootPosition,
      rightFootPosition: this.currentFrame.features.rightFootPosition,
      leftFootVelocity: this.currentFrame.features.leftFootVelocity,
      rightFootVelocity: this.currentFrame.features.rightFootVelocity,
      hipVelocity: this.currentFrame.features.hipVelocity,
      speed: 0,
      facing: new THREE.Vector3(0, 0, 1)
    };
    
    // Convert to vector
    const queryVector = this.featureToVector(queryFeature);
    
    // Search KD-tree
    const results = this.database.kdTree.findNearest(queryVector, 3);
    
    if (results.length === 0) {
      return null;
    }
    
    const best = results[0];
    
    // Check if we should transition
    const currentClip = this.database.clips[this.currentFrame.clipIndex];
    const bestClip = this.database.clips[best.frame.clipIndex];
    
    const needsTransition = best.frame.clipIndex !== this.currentFrame.clipIndex ||
                           Math.abs(best.frame.frameIndex - this.currentFrame.frameIndex) > 10;
    
    return {
      frame: best.frame,
      cost: best.distance,
      needsTransition
    };
  }
  
  private featureToVector(feature: MotionFeature): number[] {
    const vector: number[] = [];
    const weights = this.database.featureWeights;
    
    // Trajectory positions
    for (const pos of feature.trajectoryPositions) {
      vector.push(pos.x * weights.trajectoryPosition);
      vector.push(pos.y * weights.trajectoryPosition);
      vector.push(pos.z * weights.trajectoryPosition);
    }
    
    // Trajectory directions
    for (const dir of feature.trajectoryDirections) {
      vector.push(dir.x * weights.trajectoryDirection);
      vector.push(dir.z * weights.trajectoryDirection);
    }
    
    // Foot positions
    vector.push(feature.leftFootPosition.x * weights.footPosition);
    vector.push(feature.leftFootPosition.y * weights.footPosition);
    vector.push(feature.leftFootPosition.z * weights.footPosition);
    vector.push(feature.rightFootPosition.x * weights.footPosition);
    vector.push(feature.rightFootPosition.y * weights.footPosition);
    vector.push(feature.rightFootPosition.z * weights.footPosition);
    
    // Velocities
    vector.push(feature.leftFootVelocity.x * weights.footVelocity);
    vector.push(feature.leftFootVelocity.y * weights.footVelocity);
    vector.push(feature.leftFootVelocity.z * weights.footVelocity);
    vector.push(feature.rightFootVelocity.x * weights.footVelocity);
    vector.push(feature.rightFootVelocity.y * weights.footVelocity);
    vector.push(feature.rightFootVelocity.z * weights.footVelocity);
    vector.push(feature.hipVelocity.x * weights.hipVelocity);
    vector.push(feature.hipVelocity.y * weights.hipVelocity);
    vector.push(feature.hipVelocity.z * weights.hipVelocity);
    
    return vector;
  }
  
  private updateRootMotion(frame: MotionFrame, deltaTime: number): void {
    // Apply root motion from animation
    const direction = new THREE.Vector3(0, 0, 1).applyQuaternion(this.rootRotation);
    
    // Simple movement based on hip velocity
    this.rootPosition.add(
      direction.clone().multiplyScalar(frame.features.speed * deltaTime)
    );
    
    // Update rotation based on trajectory
    if (frame.features.trajectoryDirections.length > 0) {
      const targetDir = frame.features.trajectoryDirections[0];
      const currentDir = new THREE.Vector3(0, 0, 1).applyQuaternion(this.rootRotation);
      
      const angle = Math.atan2(targetDir.x, targetDir.z) - Math.atan2(currentDir.x, currentDir.z);
      const rotationSpeed = 5;
      
      this.rootRotation.multiply(
        new THREE.Quaternion().setFromAxisAngle(
          new THREE.Vector3(0, 1, 0),
          angle * rotationSpeed * deltaTime
        )
      );
    }
  }
  
  /**
   * Set root position/rotation directly
   */
  public setRootTransform(position: THREE.Vector3, rotation: THREE.Quaternion): void {
    this.rootPosition.copy(position);
    this.rootRotation.copy(rotation);
  }
  
  /**
   * Get current animation state
   */
  public getCurrentState(): { clipName: string; frameIndex: number; time: number } | null {
    if (!this.currentFrame) return null;
    
    const clip = this.database.clips[this.currentFrame.clipIndex];
    return {
      clipName: clip.name,
      frameIndex: this.currentFrame.frameIndex,
      time: this.currentFrame.time
    };
  }
}
