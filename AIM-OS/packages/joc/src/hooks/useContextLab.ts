import { useState, useEffect, useCallback, useRef } from 'react';
import { contextLab } from '../services/mcpClient';
import type { EvolutionScore, StrategyInfo, TournamentResult } from '../services/mcpClient';

// ─── Mock fallback data (used when MCP server is offline) ───

const MOCK_LEADERBOARD: EvolutionScore[] = [
    { variant: 'hhni_deep_v2', runs: 12, avg_quality: 0.782, avg_time_ms: 52, best: 0.91, worst: 0.62, generation: 2, parent: 'hhni_deep', base: 'hhni_direct', rank: 1 },
    { variant: 'hhni_direct', runs: 24, avg_quality: 0.723, avg_time_ms: 45, best: 0.85, worst: 0.58, generation: 0, parent: '', base: 'hhni_direct', rank: 2 },
    { variant: 'hybrid', runs: 18, avg_quality: 0.701, avg_time_ms: 380, best: 0.88, worst: 0.51, generation: 0, parent: '', base: 'hybrid', rank: 3 },
    { variant: 'pack_builder', runs: 20, avg_quality: 0.681, avg_time_ms: 320, best: 0.82, worst: 0.55, generation: 0, parent: '', base: 'pack_builder', rank: 4 },
    { variant: 'hhni_deep', runs: 8, avg_quality: 0.645, avg_time_ms: 68, best: 0.79, worst: 0.49, generation: 1, parent: 'hhni_direct', base: 'hhni_direct', rank: 5 },
    { variant: 'llm_research', runs: 6, avg_quality: 0.534, avg_time_ms: 4200, best: 0.72, worst: 0.38, generation: 0, parent: '', base: 'llm_research', rank: 6 },
];

const MOCK_STRATEGIES: StrategyInfo[] = [
    { name: 'hhni_direct', description: 'HHNI semantic retrieval + CMC atoms', class_name: 'HHNIDirectStrategy' },
    { name: 'pack_builder', description: '4-stage ContextPackBuilder pipeline', class_name: 'PackBuilderStrategy' },
    { name: 'hybrid', description: 'Multi-source fusion with deduplication', class_name: 'HybridStrategy' },
    { name: 'llm_research', description: 'LLM analyzes task via Gemini CLI', class_name: 'LLMResearchStrategy' },
];

interface TournamentHistoryEntry {
    id: string;
    timestamp: number;
    tasks: string[];
    variants: string[];
    winner: string;
    scoreCount: number;
}

const MOCK_HISTORY: TournamentHistoryEntry[] = [
    { id: 't_001', timestamp: Date.now() - 3600000, tasks: ['Audit registry', 'Review safety'], variants: ['hhni_direct', 'pack_builder', 'hybrid'], winner: 'hhni_direct', scoreCount: 6 },
    { id: 't_002', timestamp: Date.now() - 7200000, tasks: ['Analyze engine'], variants: ['hhni_deep_v2', 'hhni_direct', 'hybrid'], winner: 'hhni_deep_v2', scoreCount: 3 },
    { id: 't_003', timestamp: Date.now() - 86400000, tasks: ['Index workspace', 'Map dependencies'], variants: ['hhni_direct', 'llm_research'], winner: 'hhni_direct', scoreCount: 4 },
];

// ─── Hook ───

export interface ContextLabState {
    // Data
    leaderboard: EvolutionScore[];
    strategies: StrategyInfo[];
    history: TournamentHistoryEntry[];
    // Status
    loading: boolean;
    mcpConnected: boolean;
    lastError: string;
    lastResult: string;
    tournamentRunning: boolean;
    // Actions
    refresh: () => Promise<void>;
    forkVariant: (parent: string, child: string, mutations: Record<string, string>) => Promise<void>;
    runTournament: (task: string) => Promise<void>;
}

export function useContextLab(): ContextLabState {
    const [leaderboard, setLeaderboard] = useState<EvolutionScore[]>(MOCK_LEADERBOARD);
    const [strategies, setStrategies] = useState<StrategyInfo[]>(MOCK_STRATEGIES);
    const [history, setHistory] = useState<TournamentHistoryEntry[]>(MOCK_HISTORY);
    const [loading, setLoading] = useState(false);
    const [mcpConnected, setMcpConnected] = useState(false);
    const [lastError, setLastError] = useState('');
    const [lastResult, setLastResult] = useState('');
    const [tournamentRunning, setTournamentRunning] = useState(false);
    const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    // ─── Fetch leaderboard + strategies from MCP ───
    const refresh = useCallback(async () => {
        setLoading(true);
        setLastError('');
        try {
            // Parallel fetch
            const [lbResult, stratResult] = await Promise.all([
                contextLab.leaderboard(),
                contextLab.listStrategies(),
            ]);

            if (lbResult?.leaderboard) {
                setLeaderboard(lbResult.leaderboard);
                setMcpConnected(true);
            }
            if (stratResult?.strategies) {
                setStrategies(stratResult.strategies);
            }
        } catch (err) {
            setLastError(String(err));
            setMcpConnected(false);
            // Keep mock data as fallback — no state reset
        } finally {
            setLoading(false);
        }
    }, []);

    // ─── Fork ───
    const forkVariant = useCallback(async (parent: string, child: string, mutations: Record<string, string>) => {
        setLastResult('');
        setLastError('');
        try {
            const result = await contextLab.fork(parent, child, mutations);
            if (result?.variant) {
                setLastResult(`✅ Forked: ${parent} → ${child} (gen ${result.variant.generation})`);
                await refresh(); // Refresh leaderboard
            } else if (result?.text) {
                setLastResult(result.text);
            } else {
                setLastResult(`Forked: ${parent} → ${child} (MCP offline — simulated)`);
            }
        } catch (err) {
            setLastError(`Fork failed: ${String(err)}`);
        }
    }, [refresh]);

    // ─── Tournament ───
    const runTournament = useCallback(async (task: string) => {
        setTournamentRunning(true);
        setLastResult('');
        setLastError('');
        try {
            const result = await contextLab.tournament([task]);
            if (result?.result) {
                const r = result.result;
                setLastResult(`🏟️ Tournament complete: ${r.variants.length} variants × 1 task — Winner: ${r.winner}`);
                // Add to local history
                setHistory(prev => [{
                    id: r.tournament_id,
                    timestamp: r.timestamp || Date.now(),
                    tasks: r.tasks,
                    variants: r.variants,
                    winner: r.winner,
                    scoreCount: Object.keys(r.scores).length,
                }, ...prev]);
                await refresh(); // Refresh leaderboard
            } else if (result?.text) {
                setLastResult(result.text);
            } else {
                // Simulate for offline
                setLastResult(`🏟️ Tournament complete: ${strategies.length} strategies × 1 task (MCP offline — simulated)`);
            }
        } catch (err) {
            setLastError(`Tournament failed: ${String(err)}`);
        } finally {
            setTournamentRunning(false);
        }
    }, [refresh, strategies.length]);

    // ─── Auto-refresh on mount + polling ───
    useEffect(() => {
        refresh();
        intervalRef.current = setInterval(refresh, 30_000); // Poll every 30s
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [refresh]);

    return {
        leaderboard, strategies, history,
        loading, mcpConnected, lastError, lastResult, tournamentRunning,
        refresh, forkVariant, runTournament,
    };
}
