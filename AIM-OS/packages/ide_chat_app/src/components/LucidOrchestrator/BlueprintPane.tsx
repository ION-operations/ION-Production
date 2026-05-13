/**
 * Blueprint Pane Component
 * 
 * Displays architecture visualization, documentation mapping, and system structure
 * for the Lucid Orchestrator. Consumes data from the BlueprintPaneService.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Network, 
  Layers, 
  FileText, 
  Code, 
  Settings, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  Download,
  Filter,
  Search,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { BlueprintPaneData, ArchitectureNode, ArchitectureEdge, DocumentationNode } from '../../../lucid_orchestrator/data_models/core_interfaces';

interface BlueprintPaneProps {
  data: BlueprintPaneData;
  onNodeSelect?: (node: ArchitectureNode) => void;
  onNodeMove?: (nodeId: string, position: { x: number; y: number }) => void;
  onRefresh?: () => void;
  className?: string;
}

export const BlueprintPane: React.FC<BlueprintPaneProps> = ({ 
  data, 
  onNodeSelect, 
  onNodeMove,
  onRefresh,
  className = '' 
}) => {
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showDocumentation, setShowDocumentation] = useState(true);
  const [showEdges, setShowEdges] = useState(true);
  const [filteredNodes, setFilteredNodes] = useState<ArchitectureNode[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [nodeTypeFilter, setNodeTypeFilter] = useState<string>('all');
  
  const canvasRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Initialize filtered nodes
  useEffect(() => {
    setFilteredNodes(data.architecture.nodes);
  }, [data.architecture.nodes]);

  // Filter nodes based on search and type
  useEffect(() => {
    let filtered = data.architecture.nodes;

    if (searchTerm) {
      filtered = filtered.filter(node => 
        node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.type.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (nodeTypeFilter !== 'all') {
      filtered = filtered.filter(node => node.type === nodeTypeFilter);
    }

    setFilteredNodes(filtered);
  }, [data.architecture.nodes, searchTerm, nodeTypeFilter]);

  // Get node color based on type and quality
  const getNodeColor = (node: ArchitectureNode) => {
    const quality = node.data.quality || 0.5;
    const baseColors = {
      system: '#3B82F6',
      component: '#10B981',
      module: '#8B5CF6',
      class: '#F59E0B',
      function: '#EF4444'
    };
    
    const baseColor = baseColors[node.type as keyof typeof baseColors] || '#6B7280';
    
    // Adjust brightness based on quality
    const factor = 0.5 + quality * 0.5;
    return adjustColorBrightness(baseColor, factor);
  };

  // Adjust color brightness
  const adjustColorBrightness = (hex: string, factor: number) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    
    const newR = Math.round(r * factor);
    const newG = Math.round(g * factor);
    const newB = Math.round(b * factor);
    
    return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
  };

  // Get node icon
  const getNodeIcon = (node: ArchitectureNode) => {
    switch (node.type) {
      case 'system':
        return <Network className="w-4 h-4" />;
      case 'component':
        return <Layers className="w-4 h-4" />;
      case 'module':
        return <FileText className="w-4 h-4" />;
      case 'class':
        return <Code className="w-4 h-4" />;
      case 'function':
        return <Settings className="w-4 h-4" />;
      default:
        return <Network className="w-4 h-4" />;
    }
  };

  // Handle mouse down for dragging
  const handleMouseDown = (e: React.MouseEvent, node: ArchitectureNode) => {
    if (e.button === 0) { // Left mouse button
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
      setSelectedNode(node);
      onNodeSelect?.(node);
    }
  };

  // Handle mouse move for dragging
  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && selectedNode) {
      const deltaX = (e.clientX - dragStart.x) / zoom;
      const deltaY = (e.clientY - dragStart.y) / zoom;
      
      const newPosition = {
        x: selectedNode.position.x + deltaX,
        y: selectedNode.position.y + deltaY
      };
      
      onNodeMove?.(selectedNode.id, newPosition);
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };

  // Handle mouse up
  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Handle zoom
  const handleZoom = (delta: number) => {
    setZoom(prev => Math.max(0.1, Math.min(3, prev + delta)));
  };

  // Handle wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    handleZoom(delta);
  };

  // Reset view
  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Get visible edges
  const visibleEdges = useMemo(() => {
    if (!showEdges) return [];
    
    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
    return data.architecture.edges.filter(edge => 
      visibleNodeIds.has(edge.from) && visibleNodeIds.has(edge.to)
    );
  }, [data.architecture.edges, filteredNodes, showEdges]);

  // Get documentation nodes
  const documentationNodes = useMemo(() => {
    if (!showDocumentation) return [];
    
    const allDocNodes: DocumentationNode[] = [
      ...data.documentation.L0,
      ...data.documentation.L1,
      ...data.documentation.L2,
      ...data.documentation.L3,
      ...data.documentation.L4
    ];
    
    return allDocNodes;
  }, [data.documentation, showDocumentation]);

  return (
    <div className={`h-full flex flex-col bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Blueprint Pane</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={onRefresh}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Refresh"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Export"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search nodes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={nodeTypeFilter}
            onChange={(e) => setNodeTypeFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="system">System</option>
            <option value="component">Component</option>
            <option value="module">Module</option>
            <option value="class">Class</option>
            <option value="function">Function</option>
          </select>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowDocumentation(!showDocumentation)}
              className={`p-2 rounded-md transition-colors ${
                showDocumentation 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
              title="Toggle Documentation"
            >
              {showDocumentation ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>
            
            <button
              onClick={() => setShowEdges(!showEdges)}
              className={`p-2 rounded-md transition-colors ${
                showEdges 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
              title="Toggle Edges"
            >
              <Network className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleZoom(-0.1)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-sm text-gray-600 min-w-[3rem] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <button
              onClick={() => handleZoom(0.1)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={resetView}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Reset View"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative overflow-hidden">
        <div
          ref={canvasRef}
          className="w-full h-full relative cursor-grab active:cursor-grabbing"
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
        >
          <svg
            ref={svgRef}
            className="w-full h-full"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: '0 0'
            }}
          >
            {/* Edges */}
            {visibleEdges.map((edge) => {
              const fromNode = filteredNodes.find(n => n.id === edge.from);
              const toNode = filteredNodes.find(n => n.id === edge.to);
              
              if (!fromNode || !toNode) return null;

              return (
                <line
                  key={edge.id}
                  x1={fromNode.position.x + fromNode.size.width / 2}
                  y1={fromNode.position.y + fromNode.size.height / 2}
                  x2={toNode.position.x + toNode.size.width / 2}
                  y2={toNode.position.y + toNode.size.height / 2}
                  stroke={edge.style.color}
                  strokeWidth={edge.style.width}
                  strokeDasharray={edge.style.style === 'dashed' ? '5,5' : 'none'}
                  opacity={0.6}
                />
              );
            })}

            {/* Architecture Nodes */}
            {filteredNodes.map((node) => (
              <g key={node.id}>
                <rect
                  x={node.position.x}
                  y={node.position.y}
                  width={node.size.width}
                  height={node.size.height}
                  fill={getNodeColor(node)}
                  stroke={selectedNode?.id === node.id ? '#3B82F6' : '#E5E7EB'}
                  strokeWidth={selectedNode?.id === node.id ? 2 : 1}
                  rx={8}
                  ry={8}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onMouseDown={(e) => handleMouseDown(e, node)}
                />
                
                {/* Node Icon */}
                <foreignObject
                  x={node.position.x + 8}
                  y={node.position.y + 8}
                  width={20}
                  height={20}
                >
                  <div className="flex items-center justify-center w-5 h-5 text-white">
                    {getNodeIcon(node)}
                  </div>
                </foreignObject>
                
                {/* Node Label */}
                <text
                  x={node.position.x + node.size.width / 2}
                  y={node.position.y + node.size.height - 8}
                  textAnchor="middle"
                  className="text-xs font-medium fill-white"
                >
                  {node.name}
                </text>
              </g>
            ))}

            {/* Documentation Nodes */}
            {documentationNodes.map((docNode) => (
              <g key={docNode.id}>
                <circle
                  cx={docNode.position.x + docNode.size.width / 2}
                  cy={docNode.position.y + docNode.size.height / 2}
                  r={docNode.size.width / 2}
                  fill="#8B5CF6"
                  stroke="#7C3AED"
                  strokeWidth={1}
                  opacity={0.8}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                />
                
                <text
                  x={docNode.position.x + docNode.size.width / 2}
                  y={docNode.position.y + docNode.size.height / 2 + 4}
                  textAnchor="middle"
                  className="text-xs font-medium fill-white"
                >
                  {docNode.data.level}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </div>

      {/* Node Details Sidebar */}
      {selectedNode && (
        <div className="w-80 border-l border-gray-200 bg-white overflow-y-auto">
          <div className="p-4">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Node Details</h4>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Name</label>
                <p className="text-gray-900">{selectedNode.name}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Type</label>
                <p className="text-gray-900 capitalize">{selectedNode.type}</p>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-700">Position</label>
                <p className="text-gray-900">
                  ({Math.round(selectedNode.position.x)}, {Math.round(selectedNode.position.y)})
                </p>
              </div>
              
              {selectedNode.data.complexity && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Complexity</label>
                  <p className="text-gray-900">{selectedNode.data.complexity.toFixed(2)}</p>
                </div>
              )}
              
              {selectedNode.data.quality && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Quality</label>
                  <p className="text-gray-900">{(selectedNode.data.quality * 100).toFixed(1)}%</p>
                </div>
              )}
              
              {selectedNode.data.file && (
                <div>
                  <label className="text-sm font-medium text-gray-700">File</label>
                  <p className="text-gray-900 text-sm break-all">{selectedNode.data.file}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
