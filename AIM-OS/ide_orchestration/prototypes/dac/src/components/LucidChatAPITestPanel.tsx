import React, { useState } from 'react'
import { testMeshyAPI, testElevenLabsAPI, runAPITests } from '../services/lucid-chat/test'
import { MeshyService } from '../services/lucid-chat/threeD/MeshyService'
import { ElevenLabsService } from '../services/lucid-chat/audio/ElevenLabsService'
import { ThreeDService } from '../services/lucid-chat/threeD/ThreeDService'
import { AudioService } from '../services/lucid-chat/audio/AudioService'

/**
 * Lucid Chat API Test Panel
 * Test all integrated APIs
 */
export const LucidChatAPITestPanel: React.FC = () => {
  const [testResults, setTestResults] = useState<Record<string, boolean | null>>({})
  const [testing, setTesting] = useState(false)
  const [logs, setLogs] = useState<string[]>([])

  const addLog = (message: string) => {
    setLogs((prev) => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const testMeshy = async () => {
    setTesting(true)
    addLog('Testing Meshy API...')
    try {
      const meshy = new MeshyService()
      if (!meshy.isAvailable()) {
        addLog('⚠️ Meshy API key not found')
        setTestResults((prev) => ({ ...prev, meshy: false }))
        return
      }

      const result = await meshy.textTo3D({
        prompt: 'A simple cube',
        mode: 'preview',
      })

      if (result.success) {
        addLog(`✅ Meshy API test successful! Task ID: ${result.data?.task_id}`)
        setTestResults((prev) => ({ ...prev, meshy: true }))
      } else {
        addLog(`❌ Meshy API test failed: ${result.error}`)
        setTestResults((prev) => ({ ...prev, meshy: false }))
      }
    } catch (error: any) {
      addLog(`❌ Meshy API error: ${error.message}`)
      setTestResults((prev) => ({ ...prev, meshy: false }))
    } finally {
      setTesting(false)
    }
  }

  const testElevenLabs = async () => {
    setTesting(true)
    addLog('Testing ElevenLabs API...')
    try {
      const elevenlabs = new ElevenLabsService()
      if (!elevenlabs.isAvailable()) {
        addLog('⚠️ ElevenLabs API key not found')
        setTestResults((prev) => ({ ...prev, elevenlabs: false }))
        return
      }

      const voicesResult = await elevenlabs.getVoices()
      if (voicesResult.success && voicesResult.data) {
        addLog(`✅ ElevenLabs API test successful! ${voicesResult.data.length} voices available`)
        setTestResults((prev) => ({ ...prev, elevenlabs: true }))
      } else {
        addLog(`❌ ElevenLabs API test failed: ${voicesResult.error}`)
        setTestResults((prev) => ({ ...prev, elevenlabs: false }))
      }
    } catch (error: any) {
      addLog(`❌ ElevenLabs API error: ${error.message}`)
      setTestResults((prev) => ({ ...prev, elevenlabs: false }))
    } finally {
      setTesting(false)
    }
  }

  const testAll = async () => {
    setTesting(true)
    setLogs([])
    addLog('🚀 Running all API tests...')
    
    await testMeshy()
    await testElevenLabs()
    
    addLog('✅ All tests complete!')
    setTesting(false)
  }

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold">Lucid Chat API Tests</h2>
      
      <div className="flex gap-2">
        <button
          onClick={testMeshy}
          disabled={testing}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          Test Meshy
        </button>
        <button
          onClick={testElevenLabs}
          disabled={testing}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          Test ElevenLabs
        </button>
        <button
          onClick={testAll}
          disabled={testing}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
        >
          Test All
        </button>
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold">Test Results:</h3>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span>Meshy:</span>
            {testResults.meshy === true && <span className="text-green-500">✅</span>}
            {testResults.meshy === false && <span className="text-red-500">❌</span>}
            {testResults.meshy === null && <span className="text-gray-500">-</span>}
          </div>
          <div className="flex items-center gap-2">
            <span>ElevenLabs:</span>
            {testResults.elevenlabs === true && <span className="text-green-500">✅</span>}
            {testResults.elevenlabs === false && <span className="text-red-500">❌</span>}
            {testResults.elevenlabs === null && <span className="text-gray-500">-</span>}
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold">Logs:</h3>
        <div className="bg-gray-900 p-3 rounded font-mono text-sm max-h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <div className="text-gray-500">No logs yet. Click a test button to start.</div>
          ) : (
            logs.map((log, i) => (
              <div key={i} className="text-gray-300">
                {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

