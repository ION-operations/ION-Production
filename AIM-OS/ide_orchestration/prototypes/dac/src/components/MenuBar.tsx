// VSCode-style Menu Bar Component
// File, Edit, View, Go, Run, Terminal, Help menus with keyboard shortcuts

import React, { useState, useRef, useEffect } from 'react'
import {
  FileText, Edit, Eye, Navigation, Play, Terminal, HelpCircle,
  Save, FolderOpen, NewFile, OpenFile, Close, Undo, Redo, Cut, Copy, Paste,
  Find, Replace, Settings, ZoomIn, ZoomOut, Command, Search, GitBranch
} from 'lucide-react'

interface MenuItem {
  label: string
  shortcut?: string
  action: () => void
  divider?: boolean
  disabled?: boolean
}

interface Menu {
  label: string
  items: MenuItem[]
}

export const MenuBar: React.FC = () => {
  const [activeMenu, setActiveMenu] = useState<string | null>(null)
  const menuRefs = useRef<{ [key: string]: HTMLDivElement | null }>({})

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (activeMenu && menuRefs.current[activeMenu]) {
        const menuElement = menuRefs.current[activeMenu]
        if (menuElement && !menuElement.contains(event.target as Node)) {
          setActiveMenu(null)
        }
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [activeMenu])

  const menus: Menu[] = [
    {
      label: 'File',
      items: [
        { label: 'New File', shortcut: 'Ctrl+N', action: () => console.log('New File') },
        { label: 'New Window', shortcut: 'Ctrl+Shift+N', action: () => console.log('New Window') },
        { divider: true },
        { label: 'Open File...', shortcut: 'Ctrl+O', action: () => console.log('Open File') },
        { label: 'Open Folder...', shortcut: 'Ctrl+K Ctrl+O', action: () => console.log('Open Folder') },
        { divider: true },
        { label: 'Save', shortcut: 'Ctrl+S', action: () => console.log('Save') },
        { label: 'Save As...', shortcut: 'Ctrl+Shift+S', action: () => console.log('Save As') },
        { label: 'Save All', shortcut: 'Ctrl+K S', action: () => console.log('Save All') },
        { divider: true },
        { label: 'Close Editor', shortcut: 'Ctrl+W', action: () => console.log('Close Editor') },
        { label: 'Close Folder', action: () => console.log('Close Folder') },
        { divider: true },
        { label: 'Exit', action: () => console.log('Exit') },
      ]
    },
    {
      label: 'Edit',
      items: [
        { label: 'Undo', shortcut: 'Ctrl+Z', action: () => console.log('Undo') },
        { label: 'Redo', shortcut: 'Ctrl+Y', action: () => console.log('Redo') },
        { divider: true },
        { label: 'Cut', shortcut: 'Ctrl+X', action: () => console.log('Cut') },
        { label: 'Copy', shortcut: 'Ctrl+C', action: () => console.log('Copy') },
        { label: 'Paste', shortcut: 'Ctrl+V', action: () => console.log('Paste') },
        { divider: true },
        { label: 'Find', shortcut: 'Ctrl+F', action: () => console.log('Find') },
        { label: 'Replace', shortcut: 'Ctrl+H', action: () => console.log('Replace') },
        { label: 'Find in Files', shortcut: 'Ctrl+Shift+F', action: () => console.log('Find in Files') },
        { divider: true },
        { label: 'Preferences', shortcut: 'Ctrl+,', action: () => console.log('Preferences') },
      ]
    },
    {
      label: 'View',
      items: [
        { label: 'Command Palette...', shortcut: 'Ctrl+Shift+P', action: () => console.log('Command Palette') },
        { label: 'Open View...', shortcut: 'Ctrl+Shift+U', action: () => console.log('Open View') },
        { divider: true },
        { label: 'Explorer', shortcut: 'Ctrl+Shift+E', action: () => console.log('Explorer') },
        { label: 'Search', shortcut: 'Ctrl+Shift+F', action: () => console.log('Search') },
        { label: 'Source Control', shortcut: 'Ctrl+Shift+G', action: () => console.log('Source Control') },
        { label: 'Run and Debug', shortcut: 'Ctrl+Shift+D', action: () => console.log('Run and Debug') },
        { label: 'Extensions', shortcut: 'Ctrl+Shift+X', action: () => console.log('Extensions') },
        { divider: true },
        { label: 'Zoom In', shortcut: 'Ctrl+=', action: () => console.log('Zoom In') },
        { label: 'Zoom Out', shortcut: 'Ctrl+-', action: () => console.log('Zoom Out') },
        { label: 'Reset Zoom', shortcut: 'Ctrl+0', action: () => console.log('Reset Zoom') },
        { divider: true },
        { label: 'Appearance', action: () => console.log('Appearance') },
        { label: 'Editor Layout', action: () => console.log('Editor Layout') },
      ]
    },
    {
      label: 'Go',
      items: [
        { label: 'Back', shortcut: 'Ctrl+Alt+-', action: () => console.log('Back') },
        { label: 'Forward', shortcut: 'Ctrl+Shift+-', action: () => console.log('Forward') },
        { divider: true },
        { label: 'Go to File...', shortcut: 'Ctrl+P', action: () => console.log('Go to File') },
        { label: 'Go to Symbol in Workspace...', shortcut: 'Ctrl+T', action: () => console.log('Go to Symbol') },
        { label: 'Go to Line/Column...', shortcut: 'Ctrl+G', action: () => console.log('Go to Line') },
        { divider: true },
        { label: 'Go to Definition', shortcut: 'F12', action: () => console.log('Go to Definition') },
        { label: 'Go to Declaration', shortcut: 'Ctrl+F12', action: () => console.log('Go to Declaration') },
        { label: 'Go to Type Definition', shortcut: 'Ctrl+Shift+F12', action: () => console.log('Go to Type Definition') },
        { label: 'Go to References', shortcut: 'Shift+F12', action: () => console.log('Go to References') },
      ]
    },
    {
      label: 'Run',
      items: [
        { label: 'Start Debugging', shortcut: 'F5', action: () => console.log('Start Debugging') },
        { label: 'Run Without Debugging', shortcut: 'Ctrl+F5', action: () => console.log('Run Without Debugging') },
        { label: 'Stop Debugging', shortcut: 'Shift+F5', action: () => console.log('Stop Debugging') },
        { divider: true },
        { label: 'Restart Debugging', shortcut: 'Ctrl+Shift+F5', action: () => console.log('Restart Debugging') },
        { divider: true },
        { label: 'Open Configurations...', action: () => console.log('Open Configurations') },
      ]
    },
    {
      label: 'Terminal',
      items: [
        { label: 'New Terminal', shortcut: 'Ctrl+Shift+`', action: () => console.log('New Terminal') },
        { label: 'Split Terminal', shortcut: 'Ctrl+Shift+5', action: () => console.log('Split Terminal') },
        { divider: true },
        { label: 'Kill Terminal', action: () => console.log('Kill Terminal') },
        { divider: true },
        { label: 'Terminal Settings...', action: () => console.log('Terminal Settings') },
      ]
    },
    {
      label: 'Help',
      items: [
        { label: 'Welcome', action: () => console.log('Welcome') },
        { label: 'Documentation', action: () => console.log('Documentation') },
        { divider: true },
        { label: 'Keyboard Shortcuts', shortcut: 'Ctrl+K Ctrl+S', action: () => console.log('Keyboard Shortcuts') },
        { label: 'Keyboard Shortcuts Reference', action: () => console.log('Keyboard Shortcuts Reference') },
        { divider: true },
        { label: 'About', action: () => console.log('About') },
      ]
    }
  ]

  const handleMenuClick = (menuLabel: string) => {
    setActiveMenu(activeMenu === menuLabel ? null : menuLabel)
  }

  const handleMenuItemClick = (item: MenuItem) => {
    if (!item.disabled) {
      item.action()
      setActiveMenu(null)
    }
  }

  return (
    <div className="flex items-center h-full">
      {menus.map((menu) => (
        <div key={menu.label} className="relative" ref={(el) => (menuRefs.current[menu.label] = el)}>
          <button
            onClick={() => handleMenuClick(menu.label)}
            className={`px-3 py-1 text-xs text-gray-300 hover:bg-gray-800 hover:text-gray-100 transition-colors ${
              activeMenu === menu.label ? 'bg-gray-800 text-gray-100' : ''
            }`}
          >
            {menu.label}
          </button>
          {activeMenu === menu.label && (
            <div className="absolute top-full left-0 mt-0 bg-gray-900 border border-gray-700 shadow-lg z-50 min-w-[200px] py-1">
              {menu.items.map((item, index) => (
                item.divider ? (
                  <div key={`divider-${index}`} className="h-px bg-gray-700 my-1" />
                ) : (
                  <button
                    key={index}
                    onClick={() => handleMenuItemClick(item)}
                    disabled={item.disabled}
                    className={`w-full text-left px-4 py-1.5 text-xs text-gray-300 hover:bg-gray-800 hover:text-gray-100 flex items-center justify-between transition-colors ${
                      item.disabled ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    <span>{item.label}</span>
                    {item.shortcut && (
                      <span className="text-gray-500 ml-8 text-[10px]">{item.shortcut}</span>
                    )}
                  </button>
                )
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

