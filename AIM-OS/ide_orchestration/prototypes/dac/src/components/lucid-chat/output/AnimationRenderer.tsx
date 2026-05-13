/**
 * Animation Renderer
 * CSS, Lottie, and GSAP animations
 */

import React, { useEffect, useRef } from 'react'
import Lottie from 'lottie-react'

interface AnimationRendererProps {
  animation: any
  type: 'css' | 'lottie' | 'gsap'
}

export const AnimationRenderer: React.FC<AnimationRendererProps> = ({
  animation,
  type,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (type === 'gsap' && containerRef.current) {
      // GSAP animations would be initialized here
      // For now, we'll just render the container
    }
  }, [type, animation])

  if (type === 'lottie') {
    return (
      <div className="p-4 bg-gray-800 rounded-lg border border-gray-700 flex justify-center">
        <div className="w-64 h-64">
          <Lottie animationData={animation} loop={true} />
        </div>
      </div>
    )
  }

  if (type === 'css') {
    // CSS animations would be applied via className or style
    return (
      <div
        ref={containerRef}
        className="p-4 bg-gray-800 rounded-lg border border-gray-700"
        style={animation}
      >
        {/* CSS animation content */}
      </div>
    )
  }

  if (type === 'gsap') {
    return (
      <div
        ref={containerRef}
        className="p-4 bg-gray-800 rounded-lg border border-gray-700"
      >
        {/* GSAP animation would be initialized here */}
        <div className="text-sm text-gray-400">GSAP animation (not yet implemented)</div>
      </div>
    )
  }

  return null
}

