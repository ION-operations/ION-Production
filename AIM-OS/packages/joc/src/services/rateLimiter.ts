/**
 * Rate Limiter — Per-key usage budget enforcement
 *
 * Sliding window tracking with configurable limits per entry.
 * Supports: calls/hour, calls/day, cost/day, cost/month.
 * Fires alerts when approaching thresholds.
 */

import type { UsageLimit, UsageStats, VaultEntry } from './vaultService';

// ─── Types ───

export interface LimitCheckResult {
    allowed: boolean;
    reason?: string;
    remaining: {
        callsThisHour?: number;
        callsToday?: number;
        costToday?: number;
        costThisMonth?: number;
    };
    alerts: string[];
}

// ─── Core ───

const ONE_HOUR_MS = 3_600_000;
const ONE_DAY_MS = 86_400_000;

/**
 * Check if an entry is within its usage limits.
 */
export function checkLimit(entry: VaultEntry): LimitCheckResult {
    const { usageLimits: limits, usageStats: stats } = entry;
    const alerts: string[] = [];
    const threshold = limits.alertThreshold ?? 0.8;

    // Recompute sliding window stats
    const now = Date.now();
    const hourAgo = now - ONE_HOUR_MS;
    const dayStart = new Date().setHours(0, 0, 0, 0);

    const callsThisHour = stats.callTimestamps.filter(t => t > hourAgo).length;
    const callsToday = stats.callTimestamps.filter(t => t > dayStart).length;

    // Check calls/hour
    if (limits.maxCallsPerHour !== undefined && callsThisHour >= limits.maxCallsPerHour) {
        return {
            allowed: false,
            reason: `Hourly limit reached (${callsThisHour}/${limits.maxCallsPerHour})`,
            remaining: { callsThisHour: 0 },
            alerts,
        };
    }

    // Check calls/day
    if (limits.maxCallsPerDay !== undefined && callsToday >= limits.maxCallsPerDay) {
        return {
            allowed: false,
            reason: `Daily limit reached (${callsToday}/${limits.maxCallsPerDay})`,
            remaining: { callsToday: 0 },
            alerts,
        };
    }

    // Check cost/day
    if (limits.maxCostPerDay !== undefined && stats.costToday >= limits.maxCostPerDay) {
        return {
            allowed: false,
            reason: `Daily cost limit reached ($${stats.costToday.toFixed(2)}/$${limits.maxCostPerDay.toFixed(2)})`,
            remaining: { costToday: 0 },
            alerts,
        };
    }

    // Check cost/month
    if (limits.maxCostPerMonth !== undefined && stats.costThisMonth >= limits.maxCostPerMonth) {
        return {
            allowed: false,
            reason: `Monthly cost limit reached ($${stats.costThisMonth.toFixed(2)}/$${limits.maxCostPerMonth.toFixed(2)})`,
            remaining: { costThisMonth: 0 },
            alerts,
        };
    }

    // Check alert thresholds
    if (limits.maxCallsPerHour !== undefined) {
        const ratio = callsThisHour / limits.maxCallsPerHour;
        if (ratio >= threshold) alerts.push(`⚠️ ${Math.round(ratio * 100)}% of hourly call limit`);
    }
    if (limits.maxCallsPerDay !== undefined) {
        const ratio = callsToday / limits.maxCallsPerDay;
        if (ratio >= threshold) alerts.push(`⚠️ ${Math.round(ratio * 100)}% of daily call limit`);
    }
    if (limits.maxCostPerDay !== undefined && limits.maxCostPerDay > 0) {
        const ratio = stats.costToday / limits.maxCostPerDay;
        if (ratio >= threshold) alerts.push(`⚠️ ${Math.round(ratio * 100)}% of daily cost limit`);
    }
    if (limits.maxCostPerMonth !== undefined && limits.maxCostPerMonth > 0) {
        const ratio = stats.costThisMonth / limits.maxCostPerMonth;
        if (ratio >= threshold) alerts.push(`⚠️ ${Math.round(ratio * 100)}% of monthly cost limit`);
    }

    return {
        allowed: true,
        remaining: {
            callsThisHour: limits.maxCallsPerHour !== undefined ? limits.maxCallsPerHour - callsThisHour : undefined,
            callsToday: limits.maxCallsPerDay !== undefined ? limits.maxCallsPerDay - callsToday : undefined,
            costToday: limits.maxCostPerDay !== undefined ? limits.maxCostPerDay - stats.costToday : undefined,
            costThisMonth: limits.maxCostPerMonth !== undefined ? limits.maxCostPerMonth - stats.costThisMonth : undefined,
        },
        alerts,
    };
}

/**
 * Record a usage event for an entry.
 * Prunes old timestamps to keep the sliding window manageable.
 */
export function recordUsage(stats: UsageStats, cost: number = 0): UsageStats {
    const now = Date.now();
    const dayStart = new Date().setHours(0, 0, 0, 0);
    const hourAgo = now - ONE_HOUR_MS;

    // Prune timestamps older than 24 hours
    const prunedTimestamps = stats.callTimestamps.filter(t => t > dayStart - ONE_DAY_MS);
    prunedTimestamps.push(now);

    return {
        callsToday: prunedTimestamps.filter(t => t > dayStart).length,
        callsThisHour: prunedTimestamps.filter(t => t > hourAgo).length,
        costToday: stats.costToday + cost,
        costThisMonth: stats.costThisMonth + cost,
        lastUsed: new Date().toISOString(),
        callTimestamps: prunedTimestamps,
    };
}

/**
 * Reset daily stats (call at midnight or on demand).
 */
export function resetDailyStats(stats: UsageStats): UsageStats {
    return {
        ...stats,
        callsToday: 0,
        callsThisHour: 0,
        costToday: 0,
        callTimestamps: [],
    };
}

/**
 * Get usage percentage for display (0-100).
 */
export function getUsagePercent(entry: VaultEntry): number {
    const { usageLimits: limits, usageStats: stats } = entry;

    const ratios: number[] = [];
    if (limits.maxCallsPerDay && limits.maxCallsPerDay > 0) {
        ratios.push(stats.callsToday / limits.maxCallsPerDay);
    }
    if (limits.maxCostPerDay && limits.maxCostPerDay > 0) {
        ratios.push(stats.costToday / limits.maxCostPerDay);
    }
    if (limits.maxCallsPerHour && limits.maxCallsPerHour > 0) {
        ratios.push(stats.callsThisHour / limits.maxCallsPerHour);
    }

    if (ratios.length === 0) return 0;
    return Math.round(Math.max(...ratios) * 100);
}
