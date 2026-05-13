/**
 * Blueprint Pane Data Service
 * 
 * Handles architecture graph operations, documentation mapping,
 * and visualization for the Blueprint Pane of the Lucid Orchestrator.
 */

import {
  BlueprintPaneData,
  ArchitectureGraph,
  ArchitectureNode,
  ArchitectureEdge,
  DocumentationGraph,
  DocumentationNode,
  LayoutConfiguration,
  FilterConfiguration,
  Position,
  Size,
  NodeStyle,
  EdgeStyle,
  NodeData,
  DocumentationNodeData,
  GraphMetadata
} from '../data_models/core_interfaces';
import { CodePaneData } from '../data_models/core_interfaces';

export class BlueprintPaneService {
  private currentGraph: ArchitectureGraph | null = null;
  private layoutConfig: LayoutConfiguration;
  private filterConfig: FilterConfiguration;

  constructor() {
    this.layoutConfig = {
      algorithm: 'force-directed',
      settings: {
        strength: -300,
        distanceMax: 200,
        iterations: 1000
      },
      autoLayout: true,
      spacing: 50
    };

    this.filterConfig = {
      nodeTypes: ['system', 'component', 'module', 'class', 'function'],
      edgeTypes: ['composition', 'aggregation', 'inheritance', 'dependency'],
      qualityThreshold: 0.5,
      complexityThreshold: 5,
      statusFilter: ['active']
    };
  }

  /**
   * Build architecture graph from code data
   */
  async buildArchitectureGraph(codeData: CodePaneData): Promise<ArchitectureGraph> {
    const nodes: ArchitectureNode[] = [];
    const edges: ArchitectureEdge[] = [];

    // Create system node
    const systemNode = this.createSystemNode(codeData.system);
    nodes.push(systemNode);

    // Create component nodes from source files
    for (const file of codeData.files.source) {
      const componentNode = this.createComponentNode(file);
      nodes.push(componentNode);

      // Add composition edge from system to component
      edges.push({
        id: `system_to_${componentNode.id}`,
        from: systemNode.id,
        to: componentNode.id,
        type: 'composition',
        weight: 1.0,
        style: this.createEdgeStyle('composition'),
        label: 'contains'
      });
    }

    // Create documentation nodes (convert to ArchitectureNode for graph)
    for (const file of codeData.files.documentation) {
      const docNode = this.createDocumentationNode(file);
      // Convert DocumentationNode to ArchitectureNode for architecture graph
      const archNode: ArchitectureNode = {
        id: docNode.id,
        name: docNode.title,
        type: 'module',
        position: docNode.position,
        size: docNode.size,
        style: docNode.style,
        data: {
          file: docNode.data.file,
          quality: docNode.data.quality,
          level: docNode.data.level
        }
      };
      nodes.push(archNode);

      // Add reference edge from system to documentation
      edges.push({
        id: `system_to_${docNode.id}`,
        from: systemNode.id,
        to: docNode.id,
        type: 'dependency',
        weight: 0.8,
        style: this.createEdgeStyle('dependency'),
        label: 'documented by'
      });
    }

    // Add internal dependencies
    for (const dep of codeData.dependencies.internal) {
      edges.push({
        id: dep.from + '_to_' + dep.to,
        from: dep.from,
        to: dep.to,
        type: dep.type as any,
        weight: dep.weight,
        style: this.createEdgeStyle(dep.type as any),
        label: dep.type
      });
    }

    // Apply layout if auto-layout is enabled
    if (this.layoutConfig.autoLayout) {
      this.applyLayout(nodes, edges);
    }

    const graph: ArchitectureGraph = {
      nodes,
      edges,
      metadata: {
        totalNodes: nodes.length,
        totalEdges: edges.length,
        lastUpdated: new Date().toISOString(),
        version: '1.0.0'
      }
    };

    this.currentGraph = graph;
    return graph;
  }

  /**
   * Create system node
   */
  private createSystemNode(system: any): ArchitectureNode {
    return {
      id: `system_${system.id}`,
      name: system.name,
      type: 'system',
      position: { x: 400, y: 200 },
      size: { width: 200, height: 100 },
      style: this.createNodeStyle('system'),
      data: {
        system: system.id,
        file: system.rootPath,
        complexity: 0,
        status: 'active'
      }
    };
  }

  /**
   * Create component node from file
   */
  private createComponentNode(file: any): ArchitectureNode {
    const complexity = file.metadata.complexity || 0;
    const quality = this.calculateQuality(file);
    
    return {
      id: file.id,
      name: file.name,
      type: this.determineNodeType(file),
      position: { x: Math.random() * 600 + 100, y: Math.random() * 400 + 100 },
      size: { width: 150, height: 80 },
      style: this.createNodeStyle(this.determineNodeType(file), complexity, quality),
      data: {
        system: file.id.split(':')[0],
        component: file.name,
        file: file.path,
        line: 1,
        complexity,
        status: 'active',
        quality
      }
    };
  }

  /**
   * Create documentation node from file
   */
  private createDocumentationNode(file: any): DocumentationNode {
    const level = file.metadata.level || 'L0';
    const quality = file.metadata.wordCount ? Math.min(file.metadata.wordCount / 1000, 1) : 0.5;
    
    return {
      id: `doc_${file.id}`,
      title: `${level} - ${file.name}`,
      position: { x: Math.random() * 600 + 100, y: Math.random() * 400 + 100 },
      size: { width: 120, height: 60 },
      style: this.createNodeStyle('module', 0, quality),
      data: {
        file: file.path,
        level: level as 'L0' | 'L1' | 'L2' | 'L3' | 'L4',
        wordCount: file.metadata.wordCount || 0,
        quality,
        lastModified: file.lastModified,
        system: file.id.split(':')[0],
        component: file.name
      }
    };
  }

  /**
   * Determine node type from file
   */
  private determineNodeType(file: any): 'component' | 'module' | 'class' | 'function' {
    if (file.path.includes('test') || file.path.includes('spec')) {
      return 'module';
    }
    
    if (file.metadata.classes && file.metadata.classes.length > 0) {
      return 'class';
    }
    
    if (file.metadata.functions && file.metadata.functions.length > 0) {
      return 'function';
    }
    
    return 'component';
  }

  /**
   * Calculate quality score for a file
   */
  private calculateQuality(file: any): number {
    let quality = 0.5; // Base quality
    
    // Add points for documentation
    if (file.metadata.wordCount && file.metadata.wordCount > 100) {
      quality += 0.2;
    }
    
    // Add points for test coverage
    if (file.metadata.testCoverage) {
      quality += file.metadata.testCoverage * 0.2;
    }
    
    // Subtract points for high complexity
    if (file.metadata.complexity && file.metadata.complexity > 5) {
      quality -= 0.1;
    }
    
    return Math.max(0, Math.min(1, quality));
  }

  /**
   * Create node style based on type and metrics
   */
  private createNodeStyle(
    type: string, 
    complexity: number = 0, 
    quality: number = 0.5
  ): NodeStyle {
    const colorMap: Record<string, string> = {
      system: '#3B82F6',
      component: '#10B981',
      module: '#8B5CF6',
      class: '#F59E0B',
      function: '#EF4444'
    };

    const baseColor = colorMap[type] || '#6B7280';
    
    // Adjust color based on quality
    const qualityColor = this.adjustColorForQuality(baseColor, quality);
    
    // Adjust border based on complexity
    const borderWidth = Math.min(complexity / 2 + 1, 4);

    return {
      color: qualityColor,
      shape: type === 'system' ? 'rectangle' : 'circle',
      border: {
        width: borderWidth,
        style: 'solid',
        color: qualityColor
      },
      fill: {
        color: qualityColor,
        opacity: 0.1
      },
      text: {
        color: '#1F2937',
        fontSize: 12,
        fontWeight: 'normal',
        fontFamily: 'Inter, sans-serif'
      }
    };
  }

  /**
   * Adjust color based on quality score
   */
  private adjustColorForQuality(baseColor: string, quality: number): string {
    // Convert hex to RGB
    const hex = baseColor.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    // Adjust brightness based on quality
    const factor = 0.5 + quality * 0.5;
    const newR = Math.round(r * factor);
    const newG = Math.round(g * factor);
    const newB = Math.round(b * factor);
    
    return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
  }

  /**
   * Create edge style based on type
   */
  private createEdgeStyle(type: string): EdgeStyle {
    const styleMap: Record<string, EdgeStyle> = {
      composition: {
        color: '#6B7280',
        width: 2,
        style: 'solid',
        arrow: 'forward'
      },
      aggregation: {
        color: '#6B7280',
        width: 2,
        style: 'solid',
        arrow: 'forward'
      },
      inheritance: {
        color: '#8B5CF6',
        width: 2,
        style: 'solid',
        arrow: 'forward'
      },
      dependency: {
        color: '#F59E0B',
        width: 1,
        style: 'dashed',
        arrow: 'forward'
      },
      association: {
        color: '#10B981',
        width: 1,
        style: 'solid',
        arrow: 'none'
      }
    };

    return styleMap[type] || styleMap.dependency;
  }

  /**
   * Apply layout algorithm to nodes
   */
  private applyLayout(nodes: ArchitectureNode[], edges: ArchitectureEdge[]): void {
    if (this.layoutConfig.algorithm === 'force-directed') {
      this.applyForceDirectedLayout(nodes, edges);
    } else if (this.layoutConfig.algorithm === 'hierarchical') {
      this.applyHierarchicalLayout(nodes, edges);
    } else if (this.layoutConfig.algorithm === 'circular') {
      this.applyCircularLayout(nodes);
    }
  }

  /**
   * Apply force-directed layout
   */
  private applyForceDirectedLayout(nodes: ArchitectureNode[], edges: ArchitectureEdge[]): void {
    const iterations = this.layoutConfig.settings.iterations || 1000;
    const strength = this.layoutConfig.settings.strength || -300;
    const distanceMax = this.layoutConfig.settings.distanceMax || 200;

    // Initialize positions
    nodes.forEach(node => {
      if (node.position.x === 0 && node.position.y === 0) {
        node.position.x = Math.random() * 800;
        node.position.y = Math.random() * 600;
      }
    });

    // Apply force-directed algorithm
    for (let i = 0; i < iterations; i++) {
      const forces: Map<string, { x: number; y: number }> = new Map();
      
      // Initialize forces
      nodes.forEach(node => {
        forces.set(node.id, { x: 0, y: 0 });
      });

      // Calculate repulsive forces between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const node1 = nodes[i];
          const node2 = nodes[j];
          const dx = node1.position.x - node2.position.x;
          const dy = node1.position.y - node2.position.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          
          const force = strength / (distance * distance);
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;
          
          forces.get(node1.id)!.x += fx;
          forces.get(node1.id)!.y += fy;
          forces.get(node2.id)!.x -= fx;
          forces.get(node2.id)!.y -= fy;
        }
      }

      // Calculate attractive forces for connected nodes
      edges.forEach(edge => {
        const fromNode = nodes.find(n => n.id === edge.from);
        const toNode = nodes.find(n => n.id === edge.to);
        
        if (fromNode && toNode) {
          const dx = toNode.position.x - fromNode.position.x;
          const dy = toNode.position.y - fromNode.position.y;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          
          const force = (distance - distanceMax) * 0.01;
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;
          
          forces.get(fromNode.id)!.x += fx;
          forces.get(fromNode.id)!.y += fy;
          forces.get(toNode.id)!.x -= fx;
          forces.get(toNode.id)!.y -= fy;
        }
      });

      // Apply forces
      nodes.forEach(node => {
        const force = forces.get(node.id)!;
        node.position.x += force.x * 0.1;
        node.position.y += force.y * 0.1;
      });
    }
  }

  /**
   * Apply hierarchical layout
   */
  private applyHierarchicalLayout(nodes: ArchitectureNode[], edges: ArchitectureEdge[]): void {
    // Find root nodes (nodes with no incoming edges)
    const rootNodes = nodes.filter(node => 
      !edges.some(edge => edge.to === node.id)
    );

    // Assign levels
    const levels: Map<string, number> = new Map();
    const visited = new Set<string>();

    const assignLevel = (nodeId: string, level: number) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      levels.set(nodeId, level);

      // Assign levels to children
      edges
        .filter(edge => edge.from === nodeId)
        .forEach(edge => assignLevel(edge.to, level + 1));
    };

    rootNodes.forEach(node => assignLevel(node.id, 0));

    // Position nodes
    const levelGroups: Map<number, ArchitectureNode[]> = new Map();
    nodes.forEach(node => {
      const level = levels.get(node.id) || 0;
      if (!levelGroups.has(level)) {
        levelGroups.set(level, []);
      }
      levelGroups.get(level)!.push(node);
    });

    const levelHeight = 150;
    const nodeSpacing = 200;

    levelGroups.forEach((levelNodes, level) => {
      levelNodes.forEach((node, index) => {
        node.position.x = (index - levelNodes.length / 2) * nodeSpacing + 400;
        node.position.y = level * levelHeight + 100;
      });
    });
  }

  /**
   * Apply circular layout
   */
  private applyCircularLayout(nodes: ArchitectureNode[]): void {
    const centerX = 400;
    const centerY = 300;
    const radius = 200;

    nodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / nodes.length;
      node.position.x = centerX + radius * Math.cos(angle);
      node.position.y = centerY + radius * Math.sin(angle);
    });
  }

  /**
   * Update node position
   */
  async updateNodePosition(nodeId: string, position: Position): Promise<void> {
    if (!this.currentGraph) return;

    const node = this.currentGraph.nodes.find(n => n.id === nodeId);
    if (node) {
      node.position = position;
      this.currentGraph.metadata.lastUpdated = new Date().toISOString();
    }
  }

  /**
   * Export graph in different formats
   */
  async exportGraph(format: 'json' | 'graphml' | 'dot'): Promise<string> {
    if (!this.currentGraph) {
      throw new Error('No graph to export');
    }

    switch (format) {
      case 'json':
        return JSON.stringify(this.currentGraph, null, 2);
      
      case 'graphml':
        return this.exportToGraphML(this.currentGraph);
      
      case 'dot':
        return this.exportToDOT(this.currentGraph);
      
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }

  /**
   * Export to GraphML format
   */
  private exportToGraphML(graph: ArchitectureGraph): string {
    let graphml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    graphml += '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n';
    graphml += '  <graph id="architecture" edgedefault="directed">\n';

    // Add nodes
    graph.nodes.forEach(node => {
      graphml += `    <node id="${node.id}">\n`;
      graphml += `      <data key="name">${node.name}</data>\n`;
      graphml += `      <data key="type">${node.type}</data>\n`;
      graphml += `      <data key="x">${node.position.x}</data>\n`;
      graphml += `      <data key="y">${node.position.y}</data>\n`;
      graphml += `    </node>\n`;
    });

    // Add edges
    graph.edges.forEach(edge => {
      graphml += `    <edge id="${edge.id}" source="${edge.from}" target="${edge.to}">\n`;
      graphml += `      <data key="type">${edge.type}</data>\n`;
      graphml += `      <data key="weight">${edge.weight}</data>\n`;
      graphml += `    </edge>\n`;
    });

    graphml += '  </graph>\n';
    graphml += '</graphml>';
    
    return graphml;
  }

  /**
   * Export to DOT format
   */
  private exportToDOT(graph: ArchitectureGraph): string {
    let dot = 'digraph architecture {\n';
    dot += '  rankdir=TB;\n';
    dot += '  node [shape=box, style=filled];\n\n';

    // Add nodes
    graph.nodes.forEach(node => {
      const color = this.getNodeColor(node);
      const label = `"${node.name}"`;
      dot += `  ${node.id} [label=${label}, fillcolor="${color}"];\n`;
    });

    dot += '\n';

    // Add edges
    graph.edges.forEach(edge => {
      const style = this.getEdgeStyle(edge);
      dot += `  ${edge.from} -> ${edge.to} [${style}];\n`;
    });

    dot += '}\n';
    return dot;
  }

  /**
   * Get node color for DOT export
   */
  private getNodeColor(node: ArchitectureNode): string {
    const colorMap: Record<string, string> = {
      system: 'lightblue',
      component: 'lightgreen',
      module: 'lightpink',
      class: 'lightyellow',
      function: 'lightcoral'
    };
    return colorMap[node.type] || 'lightgray';
  }

  /**
   * Get edge style for DOT export
   */
  private getEdgeStyle(edge: ArchitectureEdge): string {
    const styleMap: Record<string, string> = {
      composition: 'style=solid, color=black',
      aggregation: 'style=solid, color=black',
      inheritance: 'style=solid, color=purple',
      dependency: 'style=dashed, color=orange',
      association: 'style=solid, color=green'
    };
    return styleMap[edge.type] || 'style=solid, color=black';
  }

  /**
   * Build documentation graph
   */
  async buildDocumentationGraph(codeData: CodePaneData): Promise<DocumentationGraph> {
    const documentation: DocumentationGraph = {
      L0: [],
      L1: [],
      L2: [],
      L3: [],
      L4: []
    };

    // Process documentation files
    for (const file of codeData.files.documentation) {
      if (file.metadata.level) {
        const docNode = this.createDocumentationNode(file);
        documentation[file.metadata.level].push(docNode);
      }
    }

    return documentation;
  }

  /**
   * Get current graph
   */
  getCurrentGraph(): ArchitectureGraph | null {
    return this.currentGraph;
  }

  /**
   * Get layout configuration
   */
  getLayoutConfiguration(): LayoutConfiguration {
    return this.layoutConfig;
  }

  /**
   * Update layout configuration
   */
  updateLayoutConfiguration(config: Partial<LayoutConfiguration>): void {
    this.layoutConfig = { ...this.layoutConfig, ...config };
  }

  /**
   * Get filter configuration
   */
  getFilterConfiguration(): FilterConfiguration {
    return this.filterConfig;
  }

  /**
   * Update filter configuration
   */
  updateFilterConfiguration(config: Partial<FilterConfiguration>): void {
    this.filterConfig = { ...this.filterConfig, ...config };
  }

  /**
   * Apply filters to current graph
   */
  applyFilters(): ArchitectureGraph | null {
    if (!this.currentGraph) return null;

    const filteredNodes = this.currentGraph.nodes.filter(node => {
      return this.filterConfig.nodeTypes.includes(node.type) &&
             (node.data.quality || 0) >= this.filterConfig.qualityThreshold &&
             (node.data.complexity || 0) <= this.filterConfig.complexityThreshold &&
             this.filterConfig.statusFilter.includes(node.data.status || 'active');
    });

    const filteredEdges = this.currentGraph.edges.filter(edge => {
      return this.filterConfig.edgeTypes.includes(edge.type) &&
             filteredNodes.some(n => n.id === edge.from) &&
             filteredNodes.some(n => n.id === edge.to);
    });

    return {
      ...this.currentGraph,
      nodes: filteredNodes,
      edges: filteredEdges,
      metadata: {
        ...this.currentGraph.metadata,
        totalNodes: filteredNodes.length,
        totalEdges: filteredEdges.length,
        lastUpdated: new Date().toISOString()
      }
    };
  }
}
