// ─── useAIMOS Hook ───
// Central hook connecting JOC to the live AIM-OS MCP server
// Polls real data from CMC, CAS, VIF, TCS, and AI collaboration systems

import { useState, useEffect, useCallback, useRef } from 'react';
import {
    mcp,
    checkHealth,
    getConnectionState,
    getLastLatency,
    onConnectionChange,
    type ConnectionState,
    type MemoryStats,
    type TimelineEntry,
    type ConsciousnessMetrics,
    type AIMessage,
    type Goal,
    type ProblemSummary,
} from '../services/mcpClient';

export interface AIMOSState {
    // Connection
    connected: boolean;
    health: ConnectionState;
    latency: number;

    // System data
    memory: MemoryStats | null;
    timeline: TimelineEntry[];
    consciousness: ConsciousnessMetrics | null;
    aiMessages: AIMessage[];
    goals: Goal[];
    problems: ProblemSummary | null;
    collaboration: Record<string, unknown> | null;

    // Meta
    lastRefresh: number;
    isRefreshing: boolean;
    error: string | null;

    // Actions
    refresh: () => Promise<void>;
    refreshMemory: () => Promise<void>;
    refreshTimeline: () => Promise<void>;
    refreshMessages: () => Promise<void>;
    refreshAll: () => Promise<void>;
}

const DEFAULT_POLL_INTERVAL = 12000; // 12 seconds
const FAST_POLL_INTERVAL = 5000;     // 5 seconds for messages

export function useAIMOS(options?: {
    pollInterval?: number;
    enablePolling?: boolean;
    pollDomains?: ('memory' | 'timeline' | 'consciousness' | 'messages' | 'goals' | 'problems')[];
}): AIMOSState {
    const {
        pollInterval = DEFAULT_POLL_INTERVAL,
        enablePolling = true,
        pollDomains = ['memory', 'timeline', 'consciousness', 'messages', 'goals', 'problems'],
    } = options || {};

    const [health, setHealth] = useState<ConnectionState>(getConnectionState());
    const [latency, setLatency] = useState(0);
    const [memory, setMemory] = useState<MemoryStats | null>(null);
    const [timeline, setTimeline] = useState<TimelineEntry[]>([]);
    const [consciousness, setConsciousness] = useState<ConsciousnessMetrics | null>(null);
    const [aiMessages, setAIMessages] = useState<AIMessage[]>([]);
    const [goals, setGoals] = useState<Goal[]>([]);
    const [problems, setProblems] = useState<ProblemSummary | null>(null);
    const [collaboration, setCollaboration] = useState<Record<string, unknown> | null>(null);
    const [lastRefresh, setLastRefresh] = useState(0);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const mountedRef = useRef(true);
    const pollCountRef = useRef(0);

    // Listen for connection state changes
    useEffect(() => {
        const unsub = onConnectionChange((state) => {
            if (mountedRef.current) {
                setHealth(state);
                setLatency(getLastLatency());
            }
        });
        return () => { mountedRef.current = false; unsub(); };
    }, []);

    // ─── Individual refresh functions ───

    const refreshMemory = useCallback(async () => {
        const result = await mcp.getMemoryStats();
        if (mountedRef.current && result) setMemory(result);
    }, []);

    const refreshTimeline = useCallback(async () => {
        const result = await mcp.getTimelineSummary(15);
        if (mountedRef.current && result?.entries) {
            setTimeline(result.entries);
        }
    }, []);

    const refreshConsciousness = useCallback(async () => {
        const result = await mcp.getConsciousnessMetrics();
        if (mountedRef.current && result) setConsciousness(result);
    }, []);

    const refreshMessages = useCallback(async () => {
        const result = await mcp.getAIMessages(30);
        if (mountedRef.current && result?.messages) {
            setAIMessages(result.messages);
        }
    }, []);

    const refreshGoals = useCallback(async () => {
        const result = await mcp.getGoals();
        if (mountedRef.current && result?.goals) {
            setGoals(result.goals);
        }
    }, []);

    const refreshProblems = useCallback(async () => {
        const result = await mcp.getProblemSummary();
        if (mountedRef.current && result) setProblems(result);
    }, []);

    const refreshCollaboration = useCallback(async () => {
        const result = await mcp.getCollaborationSummary();
        if (mountedRef.current && result) setCollaboration(result);
    }, []);

    // ─── Full refresh ───

    const refreshAll = useCallback(async () => {
        if (isRefreshing) return;
        setIsRefreshing(true);
        setError(null);

        try {
            // Check health first
            const healthy = await checkHealth();
            if (!healthy) {
                setError('MCP server offline');
                setIsRefreshing(false);
                return;
            }

            // Parallel fetch all domains
            const promises: Promise<void>[] = [];
            if (pollDomains.includes('memory')) promises.push(refreshMemory());
            if (pollDomains.includes('timeline')) promises.push(refreshTimeline());
            if (pollDomains.includes('consciousness')) promises.push(refreshConsciousness());
            if (pollDomains.includes('messages')) promises.push(refreshMessages());
            if (pollDomains.includes('goals')) promises.push(refreshGoals());
            if (pollDomains.includes('problems')) promises.push(refreshProblems());
            promises.push(refreshCollaboration());

            await Promise.allSettled(promises);
            if (mountedRef.current) {
                setLastRefresh(Date.now());
            }
        } catch (err) {
            if (mountedRef.current) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            }
        } finally {
            if (mountedRef.current) setIsRefreshing(false);
        }
    }, [isRefreshing, pollDomains, refreshMemory, refreshTimeline, refreshConsciousness, refreshMessages, refreshGoals, refreshProblems, refreshCollaboration]);

    // Single refresh (just the fast-changing data)
    const refresh = useCallback(async () => {
        await refreshAll();
    }, [refreshAll]);

    // ─── Initial fetch ───

    useEffect(() => {
        refreshAll();
    }, []); // eslint-disable-line react-hooks/exhaustive-deps

    // ─── Polling loop ───

    useEffect(() => {
        if (!enablePolling) return;

        const interval = setInterval(() => {
            pollCountRef.current++;

            // Every poll: fast-changing data (messages, timeline)
            if (pollDomains.includes('messages')) refreshMessages();
            if (pollDomains.includes('timeline')) refreshTimeline();

            // Every 3rd poll: medium-changing data (memory, problems)
            if (pollCountRef.current % 3 === 0) {
                if (pollDomains.includes('memory')) refreshMemory();
                if (pollDomains.includes('problems')) refreshProblems();
            }

            // Every 6th poll: slow-changing data (consciousness, goals, collaboration)
            if (pollCountRef.current % 6 === 0) {
                if (pollDomains.includes('consciousness')) refreshConsciousness();
                if (pollDomains.includes('goals')) refreshGoals();
                refreshCollaboration();
            }

            setLastRefresh(Date.now());
        }, pollInterval);

        return () => clearInterval(interval);
    }, [enablePolling, pollInterval, pollDomains, refreshMessages, refreshTimeline, refreshMemory, refreshProblems, refreshConsciousness, refreshGoals, refreshCollaboration]);

    return {
        connected: health === 'connected',
        health,
        latency,
        memory,
        timeline,
        consciousness,
        aiMessages,
        goals,
        problems,
        collaboration,
        lastRefresh,
        isRefreshing,
        error,
        refresh,
        refreshMemory,
        refreshTimeline,
        refreshMessages,
        refreshAll,
    };
}
