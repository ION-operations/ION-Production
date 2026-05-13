/**
 * API Gateway — Proxy layer for vault-protected API calls
 *
 * AIs send requests referencing a vault entry ID.
 * The gateway decrypts the key, injects it into the request,
 * makes the call, and returns a sanitized response.
 * The AI never sees the raw credential.
 */

import { decryptValue, type VaultEntry } from './vaultService';
import { checkLimit, recordUsage } from './rateLimiter';

// ─── Types ───

export type AuthMethod = 'bearer' | 'query_param' | 'body_field' | 'basic_auth' | 'x-api-key' | 'custom_header';

export interface ProxyRequestOptions {
    url: string;
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    headers?: Record<string, string>;
    body?: string | object;
    authMethod?: AuthMethod;
    authParamName?: string;     // e.g., 'key' for ?key=..., or header name
    estimatedCost?: number;     // estimated cost per call in USD
}

export interface ProxyResponse {
    success: boolean;
    status?: number;
    data?: any;
    error?: string;
    usageRecorded: boolean;
    rateLimitInfo?: {
        allowed: boolean;
        remaining: Record<string, number | undefined>;
        alerts: string[];
    };
}

// ─── Proxy Request ───

/**
 * Make an API call using vault-stored credentials.
 *
 * @param entry The vault entry containing the encrypted credential
 * @param options Request configuration
 * @param onUsageUpdate Callback to persist updated usage stats
 * @returns Sanitized response (no credential leakage)
 */
export async function proxyRequest(
    entry: VaultEntry,
    options: ProxyRequestOptions,
    onUsageUpdate?: (entryId: string, stats: VaultEntry['usageStats']) => void,
): Promise<ProxyResponse> {
    // 1. Check rate limits BEFORE making the call
    const limitCheck = checkLimit(entry);
    if (!limitCheck.allowed) {
        return {
            success: false,
            error: `Rate limit: ${limitCheck.reason}`,
            usageRecorded: false,
            rateLimitInfo: {
                allowed: false,
                remaining: limitCheck.remaining,
                alerts: limitCheck.alerts,
            },
        };
    }

    // 2. Decrypt the credential
    const rawValue = await decryptValue(entry.encryptedValue);
    if (rawValue === '[DECRYPTION_UNAVAILABLE]' || rawValue === '[DECRYPTION_FAILED]') {
        return { success: false, error: 'Failed to decrypt credential', usageRecorded: false };
    }

    // 3. Build the request with the credential injected
    const fetchOptions: RequestInit = {
        method: options.method || 'GET',
        headers: { ...options.headers },
    };

    const authMethod = options.authMethod || 'bearer';
    let url = options.url;

    switch (authMethod) {
        case 'bearer':
            (fetchOptions.headers as Record<string, string>)['Authorization'] = `Bearer ${rawValue}`;
            break;
        case 'x-api-key':
            (fetchOptions.headers as Record<string, string>)['x-api-key'] = rawValue;
            break;
        case 'query_param': {
            const paramName = options.authParamName || 'key';
            const separator = url.includes('?') ? '&' : '?';
            url = `${url}${separator}${paramName}=${encodeURIComponent(rawValue)}`;
            break;
        }
        case 'basic_auth': {
            const encoded = btoa(rawValue); // expects "user:pass" format
            (fetchOptions.headers as Record<string, string>)['Authorization'] = `Basic ${encoded}`;
            break;
        }
        case 'body_field': {
            const fieldName = options.authParamName || 'api_key';
            const body = typeof options.body === 'object' ? options.body : {};
            fetchOptions.body = JSON.stringify({ ...body, [fieldName]: rawValue });
            (fetchOptions.headers as Record<string, string>)['Content-Type'] = 'application/json';
            break;
        }
        case 'custom_header': {
            const headerName = options.authParamName || 'X-Auth-Token';
            (fetchOptions.headers as Record<string, string>)[headerName] = rawValue;
            break;
        }
    }

    // Add body if not already set
    if (options.body && !fetchOptions.body) {
        fetchOptions.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
        if (typeof options.body === 'object') {
            (fetchOptions.headers as Record<string, string>)['Content-Type'] = 'application/json';
        }
    }

    // 4. Make the API call
    try {
        const response = await fetch(url, fetchOptions);
        const contentType = response.headers.get('content-type') || '';
        let data: any;

        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        // 5. Record usage
        const newStats = recordUsage(entry.usageStats, options.estimatedCost || 0);
        onUsageUpdate?.(entry.id, newStats);

        // 6. Sanitize response — strip any leaked credentials
        const sanitizedData = sanitizeResponse(data, rawValue);

        return {
            success: response.ok,
            status: response.status,
            data: sanitizedData,
            usageRecorded: true,
            rateLimitInfo: {
                allowed: true,
                remaining: limitCheck.remaining,
                alerts: limitCheck.alerts,
            },
        };
    } catch (err: any) {
        // Still record the attempt
        const newStats = recordUsage(entry.usageStats, 0);
        onUsageUpdate?.(entry.id, newStats);

        return {
            success: false,
            error: sanitizeErrorMessage(err.message, rawValue),
            usageRecorded: true,
        };
    }
}

// ─── Sanitization ───

/**
 * Remove any accidental credential leakage from response data.
 */
function sanitizeResponse(data: any, credential: string): any {
    if (typeof data === 'string') {
        return data.replace(new RegExp(escapeRegex(credential), 'g'), '[REDACTED]');
    }
    if (typeof data === 'object' && data !== null) {
        const sanitized = JSON.stringify(data).replace(
            new RegExp(escapeRegex(credential), 'g'),
            '[REDACTED]',
        );
        try { return JSON.parse(sanitized); } catch { return sanitized; }
    }
    return data;
}

function sanitizeErrorMessage(message: string, credential: string): string {
    return message.replace(new RegExp(escapeRegex(credential), 'g'), '[REDACTED]');
}

function escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
