/**
 * CAD Exporter
 * Exports 2D building data to DXF format
 * 
 * Features:
 * - DXF R2000/R2004 compatible output
 * - Layer system with standard AIA naming
 * - All architectural entities (walls, doors, windows, dimensions)
 * - Block definitions for symbols
 * - Hatch patterns for materials
 * - Automatic dimensioning
 */

import {
  Vector2D,
  Rectangle,
  Polygon,
  Wall2D,
  Door2D,
  Window2D,
  Room2D,
  Floor2D,
  Building2D
} from '../types';

// ============================================
// LAYER DEFINITIONS
// ============================================

export interface CADLayer {
  name: string;
  color: number;       // AutoCAD Color Index (ACI)
  lineWeight: number;  // Hundredths of mm
  lineType: string;
  frozen: boolean;
  locked: boolean;
}

export const STANDARD_LAYERS: CADLayer[] = [
  { name: 'A-WALL', color: 7, lineWeight: 50, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-WALL-PATT', color: 8, lineWeight: 25, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-DOOR', color: 5, lineWeight: 35, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-GLAZ', color: 4, lineWeight: 35, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-FLOR', color: 8, lineWeight: 18, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-FURN', color: 6, lineWeight: 18, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-DIMS', color: 1, lineWeight: 25, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-ANNO', color: 3, lineWeight: 25, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-ANNO-NOTE', color: 7, lineWeight: 18, lineType: 'CONTINUOUS', frozen: false, locked: false },
  { name: 'A-GRID', color: 9, lineWeight: 18, lineType: 'DASHED', frozen: false, locked: false }
];

// ============================================
// DXF ENTITY TYPES
// ============================================

export type DXFEntityType = 
  | 'LINE' | 'POLYLINE' | 'LWPOLYLINE' | 'CIRCLE' | 'ARC' 
  | 'TEXT' | 'MTEXT' | 'DIMENSION' | 'HATCH' | 'INSERT';

export interface DXFEntity {
  type: DXFEntityType;
  layer: string;
  handle?: string;
}

export interface DXFLine extends DXFEntity {
  type: 'LINE';
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DXFPolyline extends DXFEntity {
  type: 'LWPOLYLINE';
  vertices: [number, number][];
  closed: boolean;
}

export interface DXFCircle extends DXFEntity {
  type: 'CIRCLE';
  cx: number;
  cy: number;
  radius: number;
}

export interface DXFArc extends DXFEntity {
  type: 'ARC';
  cx: number;
  cy: number;
  radius: number;
  startAngle: number;  // Degrees
  endAngle: number;
}

export interface DXFText extends DXFEntity {
  type: 'TEXT';
  x: number;
  y: number;
  height: number;
  text: string;
  rotation?: number;
  horizontalJustification?: 'left' | 'center' | 'right';
}

export interface DXFDimension extends DXFEntity {
  type: 'DIMENSION';
  dimensionType: 'linear' | 'aligned' | 'angular' | 'radial';
  point1: [number, number];
  point2: [number, number];
  textPosition: [number, number];
  rotation?: number;
}

export interface DXFHatch extends DXFEntity {
  type: 'HATCH';
  patternName: string;
  patternScale: number;
  patternAngle: number;
  boundary: [number, number][];
}

export interface DXFInsert extends DXFEntity {
  type: 'INSERT';
  blockName: string;
  x: number;
  y: number;
  scaleX: number;
  scaleY: number;
  rotation: number;
}

export type AnyDXFEntity = 
  | DXFLine | DXFPolyline | DXFCircle | DXFArc 
  | DXFText | DXFDimension | DXFHatch | DXFInsert;

// ============================================
// BLOCK DEFINITIONS
// ============================================

export interface DXFBlock {
  name: string;
  basePoint: [number, number];
  entities: AnyDXFEntity[];
}

// ============================================
// DXF STRING BUILDER
// ============================================

class DXFBuilder {
  private output: string[] = [];
  private handleCounter: number = 256;  // Start after reserved handles
  
  public getHandle(): string {
    const handle = this.handleCounter.toString(16).toUpperCase();
    this.handleCounter++;
    return handle;
  }
  
  public add(code: number, value: string | number): void {
    this.output.push(code.toString());
    this.output.push(String(value));
  }
  
  public addGroup(pairs: [number, string | number][]): void {
    for (const [code, value] of pairs) {
      this.add(code, value);
    }
  }
  
  public build(): string {
    return this.output.join('\n') + '\n';
  }
}

// ============================================
// MAIN CAD EXPORTER
// ============================================

export class CADExporter {
  private layers: CADLayer[];
  private entities: AnyDXFEntity[] = [];
  private blocks: DXFBlock[] = [];
  
  constructor(customLayers?: CADLayer[]) {
    this.layers = customLayers ?? STANDARD_LAYERS;
    this.initializeStandardBlocks();
  }
  
  private initializeStandardBlocks(): void {
    // Door symbol block
    this.blocks.push({
      name: 'DOOR_SWING',
      basePoint: [0, 0],
      entities: [
        { type: 'LINE', layer: 'A-DOOR', x1: 0, y1: 0, x2: 0.8, y2: 0 },
        { type: 'ARC', layer: 'A-DOOR', cx: 0, cy: 0, radius: 0.8, startAngle: 0, endAngle: 90 }
      ]
    });
    
    // Window symbol block
    this.blocks.push({
      name: 'WINDOW_DOUBLE',
      basePoint: [0, 0],
      entities: [
        { type: 'LINE', layer: 'A-GLAZ', x1: 0, y1: 0, x2: 1.0, y2: 0 },
        { type: 'LINE', layer: 'A-GLAZ', x1: 0, y1: 0.15, x2: 1.0, y2: 0.15 },
        { type: 'LINE', layer: 'A-GLAZ', x1: 0.5, y1: 0, x2: 0.5, y2: 0.15 }
      ]
    });
    
    // North arrow block
    this.blocks.push({
      name: 'NORTH_ARROW',
      basePoint: [0, 0],
      entities: [
        { type: 'LWPOLYLINE', layer: 'A-ANNO', vertices: [[0, 0], [0.5, 1.5], [0, 1.2]], closed: true },
        { type: 'LWPOLYLINE', layer: 'A-ANNO', vertices: [[0, 0], [-0.5, 1.5], [0, 1.2]], closed: true },
        { type: 'TEXT', layer: 'A-ANNO', x: 0, y: 1.8, height: 0.3, text: 'N' }
      ]
    });
  }
  
  /**
   * Export building to DXF format
   */
  public export(building: Building2D): string {
    this.entities = [];
    
    // Process each floor
    for (const floor of building.floors) {
      this.processFloor(floor);
    }
    
    // Build DXF file
    return this.buildDXF();
  }
  
  /**
   * Export single floor plan
   */
  public exportFloor(floor: Floor2D): string {
    this.entities = [];
    this.processFloor(floor);
    return this.buildDXF();
  }
  
  private processFloor(floor: Floor2D): void {
    // Draw walls
    for (const wall of floor.walls) {
      this.drawWall(wall);
    }
    
    // Draw doors
    for (const door of floor.doors) {
      const wall = floor.walls.find(w => w.id === door.wallId);
      if (wall) {
        this.drawDoor(door, wall);
      }
    }
    
    // Draw windows
    for (const window of floor.windows) {
      const wall = floor.walls.find(w => w.id === window.wallId);
      if (wall) {
        this.drawWindow(window, wall);
      }
    }
    
    // Draw room labels
    for (const room of floor.rooms) {
      this.drawRoomLabel(room);
    }
    
    // Add dimensions
    this.addDimensions(floor);
  }
  
  private drawWall(wall: Wall2D): void {
    const thickness = wall.thickness ?? 0.15;
    
    // Calculate wall corners
    const dir = wall.end.sub(wall.start).normalize();
    const perp = new Vector2D(-dir.y, dir.x);
    const offset = perp.scale(thickness / 2);
    
    const corners: [number, number][] = [
      [wall.start.x + offset.x, wall.start.y + offset.y],
      [wall.end.x + offset.x, wall.end.y + offset.y],
      [wall.end.x - offset.x, wall.end.y - offset.y],
      [wall.start.x - offset.x, wall.start.y - offset.y]
    ];
    
    // Wall outline
    this.entities.push({
      type: 'LWPOLYLINE',
      layer: 'A-WALL',
      vertices: corners,
      closed: true
    });
    
    // Wall hatch for exterior walls
    if (wall.type === 'exterior') {
      this.entities.push({
        type: 'HATCH',
        layer: 'A-WALL-PATT',
        patternName: 'ANSI31',
        patternScale: 0.5,
        patternAngle: 45,
        boundary: corners
      });
    }
  }
  
  private drawDoor(door: Door2D, wall: Wall2D): void {
    const wallDir = wall.end.sub(wall.start).normalize();
    const perp = new Vector2D(-wallDir.y, wallDir.x);
    
    // Door opening lines (gap in wall representation)
    const x1 = door.position.x - wallDir.x * door.width / 2;
    const y1 = door.position.y - wallDir.y * door.width / 2;
    const x2 = door.position.x + wallDir.x * door.width / 2;
    const y2 = door.position.y + wallDir.y * door.width / 2;
    
    // Door threshold line
    this.entities.push({
      type: 'LINE',
      layer: 'A-DOOR',
      x1, y1, x2, y2
    });
    
    // Door leaf line (current position)
    const leafAngle = Math.atan2(wallDir.y, wallDir.x) + 
      (door.swingDirection === 'left' ? door.swingAngle : -door.swingAngle);
    const leafEnd = new Vector2D(
      x1 + Math.cos(leafAngle) * door.width,
      y1 + Math.sin(leafAngle) * door.width
    );
    
    this.entities.push({
      type: 'LINE',
      layer: 'A-DOOR',
      x1, y1,
      x2: leafEnd.x,
      y2: leafEnd.y
    });
    
    // Swing arc
    const wallAngle = Math.atan2(wallDir.y, wallDir.x) * 180 / Math.PI;
    const startAngle = wallAngle;
    const endAngle = wallAngle + (door.swingDirection === 'left' ? 90 : -90);
    
    this.entities.push({
      type: 'ARC',
      layer: 'A-DOOR',
      cx: x1,
      cy: y1,
      radius: door.width,
      startAngle: Math.min(startAngle, endAngle),
      endAngle: Math.max(startAngle, endAngle)
    });
  }
  
  private drawWindow(window: Window2D, wall: Wall2D): void {
    const wallDir = wall.end.sub(wall.start).normalize();
    const perp = new Vector2D(-wallDir.y, wallDir.x);
    const thickness = wall.thickness ?? 0.15;
    
    // Window position along wall
    const center = window.position;
    const halfWidth = window.width / 2;
    
    const p1 = new Vector2D(
      center.x - wallDir.x * halfWidth,
      center.y - wallDir.y * halfWidth
    );
    const p2 = new Vector2D(
      center.x + wallDir.x * halfWidth,
      center.y + wallDir.y * halfWidth
    );
    
    // Window frame (outer rectangle)
    const offset1 = perp.scale(thickness / 2);
    const offset2 = perp.scale(-thickness / 2);
    
    this.entities.push({
      type: 'LWPOLYLINE',
      layer: 'A-GLAZ',
      vertices: [
        [p1.x + offset1.x, p1.y + offset1.y],
        [p2.x + offset1.x, p2.y + offset1.y],
        [p2.x + offset2.x, p2.y + offset2.y],
        [p1.x + offset2.x, p1.y + offset2.y]
      ],
      closed: true
    });
    
    // Glass pane lines (parallel to wall)
    const glassOffset1 = perp.scale(thickness * 0.2);
    const glassOffset2 = perp.scale(-thickness * 0.2);
    
    this.entities.push({
      type: 'LINE',
      layer: 'A-GLAZ',
      x1: p1.x + glassOffset1.x, y1: p1.y + glassOffset1.y,
      x2: p2.x + glassOffset1.x, y2: p2.y + glassOffset1.y
    });
    
    this.entities.push({
      type: 'LINE',
      layer: 'A-GLAZ',
      x1: p1.x + glassOffset2.x, y1: p1.y + glassOffset2.y,
      x2: p2.x + glassOffset2.x, y2: p2.y + glassOffset2.y
    });
    
    // Mullion if multiple panes
    if (window.paneCount > 1) {
      this.entities.push({
        type: 'LINE',
        layer: 'A-GLAZ',
        x1: center.x + glassOffset1.x, y1: center.y + glassOffset1.y,
        x2: center.x + glassOffset2.x, y2: center.y + glassOffset2.y
      });
    }
  }
  
  private drawRoomLabel(room: Room2D): void {
    const center = room.polygon.centroid();
    const area = room.polygon.area();
    
    // Room name
    const name = room.name ?? this.getRoomTypeName(room.type);
    
    this.entities.push({
      type: 'TEXT',
      layer: 'A-ANNO',
      x: center.x,
      y: center.y + 0.2,
      height: 0.2,
      text: name.toUpperCase(),
      horizontalJustification: 'center'
    });
    
    // Area text
    this.entities.push({
      type: 'TEXT',
      layer: 'A-ANNO-NOTE',
      x: center.x,
      y: center.y - 0.2,
      height: 0.15,
      text: `${area.toFixed(1)} m²`,
      horizontalJustification: 'center'
    });
  }
  
  private getRoomTypeName(type: string): string {
    const names: Record<string, string> = {
      living: 'Living Room',
      dining: 'Dining Room',
      kitchen: 'Kitchen',
      bedroom: 'Bedroom',
      bathroom: 'Bathroom',
      office: 'Office',
      hallway: 'Hall',
      closet: 'Closet',
      garage: 'Garage',
      utility: 'Utility',
      balcony: 'Balcony',
      stair: 'Stair',
      unknown: 'Room'
    };
    return names[type] ?? type;
  }
  
  private addDimensions(floor: Floor2D): void {
    // Find overall bounding box
    let minX = Infinity, minY = Infinity;
    let maxX = -Infinity, maxY = -Infinity;
    
    for (const wall of floor.walls) {
      minX = Math.min(minX, wall.start.x, wall.end.x);
      minY = Math.min(minY, wall.start.y, wall.end.y);
      maxX = Math.max(maxX, wall.start.x, wall.end.x);
      maxY = Math.max(maxY, wall.start.y, wall.end.y);
    }
    
    const dimOffset = 1.0;  // Distance from building
    
    // Overall width dimension
    this.entities.push({
      type: 'DIMENSION',
      layer: 'A-DIMS',
      dimensionType: 'linear',
      point1: [minX, minY - dimOffset],
      point2: [maxX, minY - dimOffset],
      textPosition: [(minX + maxX) / 2, minY - dimOffset - 0.3]
    });
    
    // Overall height dimension
    this.entities.push({
      type: 'DIMENSION',
      layer: 'A-DIMS',
      dimensionType: 'linear',
      point1: [maxX + dimOffset, minY],
      point2: [maxX + dimOffset, maxY],
      textPosition: [maxX + dimOffset + 0.3, (minY + maxY) / 2],
      rotation: 90
    });
    
    // Room dimensions
    for (const room of floor.rooms) {
      const bounds = room.polygon.boundingBox();
      const roomDimOffset = 0.3;
      
      // Width
      this.entities.push({
        type: 'DIMENSION',
        layer: 'A-DIMS',
        dimensionType: 'linear',
        point1: [bounds.minX, bounds.maxY + roomDimOffset],
        point2: [bounds.maxX, bounds.maxY + roomDimOffset],
        textPosition: [bounds.center().x, bounds.maxY + roomDimOffset + 0.15]
      });
      
      // Height
      this.entities.push({
        type: 'DIMENSION',
        layer: 'A-DIMS',
        dimensionType: 'linear',
        point1: [bounds.maxX + roomDimOffset, bounds.minY],
        point2: [bounds.maxX + roomDimOffset, bounds.maxY],
        textPosition: [bounds.maxX + roomDimOffset + 0.15, bounds.center().y],
        rotation: 90
      });
    }
  }
  
  private buildDXF(): string {
    const builder = new DXFBuilder();
    
    // HEADER section
    this.writeHeader(builder);
    
    // TABLES section
    this.writeTables(builder);
    
    // BLOCKS section
    this.writeBlocks(builder);
    
    // ENTITIES section
    this.writeEntities(builder);
    
    // End of file
    builder.add(0, 'EOF');
    
    return builder.build();
  }
  
  private writeHeader(builder: DXFBuilder): void {
    builder.add(0, 'SECTION');
    builder.add(2, 'HEADER');
    
    // AutoCAD version
    builder.add(9, '$ACADVER');
    builder.add(1, 'AC1015');  // AutoCAD 2000
    
    // Units (meters)
    builder.add(9, '$INSUNITS');
    builder.add(70, 6);  // Meters
    
    // Drawing units
    builder.add(9, '$LUNITS');
    builder.add(70, 2);  // Decimal
    
    // Precision
    builder.add(9, '$LUPREC');
    builder.add(70, 4);  // 4 decimal places
    
    builder.add(0, 'ENDSEC');
  }
  
  private writeTables(builder: DXFBuilder): void {
    builder.add(0, 'SECTION');
    builder.add(2, 'TABLES');
    
    // LTYPE table
    this.writeLinetypeTable(builder);
    
    // LAYER table
    this.writeLayerTable(builder);
    
    // STYLE table (text styles)
    this.writeStyleTable(builder);
    
    // DIMSTYLE table
    this.writeDimStyleTable(builder);
    
    builder.add(0, 'ENDSEC');
  }
  
  private writeLinetypeTable(builder: DXFBuilder): void {
    builder.add(0, 'TABLE');
    builder.add(2, 'LTYPE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTable');
    builder.add(70, 3);  // Number of linetypes
    
    // CONTINUOUS
    builder.add(0, 'LTYPE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTableRecord');
    builder.add(100, 'AcDbLinetypeTableRecord');
    builder.add(2, 'CONTINUOUS');
    builder.add(70, 0);
    builder.add(3, 'Solid line');
    builder.add(72, 65);
    builder.add(73, 0);
    builder.add(40, 0);
    
    // DASHED
    builder.add(0, 'LTYPE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTableRecord');
    builder.add(100, 'AcDbLinetypeTableRecord');
    builder.add(2, 'DASHED');
    builder.add(70, 0);
    builder.add(3, 'Dashed line');
    builder.add(72, 65);
    builder.add(73, 2);
    builder.add(40, 0.5);
    builder.add(49, 0.25);
    builder.add(74, 0);
    builder.add(49, -0.25);
    builder.add(74, 0);
    
    builder.add(0, 'ENDTAB');
  }
  
  private writeLayerTable(builder: DXFBuilder): void {
    builder.add(0, 'TABLE');
    builder.add(2, 'LAYER');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTable');
    builder.add(70, this.layers.length);
    
    for (const layer of this.layers) {
      builder.add(0, 'LAYER');
      builder.add(5, builder.getHandle());
      builder.add(100, 'AcDbSymbolTableRecord');
      builder.add(100, 'AcDbLayerTableRecord');
      builder.add(2, layer.name);
      builder.add(70, (layer.frozen ? 1 : 0) | (layer.locked ? 4 : 0));
      builder.add(62, layer.color);
      builder.add(6, layer.lineType);
      builder.add(370, layer.lineWeight);
    }
    
    builder.add(0, 'ENDTAB');
  }
  
  private writeStyleTable(builder: DXFBuilder): void {
    builder.add(0, 'TABLE');
    builder.add(2, 'STYLE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTable');
    builder.add(70, 1);
    
    // STANDARD style
    builder.add(0, 'STYLE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTableRecord');
    builder.add(100, 'AcDbTextStyleTableRecord');
    builder.add(2, 'STANDARD');
    builder.add(70, 0);
    builder.add(40, 0);
    builder.add(41, 1);
    builder.add(50, 0);
    builder.add(71, 0);
    builder.add(42, 0.2);
    builder.add(3, 'arial.ttf');
    
    builder.add(0, 'ENDTAB');
  }
  
  private writeDimStyleTable(builder: DXFBuilder): void {
    builder.add(0, 'TABLE');
    builder.add(2, 'DIMSTYLE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTable');
    builder.add(100, 'AcDbDimStyleTable');
    builder.add(70, 1);
    
    // STANDARD dimension style
    builder.add(0, 'DIMSTYLE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbSymbolTableRecord');
    builder.add(100, 'AcDbDimStyleTableRecord');
    builder.add(2, 'STANDARD');
    builder.add(70, 0);
    builder.add(41, 0.1);   // DIMASZ - arrow size
    builder.add(42, 0);     // DIMEXE
    builder.add(43, 0.1);   // DIMDLI
    builder.add(44, 0.1);   // DIMEXO
    builder.add(140, 0.15); // DIMTXT - text height
    
    builder.add(0, 'ENDTAB');
  }
  
  private writeBlocks(builder: DXFBuilder): void {
    builder.add(0, 'SECTION');
    builder.add(2, 'BLOCKS');
    
    for (const block of this.blocks) {
      builder.add(0, 'BLOCK');
      builder.add(5, builder.getHandle());
      builder.add(100, 'AcDbEntity');
      builder.add(8, '0');
      builder.add(100, 'AcDbBlockBegin');
      builder.add(2, block.name);
      builder.add(70, 0);
      builder.add(10, block.basePoint[0]);
      builder.add(20, block.basePoint[1]);
      builder.add(30, 0);
      builder.add(3, block.name);
      builder.add(1, '');
      
      // Block entities
      for (const entity of block.entities) {
        this.writeEntity(builder, entity);
      }
      
      builder.add(0, 'ENDBLK');
      builder.add(5, builder.getHandle());
      builder.add(100, 'AcDbEntity');
      builder.add(8, '0');
      builder.add(100, 'AcDbBlockEnd');
    }
    
    builder.add(0, 'ENDSEC');
  }
  
  private writeEntities(builder: DXFBuilder): void {
    builder.add(0, 'SECTION');
    builder.add(2, 'ENTITIES');
    
    for (const entity of this.entities) {
      this.writeEntity(builder, entity);
    }
    
    builder.add(0, 'ENDSEC');
  }
  
  private writeEntity(builder: DXFBuilder, entity: AnyDXFEntity): void {
    switch (entity.type) {
      case 'LINE':
        this.writeLine(builder, entity as DXFLine);
        break;
      case 'LWPOLYLINE':
        this.writePolyline(builder, entity as DXFPolyline);
        break;
      case 'CIRCLE':
        this.writeCircle(builder, entity as DXFCircle);
        break;
      case 'ARC':
        this.writeArc(builder, entity as DXFArc);
        break;
      case 'TEXT':
        this.writeText(builder, entity as DXFText);
        break;
      case 'DIMENSION':
        this.writeDimension(builder, entity as DXFDimension);
        break;
      case 'HATCH':
        this.writeHatch(builder, entity as DXFHatch);
        break;
      case 'INSERT':
        this.writeInsert(builder, entity as DXFInsert);
        break;
    }
  }
  
  private writeLine(builder: DXFBuilder, line: DXFLine): void {
    builder.add(0, 'LINE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, line.layer);
    builder.add(100, 'AcDbLine');
    builder.add(10, line.x1);
    builder.add(20, line.y1);
    builder.add(30, 0);
    builder.add(11, line.x2);
    builder.add(21, line.y2);
    builder.add(31, 0);
  }
  
  private writePolyline(builder: DXFBuilder, poly: DXFPolyline): void {
    builder.add(0, 'LWPOLYLINE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, poly.layer);
    builder.add(100, 'AcDbPolyline');
    builder.add(90, poly.vertices.length);
    builder.add(70, poly.closed ? 1 : 0);
    
    for (const [x, y] of poly.vertices) {
      builder.add(10, x);
      builder.add(20, y);
    }
  }
  
  private writeCircle(builder: DXFBuilder, circle: DXFCircle): void {
    builder.add(0, 'CIRCLE');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, circle.layer);
    builder.add(100, 'AcDbCircle');
    builder.add(10, circle.cx);
    builder.add(20, circle.cy);
    builder.add(30, 0);
    builder.add(40, circle.radius);
  }
  
  private writeArc(builder: DXFBuilder, arc: DXFArc): void {
    builder.add(0, 'ARC');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, arc.layer);
    builder.add(100, 'AcDbCircle');
    builder.add(10, arc.cx);
    builder.add(20, arc.cy);
    builder.add(30, 0);
    builder.add(40, arc.radius);
    builder.add(100, 'AcDbArc');
    builder.add(50, arc.startAngle);
    builder.add(51, arc.endAngle);
  }
  
  private writeText(builder: DXFBuilder, text: DXFText): void {
    builder.add(0, 'TEXT');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, text.layer);
    builder.add(100, 'AcDbText');
    builder.add(10, text.x);
    builder.add(20, text.y);
    builder.add(30, 0);
    builder.add(40, text.height);
    builder.add(1, text.text);
    if (text.rotation) {
      builder.add(50, text.rotation);
    }
    if (text.horizontalJustification) {
      const justCode = { left: 0, center: 1, right: 2 }[text.horizontalJustification];
      builder.add(72, justCode);
      if (justCode !== 0) {
        builder.add(11, text.x);
        builder.add(21, text.y);
        builder.add(31, 0);
      }
    }
    builder.add(100, 'AcDbText');
  }
  
  private writeDimension(builder: DXFBuilder, dim: DXFDimension): void {
    builder.add(0, 'DIMENSION');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, dim.layer);
    builder.add(100, 'AcDbDimension');
    builder.add(2, 'STANDARD');
    builder.add(10, dim.textPosition[0]);
    builder.add(20, dim.textPosition[1]);
    builder.add(30, 0);
    builder.add(70, dim.dimensionType === 'linear' ? 0 : 1);
    builder.add(100, 'AcDbAlignedDimension');
    builder.add(13, dim.point1[0]);
    builder.add(23, dim.point1[1]);
    builder.add(33, 0);
    builder.add(14, dim.point2[0]);
    builder.add(24, dim.point2[1]);
    builder.add(34, 0);
    if (dim.rotation) {
      builder.add(50, dim.rotation);
      builder.add(100, 'AcDbRotatedDimension');
    }
  }
  
  private writeHatch(builder: DXFBuilder, hatch: DXFHatch): void {
    builder.add(0, 'HATCH');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, hatch.layer);
    builder.add(100, 'AcDbHatch');
    builder.add(10, 0);
    builder.add(20, 0);
    builder.add(30, 0);
    builder.add(210, 0);
    builder.add(220, 0);
    builder.add(230, 1);
    builder.add(2, hatch.patternName);
    builder.add(70, 0);  // Pattern fill
    builder.add(71, 0);  // Non-associative
    builder.add(91, 1);  // Number of boundary paths
    
    // Boundary path
    builder.add(92, 1);  // Polyline boundary
    builder.add(72, 1);  // Has bulge
    builder.add(73, 1);  // Closed
    builder.add(93, hatch.boundary.length);
    
    for (const [x, y] of hatch.boundary) {
      builder.add(10, x);
      builder.add(20, y);
      builder.add(42, 0);  // Bulge
    }
    
    builder.add(97, 0);  // Source boundary objects
    builder.add(75, 0);  // Hatch style
    builder.add(76, 1);  // Pattern type
    builder.add(52, hatch.patternAngle);
    builder.add(41, hatch.patternScale);
    builder.add(77, 0);  // Double flag
    builder.add(78, 1);  // Number of pattern def lines
    
    // Pattern definition line
    builder.add(53, hatch.patternAngle);
    builder.add(43, 0);
    builder.add(44, 0);
    builder.add(45, 0);
    builder.add(46, 0.1);
    builder.add(79, 0);
  }
  
  private writeInsert(builder: DXFBuilder, insert: DXFInsert): void {
    builder.add(0, 'INSERT');
    builder.add(5, builder.getHandle());
    builder.add(100, 'AcDbEntity');
    builder.add(8, insert.layer);
    builder.add(100, 'AcDbBlockReference');
    builder.add(2, insert.blockName);
    builder.add(10, insert.x);
    builder.add(20, insert.y);
    builder.add(30, 0);
    builder.add(41, insert.scaleX);
    builder.add(42, insert.scaleY);
    builder.add(43, 1);
    builder.add(50, insert.rotation);
  }
}

