/**
 * AnimForge Toolbar Component
 * 
 * Left and Right icon bars with tool buttons
 * Opens drawers for detailed controls
 * 
 * @author ECHO (Director-Audio-Specialist)
 * @created 2025-12-01
 */

import React from 'react'
import {
  Pencil, Brush, PenTool, Square, Type, MousePointer2, Move, Eraser,
  Bone, Target, Paintbrush, Bot, Video, Sparkles,
  Users, Library, Film, Settings, Layers, Palette, Sliders,
  MessageSquare, Database, BookOpen, Search, HelpCircle,
  User, BarChart3, Network
} from 'lucide-react'
import { AnimForgeMode } from './store/animForgeStore'

interface AnimForgeToolbarProps {
  side: 'left' | 'right'
  activeDrawer: string | null
  onDrawerChange: (drawer: string | null) => void
  mode: AnimForgeMode
}

interface ToolButton {
  id: string
  icon: React.ElementType
  label: string
  drawer: string
  category: 'drawing' | 'rigging' | 'ai' | 'library' | 'properties' | 'consistent'
  modes?: AnimForgeMode[] // Only show in these modes (undefined = all)
}

// Left toolbar buttons
const LEFT_TOOLS: ToolButton[] = [
  // Drawing tools
  { id: 'pencil', icon: Pencil, label: 'Pencil', drawer: 'pencil', category: 'drawing', modes: ['draw'] },
  { id: 'brush', icon: Brush, label: 'Brush', drawer: 'brush', category: 'drawing', modes: ['draw'] },
  { id: 'pen', icon: PenTool, label: 'Pen (Bezier)', drawer: 'pen', category: 'drawing', modes: ['draw'] },
  { id: 'shapes', icon: Square, label: 'Shapes', drawer: 'shapes', category: 'drawing', modes: ['draw'] },
  { id: 'text', icon: Type, label: 'Text', drawer: 'text', category: 'drawing', modes: ['draw'] },
  { id: 'selection', icon: MousePointer2, label: 'Selection', drawer: 'selection', category: 'drawing' },
  { id: 'transform', icon: Move, label: 'Transform', drawer: 'transform', category: 'drawing' },
  { id: 'eraser', icon: Eraser, label: 'Eraser', drawer: 'eraser', category: 'drawing', modes: ['draw'] },
  
  // Rigging tools
  { id: 'rigging', icon: Bone, label: 'Rigging', drawer: 'rigging', category: 'rigging', modes: ['rig'] },
  { id: 'ik', icon: Target, label: 'IK/FK', drawer: 'ik', category: 'rigging', modes: ['rig'] },
  { id: 'weights', icon: Paintbrush, label: 'Weight Painting', drawer: 'weights', category: 'rigging', modes: ['rig'] },
  
  // AI tools
  { id: 'autorig', icon: Bot, label: 'AI Auto-Rig', drawer: 'autorig', category: 'ai' },
  { id: 'mocap', icon: Video, label: 'Motion Capture', drawer: 'mocap', category: 'ai', modes: ['mocap'] },
  { id: 'inbetween', icon: Sparkles, label: 'AI Inbetweening', drawer: 'inbetween', category: 'ai', modes: ['animate'] },
  
  // Library
  { id: 'characters', icon: Users, label: 'Characters', drawer: 'characters', category: 'library' },
  { id: 'symbols', icon: Library, label: 'Symbols', drawer: 'symbols', category: 'library' },
  { id: 'animations', icon: Film, label: 'Animations', drawer: 'animations', category: 'library' },
  
  { id: 'settings', icon: Settings, label: 'Settings', drawer: 'settings', category: 'library' },
]

// Left consistent buttons (bottom)
const LEFT_CONSISTENT: ToolButton[] = [
  { id: 'aiChat', icon: MessageSquare, label: 'AI Chat', drawer: 'aiChat', category: 'consistent' },
  { id: 'assets', icon: Database, label: 'Assets', drawer: 'assets', category: 'consistent' },
  { id: 'templates', icon: BookOpen, label: 'Templates', drawer: 'templates', category: 'consistent' },
  { id: 'search', icon: Search, label: 'Search', drawer: 'search', category: 'consistent' },
  { id: 'help', icon: HelpCircle, label: 'Help', drawer: 'help', category: 'consistent' },
]

// Right toolbar buttons
const RIGHT_TOOLS: ToolButton[] = [
  { id: 'properties', icon: Sliders, label: 'Properties', drawer: 'properties', category: 'properties' },
  { id: 'color', icon: Palette, label: 'Color', drawer: 'color', category: 'properties' },
  { id: 'layers', icon: Layers, label: 'Layers', drawer: 'layers', category: 'properties' },
  { id: 'animation', icon: Film, label: 'Animation', drawer: 'animation', category: 'properties', modes: ['animate'] },
  { id: 'timeline', icon: BarChart3, label: 'Timeline Overview', drawer: 'timelineOverview', category: 'properties' },
  { id: 'settingsRight', icon: Settings, label: 'Settings', drawer: 'settingsRight', category: 'properties' },
]

// Right consistent buttons (bottom)
const RIGHT_CONSISTENT: ToolButton[] = [
  { id: 'aiChatRight', icon: MessageSquare, label: 'AI Chat', drawer: 'aiChatRight', category: 'consistent' },
  { id: 'collaboration', icon: Network, label: 'Collaboration', drawer: 'collaboration', category: 'consistent' },
  { id: 'memory', icon: Database, label: 'Memory Bank', drawer: 'memory', category: 'consistent' },
  { id: 'profile', icon: User, label: 'Profile', drawer: 'profile', category: 'consistent' },
  { id: 'analytics', icon: BarChart3, label: 'Analytics', drawer: 'analytics', category: 'consistent' },
  { id: 'helpRight', icon: HelpCircle, label: 'Help', drawer: 'helpRight', category: 'consistent' },
]

export const AnimForgeToolbar: React.FC<AnimForgeToolbarProps> = ({
  side,
  activeDrawer,
  onDrawerChange,
  mode
}) => {
  const tools = side === 'left' ? LEFT_TOOLS : RIGHT_TOOLS
  const consistent = side === 'left' ? LEFT_CONSISTENT : RIGHT_CONSISTENT

  // Filter tools by current mode
  const filteredTools = tools.filter(tool => 
    !tool.modes || tool.modes.includes(mode)
  )

  // Group tools by category
  const groupedTools = filteredTools.reduce((acc, tool) => {
    if (!acc[tool.category]) acc[tool.category] = []
    acc[tool.category].push(tool)
    return acc
  }, {} as Record<string, ToolButton[]>)

  const handleClick = (drawer: string) => {
    if (activeDrawer === drawer) {
      onDrawerChange(null)
    } else {
      onDrawerChange(drawer)
    }
  }

  return (
    <div className="w-12 bg-gray-900 border-gray-800 flex flex-col shrink-0"
      style={{ borderLeftWidth: side === 'right' ? 1 : 0, borderRightWidth: side === 'left' ? 1 : 0 }}
    >
      {/* Top section - Page-specific tools */}
      <div className="flex-1 flex flex-col py-2 gap-1 overflow-y-auto">
        {Object.entries(groupedTools).map(([category, categoryTools]) => (
          <React.Fragment key={category}>
            {categoryTools.map(tool => (
              <ToolbarButton
                key={tool.id}
                tool={tool}
                isActive={activeDrawer === tool.drawer}
                onClick={() => handleClick(tool.drawer)}
              />
            ))}
            {category !== 'library' && <div className="h-px bg-gray-800 mx-2 my-1" />}
          </React.Fragment>
        ))}
      </div>

      {/* Divider */}
      <div className="h-px bg-gray-700 mx-2" />

      {/* Bottom section - Consistent tools */}
      <div className="py-2 flex flex-col gap-1">
        {consistent.map(tool => (
          <ToolbarButton
            key={tool.id}
            tool={tool}
            isActive={activeDrawer === tool.drawer}
            onClick={() => handleClick(tool.drawer)}
          />
        ))}
      </div>
    </div>
  )
}

// Toolbar button component
const ToolbarButton: React.FC<{
  tool: ToolButton
  isActive: boolean
  onClick: () => void
}> = ({ tool, isActive, onClick }) => {
  const Icon = tool.icon

  return (
    <button
      onClick={onClick}
      className={`w-10 h-10 mx-1 rounded flex items-center justify-center transition-colors ${
        isActive
          ? 'bg-purple-600 text-white'
          : 'text-gray-400 hover:text-white hover:bg-gray-800'
      }`}
      title={tool.label}
    >
      <Icon className="w-5 h-5" />
    </button>
  )
}

export default AnimForgeToolbar

