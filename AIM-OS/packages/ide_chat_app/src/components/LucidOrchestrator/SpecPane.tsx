/**
 * Spec Pane Component
 * 
 * Displays specifications, compliance checking, and quality monitoring
 * for the Lucid Orchestrator. Consumes data from the SpecPaneService.
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Filter,
  Search,
  Download,
  RefreshCw,
  Settings,
  BarChart3,
  Shield,
  Target,
  BookOpen,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { SpecPaneData, Specification, Violation, Warning, Recommendation } from '../../../lucid_orchestrator/data_models/core_interfaces';

interface SpecPaneProps {
  data: SpecPaneData;
  onSpecSelect?: (spec: Specification) => void;
  onRefresh?: () => void;
  className?: string;
}

export const SpecPane: React.FC<SpecPaneProps> = ({ 
  data, 
  onSpecSelect, 
  onRefresh,
  className = '' 
}) => {
  const [selectedSpec, setSelectedSpec] = useState<Specification | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [showViolations, setShowViolations] = useState(true);
  const [showWarnings, setShowWarnings] = useState(true);
  const [showRecommendations, setShowRecommendations] = useState(true);

  // Get all specifications
  const allSpecs = useMemo(() => {
    return [
      ...data.specs.requirements,
      ...data.specs.constraints,
      ...data.specs.standards,
      ...data.specs.guidelines
    ];
  }, [data.specs]);

  // Filter specifications
  const filteredSpecs = useMemo(() => {
    return allSpecs.filter(spec => {
      const matchesSearch = !searchTerm || 
        spec.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        spec.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesType = filterType === 'all' || spec.type === filterType;
      const matchesPriority = filterPriority === 'all' || spec.priority === filterPriority;
      const matchesStatus = filterStatus === 'all' || spec.status === filterStatus;
      
      return matchesSearch && matchesType && matchesPriority && matchesStatus;
    });
  }, [allSpecs, searchTerm, filterType, filterPriority, filterStatus]);

  // Get priority color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'deprecated':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get type icon
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'requirement':
        return <Target className="w-4 h-4" />;
      case 'constraint':
        return <Shield className="w-4 h-4" />;
      case 'standard':
        return <BookOpen className="w-4 h-4" />;
      case 'guideline':
        return <Settings className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  // Get violation icon
  const getViolationIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'info':
        return <Clock className="w-4 h-4 text-blue-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-500" />;
    }
  };

  // Handle spec selection
  const handleSpecSelect = (spec: Specification) => {
    setSelectedSpec(spec);
    onSpecSelect?.(spec);
  };

  // Get compliance score color
  const getComplianceScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get quality trend icon
  const getQualityTrendIcon = (quality: number) => {
    if (quality > 0.8) return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (quality < 0.5) return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <BarChart3 className="w-4 h-4 text-gray-500" />;
  };

  return (
    <div className={`h-full flex flex-col bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Spec Pane</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={onRefresh}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              title="Export"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search specifications..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Types</option>
            <option value="requirement">Requirements</option>
            <option value="constraint">Constraints</option>
            <option value="standard">Standards</option>
            <option value="guideline">Guidelines</option>
          </select>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="deprecated">Deprecated</option>
            <option value="draft">Draft</option>
          </select>
        </div>

        {/* Toggle switches */}
        <div className="flex items-center space-x-4 mt-3">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showViolations}
              onChange={(e) => setShowViolations(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Show Violations</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showWarnings}
              onChange={(e) => setShowWarnings(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Show Warnings</span>
          </label>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={showRecommendations}
              onChange={(e) => setShowRecommendations(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Show Recommendations</span>
          </label>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Specifications List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <div className="space-y-3">
              {filteredSpecs.map((spec) => (
                <div
                  key={spec.id}
                  onClick={() => handleSpecSelect(spec)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                    selectedSpec?.id === spec.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getTypeIcon(spec.type)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{spec.title}</h4>
                          <span className={`px-2 py-1 text-xs rounded-full border ${getPriorityColor(spec.priority)}`}>
                            {spec.priority}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(spec.status)}`}>
                            {spec.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{spec.description}</p>
                        
                        {/* Content preview */}
                        <div className="space-y-1">
                          {spec.content.must.length > 0 && (
                            <div className="text-xs text-gray-500">
                              <span className="font-medium">Must:</span> {spec.content.must.length} items
                            </div>
                          )}
                          {spec.content.mustNot.length > 0 && (
                            <div className="text-xs text-gray-500">
                              <span className="font-medium">Must Not:</span> {spec.content.mustNot.length} items
                            </div>
                          )}
                          {spec.content.should.length > 0 && (
                            <div className="text-xs text-gray-500">
                              <span className="font-medium">Should:</span> {spec.content.should.length} items
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {spec.violations.length > 0 && showViolations && (
                        <div className="flex items-center space-x-1 text-red-600">
                          <XCircle className="w-4 h-4" />
                          <span className="text-sm font-medium">{spec.violations.length}</span>
                        </div>
                      )}
                      
                      <div className="text-xs text-gray-500">
                        v{spec.version}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Details Sidebar */}
        <div className="w-96 border-l border-gray-200 bg-white overflow-y-auto">
          <div className="p-4">
            {/* Quality Metrics */}
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Quality Metrics</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">Spec Completeness</span>
                    {getQualityTrendIcon(data.quality.specCompleteness)}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(data.quality.specCompleteness * 100).toFixed(1)}%
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">Doc Alignment</span>
                    {getQualityTrendIcon(data.quality.docAlignment)}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(data.quality.docAlignment * 100).toFixed(1)}%
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">Compliance Rate</span>
                    {getQualityTrendIcon(data.quality.complianceRate)}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(data.quality.complianceRate * 100).toFixed(1)}%
                  </div>
                </div>
                
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">Overall Health</span>
                    {getQualityTrendIcon(data.quality.overallHealth)}
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(data.quality.overallHealth * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Compliance Status */}
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Compliance Status</h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Overall Score</span>
                  <span className={`text-2xl font-bold ${getComplianceScoreColor(data.compliance.overallScore)}`}>
                    {(data.compliance.overallScore * 100).toFixed(1)}%
                  </span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Violations</span>
                    <span className="font-medium text-red-600">{data.compliance.violations.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Warnings</span>
                    <span className="font-medium text-yellow-600">{data.compliance.warnings.length}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Recommendations</span>
                    <span className="font-medium text-blue-600">{data.compliance.recommendations.length}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Selected Spec Details */}
            {selectedSpec && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Specification Details</h4>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Title</label>
                    <p className="text-gray-900">{selectedSpec.title}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Description</label>
                    <p className="text-gray-900 text-sm">{selectedSpec.description}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Type</label>
                    <p className="text-gray-900 capitalize">{selectedSpec.type}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Priority</label>
                    <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(selectedSpec.priority)}`}>
                      {selectedSpec.priority}
                    </span>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(selectedSpec.status)}`}>
                      {selectedSpec.status}
                    </span>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Version</label>
                    <p className="text-gray-900">v{selectedSpec.version}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Author</label>
                    <p className="text-gray-900">{selectedSpec.author}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Last Updated</label>
                    <p className="text-gray-900 text-sm">
                      {new Date(selectedSpec.updated).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Violations */}
            {showViolations && data.compliance.violations.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Violations</h4>
                <div className="space-y-2">
                  {data.compliance.violations.slice(0, 5).map((violation) => (
                    <div key={violation.id} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        {getViolationIcon(violation.severity)}
                        <div className="flex-1">
                          <p className="text-sm font-medium text-red-900">{violation.message}</p>
                          {violation.suggestion && (
                            <p className="text-xs text-red-700 mt-1">{violation.suggestion}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {showWarnings && data.compliance.warnings.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Warnings</h4>
                <div className="space-y-2">
                  {data.compliance.warnings.slice(0, 5).map((warning) => (
                    <div key={warning.id} className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-yellow-900">{warning.message}</p>
                          <p className="text-xs text-yellow-700 mt-1">{warning.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {showRecommendations && data.compliance.recommendations.length > 0 && (
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h4>
                <div className="space-y-2">
                  {data.compliance.recommendations.slice(0, 5).map((rec) => (
                    <div key={rec.id} className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-blue-600" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-blue-900">{rec.message}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`text-xs px-2 py-1 rounded ${
                              rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                              rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {rec.priority}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded ${
                              rec.effort === 'high' ? 'bg-red-100 text-red-800' :
                              rec.effort === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {rec.effort} effort
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
