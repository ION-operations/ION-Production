/**
 * Video Renderer
 * Video playback with controls
 */

import React from 'react'

interface VideoRendererProps {
  src: string
  type?: string
  caption?: string
}

export const VideoRenderer: React.FC<VideoRendererProps> = ({
  src,
  type,
  caption,
}) => {
  return (
    <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
      <video
        src={src}
        controls
        className="w-full rounded"
        style={{ maxHeight: '600px' }}
      >
        Your browser does not support the video tag.
      </video>
      {caption && (
        <div className="mt-2 text-sm text-gray-400 text-center">{caption}</div>
      )}
    </div>
  )
}

