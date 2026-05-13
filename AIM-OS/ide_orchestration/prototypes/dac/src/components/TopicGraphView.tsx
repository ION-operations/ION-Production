/**
 * Topic Graph View Component
 * Interactive force-directed graph visualization of topic relationships
 * Integrates with SEG for real relationship data
 */

import React, { useRef, useEffect, useMemo, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { useTopicStore } from '../store/topicStore'
import { useSEG } from '../hooks/useAIMOS'
import { Topic } from '../store/topicStore'
import { TopicInfoPanel } from './TopicInfoPanel'

interface TopicGraphViewProps {
  width?: number
  height?: number
}

// Icon mapping based on topic level and category
const getTopicIcon = (topic: Topic | null): string => {
  if (!topic) return '●'
  
  // Map by category tag first
  const categoryTag = topic.tags.find(t => t.key === 'category')
  const category = categoryTag?.value.toLowerCase() || ''
  
  // Icon mappings by category
  const categoryIcons: Record<string, string> = {
    'ai': '🧠',
    'system': '⚙️',
    'graph': '🕸️',
    'document': '📄',
    'organization': '📊',
    'feature': '✨',
    'code': '💻',
    'database': '🗄️',
    'api': '🔌',
    'chat': '💬',
    'canvas': '🎨',
    'topic': '📌'
  }
  
  // Icon mappings by level
  const levelIcons: Record<string, string> = {
    'system': '🏛️',
    'section': '📁',
    'topic': '📌',
    'subtopic': '📍'
  }
  
  // Prefer category icon, fallback to level icon
  return categoryIcons[category] || levelIcons[topic.level] || '●'
}

// Get icon character for canvas rendering
const getIconChar = (topic: Topic | null): string => {
  return getTopicIcon(topic)
}

export const TopicGraphView: React.FC<TopicGraphViewProps> = ({ 
  width, 
  height 
}) => {
  const { topics, activeTopicId, setActiveTopic, getRelatedTopics } = useTopicStore()
  const { entities, relations, getEntityRelations } = useSEG()
  const graphRef = useRef<any>()
  const containerRef = useRef<HTMLDivElement>(null)
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null)
  const [hoveredNode, setHoveredNode] = useState<any>(null)
  
  // Get container dimensions if not provided
  const [dimensions, setDimensions] = useState({ width: width || 256, height: height || 600 })
  
  useEffect(() => {
    if (!width || !height) {
      const updateDimensions = () => {
        if (containerRef.current) {
          const rect = containerRef.current.getBoundingClientRect()
          setDimensions({ width: rect.width, height: rect.height })
        }
      }
      updateDimensions()
      window.addEventListener('resize', updateDimensions)
      return () => window.removeEventListener('resize', updateDimensions)
    }
  }, [width, height])
  
  // Build graph data from topics and SEG relations
  const graphData = useMemo(() => {
    const nodes: Array<{ id: string; name: string; group: number; size: number; topic: Topic | null; icon: string }> = []
    const links: Array<{ source: string; target: string; value: number; type: string }> = []
    
    // Add topic nodes
    topics.forEach(topic => {
      nodes.push({
        id: topic.id,
        name: topic.name,
        group: topic.level === 'system' ? 1 : topic.level === 'section' ? 2 : topic.level === 'topic' ? 3 : 4,
        size: Math.max(8, Math.min(24, topic.messageCount / 5 + 8)),
        topic,
        icon: getIconChar(topic)
      })
      
      // Add topic relationships as links
      topic.related_topics.forEach(rel => {
        const targetTopic = topics.find(t => t.id === rel.topic_id)
        if (targetTopic) {
          links.push({
            source: topic.id,
            target: rel.topic_id,
            value: rel.strength,
            type: rel.relation_type
          })
        }
      })
      
      // Add parent-child relationships
      if (topic.parent_topic_id) {
        links.push({
          source: topic.parent_topic_id,
          target: topic.id,
          value: 1.0,
          type: 'parent'
        })
      }
    })
    
    // Integrate SEG entities and relations
    entities.forEach(entity => {
      // Check if entity corresponds to a topic
      const matchingTopic = topics.find(t => 
        t.name.toLowerCase() === entity.name.toLowerCase() ||
        t.id === entity.id
      )
      
      if (!matchingTopic) {
        // Add SEG entity as node
        nodes.push({
          id: entity.id,
          name: entity.name,
          group: 5, // SEG entities
          size: 10,
          topic: null,
          icon: '🔗'
        })
      }
    })
    
    // Add SEG relations as links
    relations.forEach(relation => {
      // Check if both source and target exist in our nodes
      const sourceExists = nodes.some(n => n.id === relation.source_id)
      const targetExists = nodes.some(n => n.id === relation.target_id)
      
      if (sourceExists && targetExists) {
        links.push({
          source: relation.source_id,
          target: relation.target_id,
          value: relation.confidence || 0.8,
          type: relation.relation_type
        })
      }
    })
    
    return { nodes, links }
  }, [topics, entities, relations])
  
  // Color scheme for different node types
  const getNodeColor = (node: any) => {
    if (node.id === activeTopicId) return '#3b82f6' // Blue for active
    if (node.id === selectedTopic?.id) return '#8b5cf6' // Purple for selected
    if (node.group === 1) return '#10b981' // Green for system
    if (node.group === 2) return '#3b82f6' // Blue for section
    if (node.group === 3) return '#8b5cf6' // Purple for topic
    if (node.group === 4) return '#f59e0b' // Orange for subtopic
    if (node.group === 5) return '#ef4444' // Red for SEG entities
    return '#6b7280' // Gray default
  }
  
  // Link color based on relation type
  const getLinkColor = (link: any) => {
    switch (link.type) {
      case 'parent': return '#10b981' // Green for hierarchy
      case 'related': return '#3b82f6' // Blue for related
      case 'derived': return '#8b5cf6' // Purple for derived
      case 'contradicts': return '#ef4444' // Red for contradictions
      case 'SUPPORTS': return '#10b981'
      case 'CONTRADICTS': return '#ef4444'
      case 'DERIVES_FROM': return '#8b5cf6'
      default: return '#6b7280'
    }
  }
  
  const finalWidth = width || dimensions.width
  const finalHeight = height || dimensions.height
  
  return (
    <div ref={containerRef} className="w-full h-full bg-gray-900 rounded-lg overflow-hidden relative">
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        width={finalWidth}
        height={finalHeight}
        nodeLabel={(node: any) => {
          // Show only title on hover
          return `<div style="background: rgba(0,0,0,0.9); color: white; padding: 6px 10px; border-radius: 4px; font-size: 12px; font-weight: 500;">${node.name}</div>`
        }}
        nodeColor={getNodeColor}
        nodeVal={(node: any) => node.size}
        linkColor={getLinkColor}
        linkWidth={(link: any) => link.value * 2}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        onNodeClick={(node: any) => {
          if (node.topic) {
            setSelectedTopic(node.topic)
            setActiveTopic(node.id)
          }
        }}
        onNodeHover={(node: any) => {
          setHoveredNode(node)
          if (node && graphRef.current) {
            graphRef.current.getGraph().setNodeHighlight(node.id, true)
          }
        }}
        onBackgroundClick={() => {
          setSelectedTopic(null)
        }}
        cooldownTicks={100}
        onEngineStop={() => {
          if (graphRef.current) {
            graphRef.current.zoomToFit(400, 20)
          }
        }}
        nodeCanvasObjectMode={() => 'after'}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          // Draw icon instead of text
          const icon = node.icon || '●'
          const iconSize = node.size * 1.2
          
          // Draw circle background
          ctx.beginPath()
          ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI)
          ctx.fillStyle = getNodeColor(node)
          ctx.fill()
          
          // Draw border for selected/active nodes
          if (node.id === selectedTopic?.id || node.id === activeTopicId) {
            ctx.strokeStyle = '#ffffff'
            ctx.lineWidth = 2 / globalScale
            ctx.stroke()
          }
          
          // Draw icon emoji
          ctx.font = `${iconSize}px Arial`
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillStyle = '#ffffff'
          ctx.fillText(icon, node.x, node.y)
        }}
      />
      
      {/* Info Panel */}
      {selectedTopic && (
        <TopicInfoPanel
          topic={selectedTopic}
          onClose={() => setSelectedTopic(null)}
          onTopicClick={(topicId) => {
            const topic = topics.find(t => t.id === topicId)
            if (topic) {
              setSelectedTopic(topic)
              setActiveTopic(topicId)
            }
          }}
        />
      )}
      
      {/* Legend - positioned inside the graph container */}
      <div className="absolute bottom-2 left-2 bg-gray-800/95 border border-gray-700 rounded-lg p-2 text-xs text-gray-300 z-10">
        <div className="font-semibold mb-1.5 text-xs">Legend</div>
        <div className="space-y-1">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>
            <span className="text-xs">System</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-blue-500"></div>
            <span className="text-xs">Section</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-purple-500"></div>
            <span className="text-xs">Topic</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-orange-500"></div>
            <span className="text-xs">Subtopic</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500"></div>
            <span className="text-xs">SEG Entity</span>
          </div>
        </div>
      </div>
    </div>
  )
}

