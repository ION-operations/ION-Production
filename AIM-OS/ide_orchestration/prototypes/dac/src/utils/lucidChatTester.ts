/**
 * Simple test component for Lucid Chat APIs
 * Can be imported and used in React components
 */

import { testMeshyAPI, testElevenLabsAPI, runAPITests } from '../services/lucid-chat/test'

export const LucidChatAPITester = {
  /**
   * Test Meshy 3D API
   */
  async testMeshy() {
    return await testMeshyAPI()
  },

  /**
   * Test ElevenLabs TTS API
   */
  async testElevenLabs() {
    return await testElevenLabsAPI()
  },

  /**
   * Run all API tests
   */
  async testAll() {
    return await runAPITests()
  },
}

// Example usage in console:
// import { LucidChatAPITester } from './utils/lucidChatTester'
// await LucidChatAPITester.testMeshy()
// await LucidChatAPITester.testElevenLabs()
// await LucidChatAPITester.testAll()

