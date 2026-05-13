/**
 * Facial Animation System (FACS-Based)
 * Comprehensive facial expression and lip-sync system
 * 
 * Features:
 * - FACS Action Units (AU)
 * - Blend shape management
 * - Emotion presets
 * - Viseme-based lip sync
 * - Procedural eye movement
 * - Micro-expressions
 * - Expression blending
 */

import * as THREE from 'three';

// ============================================
// FACS ACTION UNITS
// ============================================

export enum ActionUnit {
  // Upper Face
  AU1_InnerBrowRaiser = 'AU1',
  AU2_OuterBrowRaiser = 'AU2',
  AU4_BrowLowerer = 'AU4',
  AU5_UpperLidRaiser = 'AU5',
  AU6_CheekRaiser = 'AU6',
  AU7_LidTightener = 'AU7',
  AU43_EyesClosed = 'AU43',
  AU45_Blink = 'AU45',
  AU46_Wink = 'AU46',
  
  // Lower Face - Lip/Jaw
  AU9_NoseWrinkler = 'AU9',
  AU10_UpperLipRaiser = 'AU10',
  AU11_NasolabialDeepener = 'AU11',
  AU12_LipCornerPuller = 'AU12',
  AU13_CheekPuffer = 'AU13',
  AU14_Dimpler = 'AU14',
  AU15_LipCornerDepressor = 'AU15',
  AU16_LowerLipDepressor = 'AU16',
  AU17_ChinRaiser = 'AU17',
  AU18_LipPucker = 'AU18',
  AU20_LipStretcher = 'AU20',
  AU22_LipFunneler = 'AU22',
  AU23_LipTightener = 'AU23',
  AU24_LipPressor = 'AU24',
  AU25_LipsPart = 'AU25',
  AU26_JawDrop = 'AU26',
  AU27_MouthStretch = 'AU27',
  AU28_LipSuck = 'AU28',
  
  // Head Position
  AU51_HeadTurnLeft = 'AU51',
  AU52_HeadTurnRight = 'AU52',
  AU53_HeadUp = 'AU53',
  AU54_HeadDown = 'AU54',
  AU55_HeadTiltLeft = 'AU55',
  AU56_HeadTiltRight = 'AU56',
  
  // Eye Position
  AU61_EyesLeft = 'AU61',
  AU62_EyesRight = 'AU62',
  AU63_EyesUp = 'AU63',
  AU64_EyesDown = 'AU64'
}

// ============================================
// VISEMES FOR LIP SYNC
// ============================================

export enum Viseme {
  Silence = 'sil',        // Closed mouth, neutral
  PP = 'PP',              // p, b, m
  FF = 'FF',              // f, v
  TH = 'TH',              // th
  DD = 'DD',              // t, d, n, l
  KK = 'KK',              // k, g, ng
  CH = 'CH',              // ch, j, sh, zh
  SS = 'SS',              // s, z
  NN = 'NN',              // n, ng
  RR = 'RR',              // r
  AA = 'AA',              // a (father)
  EE = 'EE',              // e (see)
  IH = 'IH',              // i (sit)
  OH = 'OH',              // o (go)
  OU = 'OU',              // ou (you)
}

// ============================================
// TYPES
// ============================================

export interface BlendShapeConfig {
  name: string;
  actionUnits: { au: ActionUnit; weight: number }[];
}

export interface EmotionPreset {
  name: string;
  actionUnits: Map<ActionUnit, number>;
  intensity: number;
}

export interface VisemeMapping {
  viseme: Viseme;
  blendShapes: { name: string; weight: number }[];
  duration: number;
}

export interface LipSyncData {
  phonemes: { viseme: Viseme; start: number; duration: number }[];
  totalDuration: number;
}

export interface EyeConfig {
  blinkRate: number;        // Blinks per minute
  blinkDuration: number;    // Seconds
  lookAtSpeed: number;
  maxRotation: number;
  microSaccadeRate: number;
  microSaccadeAmplitude: number;
}

export interface FacialConfig {
  blendShapeNames: string[];
  auToBlendShape: Map<ActionUnit, string[]>;
  visemeMappings: VisemeMapping[];
  eyeConfig: EyeConfig;
}

// ============================================
// EMOTION PRESETS
// ============================================

export const EmotionPresets: Record<string, Partial<Record<ActionUnit, number>>> = {
  happy: {
    [ActionUnit.AU6_CheekRaiser]: 0.8,
    [ActionUnit.AU12_LipCornerPuller]: 1.0,
    [ActionUnit.AU25_LipsPart]: 0.3,
  },
  sad: {
    [ActionUnit.AU1_InnerBrowRaiser]: 0.7,
    [ActionUnit.AU4_BrowLowerer]: 0.3,
    [ActionUnit.AU15_LipCornerDepressor]: 0.8,
    [ActionUnit.AU17_ChinRaiser]: 0.5,
  },
  angry: {
    [ActionUnit.AU4_BrowLowerer]: 1.0,
    [ActionUnit.AU5_UpperLidRaiser]: 0.5,
    [ActionUnit.AU7_LidTightener]: 0.7,
    [ActionUnit.AU23_LipTightener]: 0.8,
    [ActionUnit.AU24_LipPressor]: 0.6,
  },
  surprised: {
    [ActionUnit.AU1_InnerBrowRaiser]: 1.0,
    [ActionUnit.AU2_OuterBrowRaiser]: 1.0,
    [ActionUnit.AU5_UpperLidRaiser]: 0.9,
    [ActionUnit.AU26_JawDrop]: 0.7,
  },
  fearful: {
    [ActionUnit.AU1_InnerBrowRaiser]: 1.0,
    [ActionUnit.AU2_OuterBrowRaiser]: 0.5,
    [ActionUnit.AU4_BrowLowerer]: 0.3,
    [ActionUnit.AU5_UpperLidRaiser]: 0.8,
    [ActionUnit.AU20_LipStretcher]: 0.7,
    [ActionUnit.AU26_JawDrop]: 0.4,
  },
  disgusted: {
    [ActionUnit.AU9_NoseWrinkler]: 1.0,
    [ActionUnit.AU10_UpperLipRaiser]: 0.8,
    [ActionUnit.AU4_BrowLowerer]: 0.5,
    [ActionUnit.AU7_LidTightener]: 0.4,
  },
  contempt: {
    [ActionUnit.AU12_LipCornerPuller]: 0.5,  // Asymmetric typically
    [ActionUnit.AU14_Dimpler]: 0.6,
  },
  neutral: {}
};

// ============================================
// VISEME TO ACTION UNIT MAPPINGS
// ============================================

export const VisemeToAU: Record<Viseme, Partial<Record<ActionUnit, number>>> = {
  [Viseme.Silence]: {},
  [Viseme.PP]: {
    [ActionUnit.AU23_LipTightener]: 1.0,
    [ActionUnit.AU24_LipPressor]: 0.8,
  },
  [Viseme.FF]: {
    [ActionUnit.AU10_UpperLipRaiser]: 0.3,
    [ActionUnit.AU16_LowerLipDepressor]: 0.4,
  },
  [Viseme.TH]: {
    [ActionUnit.AU25_LipsPart]: 0.3,
    [ActionUnit.AU16_LowerLipDepressor]: 0.2,
  },
  [Viseme.DD]: {
    [ActionUnit.AU25_LipsPart]: 0.4,
    [ActionUnit.AU26_JawDrop]: 0.2,
  },
  [Viseme.KK]: {
    [ActionUnit.AU25_LipsPart]: 0.3,
    [ActionUnit.AU26_JawDrop]: 0.3,
  },
  [Viseme.CH]: {
    [ActionUnit.AU18_LipPucker]: 0.5,
    [ActionUnit.AU22_LipFunneler]: 0.4,
  },
  [Viseme.SS]: {
    [ActionUnit.AU20_LipStretcher]: 0.4,
    [ActionUnit.AU25_LipsPart]: 0.2,
  },
  [Viseme.NN]: {
    [ActionUnit.AU25_LipsPart]: 0.3,
  },
  [Viseme.RR]: {
    [ActionUnit.AU18_LipPucker]: 0.3,
    [ActionUnit.AU22_LipFunneler]: 0.3,
  },
  [Viseme.AA]: {
    [ActionUnit.AU26_JawDrop]: 0.8,
    [ActionUnit.AU25_LipsPart]: 0.7,
    [ActionUnit.AU27_MouthStretch]: 0.3,
  },
  [Viseme.EE]: {
    [ActionUnit.AU20_LipStretcher]: 0.8,
    [ActionUnit.AU25_LipsPart]: 0.4,
  },
  [Viseme.IH]: {
    [ActionUnit.AU20_LipStretcher]: 0.5,
    [ActionUnit.AU25_LipsPart]: 0.3,
  },
  [Viseme.OH]: {
    [ActionUnit.AU18_LipPucker]: 0.6,
    [ActionUnit.AU22_LipFunneler]: 0.5,
    [ActionUnit.AU26_JawDrop]: 0.4,
  },
  [Viseme.OU]: {
    [ActionUnit.AU18_LipPucker]: 0.9,
    [ActionUnit.AU22_LipFunneler]: 0.7,
  },
};

// ============================================
// BLEND SHAPE CONTROLLER
// ============================================

export class BlendShapeController {
  private mesh: THREE.SkinnedMesh;
  private blendShapeNames: string[];
  private currentWeights: Map<string, number> = new Map();
  private targetWeights: Map<string, number> = new Map();
  private blendSpeed: number = 10;
  
  constructor(mesh: THREE.SkinnedMesh) {
    this.mesh = mesh;
    this.blendShapeNames = [];
    
    // Get blend shape names from morph targets
    if (mesh.morphTargetDictionary) {
      this.blendShapeNames = Object.keys(mesh.morphTargetDictionary);
      
      for (const name of this.blendShapeNames) {
        this.currentWeights.set(name, 0);
        this.targetWeights.set(name, 0);
      }
    }
  }
  
  public setWeight(name: string, weight: number): void {
    if (this.blendShapeNames.includes(name)) {
      this.targetWeights.set(name, Math.max(0, Math.min(1, weight)));
    }
  }
  
  public setWeightImmediate(name: string, weight: number): void {
    if (this.blendShapeNames.includes(name)) {
      const clampedWeight = Math.max(0, Math.min(1, weight));
      this.currentWeights.set(name, clampedWeight);
      this.targetWeights.set(name, clampedWeight);
      this.applyWeight(name, clampedWeight);
    }
  }
  
  public getWeight(name: string): number {
    return this.currentWeights.get(name) ?? 0;
  }
  
  public update(deltaTime: number): void {
    for (const name of this.blendShapeNames) {
      const current = this.currentWeights.get(name) ?? 0;
      const target = this.targetWeights.get(name) ?? 0;
      
      if (Math.abs(current - target) > 0.001) {
        const newWeight = THREE.MathUtils.lerp(
          current,
          target,
          1 - Math.exp(-this.blendSpeed * deltaTime)
        );
        
        this.currentWeights.set(name, newWeight);
        this.applyWeight(name, newWeight);
      }
    }
  }
  
  private applyWeight(name: string, weight: number): void {
    if (this.mesh.morphTargetDictionary && this.mesh.morphTargetInfluences) {
      const index = this.mesh.morphTargetDictionary[name];
      if (index !== undefined) {
        this.mesh.morphTargetInfluences[index] = weight;
      }
    }
  }
  
  public reset(): void {
    for (const name of this.blendShapeNames) {
      this.targetWeights.set(name, 0);
    }
  }
  
  public getBlendShapeNames(): string[] {
    return [...this.blendShapeNames];
  }
}

// ============================================
// EYE CONTROLLER
// ============================================

export class EyeController {
  private leftEye: THREE.Bone | null = null;
  private rightEye: THREE.Bone | null = null;
  private config: EyeConfig;
  
  private lookAtTarget: THREE.Vector3 = new THREE.Vector3(0, 0, 1);
  private currentLookAt: THREE.Vector3 = new THREE.Vector3(0, 0, 1);
  
  private blinkTimer: number = 0;
  private nextBlinkTime: number = 0;
  private isBlinking: boolean = false;
  private blinkProgress: number = 0;
  
  private saccadeTimer: number = 0;
  private saccadeOffset: THREE.Vector2 = new THREE.Vector2();
  
  private blendShapeController: BlendShapeController | null = null;
  
  constructor(config: Partial<EyeConfig> = {}) {
    this.config = {
      blinkRate: 15,
      blinkDuration: 0.15,
      lookAtSpeed: 5,
      maxRotation: 30,
      microSaccadeRate: 3,
      microSaccadeAmplitude: 2,
      ...config
    };
    
    this.scheduleNextBlink();
  }
  
  public setEyeBones(leftEye: THREE.Bone | null, rightEye: THREE.Bone | null): void {
    this.leftEye = leftEye;
    this.rightEye = rightEye;
  }
  
  public setBlendShapeController(controller: BlendShapeController): void {
    this.blendShapeController = controller;
  }
  
  public lookAt(target: THREE.Vector3): void {
    this.lookAtTarget.copy(target);
  }
  
  public update(deltaTime: number, headPosition: THREE.Vector3): void {
    // Update look-at
    this.updateLookAt(deltaTime, headPosition);
    
    // Update blinking
    this.updateBlink(deltaTime);
    
    // Update micro-saccades
    this.updateSaccades(deltaTime);
    
    // Apply to bones or blend shapes
    this.applyEyeRotation();
  }
  
  private updateLookAt(deltaTime: number, headPosition: THREE.Vector3): void {
    // Smooth look-at interpolation
    this.currentLookAt.lerp(
      this.lookAtTarget,
      1 - Math.exp(-this.config.lookAtSpeed * deltaTime)
    );
  }
  
  private updateBlink(deltaTime: number): void {
    this.blinkTimer += deltaTime;
    
    if (!this.isBlinking && this.blinkTimer >= this.nextBlinkTime) {
      this.isBlinking = true;
      this.blinkProgress = 0;
    }
    
    if (this.isBlinking) {
      this.blinkProgress += deltaTime / this.config.blinkDuration;
      
      // Blink curve: quick close, slower open
      const blinkCurve = this.blinkProgress < 0.3
        ? this.blinkProgress / 0.3
        : 1 - (this.blinkProgress - 0.3) / 0.7;
      
      const blinkWeight = Math.max(0, Math.min(1, blinkCurve));
      
      if (this.blendShapeController) {
        this.blendShapeController.setWeightImmediate('eyesClosed', blinkWeight);
        // Or use AU
        // this.blendShapeController.setWeightImmediate('AU43', blinkWeight);
      }
      
      if (this.blinkProgress >= 1) {
        this.isBlinking = false;
        this.blinkTimer = 0;
        this.scheduleNextBlink();
        
        if (this.blendShapeController) {
          this.blendShapeController.setWeightImmediate('eyesClosed', 0);
        }
      }
    }
  }
  
  private scheduleNextBlink(): void {
    // Random time based on blink rate
    const averageInterval = 60 / this.config.blinkRate;
    this.nextBlinkTime = averageInterval * (0.5 + Math.random());
  }
  
  private updateSaccades(deltaTime: number): void {
    this.saccadeTimer += deltaTime;
    
    const saccadeInterval = 1 / this.config.microSaccadeRate;
    
    if (this.saccadeTimer >= saccadeInterval) {
      this.saccadeTimer = 0;
      
      // New random offset
      const angle = Math.random() * Math.PI * 2;
      const amplitude = this.config.microSaccadeAmplitude * THREE.MathUtils.DEG2RAD;
      
      this.saccadeOffset.set(
        Math.cos(angle) * amplitude * Math.random(),
        Math.sin(angle) * amplitude * Math.random()
      );
    }
    
    // Decay saccade offset
    this.saccadeOffset.multiplyScalar(0.95);
  }
  
  private applyEyeRotation(): void {
    if (!this.leftEye && !this.rightEye) return;
    
    // Calculate look direction
    // This is simplified - production would use proper IK
    
    const maxRot = this.config.maxRotation * THREE.MathUtils.DEG2RAD;
    
    // Apply to bones
    const applyToEye = (eye: THREE.Bone | null) => {
      if (!eye) return;
      
      // Simple rotation towards target
      // In production, use proper look-at calculation
      eye.rotation.x = THREE.MathUtils.clamp(
        this.saccadeOffset.y,
        -maxRot,
        maxRot
      );
      eye.rotation.y = THREE.MathUtils.clamp(
        this.saccadeOffset.x,
        -maxRot,
        maxRot
      );
    };
    
    applyToEye(this.leftEye);
    applyToEye(this.rightEye);
  }
  
  public triggerBlink(): void {
    this.isBlinking = true;
    this.blinkProgress = 0;
  }
}

// ============================================
// LIP SYNC CONTROLLER
// ============================================

export class LipSyncController {
  private blendShapeController: BlendShapeController;
  private currentViseme: Viseme = Viseme.Silence;
  private targetViseme: Viseme = Viseme.Silence;
  private visemeProgress: number = 1;
  private visemeSpeed: number = 15;
  
  private lipSyncData: LipSyncData | null = null;
  private lipSyncTime: number = 0;
  private isPlaying: boolean = false;
  private currentPhonemeIndex: number = 0;
  
  constructor(blendShapeController: BlendShapeController) {
    this.blendShapeController = blendShapeController;
  }
  
  public setViseme(viseme: Viseme): void {
    if (this.targetViseme !== viseme) {
      this.currentViseme = this.targetViseme;
      this.targetViseme = viseme;
      this.visemeProgress = 0;
    }
  }
  
  public startLipSync(data: LipSyncData): void {
    this.lipSyncData = data;
    this.lipSyncTime = 0;
    this.currentPhonemeIndex = 0;
    this.isPlaying = true;
  }
  
  public stopLipSync(): void {
    this.isPlaying = false;
    this.lipSyncData = null;
    this.setViseme(Viseme.Silence);
  }
  
  public update(deltaTime: number): void {
    // Update lip sync playback
    if (this.isPlaying && this.lipSyncData) {
      this.lipSyncTime += deltaTime;
      
      // Find current phoneme
      while (
        this.currentPhonemeIndex < this.lipSyncData.phonemes.length &&
        this.lipSyncTime >= this.lipSyncData.phonemes[this.currentPhonemeIndex].start +
                           this.lipSyncData.phonemes[this.currentPhonemeIndex].duration
      ) {
        this.currentPhonemeIndex++;
      }
      
      if (this.currentPhonemeIndex < this.lipSyncData.phonemes.length) {
        const phoneme = this.lipSyncData.phonemes[this.currentPhonemeIndex];
        if (this.lipSyncTime >= phoneme.start) {
          this.setViseme(phoneme.viseme);
        }
      }
      
      if (this.lipSyncTime >= this.lipSyncData.totalDuration) {
        this.stopLipSync();
      }
    }
    
    // Update viseme blend
    if (this.visemeProgress < 1) {
      this.visemeProgress += deltaTime * this.visemeSpeed;
      this.visemeProgress = Math.min(1, this.visemeProgress);
    }
    
    // Apply viseme weights
    this.applyViseme();
  }
  
  private applyViseme(): void {
    const currentAUs = VisemeToAU[this.currentViseme];
    const targetAUs = VisemeToAU[this.targetViseme];
    
    // Blend between current and target viseme
    const allAUs = new Set([
      ...Object.keys(currentAUs),
      ...Object.keys(targetAUs)
    ]);
    
    for (const au of allAUs) {
      const currentWeight = (currentAUs as any)[au] ?? 0;
      const targetWeight = (targetAUs as any)[au] ?? 0;
      const blendedWeight = THREE.MathUtils.lerp(
        currentWeight,
        targetWeight,
        this.visemeProgress
      );
      
      // Map AU to blend shape name (simplified)
      const blendShapeName = au.toLowerCase();
      this.blendShapeController.setWeight(blendShapeName, blendedWeight);
    }
  }
}

// ============================================
// EXPRESSION CONTROLLER
// ============================================

export class ExpressionController {
  private blendShapeController: BlendShapeController;
  private currentExpression: string = 'neutral';
  private targetExpression: string = 'neutral';
  private expressionIntensity: number = 1;
  private transitionProgress: number = 1;
  private transitionSpeed: number = 3;
  
  private activeAUs: Map<ActionUnit, number> = new Map();
  private targetAUs: Map<ActionUnit, number> = new Map();
  
  constructor(blendShapeController: BlendShapeController) {
    this.blendShapeController = blendShapeController;
  }
  
  public setExpression(name: string, intensity: number = 1, immediate: boolean = false): void {
    const preset = EmotionPresets[name];
    if (!preset) return;
    
    this.currentExpression = this.targetExpression;
    this.targetExpression = name;
    this.expressionIntensity = intensity;
    
    // Store current AU values
    this.activeAUs = new Map(this.targetAUs);
    
    // Set target AU values
    this.targetAUs.clear();
    for (const [au, weight] of Object.entries(preset)) {
      this.targetAUs.set(au as ActionUnit, weight * intensity);
    }
    
    if (immediate) {
      this.transitionProgress = 1;
      this.applyExpression(1);
    } else {
      this.transitionProgress = 0;
    }
  }
  
  public setActionUnit(au: ActionUnit, weight: number): void {
    this.targetAUs.set(au, weight);
  }
  
  public update(deltaTime: number): void {
    if (this.transitionProgress < 1) {
      this.transitionProgress += deltaTime * this.transitionSpeed;
      this.transitionProgress = Math.min(1, this.transitionProgress);
      this.applyExpression(this.transitionProgress);
    }
  }
  
  private applyExpression(progress: number): void {
    // Collect all AUs from both active and target
    const allAUs = new Set([
      ...this.activeAUs.keys(),
      ...this.targetAUs.keys()
    ]);
    
    for (const au of allAUs) {
      const activeWeight = this.activeAUs.get(au) ?? 0;
      const targetWeight = this.targetAUs.get(au) ?? 0;
      const blendedWeight = THREE.MathUtils.lerp(activeWeight, targetWeight, progress);
      
      // Map AU to blend shape (simplified - real implementation needs proper mapping)
      const blendShapeName = au.toLowerCase();
      this.blendShapeController.setWeight(blendShapeName, blendedWeight);
    }
  }
  
  public blendExpressions(
    expressions: { name: string; weight: number }[]
  ): void {
    this.targetAUs.clear();
    
    for (const { name, weight } of expressions) {
      const preset = EmotionPresets[name];
      if (!preset) continue;
      
      for (const [au, auWeight] of Object.entries(preset)) {
        const current = this.targetAUs.get(au as ActionUnit) ?? 0;
        this.targetAUs.set(au as ActionUnit, current + auWeight * weight);
      }
    }
    
    // Clamp all weights
    for (const [au, weight] of this.targetAUs) {
      this.targetAUs.set(au, Math.min(1, weight));
    }
    
    this.transitionProgress = 0;
  }
}

// ============================================
// MAIN FACIAL ANIMATION SYSTEM
// ============================================

export class FacialAnimationSystem {
  private mesh: THREE.SkinnedMesh;
  private blendShapeController: BlendShapeController;
  private eyeController: EyeController;
  private lipSyncController: LipSyncController;
  private expressionController: ExpressionController;
  
  private headBone: THREE.Bone | null = null;
  
  constructor(mesh: THREE.SkinnedMesh) {
    this.mesh = mesh;
    
    this.blendShapeController = new BlendShapeController(mesh);
    this.eyeController = new EyeController();
    this.lipSyncController = new LipSyncController(this.blendShapeController);
    this.expressionController = new ExpressionController(this.blendShapeController);
    
    this.eyeController.setBlendShapeController(this.blendShapeController);
  }
  
  /**
   * Setup bones for eye and head control
   */
  public setupBones(
    headBone: THREE.Bone | null,
    leftEyeBone: THREE.Bone | null,
    rightEyeBone: THREE.Bone | null
  ): void {
    this.headBone = headBone;
    this.eyeController.setEyeBones(leftEyeBone, rightEyeBone);
  }
  
  /**
   * Set facial expression
   */
  public setExpression(name: string, intensity: number = 1): void {
    this.expressionController.setExpression(name, intensity);
  }
  
  /**
   * Blend multiple expressions
   */
  public blendExpressions(expressions: { name: string; weight: number }[]): void {
    this.expressionController.blendExpressions(expressions);
  }
  
  /**
   * Set individual action unit
   */
  public setActionUnit(au: ActionUnit, weight: number): void {
    this.expressionController.setActionUnit(au, weight);
  }
  
  /**
   * Set direct blend shape weight
   */
  public setBlendShape(name: string, weight: number): void {
    this.blendShapeController.setWeight(name, weight);
  }
  
  /**
   * Look at target position
   */
  public lookAt(target: THREE.Vector3): void {
    this.eyeController.lookAt(target);
  }
  
  /**
   * Trigger a blink
   */
  public blink(): void {
    this.eyeController.triggerBlink();
  }
  
  /**
   * Set viseme for lip sync
   */
  public setViseme(viseme: Viseme): void {
    this.lipSyncController.setViseme(viseme);
  }
  
  /**
   * Start lip sync from data
   */
  public startLipSync(data: LipSyncData): void {
    this.lipSyncController.startLipSync(data);
  }
  
  /**
   * Stop lip sync
   */
  public stopLipSync(): void {
    this.lipSyncController.stopLipSync();
  }
  
  /**
   * Update all facial animation
   */
  public update(deltaTime: number): void {
    const headPosition = this.headBone?.getWorldPosition(new THREE.Vector3()) ?? new THREE.Vector3();
    
    this.blendShapeController.update(deltaTime);
    this.eyeController.update(deltaTime, headPosition);
    this.lipSyncController.update(deltaTime);
    this.expressionController.update(deltaTime);
  }
  
  /**
   * Reset to neutral
   */
  public reset(): void {
    this.blendShapeController.reset();
    this.expressionController.setExpression('neutral', 1, true);
    this.lipSyncController.stopLipSync();
  }
  
  /**
   * Get available blend shapes
   */
  public getBlendShapeNames(): string[] {
    return this.blendShapeController.getBlendShapeNames();
  }
  
  /**
   * Get available emotion presets
   */
  public getEmotionPresets(): string[] {
    return Object.keys(EmotionPresets);
  }
}

