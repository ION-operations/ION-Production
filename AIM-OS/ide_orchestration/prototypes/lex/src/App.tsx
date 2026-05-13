// Main App Component
import React from 'react'
import { IDELayout } from '@/components/Layout/IDELayout'
import './App.css'

function App() {
  return (
    <div className="App" style={{ width: '100vw', height: '100vh', overflow: 'hidden', backgroundColor: '#111827' }}>
      <IDELayout />
    </div>
  )
}

export default App

