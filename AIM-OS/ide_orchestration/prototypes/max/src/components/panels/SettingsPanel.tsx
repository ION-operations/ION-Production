// Settings Panel - Max V2
// IDE settings with AIM-OS integration

import React, { useState, useMemo } from 'react';
import { Settings as SettingsIcon, Save, Refresh, Palette, Code, Keyboard, Bell } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './SettingsPanel.css';

export type SettingsCategory = 'general' | 'editor' | 'appearance' | 'keyboard' | 'notifications' | 'aimos';

export interface Setting {
  id: string;
  category: SettingsCategory;
  label: string;
  description: string;
  type: 'boolean' | 'string' | 'number' | 'select';
  value: any;
  options?: string[];
  confidence?: number;
}

export const SettingsPanel: React.FC = () => {
  const { vif, loading, errors } = useAIMOS();
  const [activeCategory, setActiveCategory] = useState<SettingsCategory>('general');
  const [settings, setSettings] = useState<Setting[]>(() => [
    {
      id: 'autoSave',
      category: 'general',
      label: 'Auto Save',
      description: 'Automatically save files when modified',
      type: 'boolean',
      value: true,
      confidence: 0.90,
    },
    {
      id: 'theme',
      category: 'appearance',
      label: 'Theme',
      description: 'Color theme for the IDE',
      type: 'select',
      value: 'dark',
      options: ['dark', 'light', 'auto'],
      confidence: 0.88,
    },
    {
      id: 'fontSize',
      category: 'editor',
      label: 'Font Size',
      description: 'Editor font size in pixels',
      type: 'number',
      value: 14,
      confidence: 0.85,
    },
    {
      id: 'tabSize',
      category: 'editor',
      label: 'Tab Size',
      description: 'Number of spaces per tab',
      type: 'number',
      value: 2,
      confidence: 0.85,
    },
    {
      id: 'wordWrap',
      category: 'editor',
      label: 'Word Wrap',
      description: 'Wrap long lines',
      type: 'boolean',
      value: true,
      confidence: 0.80,
    },
    {
      id: 'enableAIMOS',
      category: 'aimos',
      label: 'Enable AIM-OS Integration',
      description: 'Enable AIM-OS systems integration',
      type: 'boolean',
      value: true,
      confidence: 0.95,
    },
    {
      id: 'confidenceThreshold',
      category: 'aimos',
      label: 'Confidence Threshold',
      description: 'Minimum confidence for AI operations',
      type: 'number',
      value: 0.70,
      confidence: 0.90,
    },
  ]);

  const categories: SettingsCategory[] = ['general', 'editor', 'appearance', 'keyboard', 'notifications', 'aimos'];

  const filteredSettings = useMemo(() => {
    return settings.filter(s => s.category === activeCategory);
  }, [settings, activeCategory]);

  const handleSettingChange = (id: string, value: any) => {
    setSettings(prev => prev.map(s => s.id === id ? { ...s, value } : s));
  };

  const handleSave = () => {
    // TODO: Save settings
    console.log('Saving settings:', settings);
  };

  const handleReset = () => {
    // TODO: Reset to defaults
    console.log('Resetting settings');
  };

  const getCategoryIcon = (category: SettingsCategory) => {
    switch (category) {
      case 'general':
        return <SettingsIcon className="settings-category-icon" />;
      case 'editor':
        return <Code className="settings-category-icon" />;
      case 'appearance':
        return <Palette className="settings-category-icon" />;
      case 'keyboard':
        return <Keyboard className="settings-category-icon" />;
      case 'notifications':
        return <Bell className="settings-category-icon" />;
      case 'aimos':
        return <SettingsIcon className="settings-category-icon" />;
      default:
        return <SettingsIcon className="settings-category-icon" />;
    }
  };

  if (loading.vif) {
    return <PanelLoading message="Loading Settings..." />;
  }

  if (errors.vif) {
    return (
      <div className="settings-error" role="alert">
        <p>Error loading Settings: {errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="settings-panel" role="region" aria-label="Settings Panel">
      {/* Header */}
      <div className="settings-header">
        <div className="settings-header-left">
          <SettingsIcon className="settings-header-icon" />
          <div>
            <h3 className="settings-header-title">Settings</h3>
            <p className="settings-header-subtitle">
              IDE Configuration • VIF Confidence
            </p>
          </div>
        </div>
        <div className="settings-header-right">
          <button className="settings-reset-button" onClick={handleReset} aria-label="Reset settings">
            <Refresh className="settings-icon" />
          </button>
          <button className="settings-save-button" onClick={handleSave} aria-label="Save settings">
            <Save className="settings-icon" />
            Save
          </button>
        </div>
      </div>

      {/* Categories */}
      <div className="settings-categories">
        {categories.map((category) => (
          <button
            key={category}
            className={`settings-category ${activeCategory === category ? 'active' : ''}`}
            onClick={() => setActiveCategory(category)}
            aria-label={`${category} settings`}
          >
            {getCategoryIcon(category)}
            <span className="settings-category-label">
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </span>
          </button>
        ))}
      </div>

      {/* Settings List */}
      <div className="settings-list">
        {filteredSettings.length === 0 ? (
          <div className="settings-empty">
            <SettingsIcon className="settings-empty-icon" />
            <p>No settings in this category</p>
          </div>
        ) : (
          filteredSettings.map((setting) => (
            <div key={setting.id} className="settings-item">
              <div className="settings-item-left">
                <div className="settings-label">{setting.label}</div>
                <div className="settings-description">{setting.description}</div>
              </div>
              <div className="settings-item-right">
                {setting.type === 'boolean' && (
                  <label className="settings-toggle">
                    <input
                      type="checkbox"
                      checked={setting.value}
                      onChange={(e) => handleSettingChange(setting.id, e.target.checked)}
                    />
                    <span className="settings-toggle-slider" />
                  </label>
                )}
                {setting.type === 'string' && (
                  <input
                    type="text"
                    value={setting.value}
                    onChange={(e) => handleSettingChange(setting.id, e.target.value)}
                    className="settings-input"
                  />
                )}
                {setting.type === 'number' && (
                  <input
                    type="number"
                    value={setting.value}
                    onChange={(e) => handleSettingChange(setting.id, Number(e.target.value))}
                    className="settings-input settings-input-number"
                  />
                )}
                {setting.type === 'select' && setting.options && (
                  <select
                    value={setting.value}
                    onChange={(e) => handleSettingChange(setting.id, e.target.value)}
                    className="settings-select"
                  >
                    {setting.options.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                )}
                {setting.confidence !== undefined && (
                  <ConfidenceIndicator confidence={setting.confidence} size="sm" variant="inline" />
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

