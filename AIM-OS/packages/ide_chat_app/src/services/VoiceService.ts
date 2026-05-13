/**
 * Voice Service
 * Handles Text-to-Speech (TTS) and Speech-to-Text (SST) integration
 * 
 * Created: 2025-10-30
 * Agent: Lexicon
 */

import { aimosService } from './AIMOSService'

export interface VoiceConfig {
  enabled: boolean
  tts_enabled: boolean
  sst_enabled: boolean
  voice_id?: string
  rate?: number
  pitch?: number
  volume?: number
  auto_speak?: boolean
  language?: string
}

export interface VoiceSession {
  session_id: string
  started_at: string
  transcripts: Array<{
    text: string
    confidence: number
    timestamp: string
  }>
  audio_chunks: Blob[]
}

class VoiceService {
  private config: VoiceConfig = {
    enabled: true,
    tts_enabled: true,
    sst_enabled: true,
    rate: 1.0,
    pitch: 1.0,
    volume: 1.0,
    auto_speak: false,
    language: 'en-US'
  }

  private currentSession: VoiceSession | null = null
  private isRecording: boolean = false
  private mediaRecorder: MediaRecorder | null = null
  private audioChunks: Blob[] = []

  /**
   * Initialize voice service
   */
  async initialize(): Promise<boolean> {
    if (!aimosService.isVoiceAvailable()) {
      console.warn('Voice I/O not available')
      return false
    }

    // Load config from localStorage
    const savedConfig = localStorage.getItem('voice_config')
    if (savedConfig) {
      try {
        this.config = { ...this.config, ...JSON.parse(savedConfig) }
      } catch (error) {
        console.error('Failed to load voice config:', error)
      }
    }

    return true
  }

  /**
   * Start recording audio for SST
   */
  async startRecording(): Promise<VoiceSession> {
    if (this.isRecording) {
      throw new Error('Already recording')
    }

    if (!this.config.sst_enabled) {
      throw new Error('Speech-to-text is disabled')
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      this.mediaRecorder = new MediaRecorder(stream)
      this.audioChunks = []

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data)
        }
      }

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' })
        if (this.currentSession) {
          this.currentSession.audio_chunks.push(audioBlob)
        }
      }

      this.currentSession = {
        session_id: `voice_${Date.now()}`,
        started_at: new Date().toISOString(),
        transcripts: [],
        audio_chunks: []
      }

      this.isRecording = true
      this.mediaRecorder.start()

      return this.currentSession
    } catch (error) {
      console.error('Failed to start recording:', error)
      throw error
    }
  }

  /**
   * Stop recording and get transcript
   */
  async stopRecording(): Promise<string> {
    if (!this.isRecording || !this.mediaRecorder) {
      throw new Error('Not recording')
    }

    return new Promise((resolve, reject) => {
      this.mediaRecorder!.onstop = async () => {
        try {
          // Use AIM-OS service for transcription
          const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' })
          const transcript = await aimosService.speechToText(audioBlob)

          if (this.currentSession) {
            this.currentSession.transcripts.push({
              text: transcript.text,
              confidence: transcript.confidence,
              timestamp: transcript.timestamp
            })
          }

          this.isRecording = false
          this.audioChunks = []

          // Stop media stream
          if (this.mediaRecorder?.stream) {
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop())
          }

          resolve(transcript.text)
        } catch (error) {
          reject(error)
        }
      }

      this.mediaRecorder!.stop()
    })
  }

  /**
   * Speak text using TTS
   */
  async speak(text: string, options?: Partial<VoiceConfig>): Promise<void> {
    if (!this.config.tts_enabled) {
      console.warn('Text-to-speech is disabled')
      return
    }

    try {
      await aimosService.textToSpeech(text, {
        voice: options?.voice_id || this.config.voice_id,
        rate: options?.rate || this.config.rate,
        pitch: options?.pitch || this.config.pitch,
        volume: options?.volume || this.config.volume
      })
    } catch (error) {
      console.error('Failed to speak text:', error)
      throw error
    }
  }

  /**
   * Get available voices
   */
  getAvailableVoices(): SpeechSynthesisVoice[] {
    return aimosService.getAvailableVoices()
  }

  /**
   * Update voice configuration
   */
  updateConfig(config: Partial<VoiceConfig>): void {
    this.config = { ...this.config, ...config }
    localStorage.setItem('voice_config', JSON.stringify(this.config))
  }

  /**
   * Get current configuration
   */
  getConfig(): VoiceConfig {
    return { ...this.config }
  }

  /**
   * Check if recording
   */
  isCurrentlyRecording(): boolean {
    return this.isRecording
  }

  /**
   * Get current session
   */
  getCurrentSession(): VoiceSession | null {
    return this.currentSession
  }
}

// Export singleton instance
export const voiceService = new VoiceService()
export default VoiceService

