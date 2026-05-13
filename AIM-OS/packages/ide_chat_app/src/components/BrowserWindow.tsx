import React from 'react'
import { useApp } from '../contexts/AppContext'
import { X, Minimize2, Maximize2, RefreshCw, ExternalLink } from 'lucide-react'

export function BrowserWindow() {
  const { state, dispatch } = useApp()

  if (!state.browserWindow.isVisible) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-8">
      <div className="w-full max-w-4xl h-5/6 bg-white rounded-2xl shadow-2xl flex flex-col animate-fade-in">
        {/* Browser Header */}
        <div className="h-12 bg-gray-100 rounded-t-2xl flex items-center justify-between px-4 border-b">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
          
          <div className="flex-1 mx-4">
            <div className="bg-white border border-gray-300 rounded-lg px-3 py-1 flex items-center space-x-2">
              <span className="text-sm text-gray-600">{state.browserWindow.url || 'https://example.com'}</span>
              <RefreshCw className="w-4 h-4 text-gray-400" />
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-1 hover:bg-gray-200 rounded">
              <Minimize2 className="w-4 h-4 text-gray-600" />
            </button>
            <button className="p-1 hover:bg-gray-200 rounded">
              <Maximize2 className="w-4 h-4 text-gray-600" />
            </button>
            <button
              onClick={() => dispatch({ type: 'TOGGLE_BROWSER_WINDOW' })}
              className="p-1 hover:bg-gray-200 rounded"
            >
              <X className="w-4 h-4 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Browser Content */}
        <div className="flex-1 bg-white rounded-b-2xl overflow-hidden">
          {state.browserWindow.url ? (
            <iframe
              src={state.browserWindow.url}
              className="w-full h-full border-0"
              title={state.browserWindow.title}
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <ExternalLink className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">Browser Window</h3>
                <p className="text-gray-500">No URL specified</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
