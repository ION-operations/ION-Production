/**
 * Comprehensive Meshy 3D Generation Panel
 * Full-featured interface matching official Meshy API documentation
 * Reference: https://docs.meshy.ai/en/api/
 */

import React, { useState, useRef } from 'react'
import { 
  Boxes, Upload, Settings, Download, RotateCcw, Palette, 
  Bone, Image as ImageIcon, X, Play, RefreshCw, ImagePlus,
  ChevronDown, ChevronUp, FileDown, Sparkles, Info
} from 'lucide-react'
import { MeshyService } from '../../../services/lucid-chat/threeD/MeshyService'
import { useMeshyStore, MeshyTask } from '../../../store/lucid-chat/stores'
import { Model3DViewer } from '../threeD/Model3DViewer'
import { ProgressMonitor } from '../ProgressMonitor'

type GenerationMode = 'text-to-3d' | 'image-to-3d' | 'multi-image-to-3d' | 'remesh' | 'retexture' | 'rig' | 'balance'

const ART_STYLES = [
  { value: 'realistic', label: 'Realistic' },
  { value: 'sculpture', label: 'Sculpture' },
]

const AI_MODELS = [
  { value: 'latest', label: 'Latest (Meshy 6 Preview)' },
  { value: 'meshy-5', label: 'Meshy 5' },
  { value: 'meshy-4', label: 'Meshy 4' },
]

const TOPOLOGY_OPTIONS = [
  { value: 'triangle', label: 'Triangle (Decimated)' },
  { value: 'quad', label: 'Quad (Quad-dominant)' },
]

const SYMMETRY_MODES = [
  { value: 'auto', label: 'Auto (Recommended)' },
  { value: 'on', label: 'On (Enforce)' },
  { value: 'off', label: 'Off (Disable)' },
]

export const ComprehensiveMeshyPanel: React.FC = () => {
  const meshyService = new MeshyService()
  const meshyStore = useMeshyStore()
  
  const [generationMode, setGenerationMode] = useState<GenerationMode>('text-to-3d')
  const [prompt, setPrompt] = useState('')
  const [artStyle, setArtStyle] = useState<'realistic' | 'sculpture' | ''>('')
  const [seed, setSeed] = useState<number | undefined>(undefined)
  const [mode, setMode] = useState<'preview' | 'refine'>('preview')
  const [previewTaskId, setPreviewTaskId] = useState<string>('')
  
  // Advanced Parameters
  const [aiModel, setAiModel] = useState<'meshy-4' | 'meshy-5' | 'latest'>('latest')
  const [topology, setTopology] = useState<'quad' | 'triangle'>('triangle')
  const [targetPolycount, setTargetPolycount] = useState(30000)
  const [shouldRemesh, setShouldRemesh] = useState(true)
  const [symmetryMode, setSymmetryMode] = useState<'off' | 'auto' | 'on'>('auto')
  const [isATPose, setIsATPose] = useState(false)
  const [moderation, setModeration] = useState(false)
  
  // Refine Parameters
  const [enablePBR, setEnablePBR] = useState(false)
  const [texturePrompt, setTexturePrompt] = useState('')
  const [textureImageFile, setTextureImageFile] = useState<File | null>(null)
  const [textureImagePreview, setTextureImagePreview] = useState<string | null>(null)
  const textureImageInputRef = useRef<HTMLInputElement>(null)
  
  // Image-to-3D
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Multi Image-to-3D
  const [multiImageFiles, setMultiImageFiles] = useState<File[]>([])
  const multiImageInputRef = useRef<HTMLInputElement>(null)
  
  // Remesh/Retexture/Rig/Balance
  const [taskId, setTaskId] = useState('')
  
  const [error, setError] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['generation', 'advanced']))

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(section)) {
        next.delete(section)
      } else {
        next.add(section)
      }
      return next
    })
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file')
        return
      }
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleMultiImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setMultiImageFiles(files)
  }

  const handleTextureImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file')
        return
      }
      setTextureImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setTextureImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const fileToDataUri = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  const handleGenerate = async () => {
    if (!meshyService.isAvailable()) {
      setError('Meshy API key not configured. Please set MESHY_API_KEY in .env')
      return
    }

    setError(null)

    try {
      let result

      if (generationMode === 'text-to-3d') {
        if (!prompt.trim() && mode === 'preview') {
          setError('Please enter a prompt')
          return
        }
        if (mode === 'refine' && !previewTaskId.trim()) {
          setError('Please enter the preview task ID')
          return
        }

        const request: any = {
          mode,
        }

        if (mode === 'preview') request.prompt = prompt.trim()
        if (mode === 'refine') request.preview_task_id = previewTaskId.trim()

        // Optional parameters
        if (artStyle) request.art_style = artStyle
        if (seed !== undefined) request.seed = seed
        if (aiModel !== 'latest') request.ai_model = aiModel
        if (topology !== 'triangle') request.topology = topology
        if (targetPolycount !== 30000) request.target_polycount = targetPolycount
        if (!shouldRemesh) request.should_remesh = false
        if (symmetryMode !== 'auto') request.symmetry_mode = symmetryMode
        if (isATPose) request.is_a_t_pose = true
        if (moderation) request.moderation = true

        // Refine-only parameters
        if (mode === 'refine') {
          if (enablePBR) request.enable_pbr = true
          if (texturePrompt.trim()) request.texture_prompt = texturePrompt.trim()
          if (textureImageFile) {
            request.texture_image_url = await fileToDataUri(textureImageFile)
          }
        }

        result = await meshyService.textTo3D(request)
      } else if (generationMode === 'image-to-3d') {
        if (!imageFile) {
          setError('Please upload an image')
          return
        }
        const imageUrl = await fileToDataUri(imageFile)
        
        const request: any = {
          image_url: imageUrl,
        }

        if (aiModel !== 'latest') request.ai_model = aiModel
        if (topology !== 'triangle') request.topology = topology
        if (targetPolycount !== 30000) request.target_polycount = targetPolycount
        if (!shouldRemesh) request.should_remesh = false
        if (symmetryMode !== 'auto') request.symmetry_mode = symmetryMode
        if (isATPose) request.is_a_t_pose = true
        if (moderation) request.moderation = true

        result = await meshyService.imageTo3D(request)
      } else if (generationMode === 'multi-image-to-3d') {
        if (multiImageFiles.length === 0) {
          setError('Please upload at least one image')
          return
        }
        const imageUrlArray = await Promise.all(multiImageFiles.map(fileToDataUri))
        
        const request: any = {
          image_url: imageUrlArray,
        }

        if (aiModel !== 'latest') request.ai_model = aiModel
        if (topology !== 'triangle') request.topology = topology
        if (targetPolycount !== 30000) request.target_polycount = targetPolycount
        if (!shouldRemesh) request.should_remesh = false
        if (symmetryMode !== 'auto') request.symmetry_mode = symmetryMode
        if (isATPose) request.is_a_t_pose = true
        if (moderation) request.moderation = true

        result = await meshyService.multiImageTo3D(request)
      } else if (generationMode === 'remesh') {
        if (!taskId.trim()) {
          setError('Please enter a task ID')
          return
        }
        const request: any = {
          input_task_id: taskId.trim(),
        }
        if (targetPolycount !== 30000) request.target_polycount = targetPolycount
        if (topology !== 'triangle') request.topology = topology
        result = await meshyService.remesh(request)
      } else if (generationMode === 'retexture') {
        if (!taskId.trim()) {
          setError('Please enter a task ID')
          return
        }
        // Official Retexture API requires a model_url (not a task id).
        // We accept a Meshy task id here and resolve it to a GLB URL by trying common task types.
        const sourceIdOrUrl = taskId.trim()
        let modelUrl: string | undefined

        if (sourceIdOrUrl.startsWith('http') || sourceIdOrUrl.startsWith('data:')) {
          modelUrl = sourceIdOrUrl
        } else {
          const candidates: Array<'text-to-3d' | 'image-to-3d' | 'multi-image-to-3d' | 'remesh' | 'retexture'> = [
            'text-to-3d',
            'image-to-3d',
            'multi-image-to-3d',
            'remesh',
            'retexture',
          ]

          for (const taskType of candidates) {
            const statusRes = await meshyService.getTaskStatus(sourceIdOrUrl, taskType)
            if (statusRes.success && statusRes.data) {
              modelUrl =
                statusRes.data.model_urls?.glb ||
                (typeof statusRes.data.model_url === 'string' ? statusRes.data.model_url : undefined)
              if (modelUrl) break
            }
          }
        }

        if (!modelUrl) {
          setError('Could not resolve a GLB model URL from the provided task id/URL.')
          return
        }

        const request: any = {
          model_url: modelUrl,
        }
        if (enablePBR) request.enable_pbr = true
        if (texturePrompt.trim()) request.text_style_prompt = texturePrompt.trim()
        if (textureImageFile) request.image_style_url = await fileToDataUri(textureImageFile)

        result = await meshyService.retexture(request)
      } else if (generationMode === 'rig') {
        if (!taskId.trim()) {
          setError('Please enter a task ID')
          return
        }
        // Rigging uses OpenAPI v1; MeshyService wrapper accepts `input_task_id` or `model_url`.
        const input = taskId.trim()
        const request: any = input.startsWith('http') || input.startsWith('data:')
          ? { model_url: input }
          : { input_task_id: input }
        result = await meshyService.rig(request)
      } else if (generationMode === 'balance') {
        const balanceRes = await meshyService.balance()
        if (!balanceRes.success || !balanceRes.data) {
          setError(balanceRes.error || 'Failed to retrieve balance')
          return
        }
        setError(`Balance: ${balanceRes.data.balance} credits`)
        return
      }

      if (!result || !result.success) {
        setError(result?.error || 'Failed to start generation')
        return
      }

      if (result.data) {
        const task: MeshyTask = {
          taskId: result.data.id || result.data.task_id || '',
          type: generationMode,
          prompt: prompt || undefined,
            imageData: imagePreview || undefined,
          status: result.data.status === 'SUCCEEDED' ? 'completed' : 
                  result.data.status === 'FAILED' ? 'failed' :
                  result.data.status === 'CANCELED' ? 'failed' :
                  result.data.status === 'IN_PROGRESS' ? 'processing' : 'pending',
          progress: result.data.progress || 0,
          createdAt: new Date(),
        }

        meshyStore.setCurrentTask(task)
        meshyStore.addTask(task)

        // Start polling
        const poll = generationMode === 'rig'
          ? meshyService.pollRigTaskStatus(
              task.taskId,
              (progress, status) => {
                const normalizedStatus = status === 'SUCCEEDED' ? 'completed' :
                                        status === 'FAILED' || status === 'CANCELED' ? 'failed' :
                                        status === 'IN_PROGRESS' ? 'processing' : 'pending'
                meshyStore.updateTask(task.taskId, { progress, status: normalizedStatus })
              },
              meshyStore.settings.pollingInterval
            )
          : meshyService.pollTaskStatus(
              task.taskId,
              (progress, status) => {
                const normalizedStatus = status === 'SUCCEEDED' ? 'completed' :
                                        status === 'FAILED' || status === 'CANCELED' ? 'failed' :
                                        status === 'IN_PROGRESS' ? 'processing' : 'pending'
                meshyStore.updateTask(task.taskId, { progress, status: normalizedStatus })
              },
              meshyStore.settings.pollingInterval,
              150,
              generationMode as any
            )

        poll.then((finalResult) => {
          if (finalResult.success && finalResult.data) {
            const normalizedStatus = finalResult.data.status === 'SUCCEEDED' ? 'completed' :
                                    finalResult.data.status === 'FAILED' || finalResult.data.status === 'CANCELED' ? 'failed' :
                                    finalResult.data.status === 'IN_PROGRESS' ? 'processing' : 'pending'
            meshyStore.updateTask(task.taskId, {
              status: normalizedStatus,
              progress: finalResult.data.progress || 100,
              modelUrl: finalResult.data.model_urls?.glb || finalResult.data.model_url,
              previewUrl: finalResult.data.thumbnail_url || finalResult.data.preview_url,
            })
            meshyStore.addToHistory({
              ...task,
              modelUrl: finalResult.data.model_urls?.glb || finalResult.data.model_url!,
              previewUrl: finalResult.data.thumbnail_url || finalResult.data.preview_url,
            })
          } else {
            meshyStore.updateTask(task.taskId, {
              status: 'failed',
              error: finalResult.error,
            })
          }
        })
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    }
  }

  const handleDownload = (modelUrl: string, filename: string) => {
    const a = document.createElement('a')
    a.href = modelUrl
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  const handleLoadModel = (file: File) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const url = URL.createObjectURL(file)
      const task: MeshyTask = {
        taskId: `local-${Date.now()}`,
        type: 'text-to-3d',
        status: 'completed',
        progress: 100,
        modelUrl: url,
        createdAt: new Date(),
      }
      meshyStore.setCurrentTask(task)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div className="h-full flex flex-col bg-gray-950 overflow-hidden">
      {/* Mode Selector */}
      <div className="flex border-b border-gray-800 bg-gray-900 p-2 gap-2 flex-wrap">
        {[
          { id: 'text-to-3d' as GenerationMode, label: 'Text-to-3D', icon: Boxes },
          { id: 'image-to-3d' as GenerationMode, label: 'Image-to-3D', icon: ImageIcon },
          { id: 'multi-image-to-3d' as GenerationMode, label: 'Multi-Image', icon: ImagePlus },
          { id: 'remesh' as GenerationMode, label: 'Remesh', icon: RotateCcw },
          { id: 'retexture' as GenerationMode, label: 'Retexture', icon: Palette },
          { id: 'rig' as GenerationMode, label: 'Rig & Animation', icon: Bone },
          { id: 'balance' as GenerationMode, label: 'Balance', icon: Sparkles },
        ].map((mode) => {
          const Icon = mode.icon
          return (
            <button
              key={mode.id}
              onClick={() => setGenerationMode(mode.id)}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded transition-colors ${
                generationMode === mode.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {mode.label}
            </button>
          )
        })}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-900/20 border border-red-700/50 rounded text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Text-to-3D Mode Selection */}
        {generationMode === 'text-to-3d' && (
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Generation Stage <span className="text-red-400">*</span>
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setMode('preview')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                  mode === 'preview'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                Preview (Mesh Only)
              </button>
              <button
                onClick={() => setMode('refine')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                  mode === 'refine'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                Refine (Add Texture)
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500 flex items-start gap-2">
              <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>
                Preview generates a mesh-only 3D model. Refine adds textures based on a completed preview task.
              </span>
            </div>
          </div>
        )}

        {/* Generation Parameters Section */}
        <div className="bg-gray-900 rounded-lg border border-gray-800">
          <button
            onClick={() => toggleSection('generation')}
            className="w-full flex items-center justify-between p-4 text-left"
          >
            <h3 className="text-lg font-semibold text-gray-200">Generation Parameters</h3>
            {expandedSections.has('generation') ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.has('generation') && (
            <div className="p-4 pt-0 space-y-4 border-t border-gray-800">
              {/* Text-to-3D Prompt */}
              {generationMode === 'text-to-3d' && (
                <>
                  {mode === 'preview' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Prompt <span className="text-red-400">*</span>
                        <span className="text-xs text-gray-500 ml-2">(Max 600 characters)</span>
                      </label>
                      <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe the 3D model you want to create..."
                        rows={4}
                        maxLength={600}
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                      <div className="text-xs text-gray-500 mt-1">{prompt.length}/600</div>
                    </div>
                  )}

                  {mode === 'refine' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Preview Task ID <span className="text-red-400">*</span>
                      </label>
                      <input
                        type="text"
                        value={previewTaskId}
                        onChange={(e) => setPreviewTaskId(e.target.value)}
                        placeholder="Enter the task ID from a completed preview task"
                        className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <div className="mt-2">
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Texture Prompt
                          <span className="text-xs text-gray-500 ml-2">(Optional, max 600 characters)</span>
                        </label>
                        <textarea
                          value={texturePrompt}
                          onChange={(e) => setTexturePrompt(e.target.value)}
                          placeholder="Additional description to guide the texturing process..."
                          rows={3}
                          maxLength={600}
                          className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                        />
                        <div className="text-xs text-gray-500 mt-1">{texturePrompt.length}/600</div>
                      </div>
                      <div className="mt-2">
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Texture Image (Optional)
                        </label>
                        {textureImagePreview ? (
                          <div className="relative">
                            <img
                              src={textureImagePreview}
                              alt="Texture Preview"
                              className="w-full max-h-48 object-contain rounded-lg border border-gray-700"
                            />
                            <button
                              onClick={() => {
                                setTextureImageFile(null)
                                setTextureImagePreview(null)
                                if (textureImageInputRef.current) textureImageInputRef.current.value = ''
                              }}
                              className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded hover:bg-red-700"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ) : (
                          <div
                            onClick={() => textureImageInputRef.current?.click()}
                            className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:border-gray-600 transition-colors"
                          >
                            <Upload className="w-6 h-6 text-gray-500 mx-auto mb-2" />
                            <div className="text-sm text-gray-400">Click to upload texture image</div>
                            <div className="text-xs text-gray-500 mt-1">JPG, PNG (max 10MB)</div>
                          </div>
                        )}
                        <input
                          ref={textureImageInputRef}
                          type="file"
                          accept="image/jpeg,image/png"
                          onChange={handleTextureImageUpload}
                          className="hidden"
                        />
                      </div>
                      <div className="mt-2">
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={enablePBR}
                            onChange={(e) => setEnablePBR(e.target.checked)}
                            className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-300">
                            Enable PBR Maps (Metallic, Roughness, Normal)
                          </span>
                        </label>
                        {artStyle === 'sculpture' && enablePBR && (
                          <div className="mt-1 text-xs text-yellow-400">
                            Note: Sculpture style generates its own PBR maps. Consider disabling PBR.
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Image-to-3D */}
              {generationMode === 'image-to-3d' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Image <span className="text-red-400">*</span>
                    </label>
                    <div className="space-y-2">
                      {imagePreview ? (
                        <div className="relative">
                          <img
                            src={imagePreview}
                            alt="Preview"
                            className="w-full max-h-64 object-contain rounded-lg border border-gray-700"
                          />
                          <button
                            onClick={() => {
                              setImageFile(null)
                              setImagePreview(null)
                              if (fileInputRef.current) fileInputRef.current.value = ''
                            }}
                            className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded hover:bg-red-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div
                          onClick={() => fileInputRef.current?.click()}
                          className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center cursor-pointer hover:border-gray-600 transition-colors"
                        >
                          <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                          <div className="text-sm text-gray-400">Click to upload or drag and drop</div>
                          <div className="text-xs text-gray-500 mt-1">JPG, PNG, WEBP (max 10MB)</div>
                        </div>
                      )}
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="hidden"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Optional Prompt
                      <span className="text-xs text-gray-500 ml-2">(Max 600 characters)</span>
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Additional description to guide the conversion..."
                      rows={2}
                      maxLength={600}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    />
                    <div className="text-xs text-gray-500 mt-1">{prompt.length}/600</div>
                  </div>
                </>
              )}

              {/* Multi Image-to-3D */}
              {generationMode === 'multi-image-to-3d' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Images <span className="text-red-400">*</span>
                    </label>
                    <div className="space-y-2">
                      {multiImageFiles.length > 0 && (
                        <div className="grid grid-cols-2 gap-2 mb-2">
                          {multiImageFiles.map((file, index) => (
                            <div key={index} className="relative">
                              <img
                                src={URL.createObjectURL(file)}
                                alt={`Preview ${index + 1}`}
                                className="w-full h-24 object-cover rounded border border-gray-700"
                              />
                              <button
                                onClick={() => setMultiImageFiles(prev => prev.filter((_, i) => i !== index))}
                                className="absolute top-1 right-1 p-1 bg-red-600 text-white rounded hover:bg-red-700"
                              >
                                <X className="w-3 h-3" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                      <div
                        onClick={() => multiImageInputRef.current?.click()}
                        className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:border-gray-600 transition-colors"
                      >
                        <Upload className="w-6 h-6 text-gray-500 mx-auto mb-2" />
                        <div className="text-sm text-gray-400">Click to upload multiple images</div>
                        <div className="text-xs text-gray-500 mt-1">JPG, PNG, WEBP (max 10MB each)</div>
                      </div>
                      <input
                        ref={multiImageInputRef}
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={handleMultiImageUpload}
                        className="hidden"
                      />
                      {multiImageFiles.length > 0 && (
                        <div className="text-xs text-gray-500">
                          {multiImageFiles.length} image{multiImageFiles.length !== 1 ? 's' : ''} selected
                        </div>
                      )}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Optional Prompt
                      <span className="text-xs text-gray-500 ml-2">(Max 600 characters)</span>
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Additional description to guide the conversion..."
                      rows={2}
                      maxLength={600}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    />
                    <div className="text-xs text-gray-500 mt-1">{prompt.length}/600</div>
                  </div>
                </>
              )}

              {/* Remesh/Retexture/Rig/Balance */}
              {(generationMode === 'remesh' || generationMode === 'retexture' || generationMode === 'rig' || generationMode === 'balance') && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Task ID <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={taskId}
                    onChange={(e) => setTaskId(e.target.value)}
                    placeholder="Enter the task ID of an existing model"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="mt-2 text-xs text-gray-500">
                    You can find task IDs in your generation history below.
                  </div>
                </div>
              )}

              {/* Retexture-specific */}
              {generationMode === 'retexture' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Texture Prompt
                      <span className="text-xs text-gray-500 ml-2">(Optional, max 600 characters)</span>
                    </label>
                    <textarea
                      value={texturePrompt}
                      onChange={(e) => setTexturePrompt(e.target.value)}
                      placeholder="Describe the texture style..."
                      rows={3}
                      maxLength={600}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    />
                    <div className="text-xs text-gray-500 mt-1">{texturePrompt.length}/600</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Texture Image (Optional)
                    </label>
                    {textureImagePreview ? (
                      <div className="relative">
                        <img
                          src={textureImagePreview}
                          alt="Texture Preview"
                          className="w-full max-h-48 object-contain rounded-lg border border-gray-700"
                        />
                        <button
                          onClick={() => {
                            setTextureImageFile(null)
                            setTextureImagePreview(null)
                            if (textureImageInputRef.current) textureImageInputRef.current.value = ''
                          }}
                          className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div
                        onClick={() => textureImageInputRef.current?.click()}
                        className="border-2 border-dashed border-gray-700 rounded-lg p-6 text-center cursor-pointer hover:border-gray-600 transition-colors"
                      >
                        <Upload className="w-6 h-6 text-gray-500 mx-auto mb-2" />
                        <div className="text-sm text-gray-400">Click to upload texture image</div>
                      </div>
                    )}
                    <input
                      ref={textureImageInputRef}
                      type="file"
                      accept="image/jpeg,image/png"
                      onChange={handleTextureImageUpload}
                      className="hidden"
                    />
                  </div>
                  <div>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={enablePBR}
                        onChange={(e) => setEnablePBR(e.target.checked)}
                        className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-300">Enable PBR Maps</span>
                    </label>
                  </div>
                </>
              )}

              {/* Remesh-specific */}
              {generationMode === 'remesh' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Target Polycount: {targetPolycount.toLocaleString()}
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="300000"
                      step="100"
                      value={targetPolycount}
                      onChange={(e) => setTargetPolycount(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>100</span>
                      <span>150K</span>
                      <span>300K</span>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Topology
                    </label>
                    <select
                      value={topology}
                      onChange={(e) => setTopology(e.target.value as 'quad' | 'triangle')}
                      className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {TOPOLOGY_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {/* Art Style (for text/image generation) */}
              {(generationMode === 'text-to-3d' || generationMode === 'image-to-3d' || generationMode === 'multi-image-to-3d') && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Art Style
                  </label>
                  <select
                    value={artStyle}
                    onChange={(e) => setArtStyle(e.target.value as 'realistic' | 'sculpture' | '')}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">None (Default: Realistic)</option>
                    {ART_STYLES.map((style) => (
                      <option key={style.value} value={style.value}>
                        {style.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Seed */}
              {(generationMode === 'text-to-3d' || generationMode === 'image-to-3d' || generationMode === 'multi-image-to-3d') && (
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Seed (for reproducibility)
                  </label>
                  <input
                    type="number"
                    value={seed || ''}
                    onChange={(e) => setSeed(e.target.value ? parseInt(e.target.value) : undefined)}
                    placeholder="Leave empty for random"
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Advanced Parameters Section */}
        {(generationMode === 'text-to-3d' || generationMode === 'image-to-3d' || generationMode === 'multi-image-to-3d') && (
          <div className="bg-gray-900 rounded-lg border border-gray-800">
            <button
              onClick={() => toggleSection('advanced')}
              className="w-full flex items-center justify-between p-4 text-left"
            >
              <h3 className="text-lg font-semibold text-gray-200">Advanced Parameters</h3>
              {expandedSections.has('advanced') ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
            </button>

            {expandedSections.has('advanced') && (
              <div className="p-4 pt-0 space-y-4 border-t border-gray-800">
                {/* AI Model */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    AI Model
                  </label>
                  <select
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value as 'meshy-4' | 'meshy-5' | 'latest')}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {AI_MODELS.map((model) => (
                      <option key={model.value} value={model.value}>
                        {model.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Topology */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Topology
                  </label>
                  <select
                    value={topology}
                    onChange={(e) => setTopology(e.target.value as 'quad' | 'triangle')}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {TOPOLOGY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Target Polycount */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Target Polycount: {targetPolycount.toLocaleString()}
                  </label>
                  <input
                    type="range"
                    min="100"
                    max="300000"
                    step="100"
                    value={targetPolycount}
                    onChange={(e) => setTargetPolycount(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>100</span>
                    <span>150K</span>
                    <span>300K</span>
                  </div>
                </div>

                {/* Should Remesh */}
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={shouldRemesh}
                      onChange={(e) => setShouldRemesh(e.target.checked)}
                      className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-300">Enable Remesh</span>
                  </label>
                  <div className="text-xs text-gray-500 mt-1 ml-6">
                    When disabled, returns unprocessed triangular mesh (highest precision)
                  </div>
                </div>

                {/* Symmetry Mode */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Symmetry Mode
                  </label>
                  <select
                    value={symmetryMode}
                    onChange={(e) => setSymmetryMode(e.target.value as 'off' | 'auto' | 'on')}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {SYMMETRY_MODES.map((mode) => (
                      <option key={mode.value} value={mode.value}>
                        {mode.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* A/T Pose */}
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={isATPose}
                      onChange={(e) => setIsATPose(e.target.checked)}
                      className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-300">Generate in A/T Pose</span>
                  </label>
                </div>

                {/* Moderation */}
                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={moderation}
                      onChange={(e) => setModeration(e.target.checked)}
                      className="w-4 h-4 rounded bg-gray-800 border-gray-700 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-300">Enable Content Moderation</span>
                  </label>
                  <div className="text-xs text-gray-500 mt-1 ml-6">
                    Automatically screen for potentially harmful content
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={meshyStore.currentTask?.status === 'processing'}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {meshyStore.currentTask?.status === 'processing' ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Generate
            </>
          )}
        </button>

        {/* Current Task Progress */}
        {meshyStore.currentTask && (
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
            <ProgressMonitor
              taskId={meshyStore.currentTask.taskId}
              status={meshyStore.currentTask.status}
              progress={meshyStore.currentTask.progress}
              error={meshyStore.currentTask.error}
            />
          </div>
        )}

        {/* 3D Viewer */}
        {(meshyStore.currentTask?.modelUrl || meshyStore.currentTask?.previewUrl) && (
          <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-200">3D Model Viewer</h3>
              {meshyStore.currentTask.modelUrl && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDownload(meshyStore.currentTask!.modelUrl!, 'model.glb')}
                    className="flex items-center gap-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                  >
                    <Download className="w-4 h-4" />
                    Download GLB
                  </button>
                </div>
              )}
            </div>
            <div style={{ height: '500px' }}>
              <Model3DViewer
                modelUrl={meshyStore.currentTask.modelUrl}
                previewUrl={meshyStore.currentTask.previewUrl}
                autoRotate={meshyStore.currentTask.status === 'completed'}
              />
            </div>
          </div>
        )}

        {/* Task History */}
        {meshyStore.history.length > 0 && (
          <div className="bg-gray-900 rounded-lg border border-gray-800">
            <button
              onClick={() => toggleSection('history')}
              className="w-full flex items-center justify-between p-4 text-left"
            >
              <h3 className="text-lg font-semibold text-gray-200">
                History ({meshyStore.history.length})
              </h3>
              {expandedSections.has('history') ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>

            {expandedSections.has('history') && (
              <div className="p-4 pt-0 space-y-2 border-t border-gray-800 max-h-96 overflow-y-auto">
                {meshyStore.history.map((task) => (
                  <div
                    key={task.taskId}
                    className="p-3 bg-gray-800 rounded border border-gray-700 hover:border-gray-600 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-200 truncate">
                          {task.prompt || 'Image-to-3D'}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {task.type} • {task.createdAt.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          Task ID: {task.taskId}
                        </div>
                        {task.previewUrl && (
                          <img
                            src={task.previewUrl}
                            alt="Preview"
                            className="w-full mt-2 rounded border border-gray-700"
                          />
                        )}
                      </div>
                      <div className="flex flex-col gap-1">
                        {task.modelUrl && (
                          <button
                            onClick={() => {
                              meshyStore.setCurrentTask(task)
                              setTaskId(task.taskId) // Set for remesh/retexture/rig
                            }}
                            className="p-1 text-blue-400 hover:text-blue-300"
                            title="Load in viewer"
                          >
                            <Play className="w-4 h-4" />
                          </button>
                        )}
                        {task.modelUrl && (
                          <button
                            onClick={() => handleDownload(task.modelUrl!, `model-${task.taskId}.glb`)}
                            className="p-1 text-gray-400 hover:text-gray-300"
                            title="Download"
                          >
                            <FileDown className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Model Loader */}
        <div className="bg-gray-900 rounded-lg border border-gray-800">
          <button
            onClick={() => toggleSection('loader')}
            className="w-full flex items-center justify-between text-left p-4"
          >
            <h3 className="text-lg font-semibold text-gray-200">Load Local Model</h3>
            {expandedSections.has('loader') ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expandedSections.has('loader') && (
            <div className="p-4 pt-0 border-t border-gray-800">
              <input
                type="file"
                accept=".glb,.gltf"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleLoadModel(file)
                }}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 text-sm"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
