/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Editor Store (Zustand)
   Central state management with mock data for demo
   ═══════════════════════════════════════════════════════════════════════════ */
import { create } from 'zustand';
import type {
    NodeId, ToolMode, OperatingMode, Breakpoint, SimulatedState,
    VisualNode, SourceAnchor, LayoutContext, PropertyOwnership,
    MotionTrack, PatchCandidate, EditIntent, VerificationResult,
    AlignmentGuide, DragGesture, NodeConnection, DesignQualityScore, DesignWhisper,
} from '../types';

// ─── State Shape ────────────────────────────────────────────────────────────
export interface EditorState {
    // Canvas
    zoom: number;
    panX: number;
    panY: number;

    // Selection
    selectedNodeIds: NodeId[];
    hoveredNodeId: NodeId | null;

    // Tools
    toolMode: ToolMode;
    operatingMode: OperatingMode;
    breakpoint: Breakpoint;
    simulatedState: SimulatedState;

    // Panels
    leftPanelOpen: boolean;
    rightPanelOpen: boolean;
    bottomPanelOpen: boolean;
    rightPanelTab: 'visual' | 'layout' | 'style' | 'source';
    bottomPanelTab: 'timeline' | 'patches' | 'console' | 'quality';

    // Graph
    nodes: Record<NodeId, VisualNode>;
    sourceAnchors: Record<string, SourceAnchor>;
    layoutContexts: Record<string, LayoutContext>;
    propertyStacks: Record<NodeId, PropertyOwnership[]>;

    // Compiler
    activeIntents: EditIntent[];
    patchCandidates: PatchCandidate[];

    // Timeline
    motionTracks: MotionTrack[];
    playheadMs: number;
    isPlaying: boolean;
    timelineDuration: number;

    // Drag
    activeDrag: DragGesture | null;
    alignmentGuides: AlignmentGuide[];

    // Verification
    lastVerification: VerificationResult | null;

    // Expanded tree nodes
    expandedTreeNodes: Set<NodeId>;

    // Connected Editor Graph
    nodeConnections: NodeConnection[];

    // Design Quality
    designQuality: DesignQualityScore;

    // Design Whispers
    whispers: DesignWhisper[];

    // Actions
    setZoom: (z: number) => void;
    setPan: (x: number, y: number) => void;
    selectNode: (id: NodeId | null) => void;
    toggleNodeSelection: (id: NodeId) => void;
    setHoveredNode: (id: NodeId | null) => void;
    setToolMode: (m: ToolMode) => void;
    setBreakpoint: (b: Breakpoint) => void;
    setSimulatedState: (s: SimulatedState) => void;
    setOperatingMode: (m: OperatingMode) => void;
    toggleLeftPanel: () => void;
    toggleRightPanel: () => void;
    toggleBottomPanel: () => void;
    setRightPanelTab: (t: 'visual' | 'layout' | 'style' | 'source') => void;
    setPatchCandidates: (c: PatchCandidate[]) => void;
    acceptPatch: (id: string) => void;
    setPlayhead: (ms: number) => void;
    togglePlayback: () => void;
    setActiveDrag: (d: DragGesture | null) => void;
    setAlignmentGuides: (g: AlignmentGuide[]) => void;
    toggleTreeNode: (id: NodeId) => void;
    updateNodeBounds: (id: NodeId, bounds: { x: number; y: number; w: number; h: number }) => void;
    dismissWhisper: (id: string) => void;
    acceptWhisper: (id: string) => void;
    setBottomPanelTab: (t: 'timeline' | 'patches' | 'console' | 'quality') => void;
}

// ─── Mock Data ──────────────────────────────────────────────────────────────
function buildMockNodes(): Record<NodeId, VisualNode> {
    const n = (id: string, tag: string, label: string, comp: string | undefined,
        bounds: { x: number; y: number; w: number; h: number },
        children: string[], parentId?: string, depth = 0): VisualNode => ({
            id, tag, label, componentName: comp, bounds,
            computedStyle: {}, layoutContextId: undefined,
            sourceAnchorIds: [`sa_${id}`], children, parentId, depth,
            visible: true, locked: false,
        });

    return {
        'root': n('root', 'div', 'App', 'App', { x: 0, y: 0, w: 1200, h: 900 }, ['nav', 'hero', 'features'], undefined, 0),
        'nav': n('nav', 'nav', 'NavBar', 'NavBar', { x: 0, y: 0, w: 1200, h: 56 }, ['nav_brand', 'nav_links'], 'root', 1),
        'nav_brand': n('nav_brand', 'span', 'Brand', undefined, { x: 32, y: 16, w: 80, h: 24 }, [], 'nav', 2),
        'nav_links': n('nav_links', 'div', 'NavLinks', undefined, { x: 800, y: 16, w: 368, h: 24 }, ['link1', 'link2', 'link3'], 'nav', 2),
        'link1': n('link1', 'a', 'Features', undefined, { x: 800, y: 16, w: 60, h: 20 }, [], 'nav_links', 3),
        'link2': n('link2', 'a', 'Pricing', undefined, { x: 884, y: 16, w: 50, h: 20 }, [], 'nav_links', 3),
        'link3': n('link3', 'a', 'Docs', undefined, { x: 958, y: 16, w: 36, h: 20 }, [], 'nav_links', 3),
        'hero': n('hero', 'section', 'HeroSection', 'HeroSection', { x: 0, y: 56, w: 1200, h: 440 }, ['hero_badge', 'hero_h1', 'hero_p', 'hero_actions'], 'root', 1),
        'hero_badge': n('hero_badge', 'span', 'Badge', undefined, { x: 500, y: 136, w: 200, h: 24 }, [], 'hero', 2),
        'hero_h1': n('hero_h1', 'h1', 'Heading', undefined, { x: 250, y: 176, w: 700, h: 100 }, [], 'hero', 2),
        'hero_p': n('hero_p', 'p', 'Subtitle', undefined, { x: 340, y: 292, w: 520, h: 48 }, [], 'hero', 2),
        'hero_actions': n('hero_actions', 'div', 'Actions', undefined, { x: 440, y: 372, w: 320, h: 44 }, ['btn_primary', 'btn_secondary'], 'hero', 2),
        'btn_primary': n('btn_primary', 'button', 'Get Started', 'Button', { x: 440, y: 372, w: 150, h: 44 }, [], 'hero_actions', 3),
        'btn_secondary': n('btn_secondary', 'button', 'Learn More', 'Button', { x: 602, y: 372, w: 150, h: 44 }, [], 'hero_actions', 3),
        'features': n('features', 'section', 'Features', 'FeatureGrid', { x: 0, y: 496, w: 1200, h: 300 }, ['card1', 'card2', 'card3'], 'root', 1),
        'card1': n('card1', 'div', 'FeatureCard', 'Card', { x: 40, y: 496, w: 360, h: 200 }, [], 'features', 2),
        'card2': n('card2', 'div', 'FeatureCard', 'Card', { x: 420, y: 496, w: 360, h: 200 }, [], 'features', 2),
        'card3': n('card3', 'div', 'FeatureCard', 'Card', { x: 800, y: 496, w: 360, h: 200 }, [], 'features', 2),
    };
}

function buildMockAnchors(): Record<string, SourceAnchor> {
    const components: Record<string, { file: string; kind: 'component' | 'jsx-element' | 'prop'; conf: number }> = {
        root: { file: 'src/App.tsx', kind: 'component', conf: 0.98 },
        nav: { file: 'src/components/NavBar.tsx', kind: 'component', conf: 0.95 },
        nav_brand: { file: 'src/components/NavBar.tsx', kind: 'jsx-element', conf: 0.88 },
        nav_links: { file: 'src/components/NavBar.tsx', kind: 'jsx-element', conf: 0.85 },
        link1: { file: 'src/components/NavBar.tsx', kind: 'jsx-element', conf: 0.82 },
        link2: { file: 'src/components/NavBar.tsx', kind: 'jsx-element', conf: 0.82 },
        link3: { file: 'src/components/NavBar.tsx', kind: 'jsx-element', conf: 0.82 },
        hero: { file: 'src/components/HeroSection.tsx', kind: 'component', conf: 0.96 },
        hero_badge: { file: 'src/components/HeroSection.tsx', kind: 'jsx-element', conf: 0.91 },
        hero_h1: { file: 'src/components/HeroSection.tsx', kind: 'jsx-element', conf: 0.94 },
        hero_p: { file: 'src/components/HeroSection.tsx', kind: 'jsx-element', conf: 0.93 },
        hero_actions: { file: 'src/components/HeroSection.tsx', kind: 'jsx-element', conf: 0.90 },
        btn_primary: { file: 'src/components/Button.tsx', kind: 'component', conf: 0.97 },
        btn_secondary: { file: 'src/components/Button.tsx', kind: 'component', conf: 0.97 },
        features: { file: 'src/components/FeatureGrid.tsx', kind: 'component', conf: 0.94 },
        card1: { file: 'src/components/Card.tsx', kind: 'component', conf: 0.92 },
        card2: { file: 'src/components/Card.tsx', kind: 'component', conf: 0.92 },
        card3: { file: 'src/components/Card.tsx', kind: 'component', conf: 0.92 },
    };
    const out: Record<string, SourceAnchor> = {};
    for (const [id, c] of Object.entries(components)) {
        out[`sa_${id}`] = {
            id: `sa_${id}`, filePath: c.file, exportName: id,
            symbolName: id, astPath: ['Program', 'ExportDefault', id],
            ownershipKind: c.kind, confidence: c.conf,
        };
    }
    return out;
}

function buildMockLayouts(): Record<string, LayoutContext> {
    return {
        lc_root: {
            id: 'lc_root', mode: 'flex', axis: 'y', gap: 0, parentNodeId: undefined,
            padding: { top: 0, right: 0, bottom: 0, left: 0 }, align: 'stretch', justify: 'flex-start'
        },
        lc_nav: {
            id: 'lc_nav', mode: 'flex', axis: 'x', gap: 24, parentNodeId: 'root',
            padding: { top: 16, right: 32, bottom: 16, left: 32 }, align: 'center', justify: 'space-between'
        },
        lc_hero: {
            id: 'lc_hero', mode: 'flex', axis: 'y', gap: 16, parentNodeId: 'root',
            padding: { top: 80, right: 40, bottom: 60, left: 40 }, align: 'center', justify: 'center'
        },
        lc_hero_actions: {
            id: 'lc_hero_actions', mode: 'flex', axis: 'x', gap: 12, parentNodeId: 'hero',
            padding: { top: 0, right: 0, bottom: 0, left: 0 }, align: 'center', justify: 'center'
        },
        lc_features: {
            id: 'lc_features', mode: 'grid', parentNodeId: 'root', gap: 20,
            padding: { top: 0, right: 40, bottom: 60, left: 40 }, tracks: ['1fr', '1fr', '1fr']
        },
    };
}

function buildMockPropertyStacks(): Record<NodeId, PropertyOwnership[]> {
    return {
        btn_primary: [
            {
                property: 'background', computedValue: 'linear-gradient(135deg, #4a8af4, #5c6bc0)',
                sources: [
                    { kind: 'token', path: 'tokens.colors.primary.gradient', priority: 1, label: 'Primary Gradient' },
                    { kind: 'class', path: '.btn-primary', priority: 2, label: 'Button Class' },
                ]
            },
            {
                property: 'padding', computedValue: '10px 24px',
                sources: [
                    { kind: 'token', path: 'tokens.spacing.btn-md', priority: 1, label: 'Button MD Spacing' },
                    { kind: 'prop', path: 'size="md"', priority: 2, label: 'Size Prop' },
                ]
            },
            {
                property: 'border-radius', computedValue: '8px',
                sources: [
                    { kind: 'token', path: 'tokens.radii.md', priority: 1, label: 'Radius MD' },
                ]
            },
            {
                property: 'color', computedValue: '#ffffff',
                sources: [
                    { kind: 'inherited', path: '.btn-primary', priority: 1, label: 'Button Text' },
                ]
            },
            {
                property: 'font-size', computedValue: '14px',
                sources: [
                    { kind: 'token', path: 'tokens.typography.sm', priority: 1, label: 'Font SM' },
                    { kind: 'rule', path: 'globals.css:42', priority: 2, label: 'Global Rule' },
                ]
            },
            {
                property: 'box-shadow', computedValue: '0 4px 16px rgba(74,138,244,0.3)',
                sources: [
                    { kind: 'class', path: '.btn-glow', priority: 1, label: 'Glow Effect' },
                ]
            },
        ],
        hero_h1: [
            {
                property: 'font-size', computedValue: '48px',
                sources: [
                    { kind: 'token', path: 'tokens.typography.display', priority: 1, label: 'Display Size' },
                    { kind: 'class', path: '.hero-heading', priority: 2, label: 'Hero Heading' },
                ]
            },
            {
                property: 'font-weight', computedValue: '800',
                sources: [
                    { kind: 'rule', path: 'typography.css:18', priority: 1, label: 'Type Rule' },
                ]
            },
            {
                property: 'color', computedValue: '#e8ebf0',
                sources: [
                    { kind: 'token', path: 'tokens.colors.text.primary', priority: 1, label: 'Text Primary' },
                    { kind: 'inherited', path: 'body', priority: 2, label: 'Body Inherit' },
                ]
            },
        ],
        card1: [
            {
                property: 'background', computedValue: 'rgba(255,255,255,0.02)',
                sources: [
                    { kind: 'class', path: '.card', priority: 1, label: 'Card Class' },
                ]
            },
            {
                property: 'border', computedValue: '1px solid rgba(255,255,255,0.06)',
                sources: [
                    { kind: 'token', path: 'tokens.borders.subtle', priority: 1, label: 'Subtle Border' },
                ]
            },
            {
                property: 'border-radius', computedValue: '12px',
                sources: [
                    { kind: 'token', path: 'tokens.radii.lg', priority: 1, label: 'Radius LG' },
                ]
            },
            {
                property: 'padding', computedValue: '28px',
                sources: [
                    { kind: 'token', path: 'tokens.spacing.lg', priority: 1, label: 'Spacing LG' },
                    { kind: 'prop', path: 'padding="lg"', priority: 2, label: 'Padding Prop' },
                ]
            },
        ],
    };
}

function buildMockTracks(): MotionTrack[] {
    return [
        {
            id: 'track_hero_fade', nodeId: 'hero_h1', property: 'opacity', duration: 800,
            trigger: 'mount',
            keyframes: [
                { t: 0, value: 0, easing: 'cubic-bezier(0.16, 1, 0.3, 1)' },
                { t: 800, value: 1 },
            ],
        },
        {
            id: 'track_hero_slide', nodeId: 'hero_h1', property: 'y', duration: 800,
            trigger: 'mount',
            keyframes: [
                { t: 0, value: 20, easing: 'cubic-bezier(0.16, 1, 0.3, 1)' },
                { t: 800, value: 0 },
            ],
        },
        {
            id: 'track_badge_fade', nodeId: 'hero_badge', property: 'opacity', duration: 600,
            trigger: 'mount',
            keyframes: [
                { t: 0, value: 0, easing: 'ease-out' },
                { t: 200, value: 0 },
                { t: 600, value: 1 },
            ],
        },
        {
            id: 'track_btn_scale', nodeId: 'btn_primary', property: 'scale', duration: 200,
            trigger: 'hover',
            keyframes: [
                { t: 0, value: 1, easing: 'ease-out' },
                { t: 200, value: 1.03 },
            ],
        },
        {
            id: 'track_card1_enter', nodeId: 'card1', property: 'opacity', duration: 500,
            trigger: 'scroll',
            keyframes: [
                { t: 0, value: 0, easing: 'ease-out' },
                { t: 500, value: 1 },
            ],
        },
        {
            id: 'track_card1_slide', nodeId: 'card1', property: 'y', duration: 500,
            trigger: 'scroll',
            keyframes: [
                { t: 0, value: 30, easing: 'cubic-bezier(0.16, 1, 0.3, 1)' },
                { t: 500, value: 0 },
            ],
        },
    ];
}

function buildMockPatches(): PatchCandidate[] {
    return [
        {
            id: 'patch_1', intentId: 'intent_demo', strategy: 'adjust-parent-layout',
            score: 82,
            filePatches: [
                {
                    filePath: 'src/components/HeroSection.tsx', kind: 'ast',
                    before: 'gap: "16px"', after: 'gap: "24px"'
                },
            ],
            rationale: [
                'Target is in vertical flex context',
                'Gesture aligns with stack spacing semantics',
                'Parent gap 16px → 24px preserves layout integrity',
            ],
            risks: [],
        },
        {
            id: 'patch_2', intentId: 'intent_demo', strategy: 'adjust-token',
            score: 74,
            filePatches: [
                {
                    filePath: 'src/tokens.ts', kind: 'ast',
                    before: 'spacing: { stack: "16px" }', after: 'spacing: { stack: "24px" }'
                },
            ],
            rationale: [
                'Maps to existing spacing token',
                'Token change propagates to all consumers',
            ],
            risks: ['Affects 3 other components using this token'],
        },
        {
            id: 'patch_3', intentId: 'intent_demo', strategy: 'adjust-style-rule',
            score: 58,
            filePatches: [
                {
                    filePath: 'src/styles/hero.css', kind: 'text',
                    before: '.hero-section { gap: 16px; }', after: '.hero-section { gap: 24px; }'
                },
            ],
            rationale: [
                'Direct CSS rule modification',
                'Scoped to hero section only',
            ],
            risks: [],
        },
        {
            id: 'patch_4', intentId: 'intent_demo', strategy: 'apply-transform-fallback',
            score: 22,
            filePatches: [
                {
                    filePath: 'src/components/HeroSection.tsx', kind: 'ast',
                    before: '<p className="subtitle">', after: '<p className="subtitle" style={{ transform: "translateY(8px)" }}>'
                },
            ],
            rationale: [
                'Fallback: local transform offset',
                'Does not affect layout flow',
            ],
            risks: ['Non-semantic', 'Breaks responsive behavior', 'Not token-aware'],
        },
    ];
}

// ─── Store ──────────────────────────────────────────────────────────────────
export const useEditorStore = create<EditorState>((set) => ({
    // Canvas
    zoom: 0.85,
    panX: 80,
    panY: 40,

    // Selection
    selectedNodeIds: ['btn_primary'],
    hoveredNodeId: null,

    // Tools
    toolMode: 'select',
    operatingMode: 'source-owned',
    breakpoint: 'desktop',
    simulatedState: 'normal',

    // Panels
    leftPanelOpen: true,
    rightPanelOpen: true,
    bottomPanelOpen: true,
    rightPanelTab: 'visual',
    bottomPanelTab: 'timeline',

    // Graph
    nodes: buildMockNodes(),
    sourceAnchors: buildMockAnchors(),
    layoutContexts: buildMockLayouts(),
    propertyStacks: buildMockPropertyStacks(),

    // Compiler
    activeIntents: [],
    patchCandidates: buildMockPatches(),

    // Timeline
    motionTracks: buildMockTracks(),
    playheadMs: 340,
    isPlaying: false,
    timelineDuration: 1000,

    // Drag
    activeDrag: null,
    alignmentGuides: [],

    // Verification
    lastVerification: null,

    // Tree
    expandedTreeNodes: new Set(['root', 'nav', 'hero', 'hero_actions', 'features', 'nav_links']),

    // Connected Editor Graph
    nodeConnections: [
        { id: 'c1', type: 'drives', sourceId: 'root', targetId: 'nav', strength: 0.9, label: 'Layout' },
        { id: 'c2', type: 'drives', sourceId: 'root', targetId: 'hero', strength: 0.9, label: 'Layout' },
        { id: 'c3', type: 'drives', sourceId: 'root', targetId: 'features', strength: 0.85, label: 'Layout' },
        { id: 'c4', type: 'couples', sourceId: 'hero_h1', targetId: 'hero_p', strength: 0.8, label: 'Typography' },
        { id: 'c5', type: 'sequences', sourceId: 'hero_badge', targetId: 'hero_h1', strength: 0.7, label: 'Animation' },
        { id: 'c6', type: 'sequences', sourceId: 'hero_h1', targetId: 'btn_primary', strength: 0.65, label: 'Animation' },
        { id: 'c7', type: 'modulates', sourceId: 'nav', targetId: 'hero', strength: 0.5, label: 'Spacing' },
        { id: 'c8', type: 'blends', sourceId: 'btn_primary', targetId: 'btn_secondary', strength: 0.6, label: 'Style' },
        { id: 'c9', type: 'drives', sourceId: 'features', targetId: 'card1', strength: 0.85, label: 'Grid' },
        { id: 'c10', type: 'drives', sourceId: 'features', targetId: 'card2', strength: 0.85, label: 'Grid' },
        { id: 'c11', type: 'drives', sourceId: 'features', targetId: 'card3', strength: 0.85, label: 'Grid' },
    ],

    // Design Quality
    designQuality: {
        overall: 82,
        spacing: 90,
        contrast: 95,
        typeHierarchy: 88,
        responsiveFlow: 62,
        animationPerf: 75,
        issues: [
            { dimension: 'responsiveFlow', severity: 'warning', message: 'Hero section has no tablet breakpoint override', nodeId: 'hero' },
            { dimension: 'responsiveFlow', severity: 'info', message: 'Feature grid could use auto-fit for small screens', nodeId: 'features' },
            { dimension: 'animationPerf', severity: 'info', message: 'Consider will-change for animated heading', nodeId: 'hero_h1' },
            { dimension: 'spacing', severity: 'info', message: '3 different gap values used — consider a spacing token', nodeId: 'root' },
        ],
    },

    // Design Whispers
    whispers: [
        { id: 'w1', type: 'spacing-unify', message: 'You have 3 similar gap values (12px, 16px, 14px). Unify to a spacing token?', suggestion: '--spacing-md: 14px', dismissed: false, nodeIds: ['nav', 'hero', 'features'] },
        { id: 'w2', type: 'pattern-detected', message: 'Cards share identical border-radius and padding. Extract a Card material?', dismissed: false, nodeIds: ['card1', 'card2', 'card3'] },
        { id: 'w3', type: 'contrast-warning', message: 'Hero subtitle text has contrast ratio 3.8:1 — below AA standard (4.5:1)', suggestion: 'Use rgba(255,255,255,0.85) instead', dismissed: false, nodeIds: ['hero_p'] },
    ],

    // Actions
    setZoom: (z) => set({ zoom: Math.max(0.1, Math.min(3, z)) }),
    setPan: (x, y) => set({ panX: x, panY: y }),
    selectNode: (id) => set({ selectedNodeIds: id ? [id] : [] }),
    toggleNodeSelection: (id) => set((s) => ({
        selectedNodeIds: s.selectedNodeIds.includes(id)
            ? s.selectedNodeIds.filter((n) => n !== id)
            : [...s.selectedNodeIds, id],
    })),
    setHoveredNode: (id) => set({ hoveredNodeId: id }),
    setToolMode: (m) => set({ toolMode: m }),
    setBreakpoint: (b) => set({ breakpoint: b }),
    setSimulatedState: (s) => set({ simulatedState: s }),
    setOperatingMode: (m) => set({ operatingMode: m }),
    toggleLeftPanel: () => set((s) => ({ leftPanelOpen: !s.leftPanelOpen })),
    toggleRightPanel: () => set((s) => ({ rightPanelOpen: !s.rightPanelOpen })),
    toggleBottomPanel: () => set((s) => ({ bottomPanelOpen: !s.bottomPanelOpen })),
    setRightPanelTab: (t) => set({ rightPanelTab: t }),
    setBottomPanelTab: (t) => set({ bottomPanelTab: t }),
    setPatchCandidates: (c) => set({ patchCandidates: c }),
    acceptPatch: (id) => set((s) => ({
        patchCandidates: s.patchCandidates.filter((p) => p.id !== id),
        lastVerification: {
            buildOk: true, runtimeOk: true, targetResolved: true,
            visualSimilarity: 0.96, layoutWarnings: [], accessibilityWarnings: [],
            accepted: true,
        },
    })),
    setPlayhead: (ms) => set({ playheadMs: ms }),
    togglePlayback: () => set((s) => ({ isPlaying: !s.isPlaying })),
    setActiveDrag: (d) => set({ activeDrag: d }),
    setAlignmentGuides: (g) => set({ alignmentGuides: g }),
    toggleTreeNode: (id) => set((s) => {
        const next = new Set(s.expandedTreeNodes);
        if (next.has(id)) next.delete(id); else next.add(id);
        return { expandedTreeNodes: next };
    }),
    updateNodeBounds: (id, bounds) => set((s) => ({
        nodes: { ...s.nodes, [id]: { ...s.nodes[id], bounds } },
    })),
    dismissWhisper: (id) => set((s) => ({
        whispers: s.whispers.map((w) => w.id === id ? { ...w, dismissed: true } : w),
    })),
    acceptWhisper: (id) => set((s) => ({
        whispers: s.whispers.filter((w) => w.id !== id),
    })),
}));
