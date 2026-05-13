import React from 'react'
import { useApp } from '../contexts/AppContext'

export function WaveBackground() {
  const { state } = useApp()
  
  if (!state.waveBackground.isEnabled) {
    return null
  }

  return (
    <div 
      className="fixed inset-0 -z-10 wave-bg opacity-20"
      style={{
        animationDuration: `${10 / state.waveBackground.speed}s`,
        opacity: state.waveBackground.intensity * 0.3
      }}
    />
  )
}
