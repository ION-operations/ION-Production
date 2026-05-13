/**
 * Mission Orchestrator — Parallel multi-provider dispatch & response aggregation
 *
 * Orchestrates missions across multiple AI providers simultaneously:
 *  1. Parallel browser launch + navigation
 *  2. Parallel prompt injection
 *  3. Parallel response extraction (with per-provider timeouts)
 *  4. Response aggregation + synthesis data
 *
 * Usage:
 *   const result = await orchestrate(mission, providers, onProgress);
 */

import * as basClient from './basClient';
import type { SessionState, AIProvider } from '../store/sessionStore';

// ─── Types ───

export type ProviderTarget = {
    sessionId: string;
    provider: string;
    browserId?: string;
    url: string;
};

export type ProviderResult = {
    sessionId: string;
    provider: string;
    status: 'pending' | 'injecting' | 'waiting' | 'extracting' | 'complete' | 'error' | 'timeout';
    response?: string;
    tokens?: number;
    duration?: number;
    error?: string;
    startedAt?: number;
    completedAt?: number;
};

export type OrchestratorProgress = {
    phase: 'launching' | 'injecting' | 'waiting' | 'extracting' | 'complete';
    targets: ProviderResult[];
    completedCount: number;
    totalCount: number;
    percent: number;
};

export type OrchestrationResult = {
    missionId: string;
    prompt: string;
    results: ProviderResult[];
    bestResponse?: ProviderResult;
    totalDuration: number;
    allCompleted: boolean;
};

// ─── Config ───

const RESPONSE_WAIT_MS = 30_000;      // Max time to wait for AI response
const POLL_INTERVAL_MS = 2_000;        // How often to check for responses
const EXTRACTION_TIMEOUT_MS = 10_000;  // Max time for extraction

// ─── Orchestrator ───

/**
 * Orchestrate a mission across multiple providers in parallel.
 *
 * @param missionId Unique mission identifier
 * @param prompt The full prompt to inject
 * @param targets Array of provider targets (session IDs with active browsers)
 * @param onProgress Callback fired on each progress update
 * @returns Aggregated results from all providers
 */
export async function orchestrate(
    missionId: string,
    prompt: string,
    targets: ProviderTarget[],
    onProgress?: (progress: OrchestratorProgress) => void,
): Promise<OrchestrationResult> {
    const startTime = Date.now();

    // Initialize results
    const results: ProviderResult[] = targets.map(t => ({
        sessionId: t.sessionId,
        provider: t.provider,
        status: 'pending',
    }));

    const updateResult = (idx: number, update: Partial<ProviderResult>) => {
        results[idx] = { ...results[idx], ...update };
        const completedCount = results.filter(r => r.status === 'complete' || r.status === 'error' || r.status === 'timeout').length;
        onProgress?.({
            phase: completedCount === results.length ? 'complete' :
                results.some(r => r.status === 'extracting') ? 'extracting' :
                    results.some(r => r.status === 'waiting') ? 'waiting' :
                        results.some(r => r.status === 'injecting') ? 'injecting' : 'launching',
            targets: [...results],
            completedCount,
            totalCount: results.length,
            percent: Math.round((completedCount / results.length) * 100),
        });
    };

    // ─── Phase 1: Parallel Injection ───

    const injectionPromises = targets.map(async (target, idx) => {
        if (!target.browserId) {
            updateResult(idx, { status: 'error', error: 'No browser launched' });
            return;
        }

        updateResult(idx, { status: 'injecting', startedAt: Date.now() });

        try {
            // Start new chat to prevent context pollution
            try {
                await basClient.startNewChat(target.browserId, target.provider);
            } catch { /* use existing chat if new-chat fails */ }

            // Inject the prompt via sendPrompt
            await basClient.sendPrompt({ browserId: target.browserId, prompt, provider: target.provider });
            updateResult(idx, { status: 'waiting' });
        } catch (err: any) {
            updateResult(idx, { status: 'error', error: err?.message || 'Injection failed' });
        }
    });

    await Promise.allSettled(injectionPromises);

    // ─── Phase 2: Parallel Response Extraction with Timeout ───

    const extractionPromises = targets.map(async (target, idx) => {
        if (results[idx].status !== 'waiting') return; // Skip errored targets
        if (!target.browserId) return;

        const waitStart = Date.now();

        // Poll for response with timeout
        while (Date.now() - waitStart < RESPONSE_WAIT_MS) {
            await sleep(POLL_INTERVAL_MS);
            updateResult(idx, { status: 'extracting' });

            try {
                const response = await Promise.race([
                    basClient.extractResponse({ browserId: target.browserId!, provider: target.provider }),
                    sleep(EXTRACTION_TIMEOUT_MS).then(() => null),
                ]);

                if (response && response.response) {
                    const text = response.response;
                    if (text.length > 20) { // Meaningful response threshold
                        updateResult(idx, {
                            status: 'complete',
                            response: text,
                            tokens: Math.ceil(text.length / 4), // rough estimate
                            duration: Date.now() - (results[idx].startedAt || waitStart),
                            completedAt: Date.now(),
                        });
                        return;
                    }
                }

                // Not ready yet, keep waiting
                updateResult(idx, { status: 'waiting' });
            } catch {
                // Extraction failed, retry
            }
        }

        // Timeout
        updateResult(idx, {
            status: 'timeout',
            error: `No response after ${RESPONSE_WAIT_MS / 1000}s`,
            duration: Date.now() - (results[idx].startedAt || waitStart),
        });
    });

    await Promise.allSettled(extractionPromises);

    // ─── Phase 3: Aggregate Results ───

    const completedResults = results.filter(r => r.status === 'complete');

    // Pick best response by token count (longest meaningful response)
    const bestResponse = completedResults.length > 0
        ? completedResults.reduce((best, curr) =>
            (curr.tokens || 0) > (best.tokens || 0) ? curr : best
        )
        : undefined;

    const result: OrchestrationResult = {
        missionId,
        prompt,
        results,
        bestResponse,
        totalDuration: Date.now() - startTime,
        allCompleted: results.every(r => r.status === 'complete'),
    };

    onProgress?.({
        phase: 'complete',
        targets: [...results],
        completedCount: results.length,
        totalCount: results.length,
        percent: 100,
    });

    return result;
}

// ─── Quick Dispatch Helper ───

/**
 * Quick dispatch to a single provider (for the Dashboard Quick Dispatch panel).
 */
export async function quickDispatch(
    sessionId: string,
    browserId: string,
    provider: string,
    prompt: string,
): Promise<ProviderResult> {
    const target: ProviderTarget = { sessionId, provider, browserId, url: '' };
    const result = await orchestrate(`quick-${Date.now()}`, prompt, [target]);
    return result.results[0];
}

// ─── Build targets from sessionStore sessions ───

/**
 * Convert active sessions into orchestration targets.
 */
export function buildTargets(
    sessions: Record<string, SessionState>,
    targetIds: string[],
): ProviderTarget[] {
    const results: ProviderTarget[] = [];
    for (const id of targetIds) {
        const session = sessions[id];
        if (!session) continue;
        results.push({
            sessionId: id,
            provider: session.provider,
            browserId: session.browserId,
            url: session.url,
        });
    }
    return results;
}

// ─── Utility ───

function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}
