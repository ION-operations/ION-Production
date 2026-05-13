/**
 * Comprehensive ElevenLabs TTS Panel
 * Full-featured interface with ALL ElevenLabs API capabilities
 */

import React, { useState, useEffect, useRef } from 'react'
import {
  Mic, Upload, Settings, Download, Play, Pause, Volume2, VolumeX,
  Star, Search, X, RefreshCw, Copy, Check, ChevronDown, ChevronUp,
  FileDown, Trash2, UserPlus, Zap
} from 'lucide-react'
import { ElevenLabsService } from '../../../services/lucid-chat/audio/ElevenLabsService'
import { useElevenLabsStore } from '../../../store/lucid-chat/stores'
import { EnhancedAudioPlayer } from '../audio/EnhancedAudioPlayer'

const MODELS = [
  { id: 'eleven_multilingual_v2', name: 'Multilingual v2', languages: 29, quality: 'High' },
  { id: 'eleven_flash_v2_5', name: 'Flash v2.5', languages: 32, quality: 'Ultra-Low Latency' },
  { id: 'eleven_turbo_v2_5', name: 'Turbo v2.5', languages: 32, quality: 'Balanced' },
  { id: 'eleven_monolingual_v1', name: 'Monolingual v1', languages: 1, quality: 'Highest (English)' },
]

const OUTPUT_FORMATS = [
  { id: 'mp3_44100_128', name: 'MP3 44.1kHz 128kbps', quality: 'Standard' },
  { id: 'mp3_44100_192', name: 'MP3 44.1kHz 192kbps', quality: 'High' },
  { id: 'pcm_16000', name: 'PCM 16kHz', quality: 'Low Latency' },
  { id: 'pcm_22050', name: 'PCM 22.05kHz', quality: 'Medium' },
  { id: 'pcm_24000', name: 'PCM 24kHz', quality: 'High' },
  { id: 'pcm_44100', name: 'PCM 44.1kHz', quality: 'Highest' },
]

const PRESETS = {
  balanced: { stability: 0.5, similarity_boost: 0.75, style: 0.0, use_speaker_boost: true },
  stable: { stability: 0.8, similarity_boost: 0.5, style: 0.0, use_speaker_boost: true },
  expressive: { stability: 0.3, similarity_boost: 0.9, style: 0.5, use_speaker_boost: true },
}

type TabType = 'tts' | 'voices' | 'clone' | 'settings'

export const ComprehensiveElevenLabsPanel: React.FC = () => {
  const elevenLabsService = new ElevenLabsService()
  const elevenLabsStore = useElevenLabsStore()
  
  const [activeTab, setActiveTab] = useState<TabType>('tts')
  const [text, setText] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  
  // Voice Cloning
  const [cloningName, setCloningName] = useState('')
  const [cloningDescription, setCloningDescription] = useState('')
  const [cloningFiles, setCloningFiles] = useState<File[]>([])
  const [isCloning, setIsCloning] = useState(false)
  const cloningFileInputRef = useRef<HTMLInputElement>(null)
  
  const [error, setError] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['tts']))

  useEffect(() => {
    if (elevenLabsService.isAvailable() && activeTab === 'voices') {
      elevenLabsService.getVoices().then((result) => {
        if (result.success && result.data) {
          elevenLabsStore.setVoices(result.data)
          if (result.data.length > 0 && !elevenLabsStore.selectedVoiceId) {
            elevenLabsStore.setSelectedVoice(result.data[0].voice_id)
          }
        }
      })
    }
  }, [activeTab])

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

  const handleGenerate = async () => {
    if (!elevenLabsService.isAvailable()) {
      setError('ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY in .env')
      return
    }

    if (!text.trim()) {
      setError('Please enter text')
      return
    }

    if (!elevenLabsStore.selectedVoiceId) {
      setError('Please select a voice')
      return
    }

    setError(null)
    elevenLabsStore.setGenerating(true)
    elevenLabsStore.setError(null)

    const result = await elevenLabsService.textToSpeech({
      text,
      voice_id: elevenLabsStore.selectedVoiceId,
      model_id: elevenLabsStore.modelId,
      voice_settings: elevenLabsStore.voiceSettings,
    })

    if (result.success && result.data) {
      const audioBlob = await fetch(result.data.audio_url!).then((r) => r.blob())
      elevenLabsStore.setAudio(result.data.audio_url, audioBlob)
      elevenLabsStore.addToHistory(
        text,
        elevenLabsStore.selectedVoiceId!,
        result.data.audio_url!
      )
    } else {
      elevenLabsStore.setError(result.error || 'Failed to generate audio')
    }

    elevenLabsStore.setGenerating(false)
  }

  const handleCloneVoice = async () => {
    if (!cloningName.trim()) {
      setError('Please enter a voice name')
      return
    }

    if (cloningFiles.length === 0) {
      setError('Please upload at least one audio sample')
      return
    }

    setIsCloning(true)
    setError(null)

    const result = await elevenLabsService.cloneVoice(
      cloningName,
      cloningFiles,
      cloningDescription || undefined
    )

    if (result.success && result.data) {
      // Refresh voices list
      const voicesResult = await elevenLabsService.getVoices()
      if (voicesResult.success && voicesResult.data) {
        elevenLabsStore.setVoices(voicesResult.data)
        elevenLabsStore.setSelectedVoice(result.data.voice_id)
      }
      
      // Reset cloning form
      setCloningName('')
      setCloningDescription('')
      setCloningFiles([])
      setActiveTab('voices')
    } else {
      setError(result.error || 'Failed to clone voice')
    }

    setIsCloning(false)
  }

  const handleVoiceFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    setCloningFiles(prev => [...prev, ...files])
  }

  const filteredVoices = elevenLabsStore.voices.filter(voice => {
    const matchesSearch = voice.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         voice.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || voice.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = Array.from(new Set(elevenLabsStore.voices.map(v => v.category)))

  return (
    <div className="h-full flex flex-col bg-gray-950 overflow-hidden">
      {/* Tab Navigation */}
      <div className="flex border-b border-gray-800 bg-gray-900 p-2 gap-2">
        {[
          { id: 'tts' as TabType, label: 'Text-to-Speech', icon: Mic },
          { id: 'voices' as TabType, label: 'Voices', icon: UserPlus },
          { id: 'clone' as TabType, label: 'Clone Voice', icon: Copy },
          { id: 'settings' as TabType, label: 'Settings', icon: Settings },
        ].map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
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

        {/* TTS Tab */}
        {activeTab === 'tts' && (
          <div className="space-y-4">
            {/* Voice Selection */}
            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Voice <span className="text-red-400">*</span>
              </label>
              <select
                value={elevenLabsStore.selectedVoiceId || ''}
                onChange={(e) => elevenLabsStore.setSelectedVoice(e.target.value)}
                className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a voice...</option>
                {elevenLabsStore.voices.map((voice) => (
                  <option key={voice.voice_id} value={voice.voice_id}>
                    {voice.name} {voice.category ? `(${voice.category})` : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Text Input */}
            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Text <span className="text-red-400">*</span>
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text to convert to speech..."
                rows={6}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <div className="flex justify-between mt-2">
                <div className="text-xs text-gray-500">
                  {text.length} characters / {text.split(/\s+/).filter(w => w).length} words
                </div>
                <div className="text-xs text-gray-500">
                  Max: 5,000 characters
                </div>
              </div>
            </div>

            {/* Voice Settings */}
            <div className="bg-gray-900 rounded-lg border border-gray-800">
              <button
                onClick={() => toggleSection('voiceSettings')}
                className="w-full flex items-center justify-between p-4 text-left"
              >
                <h3 className="text-lg font-semibold text-gray-200">Voice Settings</h3>
                {expandedSections.has('voiceSettings') ? (
                  <ChevronUp className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                )}
              </button>

              {expandedSections.has('voiceSettings') && (
                <div className="p-4 pt-0 space-y-4 border-t border-gray-800">
                  {/* Presets */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Presets
                    </label>
                    <div className="flex gap-2">
                      {Object.entries(PRESETS).map(([name, preset]) => (
                        <button
                          key={name}
                          onClick={() => elevenLabsStore.updateVoiceSettings(preset)}
                          className="px-3 py-1 bg-gray-800 text-gray-300 rounded hover:bg-gray-700 text-sm capitalize"
                        >
                          {name}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Stability */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Stability: {elevenLabsStore.voiceSettings.stability.toFixed(2)}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={elevenLabsStore.voiceSettings.stability}
                      onChange={(e) => elevenLabsStore.updateVoiceSettings({ stability: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>More Variable</span>
                      <span>More Stable</span>
                    </div>
                  </div>

                  {/* Similarity Boost */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Similarity Boost: {elevenLabsStore.voiceSettings.similarity_boost.toFixed(2)}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={elevenLabsStore.voiceSettings.similarity_boost}
                      onChange={(e) => elevenLabsStore.updateVoiceSettings({ similarity_boost: parseFloat(e.target.value) })}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Less Similar</span>
                      <span>More Similar</span>
                    </div>
                  </div>

                  {/* Style (if supported) */}
                  {elevenLabsStore.voiceSettings.style !== undefined && (
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Style: {elevenLabsStore.voiceSettings.style.toFixed(2)}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={elevenLabsStore.voiceSettings.style}
                        onChange={(e) => elevenLabsStore.updateVoiceSettings({ style: parseFloat(e.target.value) })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Neutral</span>
                        <span>Expressive</span>
                      </div>
                    </div>
                  )}

                  {/* Speaker Boost */}
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-300">
                      Speaker Boost
                    </label>
                    <button
                      onClick={() => elevenLabsStore.updateVoiceSettings({ 
                        use_speaker_boost: !elevenLabsStore.voiceSettings.use_speaker_boost 
                      })}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        elevenLabsStore.voiceSettings.use_speaker_boost
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                      }`}
                    >
                      {elevenLabsStore.voiceSettings.use_speaker_boost ? 'On' : 'Off'}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Model & Format Selection */}
            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Model
                </label>
                <select
                  value={elevenLabsStore.modelId}
                  onChange={(e) => {
                    // Update modelId in store (need to add this action)
                    const store = elevenLabsStore as any
                    store.modelId = e.target.value
                  }}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {MODELS.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name} - {model.quality} ({model.languages} languages)
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={elevenLabsStore.isGenerating || !text.trim() || !elevenLabsStore.selectedVoiceId}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {elevenLabsStore.isGenerating ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Generate Audio
                </>
              )}
            </button>

            {/* Audio Player */}
            {elevenLabsStore.audioUrl && (
              <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
                <EnhancedAudioPlayer
                  audioUrl={elevenLabsStore.audioUrl}
                  audioBlob={elevenLabsStore.audioBlob || undefined}
                  title="Generated Audio"
                />
              </div>
            )}
          </div>
        )}

        {/* Voices Tab */}
        {activeTab === 'voices' && (
          <div className="space-y-4">
            {/* Search & Filter */}
            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 space-y-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search voices..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={`px-3 py-1 rounded text-sm ${
                    selectedCategory === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  All
                </button>
                {categories.map((category) => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-3 py-1 rounded text-sm ${
                      selectedCategory === category
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>

            {/* Voice Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredVoices.map((voice) => (
                <div
                  key={voice.voice_id}
                  className={`p-4 bg-gray-900 rounded-lg border ${
                    elevenLabsStore.selectedVoiceId === voice.voice_id
                      ? 'border-blue-600 bg-blue-900/20'
                      : 'border-gray-800 hover:border-gray-700'
                  } transition-colors`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-200">{voice.name}</h4>
                      <div className="text-xs text-gray-500">{voice.category}</div>
                    </div>
                    <button
                      onClick={() => elevenLabsStore.toggleFavorite(voice.voice_id)}
                      className={`p-1 ${
                        elevenLabsStore.favoriteVoiceIds.includes(voice.voice_id)
                          ? 'text-yellow-400'
                          : 'text-gray-500 hover:text-yellow-400'
                      }`}
                    >
                      <Star className={`w-4 h-4 ${elevenLabsStore.favoriteVoiceIds.includes(voice.voice_id) ? 'fill-current' : ''}`} />
                    </button>
                  </div>
                  
                  {voice.description && (
                    <p className="text-xs text-gray-400 mb-3">{voice.description}</p>
                  )}

                  {voice.preview_url && (
                    <audio
                      src={voice.preview_url}
                      controls
                      className="w-full h-8 mb-3"
                    />
                  )}

                  <button
                    onClick={() => elevenLabsStore.setSelectedVoice(voice.voice_id)}
                    className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                      elevenLabsStore.selectedVoiceId === voice.voice_id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {elevenLabsStore.selectedVoiceId === voice.voice_id ? 'Selected' : 'Select'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Clone Voice Tab */}
        {activeTab === 'clone' && (
          <div className="space-y-4">
            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Voice Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={cloningName}
                  onChange={(e) => setCloningName(e.target.value)}
                  placeholder="My Custom Voice"
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={cloningDescription}
                  onChange={(e) => setCloningDescription(e.target.value)}
                  placeholder="Describe this voice..."
                  rows={3}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Audio Samples <span className="text-red-400">*</span>
                  <span className="text-xs text-gray-500 ml-2">(1-25 samples recommended)</span>
                </label>
                <div className="space-y-2">
                  <div
                    onClick={() => cloningFileInputRef.current?.click()}
                    className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center cursor-pointer hover:border-gray-600 transition-colors"
                  >
                    <Upload className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                    <div className="text-sm text-gray-400">Click to upload audio samples</div>
                    <div className="text-xs text-gray-500 mt-1">MP3, WAV, M4A (max 25MB each)</div>
                  </div>
                  <input
                    ref={cloningFileInputRef}
                    type="file"
                    accept="audio/*"
                    multiple
                    onChange={handleVoiceFileUpload}
                    className="hidden"
                  />
                  
                  {cloningFiles.length > 0 && (
                    <div className="space-y-2 mt-4">
                      {cloningFiles.map((file, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 bg-gray-800 rounded border border-gray-700"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="text-sm text-gray-200 truncate">{file.name}</div>
                            <div className="text-xs text-gray-500">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </div>
                          </div>
                          <button
                            onClick={() => setCloningFiles(prev => prev.filter((_, i) => i !== index))}
                            className="p-1 text-red-400 hover:text-red-300"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <button
                onClick={handleCloneVoice}
                disabled={isCloning || !cloningName.trim() || cloningFiles.length === 0}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {isCloning ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Cloning Voice...
                  </>
                ) : (
                  <>
                    <Copy className="w-5 h-5" />
                    Clone Voice
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-4">
            <div className="bg-gray-900 rounded-lg border border-gray-800 p-4">
              <h3 className="text-lg font-semibold text-gray-200 mb-4">Settings</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Default Model
                  </label>
                  <select
                    value={elevenLabsStore.modelId}
                    onChange={(e) => {
                      const store = elevenLabsStore as any
                      store.modelId = e.target.value
                    }}
                    className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {MODELS.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* History */}
        {elevenLabsStore.history.length > 0 && activeTab === 'tts' && (
          <div className="bg-gray-900 rounded-lg border border-gray-800">
            <button
              onClick={() => toggleSection('history')}
              className="w-full flex items-center justify-between p-4 text-left"
            >
              <h3 className="text-lg font-semibold text-gray-200">
                History ({elevenLabsStore.history.length})
              </h3>
              {expandedSections.has('history') ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>

            {expandedSections.has('history') && (
              <div className="p-4 pt-0 space-y-2 border-t border-gray-800 max-h-96 overflow-y-auto">
                {elevenLabsStore.history.map((item, index) => (
                  <div
                    key={index}
                    className="p-3 bg-gray-800 rounded border border-gray-700 hover:border-gray-600 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-gray-200 truncate">{item.text}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {item.createdAt.toLocaleString()}
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => {
                            setText(item.text)
                            elevenLabsStore.setSelectedVoice(item.voiceId)
                            setActiveTab('tts')
                          }}
                          className="p-1 text-blue-400 hover:text-blue-300"
                          title="Use again"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                        <a
                          href={item.audioUrl}
                          download
                          className="p-1 text-gray-400 hover:text-gray-300"
                          title="Download"
                        >
                          <FileDown className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

