// Panel Icon Bar Component - Standard IDE Pattern
// Vertical icon bar for left/right sidebars
import React from 'react'
import { 
  File, 
  Brain, 
  Search, 
  FileText, 
  Users, 
  Activity,
  MessageSquare,
  Settings,
  Package,
  GitBranch,
  Terminal,
  Clock,
  AlertTriangle,
  Bug
} from 'lucide-react'
import { Panel, PanelZone } from '@/types'
import { useLayoutStore } from '@/store/layoutStore'

interface PanelIconBarProps {
  zone: 'left' | 'right'
  panels: Panel[]
}

const panelIcons: Record<string, React.ComponentType<{ size?: number }>> = {
  'file-explorer': File,
  'memory-browser': Brain,
  'search-panel': Search,
  'outline-panel': FileText,
  'agent-management': Users,
  'system-monitor': Activity,
  'coding-chat': MessageSquare,
  'planning-chat': MessageSquare,
  'properties-panel': Settings,
  'component-library': Package,
  'git-panel': GitBranch,
}

export const PanelIconBar: React.FC<PanelIconBarProps> = ({ zone, panels }) => {
  const { activePanels, setActivePanel } = useLayoutStore()
  const activePanelId = activePanels[zone]
  const visiblePanels = panels.sort((a, b) => a.order - b.order)

  // Initialize active panel if none selected
  React.useEffect(() => {
    if (!activePanelId && visiblePanels.length > 0) {
      setActivePanel(zone, visiblePanels[0].id)
    }
  }, [activePanelId, visiblePanels.length, zone, setActivePanel])

  if (visiblePanels.length === 0) return null

  return (
    <div
      style={{
        width: '48px',
        height: '100%',
        backgroundColor: '#111827',
        borderRight: zone === 'left' ? '1px solid #374151' : 'none',
        borderLeft: zone === 'right' ? '1px solid #374151' : 'none',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: '8px',
        gap: '4px',
      }}
    >
      {visiblePanels.map((panel) => {
        const Icon = panelIcons[panel.type] || File
        const isActive = activePanelId === panel.id

        return (
          <button
            key={panel.id}
            onClick={() => setActivePanel(zone, panel.id)}
            title={panel.title}
            style={{
              width: '40px',
              height: '40px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: isActive ? '#374151' : 'transparent',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              color: isActive ? '#F9FAFB' : '#9CA3AF',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.backgroundColor = '#1F2937'
                e.currentTarget.style.color = '#F9FAFB'
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.color = '#9CA3AF'
              }
            }}
          >
            <Icon size={20} />
          </button>
        )
      })}
    </div>
  )
}

