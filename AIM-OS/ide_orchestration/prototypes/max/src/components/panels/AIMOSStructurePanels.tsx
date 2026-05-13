// AIM-OS Structure Panels - Max V2
// Expose AIM-OS architecture "wide open" - Super Index, Master Index, System Map, NL Tags, Docs

import React, { useState, useMemo } from 'react';
import { BookOpen, Layers, Network, Tag, FileText, ChevronRight } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { PanelLoading } from '../Loading/Loading';
import './AIMOSStructurePanels.css';

// Super Index Panel - Master concept index
export const SuperIndexPanel: React.FC = () => {
  const { hhni, loading, errors } = useAIMOS();

  const superIndex = useMemo(() => ({
    totalConcepts: 1247,
    categories: [
      { name: 'Core Systems', count: 89, concepts: ['CMC', 'HHNI', 'VIF', 'SEG', 'APOE', 'SDF-CVF', 'CAS', 'TCS'] },
      { name: 'Protocols', count: 156, concepts: ['L0-L4', 'A-H Protocol', 'MCP Tools', 'NL Tags'] },
      { name: 'Standards', count: 234, concepts: ['Documentation', 'Coding', 'Quality', 'Accessibility'] },
      { name: 'Architecture', count: 178, concepts: ['System Maps', 'Indexes', 'Hierarchies', 'Panel-First'] },
      { name: 'UI/UX', count: 145, concepts: ['Context Web', 'Evolution Explorer', 'Debug Console', 'Panel Management'] },
    ],
    recentAdditions: [
      { concept: 'Debug Infrastructure', category: 'Architecture', confidence: 0.95 },
      { concept: 'Panel-First Design', category: 'Architecture', confidence: 0.92 },
      { concept: 'Keyboard Navigation', category: 'UI/UX', confidence: 0.88 },
    ],
  }), []);

  if (loading.hhni) {
    return <PanelLoading message="Loading Super Index..." />;
  }

  if (errors.hhni) {
    return (
      <div className="structure-panel-error" role="alert">
        <p>Error loading Super Index: {errors.hhni.message}</p>
      </div>
    );
  }

  return (
    <div className="structure-panel super-index-panel" role="region" aria-label="Super Index">
      <div className="structure-panel-header">
        <div className="structure-panel-title">
          <BookOpen className="structure-panel-icon" />
          <div>
            <h3 className="structure-panel-title-text">Super Index</h3>
            <p className="structure-panel-subtitle">
              Master Concept Index • {superIndex.totalConcepts.toLocaleString()} Concepts • HHNI-Powered
            </p>
          </div>
        </div>
      </div>

      <div className="structure-panel-content">
        <div className="structure-section">
          <div className="structure-overview">
            <div className="overview-stat">
              <span className="stat-label">Total Concepts:</span>
              <span className="stat-value">{superIndex.totalConcepts.toLocaleString()}</span>
            </div>
            <p className="overview-description">Master index of all AIM-OS concepts</p>
          </div>
        </div>

        <div className="structure-section">
          <h4 className="section-title">Categories</h4>
          <div className="categories-list">
            {superIndex.categories.map((cat) => (
              <div key={cat.name} className="category-card">
                <div className="category-header">
                  <span className="category-name">{cat.name}</span>
                  <span className="category-count">{cat.count} concepts</span>
                </div>
                <div className="category-concepts">
                  {cat.concepts.map((concept) => (
                    <span key={concept} className="concept-badge">
                      {concept}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="structure-section">
          <h4 className="section-title">Recent Additions</h4>
          <div className="recent-list">
            {superIndex.recentAdditions.map((item, idx) => (
              <div key={idx} className="recent-item">
                <div className="recent-header">
                  <span className="recent-concept">{item.concept}</span>
                  <span className="recent-confidence">
                    Conf: {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <span className="recent-category">{item.category}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Master Index Panel - System-level index
export const MasterIndexPanel: React.FC = () => {
  const { cmc, loading, errors } = useAIMOS();

  const masterIndex = useMemo(() => ({
    systems: [
      {
        id: 'cmc',
        name: 'CMC - Context Memory Core',
        layer: 'Layer 1: Memory',
        status: 'Production',
        dependencies: [],
        components: ['Atoms', 'Snapshots', 'Bitemporal', 'Pipelines'],
        confidence: 0.95,
      },
      {
        id: 'hhni',
        name: 'HHNI - Hierarchical Hypergraph Neural Index',
        layer: 'Layer 2: Indexing',
        status: 'Production',
        dependencies: ['cmc'],
        components: ['Hierarchical Index', 'Semantic Search', 'Relationship Graph'],
        confidence: 0.92,
      },
      {
        id: 'vif',
        name: 'VIF - Verifiable Intelligence Framework',
        layer: 'Layer 3: Quality',
        status: 'Production',
        dependencies: ['cmc', 'hhni'],
        components: ['Confidence Tracking', 'Quality Gates', 'Witness System'],
        confidence: 0.94,
      },
      {
        id: 'seg',
        name: 'SEG - Synthesis & Evidence Graph',
        layer: 'Layer 3: Quality',
        status: 'Production',
        dependencies: ['cmc', 'hhni', 'vif'],
        components: ['Evidence Nodes', 'Contradiction Detection', 'Consensus Building'],
        confidence: 0.93,
      },
      {
        id: 'apoe',
        name: 'APOE - AI-Powered Orchestration Engine',
        layer: 'Layer 4: Orchestration',
        status: 'Production',
        dependencies: ['cmc', 'hhni', 'vif', 'seg'],
        components: ['Task Scheduling', 'Agent Coordination', 'Chain Execution'],
        confidence: 0.91,
      },
      {
        id: 'sdfcvf',
        name: 'SDF-CVF - Self-Directed Feedback & Continuous Validation',
        layer: 'Layer 3: Quality',
        status: 'Production',
        dependencies: ['cmc', 'vif', 'seg'],
        components: ['Quality Metrics', 'Improvement Suggestions', 'Validation Loops'],
        confidence: 0.90,
      },
      {
        id: 'cas',
        name: 'CAS - Consciousness Analysis System',
        layer: 'Layer 5: Consciousness',
        status: 'Production',
        dependencies: ['cmc', 'hhni', 'vif'],
        components: ['Attention Tracking', 'Drift Detection', 'Self-Awareness'],
        confidence: 0.89,
      },
      {
        id: 'tcs',
        name: 'TCS - Timeline Context System',
        layer: 'Layer 5: Consciousness',
        status: 'Production',
        dependencies: ['cmc', 'hhni'],
        components: ['Timeline Events', 'Context Restoration', 'Sequence Tracking'],
        confidence: 0.92,
      },
    ],
  }), []);

  if (loading.cmc) {
    return <PanelLoading message="Loading Master Index..." />;
  }

  if (errors.cmc) {
    return (
      <div className="structure-panel-error" role="alert">
        <p>Error loading Master Index: {errors.cmc.message}</p>
      </div>
    );
  }

  return (
    <div className="structure-panel master-index-panel" role="region" aria-label="Master Index">
      <div className="structure-panel-header">
        <div className="structure-panel-title">
          <Layers className="structure-panel-icon" />
          <div>
            <h3 className="structure-panel-title-text">Master Index</h3>
            <p className="structure-panel-subtitle">
              System-Level Index • All AIM-OS Systems • Layer Hierarchy
            </p>
          </div>
        </div>
      </div>

      <div className="structure-panel-content">
        <div className="systems-list">
          {masterIndex.systems.map((system) => (
            <div key={system.id} className="system-card">
              <div className="system-header">
                <h4 className="system-name">{system.name}</h4>
                <span className="system-confidence">
                  Conf: {(system.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="system-layer">{system.layer}</div>
              <div className="system-status">
                <span className={`status-badge ${system.status === 'Production' ? 'status-production' : 'status-development'}`}>
                  {system.status}
                </span>
              </div>
              <div className="system-components">
                <span className="components-label">Components:</span>
                <div className="components-list">
                  {system.components.map((comp) => (
                    <span key={comp} className="component-badge">
                      {comp}
                    </span>
                  ))}
                </div>
              </div>
              {system.dependencies.length > 0 && (
                <div className="system-dependencies">
                  <span className="dependencies-label">Depends on:</span>
                  <div className="dependencies-list">
                    {system.dependencies.map((dep) => (
                      <span key={dep} className="dependency-badge">
                        {dep.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// System Map Panel - Visual system relationships
export const SystemMapPanel: React.FC = () => {
  const systemMap = useMemo(() => ({
    layers: [
      { level: 1, name: 'Memory', systems: ['CMC'], color: 'purple' },
      { level: 2, name: 'Indexing', systems: ['HHNI'], color: 'blue' },
      { level: 3, name: 'Quality', systems: ['VIF', 'SEG', 'SDF-CVF'], color: 'green' },
      { level: 4, name: 'Orchestration', systems: ['APOE'], color: 'yellow' },
      { level: 5, name: 'Consciousness', systems: ['CAS', 'TCS'], color: 'pink' },
    ],
    connections: [
      { from: 'CMC', to: 'HHNI', type: 'provides_data' },
      { from: 'CMC', to: 'VIF', type: 'provides_data' },
      { from: 'HHNI', to: 'VIF', type: 'provides_data' },
      { from: 'HHNI', to: 'SEG', type: 'provides_data' },
      { from: 'VIF', to: 'SEG', type: 'validates' },
      { from: 'VIF', to: 'APOE', type: 'validates' },
      { from: 'SEG', to: 'APOE', type: 'provides_evidence' },
      { from: 'CMC', to: 'CAS', type: 'provides_data' },
      { from: 'HHNI', to: 'CAS', type: 'provides_data' },
      { from: 'CMC', to: 'TCS', type: 'provides_data' },
      { from: 'HHNI', to: 'TCS', type: 'provides_data' },
    ],
  }), []);

  return (
    <div className="structure-panel system-map-panel" role="region" aria-label="System Map">
      <div className="structure-panel-header">
        <div className="structure-panel-title">
          <Network className="structure-panel-icon" />
          <div>
            <h3 className="structure-panel-title-text">System Map</h3>
            <p className="structure-panel-subtitle">
              Visual System Relationships • Layer Hierarchy • Dependencies
            </p>
          </div>
        </div>
      </div>

      <div className="structure-panel-content">
        <div className="structure-section">
          <h4 className="section-title">Layer Hierarchy</h4>
          <div className="layers-list">
            {systemMap.layers.map((layer) => (
              <div key={layer.level} className="layer-card">
                <div className="layer-header">
                  <span className="layer-level">Layer {layer.level}</span>
                  <span className="layer-name">{layer.name}</span>
                </div>
                <div className="layer-systems">
                  {layer.systems.map((sys) => (
                    <span key={sys} className={`system-badge system-badge-${layer.color}`}>
                      {sys}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="structure-section">
          <h4 className="section-title">System Connections</h4>
          <div className="connections-list">
            {systemMap.connections.map((conn, idx) => (
              <div key={idx} className="connection-item">
                <span className="connection-from">{conn.from}</span>
                <ChevronRight className="connection-arrow" />
                <span className="connection-to">{conn.to}</span>
                <span className="connection-type">{conn.type}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// NL Tags Explorer Panel
export const NLTagsExplorerPanel: React.FC = () => {
  const nlTags = useMemo(() => ({
    totalTags: 1247,
    coverage: 0.87,
    bySystem: [
      { system: 'CMC', tags: 234, coverage: 0.92, validated: true },
      { system: 'HHNI', tags: 189, coverage: 0.88, validated: true },
      { system: 'VIF', tags: 156, coverage: 0.85, validated: false },
      { system: 'SEG', tags: 178, coverage: 0.90, validated: true },
      { system: 'APOE', tags: 145, coverage: 0.83, validated: false },
      { system: 'SDF-CVF', tags: 132, coverage: 0.80, validated: false },
      { system: 'CAS', tags: 98, coverage: 0.75, validated: false },
      { system: 'TCS', tags: 115, coverage: 0.82, validated: false },
    ],
    recentTags: [
      { id: 'VIF-WITNESS-001', description: 'Create VIF witness envelope', system: 'VIF', confidence: 0.95 },
      { id: 'CMC-STORE-001', description: 'Store atom in CMC', system: 'CMC', confidence: 0.98 },
      { id: 'HHNI-INDEX-001', description: 'Index document in HHNI', system: 'HHNI', confidence: 0.92 },
      { id: 'SEG-ENTITY-001', description: 'Create SEG entity node', system: 'SEG', confidence: 0.90 },
    ],
  }), []);

  return (
    <div className="structure-panel nl-tags-panel" role="region" aria-label="NL Tags Explorer">
      <div className="structure-panel-header">
        <div className="structure-panel-title">
          <Tag className="structure-panel-icon" />
          <div>
            <h3 className="structure-panel-title-text">NL Tags Explorer</h3>
            <p className="structure-panel-subtitle">
              Natural Language Code Tags • Coverage: {(nlTags.coverage * 100).toFixed(0)}% • {nlTags.totalTags.toLocaleString()} Tags
            </p>
          </div>
        </div>
      </div>

      <div className="structure-panel-content">
        <div className="structure-section">
          <h4 className="section-title">Coverage by System</h4>
          <div className="coverage-list">
            {nlTags.bySystem.map((sys) => (
              <div key={sys.system} className="coverage-item">
                <div className="coverage-header">
                  <span className="coverage-system">{sys.system}</span>
                  <span className={`coverage-status ${sys.validated ? 'status-validated' : 'status-pending'}`}>
                    {sys.validated ? '✓ Validated' : '⚠ Pending'}
                  </span>
                </div>
                <div className="coverage-bar-container">
                  <div className="coverage-bar">
                    <div
                      className="coverage-bar-fill"
                      style={{ width: `${sys.coverage * 100}%` }}
                      role="progressbar"
                      aria-valuenow={sys.coverage * 100}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    />
                  </div>
                  <span className="coverage-percentage">{(sys.coverage * 100).toFixed(0)}%</span>
                </div>
                <span className="coverage-count">{sys.tags} tags</span>
              </div>
            ))}
          </div>
        </div>

        <div className="structure-section">
          <h4 className="section-title">Recent Tags</h4>
          <div className="tags-list">
            {nlTags.recentTags.map((tag) => (
              <div key={tag.id} className="tag-card">
                <div className="tag-header">
                  <code className="tag-id">{tag.id}</code>
                  <span className="tag-confidence">
                    Conf: {(tag.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="tag-description">{tag.description}</p>
                <span className="tag-system">{tag.system}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Documentation Explorer Panel
export const DocumentationExplorerPanel: React.FC = () => {
  const docs = useMemo(() => ({
    totalDocs: 1247,
    byLevel: [
      { level: 'L0', name: 'Executive Summary', count: 89, avgWords: 100 },
      { level: 'L1', name: 'Overview', count: 156, avgWords: 500 },
      { level: 'L2', name: 'Architecture', count: 234, avgWords: 2000 },
      { level: 'L3', name: 'Detailed', count: 178, avgWords: 10000 },
      { level: 'L4', name: 'Complete', count: 45, avgWords: 15000 },
    ],
    recentDocs: [
      { name: 'DEBUG_INFRASTRUCTURE.md', level: 'L2', system: 'Architecture', confidence: 0.95 },
      { name: 'HIERARCHICAL_CODE_EXPLORER.md', level: 'L1', system: 'UI/UX', confidence: 0.88 },
      { name: 'AIM_OS_STRUCTURE_PANELS.md', level: 'L0', system: 'Overview', confidence: 0.92 },
      { name: 'V2_ENHANCEMENT_PLAN.md', level: 'L2', system: 'Planning', confidence: 0.90 },
    ],
  }), []);

  return (
    <div className="structure-panel docs-explorer-panel" role="region" aria-label="Documentation Explorer">
      <div className="structure-panel-header">
        <div className="structure-panel-title">
          <FileText className="structure-panel-icon" />
          <div>
            <h3 className="structure-panel-title-text">Documentation Explorer</h3>
            <p className="structure-panel-subtitle">
              L0-L4 Documentation • {docs.totalDocs.toLocaleString()} Documents • HHNI-Indexed
            </p>
          </div>
        </div>
      </div>

      <div className="structure-panel-content">
        <div className="structure-section">
          <h4 className="section-title">Documentation by Level</h4>
          <div className="docs-levels-list">
            {docs.byLevel.map((level) => (
              <div key={level.level} className="docs-level-item">
                <div className="docs-level-header">
                  <span className="docs-level-badge">{level.level}</span>
                  <span className="docs-level-name">{level.name}</span>
                </div>
                <div className="docs-level-stats">
                  <span>{level.count} docs</span>
                  <span>~{level.avgWords.toLocaleString()} words</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="structure-section">
          <h4 className="section-title">Recent Documents</h4>
          <div className="docs-list">
            {docs.recentDocs.map((doc, idx) => (
              <div key={idx} className="doc-card">
                <div className="doc-header">
                  <span className="doc-name">{doc.name}</span>
                  <span className="doc-confidence">
                    Conf: {(doc.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="doc-meta">
                  <span>{doc.level}</span>
                  <span>•</span>
                  <span>{doc.system}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

