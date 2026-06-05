import { Component, useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type PointerEvent, type ReactNode } from 'react';
import { AssistantIcon, CheckIcon, CloseIcon, CodexIcon, DocsIcon, EvidenceIcon, GraphIcon, IdeIcon, RunIcon, StopIcon, ToolsIcon, WorkSurfaceIcon } from './icons';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';

type BuildWorkbenchPageProps = {
  runtime: IonCockpitViewModel;
};

type SnapEdge = 'left' | 'right' | 'top' | 'bottom' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | null;
type PanelFrame = {
  x: number;
  y: number;
  width: number;
  height: number;
  edge: SnapEdge;
};
type DragMode = 'move' | 'resize';
type DragState = {
  mode: DragMode;
  pointerId: number;
  originX: number;
  originY: number;
  frame: PanelFrame;
};
type BuildTemplate = {
  id: string;
  label: string;
  kind: string;
  deps: string[];
  icon: ReactNode;
  summary: string;
};
type BuildMessage = {
  id: string;
  role: 'builder' | 'operator' | 'system';
  text: string;
};
type BuildPanelTab = 'chat' | 'agent' | 'tools' | 'projects';
type BuildAmbientModeId = 'quiet_ambient' | 'companion' | 'pairing' | 'meeting' | 'dictation' | 'command' | 'safe_action';
type BuildCursorContext = {
  x: number;
  y: number;
  behavior: 'move' | 'click' | 'dwell';
  updatedAt: number;
};
type BuildAmbientCandidate = {
  id: string;
  rawSpeech: string;
  interpretedPrompt: string;
  classification: string;
  aiShouldRespond: boolean;
  confidence: number;
  needsScreenContext: boolean;
  needsUserConfirmation: boolean;
  allowedMode: string;
  actionLevel: string;
  target: string;
};
type BuildProjectSystem = {
  id: string;
  label: string;
  status: string;
  branch: string;
  capsule: string;
  diff: string;
  notes: number;
  screenshots: number;
  rollback: string;
  evidence: string[];
  lanes: Array<{
    id: string;
    label: string;
    value: string;
    state: string;
  }>;
};
type BuildToolContract = {
  tool_id: string;
  label: string;
  mode_ids?: string[];
  control_class: string;
  authority: string;
  status: string;
  endpoint?: string | null;
  next_gate?: string | null;
  description: string;
};
type BuildWorkspaceMode = {
  id: string;
  label: string;
  kind: string;
  summary: string;
  deps?: string[];
  tool_ids?: string[];
};
type BuildWorkspaceModel = {
  schema_id?: string;
  generated_at?: string;
  ok?: boolean;
  verdict?: string;
  selected_project_id?: string;
  project_systems?: BuildProjectSystem[];
  authority_classes?: string[];
  agent_tool_control?: {
    modes?: BuildWorkspaceMode[];
    tool_contracts?: BuildToolContract[];
    write_confirmation_required?: boolean;
    write_confirmation_token?: string;
  };
  codex_queue_control?: {
    queued_request_count?: number;
    active_run_count?: number;
    active_process_running?: boolean;
    next_request_path?: string | null;
    automation_surface?: string;
    autorun_loop_state?: string;
  };
  builder_agent_chat?: BuildBuilderAgentChat;
};
type BuildBuilderAgentLane = {
  id: string;
  label: string;
  tier: string;
  status: string;
  count: number;
  role: string;
  allowed_outputs?: string[];
  blocked_outputs?: string[];
};
type BuildBuilderSpecialist = {
  id: string;
  label: string;
  trigger?: string;
  status?: string;
  role?: string;
  outputs?: string[];
};
type BuildBuilderContextCapsule = {
  project_id?: string;
  label?: string;
  branch?: string;
  capsule_state?: string;
  artifact_slots?: string[];
  context_refs?: string[];
  evidence_refs?: string[];
  refresh_triggers?: string[];
};
type BuildBuilderSafetyInvariant = {
  id?: string;
  assertion?: string;
  proof?: string;
};
type BuildBuilderAmbientMode = {
  id?: string;
  label?: string;
  interrupt_policy?: string;
  default_allowed_mode?: string;
};
type BuildBuilderAmbientIntentRouter = {
  schema_id?: string;
  router_id?: string;
  posture?: string;
  law?: string;
  candidate_only?: boolean;
  auto_execute_allowed?: boolean;
  continuous_fullscreen_capture_allowed?: boolean;
  raw_audio_persistence_allowed?: boolean;
  recognized_prompt_required_for_response?: boolean;
  operator_started_microphone_required?: boolean;
  classification_states?: string[];
  allowed_modes?: string[];
  speech_modes?: BuildBuilderAmbientMode[];
  router_stages?: Array<Record<string, unknown>>;
  capture_policy?: Record<string, unknown>;
  prompt_candidate_schema?: Record<string, unknown>;
  prompt_candidate_examples?: Array<Record<string, unknown>>;
  memory_layers?: Array<Record<string, unknown>>;
  action_gate_policy?: Record<string, unknown>;
  privacy_invariants?: string[];
};
type BuildBuilderAgentChat = {
  schema_id?: string;
  verdict?: string;
  surface?: string;
  standard_codex_chat_affected?: boolean;
  build_only_packet_required?: boolean;
  standard_codex_chat_write_blocked?: boolean;
  queue_surface_namespace?: string;
  preview_watchdog_ms?: number;
  preview_csp_policy?: string;
  panel_contract?: Record<string, unknown>;
  mode_surfaces?: Array<Record<string, unknown>>;
  lanes?: BuildBuilderAgentLane[];
  escalation_rules?: Array<Record<string, unknown>>;
  proof_ladder?: string[];
  activity?: Record<string, unknown>;
  authority?: Record<string, unknown>;
  message_packet_schema?: Record<string, unknown>;
  response_lifecycle?: Array<Record<string, unknown>>;
  cognition_bus?: Record<string, unknown>;
  specialist_swarm?: {
    swarm_id?: string;
    posture?: string;
    active_spawn_count?: number;
    hidden_spawn_allowed?: boolean;
    recursive_spawn_allowed?: boolean;
    fanout_rules?: string[];
    fanin_receipt_fields?: string[];
    specialists?: BuildBuilderSpecialist[];
  };
  context_capsule_system?: {
    posture?: string;
    capsule_lifecycle?: string[];
    capsules?: BuildBuilderContextCapsule[];
  };
  ambient_intent_router?: BuildBuilderAmbientIntentRouter;
  intervention_lane?: {
    status?: string;
    late_correction_allowed?: boolean;
    visible_to_operator?: boolean;
    event_types?: string[];
    required_fields?: string[];
  };
  tool_hook_matrix?: Record<string, unknown>;
  safety_invariants?: BuildBuilderSafetyInvariant[];
};
type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: any) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
  abort: () => void;
};
type BrowserSpeechWindow = Window & {
  SpeechRecognition?: new () => SpeechRecognitionLike;
  webkitSpeechRecognition?: new () => SpeechRecognitionLike;
};

const EDGE_STICK_PX = 26;
const MIN_PANEL_WIDTH = 320;
const MIN_PANEL_HEIGHT = 360;
const MAX_PANEL_WIDTH = 760;
const MAX_PANEL_HEIGHT = 840;

const BUILD_TEMPLATES: BuildTemplate[] = [
  { id: 'raw', label: 'Raw expression', kind: 'expressive_docs', deps: [], icon: <WorkSurfaceIcon />, summary: 'Styled narrative, sources, images, motion.' },
  { id: 'app', label: 'Apps', kind: 'react_app_surface', deps: ['react'], icon: <IdeIcon />, summary: 'Sites, apps, dashboards, product surfaces.' },
  { id: 'world', label: 'Worlds', kind: '3d_game_scene', deps: ['three', '@react-three/fiber'], icon: <RunIcon />, summary: '3D models, animation, games, simulation.' },
  { id: 'media', label: 'Media', kind: 'image_video_studio', deps: ['canvas', 'media'], icon: <EvidenceIcon />, summary: 'Image, video, timeline, edit studio.' },
  { id: 'flow', label: 'Graphs', kind: 'data_flow_graphs', deps: ['charts'], icon: <GraphIcon />, summary: 'Charts, data flows, node graphs.' },
  { id: 'docs', label: 'Docs', kind: 'latex_docs', deps: ['latex'], icon: <DocsIcon />, summary: 'Documentation, equations, writing with AI.' },
];

const BUILD_PROJECT_SYSTEMS: BuildProjectSystem[] = [
  {
    id: 'current-build',
    label: 'Current Build Surface',
    status: 'draft',
    branch: 'build/page-shell',
    capsule: 'candidate capsule',
    diff: 'ui + endpoint',
    notes: 4,
    screenshots: 2,
    rollback: 'preview stack',
    evidence: ['BuildWorkbenchPage.tsx', 'HELIXION_BUILD_PAGE_FIRST_SLICE_20260605.md'],
    lanes: [
      { id: 'branches', label: 'Branches', value: '1 active', state: 'tracked' },
      { id: 'diffs', label: 'Diffs', value: '4 files', state: 'staged view' },
      { id: 'notes', label: 'Notes', value: '4 local', state: 'candidate' },
      { id: 'shots', label: 'Shots', value: '2 captures', state: 'visual' },
      { id: 'capsules', label: 'Capsules', value: '1 active', state: 'bounded' },
      { id: 'rollback', label: 'Rollback', value: 'local stack', state: 'ready' },
    ],
  },
  {
    id: 'game-seed',
    label: 'Game Engine Seed',
    status: 'template',
    branch: 'build/game-loop',
    capsule: 'needs project capsule',
    diff: 'none',
    notes: 1,
    screenshots: 0,
    rollback: 'clean seed',
    evidence: ['canvas loop', 'sandbox iframe'],
    lanes: [
      { id: 'branches', label: 'Branches', value: 'seed', state: 'ready' },
      { id: 'diffs', label: 'Diffs', value: 'none', state: 'clean' },
      { id: 'notes', label: 'Notes', value: '1 idea', state: 'draft' },
      { id: 'shots', label: 'Shots', value: '0', state: 'empty' },
      { id: 'capsules', label: 'Capsules', value: 'create', state: 'gated' },
      { id: 'rollback', label: 'Rollback', value: 'seed', state: 'ready' },
    ],
  },
  {
    id: 'image-editor-seed',
    label: 'Image Editor Seed',
    status: 'template',
    branch: 'build/image-editor',
    capsule: 'needs project capsule',
    diff: 'none',
    notes: 1,
    screenshots: 0,
    rollback: 'clean seed',
    evidence: ['canvas editor shell', 'sandbox iframe'],
    lanes: [
      { id: 'branches', label: 'Branches', value: 'seed', state: 'ready' },
      { id: 'diffs', label: 'Diffs', value: 'none', state: 'clean' },
      { id: 'notes', label: 'Notes', value: '1 idea', state: 'draft' },
      { id: 'shots', label: 'Shots', value: '0', state: 'empty' },
      { id: 'capsules', label: 'Capsules', value: 'create', state: 'gated' },
      { id: 'rollback', label: 'Rollback', value: 'seed', state: 'ready' },
    ],
  },
];

function initialPanelFrame(): PanelFrame {
  if (typeof window === 'undefined') {
    return { x: 28, y: 72, width: 420, height: 540, edge: null };
  }
  const width = Math.min(460, Math.max(MIN_PANEL_WIDTH, window.innerWidth - 48));
  const height = Math.min(620, Math.max(MIN_PANEL_HEIGHT, window.innerHeight - 96));
  return {
    x: Math.max(16, window.innerWidth - width - 24),
    y: Math.max(56, window.innerHeight - height - 54),
    width,
    height,
    edge: 'right',
  };
}

function clampPanelFrame(frame: PanelFrame): PanelFrame {
  if (typeof window === 'undefined') return frame;
  const width = Math.min(MAX_PANEL_WIDTH, Math.max(MIN_PANEL_WIDTH, frame.width));
  const height = Math.min(MAX_PANEL_HEIGHT, Math.max(MIN_PANEL_HEIGHT, frame.height));
  const maxX = Math.max(0, window.innerWidth - width);
  const maxY = Math.max(40, window.innerHeight - height);
  let x = Math.min(maxX, Math.max(0, frame.x));
  let y = Math.min(maxY, Math.max(40, frame.y));
  let horizontalEdge: Extract<SnapEdge, 'left' | 'right'> | null = null;
  let verticalEdge: Extract<SnapEdge, 'top' | 'bottom'> | null = null;

  if (x <= EDGE_STICK_PX) {
    x = 0;
    horizontalEdge = 'left';
  } else if (maxX - x <= EDGE_STICK_PX) {
    x = maxX;
    horizontalEdge = 'right';
  }

  if (y <= 40 + EDGE_STICK_PX) {
    y = 40;
    verticalEdge = 'top';
  } else if (maxY - y <= EDGE_STICK_PX) {
    y = maxY;
    verticalEdge = 'bottom';
  }

  const edge: SnapEdge = verticalEdge && horizontalEdge ? `${verticalEdge}-${horizontalEdge}` : horizontalEdge ?? verticalEdge;
  return { x, y, width, height, edge };
}

function messageId(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function BuildWorkbenchPage({ runtime }: BuildWorkbenchPageProps) {
  const [panelOpen, setPanelOpen] = useState(false);
  const [panelMinimized, setPanelMinimized] = useState(false);
  const [panelFrame, setPanelFrame] = useState<PanelFrame>(() => clampPanelFrame(initialPanelFrame()));
  const [dragState, setDragState] = useState<DragState | null>(null);
  const [activeTemplate, setActiveTemplate] = useState('raw');
  const [previewDoc, setPreviewDoc] = useState(() => previewDocumentFor('raw'));
  const [rollbackStack, setRollbackStack] = useState<string[]>([]);
  const [previewStatus, setPreviewStatus] = useState<'idle' | 'ready' | 'error'>('idle');
  const [previewFinding, setPreviewFinding] = useState('isolated');
  const [previewCrashCount, setPreviewCrashCount] = useState(0);
  const [previewHeartbeatAt, setPreviewHeartbeatAt] = useState<number | null>(null);
  const [activePanelTab, setActivePanelTab] = useState<BuildPanelTab>('chat');
  const [activeProjectId, setActiveProjectId] = useState(BUILD_PROJECT_SYSTEMS[0].id);
  const [workspace, setWorkspace] = useState<BuildWorkspaceModel | null>(null);
  const [workspaceFinding, setWorkspaceFinding] = useState('loading');
  const [messages, setMessages] = useState<BuildMessage[]>([
    {
      id: 'builder-boot',
      role: 'builder',
      text: 'Build surface ready. Preview is sandboxed; execution routes are gated.',
    },
  ]);
  const [prompt, setPrompt] = useState('');
  const [listening, setListening] = useState(false);
  const previewRef = useRef<HTMLIFrameElement | null>(null);
  const lastGoodPreviewDocRef = useRef(previewDoc);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  useEffect(() => {
    const handleResize = () => setPanelFrame((frame) => clampPanelFrame(frame));
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const route = ((runtime as IonCockpitViewModel & { build_workspace_route?: string }).build_workspace_route || '/cockpit/build/workspace.json');
    setWorkspaceFinding('loading');
    fetch(route, { headers: { Accept: 'application/json' }, cache: 'no-store', signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`workspace_${response.status}`);
        return response.json() as Promise<BuildWorkspaceModel>;
      })
      .then((payload) => {
        setWorkspace(payload);
        setWorkspaceFinding(payload.verdict || (payload.ok ? 'ready' : 'projected'));
      })
      .catch((error) => {
        if (controller.signal.aborted) return;
        setWorkspaceFinding(error instanceof Error ? error.message : 'workspace_unavailable');
      });
    return () => controller.abort();
  }, [runtime]);

  useEffect(() => {
    if (!dragState) return undefined;
    const handlePointerMove = (event: globalThis.PointerEvent) => {
      if (event.pointerId !== dragState.pointerId) return;
      const dx = event.clientX - dragState.originX;
      const dy = event.clientY - dragState.originY;
      setPanelFrame(() => {
        if (dragState.mode === 'resize') {
          return clampPanelFrame({
            ...dragState.frame,
            width: dragState.frame.width + dx,
            height: dragState.frame.height + dy,
            edge: null,
          });
        }
        return clampPanelFrame({
          ...dragState.frame,
          x: dragState.frame.x + dx,
          y: dragState.frame.y + dy,
          edge: null,
        });
      });
    };
    const handlePointerUp = (event: globalThis.PointerEvent) => {
      if (event.pointerId === dragState.pointerId) setDragState(null);
    };
    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);
    window.addEventListener('pointercancel', handlePointerUp);
    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      window.removeEventListener('pointercancel', handlePointerUp);
    };
  }, [dragState]);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (previewRef.current?.contentWindow && event.source !== previewRef.current.contentWindow) return;
      const data = event.data;
      if (!data || typeof data !== 'object' || data.source !== 'ion-build-preview') return;
      if (data.type === 'heartbeat') {
        setPreviewHeartbeatAt(Date.now());
      }
      if (data.type === 'ready') {
        setPreviewStatus('ready');
        setPreviewFinding('ready');
        setPreviewHeartbeatAt(Date.now());
        lastGoodPreviewDocRef.current = previewDoc;
      }
      if (data.type === 'error') {
        setPreviewStatus('error');
        setPreviewCrashCount((count) => count + 1);
        setPreviewFinding(String(data.message || 'preview_error').slice(0, 160));
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [previewDoc]);

  useEffect(() => {
    if (previewStatus === 'error') return undefined;
    const timer = window.setInterval(() => {
      if (!previewHeartbeatAt) return;
      if (Date.now() - previewHeartbeatAt <= 6500) return;
      setPreviewStatus('error');
      setPreviewCrashCount((count) => count + 1);
      setPreviewFinding('preview_heartbeat_timeout');
    }, 2500);
    return () => window.clearInterval(timer);
  }, [previewHeartbeatAt, previewStatus]);

  const workspaceModes = workspace?.agent_tool_control?.modes ?? [];
  const workspaceTools = workspace?.agent_tool_control?.tool_contracts ?? [];
  const projectSystems = useMemo(
    () => (workspace?.project_systems?.length ? workspace.project_systems : BUILD_PROJECT_SYSTEMS),
    [workspace],
  );
  useEffect(() => {
    if (!projectSystems.length) return;
    if (!projectSystems.some((project) => project.id === activeProjectId)) {
      setActiveProjectId(projectSystems[0].id);
    }
  }, [activeProjectId, projectSystems]);
  const template = useMemo(() => {
    const projected = workspaceModes.find((item) => item.id === activeTemplate);
    const local = BUILD_TEMPLATES.find((item) => item.id === activeTemplate) ?? BUILD_TEMPLATES[0];
    return projected ? { ...local, kind: projected.kind || local.kind, summary: projected.summary || local.summary, deps: projected.deps ?? local.deps } : local;
  }, [activeTemplate, workspaceModes]);
  const activeProject = useMemo(() => projectSystems.find((item) => item.id === activeProjectId) ?? projectSystems[0] ?? BUILD_PROJECT_SYSTEMS[0], [activeProjectId, projectSystems]);
  const builderAgentChat = workspace?.builder_agent_chat ?? fallbackBuilderAgentChat(workspace);
  const activeModeTools = useMemo(
    () => workspaceTools.filter((tool) => tool.mode_ids?.includes(activeTemplate)).slice(0, 12),
    [activeTemplate, workspaceTools],
  );
  const voiceAvailable = typeof window !== 'undefined'
    && Boolean((window as BrowserSpeechWindow).SpeechRecognition || (window as BrowserSpeechWindow).webkitSpeechRecognition);
  const ttsAvailable = typeof window !== 'undefined' && 'speechSynthesis' in window;
  const panelStyle: CSSProperties = {
    left: panelFrame.x,
    top: panelFrame.y,
    width: panelFrame.width,
    height: panelMinimized ? 58 : panelFrame.height,
  };

  const startDrag = (event: PointerEvent<HTMLElement>, mode: DragMode) => {
    event.preventDefault();
    setPanelMinimized(false);
    setDragState({
      mode,
      pointerId: event.pointerId,
      originX: event.clientX,
      originY: event.clientY,
      frame: panelFrame,
    });
  };

  const loadTemplate = (templateId: string) => {
    setRollbackStack((current) => [previewDoc, ...current].slice(0, 12));
    setActiveTemplate(templateId);
    setPreviewStatus('idle');
    setPreviewFinding('loading');
    setPreviewDoc(previewDocumentFor(templateId));
  };

  const rollback = () => {
    setRollbackStack((current) => {
      const [previous, ...rest] = current;
      if (!previous) return current;
      setPreviewDoc(previous);
      setPreviewStatus('idle');
      setPreviewFinding('rolled_back');
      return rest;
    });
  };

  const restoreLastGoodPreview = () => {
    setRollbackStack((current) => [previewDoc, ...current].slice(0, 12));
    setPreviewDoc(lastGoodPreviewDocRef.current);
    setPreviewStatus('idle');
    setPreviewFinding('restored_last_good');
    setPreviewHeartbeatAt(null);
  };

  const resetSandbox = () => {
    setRollbackStack((current) => [previewDoc, ...current].slice(0, 12));
    setActiveTemplate('raw');
    setPreviewDoc(previewDocumentFor('raw'));
    setPreviewStatus('idle');
    setPreviewFinding('reset');
  };

  const submitPrompt = () => {
    const text = prompt.trim();
    if (!text) return;
    setMessages((current) => [
      ...current,
      { id: messageId('operator'), role: 'operator', text },
      {
        id: messageId('system'),
        role: 'system',
        text: 'Captured locally. Codex builder execution needs a gated action route before it can mutate source.',
      },
    ]);
    setPrompt('');
  };

  const toggleSpeech = () => {
    if (!voiceAvailable || typeof window === 'undefined') return;
    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
      return;
    }
    const SpeechRecognition = (window as BrowserSpeechWindow).SpeechRecognition || (window as BrowserSpeechWindow).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results || [])
        .map((result: any) => result?.[0]?.transcript || '')
        .join(' ')
        .trim();
      if (transcript) setPrompt(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  };

  const speakLast = () => {
    if (!ttsAvailable || typeof window === 'undefined') return;
    const last = [...messages].reverse().find((message) => message.role !== 'operator')?.text;
    if (!last) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(last));
  };

  const openPanel = () => {
    setPanelOpen(true);
    setPanelMinimized(false);
  };

  return (
    <BuildPageErrorBoundary>
      <section className="ion-build-workbench" aria-label="Build workbench">
        <iframe
          ref={previewRef}
          className={`ion-build-preview is-${previewStatus}`}
          key={previewDoc}
          sandbox="allow-scripts"
          srcDoc={previewDoc}
          title="Build preview sandbox"
        />
        {previewStatus === 'error' ? (
          <div className="ion-build-preview-recovery" role="status">
            <b>PREVIEW CRASH ISOLATED</b>
            <span>{previewFinding}</span>
            <button type="button" onClick={restoreLastGoodPreview}>RESTORE LAST GOOD</button>
          </div>
        ) : null}

        <button className={`ion-build-launcher${panelOpen && !panelMinimized ? ' is-hidden' : ''}`} onClick={openPanel} type="button" aria-label="Open Codex builder">
          <AssistantIcon />
        </button>

        {panelOpen ? (
          <aside className={`ion-build-chat-panel is-edge-${panelFrame.edge ?? 'free'}${panelMinimized ? ' is-minimized' : ''}`} style={panelStyle} aria-label="Codex CLI builder panel">
            <div className="ion-build-edge-field" aria-hidden="true" />
            <header className="ion-build-chat-head" onPointerDown={(event) => startDrag(event, 'move')}>
              <div className="ion-build-chat-title">
                <CodexIcon />
                <div>
                  <b>CODEX BUILDER</b>
                  <span>{template.kind} / {previewFinding}</span>
                </div>
              </div>
              <div className="ion-build-chat-actions" onPointerDown={(event) => event.stopPropagation()}>
                <button type="button" onClick={() => setPanelMinimized((value) => !value)} aria-label={panelMinimized ? 'Expand builder panel' : 'Minimize builder panel'}>{panelMinimized ? <RunIcon /> : <StopIcon />}</button>
                <button type="button" onClick={() => setPanelOpen(false)} aria-label="Close builder panel"><CloseIcon /></button>
              </div>
            </header>

            {!panelMinimized ? (
              <>
                <div className="ion-build-modebar" aria-label="Builder work mode">
                  {BUILD_TEMPLATES.map((item) => (
                    <button
                      aria-label={item.label}
                      className={item.id === activeTemplate ? 'is-active' : undefined}
                      key={item.id}
                      onClick={() => loadTemplate(item.id)}
                      title={`${item.label}: ${item.summary}`}
                      type="button"
                    >
                      {item.icon}
                    </button>
                  ))}
                </div>

                <div className="ion-build-capability-rail">
                  <StatusPill icon={<CheckIcon />} label={previewStatus.toUpperCase()} />
                  <StatusPill icon={<WorkSurfaceIcon />} label="IFRAME" />
                  <StatusPill icon={<ToolsIcon />} label={runtime.runtime?.status ?? 'runtime'} />
                  <StatusPill icon={<AssistantIcon />} label={workspace?.codex_queue_control?.active_process_running ? 'CODEX LIVE' : (previewCrashCount ? `CRASH ${previewCrashCount}` : (voiceAvailable ? 'STT' : 'NO STT'))} />
                </div>

                <BuildModeToolRail tools={activeModeTools} fallbackFinding={workspaceFinding} />
                <BuildAgentCognitionStrip agentChat={builderAgentChat} />

                <div className="ion-build-panel-tabs" aria-label="Builder panel tabs">
                  <button className={activePanelTab === 'chat' ? 'is-active' : undefined} onClick={() => setActivePanelTab('chat')} type="button">CHAT</button>
                  <button className={activePanelTab === 'agent' ? 'is-active' : undefined} onClick={() => setActivePanelTab('agent')} type="button">AGENT</button>
                  <button className={activePanelTab === 'tools' ? 'is-active' : undefined} onClick={() => setActivePanelTab('tools')} type="button">TOOLS</button>
                  <button className={activePanelTab === 'projects' ? 'is-active' : undefined} onClick={() => setActivePanelTab('projects')} type="button">PROJECTS</button>
                </div>

                <div className="ion-build-panel-body">
                  {activePanelTab === 'chat' ? (
                    <div className="ion-build-chat-view">
                      <BuildAgentCommandStrip activeTemplate={activeTemplate} workspace={workspace} workspaceFinding={workspaceFinding} />
                      <div className="ion-build-chat-log" aria-live="polite">
                        {messages.map((message) => (
                          <article className={`ion-build-message is-${message.role}`} key={message.id}>
                            <span>{message.role}</span>
                            <p>{message.text}</p>
                          </article>
                        ))}
                      </div>
                    </div>
                  ) : activePanelTab === 'agent' ? (
                    <BuildAgentMindView agentChat={builderAgentChat} />
                  ) : activePanelTab === 'tools' ? (
                    <BuildModeToolsView activeTemplate={activeTemplate} tools={activeModeTools} workspace={workspace} fallbackFinding={workspaceFinding} />
                  ) : (
                    <BuildProjectsView activeProject={activeProject} activeProjectId={activeProjectId} agentChat={builderAgentChat} onSelectProject={setActiveProjectId} projects={projectSystems} />
                  )}
                </div>

                <div className="ion-build-sandbox-actions">
                  <button type="button" onClick={resetSandbox}>RESET</button>
                  <button type="button" onClick={rollback} disabled={!rollbackStack.length}>ROLLBACK</button>
                  <button type="button" onClick={speakLast} disabled={!ttsAvailable}>TTS</button>
                  <button type="button" onClick={toggleSpeech} disabled={!voiceAvailable}>{listening ? 'STOP MIC' : 'STT'}</button>
                </div>

                <footer className="ion-build-composer">
                  <textarea
                    aria-label="Builder prompt"
                    onChange={(event) => setPrompt(event.target.value)}
                    onKeyDown={(event) => {
                      if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') submitPrompt();
                    }}
                    placeholder="Ask the builder"
                    rows={3}
                    value={prompt}
                  />
                  <button type="button" onClick={submitPrompt} disabled={!prompt.trim()} aria-label="Send prompt"><RunIcon /></button>
                </footer>

                <button className="ion-build-resize-handle" onPointerDown={(event) => startDrag(event, 'resize')} type="button" aria-label="Resize builder panel" />
              </>
            ) : null}
          </aside>
        ) : null}
      </section>
    </BuildPageErrorBoundary>
  );
}

function BuildAgentCognitionStrip({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const lanes = agentChat.lanes ?? [];
  const visible = lanes.slice(0, 8);
  const activity = agentChat.activity ?? {};
  const swarm = agentChat.specialist_swarm;
  return (
    <div className="ion-build-agent-cognition-strip" aria-label="Builder agent cognition lanes">
      <div className="ion-build-agent-cognition-head">
        <span>BUILDER AGENT</span>
        <b>{agentChat.verdict ?? 'PROJECTED'}</b>
        <small>{agentChat.standard_codex_chat_affected === false && agentChat.standard_codex_chat_write_blocked !== false ? 'BUILD ONLY' : 'CHECK SCOPE'}</small>
      </div>
      <div className="ion-build-agent-mini-lanes">
        {visible.map((lane) => (
          <span className={`is-${safeBuildClass(lane.id)}`} key={lane.id} title={lane.role}>
            <b>{lane.label}</b>
            <small>{lane.status} / {lane.count ?? 0}</small>
          </span>
        ))}
      </div>
      <div className="ion-build-agent-queue-proof">
        <span><b>QUEUE</b>{String(activity.queued_request_count ?? 0)}</span>
        <span><b>RUNS</b>{String(activity.active_run_count ?? 0)}</span>
        <span><b>SWARM</b>{String(swarm?.specialists?.length ?? 0)}</span>
      </div>
    </div>
  );
}

function BuildAgentMindView({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const lanes = agentChat.lanes ?? [];
  const rules = agentChat.escalation_rules ?? [];
  const proof = agentChat.proof_ladder ?? [];
  const authority = agentChat.authority ?? {};
  const contract = agentChat.panel_contract ?? {};
  return (
    <div className="ion-build-agent-mind-view">
      <header className="ion-build-mode-inspector">
        <span>{agentChat.surface ?? 'build_page_builder_chat'}</span>
        <b>{agentChat.verdict ?? 'BUILDER_AGENT_PROJECTED'}</b>
        <small>{agentChat.queue_surface_namespace ? `queue: ${agentChat.queue_surface_namespace}` : (contract.preview_isolation ? `preview: ${String(contract.preview_isolation)}` : 'isolated build panel')}</small>
      </header>

      <BuildAgentLifecycleView agentChat={agentChat} />

      <section className="ion-build-agent-lane-grid" aria-label="Builder agent lanes">
        {lanes.map((lane) => (
          <article className={`ion-build-agent-lane is-${safeBuildClass(lane.id)}`} key={lane.id}>
            <header>
              <span>{lane.tier}</span>
              <b>{lane.label}</b>
              <small>{lane.status} / {lane.count ?? 0}</small>
            </header>
            <p>{lane.role}</p>
            <div>
              {(lane.allowed_outputs ?? []).slice(0, 3).map((item) => <code key={item}>{item}</code>)}
            </div>
          </article>
        ))}
      </section>

      <BuildAgentSwarmView agentChat={agentChat} />
      <BuildAgentCapsuleView agentChat={agentChat} />
      <BuildAgentInterventionView agentChat={agentChat} />

      <section className="ion-build-agent-grid">
        <article>
          <b>ESCALATION</b>
          {rules.map((rule, index) => (
            <span key={String(rule.id ?? index)}>
              {String(rule.from ?? '')} {'->'} {String(rule.to ?? '')} / {Array.isArray(rule.when) ? rule.when.join(' ') : String(rule.when ?? '')}
            </span>
          ))}
        </article>
        <article>
          <b>PROOF LADDER</b>
          <div className="ion-build-agent-proof-ladder">
            {proof.map((step) => <code key={step}>{step}</code>)}
          </div>
        </article>
        <article>
          <b>AUTHORITY</b>
          <span>production {String(Boolean(authority.production_authority))}</span>
          <span>live exec {String(Boolean(authority.live_execution_authority))}</span>
          <span>accepted state {String(Boolean(authority.accepted_state_authority))}</span>
          <span>secrets {String(Boolean(authority.secrets_authority))}</span>
          <span>hidden reasoning {String(Boolean(authority.raw_hidden_reasoning_exposed))}</span>
          <span>standard codex chat {String(Boolean(authority.standard_codex_chat_mutation))}</span>
        </article>
      </section>

      <BuildAgentSafetyView agentChat={agentChat} />
    </div>
  );
}

function BuildAgentLifecycleView({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const packet = agentChat.message_packet_schema ?? {};
  const lifecycle = agentChat.response_lifecycle ?? [];
  const bus = agentChat.cognition_bus ?? {};
  const busLanes = stringArray(bus.lanes, 10);
  const requiredFields = stringArray(packet.required_fields, 8);
  return (
    <section className="ion-build-agent-bus" aria-label="Builder cognition bus">
      <article>
        <b>PACKET SCHEMA</b>
        <span>{String(packet.schema_id ?? 'message_packet_projected')}</span>
        <div>{requiredFields.map((field) => <code key={field}>{field}</code>)}</div>
      </article>
      <article>
        <b>COGNITION BUS</b>
        <span>{String(bus.bus_id ?? 'build_builder_agent_bus')}</span>
        <div>{busLanes.map((lane) => <code key={lane}>{lane}</code>)}</div>
      </article>
      <article>
        <b>LIFECYCLE</b>
        {lifecycle.slice(0, 8).map((step, index) => (
          <span key={String(step.id ?? index)}>{String(step.owner ?? '')} / {String(step.receipt ?? step.id ?? '')}</span>
        ))}
      </article>
    </section>
  );
}

function BuildAgentSwarmView({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const swarm = agentChat.specialist_swarm;
  const specialists = swarm?.specialists ?? [];
  if (!specialists.length) return null;
  return (
    <section className="ion-build-agent-swarm" aria-label="Builder specialist swarm">
      <header>
        <span>{swarm?.posture ?? 'visible_fanout_fanin'}</span>
        <b>SPECIALIST SWARM</b>
        <small>hidden spawn {String(Boolean(swarm?.hidden_spawn_allowed))}</small>
      </header>
      <div>
        {specialists.slice(0, 9).map((specialist) => (
          <article key={specialist.id}>
            <span>{specialist.trigger ?? 'bounded'}</span>
            <b>{specialist.label}</b>
            <small>{specialist.status ?? 'available'}</small>
            <p>{specialist.role}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function BuildAgentCapsuleView({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const capsuleSystem = agentChat.context_capsule_system;
  const capsules = capsuleSystem?.capsules ?? [];
  if (!capsules.length) return null;
  return (
    <section className="ion-build-agent-capsules" aria-label="Builder context capsules">
      <header>
        <span>{capsuleSystem?.posture ?? 'per_project_candidate_capsules'}</span>
        <b>CONTEXT CAPSULES</b>
        <small>{capsules.length} projected</small>
      </header>
      <div>
        {capsules.slice(0, 4).map((capsule) => (
          <article key={String(capsule.project_id ?? capsule.label)}>
            <span>{capsule.branch ?? 'projected'}</span>
            <b>{capsule.label ?? capsule.project_id ?? 'project'}</b>
            <small>{capsule.capsule_state ?? 'candidate'}</small>
            <div>{(capsule.artifact_slots ?? []).slice(0, 4).map((slot) => <code key={slot}>{slot}</code>)}</div>
          </article>
        ))}
      </div>
    </section>
  );
}

function BuildAgentInterventionView({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const intervention = agentChat.intervention_lane;
  const events = intervention?.event_types ?? [];
  if (!intervention) return null;
  return (
    <section className="ion-build-agent-interventions" aria-label="Builder intervention lane">
      <article>
        <b>INTERVENTION LANE</b>
        <span>{intervention.status ?? 'projected'} / late correction {String(Boolean(intervention.late_correction_allowed))}</span>
        <div>{events.slice(0, 6).map((event) => <code key={event}>{event}</code>)}</div>
      </article>
    </section>
  );
}

function BuildAgentSafetyView({ agentChat }: { agentChat: BuildBuilderAgentChat }) {
  const invariants = agentChat.safety_invariants ?? [];
  const toolMatrix = agentChat.tool_hook_matrix ?? {};
  return (
    <section className="ion-build-agent-safety" aria-label="Builder safety invariants">
      <article>
        <b>SAFETY INVARIANTS</b>
        {invariants.slice(0, 5).map((item, index) => (
          <span key={String(item.id ?? index)}>{item.assertion ?? item.id} / {item.proof}</span>
        ))}
      </article>
      <article>
        <b>TOOL HOOK MATRIX</b>
        <span>tools {String(toolMatrix.tool_count ?? 0)}</span>
        <span>disabled {stringArray(toolMatrix.disabled, 8).join(' ') || 'none'}</span>
        <span>forbidden {stringArray(toolMatrix.forbidden_capabilities, 8).join(' ')}</span>
      </article>
    </section>
  );
}

function BuildProjectsView({
  activeProject,
  activeProjectId,
  agentChat,
  onSelectProject,
  projects,
}: {
  activeProject: BuildProjectSystem;
  activeProjectId: string;
  agentChat: BuildBuilderAgentChat;
  onSelectProject: (projectId: string) => void;
  projects: BuildProjectSystem[];
}) {
  const capsules = agentChat.context_capsule_system?.capsules ?? [];
  const activeCapsule = capsules.find((capsule) => capsule.project_id === activeProject.id) ?? capsules[0];
  return (
    <div className="ion-build-projects-view">
      <div className="ion-build-project-list" aria-label="Build projects">
        {projects.map((project) => (
          <button className={project.id === activeProjectId ? 'is-active' : undefined} key={project.id} onClick={() => onSelectProject(project.id)} type="button">
            <b>{project.label}</b>
            <span>{project.status} / {project.branch}</span>
          </button>
        ))}
      </div>

      <div className="ion-build-project-detail">
        <header>
          <span>PROJECT SYSTEM</span>
          <b>{activeProject.label}</b>
        </header>

        <div className="ion-build-project-spine">
          <span><b>BRANCH</b>{activeProject.branch}</span>
          <span><b>DIFF</b>{activeProject.diff}</span>
          <span><b>CAPSULE</b>{activeProject.capsule}</span>
          <span><b>ROLLBACK</b>{activeProject.rollback}</span>
        </div>

        <div className="ion-build-project-lane-grid" aria-label="Project operations">
          {activeProject.lanes.map((lane) => (
            <article key={lane.id}>
              <span>{lane.label}</span>
              <b>{lane.value}</b>
              <small>{lane.state}</small>
            </article>
          ))}
        </div>

        <div className="ion-build-project-capsule">
          <b>CONTEXT CAPSULE</b>
          {(activeCapsule?.context_refs ?? ['HOT_CONTEXT', 'ACTIVE_CONTEXT_PACKAGE', 'DIFF RECEIPTS', 'SCREENSHOT PROOFS']).slice(0, 6).map((ref) => (
            <span key={ref}>{ref}</span>
          ))}
        </div>

        <div className="ion-build-project-evidence">
          <b>{activeProject.notes} NOTES / {activeProject.screenshots} SHOTS</b>
          {[...(activeCapsule?.evidence_refs ?? []), ...activeProject.evidence].slice(0, 8).map((item) => <span key={item}>{item}</span>)}
        </div>
      </div>
    </div>
  );
}

function BuildModeToolRail({ tools, fallbackFinding }: { tools: BuildToolContract[]; fallbackFinding: string }) {
  const visibleTools = tools.length ? tools.slice(0, 4) : [
    {
      tool_id: 'workspace_loading',
      label: fallbackFinding,
      control_class: 'projection',
      authority: 'read_only',
      status: 'projecting',
      description: 'Workspace projection status.',
    },
  ];
  return (
    <div className="ion-build-tool-rail" aria-label="Mode tool rail">
      {visibleTools.map((tool) => (
        <button className={`ion-build-tool-button is-${tool.status.replace(/[^a-z0-9_-]/gi, '_').toLowerCase()}`} disabled={tool.status === 'disabled'} key={tool.tool_id} title={tool.description} type="button">
          <b>{tool.label}</b>
          <span>{tool.authority}</span>
        </button>
      ))}
    </div>
  );
}

function BuildAgentCommandStrip({
  activeTemplate,
  workspace,
  workspaceFinding,
}: {
  activeTemplate: string;
  workspace: BuildWorkspaceModel | null;
  workspaceFinding: string;
}) {
  const queue = workspace?.codex_queue_control;
  const queued = queue?.queued_request_count ?? 0;
  const active = queue?.active_run_count ?? 0;
  return (
    <div className="ion-build-agent-command-strip" aria-label="Build agent command projection">
      <span><b>MODE</b>{activeTemplate}</span>
      <span><b>WORKSPACE</b>{workspace?.verdict ?? workspaceFinding}</span>
      <span><b>QUEUE</b>{queued} queued</span>
      <span><b>RUNS</b>{active} active</span>
    </div>
  );
}

function BuildModeToolsView({
  activeTemplate,
  tools,
  workspace,
  fallbackFinding,
}: {
  activeTemplate: string;
  tools: BuildToolContract[];
  workspace: BuildWorkspaceModel | null;
  fallbackFinding: string;
}) {
  const grouped = tools.reduce<Record<string, BuildToolContract[]>>((result, tool) => {
    const key = tool.control_class || 'tool';
    result[key] = [...(result[key] ?? []), tool];
    return result;
  }, {});
  const groups = Object.entries(grouped);
  return (
    <div className="ion-build-tools-view">
      <header className="ion-build-mode-inspector">
        <span>{activeTemplate}</span>
        <b>{workspace?.agent_tool_control?.write_confirmation_required ? 'GATED CONTROL' : fallbackFinding}</b>
        <small>{workspace?.agent_tool_control?.write_confirmation_token ?? 'read only projection'}</small>
      </header>
      {groups.length ? groups.map(([groupId, groupTools]) => (
        <section className="ion-build-tool-group" key={groupId}>
          <b>{groupId.replace(/_/g, ' ')}</b>
          {groupTools.map((tool) => (
            <article className="ion-build-tool-contract" key={tool.tool_id}>
              <header>
                <span>{tool.status}</span>
                <b>{tool.label}</b>
              </header>
              <p>{tool.description}</p>
              <div>
                <span>{tool.authority}</span>
                <span>{tool.next_gate ?? tool.endpoint ?? 'local'}</span>
              </div>
            </article>
          ))}
        </section>
      )) : (
        <section className="ion-build-tool-group">
          <b>projection</b>
          <article className="ion-build-tool-contract">
            <header><span>{fallbackFinding}</span><b>Workspace tools</b></header>
            <p>The mode tool contract is loading from the local cockpit projection.</p>
            <div><span>read_only</span><span>/cockpit/build/workspace.json</span></div>
          </article>
        </section>
      )}
    </div>
  );
}

function StatusPill({ icon, label }: { icon: ReactNode; label: string }) {
  return <span>{icon}<b>{label}</b></span>;
}

function fallbackBuilderAgentChat(workspace: BuildWorkspaceModel | null): BuildBuilderAgentChat {
  const queued = workspace?.codex_queue_control?.queued_request_count ?? 0;
  const active = workspace?.codex_queue_control?.active_run_count ?? 0;
  const toolCount = workspace?.agent_tool_control?.tool_contracts?.length ?? 0;
  return {
    schema_id: 'ion.build_workspace.builder_agent_chat.local_fallback.v0_1',
    verdict: 'BUILDER_AGENT_LOCAL_FALLBACK',
    surface: 'cockpit_build_page_builder_chat',
    standard_codex_chat_affected: false,
    build_only_packet_required: true,
    standard_codex_chat_write_blocked: true,
    queue_surface_namespace: 'build',
    preview_watchdog_ms: 6500,
    preview_csp_policy: 'iframe_srcdoc_sandbox_allow_scripts_no_same_origin',
    panel_contract: {
      preview_isolation: 'iframe_srcdoc_sandbox',
      chat_survives_preview_crash: true,
      panel_physics: 'move_resize_edge_snap_corner_snap',
    },
    lanes: [
      { id: 'spark', label: 'Spark', tier: 'fast_builder_carrier', status: 'ready', count: 0, role: 'Immediate builder conversation and mode routing.' },
      { id: 'deep', label: 'Deep', tier: 'review_and_plan', status: queued || active ? 'watching_queue' : 'ready', count: queued, role: 'Design review, dependency analysis, and work packet shaping.' },
      { id: 'arbiter', label: 'Arbiter', tier: 'critical_gate', status: 'gated', count: 0, role: 'Security and authority review for dangerous build moves.' },
      { id: 'sandbox', label: 'Sandbox', tier: 'crash_isolation', status: 'isolated', count: 1, role: 'Preview failure stays inside the iframe.' },
      { id: 'tools', label: 'Tools', tier: 'bounded_control', status: 'projected', count: toolCount, role: 'Mode-aware tool contracts.' },
      { id: 'specialists', label: 'Specialists', tier: 'visible_fanout', status: 'projected', count: active, role: 'Specialists surface as visible workpacks and receipts.' },
      { id: 'receipts', label: 'Receipts', tier: 'proof_ladder', status: 'armed', count: 0, role: 'Proof ladder for prompts, diffs, screenshots, rollback, and settlement.' },
      { id: 'interventions', label: 'Interventions', tier: 'late_correction_lane', status: 'armed', count: 0, role: 'Visible corrections and blocked-action notices.' },
    ],
    message_packet_schema: {
      schema_id: 'ion.build_workspace.builder_agent_message_packet.local_fallback.v0_1',
      required_fields: ['packet_id', 'surface', 'selected_project_id', 'mode_id', 'user_intent', 'risk_level', 'allowed_outputs', 'blocked_outputs'],
    },
    response_lifecycle: [
      { id: 'ingress', owner: 'spark', receipt: 'prompt_packet' },
      { id: 'deep_review', owner: 'deep', receipt: 'review_packet' },
      { id: 'intervention', owner: 'interventions', receipt: 'amendment_receipt' },
    ],
    cognition_bus: {
      bus_id: 'build_builder_agent_stratified_cognition_bus',
      lanes: ['spark_lane', 'deep_lane', 'arbiter_lane', 'evidence_lane', 'specialist_fanout_lane', 'receipt_lane', 'intervention_lane'],
    },
    specialist_swarm: {
      posture: 'visible_fanout_fanin',
      hidden_spawn_allowed: false,
      recursive_spawn_allowed: false,
      specialists: [
        { id: 'builder_architect', label: 'Builder Architect', trigger: 'architecture', status: 'available', role: 'Packet lifecycle and route shape.' },
        { id: 'security_arbiter', label: 'Security Arbiter', trigger: 'authority_sensitive', status: 'available', role: 'Authority and destructive action gates.' },
        { id: 'visual_proof_engineer', label: 'Visual Proof Engineer', trigger: 'visual_or_browser', status: 'available', role: 'Screenshot and console proof.' },
      ],
    },
    context_capsule_system: {
      posture: 'per_project_candidate_capsules',
      capsule_lifecycle: ['select_project', 'load_context', 'attach_prompt_packet', 'candidate_receipt'],
      capsules: [],
    },
    intervention_lane: {
      status: 'armed',
      late_correction_allowed: true,
      visible_to_operator: true,
      event_types: ['fast_reply_amended', 'deep_correction', 'arbiter_stop', 'tool_gate_block'],
    },
    tool_hook_matrix: {
      tool_count: toolCount,
      disabled: ['codex_tui_direct_control'],
      forbidden_capabilities: ['arbitrary_shell', 'raw_tui_key_injection', 'credential_access'],
    },
    safety_invariants: [
      { id: 'build_only', assertion: 'Builder-agent chat is hosted only by BuildWorkbenchPage.', proof: 'surface=cockpit_build_page_builder_chat' },
      { id: 'standard_codex_untouched', assertion: 'Standard Codex chat is not mutated.', proof: 'standard_codex_chat_affected=false' },
    ],
    escalation_rules: [
      { id: 'spark_to_deep', from: 'spark', to: 'deep', when: ['architecture', 'dependency', 'multi_file_change'] },
      { id: 'deep_to_arbiter', from: 'deep', to: 'arbiter', when: ['security', 'delete', 'deploy', 'secret'] },
    ],
    proof_ladder: ['prompt_packet', 'context_capsule', 'tool_contract', 'diff_preview', 'sandbox_visual', 'rollback_receipt'],
    activity: {
      queued_request_count: queued,
      active_run_count: active,
      tool_contract_count: toolCount,
    },
    authority: {
      production_authority: false,
      live_execution_authority: false,
      accepted_state_authority: false,
      secrets_authority: false,
      standard_codex_chat_mutation: false,
    },
  };
}

function safeBuildClass(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-|-$/g, '') || 'unknown';
}

function stringArray(value: unknown, limit = 12) {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item ?? '').trim()).filter(Boolean).slice(0, limit);
}

class BuildPageErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean; detail: string }> {
  state = { failed: false, detail: '' };

  static getDerivedStateFromError(error: unknown) {
    return { failed: true, detail: error instanceof Error ? error.message : 'build_page_error' };
  }

  render() {
    if (this.state.failed) {
      return (
        <section className="ion-build-workbench is-boundary-failed">
          <button type="button" onClick={() => this.setState({ failed: false, detail: '' })}>RESET BUILD SHELL</button>
          <code>{this.state.detail}</code>
        </section>
      );
    }
    return this.props.children;
  }
}

function previewDocumentFor(templateId: string) {
  const body = previewBodyFor(templateId);
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; background: #ffffff; color: #121212; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  * { box-sizing: border-box; }
  #stage { width: 100%; height: 100%; }
  canvas { display: block; width: 100%; height: 100%; }
  .site { min-height: 100%; display: grid; grid-template-rows: 56px minmax(0,1fr); }
  .site nav { display: flex; align-items: center; justify-content: space-between; padding: 0 28px; border-bottom: 1px solid #dedede; font-size: 12px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
  .site main { display: grid; place-items: center; padding: 32px; }
  .site h1 { max-width: 820px; font-size: 68px; line-height: .9; letter-spacing: 0; margin: 0; }
  .dashboard { min-height: 100%; display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); grid-auto-rows: minmax(140px,1fr); gap: 12px; padding: 18px; background: #f6f6f3; }
  .dash-card { border: 1px solid #d8d8d2; background: #fff; padding: 16px; display: grid; align-content: end; gap: 8px; }
  .dash-card b { font-size: 34px; }
  .dash-card span { font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
  .image-editor { height: 100%; display: grid; grid-template-rows: 44px minmax(0,1fr); background: #eeeeea; }
  .image-editor .bar { display: flex; align-items: center; gap: 8px; padding: 8px; border-bottom: 1px solid #d0d0ca; }
  .image-editor .tool { width: 28px; height: 28px; border: 1px solid #bdbdb7; background: white; }
  .image-editor .canvas { margin: 18px; background: white; border: 1px solid #d0d0ca; display: grid; place-items: center; }
  .raw-doc { min-height: 100%; display: grid; grid-template-columns: minmax(0,1fr) minmax(220px,.36fr); gap: 18px; padding: 24px; background: #fbfbf7; }
  .raw-doc main { display: grid; align-content: center; gap: 18px; min-width: 0; }
  .raw-doc h1 { max-width: 920px; font-size: 54px; line-height: .96; margin: 0; letter-spacing: 0; }
  .raw-doc p { max-width: 760px; margin: 0; font-size: 17px; line-height: 1.55; color: #333; }
  .raw-doc aside { display: grid; align-content: center; gap: 10px; min-width: 0; }
  .raw-card { min-height: 110px; border: 1px solid #d9d9d0; background: #fff; padding: 14px; display: grid; align-content: end; gap: 8px; }
  .raw-card b, .flow-node b, .docs-page b, .media-studio b { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }
  .raw-card span, .flow-node span, .docs-page span, .media-studio span { color: #555; font-size: 12px; line-height: 1.45; }
  .raw-orbit { width: min(44vw, 380px); aspect-ratio: 1; border-radius: 50%; background: conic-gradient(from 20deg, #111, #60ffc8, #f4f4ef, #111); animation: rawSpin 12s linear infinite; }
  .media-studio { height: 100%; display: grid; grid-template-columns: minmax(0,1fr) minmax(220px,.32fr); gap: 12px; padding: 18px; background: #efefeb; }
  .media-stage { background: #fff; border: 1px solid #d2d2ca; display: grid; place-items: center; min-width: 0; }
  .media-timeline { display: grid; align-content: stretch; gap: 10px; min-width: 0; }
  .media-timeline article { border: 1px solid #d2d2ca; background: #fff; padding: 12px; display: grid; gap: 8px; }
  .media-strip { height: 12px; background: linear-gradient(90deg, #111 0 22%, #60ffc8 22% 46%, #d7d7cf 46% 70%, #111 70%); }
  .flow { height: 100%; display: grid; grid-template-columns: minmax(0,1fr) minmax(260px,.36fr); gap: 14px; padding: 18px; background: #f7f7f2; }
  .flow-board { position: relative; min-width: 0; border: 1px solid #d6d6cd; background: radial-gradient(circle at 20px 20px, #e6e6dd 1px, transparent 1px) 0 0/22px 22px, #fff; overflow: hidden; }
  .flow-node { position: absolute; display: grid; gap: 5px; width: 150px; min-height: 68px; border: 1px solid #111; background: #fff; padding: 10px; box-shadow: 6px 6px 0 #60ffc8; }
  .flow-node.is-a { left: 8%; top: 18%; }
  .flow-node.is-b { left: 42%; top: 42%; }
  .flow-node.is-c { right: 8%; top: 18%; }
  .flow-line { position: absolute; height: 2px; background: #111; transform-origin: left center; }
  .flow-line.is-one { left: 24%; top: 34%; width: 28%; transform: rotate(18deg); }
  .flow-line.is-two { left: 56%; top: 48%; width: 27%; transform: rotate(-24deg); }
  .flow-side { display: grid; gap: 10px; align-content: start; min-width: 0; }
  .flow-side article { min-height: 96px; border: 1px solid #d6d6cd; background: #fff; padding: 12px; display: grid; align-content: end; gap: 8px; }
  .docs-page { height: 100%; display: grid; place-items: center; padding: 26px; background: #f1f1ed; }
  .docs-sheet { width: min(900px, 92vw); min-height: min(680px, 82vh); border: 1px solid #d5d5ce; background: #fff; padding: 42px; box-shadow: 0 22px 50px rgba(0,0,0,.1); display: grid; align-content: start; gap: 18px; }
  .docs-sheet h1 { font-family: Georgia, serif; font-size: 42px; line-height: 1.05; margin: 0; }
  .docs-equation { border: 1px solid #d5d5ce; background: #fafaf7; padding: 18px; text-align: center; font-family: Georgia, serif; font-size: 22px; }
  @keyframes rawSpin { to { transform: rotate(360deg); } }
</style>
</head>
<body>
<div id="stage">${body}</div>
<script>
  window.onerror = function(message) {
    parent.postMessage({ source: 'ion-build-preview', type: 'error', message: String(message) }, '*');
  };
	  window.onunhandledrejection = function(event) {
	    parent.postMessage({ source: 'ion-build-preview', type: 'error', message: String(event.reason || 'unhandled rejection') }, '*');
	  };
	  setInterval(function() {
	    parent.postMessage({ source: 'ion-build-preview', type: 'heartbeat', at: Date.now() }, '*');
	  }, 2000);
	  ${previewScriptFor(templateId)}
	  parent.postMessage({ source: 'ion-build-preview', type: 'ready' }, '*');
	</script>
</body>
</html>`;
}

function previewBodyFor(templateId: string) {
  switch (templateId) {
    case 'raw':
      return '<section class="raw-doc"><main><div class="raw-orbit"></div><h1>Raw ideas can become visual documents, animated notes, source-backed stories, or living drafts.</h1><p>This workspace starts as an expressive page where the builder can compose text, graphics, motion, citations, and artifacts without leaving the chat.</p></main><aside><article class="raw-card"><b>Sources</b><span>References, screenshots, and proof links live beside the draft.</span></article><article class="raw-card"><b>Motion</b><span>Small animations can explain structure without taking over the page.</span></article><article class="raw-card"><b>Style</b><span>The AI can shape the page while keeping receipts and rollback separate.</span></article></aside></section>';
    case 'app':
      return '<section class="site"><nav><b>Build</b><span>Draft Site</span></nav><main><h1>A clean app surface can start from here.</h1></main></section>';
    case 'world':
      return '<canvas id="scene" aria-label="Build canvas"></canvas>';
    case 'media':
      return '<section class="media-studio"><div class="media-stage"><canvas id="paint" width="820" height="520"></canvas></div><div class="media-timeline"><article><b>Image</b><span>Layer stack and brush surface.</span><div class="media-strip"></div></article><article><b>Video</b><span>Timeline, clips, captions, frames.</span><div class="media-strip"></div></article><article><b>Gallery</b><span>Shots, references, exports.</span><div class="media-strip"></div></article></div></section>';
    case 'flow':
      return '<section class="flow"><div class="flow-board"><div class="flow-line is-one"></div><div class="flow-line is-two"></div><article class="flow-node is-a"><b>Input</b><span>Data, files, user intent.</span></article><article class="flow-node is-b"><b>Agent</b><span>Transform, inspect, branch.</span></article><article class="flow-node is-c"><b>Output</b><span>Charts, reports, actions.</span></article></div><aside class="flow-side"><article><b>Runs</b><span>12</span></article><article><b>Signals</b><span>84%</span></article><article><b>Rollback</b><span>ready</span></article></aside></section>';
    case 'docs':
      return '<section class="docs-page"><article class="docs-sheet"><b>Draft Documentation</b><h1>A polished writing surface for long-form technical work.</h1><p>Use it for specs, guides, math, diagrams, references, and AI-assisted revision history.</p><div class="docs-equation">\\u2207 \\u00b7 F = \\u03c1 / \\u03b5\\u2080</div><span>Context capsules, citations, screenshots, and proof receipts stay attached to the project.</span></article></section>';
    default:
      return '';
  }
}

function previewScriptFor(templateId: string) {
  if (templateId === 'world') {
    return `
      const canvas = document.getElementById('scene');
      const ctx = canvas.getContext('2d');
      function size(){ canvas.width = innerWidth * devicePixelRatio; canvas.height = innerHeight * devicePixelRatio; }
      addEventListener('resize', size); size();
      let t = 0;
      function loop(){
        t += 0.018;
        const w = canvas.width, h = canvas.height;
        ctx.fillStyle = '#f7f7f2'; ctx.fillRect(0,0,w,h);
        ctx.save(); ctx.translate(w/2,h/2); ctx.rotate(t);
        ctx.fillStyle = '#161616'; ctx.fillRect(-90,-90,180,180);
        ctx.strokeStyle = '#60ffc8'; ctx.lineWidth = 8; ctx.strokeRect(-90,-90,180,180);
        ctx.rotate(-t * 1.7);
        ctx.strokeStyle = '#111'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(0,0,210,0,Math.PI*2); ctx.stroke();
        ctx.fillStyle = '#60ffc8'; ctx.beginPath(); ctx.arc(Math.cos(t*2)*210,Math.sin(t*2)*210,24,0,Math.PI*2); ctx.fill();
        ctx.restore();
        requestAnimationFrame(loop);
      }
      loop();
    `;
  }
  if (templateId === 'media') {
    return `
      const canvas = document.getElementById('paint');
      const ctx = canvas.getContext('2d');
      const grd = ctx.createLinearGradient(0,0,820,520);
      grd.addColorStop(0,'#f8f8f4'); grd.addColorStop(1,'#dff8ef');
      ctx.fillStyle = grd; ctx.fillRect(0,0,820,520);
      ctx.fillStyle = '#111'; ctx.fillRect(110,110,250,210);
      ctx.fillStyle = '#60ffc8'; ctx.beginPath(); ctx.arc(550,260,110,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle = '#111'; ctx.lineWidth = 10; ctx.strokeRect(70,70,680,380);
    `;
  }
  return '';
}
