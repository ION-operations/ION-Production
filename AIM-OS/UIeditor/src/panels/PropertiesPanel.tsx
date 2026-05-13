/* OmniBuilder — Properties Panel */
import { useEditorStore } from '../store/editorStore';
import type { PropertySourceKind } from '../types';
import VisualInstruments from './VisualInstruments';
import ConnectionGraph from './ConnectionGraph';
import { IconVisualInstruments } from '../icons/Icons';

const BADGE_CLASS: Record<PropertySourceKind, string> = {
    token: 'token', class: 'class', rule: 'rule',
    prop: 'prop', inline: 'inline', inherited: 'inherited',
};

export default function PropertiesPanel() {
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const nodes = useEditorStore((s) => s.nodes);
    const sourceAnchors = useEditorStore((s) => s.sourceAnchors);
    const propertyStacks = useEditorStore((s) => s.propertyStacks);
    const layoutContexts = useEditorStore((s) => s.layoutContexts);
    const { rightPanelTab, setRightPanelTab } = useEditorStore();

    const selId = selectedIds[0];
    const node = selId ? nodes[selId] : null;
    const anchor = node ? sourceAnchors[node.sourceAnchorIds[0]] : null;
    const props = selId ? propertyStacks[selId] : null;
    const conf = anchor?.confidence ?? 0;
    const confColor = conf > 0.9 ? 'var(--ob-conf-high)' : conf > 0.7 ? 'var(--ob-conf-medium)' : conf > 0.5 ? 'var(--ob-conf-low)' : 'var(--ob-conf-none)';

    // Find layout context
    const layout = node?.layoutContextId ? layoutContexts[node.layoutContextId] :
        Object.values(layoutContexts).find((l) => l.parentNodeId === node?.parentId) ?? null;

    if (!node) {
        return (
            <div className="ob-right-panel">
                <div className="ob-panel-tabs">
                    <button className="ob-panel-tab active">Properties</button>
                </div>
                <div className="ob-empty-state">
                    <div className="ob-empty-state-icon">⬚</div>
                    <div className="ob-empty-state-text">Select a node to inspect</div>
                </div>
            </div>
        );
    }

    return (
        <div className="ob-right-panel">
            {/* Tabs */}
            <div className="ob-panel-tabs">
                {(['visual', 'layout', 'style', 'source'] as const).map((t) => (
                    <button
                        key={t}
                        className={`ob-panel-tab${rightPanelTab === t ? ' active' : ''}`}
                        onClick={() => setRightPanelTab(t)}
                    >
                        {t === 'visual' && <IconVisualInstruments size={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />}
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                ))}
            </div>

            <div className="ob-panel-content">
                {/* Visual Instruments Tab */}
                {rightPanelTab === 'visual' && <VisualInstruments />}

                {/* Node header */}
                <div className="ob-prop-section">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                        <span style={{ fontWeight: 600, fontSize: '13px' }}>{node.componentName || `<${node.tag}>`}</span>
                        <span style={{ fontSize: '9px', color: 'var(--ob-text-tertiary)', fontFamily: 'var(--ob-font-mono)' }}>#{node.id}</span>
                    </div>
                    <div className="ob-confidence-bar">
                        <span style={{ fontSize: '10px', color: 'var(--ob-text-tertiary)' }}>Confidence</span>
                        <div className="ob-confidence-track">
                            <div className="ob-confidence-fill" style={{ width: `${conf * 100}%`, backgroundColor: confColor }} />
                        </div>
                        <span className="ob-confidence-label">{Math.round(conf * 100)}%</span>
                    </div>
                </div>

                {/* Connection Graph */}
                <ConnectionGraph />

                {/* Bounds */}
                <div className="ob-prop-section">
                    <div className="ob-prop-section-title">Bounds</div>
                    {[
                        ['x', node.bounds.x], ['y', node.bounds.y],
                        ['w', node.bounds.w], ['h', node.bounds.h],
                    ].map(([k, v]) => (
                        <div key={k as string} className="ob-prop-row">
                            <span className="ob-prop-label">{k}</span>
                            <span className="ob-prop-value">{v}px</span>
                        </div>
                    ))}
                </div>

                {/* Layout Tab */}
                {rightPanelTab === 'layout' && layout && (
                    <div className="ob-prop-section">
                        <div className="ob-prop-section-title">Layout Context</div>
                        <div className="ob-prop-row">
                            <span className="ob-prop-label">mode</span>
                            <span className="ob-prop-value" style={{ color: 'var(--ob-accent)' }}>{layout.mode}</span>
                        </div>
                        {layout.axis && <div className="ob-prop-row"><span className="ob-prop-label">axis</span><span className="ob-prop-value">{layout.axis}</span></div>}
                        {layout.gap != null && <div className="ob-prop-row"><span className="ob-prop-label">gap</span><span className="ob-prop-value">{layout.gap}px</span></div>}
                        {layout.align && <div className="ob-prop-row"><span className="ob-prop-label">align</span><span className="ob-prop-value">{layout.align}</span></div>}
                        {layout.justify && <div className="ob-prop-row"><span className="ob-prop-label">justify</span><span className="ob-prop-value">{layout.justify}</span></div>}
                        {layout.tracks && <div className="ob-prop-row"><span className="ob-prop-label">tracks</span><span className="ob-prop-value">{layout.tracks.join(' ')}</span></div>}
                        {layout.padding && (
                            <div className="ob-prop-row">
                                <span className="ob-prop-label">padding</span>
                                <span className="ob-prop-value">{layout.padding.top} {layout.padding.right} {layout.padding.bottom} {layout.padding.left}</span>
                            </div>
                        )}
                    </div>
                )}

                {/* Style Tab — Property Ownership Stack */}
                {rightPanelTab === 'style' && props && (
                    <div className="ob-prop-section">
                        <div className="ob-prop-section-title">Style Ownership</div>
                        {props.map((p, i) => (
                            <div key={i} style={{ marginBottom: 8 }}>
                                <div className="ob-prop-row" style={{ marginBottom: 2 }}>
                                    <span className="ob-prop-label">{p.property}</span>
                                    <span className="ob-prop-value">{p.computedValue}</span>
                                </div>
                                {p.sources.map((src, j) => (
                                    <div key={j} className="ob-ownership-item">
                                        <span className={`ob-ownership-badge ${BADGE_CLASS[src.kind]}`}>{src.kind}</span>
                                        <span className="ob-ownership-path" title={src.path}>{src.label}</span>
                                        <span className="ob-ownership-priority">p{src.priority}</span>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </div>
                )}
                {rightPanelTab === 'style' && !props && (
                    <div className="ob-prop-section">
                        <div className="ob-prop-section-title">Style Ownership</div>
                        <div style={{ fontSize: '11px', color: 'var(--ob-text-tertiary)', padding: '8px 0' }}>
                            No property ownership data for this node
                        </div>
                    </div>
                )}

                {/* Source Tab */}
                {rightPanelTab === 'source' && anchor && (
                    <div className="ob-prop-section">
                        <div className="ob-prop-section-title">Source Anchor</div>
                        <div className="ob-source-info">
                            <div className="ob-source-file">
                                <span className="ob-source-file-icon">📄</span>
                                {anchor.filePath}
                            </div>
                        </div>
                        <div style={{ marginTop: 8 }}>
                            {[
                                ['Kind', anchor.ownershipKind],
                                ['Export', anchor.exportName || '—'],
                                ['Symbol', anchor.symbolName || '—'],
                                ['AST Path', anchor.astPath.join(' → ')],
                            ].map(([k, v]) => (
                                <div key={k} className="ob-prop-row">
                                    <span className="ob-prop-label">{k}</span>
                                    <span className="ob-prop-value">{v}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
