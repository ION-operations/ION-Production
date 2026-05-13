/**
 * Test file for Lucid Chat API Services
 * Run tests as APIs are set up
 */

import { MeshyService } from './threeD/MeshyService'
import { PentopixService } from './threeD/PentopixService'
import { ThreeDService } from './threeD/ThreeDService'
import { ElevenLabsService } from './audio/ElevenLabsService'
import { AudioService } from './audio/AudioService'
import { MinimaxService } from './llm/MinimaxService'

/**
 * Test Meshy API
 */
export async function testMeshyAPI() {
  const meshy = new MeshyService()
  
  if (!meshy.isAvailable()) {
    console.warn('⚠️ Meshy API key not found. Set MESHY_API_KEY in .env')
    return false
  }

  console.log('🧪 Testing Meshy API...')
  
  try {
    const result = await meshy.textTo3D({
      prompt: 'A simple cube',
      mode: 'preview',
    })

    if (result.success) {
      console.log('✅ Meshy API test successful!', result.data)
      return true
    } else {
      console.error('❌ Meshy API test failed:', result.error)
      return false
    }
  } catch (error) {
    console.error('❌ Meshy API test error:', error)
    return false
  }
}

/**
 * Test Pentopix API
 */
export async function testPentopixAPI() {
  const pentopix = new PentopixService()
  
  if (!pentopix.isAvailable()) {
    console.warn('⚠️ Pentopix API key not found. Set PENTOPIX_API_KEY in .env')
    return false
  }

  console.log('🧪 Testing Pentopix API...')
  
  try {
    const result = await pentopix.generate3D({
      prompt: 'A simple cube',
      quality: 'medium',
    })

    if (result.success) {
      console.log('✅ Pentopix API test successful!', result.data)
      return true
    } else {
      console.error('❌ Pentopix API test failed:', result.error)
      return false
    }
  } catch (error) {
    console.error('❌ Pentopix API test error:', error)
    return false
  }
}

/**
 * Test unified 3D Service
 */
export async function testThreeDService() {
  const threeD = new ThreeDService()
  
  console.log('🧪 Testing unified 3D Service...')
  
  try {
    const result = await threeD.generate({
      prompt: 'A simple cube',
      provider: 'auto',
      mode: 'preview',
    })

    if (result.success) {
      console.log('✅ 3D Service test successful!', result.data)
      return true
    } else {
      console.error('❌ 3D Service test failed:', result.error)
      return false
    }
  } catch (error) {
    console.error('❌ 3D Service test error:', error)
    return false
  }
}

/**
 * Test Minimax API
 */
export async function testMinimaxAPI() {
  const minimax = new MinimaxService()
  
  if (!minimax.isAvailable()) {
    console.warn('⚠️ Minimax API key not found. Set MINIMAX_API_KEY in .env')
    return false
  }

  console.log('🧪 Testing Minimax API...')
  
  try {
    const result = await minimax.chatCompletion({
      model: 'abab5.5-chat',
      messages: [
        {
          role: 'user',
          content: 'Hello, this is a test message.',
        },
      ],
      max_tokens: 100,
    })

    if (result.success) {
      console.log('✅ Minimax API test successful!', result.data)
      return true
    } else {
      console.error('❌ Minimax API test failed:', result.error)
      return false
    }
  } catch (error) {
    console.error('❌ Minimax API test error:', error)
    return false
  }
}

/**
 * Run all API tests
 */
export async function runAPITests() {
  console.log('🚀 Running Lucid Chat API Tests...\n')
  
  const results = {
    meshy: await testMeshyAPI(),
    pentopix: await testPentopixAPI(),
    elevenlabs: await testElevenLabsAPI(),
    minimax: await testMinimaxAPI(),
    threeD: await testThreeDService(),
    audio: await testAudioService(),
  }

  console.log('\n📊 Test Results:')
  console.log(`Meshy: ${results.meshy ? '✅' : '❌'}`)
  console.log(`Pentopix: ${results.pentopix ? '✅' : '❌'}`)
  console.log(`ElevenLabs: ${results.elevenlabs ? '✅' : '❌'}`)
  console.log(`Minimax: ${results.minimax ? '✅' : '❌'}`)
  console.log(`3D Service: ${results.threeD ? '✅' : '❌'}`)
  console.log(`Audio Service: ${results.audio ? '✅' : '❌'}`)

  return results
}

