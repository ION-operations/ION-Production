// packages/ide_chat_app/src/components/LucidOrchestratorMain.tsx
import React, { useState, useEffect, useRef } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { 
  Code, 
  Network, 
  FileText, 
  Clock, 
  Play, 
  Pause, 
  Square, 
  Settings,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  RotateCcw,
  Zap,
  Brain,
  Target,
  Activity
} from 'lucide-react';

interface LucidNode {
  id: string;
  name: string;
  type: 'function' | 'component' | 'class' | 'interface' | 'test';
  filePath: string;
  line: number;
  status: 'active' | 'inactive' | 'error' | 'warning';
  dependencies: string[];
  dependents: string[];
  lastModified: Date;
  complexity: number;
  testCoverage: number;
}

interface TimelineEvent {
  id: string;
  nodeId: string;
  timestamp: number;
  type: 'execution' | 'error' | 'test' | 'modification';
  duration: number;
  status: 'success' | 'error' | 'warning';
  message: string;
}

interface SpecBlock {
  id: string;
  nodeId: string;
  title: string;
  description: string;
  requirements: string[];
  constraints: string[];
  status: 'valid' | 'violated' | 'unknown';
  lastChecked: Date;
}

export const LucidOrchestratorMain: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<LucidNode | null>(null);
  const [specBlocks, setSpecBlocks] = useState<SpecBlock[]>([]);
  const [showGrid, setShowGrid] = useState(true);
  const [autoSync, setAutoSync] = useState(true);
  

  // Mock data for demonstration
  useEffect(() => {
    const mockNodes: LucidNode[] = [
      {
        id: 'node-1',
        name: 'processUserData',
        type: 'function',
        filePath: 'src/utils/user.ts',
        line: 45,
        status: 'active',
        dependencies: ['validateInput', 'sanitizeData'],
        dependents: ['handleUserRequest'],
        lastModified: new Date(Date.now() - 1000 * 60 * 30),
        complexity: 3,
        testCoverage: 0.85
      },
      {
        id: 'node-2',
        name: 'UserComponent',
        type: 'component',
        filePath: 'src/components/User.tsx',
        line: 12,
        status: 'active',
        dependencies: ['processUserData', 'UserTypes'],
        dependents: ['App', 'UserList'],
        lastModified: new Date(Date.now() - 1000 * 60 * 15),
        complexity: 2,
        testCoverage: 0.92
      },
      {
        id: 'node-3',
        name: 'validateInput',
        type: 'function',
        filePath: 'src/utils/validation.ts',
        line: 8,
        status: 'warning',
        dependencies: [],
        dependents: ['processUserData'],
        lastModified: new Date(Date.now() - 1000 * 60 * 5),
        complexity: 1,
        testCoverage: 0.78
      }
    ];

    const mockEvents: TimelineEvent[] = [
      {
        id: 'event-1',
        nodeId: 'node-1',
        timestamp: 0,
        type: 'execution',
        duration: 150,
        status: 'success',
        message: 'processUserData executed successfully'
      },
      {
        id: 'event-2',
        nodeId: 'node-2',
        timestamp: 200,
        type: 'execution',
        duration: 80,
        status: 'success',
        message: 'UserComponent rendered'
      },
      {
        id: 'event-3',
        nodeId: 'node-3',
        timestamp: 300,
        type: 'error',
        duration: 0,
        status: 'error',
        message: 'Validation failed: invalid email format'
      },
      {
        id: 'event-4',
        nodeId: 'node-1',
        timestamp: 400,
        type: 'test',
        duration: 120,
        status: 'success',
        message: 'processUserData test passed'
      }
    ];

    const mockSpecs: SpecBlock[] = [
      {
        id: 'spec-1',
        nodeId: 'node-1',
        title: 'processUserData Contract',
        description: 'Processes user data with validation and sanitization',
        requirements: [
          'Must validate all input fields',
          'Must sanitize data before processing',
          'Must return processed data within 200ms'
        ],
        constraints: [
          'Cannot process more than 1000 records at once',
          'Must log all processing activities'
        ],
        status: 'valid',
        lastChecked: new Date()
      },
      {
        id: 'spec-2',
        nodeId: 'node-2',
        title: 'UserComponent Behavior',
        description: 'React component for displaying user information',
        requirements: [
          'Must display user name and email',
          'Must handle loading and error states',
          'Must be accessible (WCAG 2.1 AA)'
        ],
        constraints: [
          'Cannot exceed 50KB bundle size',
          'Must render within 100ms'
        ],
        status: 'valid',
        lastChecked: new Date()
      }
    ];

    setSpecBlocks(mockSpecs);
  }, []);

  const getNodeStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-900/20';
      case 'warning': return 'text-yellow-400 bg-yellow-900/20';
      case 'error': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getEventStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getSpecStatusColor = (status: string) => {
    switch (status) {
      case 'valid': return 'text-green-400 bg-green-900/20';
      case 'violated': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  return (
    <div className="h-full bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-purple-400" />
            <h1 className="text-xl font-bold">Lucid Orchestrator</h1>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>System Active</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoSync(!autoSync)}
            className={`p-2 rounded ${autoSync ? 'bg-blue-600' : 'bg-gray-700'} hover:bg-blue-700`}
            title="Auto Sync"
          >
            <Zap className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`p-2 rounded ${showGrid ? 'bg-blue-600' : 'bg-gray-700'} hover:bg-blue-700`}
            title="Show Grid"
          >
            <Target className="w-4 h-4" />
          </button>
          <button className="p-2 rounded bg-gray-700 hover:bg-gray-600" title="Settings">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Four-Pane Layout */}
      <div className="flex-1 flex">
        <PanelGroup direction="horizontal" className="flex-1">
          {/* Left: Code Pane */}
          <Panel defaultSize={25} minSize={20} className="border-r border-gray-700">
            <div className="h-full flex flex-col">
              <div className="p-3 border-b border-gray-700 bg-gray-800">
                <div className="flex items-center gap-2">
                  <Code className="w-4 h-4 text-blue-400" />
                  <span className="font-medium">Code</span>
                </div>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-3">
                  <div className="text-sm text-gray-400 mb-3">System Nodes</div>
                  {[
                    { id: 'node-1', name: 'processUserData', type: 'function', status: 'active' },
                    { id: 'node-2', name: 'UserComponent', type: 'component', status: 'active' },
                    { id: 'node-3', name: 'validateInput', type: 'function', status: 'warning' }
                  ].map((node) => (
                    <div
                      key={node.id}
                      onClick={() => setSelectedNode(node as any)}
                      className={`p-3 rounded cursor-pointer border ${
                        selectedNode?.id === node.id 
                          ? 'border-blue-500 bg-blue-900/20' 
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">{node.name}</span>
                        <span className={`px-2 py-1 rounded text-xs ${getNodeStatusColor(node.status)}`}>
                          {node.status}
                        </span>
                      </div>
                      <div className="text-xs text-gray-400">{node.type}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Panel>

          <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />

          {/* Center: Blueprint Pane */}
          <Panel defaultSize={35} minSize={25} className="border-r border-gray-700">
            <div className="h-full flex flex-col">
              <div className="p-3 border-b border-gray-700 bg-gray-800">
                <div className="flex items-center gap-2">
                  <Network className="w-4 h-4 text-green-400" />
                  <span className="font-medium">Blueprint</span>
                </div>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-4">
                  <div className="text-sm text-gray-400 mb-3">System Architecture</div>
                  
                  {/* Visual Graph Representation */}
                  <div className="relative h-64 bg-gray-800 rounded border border-gray-600 p-4">
                    {showGrid && (
                      <div className="absolute inset-0 opacity-20">
                        <svg className="w-full h-full">
                          <defs>
                            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="1"/>
                            </pattern>
                          </defs>
                          <rect width="100%" height="100%" fill="url(#grid)" />
                        </svg>
                      </div>
                    )}
                    
                    {/* Node Visualizations */}
                    <div className="relative z-10 flex items-center justify-center h-full">
                      <div className="flex items-center gap-8">
                        <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                          A
                        </div>
                        <div className="w-8 h-1 bg-gray-500"></div>
                        <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center text-white font-bold">
                          B
                        </div>
                        <div className="w-8 h-1 bg-gray-500"></div>
                        <div className="w-16 h-16 bg-yellow-600 rounded-full flex items-center justify-center text-white font-bold">
                          C
                        </div>
                      </div>
                    </div>
                  </div>

                  {selectedNode && (
                    <div className="mt-4 p-3 bg-gray-800 rounded border border-gray-600">
                      <h3 className="font-medium mb-2">{selectedNode.name}</h3>
                      <div className="text-sm text-gray-400 space-y-1">
                        <div>Type: {selectedNode.type}</div>
                        <div>File: {selectedNode.filePath}</div>
                        <div>Line: {selectedNode.line}</div>
                        <div>Complexity: {selectedNode.complexity}/10</div>
                        <div>Test Coverage: {Math.round(selectedNode.testCoverage * 100)}%</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Panel>

          <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />

          {/* Right: Spec Pane */}
          <Panel defaultSize={20} minSize={15} className="border-r border-gray-700">
            <div className="h-full flex flex-col">
              <div className="p-3 border-b border-gray-700 bg-gray-800">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-purple-400" />
                  <span className="font-medium">Spec</span>
                </div>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-3">
                  <div className="text-sm text-gray-400 mb-3">Living Documentation</div>
                  {specBlocks.map((spec) => (
                    <div key={spec.id} className="p-3 bg-gray-800 rounded border border-gray-600">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-sm">{spec.title}</h4>
                        <span className={`px-2 py-1 rounded text-xs ${getSpecStatusColor(spec.status)}`}>
                          {spec.status}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mb-2">{spec.description}</p>
                      <div className="space-y-1">
                        <div className="text-xs font-medium text-gray-300">Requirements:</div>
                        {spec.requirements.slice(0, 2).map((req, i) => (
                          <div key={i} className="text-xs text-gray-400">• {req}</div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Panel>

          <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600" />

          {/* Rightmost: System Overview Pane */}
          <Panel defaultSize={20} minSize={15}>
            <div className="h-full flex flex-col">
              <div className="p-3 border-b border-gray-700 bg-gray-800">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-orange-400" />
                  <span className="font-medium">System Overview</span>
                </div>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-4">
                  <div className="text-sm text-gray-400 mb-3">System Health</div>
                  
                  {/* Health Metrics */}
                  <div className="space-y-3">
                    <div className="p-3 bg-gray-800 rounded border border-gray-600">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Active Nodes</span>
                        <span className="text-green-400 text-sm">3</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded h-2">
                        <div className="bg-green-500 h-2 rounded" style={{ width: '75%' }}></div>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-gray-800 rounded border border-gray-600">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Test Coverage</span>
                        <span className="text-blue-400 text-sm">85%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded h-2">
                        <div className="bg-blue-500 h-2 rounded" style={{ width: '85%' }}></div>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-gray-800 rounded border border-gray-600">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Spec Compliance</span>
                        <span className="text-purple-400 text-sm">92%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded h-2">
                        <div className="bg-purple-500 h-2 rounded" style={{ width: '92%' }}></div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="mt-6">
                    <div className="text-sm text-gray-400 mb-3">Quick Actions</div>
                    <div className="space-y-2">
                      <button className="w-full p-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                        Open Timeline
                      </button>
                      <button className="w-full p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                        Generate Specs
                      </button>
                      <button className="w-full p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                        Run Analysis
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};
