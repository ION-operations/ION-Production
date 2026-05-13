// Top Bar Component for Max V2
// Provides top bar with theme, mode, search, actions, and layout switcher

import React from 'react'
import { useLayout } from '../../hooks/useLayout'
import { useCustomization } from '../../hooks/useCustomization'
import './TopBar.css'

export const TopBar: React.FC = () => {
  const { layouts, currentLayout, load } = useLayout()
  const { templates, applyTemplate } = useCustomization()

  return (
    <div className="top-bar" role="banner">
      <div className="top-bar-left">
        <div className="top-bar-logo">
          <span className="logo-text">IDE Prototype</span>
        </div>
        <nav className="top-bar-nav" aria-label="Main navigation">
          <button className="nav-button" aria-label="File">
            File
          </button>
          <button className="nav-button" aria-label="Edit">
            Edit
          </button>
          <button className="nav-button" aria-label="View">
            View
          </button>
          <button className="nav-button" aria-label="Run">
            Run
          </button>
        </nav>
      </div>
      <div className="top-bar-center">
        <div className="search-container">
          <input
            type="search"
            className="search-input"
            placeholder="Search files, symbols, or commands..."
            aria-label="Search"
          />
        </div>
      </div>
      <div className="top-bar-right">
        <div className="layout-switcher">
          <select
            className="layout-select"
            value={currentLayout?.id || ''}
            onChange={(e) => load(e.target.value)}
            aria-label="Layout switcher"
          >
            <option value="">Select Layout</option>
            {layouts.map((layout) => (
              <option key={layout.id} value={layout.id}>
                {layout.name}
              </option>
            ))}
          </select>
        </div>
        <div className="template-switcher">
          <select
            className="template-select"
            onChange={(e) => {
              if (e.target.value) {
                applyTemplate(e.target.value)
              }
            }}
            aria-label="Template switcher"
          >
            <option value="">Templates</option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </div>
        <button className="top-bar-button" aria-label="Settings">
          ⚙️
        </button>
      </div>
    </div>
  )
}

