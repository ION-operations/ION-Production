/**
 * Image Renderer
 * Image display with lightbox viewer
 */

import React, { useState } from 'react'
import { Maximize2, X } from 'lucide-react'

interface ImageRendererProps {
  src: string
  alt?: string
  caption?: string
}

export const ImageRenderer: React.FC<ImageRendererProps> = ({
  src,
  alt = 'Image',
  caption,
}) => {
  const [lightboxOpen, setLightboxOpen] = useState(false)

  return (
    <>
      <div className="relative group">
        <img
          src={src}
          alt={alt}
          className="max-w-full h-auto rounded-lg border border-gray-700 cursor-pointer hover:opacity-90 transition-opacity"
          onClick={() => setLightboxOpen(true)}
          onError={(e) => {
            // Fallback for broken images
            e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%231e293b" width="400" height="300"/%3E%3Ctext fill="%236b7280" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage not available%3C/text%3E%3C/svg%3E'
          }}
        />
        <button
          onClick={() => setLightboxOpen(true)}
          className="absolute top-2 right-2 p-2 bg-gray-800/80 rounded opacity-0 group-hover:opacity-100 transition-opacity"
          title="View full size"
        >
          <Maximize2 className="w-4 h-4 text-gray-300" />
        </button>
        {caption && (
          <div className="mt-2 text-sm text-gray-400 text-center">{caption}</div>
        )}
      </div>

      {/* Lightbox */}
      {lightboxOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
          onClick={() => setLightboxOpen(false)}
        >
          <button
            onClick={() => setLightboxOpen(false)}
            className="absolute top-4 right-4 p-2 bg-gray-800 rounded text-gray-300 hover:text-white"
          >
            <X className="w-6 h-6" />
          </button>
          <img
            src={src}
            alt={alt}
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  )
}

