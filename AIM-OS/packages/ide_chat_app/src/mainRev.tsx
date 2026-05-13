import React from 'react'
import ReactDOM from 'react-dom/client'
import AppRev from './AppRev.tsx'
import './index.css'

/**
 * Rev's IDE Prototype Entry Point
 * 
 * Launches Rev's IDE layout prototype on port 5180 (auto-increments if taken).
 * Protocol compliant: [REV] prefix, dynamic port display.
 */

// Update title with port dynamically
const updateTitle = () => {
  const port = window.location.port || '5180'
  document.title = `[REV] IDE Prototype - Port ${port}`
}

// Update title on mount and port change
if (typeof window !== 'undefined') {
  updateTitle()
  window.addEventListener('load', updateTitle)
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppRev />
  </React.StrictMode>,
)

