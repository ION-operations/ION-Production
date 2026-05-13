/**
 * Lucid Orchestrator - IR (Intermediate Representation) Model
 * 
 * This defines the core data structures for the Graph Engine that powers
 * the Blueprint Pane of the Lucid Orchestrator.
 */

export type NodeKind = 
  | 'function'
  | 'reactComponent'
  | 'component'
  | 'test'
  | 'apiHandler'
  | 'store'
  | 'reducer'
  | 'hook'
  | 'service'
  | 'job'
  | 'queue'
  | 'dbModel'
  | 'cssBlock'
  | 'type'
  | 'interface'
  | 'enum'
  | 'constant'
  | 'variable';

export type EdgeType =
  | 'calls'
  | 'imports'
  | 'mutates'
  | 'subscribesTo'
  | 'dispatches'
  | 'publishesEvent'
  | 'consumesEvent'
  | 'updatesUI'
  | 'queriesDB'
  | 'writesTo'
  | 'dependsOn'
  | 'extends'
  | 'implements'
  | 'uses'
  | 'creates'
  | 'destroys';

export type NodeStatus = 'clean' | 'drift' | 'violation' | 'proposed' | 'orphan';

export interface IRNode {
  /** Unique stable identifier for this node */
  id: string;
  
  /** Type of code unit this represents */
  kind: NodeKind;
  
  /** Symbol name (function name, component name, etc.) */
  name: string;
  
  /** Source file path */
  filePath: string;
  
  /** Line range in source file */
  range: {
    startLine: number;
    endLine: number;
    startColumn?: number;
    endColumn?: number;
  };
  
  /** Data/parameters this node consumes */
  inputs: string[];
  
  /** State this node returns or mutates */
  outputs: string[];
  
  /** Side effects this node performs */
  sideEffects: string[];
  
  /** Semantic tags for categorization */
  tags: string[];
  
  /** Current health status */
  status: NodeStatus;
  
  /** Reason for current status */
  statusReason?: string;
  
  /** Performance characteristics */
  performance?: {
    estimatedComplexity: number;
    estimatedExecutionTime: number;
    memoryUsage: number;
    cpuUsage: number;
    isAsync: boolean;
    hasSideEffects: boolean;
    isPure: boolean;
  };
  
  /** Security characteristics */
  security?: {
    level: 'low' | 'medium' | 'high' | 'critical';
    isPublic: boolean;
    handlesSensitiveData: boolean;
    requiresAuth: boolean;
  };
  
  /** Metadata for analysis */
  metadata: {
    createdAt: string;
    lastModified: string;
    author?: string;
    complexity: number;
    testCoverage?: number;
    dependencies: string[];
    dependents: string[];
    documentation?: string;
  };
}

export interface IREdge {
  /** Source node ID */
  from: string;
  
  /** Target node ID */
  to: string;
  
  /** Type of relationship */
  type: EdgeType;
  
  /** Weight/strength of relationship */
  weight?: number;
  
  /** Metadata about the relationship */
  metadata: {
    createdAt: string;
    lastSeen: string;
    frequency: number;
    isDirect: boolean;
    isAsync: boolean;
  };
}

export interface IRGraph {
  /** All nodes in the graph */
  nodes: Map<string, IRNode>;
  
  /** All edges in the graph */
  edges: Map<string, IREdge>;
  
  /** Graph metadata */
  metadata: {
    createdAt: string;
    lastUpdated: string;
    totalNodes: number;
    totalEdges: number;
    language: string;
    version: string;
  };
}

/**
 * Utility functions for working with IR graphs
 */
export class IRGraphUtils {
  /**
   * Find all nodes of a specific kind
   */
  static getNodesByKind(graph: IRGraph, kind: NodeKind): IRNode[] {
    return Array.from(graph.nodes.values()).filter(node => node.kind === kind);
  }
  
  /**
   * Find all edges of a specific type
   */
  static getEdgesByType(graph: IRGraph, type: EdgeType): IREdge[] {
    return Array.from(graph.edges.values()).filter(edge => edge.type === type);
  }
  
  /**
   * Get all nodes connected to a given node
   */
  static getConnectedNodes(graph: IRGraph, nodeId: string): {
    incoming: IRNode[];
    outgoing: IRNode[];
  } {
    const incoming: IRNode[] = [];
    const outgoing: IRNode[] = [];
    
    for (const edge of graph.edges.values()) {
      if (edge.from === nodeId) {
        const targetNode = graph.nodes.get(edge.to);
        if (targetNode) outgoing.push(targetNode);
      }
      if (edge.to === nodeId) {
        const sourceNode = graph.nodes.get(edge.from);
        if (sourceNode) incoming.push(sourceNode);
      }
    }
    
    return { incoming, outgoing };
  }
  
  /**
   * Calculate the blast radius of a node (all nodes that would be affected by changes)
   */
  static getBlastRadius(graph: IRGraph, nodeId: string): {
    direct: string[];
    indirect: string[];
    total: number;
  } {
    const visited = new Set<string>();
    const direct: string[] = [];
    const indirect: string[] = [];
    
    // Get direct connections
    const connected = this.getConnectedNodes(graph, nodeId);
    connected.incoming.forEach(node => {
      direct.push(node.id);
      visited.add(node.id);
    });
    connected.outgoing.forEach(node => {
      direct.push(node.id);
      visited.add(node.id);
    });
    
    // Get indirect connections (2 degrees of separation)
    for (const directNodeId of direct) {
      const indirectConnected = this.getConnectedNodes(graph, directNodeId);
      indirectConnected.incoming.forEach(node => {
        if (!visited.has(node.id) && node.id !== nodeId) {
          indirect.push(node.id);
          visited.add(node.id);
        }
      });
      indirectConnected.outgoing.forEach(node => {
        if (!visited.has(node.id) && node.id !== nodeId) {
          indirect.push(node.id);
          visited.add(node.id);
        }
      });
    }
    
    return {
      direct,
      indirect,
      total: direct.length + indirect.length
    };
  }
  
  /**
   * Find nodes with specific tags
   */
  static getNodesByTags(graph: IRGraph, tags: string[]): IRNode[] {
    return Array.from(graph.nodes.values()).filter(node =>
      tags.some(tag => node.tags.includes(tag))
    );
  }
  
  /**
   * Get nodes with specific status
   */
  static getNodesByStatus(graph: IRGraph, status: NodeStatus): IRNode[] {
    return Array.from(graph.nodes.values()).filter(node => node.status === status);
  }
  
  /**
   * Calculate graph health metrics
   */
  static getGraphHealth(graph: IRGraph): {
    totalNodes: number;
    cleanNodes: number;
    driftNodes: number;
    violationNodes: number;
    healthScore: number;
  } {
    const nodes = Array.from(graph.nodes.values());
    const cleanNodes = nodes.filter(n => n.status === 'clean').length;
    const driftNodes = nodes.filter(n => n.status === 'drift').length;
    const violationNodes = nodes.filter(n => n.status === 'violation').length;
    
    const healthScore = nodes.length > 0 
      ? (cleanNodes / nodes.length) * 100 
      : 100;
    
    return {
      totalNodes: nodes.length,
      cleanNodes,
      driftNodes,
      violationNodes,
      healthScore
    };
  }
}

/**
 * Event types for IR graph updates
 */
export interface IRGraphEvent {
  type: 'NODE_ADDED' | 'NODE_UPDATED' | 'NODE_REMOVED' | 'EDGE_ADDED' | 'EDGE_REMOVED' | 'STATUS_CHANGED';
  nodeId?: string;
  edgeId?: string;
  data?: any;
  timestamp: string;
}

/**
 * IR Graph Builder for incremental updates
 */
export class IRGraphBuilder {
  private graph: IRGraph;
  
  constructor() {
    this.graph = {
      nodes: new Map(),
      edges: new Map(),
      metadata: {
        createdAt: new Date().toISOString(),
        lastUpdated: new Date().toISOString(),
        totalNodes: 0,
        totalEdges: 0,
        language: 'typescript',
        version: '1.0.0'
      }
    };
  }
  
  /**
   * Add a node to the graph
   */
  addNode(node: IRNode): void {
    this.graph.nodes.set(node.id, node);
    this.graph.metadata.totalNodes = this.graph.nodes.size;
    this.graph.metadata.lastUpdated = new Date().toISOString();
  }
  
  /**
   * Add an edge to the graph
   */
  addEdge(edge: IREdge): void {
    const edgeId = `${edge.from}->${edge.to}:${edge.type}`;
    this.graph.edges.set(edgeId, edge);
    this.graph.metadata.totalEdges = this.graph.edges.size;
    this.graph.metadata.lastUpdated = new Date().toISOString();
  }
  
  /**
   * Update node status
   */
  updateNodeStatus(nodeId: string, status: NodeStatus, reason?: string): void {
    const node = this.graph.nodes.get(nodeId);
    if (node) {
      node.status = status;
      node.statusReason = reason;
      node.metadata.lastModified = new Date().toISOString();
    }
  }
  
  /**
   * Get the current graph
   */
  getGraph(): IRGraph {
    return this.graph;
  }
  
  /**
   * Export graph to JSON
   */
  exportToJSON(): string {
    const graphData = {
      nodes: Array.from(this.graph.nodes.values()),
      edges: Array.from(this.graph.edges.values()),
      metadata: {
        ...this.graph.metadata,
        exportedAt: new Date().toISOString(),
        version: '1.0.0'
      }
    };
    
    return JSON.stringify(graphData, null, 2);
  }
  
  /**
   * Import graph from JSON
   */
  importFromJSON(json: string): void {
    try {
      const data = JSON.parse(json);
      
      // Clear existing data
      this.graph.nodes.clear();
      this.graph.edges.clear();
      
      // Import nodes
      if (Array.isArray(data.nodes)) {
        for (const node of data.nodes) {
          this.graph.nodes.set(node.id, node as IRNode);
        }
      }
      
      // Import edges
      if (Array.isArray(data.edges)) {
        for (const edge of data.edges) {
          const edgeId = `${edge.from}->${edge.to}:${edge.type}`;
          this.graph.edges.set(edgeId, edge as IREdge);
        }
      }
      
      // Update metadata
      if (data.metadata) {
        this.graph.metadata = { ...this.graph.metadata, ...data.metadata };
      }
      
      this.graph.metadata.totalNodes = this.graph.nodes.size;
      this.graph.metadata.totalEdges = this.graph.edges.size;
      this.graph.metadata.lastUpdated = new Date().toISOString();
    } catch (error) {
      throw new Error(`Failed to import graph from JSON: ${error}`);
    }
  }

  /**
   * Export graph to GraphML format
   */
  exportToGraphML(): string {
    let graphml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    graphml += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n';
    
    // Define node attributes
    graphml += '  <key id="kind" for="node" attr.name="kind" attr.type="string"/>\n';
    graphml += '  <key id="filePath" for="node" attr.name="filePath" attr.type="string"/>\n';
    graphml += '  <key id="status" for="node" attr.name="status" attr.type="string"/>\n';
    
    // Define edge attributes
    graphml += '  <key id="type" for="edge" attr.name="type" attr.type="string"/>\n';
    
    graphml += '  <graph id="ir-graph" edgedefault="directed">\n';
    
    // Export nodes
    for (const node of this.graph.nodes.values()) {
      graphml += `    <node id="${node.id}">\n`;
      graphml += `      <data key="kind">${node.kind}</data>\n`;
      graphml += `      <data key="filePath">${node.filePath}</data>\n`;
      graphml += `      <data key="status">${node.status}</data>\n`;
      graphml += `    </node>\n`;
    }
    
    // Export edges
    for (const edge of this.graph.edges.values()) {
      const edgeId = `${edge.from}->${edge.to}:${edge.type}`;
      graphml += `    <edge id="${edgeId}" source="${edge.from}" target="${edge.to}">\n`;
      graphml += `      <data key="type">${edge.type}</data>\n`;
      graphml += `    </edge>\n`;
    }
    
    graphml += '  </graph>\n';
    graphml += '</graphml>';
    
    return graphml;
  }

  /**
   * Export graph to DOT format (Graphviz)
   */
  exportToDOT(): string {
    let dot = 'digraph IRGraph {\n';
    dot += '  rankdir=TB;\n';
    dot += '  node [shape=box, style=filled];\n\n';
    
    // Group nodes by file
    const nodesByFile = new Map<string, IRNode[]>();
    for (const node of this.graph.nodes.values()) {
      const file = node.filePath;
      if (!nodesByFile.has(file)) {
        nodesByFile.set(file, []);
      }
      nodesByFile.get(file)!.push(node);
    }
    
    // Create subgraphs for each file
    for (const [file, nodes] of nodesByFile.entries()) {
      const clusterName = `cluster_${file.replace(/[^a-zA-Z0-9]/g, '_')}`;
      dot += `  subgraph ${clusterName} {\n`;
      dot += `    label="${file}";\n`;
      dot += `    style=filled;\n`;
      dot += `    color=lightgray;\n`;
      
      for (const node of nodes) {
        const color = this.getNodeColor(node);
        dot += `    "${node.id}" [label="${node.name}", fillcolor="${color}"];\n`;
      }
      
      dot += '  }\n\n';
    }
    
    // Add edges
    for (const edge of this.graph.edges.values()) {
      const style = this.getEdgeStyle(edge);
      dot += `  "${edge.from}" -> "${edge.to}" [${style}];\n`;
    }
    
    dot += '}\n';
    return dot;
  }

  /**
   * Get color for node based on kind and status
   */
  private getNodeColor(node: IRNode): string {
    const statusColors = {
      'clean': 'lightgreen',
      'drift': 'yellow',
      'violation': 'red',
      'proposed': 'lightblue',
      'orphan': 'gray'
    };
    
    const kindColors = {
      'function': 'lightblue',
      'reactComponent': 'lightcoral',
      'component': 'lightcoral',
      'test': 'lightyellow',
      'apiHandler': 'lightpink',
      'store': 'lightsteelblue',
      'reducer': 'lightsteelblue',
      'hook': 'lightcyan',
      'service': 'lightgray',
      'job': 'orange',
      'queue': 'orange',
      'dbModel': 'lightgreen',
      'cssBlock': 'lightpink',
      'type': 'white',
      'interface': 'white',
      'enum': 'white',
      'constant': 'lightyellow',
      'variable': 'lightyellow'
    };
    
    return statusColors[node.status] || kindColors[node.kind] || 'white';
  }

  /**
   * Get style for edge based on type
   */
  private getEdgeStyle(edge: IREdge): string {
    const typeStyles = {
      'calls': 'color=blue',
      'imports': 'color=green, style=dashed',
      'mutates': 'color=red',
      'subscribesTo': 'color=purple, style=dotted',
      'dispatches': 'color=purple',
      'publishesEvent': 'color=purple',
      'consumesEvent': 'color=purple, style=dotted',
      'updatesUI': 'color=orange',
      'queriesDB': 'color=brown',
      'writesTo': 'color=red',
      'dependsOn': 'color=gray, style=dashed',
      'extends': 'color=black, style=bold',
      'implements': 'color=black, style=dashed',
      'uses': 'color=blue, style=dotted',
      'creates': 'color=green',
      'destroys': 'color=red, style=bold'
    };
    
    return typeStyles[edge.type] || 'color=black';
  }
}
