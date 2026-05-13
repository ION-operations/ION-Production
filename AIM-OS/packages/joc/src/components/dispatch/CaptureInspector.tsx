import { useCallback, useEffect, useMemo, useState } from 'react';

import {
    captureLastMessage,
    checkInjectorHealth,
    listInjectorTargets,
} from '../../services/windowInjectorClient';
import type {
    CaptureBlock,
    CaptureRequest,
    CapturedMessage,
    CaptureSourceKind,
    UiaTreeNode,
} from '../../types/windowCapture';
import type { InjectorHealth, InjectorTarget } from '../../types/windowInjector';

const CAPTURE_SOURCE_OPTIONS: Array<{ value: CaptureSourceKind; label: string; helper: string }> = [
    { value: 'live', label: 'Live', helper: 'Attach to the target window and capture directly through CDP or UIA.' },
    { value: 'dom', label: 'DOM', helper: 'Parse an HTML snapshot into structured message blocks.' },
    { value: 'uia', label: 'UIA', helper: 'Parse a pasted UIA tree JSON payload into message blocks.' },
    { value: 'plaintext', label: 'Plaintext', helper: 'Use raw text as a last-resort fallback capture.' },
];

function normalizeError(error: unknown): string {
    if (error instanceof Error) {
        return error.message;
    }
    return 'Unknown capture error';
}

function payloadPlaceholder(sourceKind: CaptureSourceKind): string {
    switch (sourceKind) {
        case 'dom':
            return '<article data-message-author-role="assistant"><p>Captured HTML goes here.</p></article>';
        case 'uia':
            return JSON.stringify(
                {
                    name: 'Assistant message',
                    control_type: 'document',
                    children: [
                        {
                            name: 'Here is the fix.',
                            control_type: 'text',
                            children: [],
                        },
                    ],
                },
                null,
                2,
            );
        case 'plaintext':
            return 'Paste the captured assistant text here.';
        case 'live':
            return '';
    }
}

function parseUiaPayload(payload: string): UiaTreeNode | UiaTreeNode[] {
    const parsed: unknown = JSON.parse(payload);
    const isValidObject = typeof parsed === 'object' && parsed !== null;
    if (!isValidObject) {
        throw new Error('UIA payload must be a JSON object or array.');
    }
    return parsed as UiaTreeNode | UiaTreeNode[];
}

function summarizeBlock(block: CaptureBlock): string {
    const spanText = block.spans.map(span => span.text).join(' ').trim();
    const listText = block.items.flat().map(span => span.text).join(' ').trim();
    const rowText = block.rows.flat().join(' ').trim();
    const text = block.text?.trim() || spanText || listText || rowText;
    if (!text) {
        return '';
    }
    return text.length > 140 ? `${text.slice(0, 140)}...` : text;
}

function renderItems(block: CaptureBlock) {
    if (block.items.length === 0) {
        return null;
    }
    return (
        <div className="dispatch-capture-tree-items">
            {block.items.map((item, index) => (
                <div key={`${block.id}-item-${index}`} className="dispatch-capture-tree-item">
                    {item.map(span => span.text).join(' ')}
                </div>
            ))}
        </div>
    );
}

function CaptureBlockNode({ block, depth = 0 }: { block: CaptureBlock; depth?: number }) {
    const summary = summarizeBlock(block);

    return (
        <div className="dispatch-capture-tree-node" style={{ paddingLeft: `${depth * 14}px` }}>
            <div className="dispatch-capture-tree-line">
                <span className="dispatch-capture-tree-type">{block.type}</span>
                {block.language && <span className="dispatch-capture-tree-tag">{block.language}</span>}
                {block.tool_name && <span className="dispatch-capture-tree-tag">{block.tool_name}</span>}
                {block.tool_status && <span className="dispatch-capture-tree-tag">{block.tool_status}</span>}
                {block.ordered != null && (
                    <span className="dispatch-capture-tree-tag">{block.ordered ? 'ordered' : 'unordered'}</span>
                )}
            </div>
            {summary && <div className="dispatch-capture-tree-summary">{summary}</div>}
            {renderItems(block)}
            {block.children.map(child => (
                <CaptureBlockNode key={child.id} block={child} depth={depth + 1} />
            ))}
        </div>
    );
}

export function CaptureInspector() {
    const [runtimeHealth, setRuntimeHealth] = useState<InjectorHealth | null>(null);
    const [injectorTargets, setInjectorTargets] = useState<InjectorTarget[]>([]);
    const [selectedTargetId, setSelectedTargetId] = useState('');
    const [sourceKind, setSourceKind] = useState<CaptureSourceKind>('live');
    const [manualPayload, setManualPayload] = useState('');
    const [includeCollapsedToolContent, setIncludeCollapsedToolContent] = useState(false);
    const [liveTimeoutMs, setLiveTimeoutMs] = useState(5000);
    const [isLoadingRuntime, setIsLoadingRuntime] = useState(false);
    const [runtimeError, setRuntimeError] = useState<string | null>(null);
    const [isCapturing, setIsCapturing] = useState(false);
    const [captureError, setCaptureError] = useState<string | null>(null);
    const [capturedMessage, setCapturedMessage] = useState<CapturedMessage | null>(null);
    const [lastCaptureLabel, setLastCaptureLabel] = useState<string | null>(null);

    const loadRuntimeState = useCallback(async () => {
        setIsLoadingRuntime(true);
        setRuntimeError(null);

        try {
            const [health, targets] = await Promise.all([
                checkInjectorHealth(),
                listInjectorTargets(),
            ]);
            setRuntimeHealth(health);
            setInjectorTargets(targets);
            setSelectedTargetId(previousTargetId => {
                if (previousTargetId && targets.some(target => target.id === previousTargetId)) {
                    return previousTargetId;
                }
                return targets[0]?.id ?? '';
            });
        } catch (error) {
            setRuntimeHealth(null);
            setInjectorTargets([]);
            setRuntimeError(normalizeError(error));
        } finally {
            setIsLoadingRuntime(false);
        }
    }, []);

    useEffect(() => {
        void loadRuntimeState();
    }, [loadRuntimeState]);

    const selectedTarget = useMemo(
        () => injectorTargets.find(target => target.id === selectedTargetId) ?? null,
        [injectorTargets, selectedTargetId],
    );

    const selectedSourceOption = useMemo(
        () => CAPTURE_SOURCE_OPTIONS.find(option => option.value === sourceKind) ?? CAPTURE_SOURCE_OPTIONS[0],
        [sourceKind],
    );

    const rawJson = useMemo(
        () => (capturedMessage ? JSON.stringify(capturedMessage, null, 2) : ''),
        [capturedMessage],
    );

    const executeCapture = useCallback(async (request: CaptureRequest, label: string) => {
        setIsCapturing(true);
        setCaptureError(null);

        try {
            const result = await captureLastMessage(request);
            setCapturedMessage(result);
            setLastCaptureLabel(label);
        } catch (error) {
            setCapturedMessage(null);
            setCaptureError(normalizeError(error));
        } finally {
            setIsCapturing(false);
        }
    }, []);

    const handleCapture = useCallback(async () => {
        if (!selectedTargetId) {
            setCaptureError('Select an injector target first.');
            return;
        }

        const request: CaptureRequest = {
            target_id: selectedTargetId,
            source_preference: [sourceKind],
            include_collapsed_tool_content: includeCollapsedToolContent,
            live_timeout_ms: liveTimeoutMs,
            metadata: { initiated_by: 'joc.capture_inspector' },
        };

        if (sourceKind === 'dom') {
            if (!manualPayload.trim()) {
                setCaptureError('DOM mode requires an HTML snapshot.');
                return;
            }
            request.html_snapshot = manualPayload;
        }

        if (sourceKind === 'uia') {
            if (!manualPayload.trim()) {
                setCaptureError('UIA mode requires a JSON UIA tree payload.');
                return;
            }
            try {
                request.uia_tree = parseUiaPayload(manualPayload);
            } catch (error) {
                setCaptureError(normalizeError(error));
                return;
            }
        }

        if (sourceKind === 'plaintext') {
            if (!manualPayload.trim()) {
                setCaptureError('Plaintext mode requires a text payload.');
                return;
            }
            request.plain_text = manualPayload;
        }

        await executeCapture(request, `${selectedTargetId}:${sourceKind}`);
    }, [
        executeCapture,
        includeCollapsedToolContent,
        liveTimeoutMs,
        manualPayload,
        selectedTargetId,
        sourceKind,
    ]);

    const handleQuickLiveCapture = useCallback(async (targetId: string) => {
        setSelectedTargetId(targetId);
        setSourceKind('live');
        await executeCapture(
            {
                target_id: targetId,
                source_preference: ['live'],
                include_collapsed_tool_content: includeCollapsedToolContent,
                live_timeout_ms: liveTimeoutMs,
                metadata: { initiated_by: 'joc.capture_inspector.quick_live' },
            },
            `${targetId}:live`,
        );
    }, [executeCapture, includeCollapsedToolContent, liveTimeoutMs]);

    return (
        <section className="dispatch-capture-panel">
            <div className="dispatch-capture-panel-header">
                <div>
                    <label className="dispatch-section-label">Window Capture Inspector</label>
                    <div className="dispatch-capture-subtitle">
                        Structured last-message capture for browser and desktop AI surfaces.
                    </div>
                </div>
                <div className="dispatch-capture-runtime">
                    <span className={`dispatch-runtime-badge ${runtimeHealth ? 'online' : 'offline'}`}>
                        Runtime {runtimeHealth ? 'online' : 'offline'}
                    </span>
                    <button
                        className="dispatch-secondary-btn"
                        onClick={() => void handleQuickLiveCapture(selectedTargetId)}
                        disabled={isCapturing || !selectedTargetId}
                    >
                        Capture Active Target
                    </button>
                    <button
                        className="dispatch-secondary-btn"
                        onClick={() => void loadRuntimeState()}
                        disabled={isLoadingRuntime}
                    >
                        {isLoadingRuntime ? 'Refreshing...' : 'Refresh Runtime'}
                    </button>
                </div>
            </div>

            {injectorTargets.length > 0 && (
                <div className="dispatch-capture-quick-row">
                    {injectorTargets.map(target => (
                        <button
                            key={target.id}
                            className={`dispatch-quick-target-btn ${selectedTargetId === target.id ? 'active' : ''}`}
                            onClick={() => void handleQuickLiveCapture(target.id)}
                            disabled={isCapturing}
                        >
                            {target.display_name}
                        </button>
                    ))}
                </div>
            )}

            {runtimeError && (
                <div className="dispatch-capture-error">
                    {runtimeError}
                </div>
            )}

            <div className="dispatch-capture-controls">
                <div className="dispatch-capture-control">
                    <label className="dispatch-section-label">Target</label>
                    <select
                        className="dispatch-select"
                        value={selectedTargetId}
                        onChange={event => setSelectedTargetId(event.target.value)}
                    >
                        {injectorTargets.length === 0 && <option value="">No injector targets</option>}
                        {injectorTargets.map(target => (
                            <option key={target.id} value={target.id}>
                                {target.display_name}
                            </option>
                        ))}
                    </select>
                    {selectedTarget && (
                        <div className="dispatch-capture-helper">
                            {selectedTarget.preferred_adapters.join(' -> ')}
                        </div>
                    )}
                </div>

                <div className="dispatch-capture-control">
                    <label className="dispatch-section-label">Source</label>
                    <select
                        className="dispatch-select"
                        value={sourceKind}
                        onChange={event => setSourceKind(event.target.value as CaptureSourceKind)}
                    >
                        {CAPTURE_SOURCE_OPTIONS.map(option => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                    <div className="dispatch-capture-helper">{selectedSourceOption.helper}</div>
                </div>

                <div className="dispatch-capture-control dispatch-capture-control--narrow">
                    <label className="dispatch-section-label">Live Timeout</label>
                    <input
                        className="dispatch-input"
                        type="number"
                        min={1000}
                        step={500}
                        value={liveTimeoutMs}
                        onChange={event => setLiveTimeoutMs(Number(event.target.value) || 1000)}
                    />
                    <div className="dispatch-capture-helper">Milliseconds for live CDP/UIA capture.</div>
                </div>
            </div>

            {sourceKind !== 'live' && (
                <div className="dispatch-section">
                    <label className="dispatch-section-label">Manual Payload</label>
                    <textarea
                        className="dispatch-textarea dispatch-capture-textarea"
                        value={manualPayload}
                        onChange={event => setManualPayload(event.target.value)}
                        placeholder={payloadPlaceholder(sourceKind)}
                        rows={sourceKind === 'uia' ? 10 : 8}
                    />
                </div>
            )}

            <div className="dispatch-capture-actions">
                <label className="dispatch-checkbox">
                    <input
                        type="checkbox"
                        checked={includeCollapsedToolContent}
                        onChange={event => setIncludeCollapsedToolContent(event.target.checked)}
                    />
                    Include collapsed tool content
                </label>

                <button
                    className={`dispatch-send-btn dispatch-capture-btn ${isCapturing ? 'dispatching' : ''}`}
                    onClick={() => void handleCapture()}
                    disabled={isCapturing || !selectedTargetId}
                >
                    {isCapturing ? 'Capturing...' : 'Capture Last Message'}
                </button>
            </div>

            {captureError && (
                <div className="dispatch-capture-error">
                    {captureError}
                </div>
            )}

            {capturedMessage && (
                <>
                    <div className="dispatch-capture-summary-grid">
                        <div className="dispatch-capture-summary-card">
                            <span className="dispatch-capture-summary-label">Message</span>
                            <span className="dispatch-capture-summary-value">{capturedMessage.message_id}</span>
                        </div>
                        <div className="dispatch-capture-summary-card">
                            <span className="dispatch-capture-summary-label">Adapter</span>
                            <span className="dispatch-capture-summary-value">{capturedMessage.source.adapter}</span>
                        </div>
                        <div className="dispatch-capture-summary-card">
                            <span className="dispatch-capture-summary-label">Confidence</span>
                            <span className="dispatch-capture-summary-value">{capturedMessage.source.confidence.toFixed(2)}</span>
                        </div>
                        <div className="dispatch-capture-summary-card">
                            <span className="dispatch-capture-summary-label">Complete</span>
                            <span className="dispatch-capture-summary-value">
                                {Math.round(capturedMessage.verification.completeness_score * 100)}%
                            </span>
                        </div>
                        <div className="dispatch-capture-summary-card">
                            <span className="dispatch-capture-summary-label">Run</span>
                            <span className="dispatch-capture-summary-value">{lastCaptureLabel ?? 'manual'}</span>
                        </div>
                    </div>

                    <div className="dispatch-capture-results-grid">
                        <div className="dispatch-capture-result-pane">
                            <div className="dispatch-section-label">Block Tree</div>
                            <div className="dispatch-capture-tree">
                                {capturedMessage.blocks.map(block => (
                                    <CaptureBlockNode key={block.id} block={block} />
                                ))}
                            </div>
                        </div>

                        <div className="dispatch-capture-result-pane">
                            <div className="dispatch-section-label">Plaintext</div>
                            <pre className="dispatch-capture-code">{capturedMessage.plaintext}</pre>
                        </div>

                        <div className="dispatch-capture-result-pane">
                            <div className="dispatch-section-label">Markdown</div>
                            <pre className="dispatch-capture-code">{capturedMessage.markdown}</pre>
                        </div>

                        <div className="dispatch-capture-result-pane">
                            <div className="dispatch-section-label">Raw JSON</div>
                            <pre className="dispatch-capture-code">{rawJson}</pre>
                        </div>
                    </div>
                </>
            )}
        </section>
    );
}
