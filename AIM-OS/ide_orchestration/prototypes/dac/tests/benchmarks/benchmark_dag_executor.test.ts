/**
 * Performance Benchmarks: DAGExecutor
 * 
 * Benchmarks for DAG execution performance
 */

import { describe, it, expect } from 'vitest'
import { DAGExecutor, DAGNode } from '@services/lucid-chat/orchestration'

describe('DAGExecutor Performance Benchmarks', () => {
  describe('single node execution', () => {
    it('should execute single node in <10ms', async () => {
      const nodes: DAGNode[] = [
        {
          id: 'node1',
          role: 'test',
          input: { value: 1 },
          dependencies: [],
          status: 'pending'
        }
      ]

      const startTime = performance.now()
      const result = await new DAGExecutor().execute(nodes, async (node) => {
        return { output: node.input.value }
      })
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(duration).toBeLessThan(10) // <10ms
      console.log(`[Benchmark] DAGExecutor single node: ${duration.toFixed(3)}ms`)
    })
  })

  describe('parallel execution - 10 nodes', () => {
    it('should execute 10 independent nodes in <100ms', async () => {
      const nodes: DAGNode[] = Array.from({ length: 10 }, (_, i) => ({
        id: `node${i + 1}`,
        role: 'test',
        input: { value: i },
        dependencies: [],
        status: 'pending'
      }))

      const startTime = performance.now()
      const result = await new DAGExecutor().execute(nodes, async (node) => {
        await new Promise(resolve => setTimeout(resolve, 5)) // Simulate 5ms work
        return { output: node.input.value }
      })
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(result.results.size).toBe(10)
      expect(duration).toBeLessThan(100) // <100ms (parallel execution)
      console.log(`[Benchmark] DAGExecutor 10 nodes (parallel): ${duration.toFixed(3)}ms`)
    })
  })

  describe('parallel execution - 100 nodes', () => {
    it('should execute 100 independent nodes in <1000ms', async () => {
      const nodes: DAGNode[] = Array.from({ length: 100 }, (_, i) => ({
        id: `node${i + 1}`,
        role: 'test',
        input: { value: i },
        dependencies: [],
        status: 'pending'
      }))

      const startTime = performance.now()
      const result = await new DAGExecutor().execute(nodes, async (node) => {
        await new Promise(resolve => setTimeout(resolve, 5)) // Simulate 5ms work
        return { output: node.input.value }
      })
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(result.results.size).toBe(100)
      expect(duration).toBeLessThan(1000) // <1000ms (parallel execution)
      console.log(`[Benchmark] DAGExecutor 100 nodes (parallel): ${duration.toFixed(3)}ms`)
    })
  })

  describe('complex DAG execution', () => {
    it('should execute complex DAG efficiently', async () => {
      // Create DAG: node1 -> node2, node3 -> node4
      const nodes: DAGNode[] = [
        { id: 'node1', role: 'test', input: {}, dependencies: [], status: 'pending' },
        { id: 'node2', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' },
        { id: 'node3', role: 'test', input: {}, dependencies: ['node1'], status: 'pending' },
        { id: 'node4', role: 'test', input: {}, dependencies: ['node2', 'node3'], status: 'pending' }
      ]

      const startTime = performance.now()
      const result = await new DAGExecutor().execute(nodes, async (node) => {
        await new Promise(resolve => setTimeout(resolve, 10)) // Simulate 10ms work
        return { output: node.id }
      })
      const endTime = performance.now()
      const duration = endTime - startTime

      expect(result.success).toBe(true)
      expect(result.results.size).toBe(4)
      // Parallel execution: node2 and node3 should run in parallel
      expect(duration).toBeLessThan(50) // <50ms (parallel execution)
      console.log(`[Benchmark] DAGExecutor complex DAG: ${duration.toFixed(3)}ms`)
    })
  })
})

