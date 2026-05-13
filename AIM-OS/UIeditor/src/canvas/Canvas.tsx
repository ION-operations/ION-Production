/* OmniBuilder — Canvas + Overlay + Demo Scene */
import { useRef, useCallback, useEffect } from 'react';
import { useEditorStore } from '../store/editorStore';
import type { NodeId } from '../types';
import { IconZoomIn, IconZoomOut, IconInspect, IconComponent, IconAnimate } from '../icons/Icons';
import DesignWhispers from '../panels/DesignWhispers';

// ─── Demo Scene ─────────────────────────────────────────────────────────────
function DemoScene() {
    const selectNode = useEditorStore((s) => s.selectNode);
    const setHov = useEditorStore((s) => s.setHoveredNode);
    const handler = (id: NodeId) => (e: React.MouseEvent) => {
        e.stopPropagation();
        selectNode(id);
    };
    const hov = (id: NodeId) => ({
        onMouseEnter: () => setHov(id),
        onMouseLeave: () => setHov(null),
    });

    return (
        <div className="ob-demo-scene" data-ob-node="root" data-ob-source="src/App.tsx">
            {/* Nav */}
            <nav className="ob-demo-nav" data-ob-node="nav" onClick={handler('nav')} {...hov('nav')}>
                <span className="ob-demo-nav-brand" data-ob-node="nav_brand" onClick={handler('nav_brand')} {...hov('nav_brand')}>Nexus</span>
                <div className="ob-demo-nav-links" data-ob-node="nav_links" onClick={handler('nav_links')} {...hov('nav_links')}>
                    <span className="ob-demo-nav-link" data-ob-node="link1" onClick={handler('link1')} {...hov('link1')}>Features</span>
                    <span className="ob-demo-nav-link" data-ob-node="link2" onClick={handler('link2')} {...hov('link2')}>Pricing</span>
                    <span className="ob-demo-nav-link" data-ob-node="link3" onClick={handler('link3')} {...hov('link3')}>Docs</span>
                </div>
            </nav>

            {/* Hero */}
            <section className="ob-demo-hero" data-ob-node="hero" onClick={handler('hero')} {...hov('hero')}>
                <span className="ob-demo-hero-badge" data-ob-node="hero_badge" onClick={handler('hero_badge')} {...hov('hero_badge')}>
                    ✦ Now in Public Beta
                </span>
                <h1 data-ob-node="hero_h1" onClick={handler('hero_h1')} {...hov('hero_h1')}>
                    Build interfaces that <span>think in code</span>
                </h1>
                <p data-ob-node="hero_p" onClick={handler('hero_p')} {...hov('hero_p')}>
                    The first visual editor that compiles design intent into production-grade source mutations. No more CSS archaeology.
                </p>
                <div className="ob-demo-hero-actions" data-ob-node="hero_actions" onClick={handler('hero_actions')} {...hov('hero_actions')}>
                    <button className="ob-demo-btn-primary" data-ob-node="btn_primary" onClick={handler('btn_primary')} {...hov('btn_primary')}>
                        Get Started →
                    </button>
                    <button className="ob-demo-btn-secondary" data-ob-node="btn_secondary" onClick={handler('btn_secondary')} {...hov('btn_secondary')}>
                        Watch Demo
                    </button>
                </div>
            </section>

            {/* Features */}
            <section className="ob-demo-features" data-ob-node="features" onClick={handler('features')} {...hov('features')}>
                <div className="ob-demo-card" data-ob-node="card1" onClick={handler('card1')} {...hov('card1')}>
                    <div className="ob-demo-card-icon" style={{ background: 'hsla(215,92%,62%,0.12)', color: 'var(--ob-accent)' }}><IconInspect size={24} /></div>
                    <h3>Intent Compiler</h3>
                    <p>Drag an element and get semantically ranked code mutations, not raw CSS offsets.</p>
                </div>
                <div className="ob-demo-card" data-ob-node="card2" onClick={handler('card2')} {...hov('card2')}>
                    <div className="ob-demo-card-icon" style={{ background: 'hsla(265,72%,62%,0.12)', color: 'var(--ob-purple)' }}><IconComponent size={24} /></div>
                    <h3>Source Binding</h3>
                    <p>Every node mapped to its canonical source with confidence scoring and ownership tracing.</p>
                </div>
                <div className="ob-demo-card" data-ob-node="card3" onClick={handler('card3')} {...hov('card3')}>
                    <div className="ob-demo-card-icon" style={{ background: 'hsla(152,62%,52%,0.12)', color: 'var(--ob-success)' }}><IconAnimate size={24} /></div>
                    <h3>Motion Authoring</h3>
                    <p>Timeline-based animation that compiles to your project's motion framework.</p>
                </div>
            </section>
        </div>
    );
}

// ─── Selection Overlay ──────────────────────────────────────────────────────
function SelectionOverlay() {
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const hoveredId = useEditorStore((s) => s.hoveredNodeId);
    const nodes = useEditorStore((s) => s.nodes);
    const sourceAnchors = useEditorStore((s) => s.sourceAnchors);

    return (
        <div className="ob-overlay">
            {/* Hover highlight */}
            {hoveredId && !selectedIds.includes(hoveredId) && nodes[hoveredId] && (() => {
                const n = nodes[hoveredId];
                return (
                    <div className="ob-hover-highlight" style={{
                        left: n.bounds.x, top: n.bounds.y,
                        width: n.bounds.w, height: n.bounds.h,
                    }} />
                );
            })()}

            {/* Selection boxes with handles */}
            {selectedIds.map((id) => {
                const n = nodes[id];
                if (!n) return null;
                const anchor = sourceAnchors[n.sourceAnchorIds[0]];
                const conf = anchor?.confidence ?? 0;
                const confColor = conf > 0.9 ? 'var(--ob-conf-high)' : conf > 0.7 ? 'var(--ob-conf-medium)' : conf > 0.5 ? 'var(--ob-conf-low)' : 'var(--ob-conf-none)';
                const fileName = anchor?.filePath?.split('/').pop() ?? '';

                return (
                    <div key={id}>
                        <div className="ob-selection-box" style={{
                            left: n.bounds.x, top: n.bounds.y,
                            width: n.bounds.w, height: n.bounds.h,
                        }}>
                            {/* 8 resize handles */}
                            {['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'].map((pos) => (
                                <div key={pos} className={`ob-handle ${pos}`} />
                            ))}

                            {/* Source badge */}
                            <div className="ob-source-badge">
                                <span className="ob-source-badge-dot" style={{ backgroundColor: confColor }} />
                                <span>{n.componentName || n.tag}</span>
                                <span style={{ opacity: 0.4 }}>— {fileName}</span>
                            </div>
                        </div>

                        {/* Dimension label */}
                        <div style={{
                            position: 'absolute',
                            left: n.bounds.x + n.bounds.w / 2,
                            top: n.bounds.y + n.bounds.h + 6,
                            transform: 'translateX(-50%)',
                            fontSize: '9px',
                            fontFamily: 'var(--ob-font-mono)',
                            color: 'var(--ob-accent)',
                            background: 'var(--ob-bg-elevated)',
                            padding: '1px 6px',
                            borderRadius: '3px',
                            border: '1px solid var(--ob-border)',
                            pointerEvents: 'none' as const,
                            whiteSpace: 'nowrap' as const,
                            zIndex: 55,
                        }}>
                            {n.bounds.w} × {n.bounds.h}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

// ─── Spacing Guides ─────────────────────────────────────────────────────────
function SpacingGuides() {
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const nodes = useEditorStore((s) => s.nodes);
    const toolMode = useEditorStore((s) => s.toolMode);

    if (toolMode !== 'select' || selectedIds.length !== 1) return null;
    const selId = selectedIds[0];
    const node = nodes[selId];
    if (!node || !node.parentId) return null;
    const parent = nodes[node.parentId];
    if (!parent) return null;

    const b = node.bounds;
    const p = parent.bounds;

    // Distances from node to parent bounds
    const top = b.y - p.y;
    const right = (p.x + p.w) - (b.x + b.w);
    const bottom = (p.y + p.h) - (b.y + b.h);
    const left = b.x - p.x;

    const guideStyle = (axis: 'h' | 'v', x1: number, y1: number, length: number, distance: number) => {
        if (distance <= 0) return null;
        const midX = axis === 'h' ? x1 + length / 2 : x1;
        const midY = axis === 'v' ? y1 + length / 2 : y1;
        return (
            <g key={`${axis}-${x1}-${y1}`}>
                {axis === 'h' ? (
                    <line x1={x1} y1={y1} x2={x1 + length} y2={y1}
                        stroke="var(--ob-spacing-guide, #f59e0b)" strokeWidth="1" strokeDasharray="3 2" opacity="0.7" />
                ) : (
                    <line x1={x1} y1={y1} x2={x1} y2={y1 + length}
                        stroke="var(--ob-spacing-guide, #f59e0b)" strokeWidth="1" strokeDasharray="3 2" opacity="0.7" />
                )}
                <rect x={midX - 12} y={midY - 7} width={24} height={14} rx="3"
                    fill="rgba(245,158,11,0.15)" stroke="rgba(245,158,11,0.3)" strokeWidth="0.5" />
                <text x={midX} y={midY + 3} textAnchor="middle"
                    fill="var(--ob-spacing-guide, #f59e0b)" fontSize="8"
                    fontFamily="var(--ob-font-mono)" fontWeight="600">
                    {Math.round(distance)}
                </text>
            </g>
        );
    };

    return (
        <svg className="ob-spacing-guides" style={{
            position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 54,
            width: '100%', height: '100%', overflow: 'visible',
        }}>
            {/* Top distance */}
            {guideStyle('v', b.x + b.w / 2, p.y, top, top)}
            {/* Bottom distance */}
            {guideStyle('v', b.x + b.w / 2, b.y + b.h, bottom, bottom)}
            {/* Left distance */}
            {guideStyle('h', p.x, b.y + b.h / 2, left, left)}
            {/* Right distance */}
            {guideStyle('h', b.x + b.w, b.y + b.h / 2, right, right)}
        </svg>
    );
}

// ─── Canvas ─────────────────────────────────────────────────────────────────
export default function Canvas() {
    const { zoom, panX, panY, setZoom, setPan, selectNode } = useEditorStore();
    const isPanning = useRef(false);
    const panStart = useRef({ x: 0, y: 0 });
    const panOrigin = useRef({ x: 0, y: 0 });

    const handleWheel = useCallback((e: React.WheelEvent) => {
        if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.05 : 0.05;
            setZoom(zoom + delta);
        } else {
            setPan(panX - e.deltaX * 0.5, panY - e.deltaY * 0.5);
        }
    }, [zoom, panX, panY, setZoom, setPan]);

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            e.preventDefault();
            isPanning.current = true;
            panStart.current = { x: e.clientX, y: e.clientY };
            panOrigin.current = { x: panX, y: panY };
        }
    }, [panX, panY]);

    useEffect(() => {
        const handleMove = (e: MouseEvent) => {
            if (!isPanning.current) return;
            const dx = e.clientX - panStart.current.x;
            const dy = e.clientY - panStart.current.y;
            setPan(panOrigin.current.x + dx, panOrigin.current.y + dy);
        };
        const handleUp = () => { isPanning.current = false; };
        window.addEventListener('mousemove', handleMove);
        window.addEventListener('mouseup', handleUp);
        return () => {
            window.removeEventListener('mousemove', handleMove);
            window.removeEventListener('mouseup', handleUp);
        };
    }, [setPan]);

    return (
        <div
            className="ob-canvas-area"
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onClick={(e) => { if (e.target === e.currentTarget) selectNode(null); }}
        >
            <div
                className="ob-canvas-transform"
                style={{ transform: `translate(${panX}px, ${panY}px) scale(${zoom})` }}
            >
                <div className="ob-canvas-content" style={{ position: 'relative' }}>
                    <DemoScene />
                    <SelectionOverlay />
                    <SpacingGuides />
                </div>
            </div>

            {/* Design Whispers floating bar */}
            <DesignWhispers />

            {/* Zoom controls floating */}
            <div style={{
                position: 'absolute', bottom: 12, right: 12,
                display: 'flex', gap: '4px', zIndex: 60,
            }}>
                <button
                    onClick={() => setZoom(zoom - 0.1)}
                    style={{
                        width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'var(--ob-glass-bg)', backdropFilter: 'blur(12px)',
                        border: '1px solid var(--ob-glass-border)', borderRadius: 'var(--ob-radius-sm)',
                        color: 'var(--ob-text-secondary)', cursor: 'pointer',
                    }}
                ><IconZoomOut size={14} /></button>
                <button
                    onClick={() => setZoom(1)}
                    style={{
                        height: 28, padding: '0 8px', display: 'flex', alignItems: 'center',
                        background: 'var(--ob-glass-bg)', backdropFilter: 'blur(12px)',
                        border: '1px solid var(--ob-glass-border)', borderRadius: 'var(--ob-radius-sm)',
                        color: 'var(--ob-text-tertiary)', cursor: 'pointer',
                        fontSize: '10px', fontFamily: 'var(--ob-font-mono)',
                    }}
                >{Math.round(zoom * 100)}%</button>
                <button
                    onClick={() => setZoom(zoom + 0.1)}
                    style={{
                        width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'var(--ob-glass-bg)', backdropFilter: 'blur(12px)',
                        border: '1px solid var(--ob-glass-border)', borderRadius: 'var(--ob-radius-sm)',
                        color: 'var(--ob-text-secondary)', cursor: 'pointer',
                    }}
                ><IconZoomIn size={14} /></button>
            </div>
        </div>
    );
}
