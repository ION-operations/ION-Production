/* OmniBuilder — Layer Tree (Custom SVG Icons) */
import { useEditorStore } from '../store/editorStore';
import type { NodeId } from '../types';
import { IconComponent, IconElement, IconChevron, IconLayers } from '../icons/Icons';

function TreeNode({ nodeId }: { nodeId: NodeId }) {
    const node = useEditorStore((s) => s.nodes[nodeId]);
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const expanded = useEditorStore((s) => s.expandedTreeNodes);
    const hoveredId = useEditorStore((s) => s.hoveredNodeId);
    const sourceAnchors = useEditorStore((s) => s.sourceAnchors);
    const { selectNode, setHoveredNode, toggleTreeNode } = useEditorStore();

    if (!node) return null;

    const isSelected = selectedIds.includes(nodeId);
    const isHovered = hoveredId === nodeId;
    const isExpanded = expanded.has(nodeId);
    const hasChildren = node.children.length > 0;
    const anchor = sourceAnchors[node.sourceAnchorIds[0]];
    const conf = anchor?.confidence ?? 0;
    const confColor = conf > 0.9 ? 'var(--ob-conf-high)' : conf > 0.7 ? 'var(--ob-conf-medium)' : conf > 0.5 ? 'var(--ob-conf-low)' : 'var(--ob-conf-none)';

    return (
        <>
            <div
                className={`ob-tree-node${isSelected ? ' selected' : ''}${isHovered ? ' hovered' : ''}`}
                style={{ paddingLeft: 12 + node.depth * 16 }}
                onClick={(e) => { e.stopPropagation(); selectNode(nodeId); }}
                onMouseEnter={() => setHoveredNode(nodeId)}
                onMouseLeave={() => setHoveredNode(null)}
            >
                {hasChildren ? (
                    <span
                        className="ob-tree-toggle"
                        onClick={(e) => { e.stopPropagation(); toggleTreeNode(nodeId); }}
                        style={{ transform: isExpanded ? 'rotate(90deg)' : undefined, transition: 'transform 0.15s ease' }}
                    >
                        <IconChevron size={10} />
                    </span>
                ) : (
                    <span className="ob-tree-toggle" style={{ width: 14 }} />
                )}
                <span className={`ob-tree-icon${node.componentName ? ' component' : ''}`}>
                    {node.componentName ? <IconComponent size={10} /> : <IconElement size={10} />}
                </span>
                <span className="ob-tree-label">
                    {node.componentName || `<${node.tag}>`}{' '}
                    <span style={{ opacity: 0.4 }}>
                        {node.label !== (node.componentName || node.tag) ? node.label : ''}
                    </span>
                </span>
                <span className="ob-tree-conf-dot" style={{ backgroundColor: confColor }}
                    title={`Confidence: ${Math.round(conf * 100)}%`} />
            </div>
            {isExpanded && hasChildren && node.children.map((childId) => (
                <TreeNode key={childId} nodeId={childId} />
            ))}
        </>
    );
}

export default function LayerTree() {
    const nodes = useEditorStore((s) => s.nodes);
    const rootNode = nodes['root'];

    return (
        <div className="ob-left-panel" style={{ border: 'none', background: 'transparent', backdropFilter: 'none' }}>
            <div className="ob-panel-header">
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <IconLayers size={12} />
                    Layers
                </span>
                <span style={{ fontSize: '9px', color: 'var(--ob-text-tertiary)' }}>
                    {Object.keys(nodes).length} nodes
                </span>
            </div>
            <div className="ob-panel-content">
                {rootNode && <TreeNode nodeId="root" />}
            </div>
        </div>
    );
}
