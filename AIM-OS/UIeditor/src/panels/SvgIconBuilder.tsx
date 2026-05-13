/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — SVG Animated Icon Builder
   Create, edit, and animate custom SVG icons
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback } from 'react';
import {
    IconSvgBuilder, IconPenTool, IconBezier, IconShapeRect, IconShapeCircle,
    IconKeyframe, IconEasing, IconPalette, IconPlay, IconPause, IconPlus,
    IconDownload, IconSearch,
} from '../icons/Icons';

// ─── Types ──────────────────────────────────────────────────────────────────
interface SvgIconProject {
    id: string;
    name: string;
    viewBox: string;
    elements: SvgElement[];
    animations: SvgAnimation[];
    size: number;
}

interface SvgElement {
    id: string;
    type: 'path' | 'circle' | 'rect' | 'line' | 'ellipse' | 'polygon';
    attrs: Record<string, string>;
    selected?: boolean;
}

interface SvgAnimation {
    id: string;
    elementId: string;
    property: string;
    keyframes: { percent: number; value: string; easing: string }[];
    duration: number;
    repeat: 'once' | 'loop' | 'alternate';
}

// ─── Preset icons ───────────────────────────────────────────────────────────
const PRESET_ICONS: { name: string; elements: SvgElement[] }[] = [
    {
        name: 'Lightning',
        elements: [
            { id: 'p1', type: 'polygon', attrs: { points: '13,2 3,14 12,14 11,22 21,10 12,10', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', 'stroke-linejoin': 'round' } },
        ],
    },
    {
        name: 'Heart',
        elements: [
            { id: 'p1', type: 'path', attrs: { d: 'M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8' } },
        ],
    },
    {
        name: 'Gear',
        elements: [
            { id: 'c1', type: 'circle', attrs: { cx: '12', cy: '12', r: '3', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8' } },
            { id: 'p1', type: 'path', attrs: { d: 'M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5' } },
        ],
    },
    {
        name: 'Shield',
        elements: [
            { id: 'p1', type: 'path', attrs: { d: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', 'stroke-linejoin': 'round' } },
            { id: 'p2', type: 'path', attrs: { d: 'M9 12l2 2 4-4', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round' } },
        ],
    },
    {
        name: 'Sparkle',
        elements: [
            { id: 'p1', type: 'path', attrs: { d: 'M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5z', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.5', 'stroke-linejoin': 'round' } },
            { id: 'p2', type: 'path', attrs: { d: 'M19 17l.5 1.5L21 19l-1.5.5L19 21l-.5-1.5L17 19l1.5-.5z', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.2', 'stroke-linejoin': 'round' } },
        ],
    },
    {
        name: 'Pulse',
        elements: [
            { id: 'p1', type: 'path', attrs: { d: 'M3 12h4l3-9 4 18 3-9h4', fill: 'none', stroke: 'currentColor', 'stroke-width': '1.8', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' } },
        ],
    },
];

// ─── SVG Icon Builder Component ─────────────────────────────────────────────
export default function SvgIconBuilder() {
    const [activeTool, setActiveTool] = useState<'select' | 'pen' | 'bezier' | 'rect' | 'circle'>('select');
    const [projects, setProjects] = useState<SvgIconProject[]>(() => {
        return PRESET_ICONS.map((preset, i) => ({
            id: `preset-${i}`,
            name: preset.name,
            viewBox: '0 0 24 24',
            elements: preset.elements,
            animations: [],
            size: 24,
        }));
    });
    const [activeProjectId, setActiveProjectId] = useState(projects[0]?.id ?? '');
    const [isPlaying, setIsPlaying] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showAnimPanel, setShowAnimPanel] = useState(false);
    const [selectedElementId, setSelectedElementId] = useState<string | null>(null);

    const activeProject = projects.find((p) => p.id === activeProjectId);

    const addNewProject = useCallback(() => {
        const id = `icon-${Date.now()}`;
        const newProject: SvgIconProject = {
            id, name: `Icon ${projects.length + 1}`, viewBox: '0 0 24 24',
            elements: [], animations: [], size: 24,
        };
        setProjects((prev) => [...prev, newProject]);
        setActiveProjectId(id);
    }, [projects.length]);

    const addAnimation = useCallback(() => {
        if (!activeProject || !selectedElementId) return;
        const anim: SvgAnimation = {
            id: `anim-${Date.now()}`,
            elementId: selectedElementId,
            property: 'opacity',
            keyframes: [
                { percent: 0, value: '1', easing: 'ease-in-out' },
                { percent: 50, value: '0.3', easing: 'ease-in-out' },
                { percent: 100, value: '1', easing: 'ease-in-out' },
            ],
            duration: 1000,
            repeat: 'loop',
        };
        setProjects((prev) => prev.map((p) =>
            p.id === activeProjectId ? { ...p, animations: [...p.animations, anim] } : p
        ));
    }, [activeProject, activeProjectId, selectedElementId]);

    const filteredProjects = searchQuery
        ? projects.filter((p) => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
        : projects;

    const TOOLS = [
        { key: 'select' as const, Icon: IconSvgBuilder, label: 'Select' },
        { key: 'pen' as const, Icon: IconPenTool, label: 'Pen' },
        { key: 'bezier' as const, Icon: IconBezier, label: 'Bezier' },
        { key: 'rect' as const, Icon: IconShapeRect, label: 'Rectangle' },
        { key: 'circle' as const, Icon: IconShapeCircle, label: 'Circle' },
    ];

    return (
        <div className="ob-svg-builder">
            {/* Header */}
            <div className="ob-panel-header">
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <IconSvgBuilder size={12} />
                    Icon Builder
                </span>
                <button className="ob-svg-add-btn" onClick={addNewProject} title="New icon">
                    <IconPlus size={10} />
                </button>
            </div>

            {/* Search */}
            <div className="ob-tpl-search">
                <IconSearch size={12} style={{ opacity: 0.4, flexShrink: 0 }} />
                <input
                    className="ob-tpl-search-input"
                    placeholder="Search icons..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </div>

            {/* Icon grid */}
            <div className="ob-svg-grid">
                {filteredProjects.map((proj) => (
                    <div
                        key={proj.id}
                        className={`ob-svg-grid-item${proj.id === activeProjectId ? ' active' : ''}`}
                        onClick={() => setActiveProjectId(proj.id)}
                    >
                        <svg viewBox={proj.viewBox} width={32} height={32} fill="none" stroke="currentColor"
                            strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                            {proj.elements.map((el) => {
                                const Tag = el.type as keyof JSX.IntrinsicElements;
                                return <Tag key={el.id} {...(el.attrs as any)} />;
                            })}
                        </svg>
                        <span className="ob-svg-grid-name">{proj.name}</span>
                    </div>
                ))}
            </div>

            {/* Editor area */}
            {activeProject && (
                <div className="ob-svg-editor">
                    {/* Tool strip */}
                    <div className="ob-svg-tools">
                        {TOOLS.map(({ key, Icon, label }) => (
                            <button
                                key={key}
                                className={`ob-svg-tool-btn${activeTool === key ? ' active' : ''}`}
                                onClick={() => setActiveTool(key)}
                                title={label}
                            >
                                <Icon size={12} />
                            </button>
                        ))}
                        <div style={{ flex: 1 }} />
                        <button
                            className={`ob-svg-tool-btn${showAnimPanel ? ' active' : ''}`}
                            onClick={() => setShowAnimPanel(!showAnimPanel)}
                            title="Animation"
                        >
                            <IconKeyframe size={12} />
                        </button>
                        <button className="ob-svg-tool-btn" title="Colors">
                            <IconPalette size={12} />
                        </button>
                    </div>

                    {/* Canvas preview */}
                    <div className="ob-svg-canvas">
                        <div className="ob-svg-canvas-grid" />
                        <svg
                            viewBox={activeProject.viewBox}
                            className="ob-svg-canvas-svg"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="1.8"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            {activeProject.elements.map((el) => {
                                const Tag = el.type as keyof JSX.IntrinsicElements;
                                return (
                                    <Tag
                                        key={el.id}
                                        {...(el.attrs as any)}
                                        onClick={(e: React.MouseEvent) => {
                                            e.stopPropagation();
                                            setSelectedElementId(el.id);
                                        }}
                                        style={{
                                            cursor: 'pointer',
                                            ...(selectedElementId === el.id ? { filter: 'drop-shadow(0 0 3px var(--ob-accent))' } : {}),
                                        }}
                                    />
                                );
                            })}
                        </svg>
                        <div className="ob-svg-canvas-name">{activeProject.name}</div>
                        <div className="ob-svg-canvas-size">{activeProject.size}×{activeProject.size}</div>
                    </div>

                    {/* Element list */}
                    <div className="ob-svg-elements">
                        <div className="ob-svg-section-title">Elements ({activeProject.elements.length})</div>
                        {activeProject.elements.map((el) => (
                            <div
                                key={el.id}
                                className={`ob-svg-element-row${selectedElementId === el.id ? ' selected' : ''}`}
                                onClick={() => setSelectedElementId(el.id)}
                            >
                                <span className="ob-svg-element-type">{el.type}</span>
                                <span className="ob-svg-element-id">#{el.id}</span>
                            </div>
                        ))}
                    </div>

                    {/* Animation panel */}
                    {showAnimPanel && (
                        <div className="ob-svg-anim-panel">
                            <div className="ob-svg-section-title" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <IconKeyframe size={10} />
                                Animations ({activeProject.animations.length})
                                <div style={{ flex: 1 }} />
                                <button className="ob-svg-add-btn" onClick={addAnimation} title="Add animation"
                                    style={{ opacity: selectedElementId ? 1 : 0.3 }}>
                                    <IconPlus size={8} />
                                </button>
                            </div>

                            {activeProject.animations.length === 0 ? (
                                <div style={{ fontSize: '10px', color: 'var(--ob-text-tertiary)', padding: '8px 0' }}>
                                    Select an element and click + to add animation
                                </div>
                            ) : (
                                activeProject.animations.map((anim) => (
                                    <div key={anim.id} className="ob-svg-anim-track">
                                        <div className="ob-svg-anim-header">
                                            <span className="ob-svg-anim-prop">{anim.property}</span>
                                            <span className="ob-svg-anim-target">#{anim.elementId}</span>
                                            <span className="ob-svg-anim-dur">{anim.duration}ms</span>
                                            <span className="ob-svg-anim-repeat">{anim.repeat}</span>
                                        </div>
                                        <div className="ob-svg-anim-keyframes">
                                            {anim.keyframes.map((kf, i) => (
                                                <div key={i} className="ob-svg-anim-kf" style={{ left: `${kf.percent}%` }}>
                                                    <div className="ob-svg-anim-kf-diamond" />
                                                    <span className="ob-svg-anim-kf-label">{kf.value}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))
                            )}

                            {/* Playback controls */}
                            <div className="ob-svg-anim-controls">
                                <button
                                    className="ob-svg-play-btn"
                                    onClick={() => setIsPlaying(!isPlaying)}
                                >
                                    {isPlaying ? <IconPause size={10} /> : <IconPlay size={10} />}
                                </button>
                                <div className="ob-svg-anim-progress">
                                    <div className="ob-svg-anim-progress-fill" style={{ width: isPlaying ? '100%' : '0%' }} />
                                </div>
                                <span style={{ fontSize: '9px', color: 'var(--ob-text-tertiary)', fontFamily: 'var(--ob-font-mono)' }}>
                                    {isPlaying ? 'Playing...' : '0ms'}
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Export */}
                    <div className="ob-svg-export">
                        <button className="ob-svg-export-btn">
                            <IconDownload size={10} />
                            <span>Export SVG</span>
                        </button>
                        <button className="ob-svg-export-btn">
                            <IconEasing size={10} />
                            <span>Export Animated</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
