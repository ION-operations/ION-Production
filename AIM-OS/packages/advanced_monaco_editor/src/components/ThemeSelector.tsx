/**
 * Theme Selector Component
 * 
 * Provides a comprehensive theme selection interface including:
 * - Theme preview
 * - Accessibility options
 * - Custom theme creation
 * - Theme management
 */

import React, { useState, useEffect, useCallback } from 'react';
import { ThemeManager, Theme, ThemeConfig } from '../themes/ThemeManager';
import './ThemeSelector.css';

export interface ThemeSelectorProps {
  themeManager: ThemeManager;
  onThemeChange?: (theme: Theme) => void;
  onConfigChange?: (config: ThemeConfig) => void;
  className?: string;
  showAccessibility?: boolean;
  showCustomThemes?: boolean;
  showPreview?: boolean;
}

export const ThemeSelector: React.FC<ThemeSelectorProps> = ({
  themeManager,
  onThemeChange,
  onConfigChange,
  className = '',
  showAccessibility = true,
  showCustomThemes = true,
  showPreview = true
}) => {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [currentTheme, setCurrentTheme] = useState<Theme | null>(null);
  const [config, setConfig] = useState<ThemeConfig>(themeManager.getConfig());
  const [isOpen, setIsOpen] = useState(false);
  const [showCustomThemeCreator, setShowCustomThemeCreator] = useState(false);
  const [customThemeForm, setCustomThemeForm] = useState({
    id: '',
    name: '',
    description: '',
    author: '',
    baseTheme: 'default-dark',
    colors: {} as Partial<Theme['colors']>
  });

  useEffect(() => {
    const updateThemes = () => {
      setThemes(themeManager.getAllThemes());
      setCurrentTheme(themeManager.getCurrentTheme() || null);
    };

    updateThemes();
    
    themeManager.on('themeChanged', updateThemes);
    themeManager.on('themeRegistered', updateThemes);
    themeManager.on('themeUnregistered', updateThemes);
    themeManager.on('configUpdated', (newConfig) => {
      setConfig(newConfig);
    });

    return () => {
      themeManager.off('themeChanged', updateThemes);
      themeManager.off('themeRegistered', updateThemes);
      themeManager.off('themeUnregistered', updateThemes);
      themeManager.off('configUpdated', setConfig);
    };
  }, [themeManager]);

  const handleThemeSelect = useCallback((themeId: string) => {
    const success = themeManager.setTheme(themeId);
    if (success) {
      const theme = themeManager.getTheme(themeId);
      if (theme) {
        setCurrentTheme(theme);
        onThemeChange?.(theme);
      }
    }
  }, [themeManager, onThemeChange]);

  const handleConfigChange = useCallback((newConfig: Partial<ThemeConfig>) => {
    themeManager.updateConfig(newConfig);
    onConfigChange?.(themeManager.getConfig());
  }, [themeManager, onConfigChange]);

  const handleCreateCustomTheme = useCallback(() => {
    try {
      const theme = themeManager.createCustomTheme(
        customThemeForm.id,
        customThemeForm.name,
        customThemeForm.description,
        customThemeForm.author,
        customThemeForm.baseTheme,
        customThemeForm.colors
      );
      
      setShowCustomThemeCreator(false);
      setCustomThemeForm({
        id: '',
        name: '',
        description: '',
        author: '',
        baseTheme: 'default-dark',
        colors: {}
      });
      
      // Select the new theme
      handleThemeSelect(theme.id);
    } catch (error) {
      console.error('Failed to create custom theme:', error);
    }
  }, [themeManager, customThemeForm, handleThemeSelect]);

  const handleDeleteCustomTheme = useCallback((themeId: string) => {
    if (themeManager.unregisterTheme(themeId)) {
      // If we deleted the current theme, switch to default
      if (currentTheme?.id === themeId) {
        handleThemeSelect('default-dark');
      }
    }
  }, [themeManager, currentTheme, handleThemeSelect]);

  const groupedThemes = themes.reduce((groups, theme) => {
    const category = theme.metadata.isCustom ? 'Custom' : 'Built-in';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(theme);
    return groups;
  }, {} as Record<string, Theme[]>);

  return (
    <div className={`theme-selector ${className}`}>
      <div className="theme-selector-header">
        <button
          className="theme-selector-toggle"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          aria-haspopup="true"
        >
          <span className="theme-selector-current">
            {currentTheme?.metadata.name || 'Select Theme'}
          </span>
          <span className="theme-selector-arrow">
            {isOpen ? '▲' : '▼'}
          </span>
        </button>
        
        {showCustomThemes && (
          <button
            className="theme-selector-create"
            onClick={() => setShowCustomThemeCreator(true)}
            title="Create Custom Theme"
          >
            +
          </button>
        )}
      </div>

      {isOpen && (
        <div className="theme-selector-dropdown">
          {Object.entries(groupedThemes).map(([category, categoryThemes]) => (
            <div key={category} className="theme-selector-category">
              <div className="theme-selector-category-header">
                {category}
                {category === 'Custom' && (
                  <button
                    className="theme-selector-category-action"
                    onClick={() => setShowCustomThemeCreator(true)}
                    title="Create Custom Theme"
                  >
                    +
                  </button>
                )}
              </div>
              
              {categoryThemes.map((theme) => (
                <div
                  key={theme.id}
                  className={`theme-selector-option ${
                    currentTheme?.id === theme.id ? 'selected' : ''
                  }`}
                  onClick={() => handleThemeSelect(theme.id)}
                >
                  <div className="theme-selector-option-preview">
                    <div
                      className="theme-preview"
                      style={{
                        backgroundColor: theme.colors.background,
                        color: theme.colors.foreground
                      }}
                    >
                      <div
                        className="theme-preview-keyword"
                        style={{ color: theme.colors.keyword }}
                      >
                        function
                      </div>
                      <div
                        className="theme-preview-string"
                        style={{ color: theme.colors.string }}
                      >
                        "hello"
                      </div>
                      <div
                        className="theme-preview-comment"
                        style={{ color: theme.colors.comment }}
                      >
                        // comment
                      </div>
                    </div>
                  </div>
                  
                  <div className="theme-selector-option-info">
                    <div className="theme-selector-option-name">
                      {theme.metadata.name}
                    </div>
                    <div className="theme-selector-option-description">
                      {theme.metadata.description}
                    </div>
                    <div className="theme-selector-option-meta">
                      {theme.metadata.author} • {theme.metadata.version}
                      {theme.metadata.isHighContrast && ' • High Contrast'}
                      {theme.metadata.accessibility.wcagLevel && ` • WCAG ${theme.metadata.accessibility.wcagLevel}`}
                    </div>
                  </div>
                  
                  {theme.metadata.isCustom && (
                    <button
                      className="theme-selector-option-delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteCustomTheme(theme.id);
                      }}
                      title="Delete Custom Theme"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {showAccessibility && (
        <div className="theme-selector-accessibility">
          <h4>Accessibility</h4>
          
          <div className="accessibility-option">
            <label>
              <input
                type="checkbox"
                checked={config.accessibility.highContrast}
                onChange={(e) => handleConfigChange({
                  accessibility: {
                    ...config.accessibility,
                    highContrast: e.target.checked
                  }
                })}
              />
              High Contrast
            </label>
          </div>
          
          <div className="accessibility-option">
            <label>
              <input
                type="checkbox"
                checked={config.accessibility.reducedMotion}
                onChange={(e) => handleConfigChange({
                  accessibility: {
                    ...config.accessibility,
                    reducedMotion: e.target.checked
                  }
                })}
              />
              Reduced Motion
            </label>
          </div>
          
          <div className="accessibility-option">
            <label>
              Font Size:
              <select
                value={config.accessibility.fontSize}
                onChange={(e) => handleConfigChange({
                  accessibility: {
                    ...config.accessibility,
                    fontSize: e.target.value as 'small' | 'medium' | 'large'
                  }
                })}
              >
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
            </label>
          </div>
        </div>
      )}

      {showCustomThemeCreator && (
        <div className="theme-selector-custom-creator">
          <div className="custom-theme-form">
            <h4>Create Custom Theme</h4>
            
            <div className="form-group">
              <label>
                Theme ID:
                <input
                  type="text"
                  value={customThemeForm.id}
                  onChange={(e) => setCustomThemeForm({
                    ...customThemeForm,
                    id: e.target.value
                  })}
                  placeholder="my-custom-theme"
                />
              </label>
            </div>
            
            <div className="form-group">
              <label>
                Name:
                <input
                  type="text"
                  value={customThemeForm.name}
                  onChange={(e) => setCustomThemeForm({
                    ...customThemeForm,
                    name: e.target.value
                  })}
                  placeholder="My Custom Theme"
                />
              </label>
            </div>
            
            <div className="form-group">
              <label>
                Description:
                <textarea
                  value={customThemeForm.description}
                  onChange={(e) => setCustomThemeForm({
                    ...customThemeForm,
                    description: e.target.value
                  })}
                  placeholder="A custom theme for..."
                />
              </label>
            </div>
            
            <div className="form-group">
              <label>
                Author:
                <input
                  type="text"
                  value={customThemeForm.author}
                  onChange={(e) => setCustomThemeForm({
                    ...customThemeForm,
                    author: e.target.value
                  })}
                  placeholder="Your Name"
                />
              </label>
            </div>
            
            <div className="form-group">
              <label>
                Base Theme:
                <select
                  value={customThemeForm.baseTheme}
                  onChange={(e) => setCustomThemeForm({
                    ...customThemeForm,
                    baseTheme: e.target.value
                  })}
                >
                  {themes.filter(t => !t.metadata.isCustom).map(theme => (
                    <option key={theme.id} value={theme.id}>
                      {theme.metadata.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            
            <div className="form-actions">
              <button
                className="btn-primary"
                onClick={handleCreateCustomTheme}
                disabled={!customThemeForm.id || !customThemeForm.name}
              >
                Create Theme
              </button>
              <button
                className="btn-secondary"
                onClick={() => setShowCustomThemeCreator(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
