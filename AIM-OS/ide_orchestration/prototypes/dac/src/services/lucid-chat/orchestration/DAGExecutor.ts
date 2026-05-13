/**
 * DAG Executor - Directed Acyclic Graph execution engine
 * 
 * Enables parallel execution of APOE workflows with dependency management
 */

export type NodeStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

export interface DAGNode {
  id: string
  role: string
  input: any
  dependencies: string[] // IDs of nodes this depends on
  status: NodeStatus
  result?: any
  error?: string
  startTime?: number
  endTime?: number
}

export interface DAGGraph {
  nodes: Map<string, DAGNode>
  executionOrder: string[]
  inProgress: Set<string>
  completed: Set<string>
  failed: Set<string>
}

export interface DAGExecutionResult {
  success: boolean
  results: Map<string, any>
  errors: Map<string, string>
  totalTime: number
  nodeExecutionTimes: Map<string, number>
}

export class DAGExecutor {
  /**
   * Execute DAG with parallel execution where possible
   */
  async execute(
    nodes: DAGNode[],
    executor: (node: DAGNode) => Promise<any>
  ): Promise<DAGExecutionResult> {
    const startTime = Date.now()
    
    // Build graph
    const graph = this.buildGraph(nodes)
    
    // Validate (detect cycles)
    this.validateDAG(graph)
    
    // Compute execution order
    graph.executionOrder = this.topologicalSort(graph)
    
    // Execute with parallelism
    await this.executeDAG(graph, executor)
    
    // Build result
    return {
      success: graph.failed.size === 0,
      results: new Map(
        Array.from(graph.nodes.entries())
          .filter(([_, node]) => node.status === 'completed')
          .map(([id, node]) => [id, node.result])
      ),
      errors: new Map(
        Array.from(graph.nodes.entries())
          .filter(([_, node]) => node.status === 'failed')
          .map(([id, node]) => [id, node.error!])
      ),
      totalTime: Date.now() - startTime,
      nodeExecutionTimes: new Map(
        Array.from(graph.nodes.values())
          .filter(node => node.startTime && node.endTime)
          .map(node => [node.id, node.endTime! - node.startTime!])
      ),
    }
  }

  /**
   * Build graph from nodes
   */
  private buildGraph(nodes: DAGNode[]): DAGGraph {
    const graph: DAGGraph = {
      nodes: new Map(),
      executionOrder: [],
      inProgress: new Set(),
      completed: new Set(),
      failed: new Set(),
    }
    
    for (const node of nodes) {
      graph.nodes.set(node.id, node)
    }
    
    return graph
  }

  /**
   * Validate DAG has no cycles
   */
  private validateDAG(graph: DAGGraph): void {
    const visited = new Set<string>()
    const recursionStack = new Set<string>()
    
    const hasCycle = (nodeId: string): boolean => {
      visited.add(nodeId)
      recursionStack.add(nodeId)
      
      const node = graph.nodes.get(nodeId)!
      
      for (const depId of node.dependencies) {
        if (!visited.has(depId)) {
          if (hasCycle(depId)) return true
        } else if (recursionStack.has(depId)) {
          return true // Cycle detected
        }
      }
      
      recursionStack.delete(nodeId)
      return false
    }
    
    for (const nodeId of graph.nodes.keys()) {
      if (!visited.has(nodeId)) {
        if (hasCycle(nodeId)) {
          throw new Error('Cycle detected in DAG')
        }
      }
    }
  }

  /**
   * Topological sort using Kahn's algorithm
   */
  private topologicalSort(graph: DAGGraph): string[] {
    const inDegree = new Map<string, number>()
    const sorted: string[] = []
    const queue: string[] = []
    
    // Calculate in-degrees
    for (const [nodeId, node] of graph.nodes) {
      inDegree.set(nodeId, node.dependencies.length)
      
      if (node.dependencies.length === 0) {
        queue.push(nodeId)
      }
    }
    
    // Process queue
    while (queue.length > 0) {
      const nodeId = queue.shift()!
      sorted.push(nodeId)
      
      // Find dependents (nodes that depend on this one)
      for (const [otherId, otherNode] of graph.nodes) {
        if (otherNode.dependencies.includes(nodeId)) {
          const degree = inDegree.get(otherId)! - 1
          inDegree.set(otherId, degree)
          
          if (degree === 0) {
            queue.push(otherId)
          }
        }
      }
    }
    
    // Check all nodes were sorted
    if (sorted.length !== graph.nodes.size) {
      throw new Error('Cycle detected in DAG (topological sort incomplete)')
    }
    
    return sorted
  }

  /**
   * Execute DAG with parallel execution
   */
  private async executeDAG(
    graph: DAGGraph,
    executor: (node: DAGNode) => Promise<any>
  ): Promise<void> {
    while (!this.isComplete(graph)) {
      // Find nodes ready to execute
      const ready = this.getReadyNodes(graph)
      
      if (ready.length === 0 && !this.isComplete(graph)) {
        // Deadlock detection
        const pending = Array.from(graph.nodes.values())
          .filter(n => n.status === 'pending')
        
        if (pending.length > 0) {
          throw new Error(
            `Deadlock detected: ${pending.length} nodes pending but none ready. ` +
            `Nodes: ${pending.map(n => n.id).join(', ')}`
          )
        }
        
        break
      }
      
      // Execute ready nodes in parallel
      await this.executeParallel(ready, graph, executor)
    }
  }

  /**
   * Get nodes ready to execute (dependencies satisfied)
   */
  private getReadyNodes(graph: DAGGraph): DAGNode[] {
    const ready: DAGNode[] = []
    
    for (const node of graph.nodes.values()) {
      if (node.status !== 'pending') continue
      
      // Check if all dependencies are completed
      const allDepsCompleted = node.dependencies.every(depId => {
        const dep = graph.nodes.get(depId)
        return dep && dep.status === 'completed'
      })
      
      // Check if any dependency failed
      const anyDepFailed = node.dependencies.some(depId => {
        const dep = graph.nodes.get(depId)
        return dep && dep.status === 'failed'
      })
      
      if (anyDepFailed) {
        // Skip node if dependency failed
        node.status = 'skipped'
        node.error = 'Dependency failed'
      } else if (allDepsCompleted) {
        ready.push(node)
      }
    }
    
    return ready
  }

  /**
   * Execute multiple nodes in parallel
   */
  private async executeParallel(
    nodes: DAGNode[],
    graph: DAGGraph,
    executor: (node: DAGNode) => Promise<any>
  ): Promise<void> {
    // Mark as running
    for (const node of nodes) {
      node.status = 'running'
      node.startTime = Date.now()
      graph.inProgress.add(node.id)
    }
    
    // Execute in parallel with error handling
    const promises = nodes.map(node =>
      executor(node)
        .then(result => ({ nodeId: node.id, result, error: null }))
        .catch(error => ({ nodeId: node.id, result: null, error: String(error) }))
    )
    
    const results = await Promise.all(promises)
    
    // Update graph state
    for (const { nodeId, result, error } of results) {
      const node = graph.nodes.get(nodeId)!
      node.endTime = Date.now()
      graph.inProgress.delete(nodeId)
      
      if (error) {
        node.status = 'failed'
        node.error = error
        graph.failed.add(nodeId)
      } else {
        node.status = 'completed'
        node.result = result
        graph.completed.add(nodeId)
      }
    }
  }

  /**
   * Check if execution is complete
   */
  private isComplete(graph: DAGGraph): boolean {
    const totalNodes = graph.nodes.size
    const finishedNodes = graph.completed.size + graph.failed.size
    
    // Also count skipped nodes
    let skipped = 0
    for (const node of graph.nodes.values()) {
      if (node.status === 'skipped') skipped++
    }
    
    return finishedNodes + skipped === totalNodes
  }

  /**
   * Get execution statistics
   */
  getStats(graph: DAGGraph): {
    total: number
    completed: number
    failed: number
    pending: number
    inProgress: number
    skipped: number
  } {
    let skipped = 0
    for (const node of graph.nodes.values()) {
      if (node.status === 'skipped') skipped++
    }
    
    return {
      total: graph.nodes.size,
      completed: graph.completed.size,
      failed: graph.failed.size,
      pending: Array.from(graph.nodes.values()).filter(n => n.status === 'pending').length,
      inProgress: graph.inProgress.size,
      skipped,
    }
  }
}

