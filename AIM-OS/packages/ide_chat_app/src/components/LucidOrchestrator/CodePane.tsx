/**
 * Code Pane Component
 * 
 * Displays file system, dependencies, and code metrics for the Lucid Orchestrator.
 * Consumes data from the CodePaneService.
 */

import React, { useState, useEffect, useMemo } from 'react';
import { 
  FileText, 
  Code, 
  TestTube, 
  Settings, 
  BarChart3, 
  GitBranch, 
  Search,
  Filter,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { CodePaneData, FileInfo, CodeMetrics, DependencyGraph } from '../../../lucid_orchestrator/data_models/core_interfaces';

interface CodePaneProps {
  data: CodePaneData;
  onFileSelect?: (file: FileInfo) => void;
  onRefresh?: () => void;
  className?: string;
}

export const CodePane: React.FC<CodePaneProps> = ({ 
  data, 
  onFileSelect, 
  onRefresh,
  className = '' 
}) => {
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'size' | 'lines' | 'complexity'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Filter and sort files
  const filteredFiles = useMemo(() => {
    let files: FileInfo[] = [];
    
    // Combine all files
    files = [
      ...data.files.documentation,
      ...data.files.source,
      ...data.files.tests,
      ...data.files.config,
      ...data.files.other
    ];

    // Apply search filter
    if (searchTerm) {
      files = files.filter(file => 
        file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.path.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply type filter
    if (filterType !== 'all') {
      files = files.filter(file => {
        switch (filterType) {
          case 'documentation':
            return data.files.documentation.includes(file);
          case 'source':
            return data.files.source.includes(file);
          case 'tests':
            return data.files.tests.includes(file);
          case 'config':
            return data.files.config.includes(file);
          default:
            return true;
        }
      });
    }

    // Apply sorting
    files.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'size':
          aValue = a.size;
          bValue = b.size;
          break;
        case 'lines':
          aValue = a.lines;
          bValue = b.lines;
          break;
        case 'complexity':
          aValue = a.metadata.complexity || 0;
          bValue = b.metadata.complexity || 0;
          break;
        default:
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    return files;
  }, [data.files, searchTerm, filterType, sortBy, sortOrder]);

  // Get file type icon
  const getFileIcon = (file: FileInfo) => {
    switch (file.type) {
      case 'markdown':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'python':
        return <Code className="w-4 h-4 text-yellow-500" />;
      case 'typescript':
      case 'javascript':
        return <Code className="w-4 h-4 text-blue-600" />;
      case 'json':
      case 'yaml':
        return <Settings className="w-4 h-4 text-green-500" />;
      default:
        return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  // Get file type color
  const getFileTypeColor = (file: FileInfo) => {
    switch (file.type) {
      case 'markdown':
        return 'bg-blue-100 text-blue-800';
      case 'python':
        return 'bg-yellow-100 text-yellow-800';
      case 'typescript':
        return 'bg-blue-100 text-blue-800';
      case 'javascript':
        return 'bg-yellow-100 text-yellow-800';
      case 'json':
        return 'bg-green-100 text-green-800';
      case 'yaml':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get quality indicator
  const getQualityIndicator = (file: FileInfo) => {
    const complexity = file.metadata.complexity || 0;
    const testCoverage = file.metadata.testCoverage || 0;
    
    if (complexity > 8 || testCoverage < 0.5) {
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    } else if (complexity > 5 || testCoverage < 0.8) {
      return <Clock className="w-4 h-4 text-yellow-500" />;
    } else {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
  };

  // Handle file selection
  const handleFileSelect = (file: FileInfo) => {
    setSelectedFile(file);
    onFileSelect?.(file);
  };

  return (
    <div className={`h-full flex flex-col bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Code Pane</h3>
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

        {/* Search and Filters */}
        <div className="flex items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search files..."
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
            <option value="all">All Files</option>
            <option value="documentation">Documentation</option>
            <option value="source">Source Code</option>
            <option value="tests">Tests</option>
            <option value="config">Config</option>
          </select>

          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field as any);
              setSortOrder(order as any);
            }}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="name-asc">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
            <option value="size-desc">Size Large-Small</option>
            <option value="lines-desc">Lines Large-Small</option>
            <option value="complexity-desc">Complexity High-Low</option>
          </select>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* File List */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            <div className="space-y-2">
              {filteredFiles.map((file) => (
                <div
                  key={file.id}
                  onClick={() => handleFileSelect(file)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all hover:shadow-md ${
                    selectedFile?.id === file.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(file)}
                      <div>
                        <div className="font-medium text-gray-900">{file.name}</div>
                        <div className="text-sm text-gray-500">{file.path}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${getFileTypeColor(file)}`}>
                        {file.type}
                      </span>
                      
                      {file.metadata.level && (
                        <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full">
                          {file.metadata.level}
                        </span>
                      )}
                      
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <span>{file.lines} lines</span>
                        <span>•</span>
                        <span>{(file.size / 1024).toFixed(1)} KB</span>
                        {file.metadata.complexity && (
                          <>
                            <span>•</span>
                            <span>Complexity: {file.metadata.complexity.toFixed(1)}</span>
                          </>
                        )}
                      </div>
                      
                      {getQualityIndicator(file)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Metrics Sidebar */}
        <div className="w-80 border-l border-gray-200 bg-white overflow-y-auto">
          <div className="p-4">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Code Metrics</h4>
            
            {/* Overall Metrics */}
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Total Lines</span>
                  <BarChart3 className="w-4 h-4 text-gray-500" />
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {data.metrics.totalLines.toLocaleString()}
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Test Coverage</span>
                  <TestTube className="w-4 h-4 text-gray-500" />
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {(data.metrics.testCoverage * 100).toFixed(1)}%
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Code Quality</span>
                  <CheckCircle className="w-4 h-4 text-gray-500" />
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {(data.metrics.codeQuality * 100).toFixed(1)}%
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Complexity</span>
                  <GitBranch className="w-4 h-4 text-gray-500" />
                </div>
                <div className="text-2xl font-bold text-gray-900">
                  {data.metrics.complexity.toFixed(2)}
                </div>
              </div>
            </div>

            {/* Dependencies */}
            <div className="mt-6">
              <h5 className="text-sm font-semibold text-gray-700 mb-3">Dependencies</h5>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Internal</span>
                  <span className="font-medium">{data.dependencies.internal.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">External</span>
                  <span className="font-medium">{data.dependencies.external.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Documentation</span>
                  <span className="font-medium">{data.dependencies.documentation.length}</span>
                </div>
              </div>
            </div>

            {/* File Type Breakdown */}
            <div className="mt-6">
              <h5 className="text-sm font-semibold text-gray-700 mb-3">File Types</h5>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Documentation</span>
                  <span className="font-medium">{data.files.documentation.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Source Code</span>
                  <span className="font-medium">{data.files.source.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tests</span>
                  <span className="font-medium">{data.files.tests.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Config</span>
                  <span className="font-medium">{data.files.config.length}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
