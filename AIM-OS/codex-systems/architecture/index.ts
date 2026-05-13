/**
 * Architecture Module - Complete Procedural Architecture System
 * 
 * Systems included:
 * 1. SpacePlanner - Generate room layouts from requirements
 * 2. Building3DGenerator - Create 3D models from floor plans
 * 3. CADExporter - Export to DXF format
 * 4. StyleEngine - Apply architectural styles
 * 5. CodeValidator - Building code compliance checking
 * 
 * Based on research:
 * - Parish & Müller (2001) - L-system roads
 * - Müller et al. (2006) - CGA Shape grammar
 * - Stiny (1980) - Shape grammars
 * - IBC/ADA/IRC building codes
 */

// Core types
export * from './types';

// Space Planning
export {
  SpacePlanner,
  SpacePlannerConfig,
  DEFAULT_PLANNER_CONFIG,
  TreemapAllocator,
  BSPAllocator,
  ForceDirectedOptimizer,
  AdjacencyMatrix,
  LayoutValidator
} from './planning/SpacePlanner';

// 3D Building Generation
export {
  Building3DGenerator,
  GeneratorConfig,
  DEFAULT_GENERATOR_CONFIG,
  WallGenerator,
  OpeningGenerator,
  RoofGenerator,
  FloorSlabGenerator
} from './generation/Building3DGenerator';

// CAD Export
export {
  CADExporter,
  CADLayer,
  STANDARD_LAYERS,
  DXFEntity,
  DXFLine,
  DXFPolyline,
  DXFCircle,
  DXFArc,
  DXFText,
  DXFDimension,
  DXFHatch,
  DXFInsert,
  DXFBlock
} from './export/CADExporter';

// Style System
export {
  StyleEngine,
  ARCHITECTURAL_STYLES,
  StyleParameters,
  StyledBuilding,
  StyledWall,
  StyledDoor,
  StyledWindow
} from './style/StyleEngine';

// Code Validation
export {
  CodeValidator,
  CodeRule,
  ValidationContext,
  OccupancyType,
  ConstructionType,
  ZoningRequirements,
  createDefaultContext
} from './validation/CodeValidator';

// ============================================
// CONVENIENCE FUNCTIONS
// ============================================

import { SpacePlanner } from './planning/SpacePlanner';
import { Building3DGenerator } from './generation/Building3DGenerator';
import { CADExporter } from './export/CADExporter';
import { StyleEngine } from './style/StyleEngine';
import { CodeValidator, createDefaultContext } from './validation/CodeValidator';
import { 
  BuildingProgram, 
  Rectangle, 
  Building2D, 
  ArchitecturalStyleId, 
  RoofType,
  ValidationReport 
} from './types';
import * as THREE from 'three';

/**
 * Generate a complete building from a program
 * End-to-end pipeline: requirements → 3D model
 */
export async function generateBuilding(
  program: BuildingProgram,
  siteWidth: number,
  siteDepth: number,
  options: {
    style?: ArchitecturalStyleId;
    roofType?: RoofType;
    validate?: boolean;
  } = {}
): Promise<{
  building2D: Building2D;
  building3D: THREE.Group;
  dxf: string;
  validation?: ValidationReport;
}> {
  const siteBounds = new Rectangle(0, 0, siteWidth, siteDepth);
  
  // 1. Space Planning
  const planner = new SpacePlanner({ algorithm: 'hybrid' });
  const layout = planner.plan(program, siteBounds);
  
  // 2. Convert layout to Building2D
  const building2D = layoutToBuilding2D(layout, program);
  
  // 3. Apply Style
  const styleEngine = new StyleEngine();
  const styledBuilding = options.style 
    ? styleEngine.applyStyle(building2D, options.style)
    : building2D;
  
  // 4. Generate 3D
  const generator = new Building3DGenerator();
  const building3D = generator.generate(styledBuilding, options.roofType ?? 'gable');
  
  // 5. Export DXF
  const exporter = new CADExporter();
  const dxf = exporter.export(styledBuilding);
  
  // 6. Validate (optional)
  let validation: ValidationReport | undefined;
  if (options.validate !== false) {
    const validator = new CodeValidator(['IBC', 'ADA', 'IRC']);
    const context = createDefaultContext(building2D);
    validation = validator.validate(building2D, context);
  }
  
  return {
    building2D: styledBuilding,
    building3D: building3D.group,
    dxf,
    validation
  };
}

/**
 * Convert layout result to Building2D structure
 */
function layoutToBuilding2D(
  layout: { rooms: Map<string, Rectangle> },
  program: BuildingProgram
): Building2D {
  const walls: import('./types').Wall2D[] = [];
  const rooms: import('./types').Room2D[] = [];
  const doors: import('./types').Door2D[] = [];
  const windows: import('./types').Window2D[] = [];
  
  let wallId = 0;
  let doorId = 0;
  let windowId = 0;
  
  // Convert each room rectangle
  for (const [spaceId, rect] of layout.rooms) {
    const spaceReq = program.spaces.find(s => s.id === spaceId);
    if (!spaceReq) continue;
    
    const polygon = new (await import('./types')).Polygon(rect.getCorners());
    
    // Create room
    const room: import('./types').Room2D = {
      id: spaceId,
      name: spaceReq.name,
      type: spaceReq.type,
      polygon,
      floor: 0,
      walls: [],
      doors: [],
      windows: []
    };
    
    // Create walls for room edges
    const edges = rect.getEdges();
    for (let i = 0; i < edges.length; i++) {
      const edge = edges[i];
      const wId = `wall_${wallId++}`;
      
      const wall: import('./types').Wall2D = {
        id: wId,
        start: edge.start,
        end: edge.end,
        thickness: 0.15,
        type: i === 0 || i === 2 ? 'exterior' : 'interior'  // Simplified
      };
      walls.push(wall);
      room.walls.push(wId);
      
      // Add window to exterior walls
      if (wall.type === 'exterior' && edge.length() > 1.5) {
        const windowPos = edge.midpoint();
        const wndId = `window_${windowId++}`;
        
        windows.push({
          id: wndId,
          type: 'window',
          windowType: 'casement',
          position: windowPos,
          width: Math.min(1.2, edge.length() * 0.4),
          sillHeight: 0.9,
          headHeight: 2.1,
          wallId: wId,
          paneCount: 2
        });
        room.windows.push(wndId);
      }
    }
    
    // Add door if room is habitable
    if (['living', 'bedroom', 'office', 'kitchen', 'dining'].includes(spaceReq.type)) {
      const doorWall = walls.find(w => room.walls.includes(w.id) && w.type === 'interior');
      if (doorWall) {
        const doorPos = new (await import('./types')).LineSegment(
          doorWall.start, doorWall.end
        ).midpoint();
        const dId = `door_${doorId++}`;
        
        doors.push({
          id: dId,
          type: 'door',
          doorType: 'hinged',
          position: doorPos,
          width: 0.9,
          sillHeight: 0,
          headHeight: 2.1,
          wallId: doorWall.id,
          swingDirection: 'left',
          swingAngle: Math.PI / 2
        });
        room.doors.push(dId);
      }
    }
    
    rooms.push(room);
  }
  
  // Find overall footprint
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const rect of layout.rooms.values()) {
    minX = Math.min(minX, rect.minX);
    minY = Math.min(minY, rect.minY);
    maxX = Math.max(maxX, rect.maxX);
    maxY = Math.max(maxY, rect.maxY);
  }
  
  const footprint = new (await import('./types')).Polygon([
    new (await import('./types')).Vector2D(minX, minY),
    new (await import('./types')).Vector2D(maxX, minY),
    new (await import('./types')).Vector2D(maxX, maxY),
    new (await import('./types')).Vector2D(minX, maxY)
  ]);
  
  return {
    id: `building_${Date.now()}`,
    name: program.name,
    floors: [{
      id: 'floor_0',
      level: 0,
      elevation: 0,
      height: 3.0,
      walls,
      rooms,
      doors,
      windows
    }],
    footprint,
    totalArea: rooms.reduce((sum, r) => sum + r.polygon.area(), 0)
  };
}

