/**
 * Diagram Renderer
 * Mermaid and other diagram rendering
 */

import React, { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

interface DiagramRendererProps {
  diagram: string
  type?: 'mermaid' | 'graphviz' | 'plantuml'
}

export const DiagramRenderer: React.FC<DiagramRendererProps> = ({
  diagram,
  type = 'mermaid',
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [rendered, setRendered] = useState(false)

  useEffect(() => {
    if (!containerRef.current || rendered || type !== 'mermaid') return

    // Initialize Mermaid
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#3b82f6',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#1e40af',
        lineColor: '#60a5fa',
        secondaryColor: '#1e293b',
        tertiaryColor: '#0f172a',
      },
    })

    // Generate unique ID
    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`

    // Render diagram
    mermaid
      .render(id, diagram)
      .then((result) => {
        if (containerRef.current) {
          containerRef.current.innerHTML = result.svg
          setRendered(true)
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to render diagram')
      })
  }, [diagram, type, rendered])

  if (type !== 'mermaid') {
    return (
      <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
        <div className="text-sm text-gray-400 mb-2">
          {type.toUpperCase()} diagram (not yet supported)
        </div>
        <pre className="text-xs text-gray-500 font-mono overflow-x-auto">
          {diagram}
        </pre>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-700/50 rounded-lg">
        <div className="text-sm text-red-300 mb-2">Diagram Error:</div>
        <div className="text-xs text-red-400">{error}</div>
        <pre className="mt-2 text-xs text-gray-500 font-mono overflow-x-auto">
          {diagram}
        </pre>
      </div>
    )
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg border border-gray-700 overflow-x-auto">
      <div ref={containerRef} className="flex justify-center" />
    </div>
  )
}

