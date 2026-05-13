import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { AetherIDELayout } from './components/AetherIDELayout'
import './index.css'

// Component to set document title with agent name and port
function TitleUpdater() {
  useEffect(() => {
    const port = window.location.port || '5175'
    document.title = `[AETHER V2] IDE Prototype - Port ${port}`
  }, [])
  return null
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TitleUpdater />
    <AetherIDELayout />
  </React.StrictMode>
)
