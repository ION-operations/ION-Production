/**
 * Enhanced Resize Handle Component
 * 
 * Phase 3.2: Enhanced Resizable Panels
 * 
 * Features:
 * - Visual resize preview showing current size
 * - Snap points for common sizes
 * - Constraints enforcement
 * - Smooth animations
 */

import React, { useState, useRef, useEffect } from 'react'
import { PanelResizeHandle } from 'react-resizable-panels'
import { GripVertical, GripHorizontal } from 'lucide-react'

interface EnhancedResizeHandleProps {
  direction: 'horizontal' | 'vertical'
  snapPoints?: number[] // Percentage snap points (e.g., [25, 50, 75])
  onResize?: (size: number) => void
  showPreview?: boolean
  minSize?: number
  maxSize?: number
}

export const EnhancedResizeHandle: React.FC<EnhancedResizeHandleProps> = ({
  direction,
  snapPoints = [],
  onResize,
  showPreview = true,
  minSize,
  maxSize
}) => {
  const [isDragging, setIsDragging] = useState(false)
  const [currentSize, setCurrentSize] = useState<number | null>(null)
  const [snapIndicator, setSnapIndicator] = useState<number | null>(null)
  const handleRef = useRef<HTMLDivElement>(null)

  const handleMouseDown = () => {
    setIsDragging(true)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !handleRef.current) return

    // Calculate current size based on mouse position
    // This is a simplified calculation - actual size would come from PanelGroup
    const rect = handleRef.current.getBoundingClientRect()
    let size: number | null = null

    if (direction === 'horizontal') {
      // Horizontal resize (left/right panels)
      const totalWidth = window.innerWidth
      const leftWidth = rect.left
      size = (leftWidth / totalWidth) * 100
    } else {
      // Vertical resize (top/bottom panels)
      const totalHeight = window.innerHeight
      const topHeight = rect.top
      size = (topHeight / totalHeight) * 100
    }

    // Check snap points
    if (snapPoints.length > 0 && size !== null) {
      const closestSnap = snapPoints.reduce((prev, curr) => {
        return Math.abs(curr - size) < Math.abs(prev - size) ? curr : prev
      })
      
      if (Math.abs(closestSnap - size) < 3) { // 3% threshold
        setSnapIndicator(closestSnap)
        size = closestSnap
      } else {
        setSnapIndicator(null)
      }
    }

    // Enforce constraints
    if (size !== null) {
      if (minSize !== undefined && size < minSize) size = minSize
      if (maxSize !== undefined && size > maxSize) size = maxSize
    }

    setCurrentSize(size)
    if (onResize && size !== null) {
      onResize(size)
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setCurrentSize(null)
    setSnapIndicator(null)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging])

  const isHorizontal = direction === 'horizontal'
  const GripIcon = isHorizontal ? GripVertical : GripHorizontal

  return (
    <>
      <PanelResizeHandle
        ref={handleRef}
        onMouseDown={handleMouseDown}
        className={`relative group transition-all ${
          isHorizontal
            ? 'w-1 hover:w-2 cursor-col-resize'
            : 'h-1 hover:h-2 cursor-row-resize'
        } ${
          isDragging
            ? 'bg-blue-500'
            : 'bg-gray-700 hover:bg-gray-600'
        } transition-colors`}
      >
        <div
          className={`absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity ${
            isHorizontal ? 'flex-col' : 'flex-row'
          }`}
        >
          <GripIcon className={`text-gray-400 ${isHorizontal ? 'w-3 h-3' : 'w-3 h-3'}`} />
        </div>
      </PanelResizeHandle>

      {/* Resize Preview */}
      {showPreview && isDragging && currentSize !== null && (
        <div
          className={`fixed z-50 pointer-events-none ${
            isHorizontal
              ? 'left-1/2 top-4 -translate-x-1/2'
              : 'top-1/2 left-4 -translate-y-1/2'
          }`}
        >
          <div className="bg-gray-900 border border-gray-700 rounded px-3 py-1.5 shadow-lg">
            <div className="text-xs text-gray-300 font-mono">
              {currentSize.toFixed(1)}%
              {snapIndicator !== null && (
                <span className="ml-2 text-blue-400">→ {snapIndicator.toFixed(0)}%</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Snap Point Indicators */}
      {snapPoints.length > 0 && isDragging && snapIndicator !== null && (
        <div
          className={`fixed z-40 pointer-events-none bg-blue-500/20 border border-blue-500 ${
            isHorizontal
              ? `w-1 h-full left-[${snapIndicator}%]`
              : `h-1 w-full top-[${snapIndicator}%]`
          }`}
        />
      )}
    </>
  )
}

