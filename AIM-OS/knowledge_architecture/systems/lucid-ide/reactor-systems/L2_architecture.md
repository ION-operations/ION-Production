---
id: "lucid-ide-reactor-systems-L2-architecture"
system: "lucid-ide-reactor-systems"
component: null
level: "L2"
type: "architecture"
title: "Lucid IDE Reactor Systems - Architecture"
description: "2,000-word architecture document for Lucid IDE Reactor Systems"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "reactor", "visualization", "architecture"]
dependencies: ["lucid-ide-reactor-systems-L1-overview"]
related_docs: ["lucid-ide-reactor-systems-L3-detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Reactor Systems – L2 Architecture (≈2000 words)

## System Overview

Lucid IDE Reactor Systems implement dual visualization engines providing 2D canvas-based and 3D WebGL-based reactor visualizations for system architecture, node relationships, and activity monitoring. Both systems render interactive visualizations targeting 60fps performance with <16ms frame budget.

**Core Architectural Principles:**
1. **Dual Rendering:** Independent 2D and 3D rendering systems
2. **Performance First:** 60fps target with <16ms frame budget
3. **Modular Design:** Separate visual engines for 2D and 3D
4. **Particle Systems:** Dynamic particle effects for activity visualization
5. **Spatial Algorithms:** Advanced spatial positioning for 3D layouts

## 2D Reactor Architecture

### Component Structure (`components/lucid-reactor-core.tsx`)

**Purpose:** 2D canvas-based reactor visualization with particle systems

**Architecture:**
- Canvas rendering with 2D context
- Particle system for activity effects
- Node visualization with connections
- Activity glow effects
- Processing pulse effects

**Key Features:**
- High-DPI canvas support
- Gradient connections between nodes
- Activity-based visual feedback
- Particle systems for data flow
- Real-time updates

**Rendering Pipeline:**
```
Component Mount → Canvas Setup → 
Visual Engine Initialization → 
Animation Loop Start → 
Frame Update → Particle Update → 
Node Update → Canvas Draw → 
RequestAnimationFrame → Loop
```

**Performance Optimization:**
- High-DPI scaling
- Gradient caching
- Particle culling
- Efficient canvas operations

### Visual Engine (`lib/lucid-reactor-visual-engine.ts`)

**Purpose:** 2D visual engine managing canvas rendering, particles, and node layout

**Architecture:**
- Node management
- Particle system
- Connection rendering
- Activity visualization
- Metrics tracking

**Key Operations:**
- `getNodes()` - Retrieve current nodes
- `getParticles()` - Retrieve current particles
- `getMetrics()` - Get performance metrics
- Node update operations
- Particle update operations

**Performance Characteristics:**
- Target: 60fps
- Frame budget: <16ms
- Particle limit: <10,000 particles
- Node limit: <1,000 nodes

## 3D Reactor Architecture

### Component Structure (`components/enhanced-lucid-reactor-core.tsx`)

**Purpose:** 3D WebGL-based reactor visualization with Three.js

**Architecture:**
- Three.js scene setup
- WebGL rendering
- Camera controls (OrbitControls)
- Spatial positioning
- Node system integration

**Key Features:**
- 3D spatial visualization
- Interactive camera controls
- Node selection and interaction
- Metrics overlay
- View modes (overview, focused, detailed)

**Rendering Pipeline:**
```
Component Mount → Three.js Setup → 
Scene Creation → Camera Setup → 
Node System Initialization → 
Spatial Positioning → 
Animation Loop → 
Scene Update → Render → 
RequestAnimationFrame → Loop
```

**Performance Optimization:**
- Frustum culling
- Level of detail (LOD)
- Instanced rendering
- GPU optimization

### Node System (`lib/lucid-reactor-3d/node-system.ts`)

**Purpose:** Node system managing 3D nodes, connections, and metrics

**Architecture:**
- Node data structure
- Connection management
- Metrics calculation
- State management

**Key Operations:**
- `addNode()` - Add node to system
- `removeNode()` - Remove node
- `getNodes()` - Retrieve all nodes
- `getMetrics()` - Calculate metrics
- `updateNode()` - Update node properties

**Node Properties:**
- Position (x, y, z)
- Color
- Size
- Activity level
- Connections

### Spatial Positioning Engine (`lib/lucid-reactor-3d/spatial-positioning.ts`)

**Purpose:** Spatial positioning engine for 3D node layout and camera controls

**Architecture:**
- Force-directed layout
- Spherical positioning
- Collision detection
- Animation smoothing

**Key Operations:**
- `calculateLayout()` - Calculate node positions
- `updatePositions()` - Update node positions
- `handleCollisions()` - Collision detection
- `smoothAnimation()` - Animation smoothing

**Layout Algorithms:**
- Force-directed graph layout
- Spherical layout
- Hierarchical layout
- Custom layout algorithms

### Enhanced Visual Engine (`lib/lucid-reactor-3d/enhanced-visual-engine.ts`)

**Purpose:** Enhanced visual engine managing WebGL rendering and Three.js scene

**Architecture:**
- Three.js scene management
- WebGL rendering
- Material management
- Lighting setup
- Camera controls

**Key Operations:**
- `render()` - Render scene
- `update()` - Update scene
- `setCanvasSize()` - Resize canvas
- `dispose()` - Cleanup resources

**Rendering Optimization:**
- Frustum culling
- LOD system
- Instanced rendering
- Texture optimization

## Particle System Architecture

### Particle Data Structure

**Particle Properties:**
- Position (x, y, z)
- Velocity (vx, vy, vz)
- Color
- Size
- Lifetime
- Age

### Particle Update Loop

**Update Process:**
```
Particle Creation → 
Physics Update → 
Velocity Update → 
Position Update → 
Lifetime Check → 
Particle Removal
```

**Performance Optimization:**
- Particle pooling
- Batch updates
- Culling off-screen particles
- Limit particle count

## Performance Architecture

### Frame Rate Management

**Target:** 60fps (16.67ms per frame)

**Frame Budget Allocation:**
- Rendering: <10ms
- Physics: <3ms
- State updates: <2ms
- Other: <1ms

### Optimization Strategies

**Rendering Optimization:**
- RequestAnimationFrame optimization
- Canvas/WebGL batching
- Particle culling
- Node LOD system

**Memory Optimization:**
- Object pooling
- Texture reuse
- Geometry reuse
- Dispose unused resources

**GPU Optimization:**
- Instanced rendering
- Texture atlasing
- Shader optimization
- Buffer management

## Interaction Architecture

### User Interactions

**2D Reactor:**
- Node selection
- Pan and zoom
- Particle interaction
- Activity visualization

**3D Reactor:**
- Camera controls (orbit, pan, zoom)
- Node selection
- Node interaction
- View mode switching

### Event Handling

**Mouse Events:**
- Click detection
- Drag handling
- Hover effects
- Selection

**Keyboard Events:**
- Camera controls
- View switching
- Navigation shortcuts

## State Management Architecture

### Component State

**2D Reactor State:**
- Playing/paused state
- Selected node
- System status
- Panel visibility

**3D Reactor State:**
- Camera position
- Selected node
- View mode
- Metrics visibility

### Data Flow

**Props → State:**
- Reactor data via props
- Configuration via props
- Updates via props

**State → Rendering:**
- State changes trigger re-render
- Visual updates reflect state
- Interaction updates state

## Integration Architecture

### Frontend Integration

**React Props:**
- Reactor data
- Configuration
- Event handlers
- State callbacks

**Parent Component:**
- Provides reactor data
- Handles interactions
- Manages state
- Coordinates updates

### Visual Engine Integration

**2D Engine:**
- Canvas element
- Rendering context
- Animation loop
- Event handlers

**3D Engine:**
- Three.js scene
- WebGL context
- Camera controls
- Renderer

## References

- System map: `systems/lucid-ide/reactor-systems/system.map.lucid.json5`
- System index: `systems/lucid-ide/reactor-systems/system.index.lucid.json5`
- L1 Overview: `systems/lucid-ide/reactor-systems/L1_overview.md`
- L3 Detailed: `systems/lucid-ide/reactor-systems/L3_detailed.md`

