/**
 * Command Server Connectivity Test Script
 * Tests Command Server health and priority MCP tools
 * 
 * Usage: npx ts-node scripts/test-command-server.ts
 */

import { 
  testCommandServerHealth, 
  listAvailableMCPTools, 
  testAllPriorityMCPTools 
} from '../src/services/__tests__/MCPService.test'

async function main() {
  console.log('🚀 Starting Command Server Connectivity Tests...\n')
  console.log('=' .repeat(60))
  console.log('')

  try {
    // Test 1: Health check
    console.log('📋 Test 1: Command Server Health Check')
    console.log('-'.repeat(60))
    await testCommandServerHealth()
    console.log('')
    
    // Test 2: List available tools
    console.log('📋 Test 2: List Available MCP Tools')
    console.log('-'.repeat(60))
    await listAvailableMCPTools()
    console.log('')
    
    // Test 3: Test priority tools
    console.log('📋 Test 3: Test Priority MCP Tools')
    console.log('-'.repeat(60))
    await testAllPriorityMCPTools()
    
    console.log('')
    console.log('='.repeat(60))
    console.log('✅ All tests passed! Command Server is operational.')
    console.log('')
    
    process.exit(0)
  } catch (error) {
    console.error('')
    console.error('='.repeat(60))
    console.error('❌ Tests failed!')
    console.error('')
    console.error('Error details:')
    console.error(error instanceof Error ? error.message : String(error))
    console.error('')
    console.error('Troubleshooting:')
    console.error('1. Ensure Command Server is running on http://localhost:5001')
    console.error('2. Check Command Server logs for errors')
    console.error('3. Verify MCP server is connected to Command Server')
    console.error('')
    
    process.exit(1)
  }
}

// Run tests
main().catch(error => {
  console.error('Fatal error:', error)
  process.exit(1)
})

