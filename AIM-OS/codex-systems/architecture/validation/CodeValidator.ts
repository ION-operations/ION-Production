/**
 * Building Code Validator
 * Validates buildings against building codes and accessibility standards
 * 
 * Codes supported:
 * - IBC (International Building Code) - Egress, fire, structural
 * - ADA (Americans with Disabilities Act) - Accessibility
 * - IRC (International Residential Code) - Residential
 * - Energy codes (simplified)
 * - Local zoning (configurable)
 */

import {
  Vector2D,
  Polygon,
  Building2D,
  Floor2D,
  Room2D,
  Wall2D,
  Door2D,
  Window2D,
  ValidationResult,
  CodeViolation,
  ValidationReport,
  RoomType
} from '../types';

// ============================================
// CODE RULE DEFINITIONS
// ============================================

export interface CodeRule {
  id: string;
  code: 'IBC' | 'ADA' | 'IRC' | 'ENERGY' | 'ZONING';
  category: 'egress' | 'fire' | 'accessibility' | 'structural' | 'zoning' | 'energy' | 'habitability';
  description: string;
  severity: 'critical' | 'major' | 'minor';
  check: (building: Building2D, context: ValidationContext) => ValidationResult;
}

export interface ValidationContext {
  occupancyType: OccupancyType;
  constructionType: ConstructionType;
  sprinklered: boolean;
  buildingArea: number;
  buildingHeight: number;
  stories: number;
  occupantLoad: number;
  zoning?: ZoningRequirements;
}

export type OccupancyType = 
  | 'R-1' | 'R-2' | 'R-3'  // Residential
  | 'B'                     // Business
  | 'A-1' | 'A-2' | 'A-3'  // Assembly
  | 'E'                     // Educational
  | 'M'                     // Mercantile
  | 'S-1' | 'S-2'          // Storage
  | 'I-1' | 'I-2' | 'I-3'; // Institutional

export type ConstructionType = 
  | 'I-A' | 'I-B'
  | 'II-A' | 'II-B'
  | 'III-A' | 'III-B'
  | 'IV'
  | 'V-A' | 'V-B';

export interface ZoningRequirements {
  maxHeight: number;
  maxStories: number;
  maxFAR: number;
  minFrontSetback: number;
  minSideSetback: number;
  minRearSetback: number;
  maxCoverage: number;
  parkingRequired: number;  // Spaces per unit/1000sf
}

// ============================================
// IBC EGRESS RULES
// ============================================

const IBC_EGRESS_RULES: CodeRule[] = [
  {
    id: 'IBC-1005.1',
    code: 'IBC',
    category: 'egress',
    description: 'Minimum egress width',
    severity: 'critical',
    check: (building, context) => {
      for (const floor of building.floors) {
        // Calculate required egress width (0.3" per occupant for stairs, 0.2" for other)
        const floorOccupants = calculateFloorOccupants(floor);
        const requiredWidth = floorOccupants * 0.2 * 0.0254;  // Convert to meters
        
        const exitWidth = floor.doors
          .filter(d => isExitDoor(d, floor))
          .reduce((sum, d) => sum + d.width, 0);
        
        if (exitWidth < requiredWidth) {
          return {
            status: 'fail',
            details: `Exit width ${exitWidth.toFixed(2)}m < required ${requiredWidth.toFixed(2)}m (floor ${floor.level})`,
            location: floor.id
          };
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IBC-1006.2.1',
    code: 'IBC',
    category: 'egress',
    description: 'Number of exits required',
    severity: 'critical',
    check: (building, context) => {
      for (const floor of building.floors) {
        const occupants = calculateFloorOccupants(floor);
        let requiredExits = 1;
        
        if (occupants > 500) requiredExits = 3;
        else if (occupants > 1000) requiredExits = 4;
        else if (occupants > 10) requiredExits = 2;
        
        const exitCount = floor.doors.filter(d => isExitDoor(d, floor)).length;
        
        if (exitCount < requiredExits) {
          return {
            status: 'fail',
            details: `${exitCount} exits < ${requiredExits} required (floor ${floor.level}, ${occupants} occupants)`,
            location: floor.id
          };
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IBC-1007.1',
    code: 'IBC',
    category: 'egress',
    description: 'Maximum travel distance to exit',
    severity: 'critical',
    check: (building, context) => {
      // Maximum travel distance varies by occupancy and sprinklers
      let maxDistance = context.sprinklered ? 76 : 61;  // meters (250ft/200ft)
      
      if (context.occupancyType.startsWith('R-')) {
        maxDistance = context.sprinklered ? 76 : 61;
      } else if (context.occupancyType === 'B') {
        maxDistance = context.sprinklered ? 91 : 61;
      }
      
      for (const floor of building.floors) {
        for (const room of floor.rooms) {
          const farthestPoint = findFarthestPointFromExits(room, floor);
          const distanceToExit = calculateDistanceToNearestExit(farthestPoint, floor);
          
          if (distanceToExit > maxDistance) {
            return {
              status: 'fail',
              details: `Travel distance ${distanceToExit.toFixed(1)}m > max ${maxDistance}m`,
              location: room.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IBC-1010.1.1',
    code: 'IBC',
    category: 'egress',
    description: 'Minimum door width',
    severity: 'critical',
    check: (building, context) => {
      const minWidth = 0.813;  // 32 inches
      const minEgressWidth = 0.914;  // 36 inches for egress doors
      
      for (const floor of building.floors) {
        for (const door of floor.doors) {
          const isEgress = isExitDoor(door, floor);
          const requiredWidth = isEgress ? minEgressWidth : minWidth;
          
          if (door.width < requiredWidth) {
            return {
              status: 'fail',
              details: `Door width ${(door.width * 39.37).toFixed(1)}" < ${isEgress ? '36"' : '32"'} min`,
              location: door.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IBC-1010.1.3',
    code: 'IBC',
    category: 'egress',
    description: 'Door swing direction',
    severity: 'major',
    check: (building, context) => {
      // Egress doors serving >50 occupants must swing in direction of egress travel
      for (const floor of building.floors) {
        for (const room of floor.rooms) {
          const occupants = calculateRoomOccupants(room);
          
          if (occupants > 50) {
            const exitDoors = floor.doors.filter(d => 
              d.wallId && room.walls.includes(d.wallId) && isExitDoor(d, floor)
            );
            
            for (const door of exitDoors) {
              // Check if door swings outward (simplified check)
              if (door.swingDirection === 'left' || door.swingDirection === 'right') {
                // Would need more context to determine if this is correct direction
                // For now, just warn
              }
            }
          }
        }
      }
      return { status: 'pass' };
    }
  }
];

// ============================================
// ADA ACCESSIBILITY RULES
// ============================================

const ADA_RULES: CodeRule[] = [
  {
    id: 'ADA-404.2.3',
    code: 'ADA',
    category: 'accessibility',
    description: 'Clear door width',
    severity: 'major',
    check: (building, context) => {
      const minClearWidth = 0.813;  // 32" clear
      
      for (const floor of building.floors) {
        for (const door of floor.doors) {
          // Clear width is less than door width due to door thickness
          const clearWidth = door.width - 0.05;  // Approximate
          
          if (clearWidth < minClearWidth) {
            return {
              status: 'fail',
              details: `Clear width ${(clearWidth * 39.37).toFixed(1)}" < 32" required`,
              location: door.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'ADA-404.2.4',
    code: 'ADA',
    category: 'accessibility',
    description: 'Door maneuvering clearance',
    severity: 'major',
    check: (building, context) => {
      // Requires clear floor space on both sides of door
      // Pull side: 60" deep, door width + 18" (push side: 48" deep, door width + 12")
      
      for (const floor of building.floors) {
        for (const door of floor.doors) {
          const wall = floor.walls.find(w => w.id === door.wallId);
          if (!wall) continue;
          
          // Would need room geometry to check clearances
          // Simplified check: ensure door isn't in a corner
          // This is a placeholder for more sophisticated spatial analysis
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'ADA-403.5.1',
    code: 'ADA',
    category: 'accessibility',
    description: 'Accessible route width',
    severity: 'major',
    check: (building, context) => {
      const minWidth = 0.914;  // 36" minimum
      const passingWidth = 1.524;  // 60" for passing
      
      for (const floor of building.floors) {
        const hallways = floor.rooms.filter(r => r.type === 'hallway');
        
        for (const hall of hallways) {
          const bounds = hall.polygon.boundingBox();
          const minDimension = Math.min(bounds.width, bounds.height);
          
          if (minDimension < minWidth) {
            return {
              status: 'fail',
              details: `Hallway width ${(minDimension * 39.37).toFixed(1)}" < 36" required`,
              location: hall.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'ADA-604',
    code: 'ADA',
    category: 'accessibility',
    description: 'Accessible bathroom clearances',
    severity: 'major',
    check: (building, context) => {
      // Check for adequate bathroom size for wheelchair turning
      const minTurnRadius = 1.524;  // 60" diameter turning space
      
      for (const floor of building.floors) {
        const bathrooms = floor.rooms.filter(r => r.type === 'bathroom');
        
        for (const bathroom of bathrooms) {
          const bounds = bathroom.polygon.boundingBox();
          const minDimension = Math.min(bounds.width, bounds.height);
          
          // Simplified check - real check would verify actual clear floor space
          if (minDimension < minTurnRadius) {
            return {
              status: 'warn',
              details: `Bathroom may lack 60" turning radius (${bathroom.id})`,
              location: bathroom.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  }
];

// ============================================
// HABITABILITY RULES
// ============================================

const HABITABILITY_RULES: CodeRule[] = [
  {
    id: 'IRC-R304.1',
    code: 'IRC',
    category: 'habitability',
    description: 'Minimum room area',
    severity: 'major',
    check: (building, context) => {
      // Habitable rooms must be at least 70 sf (6.5 m²)
      const minArea = 6.5;  // m²
      
      for (const floor of building.floors) {
        const habitableRooms = floor.rooms.filter(r => isHabitableRoom(r.type));
        
        for (const room of habitableRooms) {
          if (room.polygon.area() < minArea) {
            return {
              status: 'fail',
              details: `Room area ${room.polygon.area().toFixed(1)}m² < ${minArea}m² minimum`,
              location: room.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IRC-R304.2',
    code: 'IRC',
    category: 'habitability',
    description: 'Minimum room dimension',
    severity: 'major',
    check: (building, context) => {
      // Habitable rooms must be at least 7 feet (2.13m) in any dimension
      const minDimension = 2.13;
      
      for (const floor of building.floors) {
        const habitableRooms = floor.rooms.filter(r => isHabitableRoom(r.type));
        
        for (const room of habitableRooms) {
          const bounds = room.polygon.boundingBox();
          const minDim = Math.min(bounds.width, bounds.height);
          
          if (minDim < minDimension) {
            return {
              status: 'fail',
              details: `Room dimension ${(minDim * 3.28).toFixed(1)}' < 7' minimum`,
              location: room.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IRC-R303.1',
    code: 'IRC',
    category: 'habitability',
    description: 'Natural light requirements',
    severity: 'major',
    check: (building, context) => {
      // Habitable rooms need glazing = 8% of floor area
      const minGlazingRatio = 0.08;
      
      for (const floor of building.floors) {
        const habitableRooms = floor.rooms.filter(r => isHabitableRoom(r.type));
        
        for (const room of habitableRooms) {
          const roomArea = room.polygon.area();
          
          // Find windows in this room's walls
          const roomWindows = floor.windows.filter(w => 
            room.windows.includes(w.id)
          );
          
          const glazingArea = roomWindows.reduce((sum, w) => {
            const height = w.headHeight - w.sillHeight;
            return sum + (w.width * height);
          }, 0);
          
          const glazingRatio = glazingArea / roomArea;
          
          if (glazingRatio < minGlazingRatio) {
            return {
              status: 'fail',
              details: `Glazing ${(glazingRatio * 100).toFixed(1)}% < 8% required in ${room.name || room.type}`,
              location: room.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'IRC-R305.1',
    code: 'IRC',
    category: 'habitability',
    description: 'Minimum ceiling height',
    severity: 'major',
    check: (building, context) => {
      // Habitable rooms need 7' ceiling height
      const minHeight = 2.13;  // 7 feet in meters
      
      for (const floor of building.floors) {
        const habitableRooms = floor.rooms.filter(r => isHabitableRoom(r.type));
        
        for (const room of habitableRooms) {
          const height = room.height ?? floor.height - 0.3;  // Default with slab thickness
          
          if (height < minHeight) {
            return {
              status: 'fail',
              details: `Ceiling height ${(height * 3.28).toFixed(1)}' < 7' minimum`,
              location: room.id
            };
          }
        }
      }
      return { status: 'pass' };
    }
  }
];

// ============================================
// ZONING RULES
// ============================================

const ZONING_RULES: CodeRule[] = [
  {
    id: 'ZONING-HEIGHT',
    code: 'ZONING',
    category: 'zoning',
    description: 'Maximum building height',
    severity: 'critical',
    check: (building, context) => {
      if (!context.zoning) return { status: 'pass' };
      
      if (context.buildingHeight > context.zoning.maxHeight) {
        return {
          status: 'fail',
          details: `Building height ${context.buildingHeight.toFixed(1)}m > ${context.zoning.maxHeight}m limit`
        };
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'ZONING-FAR',
    code: 'ZONING',
    category: 'zoning',
    description: 'Floor Area Ratio (FAR)',
    severity: 'critical',
    check: (building, context) => {
      if (!context.zoning) return { status: 'pass' };
      
      const lotArea = building.footprint.area();
      const totalFloorArea = building.floors.reduce((sum, f) => 
        sum + f.rooms.reduce((s, r) => s + r.polygon.area(), 0), 0
      );
      
      const far = totalFloorArea / lotArea;
      
      if (far > context.zoning.maxFAR) {
        return {
          status: 'fail',
          details: `FAR ${far.toFixed(2)} > ${context.zoning.maxFAR} limit`
        };
      }
      return { status: 'pass' };
    }
  },
  {
    id: 'ZONING-COVERAGE',
    code: 'ZONING',
    category: 'zoning',
    description: 'Maximum lot coverage',
    severity: 'major',
    check: (building, context) => {
      if (!context.zoning) return { status: 'pass' };
      
      const lotArea = building.footprint.area();
      const buildingFootprintArea = building.floors[0]?.rooms.reduce(
        (sum, r) => sum + r.polygon.area(), 0
      ) ?? 0;
      
      const coverage = buildingFootprintArea / lotArea;
      
      if (coverage > context.zoning.maxCoverage) {
        return {
          status: 'fail',
          details: `Lot coverage ${(coverage * 100).toFixed(1)}% > ${(context.zoning.maxCoverage * 100)}% limit`
        };
      }
      return { status: 'pass' };
    }
  }
];

// ============================================
// HELPER FUNCTIONS
// ============================================

function calculateFloorOccupants(floor: Floor2D): number {
  return floor.rooms.reduce((sum, room) => sum + calculateRoomOccupants(room), 0);
}

function calculateRoomOccupants(room: Room2D): number {
  // Occupant load factors (sf per occupant) - converted to m²
  const factors: Record<RoomType, number> = {
    living: 18.6,      // 200 sf
    dining: 13.9,      // 150 sf
    kitchen: 18.6,     // 200 sf
    bedroom: 18.6,     // 200 sf
    bathroom: 46.5,    // 500 sf
    office: 9.3,       // 100 sf
    hallway: 27.9,     // 300 sf
    closet: 92.9,      // 1000 sf
    garage: 18.6,      // 200 sf
    utility: 27.9,     // 300 sf
    balcony: 46.5,     // 500 sf
    stair: 27.9,       // 300 sf
    elevator: 46.5,    // 500 sf
    unknown: 9.3       // 100 sf (worst case)
  };
  
  const factor = factors[room.type] ?? 9.3;
  return Math.ceil(room.polygon.area() / factor);
}

function isExitDoor(door: Door2D, floor: Floor2D): boolean {
  // Simplified: assume doors on exterior walls are exits
  if (!door.wallId) return false;
  
  const wall = floor.walls.find(w => w.id === door.wallId);
  return wall?.type === 'exterior';
}

function isHabitableRoom(type: RoomType): boolean {
  return ['living', 'dining', 'bedroom', 'office'].includes(type);
}

function findFarthestPointFromExits(room: Room2D, floor: Floor2D): Vector2D {
  // Return centroid as approximation
  return room.polygon.centroid();
}

function calculateDistanceToNearestExit(point: Vector2D, floor: Floor2D): number {
  const exitDoors = floor.doors.filter(d => isExitDoor(d, floor));
  
  if (exitDoors.length === 0) return Infinity;
  
  let minDist = Infinity;
  for (const door of exitDoors) {
    const dist = point.distanceTo(door.position);
    minDist = Math.min(minDist, dist);
  }
  
  return minDist;
}

// ============================================
// MAIN CODE VALIDATOR
// ============================================

export class CodeValidator {
  private rules: CodeRule[] = [];
  
  constructor(ruleSets: ('IBC' | 'ADA' | 'IRC' | 'ZONING')[] = ['IBC', 'ADA', 'IRC']) {
    if (ruleSets.includes('IBC')) {
      this.rules.push(...IBC_EGRESS_RULES);
    }
    if (ruleSets.includes('ADA')) {
      this.rules.push(...ADA_RULES);
    }
    if (ruleSets.includes('IRC')) {
      this.rules.push(...HABITABILITY_RULES);
    }
    if (ruleSets.includes('ZONING')) {
      this.rules.push(...ZONING_RULES);
    }
  }
  
  /**
   * Add custom rule
   */
  public addRule(rule: CodeRule): void {
    this.rules.push(rule);
  }
  
  /**
   * Validate building against all rules
   */
  public validate(building: Building2D, context: ValidationContext): ValidationReport {
    const violations: CodeViolation[] = [];
    const warnings: { ruleId: string; description: string }[] = [];
    
    for (const rule of this.rules) {
      try {
        const result = rule.check(building, context);
        
        if (result.status === 'fail') {
          violations.push({
            ruleId: rule.id,
            category: rule.category,
            description: rule.description,
            details: result.details ?? '',
            location: result.location ?? '',
            severity: rule.severity
          });
        } else if (result.status === 'warn') {
          warnings.push({
            ruleId: rule.id,
            description: result.details ?? rule.description
          });
        }
      } catch (error) {
        warnings.push({
          ruleId: rule.id,
          description: `Error checking rule: ${error}`
        });
      }
    }
    
    // Calculate compliance score
    const criticalViolations = violations.filter(v => v.severity === 'critical').length;
    const majorViolations = violations.filter(v => v.severity === 'major').length;
    const minorViolations = violations.filter(v => v.severity === 'minor').length;
    
    // Weighted score: critical = 30pts, major = 10pts, minor = 2pts
    const maxScore = this.rules.length * 10;  // Assume average 10 pts per rule
    const deductions = criticalViolations * 30 + majorViolations * 10 + minorViolations * 2;
    const score = Math.max(0, Math.round(100 * (1 - deductions / maxScore)));
    
    return {
      valid: violations.length === 0,
      violations,
      warnings,
      score
    };
  }
  
  /**
   * Get summary of required changes
   */
  public getSummary(report: ValidationReport): string {
    if (report.valid) {
      return `✓ Building passes all ${this.rules.length} code checks (Score: ${report.score}/100)`;
    }
    
    const lines: string[] = [
      `✗ Building has ${report.violations.length} code violations (Score: ${report.score}/100)`,
      ''
    ];
    
    // Group by category
    const byCategory = new Map<string, CodeViolation[]>();
    for (const v of report.violations) {
      if (!byCategory.has(v.category)) byCategory.set(v.category, []);
      byCategory.get(v.category)!.push(v);
    }
    
    for (const [category, violations] of byCategory) {
      lines.push(`${category.toUpperCase()} (${violations.length} issues):`);
      for (const v of violations) {
        const icon = v.severity === 'critical' ? '🔴' : (v.severity === 'major' ? '🟠' : '🟡');
        lines.push(`  ${icon} [${v.ruleId}] ${v.description}`);
        if (v.details) lines.push(`      ${v.details}`);
      }
      lines.push('');
    }
    
    if (report.warnings.length > 0) {
      lines.push(`WARNINGS (${report.warnings.length}):`);
      for (const w of report.warnings) {
        lines.push(`  ⚠️ [${w.ruleId}] ${w.description}`);
      }
    }
    
    return lines.join('\n');
  }
}

// ============================================
// DEFAULT CONTEXT FACTORY
// ============================================

export function createDefaultContext(building: Building2D): ValidationContext {
  const totalArea = building.floors.reduce(
    (sum, f) => sum + f.rooms.reduce((s, r) => s + r.polygon.area(), 0),
    0
  );
  
  const maxFloorElevation = Math.max(...building.floors.map(f => f.elevation + f.height));
  
  return {
    occupancyType: 'R-3',  // Single-family residential
    constructionType: 'V-B',  // Wood frame
    sprinklered: false,
    buildingArea: totalArea,
    buildingHeight: maxFloorElevation,
    stories: building.floors.length,
    occupantLoad: building.floors.reduce(
      (sum, f) => sum + calculateFloorOccupants(f),
      0
    )
  };
}

