/**
 * Automation Macros — Advanced AI Workflow Engine
 *
 * The most advanced AI macro system: conditional branching, variable system,
 * parallel step execution, loops, retry policies, event-driven triggers,
 * macro composition, and runtime context awareness.
 */

import type { ActionType } from './schedulerEngine';

// ═══════════════════════════════════════════════
// ─── CORE TYPES ───
// ═══════════════════════════════════════════════

export type MacroTrigger =
    | 'manual'
    | 'scheduled'
    | 'on_mission_complete'
    | 'on_mission_fail'
    | 'on_session_error'
    | 'on_health_degraded'
    | 'on_cost_threshold'
    | 'on_vault_alert'
    | 'on_new_conversation'
    | 'on_provider_offline'
    | 'webhook'
    | 'file_change'
    | 'cron';

export type StepType =
    | 'action'          // Execute a single action
    | 'condition'       // If/else branching
    | 'loop'            // Iterate over a list or count
    | 'parallel'        // Run multiple steps simultaneously
    | 'wait'            // Delay execution
    | 'set_variable'    // Set a runtime variable
    | 'transform'       // Transform data between steps
    | 'sub_macro'       // Call another macro
    | 'gate'            // Wait for external signal / approval
    | 'retry_block'     // Retry a set of steps with backoff
    | 'switch'          // Multi-way branch (like switch/case)
    | 'emit_event'      // Emit a custom event for other macros
    | 'try_catch';      // Try/catch/finally error handling

export type ConditionOperator =
    | 'eq' | 'neq' | 'gt' | 'lt' | 'gte' | 'lte'
    | 'contains' | 'not_contains'
    | 'matches'        // regex
    | 'exists' | 'not_exists'
    | 'is_online' | 'is_offline'
    | 'is_healthy' | 'is_degraded';

// ═══════════════════════════════════════════════
// ─── VARIABLE SYSTEM ───
// ═══════════════════════════════════════════════

export interface MacroVariable {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'array' | 'object';
    defaultValue?: any;
    description?: string;
    required?: boolean;
    validation?: {
        min?: number;
        max?: number;
        pattern?: string;
        enum?: any[];
    };
}

export interface RuntimeContext {
    variables: Record<string, any>;     // Mutable runtime state
    stepOutputs: Record<string, any>;   // Outputs from completed steps
    iteration: number;                  // Current loop iteration (0-based)
    parentContext?: RuntimeContext;      // For sub-macros
    startedAt: number;
    eventPayload?: Record<string, any>; // Data from the trigger event
}

// ═══════════════════════════════════════════════
// ─── STEP DEFINITIONS ───
// ═══════════════════════════════════════════════

export interface BaseStep {
    id: string;
    name: string;
    type: StepType;
    description?: string;
    enabled?: boolean;                  // Can disable steps without removing
    tags?: string[];
}

export interface ActionStep extends BaseStep {
    type: 'action';
    actionType: ActionType;
    payload?: Record<string, any>;      // Can use {{variable}} interpolation
    timeout?: number;
    outputVariable?: string;            // Store result in this variable name
}

export interface ConditionStep extends BaseStep {
    type: 'condition';
    condition: {
        left: string;                   // Variable path or literal, supports {{var}}
        operator: ConditionOperator;
        right?: string;                 // Comparison value
    };
    thenSteps: MacroStep[];             // Execute if true
    elseSteps?: MacroStep[];            // Execute if false
}

export interface SwitchStep extends BaseStep {
    type: 'switch';
    expression: string;                 // Variable to switch on, supports {{var}}
    cases: {
        value: string;
        steps: MacroStep[];
    }[];
    defaultSteps?: MacroStep[];
}

export interface LoopStep extends BaseStep {
    type: 'loop';
    mode: 'count' | 'for_each' | 'while' | 'until';
    count?: number;                     // For 'count' mode
    collection?: string;                // Variable name for 'for_each', supports {{var}}
    condition?: {                       // For 'while' / 'until' modes
        left: string;
        operator: ConditionOperator;
        right?: string;
    };
    maxIterations?: number;             // Safety limit (default 100)
    iteratorVariable?: string;          // Variable name for current item
    bodySteps: MacroStep[];
}

export interface ParallelStep extends BaseStep {
    type: 'parallel';
    branches: {
        name: string;
        steps: MacroStep[];
    }[];
    waitMode: 'all' | 'any' | 'settled'; // all=wait for all, any=first success, settled=all regardless of errors
    timeout?: number;
}

export interface WaitStep extends BaseStep {
    type: 'wait';
    durationMs?: number;
    durationExpression?: string;        // Dynamic: "{{delay_seconds}} * 1000"
    waitUntil?: string;                 // ISO timestamp or {{variable}}
    waitForEvent?: string;              // Wait for a specific event name
    eventTimeout?: number;              // Max wait for event (ms)
}

export interface SetVariableStep extends BaseStep {
    type: 'set_variable';
    variable: string;
    value: any;                         // Can use {{var}} interpolation
    expression?: string;                // JS-like expression: "{{count}} + 1"
}

export interface TransformStep extends BaseStep {
    type: 'transform';
    inputVariable: string;
    outputVariable: string;
    transform: 'map' | 'filter' | 'reduce' | 'sort' | 'flatten' | 'unique' | 'pick' | 'omit' | 'merge' | 'stringify' | 'parse' | 'format_template';
    transformArgs?: Record<string, any>;
}

export interface SubMacroStep extends BaseStep {
    type: 'sub_macro';
    macroId: string;                    // Reference to another macro
    inputMapping?: Record<string, string>;  // Map parent vars to child vars
    outputMapping?: Record<string, string>; // Map child results back to parent vars
}

export interface GateStep extends BaseStep {
    type: 'gate';
    gateType: 'approval' | 'signal' | 'time_window' | 'cost_check';
    message?: string;                   // Message for approval gates
    signalName?: string;                // For signal gates
    timeWindow?: { start: string; end: string }; // Only proceed within window
    costCheck?: { maxCost: number };    // Only proceed if under budget
    timeout?: number;
    onTimeout?: 'continue' | 'abort' | 'skip';
}

export interface RetryBlockStep extends BaseStep {
    type: 'retry_block';
    steps: MacroStep[];
    maxRetries: number;
    backoffStrategy: 'fixed' | 'exponential' | 'linear';
    initialDelayMs: number;
    maxDelayMs?: number;
    retryOn?: string[];                 // Error types to retry on
    onExhausted?: 'fail' | 'continue' | 'fallback';
    fallbackSteps?: MacroStep[];
}

export interface TryCatchStep extends BaseStep {
    type: 'try_catch';
    trySteps: MacroStep[];
    catchSteps?: MacroStep[];           // Executed on error (error available as {{error}})
    finallySteps?: MacroStep[];         // Always executed
}

export interface EmitEventStep extends BaseStep {
    type: 'emit_event';
    eventName: string;
    eventData?: Record<string, any>;    // supports {{var}} interpolation
}

export type MacroStep =
    | ActionStep
    | ConditionStep
    | SwitchStep
    | LoopStep
    | ParallelStep
    | WaitStep
    | SetVariableStep
    | TransformStep
    | SubMacroStep
    | GateStep
    | RetryBlockStep
    | TryCatchStep
    | EmitEventStep;

// ═══════════════════════════════════════════════
// ─── MACRO DEFINITION ───
// ═══════════════════════════════════════════════

export interface AutomationMacro {
    id: string;
    name: string;
    description: string;
    icon: string;
    version: number;
    steps: MacroStep[];
    variables: MacroVariable[];         // Declared input variables
    trigger: MacroTrigger;
    triggerConfig?: {                   // Additional trigger configuration
        cronExpression?: string;
        webhookPath?: string;
        watchPaths?: string[];
        eventFilter?: Record<string, any>;
        costThreshold?: number;
    };
    tags: string[];
    category?: string;
    enabled: boolean;
    lastRun?: string;
    runCount: number;
    averageDuration?: number;
    successRate?: number;               // 0-1
    errorLog?: string[];                // Last N errors
    createdAt: string;
    updatedAt: string;
}

// ═══════════════════════════════════════════════
// ─── EXECUTION STATE ───
// ═══════════════════════════════════════════════

export type ExecutionPhase = 'initializing' | 'running' | 'waiting' | 'gated' | 'retrying' | 'completed' | 'failed' | 'cancelled';

export interface StepResult {
    stepId: string;
    stepName: string;
    stepType: StepType;
    status: 'success' | 'error' | 'skipped' | 'timeout' | 'cancelled';
    duration: number;
    output?: any;
    error?: string;
    retryCount?: number;
    children?: StepResult[];            // Results from branches, loops, sub-macros
}

export interface MacroExecution {
    id: string;
    macroId: string;
    macroName: string;
    startedAt: number;
    endedAt?: number;
    currentStep: number;
    totalSteps: number;
    phase: ExecutionPhase;
    progress: number;                   // 0-100
    stepResults: StepResult[];
    context: RuntimeContext;
    logs: string[];                     // Human-readable log entries
}

// ═══════════════════════════════════════════════
// ─── VARIABLE INTERPOLATION ───
// ═══════════════════════════════════════════════

/**
 * Interpolate {{variable}} references in strings and objects.
 * Supports nested paths: {{step1.result.data}}
 */
export function interpolate(template: any, ctx: RuntimeContext): any {
    if (typeof template === 'string') {
        return template.replace(/\{\{([^}]+)\}\}/g, (_, path: string) => {
            const resolved = resolvePath(path.trim(), ctx);
            return resolved !== undefined ? String(resolved) : `{{${path}}}`;
        });
    }
    if (Array.isArray(template)) return template.map(item => interpolate(item, ctx));
    if (typeof template === 'object' && template !== null) {
        const result: Record<string, any> = {};
        for (const [k, v] of Object.entries(template)) {
            result[k] = interpolate(v, ctx);
        }
        return result;
    }
    return template;
}

function resolvePath(path: string, ctx: RuntimeContext): any {
    // Check variables first, then step outputs
    const parts = path.split('.');
    let value: any;

    if (parts[0] === 'env') {
        // environment references
        return undefined;
    }

    // Try variables
    value = ctx.variables[parts[0]];
    if (value === undefined) {
        // Try step outputs
        value = ctx.stepOutputs[parts[0]];
    }

    // Navigate nested path
    for (let i = 1; i < parts.length && value !== undefined; i++) {
        value = value?.[parts[i]];
    }

    return value;
}

// ═══════════════════════════════════════════════
// ─── CONDITION EVALUATOR ───
// ═══════════════════════════════════════════════

export function evaluateCondition(
    condition: { left: string; operator: ConditionOperator; right?: string },
    ctx: RuntimeContext,
): boolean {
    const left = interpolate(condition.left, ctx);
    const right = condition.right !== undefined ? interpolate(condition.right, ctx) : undefined;

    switch (condition.operator) {
        case 'eq': return left == right;
        case 'neq': return left != right;
        case 'gt': return Number(left) > Number(right);
        case 'lt': return Number(left) < Number(right);
        case 'gte': return Number(left) >= Number(right);
        case 'lte': return Number(left) <= Number(right);
        case 'contains': return String(left).includes(String(right));
        case 'not_contains': return !String(left).includes(String(right));
        case 'matches':
            try { return new RegExp(String(right)).test(String(left)); }
            catch { return false; }
        case 'exists': return left !== undefined && left !== null;
        case 'not_exists': return left === undefined || left === null;
        case 'is_online': return left === true || left === 'online';
        case 'is_offline': return left === false || left === 'offline';
        case 'is_healthy': return left === 'healthy' || Number(left) > 0.7;
        case 'is_degraded': return left === 'degraded' || (Number(left) > 0 && Number(left) <= 0.7);
        default: return false;
    }
}

// ═══════════════════════════════════════════════
// ─── MACRO CREATION HELPERS ───
// ═══════════════════════════════════════════════

let _stepCounter = 0;
function stepId(): string {
    return `step-${++_stepCounter}-${Math.random().toString(36).slice(2, 5)}`;
}

export function createMacro(
    name: string,
    description: string,
    icon: string,
    steps: MacroStep[],
    options?: {
        trigger?: MacroTrigger;
        triggerConfig?: AutomationMacro['triggerConfig'];
        tags?: string[];
        category?: string;
        variables?: MacroVariable[];
    },
): AutomationMacro {
    const now = new Date().toISOString();
    return {
        id: `macro-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        name,
        description,
        icon,
        version: 1,
        steps,
        variables: options?.variables || [],
        trigger: options?.trigger || 'manual',
        triggerConfig: options?.triggerConfig,
        tags: options?.tags || [],
        category: options?.category,
        enabled: true,
        runCount: 0,
        createdAt: now,
        updatedAt: now,
    };
}

// Step builder helpers
export const step = {
    action: (name: string, actionType: ActionType, payload?: Record<string, any>, opts?: Partial<ActionStep>): ActionStep => ({
        id: stepId(), name, type: 'action', actionType, payload, ...opts,
    }),

    condition: (name: string, left: string, op: ConditionOperator, right: string | undefined, thenSteps: MacroStep[], elseSteps?: MacroStep[]): ConditionStep => ({
        id: stepId(), name, type: 'condition',
        condition: { left, operator: op, right },
        thenSteps, elseSteps,
    }),

    switchCase: (name: string, expression: string, cases: { value: string; steps: MacroStep[] }[], defaultSteps?: MacroStep[]): SwitchStep => ({
        id: stepId(), name, type: 'switch', expression, cases, defaultSteps,
    }),

    loop: (name: string, mode: LoopStep['mode'], body: MacroStep[], config?: Partial<LoopStep>): LoopStep => ({
        id: stepId(), name, type: 'loop', mode, bodySteps: body, ...config,
    }),

    parallel: (name: string, branches: { name: string; steps: MacroStep[] }[], waitMode: ParallelStep['waitMode'] = 'all'): ParallelStep => ({
        id: stepId(), name, type: 'parallel', branches, waitMode,
    }),

    wait: (name: string, durationMs: number): WaitStep => ({
        id: stepId(), name, type: 'wait', durationMs,
    }),

    setVar: (name: string, variable: string, value: any): SetVariableStep => ({
        id: stepId(), name, type: 'set_variable', variable, value,
    }),

    subMacro: (name: string, macroId: string, inputMapping?: Record<string, string>): SubMacroStep => ({
        id: stepId(), name, type: 'sub_macro', macroId, inputMapping,
    }),

    retry: (name: string, steps: MacroStep[], maxRetries: number = 3, opts?: Partial<RetryBlockStep>): RetryBlockStep => ({
        id: stepId(), name, type: 'retry_block', steps, maxRetries,
        backoffStrategy: 'exponential', initialDelayMs: 1000, ...opts,
    }),

    tryCatch: (name: string, trySteps: MacroStep[], catchSteps?: MacroStep[], finallySteps?: MacroStep[]): TryCatchStep => ({
        id: stepId(), name, type: 'try_catch', trySteps, catchSteps, finallySteps,
    }),

    emit: (name: string, eventName: string, eventData?: Record<string, any>): EmitEventStep => ({
        id: stepId(), name, type: 'emit_event', eventName, eventData,
    }),

    gate: (name: string, gateType: GateStep['gateType'], opts?: Partial<GateStep>): GateStep => ({
        id: stepId(), name, type: 'gate', gateType, ...opts,
    }),

    transform: (name: string, inputVar: string, outputVar: string, transform: TransformStep['transform'], args?: Record<string, any>): TransformStep => ({
        id: stepId(), name, type: 'transform', inputVariable: inputVar, outputVariable: outputVar, transform, transformArgs: args,
    }),
};

// ═══════════════════════════════════════════════
// ─── BUILT-IN MACROS (using advanced features) ───
// ═══════════════════════════════════════════════

export const BUILT_IN_MACROS: AutomationMacro[] = [
    createMacro(
        'Morning Brief',
        'Health check → launch all providers in parallel → inject daily prompt → wait for responses → extract and synthesize',
        '☀️',
        [
            step.action('Health Check', 'health_check', { target: 'all' }, { outputVariable: 'healthResult' }),
            step.condition('Check Health', '{{healthResult}}', 'is_healthy', undefined, [
                // Healthy path: launch all providers in parallel
                step.parallel('Launch All Providers', [
                    {
                        name: 'ChatGPT', steps: [
                            step.action('Launch ChatGPT', 'launch_mission', { provider: 'chatgpt', prompt: 'Good morning! Summarize the latest AI and tech developments today.' }),
                        ]
                    },
                    {
                        name: 'Gemini', steps: [
                            step.action('Launch Gemini', 'launch_mission', { provider: 'gemini', prompt: 'Good morning! Summarize the latest AI and tech developments today.' }),
                        ]
                    },
                    {
                        name: 'Claude', steps: [
                            step.action('Launch Claude', 'launch_mission', { provider: 'claude', prompt: 'Good morning! Summarize the latest AI and tech developments today.' }),
                        ]
                    },
                ], 'settled'),
                step.wait('Wait for Responses', 30000),
                step.emit('Notify', 'brief_complete', { message: '☀️ Morning Brief complete — check Synthesizer' }),
            ], [
                // Unhealthy path
                step.action('Alert', 'notify', { message: '⚠️ Morning Brief skipped — system health degraded' }),
            ]),
        ],
        {
            trigger: 'scheduled',
            triggerConfig: { cronExpression: '0 8 * * *' },
            tags: ['daily', 'research', 'morning'],
            category: 'research',
            variables: [
                { name: 'prompt', type: 'string', defaultValue: 'Summarize the latest AI and tech developments today.', description: 'Daily briefing prompt' },
            ],
        },
    ),

    createMacro(
        'Session Cleanup',
        'Rotate stale sessions with retry, check health, report results',
        '🧹',
        [
            step.retry('Rotate with Retry', [
                step.action('Auto-Rotate', 'auto_rotate', { threshold: 40, providers: ['chatgpt', 'gemini', 'claude'] }),
            ], 3, { backoffStrategy: 'exponential', initialDelayMs: 2000 }),
            step.wait('Cooldown', 3000),
            step.action('Health Check', 'health_check', { target: 'all' }, { outputVariable: 'postHealth' }),
            step.condition('Report', '{{postHealth}}', 'is_healthy', undefined, [
                step.action('Success', 'notify', { message: '🧹 Session cleanup complete — all systems healthy' }),
            ], [
                step.action('Warning', 'notify', { message: '🧹 Cleanup done but health still degraded' }),
            ]),
        ],
        { trigger: 'scheduled', triggerConfig: { cronExpression: '0 18 * * *' }, tags: ['maintenance'], category: 'maintenance' },
    ),

    createMacro(
        'Cost Report',
        'Reset daily vault stats and generate a cost summary',
        '📊',
        [
            step.action('Snapshot Stats', 'vault_reset', { scope: 'snapshot' }, { outputVariable: 'costSnapshot' }),
            step.action('Reset Daily', 'vault_reset', { scope: 'daily' }),
            step.action('Report', 'notify', { message: '📊 Daily cost report: {{costSnapshot}}' }),
        ],
        { trigger: 'scheduled', triggerConfig: { cronExpression: '59 23 * * *' }, tags: ['reporting', 'daily'], category: 'reporting' },
    ),

    createMacro(
        'Auto-Research',
        'Parallel dispatch research prompt to all providers with retry on failure, then synthesize results',
        '🔬',
        [
            step.setVar('Set Prompt', 'researchPrompt', '{{prompt}}'),
            step.tryCatch('Research Pipeline', [
                step.parallel('Dispatch to All', [
                    {
                        name: 'ChatGPT Research', steps: [
                            step.retry('ChatGPT', [
                                step.action('Inject', 'launch_mission', { provider: 'chatgpt', prompt: '{{researchPrompt}}' }),
                            ], 2),
                        ]
                    },
                    {
                        name: 'Gemini Research', steps: [
                            step.retry('Gemini', [
                                step.action('Inject', 'launch_mission', { provider: 'gemini', prompt: '{{researchPrompt}}' }),
                            ], 2),
                        ]
                    },
                    {
                        name: 'Claude Research', steps: [
                            step.retry('Claude', [
                                step.action('Inject', 'launch_mission', { provider: 'claude', prompt: '{{researchPrompt}}' }),
                            ], 2),
                        ]
                    },
                ], 'settled'),
                step.wait('Extraction Time', 45000),
                step.emit('Done', 'research_complete', { prompt: '{{researchPrompt}}' }),
            ], [
                // Catch: some providers failed
                step.action('Partial Result', 'notify', { message: '🔬 Research partially complete — some providers errored: {{error}}' }),
            ], [
                // Finally: always notify
                step.action('Complete', 'notify', { message: '🔬 Auto-Research pipeline finished' }),
            ]),
        ],
        {
            trigger: 'manual', tags: ['research'],
            category: 'research',
            variables: [
                { name: 'prompt', type: 'string', required: true, description: 'Research prompt to dispatch to all providers' },
            ],
        },
    ),

    createMacro(
        'Provider Health Monitor',
        'Loop through all providers, check health, auto-restart if degraded, emit alert if failed',
        '🏥',
        [
            step.setVar('Init Providers', 'providers', ['chatgpt', 'gemini', 'claude', 'perplexity']),
            step.loop('Check Each Provider', 'for_each', [
                step.action('Check', 'health_check', { target: '{{currentProvider}}' }, { outputVariable: 'providerHealth' }),
                step.switchCase('Handle Status', '{{providerHealth}}', [
                    {
                        value: 'healthy', steps: [
                            step.action('Log OK', 'notify', { message: '✅ {{currentProvider}} healthy', silent: true }),
                        ]
                    },
                    {
                        value: 'degraded', steps: [
                            step.retry('Auto-Restart', [
                                step.action('Rotate', 'auto_rotate', { provider: '{{currentProvider}}' }),
                            ], 2),
                        ]
                    },
                ], [
                    // Default: offline
                    step.emit('Provider Down', 'provider_offline', { provider: '{{currentProvider}}' }),
                ]),
            ], { collection: 'providers', iteratorVariable: 'currentProvider', maxIterations: 10 }),
        ],
        {
            trigger: 'on_health_degraded', tags: ['monitoring', 'auto-recovery'],
            category: 'monitoring',
        },
    ),

    createMacro(
        'Budget Guardian',
        'Check cost thresholds, pause expensive providers if over budget, alert user',
        '💰',
        [
            step.gate('Business Hours', 'time_window', {
                timeWindow: { start: '08:00', end: '22:00' },
                onTimeout: 'continue',
            }),
            step.action('Get Costs', 'vault_reset', { scope: 'snapshot' }, { outputVariable: 'costs' }),
            step.condition('Over Budget?', '{{costs}}', 'gt', '50', [
                step.action('ALERT', 'notify', { message: '🚨 BUDGET ALERT: ${{costs}} spent today — exceeds $50 limit!', urgent: true }),
                step.emit('Budget Exceeded', 'cost_threshold', { amount: '{{costs}}' }),
            ], [
                step.condition('Near Budget?', '{{costs}}', 'gt', '40', [
                    step.action('Warning', 'notify', { message: '⚠️ Budget warning: ${{costs}} of $50 daily limit used' }),
                ]),
            ]),
        ],
        {
            trigger: 'on_cost_threshold', triggerConfig: { costThreshold: 40 },
            tags: ['budget', 'guard'], category: 'financial',
        },
    ),
];

// ═══════════════════════════════════════════════
// ─── MACRO EXECUTOR ───
// ═══════════════════════════════════════════════

/**
 * Execute a macro with full runtime context, variable interpolation,
 * conditional branching, loops, parallel execution, retry policies,
 * and event emission.
 */
export async function executeMacro(
    macro: AutomationMacro,
    stepHandler: (step: MacroStep, ctx: RuntimeContext) => Promise<any>,
    onProgress?: (execution: MacroExecution) => void,
    initialVars?: Record<string, any>,
): Promise<MacroExecution> {
    const execution: MacroExecution = {
        id: `exec-${Date.now()}`,
        macroId: macro.id,
        macroName: macro.name,
        startedAt: Date.now(),
        currentStep: 0,
        totalSteps: countSteps(macro.steps),
        phase: 'initializing',
        progress: 0,
        stepResults: [],
        context: {
            variables: { ...getDefaultVariables(macro.variables), ...initialVars },
            stepOutputs: {},
            iteration: 0,
            startedAt: Date.now(),
        },
        logs: [`[${new Date().toLocaleTimeString()}] Starting macro: ${macro.name}`],
    };

    onProgress?.(execution);

    try {
        execution.phase = 'running';
        await executeSteps(macro.steps, execution, stepHandler, onProgress);
        execution.phase = 'completed';
    } catch (err: any) {
        execution.phase = 'failed';
        execution.logs.push(`[${new Date().toLocaleTimeString()}] FATAL: ${err.message}`);
    }

    execution.endedAt = Date.now();
    execution.progress = 100;
    execution.logs.push(`[${new Date().toLocaleTimeString()}] Finished: ${execution.phase} (${execution.endedAt - execution.startedAt}ms)`);
    onProgress?.(execution);

    return execution;
}

async function executeSteps(
    steps: MacroStep[],
    execution: MacroExecution,
    handler: (step: MacroStep, ctx: RuntimeContext) => Promise<any>,
    onProgress?: (execution: MacroExecution) => void,
): Promise<void> {
    for (const s of steps) {
        if (s.enabled === false) continue;

        const stepStart = Date.now();
        execution.currentStep++;
        execution.progress = Math.round((execution.currentStep / execution.totalSteps) * 100);
        execution.logs.push(`[${new Date().toLocaleTimeString()}] → ${s.name} (${s.type})`);
        onProgress?.(execution);

        try {
            const result = await executeStep(s, execution, handler, onProgress);
            execution.stepResults.push({
                stepId: s.id,
                stepName: s.name,
                stepType: s.type,
                status: 'success',
                duration: Date.now() - stepStart,
                output: result,
            });
        } catch (err: any) {
            execution.stepResults.push({
                stepId: s.id,
                stepName: s.name,
                stepType: s.type,
                status: 'error',
                duration: Date.now() - stepStart,
                error: err.message,
            });
            throw err; // Propagate unless handled by try_catch
        }
    }
}

async function executeStep(
    s: MacroStep,
    execution: MacroExecution,
    handler: (step: MacroStep, ctx: RuntimeContext) => Promise<any>,
    onProgress?: (execution: MacroExecution) => void,
): Promise<any> {
    const ctx = execution.context;

    switch (s.type) {
        case 'action': {
            const interpolated = { ...s, payload: interpolate(s.payload, ctx) };
            const result = await handler(interpolated, ctx);
            if (s.outputVariable) {
                ctx.variables[s.outputVariable] = result;
                ctx.stepOutputs[s.id] = result;
            }
            return result;
        }

        case 'condition': {
            const matched = evaluateCondition(s.condition, ctx);
            execution.logs.push(`  condition: ${matched ? 'TRUE → then' : 'FALSE → else'}`);
            const branch = matched ? s.thenSteps : (s.elseSteps || []);
            if (branch.length > 0) await executeSteps(branch, execution, handler, onProgress);
            return matched;
        }

        case 'switch': {
            const expr = String(interpolate(s.expression, ctx));
            const matchingCase = s.cases.find(c => c.value === expr);
            const branch = matchingCase?.steps || s.defaultSteps || [];
            execution.logs.push(`  switch(${expr}) → ${matchingCase ? matchingCase.value : 'default'}`);
            if (branch.length > 0) await executeSteps(branch, execution, handler, onProgress);
            return expr;
        }

        case 'loop': {
            const maxIter = s.maxIterations || 100;
            let iterations = 0;

            if (s.mode === 'count') {
                const count = Math.min(s.count || 0, maxIter);
                for (let i = 0; i < count; i++) {
                    ctx.iteration = i;
                    if (s.iteratorVariable) ctx.variables[s.iteratorVariable] = i;
                    await executeSteps(s.bodySteps, execution, handler, onProgress);
                    iterations++;
                }
            } else if (s.mode === 'for_each') {
                const collection = s.collection ? resolvePath(interpolate(s.collection, ctx), ctx) || ctx.variables[s.collection] : [];
                const items = Array.isArray(collection) ? collection : [];
                for (let i = 0; i < Math.min(items.length, maxIter); i++) {
                    ctx.iteration = i;
                    if (s.iteratorVariable) ctx.variables[s.iteratorVariable] = items[i];
                    await executeSteps(s.bodySteps, execution, handler, onProgress);
                    iterations++;
                }
            } else if (s.mode === 'while') {
                while (s.condition && evaluateCondition(s.condition, ctx) && iterations < maxIter) {
                    ctx.iteration = iterations;
                    await executeSteps(s.bodySteps, execution, handler, onProgress);
                    iterations++;
                }
            } else if (s.mode === 'until') {
                do {
                    ctx.iteration = iterations;
                    await executeSteps(s.bodySteps, execution, handler, onProgress);
                    iterations++;
                } while (s.condition && !evaluateCondition(s.condition, ctx) && iterations < maxIter);
            }

            execution.logs.push(`  loop completed: ${iterations} iterations`);
            return iterations;
        }

        case 'parallel': {
            execution.phase = 'running';
            const promises = s.branches.map(async (branch) => {
                try {
                    await executeSteps(branch.steps, execution, handler, onProgress);
                    return { name: branch.name, status: 'success' as const };
                } catch (err: any) {
                    if (s.waitMode === 'all') throw err;
                    return { name: branch.name, status: 'error' as const, error: err.message };
                }
            });

            if (s.waitMode === 'any') {
                // Use Promise.race as a cross-target alternative to Promise.any
                const result = await Promise.race(promises);
                return result;
            } else {
                const results = await Promise.allSettled(promises);
                return results;
            }
        }

        case 'wait': {
            const ms = s.durationMs || 1000;
            execution.phase = 'waiting';
            execution.logs.push(`  waiting ${ms}ms`);
            onProgress?.(execution);
            await sleep(ms);
            execution.phase = 'running';
            return ms;
        }

        case 'set_variable': {
            const val = interpolate(s.value, ctx);
            ctx.variables[s.variable] = val;
            execution.logs.push(`  set ${s.variable} = ${JSON.stringify(val).slice(0, 60)}`);
            return val;
        }

        case 'transform': {
            const input = ctx.variables[s.inputVariable];
            let output: any = input;

            switch (s.transform) {
                case 'stringify': output = JSON.stringify(input); break;
                case 'parse': output = typeof input === 'string' ? JSON.parse(input) : input; break;
                case 'flatten': output = Array.isArray(input) ? input.flat() : input; break;
                case 'unique': output = Array.isArray(input) ? [...new Set(input)] : input; break;
                case 'sort': output = Array.isArray(input) ? [...input].sort() : input; break;
                default: output = input;
            }

            ctx.variables[s.outputVariable] = output;
            return output;
        }

        case 'sub_macro':
            execution.logs.push(`  invoking sub-macro: ${s.macroId}`);
            return await handler(s, ctx);

        case 'gate': {
            execution.phase = 'gated';
            execution.logs.push(`  gate: ${s.gateType} — ${s.message || 'waiting...'}`);
            onProgress?.(execution);

            if (s.gateType === 'time_window' && s.timeWindow) {
                const now = new Date();
                const [sh, sm] = s.timeWindow.start.split(':').map(Number);
                const [eh, em] = s.timeWindow.end.split(':').map(Number);
                const startMin = sh * 60 + sm;
                const endMin = eh * 60 + em;
                const nowMin = now.getHours() * 60 + now.getMinutes();
                if (nowMin < startMin || nowMin > endMin) {
                    if (s.onTimeout === 'abort') throw new Error('Outside time window');
                    if (s.onTimeout === 'skip') return 'skipped';
                }
            }

            execution.phase = 'running';
            return 'passed';
        }

        case 'retry_block': {
            let lastError: Error | null = null;
            for (let attempt = 0; attempt <= s.maxRetries; attempt++) {
                try {
                    await executeSteps(s.steps, execution, handler, onProgress);
                    return { attempts: attempt + 1, status: 'success' };
                } catch (err: any) {
                    lastError = err;
                    execution.phase = 'retrying';
                    execution.logs.push(`  retry ${attempt + 1}/${s.maxRetries}: ${err.message}`);

                    if (attempt < s.maxRetries) {
                        const delay = s.backoffStrategy === 'exponential'
                            ? Math.min(s.initialDelayMs * Math.pow(2, attempt), s.maxDelayMs || 60000)
                            : s.backoffStrategy === 'linear'
                                ? s.initialDelayMs * (attempt + 1)
                                : s.initialDelayMs;
                        await sleep(delay);
                    }
                }
            }

            execution.phase = 'running';
            if (s.onExhausted === 'continue') return { attempts: s.maxRetries + 1, status: 'exhausted' };
            if (s.onExhausted === 'fallback' && s.fallbackSteps) {
                await executeSteps(s.fallbackSteps, execution, handler, onProgress);
                return { attempts: s.maxRetries + 1, status: 'fallback' };
            }
            throw lastError || new Error('Retries exhausted');
        }

        case 'try_catch': {
            try {
                await executeSteps(s.trySteps, execution, handler, onProgress);
            } catch (err: any) {
                ctx.variables['error'] = err.message;
                execution.logs.push(`  caught: ${err.message}`);
                if (s.catchSteps) await executeSteps(s.catchSteps, execution, handler, onProgress);
            } finally {
                if (s.finallySteps) await executeSteps(s.finallySteps, execution, handler, onProgress);
            }
            return 'ok';
        }

        case 'emit_event': {
            execution.logs.push(`  emit: ${s.eventName}`);
            return await handler({ ...s, eventData: interpolate(s.eventData, ctx) } as MacroStep, ctx);
        }

        default:
            return await handler(s, ctx);
    }
}

// ─── Helpers ───

function countSteps(steps: MacroStep[]): number {
    let count = 0;
    for (const s of steps) {
        count++;
        if (s.type === 'condition') count += countSteps(s.thenSteps) + countSteps(s.elseSteps || []);
        if (s.type === 'loop') count += countSteps(s.bodySteps);
        if (s.type === 'parallel') s.branches.forEach(b => { count += countSteps(b.steps); });
        if (s.type === 'retry_block') count += countSteps(s.steps) + countSteps(s.fallbackSteps || []);
        if (s.type === 'try_catch') count += countSteps(s.trySteps) + countSteps(s.catchSteps || []) + countSteps(s.finallySteps || []);
        if (s.type === 'switch') s.cases.forEach(c => { count += countSteps(c.steps); });
    }
    return count;
}

function getDefaultVariables(vars: MacroVariable[]): Record<string, any> {
    const defaults: Record<string, any> = {};
    for (const v of vars) {
        if (v.defaultValue !== undefined) defaults[v.name] = v.defaultValue;
    }
    return defaults;
}

function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}
