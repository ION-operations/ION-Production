// Main App Entry Point - V2 Performance Optimized
import React from 'react'
import ReactDOM from 'react-dom/client'
import { IDELayout } from './components/IDELayout'
import { ErrorBoundary } from './components/ErrorBoundary'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary panelName="IDE Application">
      <IDELayout />
    </ErrorBoundary>
  </React.StrictMode>
)

