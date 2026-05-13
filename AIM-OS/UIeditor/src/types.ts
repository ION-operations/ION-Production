/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Canonical Type System
   The structural types that define the visual editor's internal truth layer.
   ═══════════════════════════════════════════════════════════════════════════ */

// ─── Primitive IDs ──────────────────────────────────────────────────────────
export type NodeId = string;
export type SourceId = string;
export type IntentId = string;
export type TrackId = string;

// ─── Tool Modes ─────────────────────────────────────────────────────────────
export type ToolMode =
    | 'select'
    | 'move'
    | 'resize'
    | 'constraint'
    | 'style'
    | 'animate'
    | 'inspect'
    | 'reparent';

// ─── Operating Modes ────────────────────────────────────────────────────────
export type OperatingMode = 'source-owned' | 'localhost-bridge' | 'recon';

// ─── Breakpoint Targets ─────────────────────────────────────────────────────
export type Breakpoint = 'desktop' | 'tablet' | 'mobile';

// ─── Simulated States ───────────────────────────────────────────────────────
export type SimulatedState =
    | 'normal'
    | 'hover'
    | 'focus'
    | 'pressed'
    | 'selected'
    | 'disabled'
    | 'loading'
    | 'empty'
    | 'error'
    | 'success';

// ─── Visual Node ────────────────────────────────────────────────────────────
export interface VisualNode {
    id: NodeId;
    tag: string;
    componentName?: string;
    label: string;
    bounds: { x: number; y: number; w: number; h: number };
    transform?: number[];
    computedStyle: Record<string, string>;
    layoutContextId?: string;
    sourceAnchorIds: SourceId[];
    children: NodeId[];
    parentId?: NodeId;
    depth: number;
    visible: boolean;
    locked: boolean;
}

// ─── Source Anchor ───────────────────────────────────────────────────────────
export type OwnershipKind =
    | 'jsx-element'
    | 'component'
    | 'prop'
    | 'style-rule'
    | 'token'
    | 'variant';

export interface SourceAnchor {
    id: SourceId;
    filePath: string;
    exportName?: string;
    symbolName?: string;
    astPath: string[];
    ownershipKind: OwnershipKind;
    confidence: number;
}

// ─── Binding Resolution ─────────────────────────────────────────────────────
export interface BindingResolution {
    nodeId: NodeId;
    anchors: SourceAnchor[];
    primaryAnchor?: SourceAnchor;
    confidence: number;
    reasons: string[];
}

// ─── Edit Intent ────────────────────────────────────────────────────────────
export type IntentType =
    | 'move'
    | 'resize'
    | 'restyle'
    | 'reparent'
    | 'reorder'
    | 'animate'
    | 'tokenize'
    | 'variantize';

export interface EditIntent {
    id: IntentId;
    type: IntentType;
    targetNodeId: NodeId;
    gesturePayload: unknown;
    semanticGoal?: string;
    timestamp: number;
}

// ─── Patch Candidate ────────────────────────────────────────────────────────
export type PatchStrategy =
    | 'adjust-parent-layout'
    | 'adjust-token'
    | 'adjust-prop'
    | 'adjust-style-rule'
    | 'insert-wrapper'
    | 'apply-transform-fallback'
    | 'reorder-children'
    | 'adjust-margin';

export interface PatchCandidate {
    id: string;
    intentId: IntentId;
    strategy: PatchStrategy;
    filePatches: FilePatch[];
    score: number;
    rationale: string[];
    risks: string[];
}

export interface FilePatch {
    filePath: string;
    kind: 'ast' | 'text';
    before?: string;
    after?: string;
}

// ─── Layout Context ─────────────────────────────────────────────────────────
export type LayoutMode = 'flow' | 'flex' | 'grid' | 'absolute' | 'stack';

export interface LayoutContext {
    id: string;
    mode: LayoutMode;
    parentNodeId?: NodeId;
    axis?: 'x' | 'y' | 'both';
    gap?: number;
    padding?: { top: number; right: number; bottom: number; left: number };
    align?: string;
    justify?: string;
    tracks?: string[];
    breakpoints?: Record<string, Partial<LayoutContext>>;
}

// ─── Property Ownership ─────────────────────────────────────────────────────
export type PropertySourceKind =
    | 'token'
    | 'class'
    | 'rule'
    | 'prop'
    | 'inline'
    | 'inherited';

export interface PropertyOwnership {
    property: string;
    computedValue: string;
    sources: Array<{
        kind: PropertySourceKind;
        path: string;
        priority: number;
        label: string;
    }>;
}

// ─── Motion & Timeline ──────────────────────────────────────────────────────
export type MotionProperty =
    | 'x'
    | 'y'
    | 'scale'
    | 'scaleX'
    | 'scaleY'
    | 'rotate'
    | 'opacity'
    | 'color'
    | 'filter'
    | 'width'
    | 'height';

export type MotionTrigger =
    | 'mount'
    | 'hover'
    | 'press'
    | 'scroll'
    | 'state-change'
    | 'timeline';

export interface Keyframe {
    t: number; // time in ms
    value: number | string;
    easing?: string;
}

export interface MotionTrack {
    id: TrackId;
    nodeId: NodeId;
    property: MotionProperty;
    keyframes: Keyframe[];
    trigger?: MotionTrigger;
    duration: number;
}

// ─── Token Suggestion ───────────────────────────────────────────────────────
export interface TokenSuggestion {
    kind: 'spacing' | 'color' | 'radius' | 'duration' | 'easing';
    value: string | number;
    occurrences: number;
    suggestedName: string;
}

// ─── Verification ───────────────────────────────────────────────────────────
export interface VerificationResult {
    buildOk: boolean;
    runtimeOk: boolean;
    targetResolved: boolean;
    visualSimilarity: number;
    layoutWarnings: string[];
    accessibilityWarnings: string[];
    accepted: boolean;
}

// ─── Interaction Transitions ────────────────────────────────────────────────
export interface InteractionTransition {
    from: string;
    to: string;
    trigger: string;
    guards?: string[];
    effects?: string[];
}

// ─── Compile Context (for strategies) ───────────────────────────────────────
export interface CompileContext {
    node: VisualNode;
    layout: LayoutContext;
    binding: BindingResolution;
    siblings: VisualNode[];
    parent?: VisualNode;
    tokens: Record<string, string | number>;
    propertyStack: PropertyOwnership[];
}

// ─── Intent Strategy Interface ──────────────────────────────────────────────
export interface IntentStrategy {
    id: string;
    name: string;
    supports(intent: EditIntent, ctx: CompileContext): boolean;
    propose(intent: EditIntent, ctx: CompileContext): Promise<PatchCandidate[]>;
}

// ─── Drag Gesture ───────────────────────────────────────────────────────────
export interface DragGesture {
    nodeId: NodeId;
    start: { x: number; y: number };
    current: { x: number; y: number };
    startBounds: { x: number; y: number; w: number; h: number };
}

// ─── Alignment Guide ───────────────────────────────────────────────────────
export interface AlignmentGuide {
    type: 'horizontal' | 'vertical';
    position: number;
    label?: string;
    sourceNodeId: NodeId;
}

// ─── Distance Indicator ─────────────────────────────────────────────────────
export interface DistanceIndicator {
    from: { x: number; y: number };
    to: { x: number; y: number };
    distance: number;
    axis: 'x' | 'y';
}

// ─── Node Connections (Connected Editor Graph) ──────────────────────────────
export type ConnectionType =
    | 'drives'      // container width drives child responsive
    | 'modulates'   // theme token modulates all using it
    | 'gates'       // @media query gates which rules are active
    | 'couples'     // typography and rhythm are bidirectionally coupled
    | 'sequences'   // entrance animations trigger in sequence
    | 'blends';     // multiple CSS layers blend to final value

export interface NodeConnection {
    id: string;
    type: ConnectionType;
    sourceId: NodeId;
    targetId: NodeId;
    strength: number; // 0-1
    label?: string;
}

// ─── Design Quality Scoring ─────────────────────────────────────────────────
export interface DesignQualityScore {
    overall: number; // 0-100
    spacing: number;
    contrast: number;
    typeHierarchy: number;
    responsiveFlow: number;
    animationPerf: number;
    issues: DesignIssue[];
}

export interface DesignIssue {
    dimension: 'spacing' | 'contrast' | 'typeHierarchy' | 'responsiveFlow' | 'animationPerf';
    severity: 'info' | 'warning' | 'error';
    message: string;
    nodeId?: NodeId;
}

// ─── Design Whispers ────────────────────────────────────────────────────────
export interface DesignWhisper {
    id: string;
    type: 'token-suggestion' | 'contrast-warning' | 'pattern-detected' | 'spacing-unify' | 'accessibility';
    message: string;
    suggestion?: string;
    dismissed: boolean;
    nodeIds?: NodeId[];
}
