/**
 * Enhanced Audio Player Component
 * Audio playback with waveform visualization
 */

import React, { useRef, useEffect, useState } from 'react'
import { Play, Pause, Volume2, VolumeX, Download } from 'lucide-react'
import WaveSurfer from 'wavesurfer.js'

interface EnhancedAudioPlayerProps {
  audioUrl: string
  audioBlob?: Blob
  title?: string
  onPlay?: () => void
  onPause?: () => void
  onEnd?: () => void
}

export const EnhancedAudioPlayer: React.FC<EnhancedAudioPlayerProps> = ({
  audioUrl,
  audioBlob,
  title,
  onPlay,
  onPause,
  onEnd,
}) => {
  const waveformRef = useRef<HTMLDivElement>(null)
  const wavesurferRef = useRef<WaveSurfer | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [duration, setDuration] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!waveformRef.current) return

    // Initialize WaveSurfer
    const wavesurfer = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: '#4a90e2',
      progressColor: '#60a5fa',
      cursorColor: '#93c5fd',
      barWidth: 2,
      barRadius: 3,
      responsive: true,
      height: 100,
      normalize: true,
      backend: 'WebAudio',
      mediaControls: false,
    })

    wavesurferRef.current = wavesurfer

    // Load audio
    if (audioBlob) {
      const blobUrl = URL.createObjectURL(audioBlob)
      wavesurfer.load(blobUrl)
    } else {
      wavesurfer.load(audioUrl)
    }

    // Event listeners
    wavesurfer.on('ready', () => {
      setLoading(false)
      setDuration(wavesurfer.getDuration())
    })

    wavesurfer.on('play', () => {
      setIsPlaying(true)
      if (onPlay) onPlay()
    })

    wavesurfer.on('pause', () => {
      setIsPlaying(false)
      if (onPause) onPause()
    })

    wavesurfer.on('finish', () => {
      setIsPlaying(false)
      if (onEnd) onEnd()
    })

    wavesurfer.on('timeupdate', () => {
      setCurrentTime(wavesurfer.getCurrentTime())
    })

    // Cleanup
    return () => {
      wavesurfer.destroy()
    }
  }, [audioUrl, audioBlob, onPlay, onPause, onEnd])

  const handlePlayPause = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause()
    }
  }

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume)
    setIsMuted(newVolume === 0)
    if (wavesurferRef.current) {
      wavesurferRef.current.setVolume(newVolume)
    }
  }

  const handleMute = () => {
    if (isMuted) {
      handleVolumeChange(volume || 0.5)
    } else {
      handleVolumeChange(0)
    }
  }

  const handleDownload = () => {
    if (audioBlob) {
      const url = URL.createObjectURL(audioBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = title || 'audio.mp3'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } else {
      const a = document.createElement('a')
      a.href = audioUrl
      a.download = title || 'audio.mp3'
      a.click()
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="w-full bg-gray-800 rounded-lg p-4 space-y-3">
      {/* Title */}
      {title && (
        <div className="text-sm font-medium text-gray-200">{title}</div>
      )}

      {/* Waveform */}
      <div className="w-full">
        {loading ? (
          <div className="h-24 bg-gray-700 rounded flex items-center justify-center">
            <div className="text-sm text-gray-400">Loading waveform...</div>
          </div>
        ) : (
          <div ref={waveformRef} className="w-full" />
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        {/* Play/Pause */}
        <button
          onClick={handlePlayPause}
          disabled={loading}
          className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isPlaying ? (
            <Pause className="w-5 h-5" />
          ) : (
            <Play className="w-5 h-5" />
          )}
        </button>

        {/* Time Display */}
        <div className="text-xs text-gray-400 font-mono">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>

        {/* Volume Control */}
        <div className="flex items-center gap-2 flex-1">
          <button
            onClick={handleMute}
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
          >
            {isMuted ? (
              <VolumeX className="w-4 h-4" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        {/* Download */}
        <button
          onClick={handleDownload}
          className="p-2 text-gray-400 hover:text-gray-300 transition-colors"
          title="Download audio"
        >
          <Download className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

