export type CaptureSourceKind = 'dom' | 'uia' | 'plaintext' | 'live';

export interface CaptureInlineSpan {
    type: 'text' | 'inline_code' | 'link' | 'citation' | 'status';
    text: string;
    href?: string | null;
    metadata?: Record<string, unknown>;
}

export interface CaptureBlock {
    id: string;
    type:
        | 'paragraph'
        | 'heading'
        | 'list'
        | 'code_block'
        | 'table'
        | 'tool_call'
        | 'tool_result'
        | 'status_line'
        | 'quote'
        | 'unknown_block';
    text?: string | null;
    spans: CaptureInlineSpan[];
    children: CaptureBlock[];
    items: CaptureInlineSpan[][];
    rows: string[][];
    language?: string | null;
    level?: number | null;
    ordered?: boolean | null;
    tool_name?: string | null;
    tool_status?: string | null;
    arguments?: unknown;
    collapsed?: boolean | null;
    metadata?: Record<string, unknown>;
}

export interface UiaTreeNode {
    name?: string | null;
    value?: string | null;
    control_type?: string | null;
    automation_id?: string | null;
    class_name?: string | null;
    is_enabled?: boolean | null;
    metadata?: Record<string, unknown>;
    children?: UiaTreeNode[];
}

export interface CaptureRequest {
    target_id: string;
    provider?: string | null;
    source_preference?: CaptureSourceKind[];
    html_snapshot?: string | null;
    uia_tree?: UiaTreeNode | UiaTreeNode[] | null;
    plain_text?: string | null;
    message_role?: string;
    include_collapsed_tool_content?: boolean;
    live_timeout_ms?: number;
    metadata?: Record<string, unknown>;
}

export interface CapturedMessage {
    target_id: string;
    message_id: string;
    captured_at: string;
    source: {
        adapter: string;
        kind: CaptureSourceKind;
        confidence: number;
        provider?: string | null;
    };
    verification: {
        stable: boolean;
        completeness_score: number;
        indicators: string[];
    };
    blocks: CaptureBlock[];
    plaintext: string;
    markdown: string;
    metadata: Record<string, unknown>;
}
