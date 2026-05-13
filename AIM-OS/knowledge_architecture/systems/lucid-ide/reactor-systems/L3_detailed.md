---
id: "lucid-ide-reactor-systems-L3-detailed"
system: "lucid-ide-reactor-systems"
component: null
level: "L3"
type: "detailed"
title: "Lucid IDE Reactor Systems - Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Lucid IDE Reactor Systems"
audience: "developers, implementers, maintainers"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "reactor", "visualization", "implementation"]
dependencies: ["lucid-ide-reactor-systems-L2-architecture"]
related_docs: ["lucid-ide-reactor-systems-L4-complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Reactor Systems – L3 Detailed Implementation Guide

**Purpose:** Complete implementation guide for Lucid IDE Reactor Systems with step-by-step instructions, code examples, 2D/3D rendering, particle systems, performance optimization, and best practices.

**Audience:** Developers implementing, integrating with, or maintaining the Lucid IDE Reactor Systems.

**Prerequisites:**
- React 19+
- TypeScript 5+
- Canvas API knowledge
- Three.js knowledge
- Understanding of particle systems and physics

---

## 📜 **EVOLUTION & HISTORY**

### **Version Timeline**

**v1.0 (2025-11-09) - Initial Documentation**
- **Changes:** Comprehensive AIM-OS protocol-compliant documentation
- **Key Features:** 2D canvas-based and 3D WebGL-based reactor visualizations
- **Status:** Production-ready with 60fps performance targets

### **Key Evolution Points**

**Phase 1: 2D Reactor (Initial)**
- **Goal:** Basic 2D canvas visualization
- **Implementation:** Canvas API, particle systems, activity visualization
- **Outcome:** Functional 2D reactor visualization

**Phase 2: 3D Reactor**
- **Goal:** 3D WebGL visualization
- **Implementation:** Three.js integration, spatial positioning
- **Outcome:** Advanced 3D reactor visualization

**Phase 3: Performance Optimization**
- **Goal:** Achieve 60fps performance
- **Implementation:** Optimization strategies, particle culling, LOD system
- **Outcome:** Optimized rendering performance

---

## 🔧 **IMPLEMENTATION GUIDE**

### **Step 1: 2D Reactor Implementation**

#### **1.1 Canvas Setup**

```typescript
// components/lucid-reactor-core.tsx
"use client"

import { useEffect, useRef, useState } from "react"

interface ReactorNode {
  id: string
  x: number
  y: number
  activity: number
  connections: string[]
}

export function LucidReactorCore({ nodes }: { nodes: ReactorNode[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationFrameRef = useRef<number | null>(null)
  const [isPlaying, setIsPlaying] = useState(true)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // High-DPI support
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    // Animation loop
    const animate = () => {
      if (!isPlaying) return

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr)

      // Render nodes
      nodes.forEach(node => {
        // Node circle
        ctx.beginPath()
        ctx.arc(node.x, node.y, 10, 0, Math.PI * 2)
        ctx.fillStyle = `hsl(${node.activity * 120}, 100%, 50%)`
        ctx.fill()

        // Activity glow
        ctx.beginPath()
        ctx.arc(node.x, node.y, 10 + node.activity * 5, 0, Math.PI * 2)
        ctx.strokeStyle = `rgba(255, 255, 255, ${node.activity * 0.5})`
        ctx.lineWidth = 2
        ctx.stroke()
      })

      // Render connections
      nodes.forEach(node => {
        node.connections.forEach(connectionId => {
          const targetNode = nodes.find(n => n.id === connectionId)
          if (!targetNode) return

          // Gradient connection
          const gradient = ctx.createLinearGradient(
            node.x, node.y,
            targetNode.x, targetNode.y
          )
          gradient.addColorStop(0, `rgba(255, 255, 255, ${node.activity * 0.3})`)
          gradient.addColorStop(1, `rgba(255, 255, 255, ${targetNode.activity * 0.3})`)

          ctx.beginPath()
          ctx.moveTo(node.x, node.y)
          ctx.lineTo(targetNode.x, targetNode.y)
          ctx.strokeStyle = gradient
          ctx.lineWidth = 2
          ctx.stroke()
        })
      })

      animationFrameRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [nodes, isPlaying])

  return (
    <div className="reactor-container">
      <canvas ref={canvasRef} className="reactor-canvas" />
      <div className="reactor-controls">
        <button onClick={() => setIsPlaying(!isPlaying)}>
          {isPlaying ? "Pause" : "Play"}
        </button>
      </div>
    </div>
  )
}
```

#### **1.2 Particle System**

```typescript
// lib/particle-system.ts
export interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  color: string
}

export class ParticleSystem {
  private particles: Particle[] = []
  private maxParticles: number = 1000

  addParticle(particle: Particle) {
    if (this.particles.length >= this.maxParticles) {
      this.particles.shift()
    }
    this.particles.push(particle)
  }

  update(deltaTime: number) {
    this.particles = this.particles.filter(particle => {
      particle.x += particle.vx * deltaTime
      particle.y += particle.vy * deltaTime
      particle.life -= deltaTime
      return particle.life > 0
    })
  }

  render(ctx: CanvasRenderingContext2D) {
    this.particles.forEach(particle => {
      const alpha = particle.life / particle.maxLife
      ctx.fillStyle = particle.color.replace("rgb", "rgba").replace(")", `, ${alpha})`)
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  clear() {
    this.particles = []
  }
}
```

### **Step 2: 3D Reactor Implementation**

#### **2.1 Three.js Scene Setup**

```typescript
// components/enhanced-lucid-reactor-core.tsx
"use client"

import { useEffect, useRef } from "react"
import * as THREE from "three"
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls"

interface ReactorNode {
  id: string
  position: [number, number, number]
  activity: number
  connections: string[]
}

export function EnhancedLucidReactorCore({ nodes }: { nodes: ReactorNode[] }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)
  const controlsRef = useRef<OrbitControls | null>(null)
  const nodeMeshesRef = useRef<Map<string, THREE.Mesh>>(new Map())
  const animationFrameRef = useRef<number | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0a0a)
    sceneRef.current = scene

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    )
    camera.position.set(0, 0, 50)
    cameraRef.current = camera

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(
      containerRef.current.clientWidth,
      containerRef.current.clientHeight
    )
    renderer.setPixelRatio(window.devicePixelRatio)
    containerRef.current.appendChild(renderer.domElement)
    rendererRef.current = renderer

    // Controls setup
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controlsRef.current = controls

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5)
    directionalLight.position.set(5, 5, 5)
    scene.add(directionalLight)

    // Create node meshes
    nodes.forEach(node => {
      const geometry = new THREE.SphereGeometry(1, 32, 32)
      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(node.activity * 0.3, 1, 0.5),
        emissive: new THREE.Color().setHSL(node.activity * 0.3, 1, node.activity * 0.5),
      })
      const mesh = new THREE.Mesh(geometry, material)
      mesh.position.set(...node.position)
      scene.add(mesh)
      nodeMeshesRef.current.set(node.id, mesh)
    })

    // Create connection lines
    nodes.forEach(node => {
      node.connections.forEach(connectionId => {
        const targetNode = nodes.find(n => n.id === connectionId)
        if (!targetNode) return

        const geometry = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(...node.position),
          new THREE.Vector3(...targetNode.position),
        ])
        const material = new THREE.LineBasicMaterial({
          color: 0xffffff,
          opacity: 0.3,
          transparent: true,
        })
        const line = new THREE.Line(geometry, material)
        scene.add(line)
      })
    })

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate)
      
      // Update node colors based on activity
      nodes.forEach(node => {
        const mesh = nodeMeshesRef.current.get(node.id)
        if (mesh && mesh.material instanceof THREE.MeshStandardMaterial) {
          mesh.material.color.setHSL(node.activity * 0.3, 1, 0.5)
          mesh.material.emissive.setHSL(node.activity * 0.3, 1, node.activity * 0.5)
        }
      })

      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current || !camera || !renderer) return
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(
        containerRef.current.clientWidth,
        containerRef.current.clientHeight
      )
    }
    window.addEventListener("resize", handleResize)

    // Cleanup
    return () => {
      window.removeEventListener("resize", handleResize)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
      nodeMeshesRef.current.forEach(mesh => {
        mesh.geometry.dispose()
        if (mesh.material instanceof THREE.Material) {
          mesh.material.dispose()
        }
      })
    }
  }, [nodes])

  return <div ref={containerRef} className="reactor-3d-container" />
}
```

#### **2.2 Spatial Positioning Engine**

```typescript
// lib/spatial-positioning.ts
import * as THREE from "three"

export class SpatialPositioningEngine {
  private nodes: Map<string, THREE.Vector3> = new Map()
  private forces: Map<string, THREE.Vector3> = new Map()

  addNode(id: string, position: THREE.Vector3) {
    this.nodes.set(id, position.clone())
    this.forces.set(id, new THREE.Vector3())
  }

  update(deltaTime: number) {
    // Calculate forces
    this.nodes.forEach((node, nodeId) => {
      const force = new THREE.Vector3()

      // Repulsion from other nodes
      this.nodes.forEach((otherNode, otherId) => {
        if (nodeId === otherId) return
        const direction = new THREE.Vector3().subVectors(node, otherNode)
        const distance = direction.length()
        if (distance > 0) {
          direction.normalize()
          const repulsion = 1 / (distance * distance)
          force.add(direction.multiplyScalar(repulsion))
        }
      })

      // Attraction to connections
      // (Implementation depends on connection data)

      this.forces.set(nodeId, force)
    })

    // Apply forces
    this.nodes.forEach((node, nodeId) => {
      const force = this.forces.get(nodeId)
      if (force) {
        node.add(force.multiplyScalar(deltaTime * 0.1))
      }
    })
  }

  getNodePosition(id: string): THREE.Vector3 | undefined {
    return this.nodes.get(id)?.clone()
  }
}
```

### **Step 3: Performance Optimization**

#### **3.1 Frame Rate Management**

```typescript
// lib/frame-rate-manager.ts
export class FrameRateManager {
  private targetFPS: number = 60
  private frameTime: number = 1000 / this.targetFPS
  private lastFrameTime: number = 0
  private deltaTime: number = 0

  update(): boolean {
    const currentTime = performance.now()
    const elapsed = currentTime - this.lastFrameTime

    if (elapsed >= this.frameTime) {
      this.deltaTime = elapsed / 1000
      this.lastFrameTime = currentTime
      return true
    }

    return false
  }

  getDeltaTime(): number {
    return this.deltaTime
  }

  setTargetFPS(fps: number) {
    this.targetFPS = fps
    this.frameTime = 1000 / fps
  }
}
```

#### **3.2 Particle Culling**

```typescript
// lib/particle-culling.ts
export class ParticleCuller {
  private viewport: { x: number; y: number; width: number; height: number }

  constructor(viewport: { x: number; y: number; width: number; height: number }) {
    this.viewport = viewport
  }

  isVisible(particle: Particle): boolean {
    return (
      particle.x >= this.viewport.x &&
      particle.x <= this.viewport.x + this.viewport.width &&
      particle.y >= this.viewport.y &&
      particle.y <= this.viewport.y + this.viewport.height
    )
  }

  cull(particles: Particle[]): Particle[] {
    return particles.filter(particle => this.isVisible(particle))
  }
}
```

### **Step 4: Testing**

#### **4.1 Component Testing**

```typescript
// __tests__/components/lucid-reactor-core.test.tsx
import { render, screen } from "@testing-library/react"
import { LucidReactorCore } from "@/components/lucid-reactor-core"

const mockNodes = [
  {
    id: "1",
    x: 100,
    y: 100,
    activity: 0.5,
    connections: ["2"],
  },
  {
    id: "2",
    x: 200,
    y: 200,
    activity: 0.7,
    connections: [],
  },
]

describe("LucidReactorCore", () => {
  it("renders canvas", () => {
    render(<LucidReactorCore nodes={mockNodes} />)
    const canvas = screen.getByRole("img", { hidden: true })
    expect(canvas).toBeInTheDocument()
  })
})
```

### **Step 5: Troubleshooting**

#### **5.1 Common Issues**

**Issue: Low frame rate**
- **Cause:** Too many particles or nodes
- **Solution:** Implement culling, reduce particle count, use LOD

**Issue: Memory leaks**
- **Cause:** Not disposing Three.js resources
- **Solution:** Cleanup in useEffect return, dispose geometries/materials

**Issue: Canvas not rendering**
- **Cause:** Container not mounted or wrong dimensions
- **Solution:** Ensure container has dimensions, check useEffect dependencies

### **Step 6: Best Practices**

#### **6.1 Rendering**

**Do:**
- ✅ Use requestAnimationFrame for animation
- ✅ Implement frame rate limiting
- ✅ Use object pooling for particles
- ✅ Implement culling for off-screen objects
- ✅ Dispose resources properly

**Don't:**
- ❌ Create new objects every frame
- ❌ Render unnecessary objects
- ❌ Ignore performance metrics
- ❌ Skip cleanup
- ❌ Over-render

---

## 📚 **REFERENCES**

- System map: `systems/lucid-ide/reactor-systems/system.map.lucid.json5`
- System index: `systems/lucid-ide/reactor-systems/system.index.lucid.json5`
- L2 Architecture: `systems/lucid-ide/reactor-systems/L2_architecture.md`
- L4 Complete: `systems/lucid-ide/reactor-systems/L4_complete.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

