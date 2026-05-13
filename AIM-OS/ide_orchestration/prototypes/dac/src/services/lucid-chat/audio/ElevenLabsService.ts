/**
 * ElevenLabs API Service
 * Text-to-Speech (TTS) and voice synthesis
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

export interface ElevenLabsTTSRequest {
  text: string
  voice_id?: string // Default: '21m00Tcm4TlvDq8ikWAM'
  model_id?: string // Default: 'eleven_monolingual_v1'
  voice_settings?: {
    stability?: number // 0.0-1.0
    similarity_boost?: number // 0.0-1.0
    style?: number // 0.0-1.0
    use_speaker_boost?: boolean
  }
}

export interface ElevenLabsTTSResponse {
  audio: string // base64 encoded audio
  audio_url?: string // URL to audio file
  duration?: number // Duration in seconds
}

export interface ElevenLabsVoice {
  voice_id: string
  name: string
  category: string
  description?: string
  preview_url?: string
}

export class ElevenLabsService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('elevenlabs', 'https://api.elevenlabs.io/v1', apiKey)
  }

  isAvailable(): boolean {
    return !!this.apiKey
  }

  protected getDefaultHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    
    if (this.apiKey) {
      headers['xi-api-key'] = this.apiKey
    }
    
    return headers
  }

  async textToSpeech(
    request: ElevenLabsTTSRequest
  ): Promise<APIResponse<ElevenLabsTTSResponse>> {
    const voiceId = request.voice_id || '21m00Tcm4TlvDq8ikWAM'
    return this.handleRequest(
      async () => {
        const modelId = request.model_id || 'eleven_monolingual_v1'

        const response = await fetch(
          `${this.baseURL}/text-to-speech/${voiceId}`,
          {
            method: 'POST',
            headers: this.getDefaultHeaders(),
            body: JSON.stringify({
              text: request.text,
              model_id: modelId,
              voice_settings: request.voice_settings || {
                stability: 0.5,
                similarity_boost: 0.75,
              },
            }),
          }
        )

        if (!response.ok) {
          const error = await response.text()
          throw new Error(`ElevenLabs API Error: ${response.status} - ${error}`)
        }

        // ElevenLabs returns audio as binary data
        const audioBlob = await response.blob()
        const audioBase64 = await this.blobToBase64(audioBlob)

        return {
          audio: audioBase64,
          audio_url: URL.createObjectURL(audioBlob),
          duration: undefined, // Would need to calculate from audio
        }
      },
      `/text-to-speech/${voiceId}`,
      request
    )
  }

  async getVoices(): Promise<APIResponse<ElevenLabsVoice[]>> {
    return this.handleRequest(
      async () => {
        const response = await this.client.get<{ voices: ElevenLabsVoice[] }>(
          '/voices'
        )
        return response.voices
      },
      '/voices',
      {}
    )
  }

  async cloneVoice(
    name: string,
    files: File[],
    description?: string
  ): Promise<APIResponse<ElevenLabsVoice>> {
    return this.handleRequest(
      async () => {
        const formData = new FormData()
        formData.append('name', name)
        if (description) {
          formData.append('description', description)
        }
        
        files.forEach((file, index) => {
          formData.append(`files`, file)
        })

        const response = await fetch(`${this.baseURL}/voices/add`, {
          method: 'POST',
          headers: {
            'xi-api-key': this.apiKey!,
          },
          body: formData,
        })

        if (!response.ok) {
          const error = await response.text()
          throw new Error(`ElevenLabs API Error: ${response.status} - ${error}`)
        }

        return await response.json()
      },
      '/voices/add',
      { name, description, file_count: files.length }
    )
  }

  async deleteVoice(voiceId: string): Promise<APIResponse<void>> {
    return this.handleRequest(
      async () => {
        await this.client.delete(`/voices/${voiceId}`)
      },
      `/voices/${voiceId}`,
      { voiceId }
    )
  }

  async updateVoiceSettings(
    voiceId: string,
    settings: {
      stability?: number
      similarity_boost?: number
      style?: number
      use_speaker_boost?: boolean
    }
  ): Promise<APIResponse<void>> {
    return this.handleRequest(
      async () => {
        await this.client.post(`/voices/${voiceId}/settings`, settings)
      },
      `/voices/${voiceId}/settings`,
      { voiceId, settings }
    )
  }

  /**
   * Stream text-to-speech via WebSocket (for real-time playback)
   * Note: This is a placeholder - actual implementation requires WebSocket connection
   */
  async streamTextToSpeech(
    text: string,
    voiceId: string,
    onChunk: (chunk: Blob) => void
  ): Promise<void> {
    // TODO: Implement WebSocket streaming
    // For now, use regular TTS and simulate streaming
    const result = await this.textToSpeech({
      text,
      voice_id: voiceId,
    })
    
    if (result.success && result.data) {
      // Simulate streaming by chunking the audio
      const audioBlob = await fetch(result.data.audio_url!).then(r => r.blob())
      const chunkSize = 1024 * 4 // 4KB chunks
      
      for (let i = 0; i < audioBlob.size; i += chunkSize) {
        const chunk = audioBlob.slice(i, i + chunkSize)
        onChunk(chunk)
        await new Promise(resolve => setTimeout(resolve, 50)) // Simulate network delay
      }
    }
  }

  private async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64 = reader.result as string
        // Remove data URL prefix if present
        const base64Data = base64.includes(',') 
          ? base64.split(',')[1] 
          : base64
        resolve(base64Data)
      }
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }
}

