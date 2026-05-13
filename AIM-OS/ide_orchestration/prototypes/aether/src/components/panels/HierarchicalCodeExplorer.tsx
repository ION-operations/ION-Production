// Enhanced Hierarchical Code Explorer V1
// Auto-expanding, auto-scrolling, auto-collapsing codebase explorer with connection visualization

import React, { useState, useEffect, useRef, useMemo } from 'react'
import { ChevronRight, ChevronDown, File, FolderOpen } from 'lucide-react'

interface Connection {
  targetPath: string
  type: 'imports' | 'uses' | 'depends_on' | 'exports_to'
  targetSection?: string
}

// Build comprehensive codebase structure with connections
const buildCodebaseStructure = () => {
  return {
    'src/': {
      'components/': {
        'AetherIDELayout.tsx': {
          type: 'file',
          exports: ['AetherIDELayout'],
          imports: ['react', 'react-resizable-panels', 'zustand'],
          connections: [
            { targetPath: 'src/components/panelMappings.ts', type: 'imports' },
            { targetPath: 'src/components/hooks/usePanelManagement.ts', type: 'imports' },
            { targetPath: 'src/components/ErrorBoundary.tsx', type: 'imports' },
            { targetPath: 'src/components/LoadingPanel.tsx', type: 'imports' },
            { targetPath: 'src/stores/panelStore.ts', type: 'imports' }
          ],
          sections: [
            { name: 'Top Bar', lines: [1, 50], connections: [
              { targetPath: 'src/components/panels/index.tsx', type: 'uses' }
            ]},
            { name: 'Left Drawer', lines: [51, 150] },
            { name: 'Main Content', lines: [151, 300] },
            { name: 'Right Drawer', lines: [301, 450] },
            { name: 'Bottom Drawer', lines: [451, 603] }
          ]
        },
        'ErrorBoundary.tsx': {
          type: 'file',
          exports: ['PanelErrorBoundary'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'Error Boundary Component', lines: [1, 80] }
          ]
        },
        'LoadingPanel.tsx': {
          type: 'file',
          exports: ['LoadingPanel', 'PanelSuspense'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'Loading States', lines: [1, 50] }
          ]
        },
        'panelMappings.ts': {
          type: 'file',
          exports: ['DEFAULT_PANEL_CONFIGS', 'PANEL_ID_MAP'],
          imports: [],
          connections: [],
          sections: [
            { name: 'Panel Configurations', lines: [1, 340] }
          ]
        },
        'hooks/': {
          'usePanelManagement.ts': {
            type: 'file',
            exports: ['usePanelInitialization', 'useActivePanel', 'usePanelControls'],
            imports: ['react', 'zustand'],
            connections: [
              { targetPath: 'src/stores/panelStore.ts', type: 'imports' },
              { targetPath: 'src/components/panelMappings.ts', type: 'imports' }
            ],
            sections: [
              { name: 'Panel Initialization', lines: [1, 41] },
              { name: 'Active Panel Hook', lines: [43, 64] },
              { name: 'Panel Controls', lines: [66, 76] }
            ]
          }
        },
        'panels/': {
          'AIMOSStatusPanel.tsx': {
            type: 'file',
            exports: ['AIMOSStatusPanel'],
            imports: ['react'],
            connections: [
              { targetPath: 'src/hooks/useAIMOS.ts', type: 'imports' }
            ],
            sections: [
              { name: 'AIM-OS Status Display', lines: [1, 200] }
            ]
          },
          'AIMOSStructurePanels.tsx': {
            type: 'file',
            exports: ['SuperIndexPanel', 'MasterIndexPanel', 'SystemMapPanel'],
            imports: ['react'],
            connections: [],
            sections: [
              { name: 'Structure Panels', lines: [1, 300] }
            ]
          },
          'DebugConsolePanel.tsx': {
            type: 'file',
            exports: ['DebugConsolePanel'],
            imports: ['react'],
            connections: [],
            sections: [
              { name: 'Debug Console', lines: [1, 250] }
            ]
          },
          'FileVersionHistory.tsx': {
            type: 'file',
            exports: ['FileVersionHistoryPanel', 'FileVersionHistoryPanelV2'],
            imports: ['react'],
            connections: [],
            sections: [
              { name: 'Version History', lines: [1, 500] }
            ]
          },
          'HierarchicalCodeExplorer.tsx': {
            type: 'file',
            exports: ['HierarchicalCodeExplorerV1', 'HierarchicalCodeExplorerV2', 'HierarchicalCodeExplorerV3'],
            imports: ['react'],
            connections: [],
            sections: [
              { name: 'V1: Tree-Based', lines: [1, 161] },
              { name: 'V2: Graph-Based', lines: [163, 229] },
              { name: 'V3: Semantic', lines: [231, 315] }
            ]
          },
          'index.tsx': {
            type: 'file',
            exports: ['FileExplorerPanel', 'ComponentLibraryPanel', 'AIMemoryPanel', 'EvolutionExplorerPanel'],
            imports: ['react'],
            connections: [
              { targetPath: 'src/components/panels/HierarchicalCodeExplorer.tsx', type: 'imports' },
              { targetPath: 'src/components/panels/AIMOSStatusPanel.tsx', type: 'imports' },
              { targetPath: 'src/components/panels/AIMOSStructurePanels.tsx', type: 'imports' }
            ],
            sections: [
              { name: 'Panel Exports', lines: [1, 1000] }
            ]
          }
        }
      },
      'hooks/': {
        'useAIMOS.ts': {
          type: 'file',
          exports: ['useAIMOS'],
          imports: ['react'],
          connections: [
            { targetPath: 'src/hooks/useCMC.ts', type: 'imports' },
            { targetPath: 'src/hooks/useHHNI.ts', type: 'imports' },
            { targetPath: 'src/hooks/useVIF.ts', type: 'imports' }
          ],
          sections: [
            { name: 'Unified AIM-OS Hook', lines: [1, 200] }
          ]
        },
        'useCMC.ts': {
          type: 'file',
          exports: ['useCMC'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'CMC Hook', lines: [1, 150] }
          ]
        },
        'useHHNI.ts': {
          type: 'file',
          exports: ['useHHNI'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'HHNI Hook', lines: [1, 150] }
          ]
        },
        'useVIF.ts': {
          type: 'file',
          exports: ['useVIF'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'VIF Hook', lines: [1, 150] }
          ]
        },
        'useSEG.ts': {
          type: 'file',
          exports: ['useSEG'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'SEG Hook', lines: [1, 150] }
          ]
        },
        'useAPOE.ts': {
          type: 'file',
          exports: ['useAPOE'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'APOE Hook', lines: [1, 150] }
          ]
        },
        'useTCS.ts': {
          type: 'file',
          exports: ['useTCS'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'TCS Hook', lines: [1, 150] }
          ]
        },
        'useCAS.ts': {
          type: 'file',
          exports: ['useCAS'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'CAS Hook', lines: [1, 150] }
          ]
        },
        'useSDFCVF.ts': {
          type: 'file',
          exports: ['useSDFCVF'],
          imports: ['react'],
          connections: [],
          sections: [
            { name: 'SDF-CVF Hook', lines: [1, 150] }
          ]
        },
        'index.ts': {
          type: 'file',
          exports: ['useAIMOS', 'useCMC', 'useHHNI'],
          imports: [],
          connections: [
            { targetPath: 'src/hooks/useAIMOS.ts', type: 'exports_to' },
            { targetPath: 'src/hooks/useCMC.ts', type: 'exports_to' },
            { targetPath: 'src/hooks/useHHNI.ts', type: 'exports_to' }
          ],
          sections: [
            { name: 'Hook Exports', lines: [1, 50] }
          ]
        },
        'types.ts': {
          type: 'file',
          exports: ['AIMOSTypes'],
          imports: [],
          connections: [],
          sections: [
            { name: 'Type Definitions', lines: [1, 100] }
          ]
        }
      },
      'stores/': {
        'panelStore.ts': {
          type: 'file',
          exports: ['usePanelStore'],
          imports: ['zustand'],
          connections: [],
          sections: [
            { name: 'Panel Store', lines: [1, 380] }
          ]
        },
        'index.ts': {
          type: 'file',
          exports: ['usePanelStore'],
          imports: [],
          connections: [
            { targetPath: 'src/stores/panelStore.ts', type: 'exports_to' }
          ],
          sections: [
            { name: 'Store Exports', lines: [1, 10] }
          ]
        }
      },
      'mockData/': {
        'index.ts': {
          type: 'file',
          exports: ['mockFileTree', 'mockTimeline'],
          imports: [],
          connections: [],
          sections: [
            { name: 'Mock Data', lines: [1, 200] }
          ]
        },
        'debugData.ts': {
          type: 'file',
          exports: ['mockDebugConsole'],
          imports: [],
          connections: [],
          sections: [
            { name: 'Debug Mock Data', lines: [1, 150] }
          ]
        }
      },
      'utils/': {
        'index.ts': {
          type: 'file',
          exports: ['utils'],
          imports: [],
          connections: [],
          sections: [
            { name: 'Utility Functions', lines: [1, 50] }
          ]
        }
      },
      'main.tsx': {
        type: 'file',
        exports: [],
        imports: ['react', 'react-dom'],
        connections: [
          { targetPath: 'src/components/AetherIDELayout.tsx', type: 'imports' }
        ],
        sections: [
          { name: 'App Entry Point', lines: [1, 20] }
        ]
      },
      'index.css': {
        type: 'file',
        exports: [],
        imports: [],
        connections: [],
        sections: [
          { name: 'Global Styles', lines: [1, 30] }
        ]
      }
    }
  }
}

interface HierarchicalCodeExplorerV1Props {
  activeFile?: string
  activeSection?: string
}

export const HierarchicalCodeExplorerV1: React.FC<HierarchicalCodeExplorerV1Props> = ({ 
  activeFile,
  activeSection 
}) => {
  const codebase = useMemo(() => buildCodebaseStructure(), [])
  const containerRef = useRef<HTMLDivElement>(null)
  const fileRefs = useRef<Record<string, HTMLDivElement | null>>({})
  const sectionRefs = useRef<Record<string, HTMLDivElement | null>>({})
  const svgRef = useRef<SVGSVGElement>(null)
  
  const [expanded, setExpanded] = useState<Set<string>>(() => {
    const allFolders = new Set<string>()
    const collectFolders = (tree: any, path: string = '') => {
      Object.entries(tree).forEach(([name, value]: [string, any]) => {
        const fullPath = path ? `${path}${name}` : name
        if (typeof value === 'object' && value !== null && !value.type) {
          allFolders.add(fullPath)
          collectFolders(value, fullPath)
        }
      })
    }
    collectFolders(codebase)
    return allFolders
  })
  
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())
  const [expandedFiles, setExpandedFiles] = useState<Set<string>>(new Set())
  const [selectedItem, setSelectedItem] = useState<{ type: 'file' | 'section' | 'folder', path: string, section?: string } | null>(null)

  // Auto-expand and scroll to active file
  useEffect(() => {
    if (!activeFile) return

    const pathParts = activeFile.split('/')
    let currentPath = ''
    const pathsToExpand = new Set<string>()
    
    pathParts.forEach((part, index) => {
      if (index < pathParts.length - 1) {
        currentPath = currentPath ? `${currentPath}${part}/` : `${part}/`
        pathsToExpand.add(currentPath)
      }
    })
    
    setExpanded(prev => {
      const newExpanded = new Set(prev)
      pathsToExpand.forEach(path => newExpanded.add(path))
      return newExpanded
    })
    
    setExpandedFiles(prev => new Set(prev).add(activeFile))
    
    if (activeSection) {
      setExpandedSections(prev => new Set(prev).add(`${activeFile}:${activeSection}`))
    }
    
    setTimeout(() => {
      const fileElement = fileRefs.current[activeFile]
      if (fileElement && containerRef.current) {
        fileElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        fileElement.classList.add('bg-blue-900/30', 'border-l-2', 'border-blue-400')
        setTimeout(() => {
          fileElement.classList.remove('bg-blue-900/30', 'border-l-2', 'border-blue-400')
        }, 2000)
      }
    }, 100)
  }, [activeFile, activeSection])

  // Auto-collapse inactive files/sections
  useEffect(() => {
    if (!activeFile) return
    
    setExpandedFiles(() => {
      const newSet = new Set<string>()
      if (activeFile) newSet.add(activeFile)
      return newSet
    })
    
    if (activeSection) {
      setExpandedSections(() => {
        const newSet = new Set<string>()
        newSet.add(`${activeFile}:${activeSection}`)
        return newSet
      })
    } else {
      setExpandedSections(new Set())
    }
  }, [activeFile, activeSection])

  // Get connections for selected item
  const getConnections = (): Connection[] => {
    if (!selectedItem) return []
    
    const findFile = (tree: any, targetPath: string): any => {
      const parts = targetPath.split('/').filter(p => p)
      let current = tree
      for (const part of parts) {
        if (current[part]) {
          current = current[part]
        } else {
          return null
        }
      }
      return current?.type === 'file' ? current : null
    }
    
    const file = findFile(codebase, selectedItem.path)
    if (!file) return []
    
    if (selectedItem.type === 'section' && selectedItem.section) {
      const section = file.sections?.find((s: any) => s.name === selectedItem.section)
      return section?.connections || []
    }
    
    return file.connections || []
  }

  // Draw connection lines
  useEffect(() => {
    if (!selectedItem || !svgRef.current || !containerRef.current) return
    
    const connections = getConnections()
    if (connections.length === 0) {
      svgRef.current.innerHTML = ''
      return
    }
    
    const svg = svgRef.current
    const container = containerRef.current
    
    // Update SVG size to match container
    svg.setAttribute('width', container.scrollWidth.toString())
    svg.setAttribute('height', container.scrollHeight.toString())
    
    // Clear previous lines
    svg.innerHTML = ''
    
    const sourceElement = selectedItem.type === 'section' && selectedItem.section
      ? sectionRefs.current[`${selectedItem.path}:${selectedItem.section}`]
      : fileRefs.current[selectedItem.path]
    
    if (!sourceElement) return
    
    // Get positions relative to container
    const sourceRect = sourceElement.getBoundingClientRect()
    const containerRect = container.getBoundingClientRect()
    const sourceX = sourceRect.left - containerRect.left + container.scrollLeft
    const sourceY = sourceRect.top - containerRect.top + sourceRect.height / 2 + container.scrollTop
    const highwayX = 20 // Left margin for highway
    
    connections.forEach((conn, idx) => {
      const targetElement = fileRefs.current[conn.targetPath]
      if (!targetElement) return
      
      const targetRect = targetElement.getBoundingClientRect()
      const targetX = targetRect.left - containerRect.left + container.scrollLeft
      const targetY = targetRect.top - containerRect.top + targetRect.height / 2 + container.scrollTop
      
      // Create path: left from source → vertical highway → horizontal → target
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      const d = `M ${sourceX} ${sourceY} 
                 L ${highwayX} ${sourceY} 
                 L ${highwayX} ${targetY} 
                 L ${targetX} ${targetY}`
      path.setAttribute('d', d)
      path.setAttribute('stroke', idx % 2 === 0 ? '#3b82f6' : '#8b5cf6')
      path.setAttribute('stroke-width', '1.5')
      path.setAttribute('fill', 'none')
      path.setAttribute('opacity', '0.6')
      path.setAttribute('marker-end', 'url(#arrowhead)')
      svg.appendChild(path)
    })
    
    // Add arrow marker
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs')
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker')
    marker.setAttribute('id', 'arrowhead')
    marker.setAttribute('markerWidth', '10')
    marker.setAttribute('markerHeight', '10')
    marker.setAttribute('refX', '9')
    marker.setAttribute('refY', '3')
    marker.setAttribute('orient', 'auto')
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon')
    polygon.setAttribute('points', '0 0, 10 3, 0 6')
    polygon.setAttribute('fill', '#3b82f6')
    marker.appendChild(polygon)
    defs.appendChild(marker)
    svg.appendChild(defs)
    
    // Update on scroll
    const updateLines = () => {
      if (!selectedItem || !sourceElement) return
      const currentConnections = getConnections()
      const sourceRect = sourceElement.getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      const sourceX = sourceRect.left - containerRect.left + container.scrollLeft
      const sourceY = sourceRect.top - containerRect.top + sourceRect.height / 2 + container.scrollTop
      
      const paths = svg.querySelectorAll('path')
      paths.forEach((path, idx) => {
        const conn = currentConnections[idx]
        if (!conn) return
        const targetElement = fileRefs.current[conn.targetPath]
        if (!targetElement) return
        
        const targetRect = targetElement.getBoundingClientRect()
        const targetX = targetRect.left - containerRect.left + container.scrollLeft
        const targetY = targetRect.top - containerRect.top + targetRect.height / 2 + container.scrollTop
        
        const d = `M ${sourceX} ${sourceY} 
                   L ${highwayX} ${sourceY} 
                   L ${highwayX} ${targetY} 
                   L ${targetX} ${targetY}`
        path.setAttribute('d', d)
      })
    }
    
    container.addEventListener('scroll', updateLines)
    window.addEventListener('resize', updateLines)
    
    return () => {
      container.removeEventListener('scroll', updateLines)
      window.removeEventListener('resize', updateLines)
    }
  }, [selectedItem, expanded, expandedFiles, expandedSections])

  const toggleExpand = (path: string) => {
    setExpanded(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(path)) {
        newExpanded.delete(path)
      } else {
        newExpanded.add(path)
      }
      return newExpanded
    })
  }

  const toggleFile = (filePath: string) => {
    setExpandedFiles(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(filePath)) {
        newExpanded.delete(filePath)
        setSelectedItem(null)
      } else {
        newExpanded.add(filePath)
        setSelectedItem({ type: 'file', path: filePath })
      }
      return newExpanded
    })
  }

  const toggleSection = (filePath: string, sectionName: string) => {
    const key = `${filePath}:${sectionName}`
    setExpandedSections(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(key)) {
        newExpanded.delete(key)
        setSelectedItem(null)
      } else {
        newExpanded.add(key)
        setSelectedItem({ type: 'section', path: filePath, section: sectionName })
      }
      return newExpanded
    })
  }

  const renderTree = (tree: any, path: string = '', depth: number = 0): React.ReactNode[] => {
    return Object.entries(tree).map(([name, value]: [string, any]) => {
      const fullPath = path ? `${path}${name}` : name
      const isExpanded = expanded.has(fullPath)
      const isFolder = typeof value === 'object' && value !== null && !value.type
      const isActiveFile = activeFile === fullPath
      const isSelected = selectedItem?.path === fullPath && selectedItem?.type === 'file'

      if (!isFolder && value.type === 'file') {
        const isFileExpanded = expandedFiles.has(fullPath)
        return (
          <div 
            key={fullPath}
            ref={(el) => { fileRefs.current[fullPath] = el }}
            className={`relative ${isActiveFile ? 'bg-blue-900/20 border-l-2 border-blue-400' : ''} ${isSelected ? 'ring-1 ring-blue-400' : ''}`}
          >
            <div
              className={`flex items-center gap-1 px-2 py-1 text-xs hover:bg-gray-700 cursor-pointer transition-colors ${
                isActiveFile ? 'bg-blue-900/30' : ''
              }`}
              style={{ paddingLeft: `${depth * 12 + 8}px` }}
              onClick={() => toggleFile(fullPath)}
            >
              {isFileExpanded ? (
                <ChevronDown className="w-3 h-3 text-gray-400" />
              ) : (
                <ChevronRight className="w-3 h-3 text-gray-400" />
              )}
              <File className={`w-4 h-4 ${isActiveFile ? 'text-blue-400' : 'text-blue-400'}`} />
              <span className={`text-gray-300 ${isActiveFile ? 'font-semibold' : ''}`}>{name}</span>
              {isActiveFile && (
                <span className="ml-auto text-xs text-blue-400">● Active</span>
              )}
              {isSelected && value.connections && value.connections.length > 0 && (
                <span className="ml-2 text-xs text-purple-400">
                  {value.connections.length} connection{value.connections.length !== 1 ? 's' : ''}
                </span>
              )}
            </div>
            {isFileExpanded && (
              <div style={{ paddingLeft: `${(depth + 1) * 12 + 8}px` }}>
                <div className="px-2 py-1 text-xs text-gray-500">
                  <span className="text-green-400">Exports:</span> {value.exports?.join(', ') || 'none'}
                </div>
                <div className="px-2 py-1 text-xs text-gray-500">
                  <span className="text-blue-400">Imports:</span> {value.imports?.join(', ') || 'none'}
                </div>
                <div className="px-2 py-1 text-xs text-gray-500 mb-1">Sections:</div>
                {value.sections?.map((section: any) => {
                  const sectionKey = `${fullPath}:${section.name}`
                  const isSectionExpanded = expandedSections.has(sectionKey)
                  const isActiveSection = activeSection === section.name && isActiveFile
                  const isSectionSelected = selectedItem?.path === fullPath && selectedItem?.section === section.name
                  return (
                    <div 
                      key={section.name}
                      ref={(el) => { sectionRefs.current[sectionKey] = el }}
                      className={`mb-1 ${isSectionSelected ? 'ring-1 ring-purple-400' : ''}`}
                    >
                      <div
                        className={`flex items-center gap-1 px-2 py-1 text-xs hover:bg-gray-700 cursor-pointer rounded transition-colors ${
                          isActiveSection ? 'bg-blue-900/30 border-l-2 border-blue-400' : ''
                        }`}
                        onClick={() => toggleSection(fullPath, section.name)}
                      >
                        {isSectionExpanded ? (
                          <ChevronDown className="w-3 h-3 text-gray-400" />
                        ) : (
                          <ChevronRight className="w-3 h-3 text-gray-400" />
                        )}
                        <span className={`text-gray-300 ${isActiveSection ? 'font-semibold text-blue-300' : ''}`}>
                          {section.name}
                        </span>
                        <span className="text-gray-500 ml-auto">lines {section.lines[0]}-{section.lines[1]}</span>
                        {isActiveSection && (
                          <span className="ml-2 text-xs text-blue-400">●</span>
                        )}
                        {isSectionSelected && section.connections && section.connections.length > 0 && (
                          <span className="ml-2 text-xs text-purple-400">
                            {section.connections.length} connection{section.connections.length !== 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                      {isSectionExpanded && (
                        <div className="px-4 py-2 text-xs text-gray-400 bg-gray-800 rounded ml-4">
                          <div className="font-mono text-gray-500">// {section.name} code section</div>
                          <div className="text-gray-500 mt-1">Lines {section.lines[0]}-{section.lines[1]}</div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )
      }

      // Folder
      const isFolderSelected = selectedItem?.path === fullPath && selectedItem?.type === 'folder'
      return (
        <div key={fullPath}>
          <div
            className={`flex items-center gap-1 px-2 py-1 text-xs hover:bg-gray-700 cursor-pointer ${isFolderSelected ? 'ring-1 ring-yellow-400' : ''}`}
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => {
              toggleExpand(fullPath)
              setSelectedItem({ type: 'folder', path: fullPath })
            }}
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3 text-gray-400" />
            ) : (
              <ChevronRight className="w-3 h-3 text-gray-400" />
            )}
            <FolderOpen className="w-4 h-4 text-yellow-400" />
            <span className="text-gray-300">{name}</span>
          </div>
          {isExpanded && renderTree(value, fullPath, depth + 1)}
        </div>
      )
    })
  }

  const connections = getConnections()

  return (
    <div className="h-full flex flex-col relative">
      <div className="p-3 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs font-semibold text-blue-400 mb-1">Hierarchical Code Explorer V1</div>
            <div className="text-xs text-gray-500">Auto-Expanding • Connection Visualization • Highway Lines</div>
          </div>
          {activeFile && (
            <div className="text-xs text-blue-400">
              Active: {activeFile.split('/').pop()}
            </div>
          )}
        </div>
        {selectedItem && connections.length > 0 && (
          <div className="text-xs text-purple-400 mt-2">
            Showing {connections.length} connection{connections.length !== 1 ? 's' : ''} from {selectedItem.type === 'section' ? `${selectedItem.path.split('/').pop()}:${selectedItem.section}` : selectedItem.path.split('/').pop()}
          </div>
        )}
      </div>
      <div 
        ref={containerRef}
        className="flex-1 overflow-auto p-2 relative"
      >
        {/* SVG overlay for connection lines */}
        <svg
          ref={svgRef}
          className="absolute top-0 left-0 pointer-events-none"
          style={{ width: '100%', height: '100%', zIndex: 10 }}
        />
        {/* Highway vertical line */}
        {selectedItem && connections.length > 0 && (
          <div 
            className="absolute left-5 top-0 bottom-0 w-0.5 bg-purple-500/30 pointer-events-none"
            style={{ zIndex: 5 }}
          />
        )}
        <div className="relative" style={{ zIndex: 1 }}>
          {renderTree(codebase)}
        </div>
      </div>
    </div>
  )
}

// Keep V2 and V3 unchanged
export const HierarchicalCodeExplorerV2: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-green-400 mb-1">Hierarchical Code Explorer V2</div>
        <div className="text-xs text-gray-500">Graph-Based • Connection Visualization • Relationship Mapping</div>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-3">
        <div className="text-xs text-gray-400">Graph visualization coming soon...</div>
      </div>
    </div>
  )
}

export const HierarchicalCodeExplorerV3: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      <div className="p-3 border-b border-gray-700">
        <div className="text-xs font-semibold text-purple-400 mb-1">Hierarchical Code Explorer V3</div>
        <div className="text-xs text-gray-500">Semantic Sections • HHNI-Powered • Intent-Based Navigation</div>
      </div>
      <div className="flex-1 overflow-auto p-3">
        <div className="text-xs text-gray-400">Semantic explorer coming soon...</div>
      </div>
    </div>
  )
}
