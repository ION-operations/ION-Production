export interface InjectorHealth {
    status: string;
    service: string;
    version: string;
    queue_depth: number;
    adapters: Record<string, boolean>;
}

export interface InjectorTarget {
    id: string;
    display_name: string;
    preferred_adapters: string[];
    verification_policy: string[];
}

export interface InjectorDispatchRequest {
    target_id: string;
    command_text: string;
    preferred_adapter?: string | null;
    allow_repair?: boolean;
    wait_for_completion?: boolean;
    initiated_by: 'joc';
}

export interface InjectorDispatchAccepted {
    execution_id: string;
    state: 'queued' | 'running' | 'success' | 'failed' | 'timeout';
}

export interface InjectorExecutionRecord {
    execution_id: string;
    state: string;
    created_at: string;
    updated_at: string;
    request: InjectorDispatchRequest;
    result?: {
        target_id: string;
        state: string;
        adapter_used?: string;
        verification: {
            passed: boolean;
            manual_review_required: boolean;
            signals: { name: string; passed: boolean; detail?: string }[];
        };
        timings_ms: Record<string, number>;
        error?: string;
    };
}

