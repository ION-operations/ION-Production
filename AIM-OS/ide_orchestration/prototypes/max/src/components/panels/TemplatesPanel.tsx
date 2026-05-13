// Templates Panel - Max V2
// Code and project templates with AIM-OS integration

import React, { useState, useMemo } from 'react';
import { FileText, Code, Folder, Search, Copy, ExternalLink, Zap } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './TemplatesPanel.css';

export type TemplateCategory = 'all' | 'component' | 'hook' | 'panel' | 'project' | 'utility';

export interface Template {
  id: string;
  name: string;
  category: TemplateCategory;
  description: string;
  code: string;
  tags: string[];
  confidence?: number;
  usageCount?: number;
  hhniPath?: string[];
}

export const TemplatesPanel: React.FC = () => {
  const { hhni, vif, loading, errors } = useAIMOS();
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  // Mock templates with AIM-OS integration
  const templates: Template[] = useMemo(() => [
    {
      id: 'tpl_1',
      name: 'React Component',
      category: 'component',
      description: 'Basic React functional component with TypeScript',
      code: `import React from 'react';

interface Props {
  // Add props here
}

export const ComponentName: React.FC<Props> = ({}) => {
  return (
    <div>
      {/* Component content */}
    </div>
  );
};`,
      tags: ['react', 'typescript', 'component'],
      confidence: 0.95,
      usageCount: 12,
      hhniPath: ['IDE', 'Templates', 'Components', 'React'],
    },
    {
      id: 'tpl_2',
      name: 'Custom Hook',
      category: 'hook',
      description: 'Custom React hook with TypeScript',
      code: `import { useState, useEffect } from 'react';

export const useCustomHook = () => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Hook logic
  }, []);

  return { state, setState };
};`,
      tags: ['react', 'hook', 'typescript'],
      confidence: 0.92,
      usageCount: 8,
      hhniPath: ['IDE', 'Templates', 'Hooks', 'Custom'],
    },
    {
      id: 'tpl_3',
      name: 'Panel Component',
      category: 'panel',
      description: 'IDE panel component with AIM-OS integration',
      code: `import React from 'react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import './PanelName.css';

export const PanelName: React.FC = () => {
  const { cmc, vif, loading, errors } = useAIMOS();

  if (loading.cmc || loading.vif) {
    return <PanelLoading message="Loading..." />;
  }

  return (
    <div className="panel-name">
      {/* Panel content */}
    </div>
  );
};`,
      tags: ['panel', 'aimos', 'react'],
      confidence: 0.90,
      usageCount: 15,
      hhniPath: ['IDE', 'Templates', 'Panels', 'AIMOS'],
    },
    {
      id: 'tpl_4',
      name: 'TypeScript Interface',
      category: 'utility',
      description: 'TypeScript interface template',
      code: `export interface InterfaceName {
  // Add properties here
}`,
      tags: ['typescript', 'interface'],
      confidence: 0.88,
      usageCount: 20,
      hhniPath: ['IDE', 'Templates', 'Types', 'Interface'],
    },
  ], []);

  // Filter templates
  const filteredTemplates = useMemo(() => {
    return templates.filter((tpl) => {
      const matchesCategory = selectedCategory === 'all' || tpl.category === selectedCategory;
      const matchesSearch =
        tpl.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tpl.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tpl.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      return matchesCategory && matchesSearch;
    });
  }, [templates, selectedCategory, searchQuery]);

  const selectedTemplateData = useMemo(() => {
    return selectedTemplate ? templates.find(t => t.id === selectedTemplate) : null;
  }, [selectedTemplate, templates]);

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
  };

  const categories: TemplateCategory[] = ['all', 'component', 'hook', 'panel', 'project', 'utility'];

  if (loading.hhni || loading.vif) {
    return <PanelLoading message="Loading Templates..." />;
  }

  if (errors.hhni || errors.vif) {
    return (
      <div className="templates-error" role="alert">
        <p>Error loading Templates: {errors.hhni?.message || errors.vif?.message}</p>
      </div>
    );
  }

  return (
    <div className="templates-panel" role="region" aria-label="Templates Panel">
      {/* Header */}
      <div className="templates-header">
        <div className="templates-header-left">
          <FileText className="templates-header-icon" />
          <div>
            <h3 className="templates-header-title">Templates</h3>
            <p className="templates-header-subtitle">
              Code Templates • Project Templates • HHNI Search
            </p>
          </div>
        </div>
        <div className="templates-header-right">
          <span className="templates-count">{filteredTemplates.length} templates</span>
        </div>
      </div>

      {/* Controls */}
      <div className="templates-controls">
        <div className="templates-search">
          <Search className="templates-search-icon" />
          <input
            type="text"
            className="templates-search-input"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search templates"
          />
        </div>
        <div className="templates-categories">
          {categories.map((category) => (
            <button
              key={category}
              className={`templates-category ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => setSelectedCategory(category)}
              aria-label={`Filter by ${category}`}
            >
              {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Template List */}
      <div className="templates-list">
        {filteredTemplates.length === 0 ? (
          <div className="templates-empty">
            <FileText className="templates-empty-icon" />
            <p>No templates found</p>
            {searchQuery && <p className="templates-empty-hint">Try a different search query</p>}
          </div>
        ) : (
          filteredTemplates.map((template) => (
            <div
              key={template.id}
              className={`templates-item ${selectedTemplate === template.id ? 'selected' : ''}`}
              onClick={() => setSelectedTemplate(selectedTemplate === template.id ? null : template.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setSelectedTemplate(selectedTemplate === template.id ? null : template.id);
                }
              }}
            >
              <div className="templates-item-header">
                <div className="templates-item-left">
                  {template.category === 'component' && <Code className="templates-item-icon" />}
                  {template.category === 'hook' && <Zap className="templates-item-icon" />}
                  {template.category === 'panel' && <FileText className="templates-item-icon" />}
                  {template.category === 'project' && <Folder className="templates-item-icon" />}
                  {template.category === 'utility' && <Code className="templates-item-icon" />}
                  <div className="templates-item-info">
                    <div className="templates-item-name">{template.name}</div>
                    <div className="templates-item-description">{template.description}</div>
                  </div>
                </div>
                <div className="templates-item-right">
                  {template.confidence !== undefined && (
                    <ConfidenceIndicator confidence={template.confidence} size="sm" variant="inline" />
                  )}
                  {template.usageCount !== undefined && (
                    <span className="templates-item-usage">{template.usageCount}x</span>
                  )}
                </div>
              </div>

              {selectedTemplate === template.id && (
                <div className="templates-item-details">
                  {/* Code Preview */}
                  <div className="templates-detail-section">
                    <div className="templates-detail-section-header">
                      Code Preview
                      <button
                        className="templates-copy-button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCopyCode(template.code);
                        }}
                        aria-label="Copy code"
                      >
                        <Copy className="templates-copy-icon" />
                        Copy
                      </button>
                    </div>
                    <div className="templates-code-preview">
                      <pre>
                        <code>{template.code}</code>
                      </pre>
                    </div>
                  </div>

                  {/* Tags */}
                  {template.tags.length > 0 && (
                    <div className="templates-detail-section">
                      <div className="templates-detail-section-header">Tags</div>
                      <div className="templates-tags">
                        {template.tags.map((tag) => (
                          <span key={tag} className="templates-tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

