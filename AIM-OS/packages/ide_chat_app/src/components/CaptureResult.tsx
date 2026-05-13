/**
 * Capture Result Component
 * Displays thumbnail and coordinates after template capture
 */

import React, { useState, useEffect } from 'react';
import { X, Save, Camera } from 'lucide-react';

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface CaptureResultProps {
  thumbnail: string; // Base64 image
  rectangle: Rectangle;
  onSave: (metadata: { name: string; theme: 'light' | 'dark' | 'hover' }) => void;
  onCancel: () => void;
}

export const CaptureResult: React.FC<CaptureResultProps> = ({
  thumbnail,
  rectangle,
  onSave,
  onCancel
}) => {
  const [templateName, setTemplateName] = useState('');
  const [theme, setTheme] = useState<'light' | 'dark' | 'hover'>('light');

  const handleSave = () => {
    if (!templateName.trim()) {
      alert('Please enter a template name');
      return;
    }
    onSave({ name: templateName.trim(), theme });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-2xl w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Camera className="w-5 h-5" />
            Template Captured
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Thumbnail Preview */}
        <div className="mb-4">
          <div className="bg-gray-800 rounded p-4 flex items-center justify-center">
            <img
              src={`data:image/png;base64,${thumbnail}`}
              alt="Template preview"
              className="max-w-full max-h-64 rounded border border-gray-700"
            />
          </div>
        </div>

        {/* Coordinates */}
        <div className="mb-4 p-3 bg-gray-800 rounded font-mono text-sm text-gray-300">
          <div className="grid grid-cols-2 gap-2">
            <div>X: {rectangle.x}</div>
            <div>Y: {rectangle.y}</div>
            <div>Width: {rectangle.width}</div>
            <div>Height: {rectangle.height}</div>
          </div>
        </div>

        {/* Metadata Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Template Name
            </label>
            <input
              type="text"
              placeholder="e.g., Stop Button"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Theme
            </label>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'hover')}
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white focus:outline-none focus:border-blue-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="hover">Hover</option>
            </select>
          </div>

          <div className="flex gap-3 justify-end">
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save Template
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

