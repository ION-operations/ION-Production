/**
 * Unit Tests: DAGExecutor
 * 
 * Tests for DAG execution with parallel processing
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { DAGExecutor, DAGNode } from '@services/lucid-chat/orchestration'

describe('DAGExecutor', () => {
  let executor: DAGExecutor

  beforeEach(() => {
    executor = new DAGExecutor()
  })

  describe('execute - single node', () => {
    it('should execute single node without dependencies', async () => {
      const nodes: DAGNode[] = [
        {
          id: 'node1',
          role: 'test',
          input: { value: 1 },
          dependencies: [],
          status: 'pending'
        }
      ]

      const result = await executor.execute(nodes, async (node) => {
        return { output: node.input.value * 2 }
      })

      expect(result.success).toBe(true)
      expect(result.results.size).toBe(1)
      expect(result.results.get('node1')).toEqual({ output: 2 })
      expect(result.errors.size).toBe(0)
    })
  })

  describe('execute - linear DAG', () => {
    it('should execute nodes in dependency order', async () => {
      const nodes: DAGNode[] = [
        {
          id: 'node1',
          role: 'test',
          input: { value: 1 },
          dependencies: [],
          status: 'pending'
        },
        {
          id: 'node2',
          role: 'test',
          input: { value: 2 },
          dependencies: ['node1'],
          status: 'pending'
        },
        {
          id: 'node3',
          role: 'test',
          input: { value: 3 },
          dependencies: ['node2'],
          status: 'pending'
        }
      ]

      const executionOrder: string[] = []
      const result = await executor.execute(nodes, async (node) => {
        executionOrder.push(node.id)
        return { output: node.input.value }
      })

      expect(result.success).toBe(true)
      expect(executionOrder).toEqual(['node1', 'node2', 'node3'])
    })
  })

  describe('execute - parallel nodes', () => {
    it('should execute independent nodes in parallel', async () => {
      const nodes: DAGNode[] = [
        {
          id: 'node1',
          role: 'test',
          input: { value: 1 },
          dependencies: [],
          status: 'pending'
        },
        {
          id: 'node2',
          role: 'test',
          input: { value: 2 },
          dependencies: [],
          status: 'pending'
        },
        {
          id: 'node3',
          role: 'test',
          input: { value: 3 },
          dependencies: [],
          status: 'pending'
        }
      ]

      const startTimes = new Map<string, number>()
      const result = await executor.execute(nodes, async (node) => {
        startTimes.set(node.id, Date.now())
        await new Promise(resolve => setTimeout(resolve, 50)) // Simulate work
        return { output: node.input.value }
      })

      expect(result.success).toBe(true)
      expect(result.results.size).toBe(3)
      
      // Check that nodes started around the same time (parallel execution)
      const times = Array.from(startTimes.values())
      const maxTime = Math.max(...times)
      const minTime = Math.min(...times)
      expect(maxTime - minTime).toBeLessThan(20) // Should start within 20ms
    })
  })

  describe('execute - complex DAG', () => {
    it('should handle complex dependency graph', async () => {
      // node1 -> node2, node3
      // node2 -> node4
      // node3 -> node4
      // node4 -> node5
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: [], status: 'pending' },
        { id: 'node2', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' },
        { id: 'node3', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' },
        { id: 'node4', role: 'test', input: {}, dependencies: ['node2', 'node3'], status: 'pending' },
        { id: 'node5', role: 'test', input: {}, dependencies: ['node4'], status: 'pending' }
      ]

      const executionOrder: string[] = []
      const result = await executor.execute(nodes, async (node) => {
        executionOrder.push(node.id)
        return { output: node.id }
      })

      expect(result.success).toBe(true)
      expect(result.results.size).toBe(5)
      
      // node1 must come first
      expect(executionOrder[0]).toBe('node1')
      // node2 and node3 can be in any order (parallel)
      expect(executionOrder.slice(1, 3).sort()).toEqual(['node2', 'node3'])
      // node4 must come after node2 and node3
      expect(executionOrder.indexOf('node4')).toBeGreaterThan(executionOrder.indexOf('node2'))
      expect(executionOrder.indexOf('node4')).toBeGreaterThan(executionOrder.indexOf('node3'))
      // node5 must come last
      expect(executionOrder[executionOrder.length - 1]).toBe('node5')
    })
  })

  describe('cycle detection', () => {
    it('should throw error for cycle', async () => {
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: ['node2'], status: 'pending' },
        { id: 'node2', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' }
      ]

      await expect(
        executor.execute(nodes, async (node) => ({ output: node.id }))
      ).rejects.toThrow('Cycle detected')
    })

    it('should throw error for self-loop', async () => {
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' }
      ]

      await expect(
        executor.execute(nodes, async (node) => ({ output: node.id }))
      ).rejects.toThrow('Cycle detected')
    })
  })

  describe('error handling', () => {
    it('should handle node execution errors', async () => {
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: [], status: 'pending' },
        { id: 'node2', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' }
      ]

      const result = await executor.execute(nodes, async (node) => {
        if (node.id === 'node1') {
          throw new Error('Node 1 failed')
        }
        return { output: node.id }
      })

      expect(result.success).toBe(false)
      expect(result.errors.size).toBe(1)
      expect(result.errors.get('node1')).toContain('Node 1 failed')
      // node2 should be skipped because node1 failed
      expect(result.results.size).toBe(0)
    })

    it('should continue execution when one node fails', async () => {
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: [], status: 'pending' },
        { id: 'node2', role: 'test', input: {}, dependencies: [], status: 'pending' },
        { id: 'node3', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' }
      ]

      const result = await executor.execute(nodes, async (node) => {
        if (node.id === 'node1') {
          throw new Error('Node 1 failed')
        }
        return { output: node.id }
      })

      expect(result.success).toBe(false)
      expect(result.errors.size).toBe(1)
      expect(result.results.size).toBe(1) // node2 should succeed
      expect(result.results.get('node2')).toBeDefined()
    })
  })

  describe('execution timing', () => {
    it('should track execution time', async () => {
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: [], status: 'pending' }
      ]

      const result = await executor.execute(nodes, async (node) => {
        await new Promise(resolve => setTimeout(resolve, 50))
        return { output: node.id }
      })

      expect(result.totalTime).toBeGreaterThan(40)
      expect(result.totalTime).toBeLessThan(200)
      expect(result.nodeExecutionTimes.size).toBe(1)
      expect(result.nodeExecutionTimes.get('node1')).toBeGreaterThan(40)
    })
  })

  describe('empty DAG', () => {
    it('should handle empty node array', async () => {
      const result = await executor.execute([], async (node) => ({ output: node.id }))
      
      expect(result.success).toBe(true)
      expect(result.results.size).toBe(0)
      expect(result.errors.size).toBe(0)
    })
  })

  describe('missing dependencies', () => {
    it('should handle missing dependency gracefully', async () => {
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: ['missing'], status: 'pending' }
      ]

      await expect(
        executor.execute(nodes, async (node) => ({ output: node.id }))
      ).rejects.toThrow()
    })
  })
})

