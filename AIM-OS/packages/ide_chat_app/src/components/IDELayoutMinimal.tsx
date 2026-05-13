import React from 'react'

interface IDELayoutMinimalProps {
  theme?: string
}

export const IDELayoutMinimal: React.FC<IDELayoutMinimalProps> = ({ theme = 'dark' }) => {
  return (
    <div className="flex-1 flex bg-gray-900">
      {/* Left Drawer */}
      <div className="w-64 bg-gray-800 border-r border-gray-700">
        <div className="p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Explorer</h3>
          <div className="space-y-2">
            <div className="text-gray-300">📁 src</div>
            <div className="text-gray-300 ml-4">📄 App.tsx</div>
            <div className="text-gray-300 ml-4">📄 index.tsx</div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-center px-4">
          <span className="text-sm text-gray-300">IDE - Minimal Working Version</span>
        </div>

        {/* Main Editor Area */}
        <div className="flex-1 bg-gray-900 p-4">
          <div className="h-full bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-bold text-white mb-4">Welcome to the IDE!</h2>
            <p className="text-gray-300 mb-4">
              This is a minimal working version of the IDE. We're building up the features incrementally.
            </p>
            <div className="bg-gray-700 p-4 rounded">
              <h3 className="text-lg font-semibold text-white mb-2">Current Status:</h3>
              <ul className="text-gray-300 space-y-1">
                <li>✅ Basic layout structure</li>
                <li>✅ Left drawer with file explorer</li>
                <li>✅ Main content area</li>
                <li>🔄 TypeScript errors being fixed</li>
                <li>⏳ Advanced features coming soon</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Right Drawer */}
      <div className="w-64 bg-gray-800 border-l border-gray-700">
        <div className="p-4">
          <h3 className="text-lg font-semibold text-white mb-4">Tools</h3>
          <div className="space-y-2">
            <div className="text-gray-300">🔧 Terminal</div>
            <div className="text-gray-300">📊 Timeline</div>
            <div className="text-gray-300">🐛 Problems</div>
          </div>
        </div>
      </div>
    </div>
  )
}
