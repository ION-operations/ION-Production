/**
 * MCP Service Test Utility
 * Tests Command Server connectivity and MCP tools
 * Run this to verify backend integration
 */

import { mcpService, MCPService } from '../MCPService'

/**
 * Test Command Server health
 */
export async function testCommandServerHealth(): Promise<void> {
  console.log('🔍 Testing Command Server health...')
  
  const health = await mcpService.checkHealth()
  
  if (health.status === 'ok') {
    console.log('✅ Command Server is healthy')
    console.log(`   Port: ${health.port}`)
    console.log(`   Message: ${health.message}`)
  } else {
    console.error('❌ Command Server health check failed')
    console.error(`   Error: ${health.message}`)
    throw new Error(`Command Server unavailable: ${health.message}`)
  }
}

/**
 * Test MCP tool execution
 */
export async function testMCPTool(
  tool: string,
  arguments_: Record<string, any> = {}
): Promise<void> {
  console.log(`🔍 Testing MCP tool: ${tool}...`)
  
  const result = await mcpService.executeTool(tool, arguments_)
  
  if (result.success) {
    console.log(`✅ ${tool} executed successfully`)
    console.log(`   Result:`, JSON.stringify(result.result, null, 2))
  } else {
    console.error(`❌ ${tool} execution failed`)
    console.error(`   Error: ${result.error}`)
    throw new Error(`MCP tool ${tool} failed: ${result.error}`)
  }
}

/**
 * Test all priority MCP tools
 */
export async function testAllPriorityMCPTools(): Promise<void> {
  console.log('🧪 Testing all priority MCP tools...\n')

  const tests = [
    {
      tool: 'mcp_lucid-mcp_store_memory',
      args: {
        content: 'Test memory storage from Alex',
        tags: { test: 1.0, alex: 1.0 },
        metadata: { source: 'alex_test' }
      }
    },
    {
      tool: 'mcp_lucid-mcp_retrieve_memory',
      args: {
        query: 'test',
        limit: 5
      }
    },
    {
      tool: 'mcp_lucid-mcp_track_confidence',
      args: {
        model_id: 'test_model',
        confidence_score: 0.85,
        task_criticality: 'routine'
      }
    },
    {
      tool: 'mcp_lucid-mcp_create_plan',
      args: {
        goal: 'Test plan creation',
        context: 'Testing from Alex',
        priority: 'medium'
      }
    },
    {
      tool: 'mcp_lucid-mcp_synthesize_knowledge',
      args: {
        query: 'test knowledge synthesis',
        limit: 5
      }
    },
    {
      tool: 'mcp_lucid-mcp_add_timeline_entry',
      args: {
        entry_type: 'test',
        content: 'Test timeline entry from Alex',
        metadata: { source: 'alex_test' }
      }
    },
    {
      tool: 'mcp_lucid-mcp_get_timeline_summary',
      args: {
        limit: 10
      }
    },
    {
      tool: 'mcp_lucid-mcp_get_consciousness_metrics',
      args: {}
    }
  ]

  const results: Array<{ tool: string; success: boolean; error?: string }> = []

  for (const test of tests) {
    try {
      await testMCPTool(test.tool, test.args)
      results.push({ tool: test.tool, success: true })
    } catch (error) {
      results.push({
        tool: test.tool,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    }
    console.log('') // Empty line between tests
  }

  // Summary
  console.log('📊 Test Summary:')
  const successCount = results.filter(r => r.success).length
  const failureCount = results.filter(r => !r.success).length
  console.log(`   ✅ Passed: ${successCount}/${results.length}`)
  console.log(`   ❌ Failed: ${failureCount}/${results.length}`)

  if (failureCount > 0) {
    console.log('\n❌ Failed Tests:')
    results
      .filter(r => !r.success)
      .forEach(r => {
        console.log(`   - ${r.tool}: ${r.error}`)
      })
  }

  if (failureCount > 0) {
    throw new Error(`${failureCount} MCP tool tests failed`)
  }
}

/**
 * List available MCP tools
 */
export async function listAvailableMCPTools(): Promise<void> {
  console.log('📋 Listing available MCP tools...\n')
  
  const result = await mcpService.listTools()
  
  if (result.success && result.tools) {
    console.log(`✅ Found ${result.tools.length} MCP tools:`)
    result.tools.forEach(tool => {
      console.log(`   - ${tool}`)
    })
  } else {
    console.error('❌ Failed to list MCP tools')
    console.error(`   Error: ${result.error}`)
    throw new Error(`Failed to list MCP tools: ${result.error}`)
  }
}

/**
 * Run all tests
 */
export async function runAllTests(): Promise<void> {
  console.log('🚀 Starting MCP Service Tests...\n')
  
  try {
    // Test 1: Health check
    await testCommandServerHealth()
    console.log('')
    
    // Test 2: List tools
    await listAvailableMCPTools()
    console.log('')
    
    // Test 3: Test priority tools
    await testAllPriorityMCPTools()
    
    console.log('\n✅ All tests passed!')
  } catch (error) {
    console.error('\n❌ Tests failed!')
    console.error(error)
    throw error
  }
}

// Export for use in other files
export { mcpService }

