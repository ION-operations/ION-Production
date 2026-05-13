// Properties Panel - Max V2
// Property editor with AIM-OS integration

import React, { useState, useMemo } from 'react';
import { Settings, Edit, Save, X, Check } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './PropertiesPanel.css';

export interface Property {
  key: string;
  value: any;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  editable: boolean;
  description?: string;
  confidence?: number;
}

export const PropertiesPanel: React.FC = () => {
  const { vif, loading, errors } = useAIMOS();
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');

  // Mock properties
  const properties: Property[] = useMemo(() => [
    {
      key: 'name',
      value: 'Max V2 IDE',
      type: 'string',
      editable: true,
      description: 'IDE name',
      confidence: 0.95,
    },
    {
      key: 'version',
      value: '2.0.0',
      type: 'string',
      editable: false,
      description: 'IDE version',
      confidence: 1.0,
    },
    {
      key: 'theme',
      value: 'dark',
      type: 'string',
      editable: true,
      description: 'Color theme',
      confidence: 0.90,
    },
    {
      key: 'autoSave',
      value: true,
      type: 'boolean',
      editable: true,
      description: 'Auto-save enabled',
      confidence: 0.88,
    },
    {
      key: 'maxPanels',
      value: 10,
      type: 'number',
      editable: true,
      description: 'Maximum panels',
      confidence: 0.85,
    },
  ], []);

  const handleEdit = (property: Property) => {
    setEditingKey(property.key);
    setEditValue(String(property.value));
  };

  const handleSave = (key: string) => {
    // TODO: Save property value
    console.log(`Saving ${key}: ${editValue}`);
    setEditingKey(null);
    setEditValue('');
  };

  const handleCancel = () => {
    setEditingKey(null);
    setEditValue('');
  };

  const renderPropertyValue = (property: Property) => {
    if (editingKey === property.key) {
      return (
        <div className="properties-edit-controls">
          {property.type === 'boolean' ? (
            <input
              type="checkbox"
              checked={editValue === 'true'}
              onChange={(e) => setEditValue(String(e.target.checked))}
              className="properties-checkbox"
            />
          ) : (
            <input
              type={property.type === 'number' ? 'number' : 'text'}
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="properties-input"
            />
          )}
          <button
            className="properties-save-button"
            onClick={() => handleSave(property.key)}
            aria-label="Save"
          >
            <Check className="properties-icon" />
          </button>
          <button
            className="properties-cancel-button"
            onClick={handleCancel}
            aria-label="Cancel"
          >
            <X className="properties-icon" />
          </button>
        </div>
      );
    }

    return (
      <div className="properties-value-display">
        <span className="properties-value">
          {property.type === 'boolean' ? (property.value ? 'true' : 'false') : String(property.value)}
        </span>
        {property.editable && (
          <button
            className="properties-edit-button"
            onClick={() => handleEdit(property)}
            aria-label={`Edit ${property.key}`}
          >
            <Edit className="properties-icon" />
          </button>
        )}
      </div>
    );
  };

  if (loading.vif) {
    return <PanelLoading message="Loading Properties..." />;
  }

  if (errors.vif) {
    return (
      <div className="properties-error" role="alert">
        <p>Error loading Properties: {errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="properties-panel" role="region" aria-label="Properties Panel">
      {/* Header */}
      <div className="properties-header">
        <div className="properties-header-left">
          <Settings className="properties-header-icon" />
          <div>
            <h3 className="properties-header-title">Properties</h3>
            <p className="properties-header-subtitle">
              Property Editor • VIF Confidence
            </p>
          </div>
        </div>
      </div>

      {/* Properties List */}
      <div className="properties-list">
        {properties.map((property) => (
          <div key={property.key} className="properties-item">
            <div className="properties-item-left">
              <div className="properties-key">{property.key}</div>
              {property.description && (
                <div className="properties-description">{property.description}</div>
              )}
            </div>
            <div className="properties-item-right">
              {renderPropertyValue(property)}
              {property.confidence !== undefined && (
                <ConfidenceIndicator confidence={property.confidence} size="sm" variant="inline" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

