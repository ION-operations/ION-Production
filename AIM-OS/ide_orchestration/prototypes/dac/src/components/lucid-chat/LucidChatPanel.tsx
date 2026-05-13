/**
 * Lucid Chat Main Panel
 * Unified panel for all API integrations
 */

import React, { useState, useEffect } from 'react'
import { Mic, MessageSquare, Boxes, Settings } from 'lucide-react'
import { ProgressMonitor } from './ProgressMonitor'
import { PromptInputPanel } from './PromptInputPanel'
import { Model3DViewer } from './threeD/Model3DViewer'
import { EnhancedAudioPlayer } from './audio/EnhancedAudioPlayer'
import { EnhancedChatInterface } from './chat/EnhancedChatInterface'
import { AdvancedChatPanel } from './AdvancedChatPanel'
import { ComprehensiveMeshyPanel } from './meshy/ComprehensiveMeshyPanel'
import { ComprehensiveElevenLabsPanel } from './elevenlabs/ComprehensiveElevenLabsPanel'
import { MeshyService } from '../../services/lucid-chat/threeD/MeshyService'
import { ElevenLabsService } from '../../services/lucid-chat/audio/ElevenLabsService'
import { MinimaxService } from '../../services/lucid-chat/llm/MinimaxService'
import { useMeshyStore } from '../../store/lucid-chat/stores'
import { useElevenLabsStore } from '../../store/lucid-chat/stores'
import { useMinimaxStore } from '../../store/lucid-chat/stores'

type TabType = 'meshy' | 'elevenlabs' | 'minimax' | 'settings'

export const LucidChatPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('meshy')
  const [prompt, setPrompt] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Services
  const meshyService = new MeshyService()
  const elevenLabsService = new ElevenLabsService()
  const minimaxService = new MinimaxService()

  // Stores
  const meshyStore = useMeshyStore()
  const elevenLabsStore = useElevenLabsStore()
  const minimaxStore = useMinimaxStore()

  // Load voices on mount
  useEffect(() => {
    if (elevenLabsService.isAvailable()) {
      elevenLabsService.getVoices().then((result) => {
        if (result.success && result.data) {
          elevenLabsStore.setVoices(result.data)
          if (result.data.length > 0) {
            elevenLabsStore.setSelectedVoice(result.data[0].voice_id)
          }
        }
      })
    }
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setError(null)

    try {
      if (activeTab === 'meshy') {
        await handleMeshyGenerate()
      } else if (activeTab === 'elevenlabs') {
        await handleElevenLabsGenerate()
      } else if (activeTab === 'minimax') {
        await handleMinimaxGenerate()
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    }
  }

  const handleMeshyGenerate = async () => {
    if (!meshyService.isAvailable()) {
      setError('Meshy API key not configured. Please set MESHY_API_KEY in .env')
      return
    }

    const normalizeStatus = (status: string): 'pending' | 'processing' | 'completed' | 'failed' => {
      if (status === 'SUCCEEDED') return 'completed'
      if (status === 'FAILED' || status === 'CANCELED') return 'failed'
      if (status === 'IN_PROGRESS') return 'processing'
      return 'pending'
    }

    const task: any = {
      taskId: '',
      type: 'text-to-3d',
      prompt,
      status: 'pending',
      progress: 0,
      createdAt: new Date(),
    }

    const result = await meshyService.textTo3D({
      prompt,
      mode: meshyStore.settings.defaultMode,
      art_style: meshyStore.settings.defaultArtStyle || undefined,
    })

    if (!result.success) {
      setError(result.error || 'Failed to start 3D generation')
      return
    }

    if (result.data) {
      task.taskId = result.data.task_id
      task.status = normalizeStatus(result.data.status as any)
      meshyStore.setCurrentTask(task)
      meshyStore.addTask(task)

      // Start polling
      meshyService.pollTaskStatus(
        task.taskId,
        (progress, status) => {
          meshyStore.updateTask(task.taskId, { progress, status: normalizeStatus(status) })
        },
        meshyStore.settings.pollingInterval
      ).then((finalResult) => {
        if (finalResult.success && finalResult.data) {
          meshyStore.updateTask(task.taskId, {
            status: normalizeStatus(finalResult.data.status as any),
            progress: finalResult.data.progress || 100,
            modelUrl: finalResult.data.model_url,
            previewUrl: finalResult.data.preview_url,
          })
          meshyStore.addToHistory(task)
        } else {
          meshyStore.updateTask(task.taskId, {
            status: 'failed',
            error: finalResult.error,
          })
        }
      })
    }
  }

  const handleElevenLabsGenerate = async () => {
    if (!elevenLabsService.isAvailable()) {
      setError('ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY in .env')
      return
    }

    if (!elevenLabsStore.selectedVoiceId) {
      setError('Please select a voice')
      return
    }

    elevenLabsStore.setGenerating(true)
    elevenLabsStore.setError(null)

    const result = await elevenLabsService.textToSpeech({
      text: prompt,
      voice_id: elevenLabsStore.selectedVoiceId,
      model_id: elevenLabsStore.modelId,
      voice_settings: elevenLabsStore.voiceSettings,
    })

    if (result.success && result.data) {
      const audioBlob = await fetch(result.data.audio_url!).then((r) => r.blob())
      elevenLabsStore.setAudio(result.data.audio_url, audioBlob)
      elevenLabsStore.addToHistory(
        prompt,
        elevenLabsStore.selectedVoiceId!,
        result.data.audio_url!
      )
    } else {
      elevenLabsStore.setError(result.error || 'Failed to generate audio')
    }

    elevenLabsStore.setGenerating(false)
  }

  const handleMinimaxGenerate = async () => {
    if (!minimaxService.isAvailable()) {
      setError('Minimax API key not configured. Please set MINIMAX_API_KEY in .env')
      return
    }

    // Add user message
    minimaxStore.addMessage({
      role: 'user',
      content: prompt,
      timestamp: new Date(),
    })

    minimaxStore.setInput('')
    minimaxStore.setStreaming(true)
    minimaxStore.setStreamingMessage('')

    let fullResponse = ''

    await minimaxService.streamChatCompletion(
      {
        model: minimaxStore.selectedModel,
        messages: [
          ...minimaxStore.messages.map((m) => ({
            role: m.role as 'system' | 'user' | 'assistant',
            content: m.content,
          })),
        ],
        temperature: minimaxStore.temperature,
        max_tokens: minimaxStore.maxTokens,
        top_p: minimaxStore.topP,
        frequency_penalty: minimaxStore.frequencyPenalty,
        presence_penalty: minimaxStore.presencePenalty,
      },
      (chunk) => {
        const content = chunk.choices[0]?.delta?.content || ''
        if (content) {
          fullResponse += content
          minimaxStore.setStreamingMessage(fullResponse)
        }
      }
    )

    // Add assistant message
    minimaxStore.addMessage({
      role: 'assistant',
      content: fullResponse,
      timestamp: new Date(),
    })

    minimaxStore.setStreaming(false)
    minimaxStore.setStreamingMessage('')
  }

  const tabs = [
    { id: 'meshy' as TabType, label: '3D Models', icon: Boxes },
    { id: 'elevenlabs' as TabType, label: 'Audio', icon: Mic },
    { id: 'minimax' as TabType, label: 'Chat', icon: MessageSquare },
    { id: 'settings' as TabType, label: 'Settings', icon: Settings },
  ]

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-800 bg-gray-900">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-400 border-b-2 border-blue-400 bg-gray-900'
                  : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-900/20 border border-red-700/50 rounded text-sm text-red-300">
            {error}
          </div>
        )}

        {activeTab === 'meshy' && (
          <ComprehensiveMeshyPanel />
        )}

        {activeTab === 'elevenlabs' && (
          <ComprehensiveElevenLabsPanel />
        )}

        {activeTab === 'minimax' && (
          <div className="h-full flex flex-col">
            <AdvancedChatPanel />
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-200">Settings</h2>
            <div className="text-sm text-gray-400">
              API configuration and preferences coming soon...
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

