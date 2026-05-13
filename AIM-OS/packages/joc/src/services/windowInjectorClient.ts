import type {
    InjectorDispatchAccepted,
    InjectorDispatchRequest,
    InjectorExecutionRecord,
    InjectorHealth,
    InjectorTarget,
} from '../types/windowInjector';
import type { CaptureRequest, CapturedMessage } from '../types/windowCapture';

const WINDOW_INJECTOR_BASE = 'http://localhost:5013';

async function injectorRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${WINDOW_INJECTOR_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options?.headers || {}),
        },
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Window injector ${response.status}: ${text}`);
    }

    return response.json();
}

export async function checkInjectorHealth(): Promise<InjectorHealth> {
    return injectorRequest<InjectorHealth>('/health');
}

export async function listInjectorTargets(): Promise<InjectorTarget[]> {
    return injectorRequest<InjectorTarget[]>('/api/targets');
}

export async function dispatchInjectorCommand(
    request: InjectorDispatchRequest,
): Promise<InjectorDispatchAccepted> {
    return injectorRequest<InjectorDispatchAccepted>('/api/dispatch', {
        method: 'POST',
        body: JSON.stringify(request),
    });
}

export async function getInjectorExecution(
    executionId: string,
): Promise<InjectorExecutionRecord> {
    return injectorRequest<InjectorExecutionRecord>(`/api/executions/${executionId}`);
}

export async function probeInjectorTarget(targetId: string): Promise<unknown> {
    return injectorRequest(`/api/targets/${targetId}/probe`, {
        method: 'POST',
    });
}

export async function captureLastMessage(
    request: CaptureRequest,
): Promise<CapturedMessage> {
    return injectorRequest<CapturedMessage>('/api/capture/last-message', {
        method: 'POST',
        body: JSON.stringify(request),
    });
}
