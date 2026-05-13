/**
 * Architectural Style Engine
 * Applies stylistic parameters to procedurally generated buildings
 * 
 * Styles supported:
 * - Modern (Minimalist, clean lines, large windows)
 * - Classical (Symmetry, ornament, proportions)
 * - Art Deco (Geometric patterns, setbacks)
 * - Victorian (Ornate, asymmetric, varied materials)
 * - Craftsman (Wood, natural materials, porches)
 * - Colonial (Symmetry, shutters, dormers)
 * - Mediterranean (Stucco, tile roofs, arches)
 * - Industrial (Exposed structure, large spans)
 */

import {
  ArchitecturalStyle,
  ArchitecturalStyleId,
  NumberRange,
  MaterialPalette,
  RoofType,
  WindowType,
  DoorType,
  Wall2D,
  Door2D,
  Window2D,
  Room2D,
  Building2D
} from '../types';

// ============================================
// STYLE DEFINITIONS
// ============================================

export const ARCHITECTURAL_STYLES: ArchitecturalStyle[] = [
  {
    id: 'modern',
    name: 'Modern',
    era: '1920-present',
    proportions: {
      floorToFloorHeight: { min: 3.0, max: 4.0 },
      windowToWallRatio: { min: 0.4, max: 0.8 },
      doorHeight: { min: 2.1, max: 2.7 },
      ceilingHeight: { min: 2.7, max: 3.5 }
    },
    roof: {
      types: ['flat', 'shed', 'butterfly'],
      pitchRange: { min: 0, max: 15 },
      overhangRange: { min: 0.3, max: 1.5 }
    },
    facade: {
      symmetry: 'asymmetric',
      materials: {
        primary: ['glass', 'concrete', 'steel'],
        secondary: ['wood', 'stone'],
        accent: ['corten', 'copper', 'black-steel']
      },
      ornamentLevel: 'minimal'
    },
    windows: {
      types: ['fixed', 'sliding', 'casement'],
      proportions: { min: 0.5, max: 3.0 }
    },
    doors: {
      types: ['hinged', 'sliding', 'pocket']
    },
    details: {
      cornices: false,
      pilasters: false,
      quoins: false,
      stringCourses: false,
      balconies: true
    }
  },
  {
    id: 'classical',
    name: 'Classical',
    era: 'Ancient - 19th century',
    proportions: {
      floorToFloorHeight: { min: 3.5, max: 5.0 },
      windowToWallRatio: { min: 0.2, max: 0.4 },
      doorHeight: { min: 2.4, max: 3.6 },
      ceilingHeight: { min: 3.0, max: 4.5 }
    },
    roof: {
      types: ['gable', 'hip', 'mansard'],
      pitchRange: { min: 25, max: 45 },
      overhangRange: { min: 0.3, max: 0.8 }
    },
    facade: {
      symmetry: 'symmetric',
      materials: {
        primary: ['stone', 'brick', 'stucco'],
        secondary: ['limestone', 'marble'],
        accent: ['bronze', 'wrought-iron']
      },
      ornamentLevel: 'rich'
    },
    windows: {
      types: ['double-hung', 'casement', 'fixed'],
      proportions: { min: 1.5, max: 2.5 }
    },
    doors: {
      types: ['hinged', 'double']
    },
    details: {
      cornices: true,
      pilasters: true,
      quoins: true,
      stringCourses: true,
      balconies: true
    }
  },
  {
    id: 'art_deco',
    name: 'Art Deco',
    era: '1920s-1940s',
    proportions: {
      floorToFloorHeight: { min: 3.2, max: 4.0 },
      windowToWallRatio: { min: 0.3, max: 0.5 },
      doorHeight: { min: 2.4, max: 3.0 },
      ceilingHeight: { min: 2.8, max: 3.5 }
    },
    roof: {
      types: ['flat', 'gable'],
      pitchRange: { min: 0, max: 30 },
      overhangRange: { min: 0.1, max: 0.5 }
    },
    facade: {
      symmetry: 'symmetric',
      materials: {
        primary: ['limestone', 'terracotta', 'concrete'],
        secondary: ['glass-block', 'chrome'],
        accent: ['gold', 'bronze', 'black-granite']
      },
      ornamentLevel: 'moderate'
    },
    windows: {
      types: ['casement', 'fixed'],
      proportions: { min: 1.2, max: 2.0 }
    },
    doors: {
      types: ['hinged', 'revolving']
    },
    details: {
      cornices: true,
      pilasters: true,
      quoins: false,
      stringCourses: true,
      balconies: false
    }
  },
  {
    id: 'victorian',
    name: 'Victorian',
    era: '1837-1901',
    proportions: {
      floorToFloorHeight: { min: 3.0, max: 4.0 },
      windowToWallRatio: { min: 0.25, max: 0.45 },
      doorHeight: { min: 2.3, max: 2.8 },
      ceilingHeight: { min: 2.8, max: 3.6 }
    },
    roof: {
      types: ['gable', 'hip', 'mansard', 'gambrel'],
      pitchRange: { min: 35, max: 60 },
      overhangRange: { min: 0.3, max: 1.0 }
    },
    facade: {
      symmetry: 'asymmetric',
      materials: {
        primary: ['wood-siding', 'brick', 'shingle'],
        secondary: ['stone', 'slate'],
        accent: ['painted-trim', 'stained-glass']
      },
      ornamentLevel: 'rich'
    },
    windows: {
      types: ['double-hung', 'casement', 'fixed'],
      proportions: { min: 1.5, max: 3.0 }
    },
    doors: {
      types: ['hinged', 'double']
    },
    details: {
      cornices: true,
      pilasters: false,
      quoins: false,
      stringCourses: false,
      balconies: true
    }
  },
  {
    id: 'craftsman',
    name: 'Craftsman',
    era: '1900-1930',
    proportions: {
      floorToFloorHeight: { min: 2.8, max: 3.2 },
      windowToWallRatio: { min: 0.25, max: 0.4 },
      doorHeight: { min: 2.1, max: 2.4 },
      ceilingHeight: { min: 2.6, max: 3.0 }
    },
    roof: {
      types: ['gable', 'hip'],
      pitchRange: { min: 20, max: 35 },
      overhangRange: { min: 0.6, max: 1.2 }
    },
    facade: {
      symmetry: 'balanced',
      materials: {
        primary: ['wood-siding', 'shingle', 'stone'],
        secondary: ['brick', 'stucco'],
        accent: ['natural-wood', 'copper']
      },
      ornamentLevel: 'moderate'
    },
    windows: {
      types: ['double-hung', 'casement'],
      proportions: { min: 1.3, max: 2.0 }
    },
    doors: {
      types: ['hinged']
    },
    details: {
      cornices: false,
      pilasters: false,
      quoins: false,
      stringCourses: false,
      balconies: false
    }
  },
  {
    id: 'colonial',
    name: 'Colonial',
    era: '1600-1800 (Revival: 1880-present)',
    proportions: {
      floorToFloorHeight: { min: 2.8, max: 3.4 },
      windowToWallRatio: { min: 0.2, max: 0.35 },
      doorHeight: { min: 2.1, max: 2.5 },
      ceilingHeight: { min: 2.5, max: 3.0 }
    },
    roof: {
      types: ['gable', 'hip', 'gambrel'],
      pitchRange: { min: 30, max: 45 },
      overhangRange: { min: 0.2, max: 0.5 }
    },
    facade: {
      symmetry: 'symmetric',
      materials: {
        primary: ['brick', 'wood-siding', 'clapboard'],
        secondary: ['stone', 'shingle'],
        accent: ['white-trim', 'black-shutters']
      },
      ornamentLevel: 'moderate'
    },
    windows: {
      types: ['double-hung'],
      proportions: { min: 1.5, max: 2.2 }
    },
    doors: {
      types: ['hinged']
    },
    details: {
      cornices: true,
      pilasters: true,
      quoins: true,
      stringCourses: false,
      balconies: false
    }
  },
  {
    id: 'mediterranean',
    name: 'Mediterranean',
    era: 'Revival: 1920s-present',
    proportions: {
      floorToFloorHeight: { min: 3.0, max: 3.8 },
      windowToWallRatio: { min: 0.2, max: 0.4 },
      doorHeight: { min: 2.2, max: 2.8 },
      ceilingHeight: { min: 2.8, max: 3.4 }
    },
    roof: {
      types: ['hip', 'gable'],
      pitchRange: { min: 15, max: 30 },
      overhangRange: { min: 0.4, max: 1.0 }
    },
    facade: {
      symmetry: 'balanced',
      materials: {
        primary: ['stucco', 'stone'],
        secondary: ['terracotta', 'tile'],
        accent: ['wrought-iron', 'wood-beam']
      },
      ornamentLevel: 'moderate'
    },
    windows: {
      types: ['casement', 'fixed'],
      proportions: { min: 1.0, max: 2.0 }
    },
    doors: {
      types: ['hinged', 'double']
    },
    details: {
      cornices: true,
      pilasters: false,
      quoins: false,
      stringCourses: false,
      balconies: true
    }
  },
  {
    id: 'industrial',
    name: 'Industrial',
    era: '1850-present',
    proportions: {
      floorToFloorHeight: { min: 3.5, max: 6.0 },
      windowToWallRatio: { min: 0.4, max: 0.7 },
      doorHeight: { min: 2.4, max: 4.0 },
      ceilingHeight: { min: 3.0, max: 5.0 }
    },
    roof: {
      types: ['flat', 'shed', 'gable'],
      pitchRange: { min: 0, max: 20 },
      overhangRange: { min: 0, max: 0.3 }
    },
    facade: {
      symmetry: 'asymmetric',
      materials: {
        primary: ['steel', 'glass', 'concrete'],
        secondary: ['brick', 'metal-panel'],
        accent: ['exposed-ductwork', 'steel-beam']
      },
      ornamentLevel: 'minimal'
    },
    windows: {
      types: ['fixed', 'awning'],
      proportions: { min: 0.5, max: 2.0 }
    },
    doors: {
      types: ['sliding', 'hinged', 'revolving']
    },
    details: {
      cornices: false,
      pilasters: false,
      quoins: false,
      stringCourses: false,
      balconies: false
    }
  }
];

// ============================================
// STYLE ENGINE
// ============================================

export class StyleEngine {
  private styles: Map<ArchitecturalStyleId, ArchitecturalStyle>;
  private random: () => number;
  
  constructor(seed?: number) {
    this.styles = new Map(ARCHITECTURAL_STYLES.map(s => [s.id, s]));
    this.random = seed !== undefined ? this.seededRandom(seed) : Math.random;
  }
  
  private seededRandom(seed: number): () => number {
    return () => {
      seed = (seed * 1103515245 + 12345) & 0x7fffffff;
      return seed / 0x7fffffff;
    };
  }
  
  /**
   * Get style by ID
   */
  public getStyle(id: ArchitecturalStyleId): ArchitecturalStyle | undefined {
    return this.styles.get(id);
  }
  
  /**
   * Get all available styles
   */
  public getAllStyles(): ArchitecturalStyle[] {
    return Array.from(this.styles.values());
  }
  
  /**
   * Apply style to a building
   */
  public applyStyle(building: Building2D, styleId: ArchitecturalStyleId): StyledBuilding {
    const style = this.styles.get(styleId);
    if (!style) {
      throw new Error(`Unknown style: ${styleId}`);
    }
    
    const styledBuilding: StyledBuilding = {
      ...building,
      style,
      styleParameters: this.generateStyleParameters(style),
      styledWalls: [],
      styledDoors: [],
      styledWindows: []
    };
    
    // Apply style to floors
    for (const floor of building.floors) {
      // Style walls
      for (const wall of floor.walls) {
        styledBuilding.styledWalls.push(this.styleWall(wall, style));
      }
      
      // Style doors
      for (const door of floor.doors) {
        styledBuilding.styledDoors.push(this.styleDoor(door, style));
      }
      
      // Style windows
      for (const window of floor.windows) {
        styledBuilding.styledWindows.push(this.styleWindow(window, style));
      }
    }
    
    return styledBuilding;
  }
  
  /**
   * Generate style-specific parameters
   */
  private generateStyleParameters(style: ArchitecturalStyle): StyleParameters {
    return {
      floorHeight: this.sampleRange(style.proportions.floorToFloorHeight),
      ceilingHeight: this.sampleRange(style.proportions.ceilingHeight),
      windowToWallRatio: this.sampleRange(style.proportions.windowToWallRatio),
      doorHeight: this.sampleRange(style.proportions.doorHeight),
      
      roofType: this.pickRandom(style.roof.types),
      roofPitch: this.sampleRange(style.roof.pitchRange),
      roofOverhang: this.sampleRange(style.roof.overhangRange),
      
      primaryMaterial: this.pickRandom(style.facade.materials.primary),
      secondaryMaterial: this.pickRandom(style.facade.materials.secondary),
      accentMaterial: this.pickRandom(style.facade.materials.accent),
      
      windowType: this.pickRandom(style.windows.types),
      windowProportions: this.sampleRange(style.windows.proportions),
      
      doorType: this.pickRandom(style.doors.types),
      
      hasCornices: style.details.cornices,
      hasPilasters: style.details.pilasters,
      hasQuoins: style.details.quoins,
      hasStringCourses: style.details.stringCourses,
      hasBalconies: style.details.balconies
    };
  }
  
  /**
   * Apply style to wall
   */
  private styleWall(wall: Wall2D, style: ArchitecturalStyle): StyledWall {
    const isExterior = wall.type === 'exterior';
    
    return {
      ...wall,
      material: isExterior 
        ? this.pickRandom(style.facade.materials.primary)
        : 'plaster',
      trimMaterial: this.pickRandom(style.facade.materials.secondary),
      hasMolding: style.details.stringCourses && isExterior,
      hasQuoins: style.details.quoins && isExterior && this.isCornerWall(wall),
      textureScale: this.getMaterialTextureScale(
        this.pickRandom(style.facade.materials.primary)
      )
    };
  }
  
  /**
   * Apply style to door
   */
  private styleDoor(door: Door2D, style: ArchitecturalStyle): StyledDoor {
    const doorType = this.pickRandom(style.doors.types);
    
    return {
      ...door,
      doorType,
      material: this.getDoorMaterial(style, doorType),
      frameMaterial: this.pickRandom(style.facade.materials.secondary),
      hasGlass: doorType !== 'pocket' && this.random() > 0.5,
      glassPanes: style.id === 'victorian' ? 6 : (style.id === 'classical' ? 4 : 1),
      hasSidelight: style.id === 'colonial' || style.id === 'classical',
      hasTransom: style.details.cornices && this.random() > 0.6,
      handleStyle: this.getHandleStyle(style),
      panelCount: this.getPanelCount(style, doorType)
    };
  }
  
  /**
   * Apply style to window
   */
  private styleWindow(window: Window2D, style: ArchitecturalStyle): StyledWindow {
    const windowType = this.pickRandom(style.windows.types);
    const proportions = this.sampleRange(style.windows.proportions);
    
    // Adjust window dimensions to match style proportions
    const currentAspect = (window.headHeight - window.sillHeight) / window.width;
    let adjustedHeight = window.headHeight - window.sillHeight;
    let adjustedWidth = window.width;
    
    if (currentAspect < proportions) {
      adjustedHeight = adjustedWidth * proportions;
    } else if (currentAspect > proportions) {
      adjustedWidth = adjustedHeight / proportions;
    }
    
    return {
      ...window,
      windowType,
      adjustedWidth,
      adjustedHeight,
      frameMaterial: this.pickRandom(style.facade.materials.secondary),
      frameWidth: style.id === 'modern' ? 0.03 : 0.06,
      paneLayout: this.getPaneLayout(style, windowType),
      hasShutters: style.id === 'colonial' || style.id === 'mediterranean',
      shutterMaterial: 'painted-wood',
      hasLintel: style.details.cornices,
      lintelStyle: this.getLintelStyle(style),
      hasSill: true,
      sillMaterial: this.pickRandom(style.facade.materials.secondary),
      hasMullions: this.shouldHaveMullions(style)
    };
  }
  
  // Helper methods
  
  private sampleRange(range: NumberRange): number {
    return range.min + this.random() * (range.max - range.min);
  }
  
  private pickRandom<T>(array: T[]): T {
    return array[Math.floor(this.random() * array.length)];
  }
  
  private isCornerWall(wall: Wall2D): boolean {
    // Simplified check - in real implementation would check building corners
    return this.random() > 0.7;
  }
  
  private getMaterialTextureScale(material: string): number {
    const scales: Record<string, number> = {
      'brick': 0.1,
      'stone': 0.15,
      'wood-siding': 0.2,
      'stucco': 0.05,
      'concrete': 0.1,
      'glass': 1.0,
      'steel': 0.5
    };
    return scales[material] ?? 0.1;
  }
  
  private getDoorMaterial(style: ArchitecturalStyle, doorType: DoorType): string {
    if (style.id === 'modern') {
      return doorType === 'sliding' ? 'glass-aluminum' : 'wood-modern';
    }
    if (style.id === 'industrial') {
      return 'steel';
    }
    return 'painted-wood';
  }
  
  private getHandleStyle(style: ArchitecturalStyle): string {
    const handles: Record<ArchitecturalStyleId, string> = {
      modern: 'lever-modern',
      classical: 'brass-knob',
      art_deco: 'chrome-geometric',
      victorian: 'brass-ornate',
      craftsman: 'bronze-simple',
      colonial: 'brass-traditional',
      mediterranean: 'wrought-iron',
      industrial: 'steel-bar'
    };
    return handles[style.id] ?? 'lever-modern';
  }
  
  private getPanelCount(style: ArchitecturalStyle, doorType: DoorType): number {
    if (doorType === 'sliding' || doorType === 'pocket') return 0;
    
    const panels: Record<ArchitecturalStyleId, number> = {
      modern: 0,
      classical: 6,
      art_deco: 2,
      victorian: 4,
      craftsman: 2,
      colonial: 6,
      mediterranean: 4,
      industrial: 0
    };
    return panels[style.id] ?? 0;
  }
  
  private getPaneLayout(style: ArchitecturalStyle, windowType: WindowType): string {
    if (style.id === 'modern') return 'single';
    if (style.id === 'colonial') return '6-over-6';
    if (style.id === 'victorian') return '2-over-2';
    if (style.id === 'craftsman') return '4-over-1';
    return '1-over-1';
  }
  
  private getLintelStyle(style: ArchitecturalStyle): string {
    if (style.id === 'classical') return 'pediment';
    if (style.id === 'art_deco') return 'keystone';
    if (style.id === 'victorian') return 'arch';
    return 'flat';
  }
  
  private shouldHaveMullions(style: ArchitecturalStyle): boolean {
    return ['colonial', 'victorian', 'craftsman', 'art_deco'].includes(style.id);
  }
}

// ============================================
// STYLED TYPES
// ============================================

export interface StyleParameters {
  floorHeight: number;
  ceilingHeight: number;
  windowToWallRatio: number;
  doorHeight: number;
  
  roofType: RoofType;
  roofPitch: number;
  roofOverhang: number;
  
  primaryMaterial: string;
  secondaryMaterial: string;
  accentMaterial: string;
  
  windowType: WindowType;
  windowProportions: number;
  
  doorType: DoorType;
  
  hasCornices: boolean;
  hasPilasters: boolean;
  hasQuoins: boolean;
  hasStringCourses: boolean;
  hasBalconies: boolean;
}

export interface StyledBuilding extends Building2D {
  style: ArchitecturalStyle;
  styleParameters: StyleParameters;
  styledWalls: StyledWall[];
  styledDoors: StyledDoor[];
  styledWindows: StyledWindow[];
}

export interface StyledWall extends Wall2D {
  material: string;
  trimMaterial: string;
  hasMolding: boolean;
  hasQuoins: boolean;
  textureScale: number;
}

export interface StyledDoor extends Door2D {
  material: string;
  frameMaterial: string;
  hasGlass: boolean;
  glassPanes: number;
  hasSidelight: boolean;
  hasTransom: boolean;
  handleStyle: string;
  panelCount: number;
}

export interface StyledWindow extends Window2D {
  adjustedWidth: number;
  adjustedHeight: number;
  frameMaterial: string;
  frameWidth: number;
  paneLayout: string;
  hasShutters: boolean;
  shutterMaterial: string;
  hasLintel: boolean;
  lintelStyle: string;
  hasSill: boolean;
  sillMaterial: string;
  hasMullions: boolean;
}

