/**
 * LUCID Document Editor - Pagination Settings Panel
 * 
 * UI component for configuring pagination settings
 */

import React, { useState } from 'react';
import { Settings, X, Save } from 'lucide-react';
import { PaginationSettings, DEFAULT_PAGINATION, PAGE_SIZES, PaginationCalculator } from './index';

export interface PaginationSettingsPanelProps {
  settings: PaginationSettings;
  onSettingsChange: (settings: PaginationSettings) => void;
  onClose?: () => void;
}

export const PaginationSettingsPanel: React.FC<PaginationSettingsPanelProps> = ({
  settings,
  onSettingsChange,
  onClose,
}) => {
  const [localSettings, setLocalSettings] = useState<PaginationSettings>(settings);
  const [isOpen, setIsOpen] = useState(false);

  const handleSave = () => {
    onSettingsChange(localSettings);
    setIsOpen(false);
    if (onClose) onClose();
  };

  const handlePageSizeChange = (pageSize: PaginationSettings['pageSize']) => {
    const newSettings = {
      ...localSettings,
      pageSize,
      customWidth: pageSize === 'Custom' ? localSettings.customWidth : PAGE_SIZES[pageSize]?.width || 210,
      customHeight: pageSize === 'Custom' ? localSettings.customHeight : PAGE_SIZES[pageSize]?.height || 297,
    };
    setLocalSettings(newSettings);
  };

  const calculatedLines = PaginationCalculator.calculateLinesPerPage(localSettings);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="pagination-settings-toggle"
        title="Pagination Settings"
        style={{
          background: 'none',
          border: 'none',
          color: '#cccccc',
          cursor: 'pointer',
          padding: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          borderRadius: '3px',
        }}
      >
        <Settings size={16} />
        <span>Page Settings</span>
      </button>
    );
  }

  return (
    <div
      className="pagination-settings-panel"
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        backgroundColor: '#252526',
        border: '1px solid #3e3e42',
        borderRadius: '6px',
        padding: '20px',
        minWidth: '400px',
        maxWidth: '600px',
        zIndex: 1000,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, color: '#ffffff', fontSize: '18px' }}>Pagination Settings</h3>
        <button
          onClick={() => {
            setIsOpen(false);
            if (onClose) onClose();
          }}
          style={{
            background: 'none',
            border: 'none',
            color: '#cccccc',
            cursor: 'pointer',
            padding: '4px',
          }}
        >
          <X size={20} />
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Page Size */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
            Page Size
          </label>
          <select
            value={localSettings.pageSize}
            onChange={(e) => handlePageSizeChange(e.target.value as PaginationSettings['pageSize'])}
            style={{
              width: '100%',
              padding: '8px',
              backgroundColor: '#3c3c3c',
              border: '1px solid #5a5a5a',
              borderRadius: '3px',
              color: '#ffffff',
              fontSize: '14px',
            }}
          >
            <option value="A4">A4 (210 × 297 mm)</option>
            <option value="Letter">Letter (216 × 279 mm)</option>
            <option value="Legal">Legal (216 × 356 mm)</option>
            <option value="Custom">Custom</option>
          </select>
        </div>

        {/* Custom Dimensions */}
        {localSettings.pageSize === 'Custom' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
                Width (mm)
              </label>
              <input
                type="number"
                value={localSettings.customWidth}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, customWidth: parseFloat(e.target.value) || 210 })
                }
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#3c3c3c',
                  border: '1px solid #5a5a5a',
                  borderRadius: '3px',
                  color: '#ffffff',
                  fontSize: '14px',
                }}
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
                Height (mm)
              </label>
              <input
                type="number"
                value={localSettings.customHeight}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, customHeight: parseFloat(e.target.value) || 297 })
                }
                style={{
                  width: '100%',
                  padding: '8px',
                  backgroundColor: '#3c3c3c',
                  border: '1px solid #5a5a5a',
                  borderRadius: '3px',
                  color: '#ffffff',
                  fontSize: '14px',
                }}
              />
            </div>
          </div>
        )}

        {/* Lines Per Page */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
            Lines Per Page: {calculatedLines} (calculated) or{' '}
            <input
              type="number"
              value={localSettings.linesPerPage}
              onChange={(e) =>
                setLocalSettings({ ...localSettings, linesPerPage: parseInt(e.target.value) || 50 })
              }
              style={{
                width: '80px',
                padding: '4px',
                backgroundColor: '#3c3c3c',
                border: '1px solid #5a5a5a',
                borderRadius: '3px',
                color: '#ffffff',
                fontSize: '14px',
              }}
            />
          </label>
          <small style={{ color: '#858585', fontSize: '12px' }}>
            Calculated based on page size, margins, font size, and line height
          </small>
        </div>

        {/* Font Size */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
            Font Size (px): {localSettings.fontSize}
          </label>
          <input
            type="range"
            min="8"
            max="24"
            value={localSettings.fontSize}
            onChange={(e) =>
              setLocalSettings({ ...localSettings, fontSize: parseInt(e.target.value) })
            }
            style={{ width: '100%' }}
          />
        </div>

        {/* Line Height */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
            Line Height: {localSettings.lineHeight}x
          </label>
          <input
            type="range"
            min="1"
            max="3"
            step="0.1"
            value={localSettings.lineHeight}
            onChange={(e) =>
              setLocalSettings({ ...localSettings, lineHeight: parseFloat(e.target.value) })
            }
            style={{ width: '100%' }}
          />
        </div>

        {/* Margins */}
        <div>
          <label style={{ display: 'block', marginBottom: '8px', color: '#cccccc', fontSize: '14px' }}>
            Margins (mm)
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '12px', color: '#858585' }}>Top</label>
              <input
                type="number"
                value={localSettings.marginTop}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, marginTop: parseFloat(e.target.value) || 20 })
                }
                style={{
                  width: '100%',
                  padding: '6px',
                  backgroundColor: '#3c3c3c',
                  border: '1px solid #5a5a5a',
                  borderRadius: '3px',
                  color: '#ffffff',
                  fontSize: '14px',
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', color: '#858585' }}>Bottom</label>
              <input
                type="number"
                value={localSettings.marginBottom}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, marginBottom: parseFloat(e.target.value) || 20 })
                }
                style={{
                  width: '100%',
                  padding: '6px',
                  backgroundColor: '#3c3c3c',
                  border: '1px solid #5a5a5a',
                  borderRadius: '3px',
                  color: '#ffffff',
                  fontSize: '14px',
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', color: '#858585' }}>Left</label>
              <input
                type="number"
                value={localSettings.marginLeft}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, marginLeft: parseFloat(e.target.value) || 20 })
                }
                style={{
                  width: '100%',
                  padding: '6px',
                  backgroundColor: '#3c3c3c',
                  border: '1px solid #5a5a5a',
                  borderRadius: '3px',
                  color: '#ffffff',
                  fontSize: '14px',
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: '12px', color: '#858585' }}>Right</label>
              <input
                type="number"
                value={localSettings.marginRight}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, marginRight: parseFloat(e.target.value) || 20 })
                }
                style={{
                  width: '100%',
                  padding: '6px',
                  backgroundColor: '#3c3c3c',
                  border: '1px solid #5a5a5a',
                  borderRadius: '3px',
                  color: '#ffffff',
                  fontSize: '14px',
                }}
              />
            </div>
          </div>
        </div>

        {/* Show Page Breaks */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={localSettings.showPageBreaks}
            onChange={(e) =>
              setLocalSettings({ ...localSettings, showPageBreaks: e.target.checked })
            }
            style={{ cursor: 'pointer' }}
          />
          <label style={{ color: '#cccccc', fontSize: '14px', cursor: 'pointer' }}>
            Show Page Breaks
          </label>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '8px' }}>
          <button
            onClick={() => {
              setLocalSettings(DEFAULT_PAGINATION);
            }}
            style={{
              padding: '8px 16px',
              backgroundColor: '#3c3c3c',
              border: '1px solid #5a5a5a',
              borderRadius: '3px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            style={{
              padding: '8px 16px',
              backgroundColor: '#007acc',
              border: 'none',
              borderRadius: '3px',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Save size={16} />
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

