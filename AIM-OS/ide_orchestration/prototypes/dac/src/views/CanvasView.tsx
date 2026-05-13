/**
 * Canvas View - Main View Wrapper for Canvas Editor
 * 
 * Wraps CanvasEditor component for use as a main view in DAC v2 IDE.
 */

import React from 'react'
import { CanvasEditor } from '../components/CanvasEditor'
import { useCanvasStore } from '../store/canvasStore'
import { FileText } from 'lucide-react'

export interface CanvasViewProps {
  canvasId?: string
}

export const CanvasView: React.FC<CanvasViewProps> = ({ canvasId }) => {
  const activeCanvas = useCanvasStore((state) => state.activeCanvas)
  const canvases = useCanvasStore((state) => state.canvases)
  const setActiveCanvas = useCanvasStore((state) => state.setActiveCanvas)
  
  const targetCanvasId = canvasId || activeCanvas
  
  // If no canvas, show empty state
  if (!targetCanvasId || !canvases[targetCanvasId]) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center text-gray-400">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg mb-2">No Canvas Selected</p>
          <p className="text-sm">Create a canvas from chat or start a new one</p>
        </div>
      </div>
    )
  }
  
  return <CanvasEditor canvasId={targetCanvasId} />
}

export default CanvasView

