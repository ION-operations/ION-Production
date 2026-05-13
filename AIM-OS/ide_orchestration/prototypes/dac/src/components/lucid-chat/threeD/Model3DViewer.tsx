/**
 * 3D Model Viewer Component
 * Displays 3D models using Three.js and React Three Fiber
 */

import React, { Suspense, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Environment, Html, useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { Mesh } from 'three'
import { Loader2 } from 'lucide-react'

interface Model3DViewerProps {
  modelUrl?: string
  previewUrl?: string
  autoRotate?: boolean
  onLoad?: () => void
  onError?: (error: string) => void
}

// Simple box placeholder while loading
const PlaceholderBox: React.FC = () => {
  const meshRef = useRef<Mesh>(null)
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.5
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3
    }
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#4a90e2" wireframe />
    </mesh>
  )
}

// GLTF/GLB Model Loader
const ModelLoader: React.FC<{
  url: string
  onLoad?: () => void
  onError?: (error: string) => void
}> = ({ url, onLoad, onError }) => {
  const [error, setError] = useState<string | null>(null)
  
  let gltf: any = null
  try {
    // useGLTF is a hook, must be called unconditionally
    gltf = useGLTF(url)
  } catch (err: any) {
    setError(err.message || 'Failed to load model')
    if (onError) {
      onError(err.message || 'Failed to load model')
    }
  }

  React.useEffect(() => {
    if (gltf && onLoad) {
      onLoad()
    }
  }, [gltf, onLoad])

  if (error) {
    return (
      <Html center>
        <div className="text-red-400 text-sm">Failed to load model</div>
      </Html>
    )
  }

  if (gltf && gltf.scene) {
    return <primitive object={gltf.scene} />
  }

  return <PlaceholderBox />
}

// Preview Image Display
const PreviewImage: React.FC<{ url: string }> = ({ url }) => {
  const texture = React.useMemo(() => {
    const loader = new THREE.TextureLoader()
    return loader.load(url)
  }, [url])

  return (
    <mesh>
      <planeGeometry args={[4, 4]} />
      <meshBasicMaterial map={texture} />
    </mesh>
  )
}

export const Model3DViewer: React.FC<Model3DViewerProps> = ({
  modelUrl,
  previewUrl,
  autoRotate = true,
  onLoad,
  onError,
}) => {
  const [loading, setLoading] = useState(true)

  const handleLoad = () => {
    setLoading(false)
    if (onLoad) onLoad()
  }

  const handleError = (error: string) => {
    setLoading(false)
    if (onError) onError(error)
  }

  return (
    <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden relative" style={{ minHeight: '400px' }}>
      <Canvas
        gl={{ antialias: true, alpha: true }}
        camera={{ position: [0, 0, 5], fov: 50 }}
      >
        <Suspense
          fallback={
            <Html center>
              <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </Html>
          }
        >
          <PerspectiveCamera makeDefault position={[0, 0, 5]} />
          
          {/* Lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
          <pointLight position={[-10, -10, -5]} intensity={0.5} />

          {/* Environment for better lighting */}
          <Environment preset="sunset" />

          {/* Model or Preview */}
          {modelUrl ? (
            <ModelLoader url={modelUrl} onLoad={handleLoad} onError={handleError} />
          ) : previewUrl ? (
            <PreviewImage url={previewUrl} />
          ) : (
            <PlaceholderBox />
          )}

          {/* Controls */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            autoRotate={autoRotate}
            autoRotateSpeed={1}
            minDistance={2}
            maxDistance={10}
          />
        </Suspense>
      </Canvas>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-gray-900/80 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-2" />
            <div className="text-sm text-gray-400">Loading 3D model...</div>
          </div>
        </div>
      )}

      {/* Controls Info */}
      <div className="absolute bottom-2 left-2 text-xs text-gray-500 bg-gray-900/80 px-2 py-1 rounded">
        Left Click: Rotate | Right Click: Pan | Scroll: Zoom
      </div>
    </div>
  )
}

