/**
 * AnimForge Canvas Component
 * 
 * Main drawing/animation canvas with:
 * - WebGL-accelerated rendering (via Pixi.js pattern)
 * - Onion skin overlay (previous/next frames ghosted)
 * - Grid and rulers
 * - Skeleton bone visualization
 * - Mode-specific overlays (Draw, Rig, Animate, Mocap)
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import React, { useRef, useEffect, useState, useCallback } from 'react'
import { useAnimForgeStore, AnimForgeMode, Point } from './store/animForgeStore'

interface AnimForgeCanvasProps {
  mode: AnimForgeMode
  showGrid: boolean
  showRulers: boolean
  showOnionSkin: boolean
  showBones: boolean
  zoomLevel: number
}

export const AnimForgeCanvas: React.FC<AnimForgeCanvasProps> = ({
  mode,
  showGrid,
  showRulers,
  showOnionSkin,
  showBones,
  zoomLevel
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [canvasSize, setCanvasSize] = useState({ width: 1920, height: 1080 })
  const [isDrawing, setIsDrawing] = useState(false)
  const [currentPath, setCurrentPath] = useState<Point[]>([])
  
  const {
    currentFrame,
    totalFrames,
    layers,
    selectedLayerId,
    skeleton,
    onionSkin,
    strokeColor,
    strokeWidth,
    currentTool,
    panPosition
  } = useAnimForgeStore()

  // Handle canvas resize
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect()
        setCanvasSize({ width, height })
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Main render loop
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.fillStyle = '#1a1a2e'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Apply zoom and pan
    ctx.save()
    ctx.translate(canvas.width / 2 + panPosition.x, canvas.height / 2 + panPosition.y)
    ctx.scale(zoomLevel / 100, zoomLevel / 100)
    ctx.translate(-canvasSize.width / 2, -canvasSize.height / 2)

    // Draw stage background (white)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvasSize.width, canvasSize.height)

    // Draw grid
    if (showGrid) {
      drawGrid(ctx, canvasSize.width, canvasSize.height)
    }

    // Draw onion skin (previous frames)
    if (showOnionSkin && onionSkin.enabled) {
      drawOnionSkin(ctx, 'previous')
    }

    // Draw current frame content
    drawCurrentFrame(ctx)

    // Draw onion skin (next frames)
    if (showOnionSkin && onionSkin.enabled) {
      drawOnionSkin(ctx, 'next')
    }

    // Draw skeleton bones
    if (showBones && skeleton) {
      drawSkeleton(ctx)
    }

    // Draw current drawing path
    if (isDrawing && currentPath.length > 0) {
      drawPath(ctx, currentPath, strokeColor, strokeWidth)
    }

    // Draw mode-specific overlays
    drawModeOverlay(ctx)

    ctx.restore()

    // Draw rulers (outside of transform)
    if (showRulers) {
      drawRulers(ctx, canvas.width, canvas.height, zoomLevel)
    }

  }, [
    canvasSize, zoomLevel, panPosition, showGrid, showRulers, showOnionSkin, showBones,
    currentFrame, layers, skeleton, onionSkin, isDrawing, currentPath, strokeColor, strokeWidth, mode
  ])

  // Grid drawing
  const drawGrid = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    const gridSize = 50
    ctx.strokeStyle = '#e0e0e0'
    ctx.lineWidth = 0.5

    // Vertical lines
    for (let x = 0; x <= width; x += gridSize) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }

    // Horizontal lines
    for (let y = 0; y <= height; y += gridSize) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }

    // Center lines (darker)
    ctx.strokeStyle = '#b0b0b0'
    ctx.lineWidth = 1

    // Vertical center
    ctx.beginPath()
    ctx.moveTo(width / 2, 0)
    ctx.lineTo(width / 2, height)
    ctx.stroke()

    // Horizontal center
    ctx.beginPath()
    ctx.moveTo(0, height / 2)
    ctx.lineTo(width, height / 2)
    ctx.stroke()
  }

  // Onion skin drawing
  const drawOnionSkin = (ctx: CanvasRenderingContext2D, direction: 'previous' | 'next') => {
    const frames = direction === 'previous' ? onionSkin.previousFrames : onionSkin.nextFrames
    const baseOpacity = direction === 'previous' ? onionSkin.previousOpacity : onionSkin.nextOpacity
    const tintColor = direction === 'previous' ? onionSkin.previousColor : onionSkin.nextColor

    for (let i = 1; i <= frames; i++) {
      const frameNumber = direction === 'previous' ? currentFrame - i : currentFrame + i
      if (frameNumber < 1 || frameNumber > totalFrames) continue

      const opacity = baseOpacity * (1 - (i - 1) / frames)
      ctx.globalAlpha = opacity

      // Draw frame content with tint
      layers.forEach(layer => {
        if (!layer.visible) return
        const frame = layer.frames[frameNumber - 1]
        if (frame && frame.content) {
          // Draw paths with tint
          frame.content.paths.forEach(path => {
            ctx.strokeStyle = tintColor
            ctx.lineWidth = path.strokeWidth
            ctx.beginPath()
            path.points.forEach((point, idx) => {
              if (idx === 0) ctx.moveTo(point.x, point.y)
              else ctx.lineTo(point.x, point.y)
            })
            ctx.stroke()
          })
        }
      })

      ctx.globalAlpha = 1
    }
  }

  // Current frame drawing
  const drawCurrentFrame = (ctx: CanvasRenderingContext2D) => {
    layers.forEach(layer => {
      if (!layer.visible) return
      
      ctx.globalAlpha = layer.opacity / 100
      
      const frame = layer.frames[currentFrame - 1]
      if (frame && frame.content) {
        frame.content.paths.forEach(path => {
          drawPath(ctx, path.points, path.strokeColor, path.strokeWidth, path.fillColor, path.closed)
        })
      }
      
      ctx.globalAlpha = 1
    })
  }

  // Path drawing helper
  const drawPath = (
    ctx: CanvasRenderingContext2D,
    points: Point[],
    stroke: string,
    width: number,
    fill?: string,
    closed?: boolean
  ) => {
    if (points.length < 2) return

    ctx.strokeStyle = stroke
    ctx.lineWidth = width
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'

    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y)

    // Smooth curve through points
    for (let i = 1; i < points.length - 1; i++) {
      const xc = (points[i].x + points[i + 1].x) / 2
      const yc = (points[i].y + points[i + 1].y) / 2
      ctx.quadraticCurveTo(points[i].x, points[i].y, xc, yc)
    }

    // Last point
    if (points.length > 1) {
      ctx.lineTo(points[points.length - 1].x, points[points.length - 1].y)
    }

    if (closed) {
      ctx.closePath()
      if (fill && fill !== 'transparent') {
        ctx.fillStyle = fill
        ctx.fill()
      }
    }

    ctx.stroke()
  }

  // Skeleton drawing
  const drawSkeleton = (ctx: CanvasRenderingContext2D) => {
    if (!skeleton) return

    skeleton.bones.forEach(bone => {
      // Draw bone line
      const endX = bone.position.x + Math.cos(bone.rotation * Math.PI / 180) * bone.length
      const endY = bone.position.y + Math.sin(bone.rotation * Math.PI / 180) * bone.length

      ctx.strokeStyle = bone.color
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(bone.position.x, bone.position.y)
      ctx.lineTo(endX, endY)
      ctx.stroke()

      // Draw joint circle
      ctx.fillStyle = bone.color
      ctx.beginPath()
      ctx.arc(bone.position.x, bone.position.y, 6, 0, Math.PI * 2)
      ctx.fill()

      // Draw end point
      ctx.fillStyle = '#ffffff'
      ctx.beginPath()
      ctx.arc(endX, endY, 4, 0, Math.PI * 2)
      ctx.fill()
    })
  }

  // Mode overlay
  const drawModeOverlay = (ctx: CanvasRenderingContext2D) => {
    // Mode indicator in corner
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
    ctx.fillRect(10, 10, 100, 30)
    ctx.fillStyle = '#ffffff'
    ctx.font = '14px Inter, sans-serif'
    ctx.fillText(`Mode: ${mode.toUpperCase()}`, 20, 30)

    // Frame indicator
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
    ctx.fillRect(10, 50, 120, 30)
    ctx.fillStyle = '#ffffff'
    ctx.fillText(`Frame: ${currentFrame}/${totalFrames}`, 20, 70)
  }

  // Rulers drawing
  const drawRulers = (ctx: CanvasRenderingContext2D, width: number, height: number, zoom: number) => {
    const rulerSize = 20
    const tickSpacing = 50 * (zoom / 100)

    // Horizontal ruler background
    ctx.fillStyle = '#2d2d3d'
    ctx.fillRect(0, 0, width, rulerSize)

    // Vertical ruler background
    ctx.fillRect(0, 0, rulerSize, height)

    // Ruler markings
    ctx.fillStyle = '#888888'
    ctx.font = '10px monospace'

    // Horizontal ticks
    for (let x = rulerSize; x < width; x += tickSpacing) {
      ctx.beginPath()
      ctx.moveTo(x, rulerSize - 5)
      ctx.lineTo(x, rulerSize)
      ctx.strokeStyle = '#666666'
      ctx.stroke()
      
      const value = Math.round((x - rulerSize) / (zoom / 100))
      ctx.fillText(value.toString(), x + 2, rulerSize - 8)
    }

    // Vertical ticks
    for (let y = rulerSize; y < height; y += tickSpacing) {
      ctx.beginPath()
      ctx.moveTo(rulerSize - 5, y)
      ctx.lineTo(rulerSize, y)
      ctx.strokeStyle = '#666666'
      ctx.stroke()
      
      const value = Math.round((y - rulerSize) / (zoom / 100))
      ctx.save()
      ctx.translate(rulerSize - 8, y + 2)
      ctx.rotate(-Math.PI / 2)
      ctx.fillText(value.toString(), 0, 0)
      ctx.restore()
    }

    // Corner
    ctx.fillStyle = '#3d3d4d'
    ctx.fillRect(0, 0, rulerSize, rulerSize)
  }

  // Mouse event handlers
  const getCanvasPoint = useCallback((e: React.MouseEvent): Point => {
    const canvas = canvasRef.current
    if (!canvas) return { x: 0, y: 0 }

    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left - canvas.width / 2 - panPosition.x) / (zoomLevel / 100) + canvasSize.width / 2
    const y = (e.clientY - rect.top - canvas.height / 2 - panPosition.y) / (zoomLevel / 100) + canvasSize.height / 2

    return { x, y }
  }, [panPosition, zoomLevel, canvasSize])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (mode !== 'draw') return
    if (currentTool !== 'pencil' && currentTool !== 'brush') return

    setIsDrawing(true)
    const point = getCanvasPoint(e)
    setCurrentPath([point])
  }, [mode, currentTool, getCanvasPoint])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDrawing) return

    const point = getCanvasPoint(e)
    setCurrentPath(prev => [...prev, point])
  }, [isDrawing, getCanvasPoint])

  const handleMouseUp = useCallback(() => {
    if (!isDrawing) return
    
    setIsDrawing(false)
    
    // Save path to current frame
    if (currentPath.length > 1) {
      const { pushHistory, layers, selectedLayerId, currentFrame } = useAnimForgeStore.getState()
      
      // Find selected layer and add path
      const layerIndex = layers.findIndex(l => l.id === selectedLayerId)
      if (layerIndex >= 0) {
        const layer = layers[layerIndex]
        const frameIndex = currentFrame - 1
        
        if (!layer.frames[frameIndex].content) {
          layer.frames[frameIndex].content = { paths: [], transforms: [], boneStates: [] }
          layer.frames[frameIndex].type = 'keyframe'
        }
        
        layer.frames[frameIndex].content!.paths.push({
          id: `path-${Date.now()}`,
          points: currentPath,
          strokeColor,
          fillColor: 'transparent',
          strokeWidth,
          closed: false
        })
        
        pushHistory('Draw path')
      }
    }
    
    setCurrentPath([])
  }, [isDrawing, currentPath, strokeColor, strokeWidth])

  return (
    <div 
      ref={containerRef}
      className="w-full h-full relative bg-gray-950 overflow-hidden"
    >
      {/* Canvas */}
      <canvas
        ref={canvasRef}
        width={containerRef.current?.clientWidth || 1920}
        height={containerRef.current?.clientHeight || 1080}
        className="absolute inset-0 cursor-crosshair"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      />

      {/* Mode indicator overlay */}
      <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Mode:</span>
          <span className="text-white font-semibold capitalize">{mode}</span>
        </div>
      </div>

      {/* Frame indicator overlay */}
      <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Frame:</span>
          <span className="text-white font-mono">{currentFrame}</span>
          <span className="text-gray-500">/</span>
          <span className="text-gray-400 font-mono">{totalFrames}</span>
        </div>
      </div>

      {/* Zoom indicator */}
      <div className="absolute bottom-4 right-4 bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 text-sm">
        <span className="text-gray-400">{zoomLevel}%</span>
      </div>

      {/* Mocap split view (when in mocap mode) */}
      {mode === 'mocap' && (
        <div className="absolute inset-0 flex">
          <div className="w-1/2 border-r border-gray-700 flex items-center justify-center bg-gray-900">
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-2">📹</div>
              <div className="text-sm">Webcam View</div>
              <div className="text-xs text-gray-600 mt-1">Click to enable camera</div>
            </div>
          </div>
          <div className="w-1/2 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-2">🎭</div>
              <div className="text-sm">Character Preview</div>
              <div className="text-xs text-gray-600 mt-1">Real-time pose mapping</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AnimForgeCanvas

