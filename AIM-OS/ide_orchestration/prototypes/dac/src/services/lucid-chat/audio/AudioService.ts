/**
 * Audio Service - Unified interface for all audio APIs
 */

import { ElevenLabsService, ElevenLabsTTSRequest } from './ElevenLabsService'
import { APIResponse } from '../base/BaseAPIService'

export interface TTSRequest {
  text: string
  voice?: string
  provider?: 'elevenlabs' | 'google' | 'openai' | 'auto'
  speed?: number // 0.5-2.0
  pitch?: number // -20 to +20 semitones
}

export interface TTSResponse {
  audio: string // base64 encoded audio
  audio_url?: string // URL to audio file
  provider: string
  duration?: number
}

export class AudioService {
  private elevenlabs: ElevenLabsService

  constructor() {
    this.elevenlabs = new ElevenLabsService()
  }

  async textToSpeech(request: TTSRequest): Promise<APIResponse<TTSResponse>> {
    const provider = request.provider || this.selectProvider()

    if (provider === 'elevenlabs' && this.elevenlabs.isAvailable()) {
      const result = await this.elevenlabs.textToSpeech({
        text: request.text,
        voice_id: request.voice,
      })

      if (!result.success || !result.data) {
        return result as APIResponse<TTSResponse>
      }

      return {
        success: true,
        data: {
          audio: result.data.audio,
          audio_url: result.data.audio_url,
          provider: 'elevenlabs',
          duration: result.data.duration,
        },
        metadata: result.metadata,
      }
    }

    return {
      success: false,
      error: 'No TTS service available',
    }
  }

  private selectProvider(): 'elevenlabs' | 'google' | 'openai' {
    if (this.elevenlabs.isAvailable()) return 'elevenlabs'
    // TODO: Add other providers
    return 'elevenlabs'
  }

  async getAvailableVoices(provider?: 'elevenlabs'): Promise<APIResponse<any[]>> {
    if (provider === 'elevenlabs' || !provider) {
      return await this.elevenlabs.getVoices()
    }
    return { success: false, error: 'Provider not supported' }
  }
}

