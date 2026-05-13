/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Edit-Intent Compiler
   Converts visual gestures into ranked, semantically meaningful code mutations
   ═══════════════════════════════════════════════════════════════════════════ */
import type {
    EditIntent, PatchCandidate, CompileContext, IntentStrategy,
} from '../types';

// ─── Scoring Engine ─────────────────────────────────────────────────────────
const STRATEGY_BASE_SCORES: Record<string, number> = {
    'adjust-prop': 30,
    'adjust-token': 26,
    'adjust-parent-layout': 24,
    'adjust-style-rule': 18,
    'reorder-children': 14,
    'adjust-margin': 12,
    'insert-wrapper': 8,
    'apply-transform-fallback': 3,
};

export function scoreCandidate(
    candidate: PatchCandidate,
    ctx: CompileContext,
): PatchCandidate {
    let score = STRATEGY_BASE_SCORES[candidate.strategy] ?? 0;

    // Binding confidence bonus (up to 20 points)
    score += Math.round(ctx.binding.confidence * 20);

    // Risk penalty
    score -= candidate.risks.length * 4;

    // Locality bonus: fewer files changed = better
    if (candidate.filePatches.length === 1) score += 5;

    // Token consistency: if strategy uses tokens and project has tokens
    if (candidate.strategy === 'adjust-token' && Object.keys(ctx.tokens).length > 0) {
        score += 6;
    }

    // AST patches preferred over text patches
    const astRatio = candidate.filePatches.filter((p) => p.kind === 'ast').length / (candidate.filePatches.length || 1);
    score += Math.round(astRatio * 8);

    return { ...candidate, score: Math.max(0, Math.min(100, score)) };
}

// ─── Core Compiler ──────────────────────────────────────────────────────────
export async function compileIntent(
    intent: EditIntent,
    ctx: CompileContext,
    strategies: IntentStrategy[],
): Promise<PatchCandidate[]> {
    const active = strategies.filter((s) => s.supports(intent, ctx));
    const proposals = await Promise.all(active.map((s) => s.propose(intent, ctx)));
    return proposals
        .flat()
        .map((candidate) => scoreCandidate(candidate, ctx))
        .sort((a, b) => b.score - a.score);
}

// ─── Built-in Strategies ────────────────────────────────────────────────────

export const flexGapMoveStrategy: IntentStrategy = {
    id: 'flex-gap-move',
    name: 'Adjust Flex Gap',
    supports(intent, ctx) {
        return intent.type === 'move' && ctx.layout.mode === 'flex';
    },
    async propose(intent, ctx) {
        const payload = intent.gesturePayload as { deltaX: number; deltaY: number };
        const delta = ctx.layout.axis === 'y' ? payload.deltaY : payload.deltaX;
        const nextGap = Math.max(0, (ctx.layout.gap ?? 0) + delta);
        const file = ctx.binding.primaryAnchor?.filePath ?? 'unknown';
        return [{
            id: crypto.randomUUID(), intentId: intent.id,
            strategy: 'adjust-parent-layout',
            filePatches: [{
                filePath: file, kind: 'ast',
                before: `gap: "${ctx.layout.gap ?? 0}px"`,
                after: `gap: "${nextGap}px"`,
            }],
            score: 0,
            rationale: [
                `Target in ${ctx.layout.axis === 'y' ? 'vertical' : 'horizontal'} flex context`,
                `Gesture aligns with stack spacing semantics`,
                `Parent gap ${ctx.layout.gap ?? 0}px → ${nextGap}px`,
            ],
            risks: [],
        }];
    },
};

export const gridPlacementStrategy: IntentStrategy = {
    id: 'grid-placement-move',
    name: 'Adjust Grid Placement',
    supports(intent, ctx) {
        return intent.type === 'move' && ctx.layout.mode === 'grid';
    },
    async propose(intent, ctx) {
        const file = ctx.binding.primaryAnchor?.filePath ?? 'unknown';
        return [{
            id: crypto.randomUUID(), intentId: intent.id,
            strategy: 'adjust-parent-layout',
            filePatches: [{ filePath: file, kind: 'ast' }],
            score: 0,
            rationale: [
                `Target in CSS Grid context`,
                `Adjusting grid column/row placement`,
            ],
            risks: [],
        }];
    },
};

export const marginAdjustStrategy: IntentStrategy = {
    id: 'margin-adjust',
    name: 'Adjust Margin',
    supports(intent, _ctx) {
        return intent.type === 'move';
    },
    async propose(intent, ctx) {
        const payload = intent.gesturePayload as { deltaX: number; deltaY: number };
        const file = ctx.binding.primaryAnchor?.filePath ?? 'unknown';
        return [{
            id: crypto.randomUUID(), intentId: intent.id,
            strategy: 'adjust-margin',
            filePatches: [{
                filePath: file, kind: 'ast',
                before: `margin: "0"`,
                after: `margin: "${payload.deltaY}px ${payload.deltaX}px"`,
            }],
            score: 0,
            rationale: ['Adds directional margin to element'],
            risks: ['Less semantic than parent layout adjustment'],
        }];
    },
};

export const transformFallbackStrategy: IntentStrategy = {
    id: 'transform-fallback',
    name: 'Transform Fallback',
    supports(intent, _ctx) {
        return intent.type === 'move' || intent.type === 'resize';
    },
    async propose(intent, ctx) {
        const payload = intent.gesturePayload as { deltaX: number; deltaY: number };
        const file = ctx.binding.primaryAnchor?.filePath ?? 'unknown';
        return [{
            id: crypto.randomUUID(), intentId: intent.id,
            strategy: 'apply-transform-fallback',
            filePatches: [{
                filePath: file, kind: 'ast',
                before: '',
                after: `style={{ transform: "translate(${payload.deltaX}px, ${payload.deltaY}px)" }}`,
            }],
            score: 0,
            rationale: ['Fallback: local transform offset', 'Does not affect layout flow'],
            risks: ['Non-semantic', 'Breaks responsive behavior', 'Not token-aware'],
        }];
    },
};

export const tokenResizeStrategy: IntentStrategy = {
    id: 'token-resize',
    name: 'Adjust Size Token',
    supports(intent, _ctx) {
        return intent.type === 'resize';
    },
    async propose(intent, ctx) {
        const file = ctx.binding.primaryAnchor?.filePath ?? 'unknown';
        return [{
            id: crypto.randomUUID(), intentId: intent.id,
            strategy: 'adjust-token',
            filePatches: [{ filePath: file, kind: 'ast' }],
            score: 0,
            rationale: ['Maps resize to size/spacing token when available'],
            risks: [],
        }];
    },
};

// ─── All Strategies ─────────────────────────────────────────────────────────
export const allStrategies: IntentStrategy[] = [
    flexGapMoveStrategy,
    gridPlacementStrategy,
    marginAdjustStrategy,
    transformFallbackStrategy,
    tokenResizeStrategy,
];
