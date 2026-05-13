/**
 * Lucid Orchestrator Main Component
 * 
 * Integrates all four panes (Code, Blueprint, Spec, Timeline) and provides
 * unified data management and cross-pane synchronization.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Code, 
  Network, 
  FileText, 
  Clock, 
  RefreshCw, 
  Settings, 
  Download,
  Maximize2,
  Minimize2,
  Split,
  Grid3X3,
  BarChart3,
  Activity
} from 'lucide-react';
import { CodePane } from './CodePane';
import { BlueprintPane } from './BlueprintPane';
import { SpecPane } from './SpecPane';
import { TimelinePane } from './TimelinePane';
import { LucidOrchestratorData, CodePaneData, BlueprintPaneData, SpecPaneData, TimelinePaneData } from '../../../lucid_orchestrator/data_models/core_interfaces';
import { LucidOrchestratorService } from '../../../lucid_orchestrator/data_services/lucid_orchestrator_service';
import { 
  RealtimeCollaborationService, 
  AnalyticsService, 
  PerformanceService, 
  TestingService 
} from '../../services';

interface LucidOrchestratorMainProps {
  systemId?: string;
  onSystemChange?: (systemId: string) => void;
  className?: string;
}

export const LucidOrchestratorMain: React.FC<LucidOrchestratorMainProps> = ({ 
  systemId = 'cmc',
  onSystemChange,
  className = '' 
}) => {
  const [orchestratorData, setOrchestratorData] = useState<LucidOrchestratorData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activePane, setActivePane] = useState<'code' | 'blueprint' | 'spec' | 'timeline'>('code');
  const [viewMode, setViewMode] = useState<'single' | 'split' | 'grid'>('single');
  const [selectedSystem, setSelectedSystem] = useState(systemId);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Initialize orchestrator service
  const [orchestrator] = useState(() => new LucidOrchestratorService('knowledge_architecture/systems'));
  
  // Initialize additional services
  const [collaborationService] = useState(() => new RealtimeCollaborationService());
  const [analyticsService] = useState(() => new AnalyticsService());
  const [performanceService] = useState(() => new PerformanceService());
  const [testingService] = useState(() => new TestingService());

  // Load system data
  const loadSystemData = useCallback(async (systemId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await orchestrator.loadSystem(systemId);
      setOrchestratorData(data);
      onSystemChange?.(systemId);
      
      // Run analytics on loaded data
      analyticsService.analyzeSystem(data);
      
      // Run performance tests
      testingService.runAllTests(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load system data');
      console.error('Error loading system data:', err);
    } finally {
      setLoading(false);
    }
  }, [orchestrator, onSystemChange]);

  // Load initial system
  useEffect(() => {
    loadSystemData(selectedSystem);
  }, [selectedSystem, loadSystemData]);

  // Subscribe to data changes
  useEffect(() => {
    const unsubscribe = orchestrator.subscribeToChanges((data) => {
      setOrchestratorData(data);
    });

    return unsubscribe;
  }, [orchestrator]);

  // Subscribe to analytics updates
  useEffect(() => {
    const handleInsightsUpdate = (insights: any[]) => {
      console.log('Analytics insights updated:', insights);
    };

    analyticsService.on('insights_updated', handleInsightsUpdate);
    return () => {
      analyticsService.off('insights_updated', handleInsightsUpdate);
    };
  }, [analyticsService]);

  // Subscribe to performance updates
  useEffect(() => {
    const handlePerformanceUpdate = (metrics: any) => {
      console.log('Performance metrics updated:', metrics);
    };

    performanceService.on('render_metrics', handlePerformanceUpdate);
    performanceService.on('memory_metrics', handlePerformanceUpdate);
    return () => {
      performanceService.off('render_metrics', handlePerformanceUpdate);
      performanceService.off('memory_metrics', handlePerformanceUpdate);
    };
  }, [performanceService]);

  // Subscribe to collaboration updates
  useEffect(() => {
    const handleCollaborationUpdate = (state: any) => {
      console.log('Collaboration state updated:', state);
    };

    collaborationService.on('state_changed', handleCollaborationUpdate);
    return () => {
      collaborationService.off('state_changed', handleCollaborationUpdate);
    };
  }, [collaborationService]);

  // Cleanup services on unmount
  useEffect(() => {
    return () => {
      collaborationService.cleanup();
      analyticsService.cleanup();
      performanceService.cleanup();
      testingService.cleanup();
    };
  }, [collaborationService, analyticsService, performanceService, testingService]);

  // Handle system change
  const handleSystemChange = (newSystemId: string) => {
    setSelectedSystem(newSystemId);
    loadSystemData(newSystemId);
  };

  // Handle refresh
  const handleRefresh = async () => {
    if (selectedSystem) {
      await loadSystemData(selectedSystem);
    }
  };

  // Handle node move in blueprint
  const handleNodeMove = useCallback(async (nodeId: string, position: { x: number; y: number }) => {
    if (!orchestratorData) return;
    
    try {
      const blueprintService = orchestrator.getServices().blueprint;
      await blueprintService.updateNodePosition(nodeId, position);
      
      // Update local data
      setOrchestratorData(prev => {
        if (!prev) return null;
        
        const updatedBlueprint = { ...prev.blueprint };
        const nodeIndex = updatedBlueprint.architecture.nodes.findIndex(n => n.id === nodeId);
        if (nodeIndex !== -1) {
          updatedBlueprint.architecture.nodes[nodeIndex] = {
            ...updatedBlueprint.architecture.nodes[nodeIndex],
            position
          };
        }
        
        return {
          ...prev,
          blueprint: updatedBlueprint
        };
      });
    } catch (err) {
      console.error('Error updating node position:', err);
    }
  }, [orchestrator, orchestratorData]);

  // Handle file selection in code pane
  const handleFileSelect = useCallback((file: any) => {
    console.log('File selected:', file);
    // Could trigger cross-pane updates here
  }, []);

  // Handle spec selection in spec pane
  const handleSpecSelect = useCallback((spec: any) => {
    console.log('Spec selected:', spec);
    // Could trigger cross-pane updates here
  }, []);

  // Handle event selection in timeline pane
  const handleEventSelect = useCallback((event: any) => {
    console.log('Event selected:', event);
    // Could trigger cross-pane updates here
  }, []);

  // Export data
  const handleExport = async (format: 'json' | 'graphml' | 'dot' = 'json') => {
    if (!selectedSystem) return;
    
    try {
      const exportData = await orchestrator.exportSystem(selectedSystem, format);
      const blob = new Blob([exportData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedSystem}_export.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting data:', err);
    }
  };

  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Get pane icon
  const getPaneIcon = (pane: string) => {
    switch (pane) {
      case 'code':
        return <Code className="w-4 h-4" />;
      case 'blueprint':
        return <Network className="w-4 h-4" />;
      case 'spec':
        return <FileText className="w-4 h-4" />;
      case 'timeline':
        return <Clock className="w-4 h-4" />;
      default:
        return <Code className="w-4 h-4" />;
    }
  };

  // Render single pane
  const renderSinglePane = () => {
    if (!orchestratorData) return null;

    switch (activePane) {
      case 'code':
        return (
          <CodePane
            data={orchestratorData.code}
            onFileSelect={handleFileSelect}
            onRefresh={handleRefresh}
          />
        );
      case 'blueprint':
        return (
          <BlueprintPane
            data={orchestratorData.blueprint}
            onNodeMove={handleNodeMove}
            onRefresh={handleRefresh}
          />
        );
      case 'spec':
        return (
          <SpecPane
            data={orchestratorData.spec}
            onSpecSelect={handleSpecSelect}
            onRefresh={handleRefresh}
          />
        );
      case 'timeline':
        return (
          <TimelinePane
            data={orchestratorData.timeline}
            onEventSelect={handleEventSelect}
            onRefresh={handleRefresh}
          />
        );
      default:
        return null;
    }
  };

  // Render split view
  const renderSplitView = () => {
    if (!orchestratorData) return null;

    return (
      <div className="flex h-full">
        <div className="flex-1">
          {activePane === 'code' && (
            <CodePane
              data={orchestratorData.code}
              onFileSelect={handleFileSelect}
              onRefresh={handleRefresh}
            />
          )}
          {activePane === 'blueprint' && (
            <BlueprintPane
              data={orchestratorData.blueprint}
              onNodeMove={handleNodeMove}
              onRefresh={handleRefresh}
            />
          )}
          {activePane === 'spec' && (
            <SpecPane
              data={orchestratorData.spec}
              onSpecSelect={handleSpecSelect}
              onRefresh={handleRefresh}
            />
          )}
          {activePane === 'timeline' && (
            <TimelinePane
              data={orchestratorData.timeline}
              onEventSelect={handleEventSelect}
              onRefresh={handleRefresh}
            />
          )}
        </div>
        <div className="w-80 border-l border-gray-200 bg-white">
          <div className="p-4">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">System Overview</h4>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">System</label>
                <p className="text-gray-900">{orchestratorData.metadata.name}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <p className="text-gray-900 capitalize">{orchestratorData.metadata.status}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Last Updated</label>
                <p className="text-gray-900 text-sm">
                  {new Date(orchestratorData.metadata.updatedAt).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render grid view
  const renderGridView = () => {
    if (!orchestratorData) return null;

    return (
      <div className="grid grid-cols-2 h-full">
        <div className="border-r border-gray-200">
          <CodePane
            data={orchestratorData.code}
            onFileSelect={handleFileSelect}
            onRefresh={handleRefresh}
          />
        </div>
        <div className="border-r border-gray-200">
          <BlueprintPane
            data={orchestratorData.blueprint}
            onNodeMove={handleNodeMove}
            onRefresh={handleRefresh}
          />
        </div>
        <div className="border-r border-gray-200">
          <SpecPane
            data={orchestratorData.spec}
            onSpecSelect={handleSpecSelect}
            onRefresh={handleRefresh}
          />
        </div>
        <div>
          <TimelinePane
            data={orchestratorData.timeline}
            onEventSelect={handleEventSelect}
            onRefresh={handleRefresh}
          />
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className={`h-full flex items-center justify-center bg-gray-50 ${className}`}>
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading system data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`h-full flex items-center justify-center bg-gray-50 ${className}`}>
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <Activity className="w-8 h-8 mx-auto mb-2" />
            <p className="text-lg font-medium">Error Loading System</p>
          </div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!orchestratorData) {
    return (
      <div className={`h-full flex items-center justify-center bg-gray-50 ${className}`}>
        <div className="text-center">
          <p className="text-gray-600">No system data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`h-full flex flex-col bg-gray-50 ${isFullscreen ? 'fixed inset-0 z-50' : ''} ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <h2 className="text-xl font-semibold text-gray-900">Lucid Orchestrator</h2>
            <div className="flex items-center space-x-2">
              <select
                value={selectedSystem}
                onChange={(e) => handleSystemChange(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="cmc">CMC</option>
                <option value="hhni">HHNI</option>
                <option value="vif">VIF</option>
                <option value="seg">SEG</option>
                <option value="apoe">APOE</option>
                <option value="sdfcvf">SDF-CVF</option>
              </select>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            
            <button
              onClick={() => handleExport('json')}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Export JSON"
            >
              <Download className="w-4 h-4" />
            </button>
            
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Toggle Fullscreen"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Pane Tabs */}
        <div className="flex items-center space-x-1">
          {(['code', 'blueprint', 'spec', 'timeline'] as const).map((pane) => (
            <button
              key={pane}
              onClick={() => setActivePane(pane)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                activePane === pane
                  ? 'bg-blue-100 text-blue-800'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
            >
              {getPaneIcon(pane)}
              <span className="capitalize">{pane}</span>
            </button>
          ))}
        </div>

        {/* View Mode Controls */}
        <div className="flex items-center space-x-2 mt-4">
          <span className="text-sm text-gray-600">View:</span>
          <button
            onClick={() => setViewMode('single')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'single'
                ? 'bg-blue-100 text-blue-800'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
            }`}
            title="Single Pane"
          >
            <Split className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('split')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'split'
                ? 'bg-blue-100 text-blue-800'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
            }`}
            title="Split View"
          >
            <BarChart3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'grid'
                ? 'bg-blue-100 text-blue-800'
                : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
            }`}
            title="Grid View"
          >
            <Grid3X3 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'single' && renderSinglePane()}
        {viewMode === 'split' && renderSplitView()}
        {viewMode === 'grid' && renderGridView()}
      </div>
    </div>
  );
};
