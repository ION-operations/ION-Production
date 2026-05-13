// Layout Management UI Component
import React, { useState } from 'react'
import { Save, FolderOpen, Trash2, X } from 'lucide-react'
import { useLayoutStore } from '@/store/layoutStore'

export const LayoutManager: React.FC = () => {
  const { saveLayout, loadLayout, deleteLayout, getLayoutNames, activeLayout } = useLayoutStore()
  const [isOpen, setIsOpen] = useState(false)
  const [saveName, setSaveName] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)

  const layouts = getLayoutNames()

  const handleSave = () => {
    if (saveName.trim()) {
      const layoutId = `layout-${Date.now()}`
      saveLayout(layoutId, saveName.trim())
      setSaveName('')
      setShowSaveDialog(false)
    }
  }

  const handleLoad = (layoutId: string) => {
    loadLayout(layoutId)
    setIsOpen(false)
  }

  const handleDelete = (layoutId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Delete this layout?')) {
      deleteLayout(layoutId)
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          top: '50px',
          right: '20px',
          padding: '8px 12px',
          backgroundColor: '#3B82F6',
          color: '#F9FAFB',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '13px',
          zIndex: 1000,
        }}
        title="Manage Layouts"
      >
        <FolderOpen size={16} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
        Layouts
      </button>
    )
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: '50px',
        right: '20px',
        width: '300px',
        backgroundColor: '#1F2937',
        border: '1px solid #374151',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        zIndex: 1001,
        padding: '16px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ color: '#F9FAFB', fontSize: '16px', fontWeight: 'bold', margin: 0 }}>Layout Manager</h3>
        <button
          onClick={() => setIsOpen(false)}
          style={{
            background: 'none',
            border: 'none',
            color: '#9CA3AF',
            cursor: 'pointer',
            padding: '4px',
          }}
          aria-label="Close"
        >
          <X size={18} />
        </button>
      </div>

      {showSaveDialog ? (
        <div style={{ marginBottom: '16px' }}>
          <input
            type="text"
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            placeholder="Layout name"
            onKeyPress={(e) => {
              if (e.key === 'Enter') handleSave()
              if (e.key === 'Escape') setShowSaveDialog(false)
            }}
            autoFocus
            style={{
              width: '100%',
              padding: '8px',
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderRadius: '4px',
              color: '#F9FAFB',
              fontSize: '13px',
              marginBottom: '8px',
            }}
          />
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={handleSave}
              style={{
                flex: 1,
                padding: '6px 12px',
                backgroundColor: '#10B981',
                color: '#F9FAFB',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              Save
            </button>
            <button
              onClick={() => {
                setShowSaveDialog(false)
                setSaveName('')
              }}
              style={{
                flex: 1,
                padding: '6px 12px',
                backgroundColor: '#6B7280',
                color: '#F9FAFB',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setShowSaveDialog(true)}
          style={{
            width: '100%',
            padding: '8px 12px',
            backgroundColor: '#3B82F6',
            color: '#F9FAFB',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '13px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
          }}
        >
          <Save size={16} />
          Save Current Layout
        </button>
      )}

      <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
        {layouts.length === 0 ? (
          <div style={{ color: '#9CA3AF', fontSize: '13px', textAlign: 'center', padding: '20px' }}>
            No saved layouts
          </div>
        ) : (
          layouts.map((layout) => (
            <div
              key={layout.id}
              onClick={() => handleLoad(layout.id)}
              style={{
                padding: '10px',
                marginBottom: '8px',
                backgroundColor: activeLayout === layout.id ? '#374151' : '#111827',
                border: '1px solid #374151',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <span style={{ color: '#F9FAFB', fontSize: '13px' }}>{layout.name}</span>
              <button
                onClick={(e) => handleDelete(layout.id, e)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#EF4444',
                  cursor: 'pointer',
                  padding: '4px',
                }}
                title="Delete layout"
                aria-label="Delete layout"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

