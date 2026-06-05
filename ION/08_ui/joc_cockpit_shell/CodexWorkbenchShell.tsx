import { useEffect, useLayoutEffect, useMemo, useRef, useState, type CSSProperties, type DragEvent, type FormEvent, type KeyboardEvent as ReactKeyboardEvent, type MouseEvent as ReactMouseEvent, type PointerEvent as ReactPointerEvent, type ReactNode, type UIEvent } from 'react';
import { createPortal } from 'react-dom';
import type {
  IonCockpitViewModel,
  IonCodexConversationArchive,
  IonCodexConversationArchiveSession,
  IonCodexGitRollback,
  JocCommsMessage,
  JocCommsThread,
} from './ionRuntimeCockpitTypes';
import {
  AgentsIcon,
  ArchiveIcon,
  AssistantIcon,
  AuthorityIcon,
  BranchIcon,
  CheckIcon,
  CloseIcon,
  ComposeIcon,
  ConnectionsIcon,
  CodexIcon,
  DocsIcon,
  EvidenceIcon,
  EmailIcon,
  GithubIcon,
  GmailIcon,
  IdeIcon,
  LensIcon,
  PauseIcon,
  ProjectsIcon,
  QueueIcon,
  RollbackIcon,
  RunIcon,
  SessionsIcon,
  SettingsIcon,
  StatusIcon,
  SupabaseIcon,
  WebhookIcon,
} from './icons';

export type CodexTabId = 'chat' | 'ion' | 'ide' | 'archive' | 'context' | 'settings' | 'hooks' | 'skills' | 'tools' | 'traces' | 'queue';
type CodexChatLaneId = 'codex_general' | 'ion_system';
type CoreLeftDrawerId = 'compose' | 'files' | 'sessions' | 'context' | 'projects' | 'agents';
type ConnectionId = 'gmail' | 'supabase' | 'github' | 'email' | 'webhook';
type ConnectionDrawerId = `connection:${ConnectionId}`;
type LeftDrawerId = CoreLeftDrawerId | 'connections' | ConnectionDrawerId;
type RightDrawerId = 'branches' | 'rollback' | 'status' | 'messageQueue' | 'assistant' | 'ide' | 'evidence' | 'authority' | 'settings' | 'missionProfile';
type ArchiveViewId = 'recent' | 'active' | 'projects' | 'models' | 'packets';
type ChatDrawerPageId = 'active' | 'all' | 'find' | 'groups' | 'work' | 'attached';
type ChatDrawerGroupViewId = 'projects' | 'models' | 'agents' | 'context';
type ChatViewMode = 'live' | 'archive';
type ChatCommandPanelId = '' | 'agent' | 'context' | 'attachments' | 'queue' | 'staged' | 'diffs' | 'model' | 'carrier';
type EditDrawerViewId = 'current' | 'checkpoints' | 'archive' | 'receipts';
type AssistantDrawerViewId = 'response' | 'thinking' | 'edits' | 'runs' | 'proof' | 'context' | 'events' | 'raw';
type CodexAtlasLensId = 'trunks' | 'branches' | 'chats' | 'timeline' | 'files';
type CodexAtlasNodeKind = 'trunk' | 'branch' | 'chat' | 'queue' | 'timeline' | 'file';
type CodexAtlasTone = 'ready' | 'watch' | 'blocked' | 'muted' | 'active';
type CodexAtlasNode = {
  id: string;
  kind: CodexAtlasNodeKind;
  title: string;
  detail: string;
  meta: string;
  ref: string;
  parent?: string;
  tone: CodexAtlasTone;
  icon: ReactNode;
};
type AgentModeId = 'auto' | 'prompt' | 'plan' | 'implement' | 'review' | 'queue';
type ThinkingModeId = 'auto' | 'low' | 'medium' | 'high' | 'xhigh';
type ArchiveGroup = {
  id: string;
  title: string;
  sessions: IonCodexConversationArchiveSession[];
};
type OpenChatTab = {
  id: string;
  kind: 'archive';
  sessionId: string;
  title: string;
  subtitle?: string;
  projectLabel?: string;
  model?: string;
  isCurrent?: boolean;
  windowStart?: number;
  openedAt: string;
  lastOpenedAt?: string;
  lastClosedAt?: string;
  lastViewedAt: string;
};
type ContextSystemInventoryRow = {
  agent: Record<string, unknown>;
  agentId: string;
  roleId: string;
  domainId: string;
  displayName: string;
  status: string;
  packageClass: string;
  packageStrategy: string;
  cardPath: string;
  cardExists: boolean;
  contextRefCount: number;
  variationTags: string[];
  mappedBindings: Array<Record<string, unknown>>;
  mappedFreshChats: Array<Record<string, unknown>>;
  mappedOpenTabs: OpenChatTab[];
  activeForCurrentChat: boolean;
};
type PersistedOpenChatTabs = {
  activeTabId: string;
  tabs: OpenChatTab[];
};
type ChatHistoryMeta = {
  lastOpenedAt?: string;
  lastClosedAt?: string;
};
type ChatDrawerPrefs = {
  hideShortChats: boolean;
  shortChatMaxUserPrompts: number;
};
type ChatHistorySortId = 'last_message' | 'first_message' | 'last_opened' | 'last_closed';
type ChatHistoryEntry = {
  session: IonCodexConversationArchiveSession;
  title: string;
  timestamp: number;
  detail: string;
};
type DrawerSessionPreviewItem = {
  role: string;
  text: string;
  timestamp?: string;
};
type ChatTabHoverInfo = {
  sessionId: string;
  left: number;
  top: number;
  width: number;
};
type MissionCommsThreadDetail = {
  thread: JocCommsThread | null;
  messages: JocCommsMessage[];
  source: string;
  loadedAt: string;
};
type MissionTimelineEvent = {
  id: string;
  kind: string;
  title: string;
  status: string;
  detail: string;
  source: string;
  at: string;
  tone: 'ready' | 'active' | 'watch' | 'blocked' | 'empty';
};
type CodexChatAgentIdentity = {
  displayName: string;
  roleId: string;
  instanceId: string;
  carrier: string;
  domain: string;
  source: string;
  detail: string;
  title: string;
};
type CodexSubwayMapNode = {
  id: string;
  lane: 'context' | 'diff' | 'queue' | 'carrier';
  label: string;
  value: string;
  detail: string;
  meta: string;
  x: number;
  y: number;
  tone: 'ready' | 'watch' | 'blocked' | 'empty' | 'active';
  action: 'context' | 'attachments' | 'queue' | 'rollback' | 'carrier';
};
type CodexContextMapView = 'subway' | 'timeline';
type CodexTimelineDensity = 'standard' | 'super' | 'ultra';
type CodexContextMapSize = 'mini' | 'mid' | 'full';
type CodexContextAgentLens = 'card' | 'package' | 'proof' | 'files';
type CodexTimelineEvent = {
  id: string;
  track: 'context' | 'diff' | 'tools' | 'queue' | 'carrier' | 'evidence';
  label: string;
  value: string;
  detail: string;
  meta: string;
  start: number;
  span: number;
  tone: 'context-read' | 'diff-add' | 'diff-remove' | 'diff-change' | 'tool' | 'queue' | 'carrier' | 'evidence' | 'blocked';
  texture: 'solid' | 'stripe' | 'hatch' | 'dot' | 'dash' | 'mesh';
  action: CodexSubwayMapNode['action'];
};
type CodexChatTimelineTrackId = 'diff' | 'chat' | 'context' | 'reads' | 'tools' | 'agents' | 'queue';
type CodexChatTimelineTone =
  | 'diff-add'
  | 'diff-remove'
  | 'diff-change'
  | 'chat-user'
  | 'chat-assistant'
  | 'context-read'
  | 'read'
  | 'tool'
  | 'agent'
  | 'queue'
  | 'blocked'
  | 'evidence';
type CodexChatTimelineClip = {
  id: string;
  track: CodexChatTimelineTrackId;
  label: string;
  value: string;
  detail: string;
  start: number;
  span: number;
  targetIndex: number;
  tone: CodexChatTimelineTone;
  texture: CodexTimelineEvent['texture'];
};
type CodexChatTimelineModel = {
  frames: number;
  clips: CodexChatTimelineClip[];
  summary: {
    turnCount: number;
    diffCount: number;
    toolCount: number;
    readCount: number;
    agentCount: number;
  };
};
type CodexChatScrollTrackId = 'edit' | 'thread' | 'work';
type CodexChatScrollSequenceMarker = {
  id: string;
  scrollTrack: CodexChatScrollTrackId;
  targetIndex: number;
  tone: CodexChatTimelineTone;
  detail: string;
  top: number;
};
type CodexChatScrollSequenceWindow = {
  total: number;
  oldest: number;
  newest: number;
};
type IonTruthTone = 'ready' | 'active' | 'watch' | 'blocked' | 'empty';
const CODEX_CONTEXT_MAP_SIZES: CodexContextMapSize[] = ['mini', 'mid', 'full'];
const CODEX_CONTEXT_TIMELINE_DENSITY_BY_SIZE: Record<CodexContextMapSize, CodexTimelineDensity> = {
  mini: 'ultra',
  mid: 'super',
  full: 'standard',
};
const CODEX_CHAT_TIMELINE_MIN_FRAMES = 48;
const CODEX_CHAT_TIMELINE_MAX_FRAMES = 96;
const CODEX_CONTEXT_MAP_SIZE_LABELS: Record<CodexContextMapSize, string> = {
  mini: 'MINI',
  mid: 'MID',
  full: 'FULL',
};
type CodexMessageQueueItem = {
  id: string;
  title: string;
  message: string;
  mode: ExecutionModeId;
  laneId: string;
  contextRefs?: string[];
  createdAt: string;
  updatedAt: string;
  lastDispatchedAt?: string;
};
type CodexMessageQueueGroup = {
  id: string;
  name: string;
  items: CodexMessageQueueItem[];
  createdAt: string;
  updatedAt: string;
};
type PersistedCodexMessageQueues = {
  activeGroupId: string;
  items: CodexMessageQueueItem[];
  groups: CodexMessageQueueGroup[];
};
type PendingChatTurn = {
  clientId: string;
  message: string;
  mode: ExecutionModeId;
  laneId: CodexChatLaneId;
  agentMode: AgentModeId;
  selectedModel: string;
  thinkingMode: ThinkingModeId;
  contextRefs: string[];
  targetSessionId?: string;
  targetSessionTitle?: string;
  newCodexSession?: boolean;
  codexSessionTransport?: 'raw_cli' | 'app_server';
  createdAt: string;
  status: 'sending' | 'settled' | 'failed';
  error?: string;
  settledAt?: string;
  assistantPreview?: string;
  responseStatus?: string;
  responseRunPath?: string;
  responseMode?: string;
  responseSurface?: string;
  responseThreadId?: string;
};
type ServerUserTurnReceipt = {
  message: string;
  createdAt: string;
  clientId?: string;
  turnId?: string;
  hasServerWork?: boolean;
};
type PendingChatActivitySnapshot = {
  workerActive: boolean;
  workerStatus: string;
  workerDuration: string;
  queuedRequestCount: number;
  responseRun?: Record<string, unknown>;
};
type ArchiveBufferDirection = 'older' | 'newer';
type ArchiveTranscriptBuffer = {
  direction: ArchiveBufferDirection;
  sessionId: string;
  startIndex: number;
  endIndex: number;
  items: Array<Record<string, unknown>>;
  projection: IonCodexConversationArchive;
  createdAt: string;
};
type ArchiveBufferScrollAdjustment = {
  direction: ArchiveBufferDirection;
  beforeHeight: number;
  beforeTop: number;
  key: string;
};
type ArchiveVirtualLoadRequest = {
  sessionId: string;
  startIndex: number;
  scrollTop: number;
};
type ArchiveTranscriptBlock =
  | { kind: 'message'; item: Record<string, unknown>; key: string }
  | {
      kind: 'work';
      key: string;
      items: Array<Record<string, unknown>>;
      assistantItems: Array<Record<string, unknown>>;
      toolItems: Array<Record<string, unknown>>;
      contextItems: Array<Record<string, unknown>>;
      eventItems: Array<Record<string, unknown>>;
      editItems: Array<Record<string, unknown>>;
      thinkingItems: Array<Record<string, unknown>>;
      runItems: Array<Record<string, unknown>>;
      proofItems: Array<Record<string, unknown>>;
      rawItems: Array<Record<string, unknown>>;
    };
type ArchiveConversationGroup = {
  group_id: string;
  user_turn: Record<string, unknown>;
  assistant_turns: Array<Record<string, unknown>>;
  execution_turns: Array<Record<string, unknown>>;
  context_turns: Array<Record<string, unknown>>;
  other_turns: Array<Record<string, unknown>>;
  return_records: Array<Record<string, unknown>>;
  turn_trace: Record<string, unknown> & { events: Array<Record<string, unknown>> };
};
type BranchSource = {
  kind: 'current_turn' | 'archive_session';
  title?: string;
  objective?: string;
  prompt?: string;
  turnId?: unknown;
  sessionId?: string;
  role?: string;
  message?: string;
  messageSha256?: string;
};
type CodexFileTreeEntry = {
  path: string;
  kind: 'file' | 'dir';
  bytes?: number;
};
type SpeechRecognitionAlternativeLike = {
  transcript: string;
  confidence?: number;
};
type SpeechRecognitionResultLike = {
  isFinal: boolean;
  length: number;
  [index: number]: SpeechRecognitionAlternativeLike | undefined;
};
type SpeechRecognitionResultListLike = {
  length: number;
  [index: number]: SpeechRecognitionResultLike | undefined;
};
type SpeechRecognitionEventLike = Event & {
  resultIndex: number;
  results: SpeechRecognitionResultListLike;
};
type SpeechRecognitionErrorEventLike = Event & {
  error?: string;
  message?: string;
};
type SpeechRecognitionLike = EventTarget & {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onstart: ((event: Event) => void) | null;
  onend: ((event: Event) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEventLike) => void) | null;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
};
type SpeechRecognitionConstructorLike = new () => SpeechRecognitionLike;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructorLike;
    webkitSpeechRecognition?: SpeechRecognitionConstructorLike;
  }
}

export const codexWorkbenchTabs: Array<{ id: CodexTabId; label: string }> = [
  { id: 'chat', label: 'CHAT' },
  { id: 'ion', label: 'ION' },
  { id: 'ide', label: 'IDE' },
  { id: 'archive', label: 'PAST' },
  { id: 'context', label: 'CONTEXT' },
  { id: 'settings', label: 'SETTINGS' },
  { id: 'hooks', label: 'HOOKS' },
  { id: 'skills', label: 'SKILLS' },
  { id: 'tools', label: 'TOOLS' },
  { id: 'traces', label: 'TRACES' },
  { id: 'queue', label: 'QUEUE' },
];

type IconBarItem<T extends string> = { id: T; icon: ReactNode; title: string; className?: string };
type ConnectionProfile = {
  id: ConnectionId;
  label: string;
  shortLabel: string;
  icon: ReactNode;
  category: string;
  mode: string;
  scopes: string[];
  storage: string;
};

const coreLeftDrawers: Array<IconBarItem<CoreLeftDrawerId>> = [
  { id: 'compose', icon: <ComposeIcon />, title: 'compose' },
  { id: 'files', icon: <DocsIcon />, title: 'context atlas' },
  { id: 'sessions', icon: <SessionsIcon />, title: 'past chats' },
  { id: 'context', icon: <LensIcon />, title: 'context' },
  { id: 'projects', icon: <ProjectsIcon />, title: 'projects' },
  { id: 'agents', icon: <AgentsIcon />, title: 'agents' },
];

const connectionProfiles: ConnectionProfile[] = [
  {
    id: 'gmail',
    label: 'Gmail',
    shortLabel: 'gmail',
    icon: <GmailIcon />,
    category: 'mail',
    mode: 'oauth connector draft',
    scopes: ['mail.readonly', 'mail.send', 'labels'],
    storage: 'no token storage in cockpit',
  },
  {
    id: 'supabase',
    label: 'Supabase',
    shortLabel: 'supabase',
    icon: <SupabaseIcon />,
    category: 'database',
    mode: 'project ref connector draft',
    scopes: ['read model', 'edge functions', 'storage metadata'],
    storage: 'vault-backed key required outside UI',
  },
  {
    id: 'github',
    label: 'GitHub',
    shortLabel: 'github',
    icon: <GithubIcon />,
    category: 'repo',
    mode: 'app/token connector draft',
    scopes: ['issues', 'pull requests', 'repository metadata'],
    storage: 'no token storage in cockpit',
  },
  {
    id: 'email',
    label: 'Email',
    shortLabel: 'email',
    icon: <EmailIcon />,
    category: 'mail',
    mode: 'smtp/imap connector draft',
    scopes: ['inbox', 'send', 'archive'],
    storage: 'server-side secret required',
  },
  {
    id: 'webhook',
    label: 'Webhook',
    shortLabel: 'webhook',
    icon: <WebhookIcon />,
    category: 'automation',
    mode: 'http endpoint connector draft',
    scopes: ['inbound events', 'signed outbound calls'],
    storage: 'signed endpoint required',
  },
];

const rightDrawers: Array<{ id: RightDrawerId; icon: ReactNode; title: string }> = [
  { id: 'branches', icon: <BranchIcon />, title: 'branches' },
  { id: 'rollback', icon: <RollbackIcon />, title: 'edits' },
  { id: 'status', icon: <StatusIcon />, title: 'status' },
  { id: 'messageQueue', icon: <QueueIcon />, title: 'message queues' },
  { id: 'assistant', icon: <AssistantIcon />, title: 'assistant' },
  { id: 'missionProfile', icon: <AgentsIcon />, title: 'mission profile' },
  { id: 'ide', icon: <IdeIcon />, title: 'ide' },
  { id: 'evidence', icon: <EvidenceIcon />, title: 'evidence' },
  { id: 'authority', icon: <AuthorityIcon />, title: 'gates' },
  { id: 'settings', icon: <SettingsIcon />, title: 'settings' },
];

const executionModes = [
  { id: 'auto', label: 'AUTO' },
  { id: 'respond_only', label: 'PROMPT' },
  { id: 'queue_for_codex', label: 'QUEUE' },
  { id: 'queue_and_start', label: 'RUN' },
] as const;
type ExecutionModeId = (typeof executionModes)[number]['id'];

const agentModeOptions: Array<{ id: AgentModeId; label: string; executionMode: ExecutionModeId; detail: string }> = [
  { id: 'auto', label: 'Auto', executionMode: 'auto', detail: 'Codex chat engine selects reply, queue, or work routing from the prompt.' },
  { id: 'prompt', label: 'Prompt', executionMode: 'respond_only', detail: 'Direct response in the live chat.' },
  { id: 'plan', label: 'Plan', executionMode: 'respond_only', detail: 'Planning and review posture before work is queued.' },
  { id: 'implement', label: 'Implement', executionMode: 'queue_and_start', detail: 'Stage and run bounded implementation work.' },
  { id: 'review', label: 'Review', executionMode: 'respond_only', detail: 'Code-review and proof-focused response posture.' },
  { id: 'queue', label: 'Queue', executionMode: 'queue_for_codex', detail: 'Stage messages into the Codex queue drawer.' },
];

const thinkingModeOptions: Array<{ id: ThinkingModeId; label: string }> = [
  { id: 'auto', label: 'Auto' },
  { id: 'low', label: 'Low' },
  { id: 'medium', label: 'Medium' },
  { id: 'high', label: 'High' },
  { id: 'xhigh', label: 'XHigh' },
];

const WRITE_CONFIRMATION_TOKEN = 'ION_BOUNDED_WRITE_CONFIRMED';
const ARCHIVE_TRANSCRIPT_CHUNK_SIZE = 500;
const ARCHIVE_FAST_OPEN_CHUNK_SIZE = 180;
const ARCHIVE_PREFETCH_MIN_PX = 520;
const ARCHIVE_PREFETCH_VIEWPORT_MULTIPLIER = 1.35;
const ARCHIVE_PREFETCH_SCROLL_RATIO = 0.9;
const ARCHIVE_PREFETCH_DESPAWN_VIEWPORT_MULTIPLIER = 2.2;
const ARCHIVE_BUFFER_PROMOTION_PX = 32;
const ARCHIVE_VIRTUAL_ITEM_PX = 148;
const ARCHIVE_VIRTUAL_OVERSCAN_ITEMS = 80;
const LIVE_BOTTOM_STICKY_PX = 140;
const CHAT_TAB_STORAGE_KEY = 'ion.codexWorkbench.openChatTabs.v1';
const CHAT_TITLE_OVERRIDES_STORAGE_KEY = 'ion.codexWorkbench.chatTitleOverrides.v1';
const CHAT_HISTORY_META_STORAGE_KEY = 'ion.codexWorkbench.chatHistoryMeta.v1';
const CHAT_FAVORITES_STORAGE_KEY = 'ion.codexWorkbench.favoriteChats.v1';
const CHAT_DRAWER_PREFS_STORAGE_KEY = 'ion.codexWorkbench.chatDrawerPrefs.v2';
const MESSAGE_QUEUE_STORAGE_KEY = 'ion.codexWorkbench.messageQueues.v1';
const CONTEXT_REFS_STORAGE_KEY = 'ion.codexWorkbench.contextRefs.v1';
const CONNECTIONS_STORAGE_KEY = 'ion.codexWorkbench.connections.v1';
const CODEX_LIVE_SESSION_ID = 'live:codex';
const CODEX_CURRENT_SESSION_TITLE = 'Current Codex Session';
const FILE_PICKER_ROOTS = ['ION', 'ION/08_ui', 'ION/04_packages/kernel', 'browser_extension', 'Needs_Routed', 'Cosmos'];
const STT_LANGUAGES = [
  { value: 'en-US', label: 'EN US' },
  { value: 'en-CA', label: 'EN CA' },
  { value: 'en-GB', label: 'EN UK' },
  { value: 'fr-CA', label: 'FR CA' },
  { value: 'es-US', label: 'ES US' },
] as const;

const archiveViews: Array<{ id: ArchiveViewId; label: string; icon: ReactNode }> = [
  { id: 'recent', label: 'RECENT', icon: <SessionsIcon /> },
  { id: 'active', label: 'MOST ACTIVE', icon: <StatusIcon /> },
  { id: 'projects', label: 'PROJECTS', icon: <ProjectsIcon /> },
  { id: 'models', label: 'MODELS', icon: <CodexIcon /> },
  { id: 'packets', label: 'WORK PACKETS', icon: <QueueIcon /> },
];

const chatDrawerPages: Array<{ id: ChatDrawerPageId; label: string; icon: ReactNode }> = [
  { id: 'active', label: 'ACTIVE', icon: <StatusIcon /> },
  { id: 'all', label: 'ALL', icon: <SessionsIcon /> },
  { id: 'find', label: 'FIND', icon: <LensIcon /> },
  { id: 'groups', label: 'GROUPS', icon: <ProjectsIcon /> },
  { id: 'work', label: 'WORK', icon: <QueueIcon /> },
  { id: 'attached', label: 'ATTACHED', icon: <ArchiveIcon /> },
];

const chatDrawerGroupViews: Array<{ id: ChatDrawerGroupViewId; label: string }> = [
  { id: 'projects', label: 'Projects' },
  { id: 'models', label: 'Models' },
  { id: 'agents', label: 'Agents' },
  { id: 'context', label: 'Context' },
];

const chatHistorySortOptions: Array<{ id: ChatHistorySortId; label: string }> = [
  { id: 'last_message', label: 'Last message' },
  { id: 'first_message', label: 'First message' },
  { id: 'last_opened', label: 'Last opened' },
  { id: 'last_closed', label: 'Last closed' },
];

export function CodexWorkbenchShell({
  runtime,
  onRuntimeRefresh,
  activeTab: controlledActiveTab,
  hideSubtabs = false,
  onActiveTabChange,
  surface = 'full',
  ideContextBridge,
}: {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
  activeTab?: CodexTabId;
  hideSubtabs?: boolean;
  onActiveTabChange?: (tab: CodexTabId) => void;
  surface?: 'full' | 'chat-cell';
  ideContextBridge?: Record<string, unknown>;
}) {
  const [localActiveTab, setLocalActiveTab] = useState<CodexTabId>('chat');
  const [leftDrawer, setLeftDrawer] = useState<LeftDrawerId>('sessions');
  const [rightDrawer, setRightDrawer] = useState<RightDrawerId>('assistant');
  const [leftDrawerOpen, setLeftDrawerOpen] = useState(() => {
    if (surface === 'chat-cell') return false;
    if ((controlledActiveTab ?? 'chat') !== 'chat') return false;
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return true;
    return window.matchMedia('(min-width: 1200px)').matches;
  });
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [chatArchiveDrawerPrimed, setChatArchiveDrawerPrimed] = useState(() => (controlledActiveTab ?? 'chat') === 'chat');
  const [connectionState, setConnectionState] = useState<Record<ConnectionId, boolean>>(() => loadPersistedConnectionState());
  const [executionMode, setExecutionMode] = useState<ExecutionModeId>('auto');
  const [composer, setComposer] = useState('');
  const [messageQueueState, setMessageQueueState] = useState<PersistedCodexMessageQueues>(() => loadPersistedCodexMessageQueues());
  const [messageQueueDraftTitle, setMessageQueueDraftTitle] = useState('');
  const [messageQueueDraftBody, setMessageQueueDraftBody] = useState('');
  const [messageQueueDraftMode, setMessageQueueDraftMode] = useState<ExecutionModeId>('queue_for_codex');
  const [editingMessageQueueItemId, setEditingMessageQueueItemId] = useState('');
  const [messageQueueEditTitle, setMessageQueueEditTitle] = useState('');
  const [messageQueueEditBody, setMessageQueueEditBody] = useState('');
  const [messageQueueEditMode, setMessageQueueEditMode] = useState<ExecutionModeId>('queue_for_codex');
  const [messageQueueGroupName, setMessageQueueGroupName] = useState('');
  const [messageQueueDraggingId, setMessageQueueDraggingId] = useState('');
  const [messageQueueDispatchingId, setMessageQueueDispatchingId] = useState('');
  const [queuePaused, setQueuePaused] = useState(false);
  const [queueInsertOpen, setQueueInsertOpen] = useState(false);
  const [fileTreeRoot, setFileTreeRoot] = useState('ION');
  const [fileTreeDepth, setFileTreeDepth] = useState(3);
  const [fileTreeRefreshVersion, setFileTreeRefreshVersion] = useState(0);
  const [fileTreeSearch, setFileTreeSearch] = useState('');
  const [contextAtlasLens, setContextAtlasLens] = useState<CodexAtlasLensId>('trunks');
  const [contextAtlasQuery, setContextAtlasQuery] = useState('');
  const [selectedContextAtlasNodeId, setSelectedContextAtlasNodeId] = useState('');
  const [fileTreeEntries, setFileTreeEntries] = useState<CodexFileTreeEntry[]>([]);
  const [fileTreeBusy, setFileTreeBusy] = useState(false);
  const [fileTreeError, setFileTreeError] = useState('');
  const [selectedContextRefs, setSelectedContextRefs] = useState<string[]>(() => loadPersistedContextRefs());
  const [commandPanel, setCommandPanel] = useState<ChatCommandPanelId>('');
  const [contextMapView, setContextMapView] = useState<CodexContextMapView>('timeline');
  const [contextMapOpen, setContextMapOpen] = useState(true);
  const [contextMapSize, setContextMapSize] = useState<CodexContextMapSize>('mini');
  const [contextTimelineLegendOpen, setContextTimelineLegendOpen] = useState(false);
  const [selectedContextSubwayNodeId, setSelectedContextSubwayNodeId] = useState('');
  const [selectedContextAgentId, setSelectedContextAgentId] = useState('');
  const [contextAgentLens, setContextAgentLens] = useState<CodexContextAgentLens>('card');
  const [contextMapBottomBarSlot, setContextMapBottomBarSlot] = useState<HTMLElement | null>(null);
  const [agentMode, setAgentMode] = useState<AgentModeId>('auto');
  const [selectedModelOverride, setSelectedModelOverride] = useState('');
  const [thinkingMode, setThinkingMode] = useState<ThinkingModeId>('auto');
  const [sendError, setSendError] = useState('');
  const [actionNotice, setActionNotice] = useState('');
  const [sending, setSending] = useState(false);
  const [pendingChatTurns, setPendingChatTurns] = useState<PendingChatTurn[]>([]);
  const [pendingClockTick, setPendingClockTick] = useState(0);
  const [agentStopBusy, setAgentStopBusy] = useState(false);
  const [sttSupported, setSttSupported] = useState(false);
  const [sttListening, setSttListening] = useState(false);
  const [sttLanguage, setSttLanguage] = useState('en-US');
  const [sttInterim, setSttInterim] = useState('');
  const [sttStatus, setSttStatus] = useState('voice idle');
  const [archiveView, setArchiveView] = useState<ArchiveViewId>('recent');
  const [archiveSearch, setArchiveSearch] = useState('');
  const [chatDrawerPage, setChatDrawerPage] = useState<ChatDrawerPageId>('active');
  const [chatDrawerIdSearch, setChatDrawerIdSearch] = useState('');
  const [chatDrawerGroupView, setChatDrawerGroupView] = useState<ChatDrawerGroupViewId>('projects');
  const [archiveProjection, setArchiveProjection] = useState<IonCodexConversationArchive | null>(null);
  const [archiveBusy, setArchiveBusy] = useState(false);
  const [archiveBackgroundBusy, setArchiveBackgroundBusy] = useState(false);
  const [archiveAction, setArchiveAction] = useState('');
  const [archivePrefetch, setArchivePrefetch] = useState<ArchiveTranscriptBuffer | null>(null);
  const [archivePrefetchBusy, setArchivePrefetchBusy] = useState<ArchiveBufferDirection | ''>('');
  const [rollbackProjection, setRollbackProjection] = useState<IonCodexGitRollback | null>(null);
  const [rollbackBusy, setRollbackBusy] = useState(false);
  const [rollbackPreview, setRollbackPreview] = useState<Record<string, unknown> | null>(null);
  const [editDrawerView, setEditDrawerView] = useState<EditDrawerViewId>('current');
  const [assistantDrawerView, setAssistantDrawerView] = useState<AssistantDrawerViewId>('response');
  const [contextSurfaceId, setContextSurfaceId] = useState('capsule');
  const [contextEventId, setContextEventId] = useState('');
  const [openChatTabs, setOpenChatTabs] = useState<OpenChatTab[]>(() => loadPersistedOpenChatTabs().tabs);
  const [activeChatTabId, setActiveChatTabId] = useState(() => loadPersistedOpenChatTabs().activeTabId);
  const [chatTitleOverrides, setChatTitleOverrides] = useState<Record<string, string>>(() => loadPersistedChatTitleOverrides());
  const [chatHistoryMeta, setChatHistoryMeta] = useState<Record<string, ChatHistoryMeta>>(() => loadPersistedChatHistoryMeta());
  const [favoriteChatIds, setFavoriteChatIds] = useState<string[]>(() => loadPersistedFavoriteChatIds());
  const [chatDrawerPrefs, setChatDrawerPrefs] = useState<ChatDrawerPrefs>(() => loadPersistedChatDrawerPrefs());
  const [chatHistoryMenuOpen, setChatHistoryMenuOpen] = useState(false);
  const [chatHistorySort, setChatHistorySort] = useState<ChatHistorySortId>('last_message');
  const [selectedSessionId, setSelectedSessionId] = useState('');
  const [newCodexSessionRequested, setNewCodexSessionRequested] = useState(false);
  const [expandedDrawerSessionIds, setExpandedDrawerSessionIds] = useState<Set<string>>(() => new Set());
  const [renamingChatId, setRenamingChatId] = useState('');
  const [renameDraft, setRenameDraft] = useState('');
  const [chatTabHoverInfo, setChatTabHoverInfo] = useState<ChatTabHoverInfo | null>(null);
  const [missionCommsThreads, setMissionCommsThreads] = useState<JocCommsThread[]>([]);
  const [selectedMissionThreadId, setSelectedMissionThreadId] = useState('');
  const [missionCommsThreadDetail, setMissionCommsThreadDetail] = useState<MissionCommsThreadDetail>({
    thread: null,
    messages: [],
    source: '',
    loadedAt: '',
  });
  const [missionCommsLoading, setMissionCommsLoading] = useState(false);
  const [missionCommsThreadLoading, setMissionCommsThreadLoading] = useState(false);
  const [missionCommsError, setMissionCommsError] = useState('');
  const [chatViewMode, setChatViewMode] = useState<ChatViewMode>('live');
  const [chatTimelineScrollRatio, setChatTimelineScrollRatio] = useState(1);
  const [newCapsuleChatBusy, setNewCapsuleChatBusy] = useState(false);
  const transcriptRef = useRef<HTMLDivElement | null>(null);
  const archiveTranscriptRef = useRef<HTMLDivElement | null>(null);
  const livePinnedToBottomRef = useRef(true);
  const liveNewestKeyRef = useRef('');
  const archiveScrollTargetRef = useRef<'top' | 'bottom'>('bottom');
  const archiveProgrammaticScrollUntilRef = useRef(0);
  const archiveLastScrollTopRef = useRef(0);
  const archivePrefetchKeyRef = useRef('');
  const archiveRequestKeyRef = useRef('');
  const archiveBufferRenderAdjustmentRef = useRef<ArchiveBufferScrollAdjustment | null>(null);
  const archiveBufferRemovalAdjustmentRef = useRef<ArchiveBufferScrollAdjustment | null>(null);
  const archiveBufferPromotionTopRef = useRef<number | null>(null);
  const archiveVirtualRestoreTopRef = useRef<number | null>(null);
  const archiveVirtualPendingLoadRef = useRef<ArchiveVirtualLoadRequest | null>(null);
  const archiveVirtualLoadingKeyRef = useRef('');
  const missionCommsThreadRequestRef = useRef('');
  const archiveSuppressNextAutoScrollRef = useRef(false);
  const archiveBufferPixelSizeRef = useRef(0);
  const messageQueueDraggingIdRef = useRef('');
  const messageQueuePointerCleanupRef = useRef<(() => void) | null>(null);
  const speechRecognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const activeTab = controlledActiveTab ?? localActiveTab;
  const filePickerOpen = leftDrawerOpen && leftDrawer === 'files';
  const connectedConnections = useMemo(() => connectionProfiles.filter((profile) => connectionState[profile.id]), [connectionState]);
  const leftRailItems = useMemo<Array<IconBarItem<LeftDrawerId>>>(() => [
    ...coreLeftDrawers,
    ...connectedConnections.map((profile, index) => ({
      id: connectionDrawerId(profile.id),
      icon: profile.icon,
      title: profile.label,
      className: ['is-connected-connector', index === 0 ? 'is-bottom-stack-start' : ''].filter(Boolean).join(' '),
    })),
    {
      id: 'connections',
      icon: <ConnectionsIcon />,
      title: 'connections',
      className: ['is-connections-button', connectedConnections.length === 0 ? 'is-bottom-stack-start' : ''].filter(Boolean).join(' '),
    },
  ], [connectedConnections]);
  const setActiveCodexTab = (tab: CodexTabId) => {
    if (controlledActiveTab === undefined) setLocalActiveTab(tab);
    onActiveTabChange?.(tab);
  };

  useEffect(() => {
    if (activeTab !== 'context') return;
    setLeftDrawerOpen(false);
    setRightDrawerOpen(false);
  }, [activeTab]);

  const chat = runtime.codex_capsule_chat;
  const cli = runtime.codex_cli_workbench;
  const mcpSummary = record(runtime.chatgpt_browser_mcp);
  const archive = archiveProjection ?? runtime.codex_conversation_archive;
  const rollback = rollbackProjection ?? runtime.codex_git_rollback;
  const memory = record(chat?.memory_visualization);
  const chatMemory = record(chat?.memory);
  const archiveAttachments = records(chatMemory.archive_attachments);
  const selectedContextRefCount = selectedContextRefs.length;
  const totalAttachmentCount = archiveAttachments.length + selectedContextRefCount;
  const cliSummary = record(cli?.summary);
  const settings = record(cli?.settings);
  const hooks = record(cli?.hooks);
  const skills = record(cli?.skills);
  const tools = record(cli?.tools);
  const project = record(cli?.project_context);
  const agents = record(cli?.agents_and_roles);
  const queue = record(runtime.chatgpt_browser_mcp?.codex_queue_runner);
  const queueTelemetry = record(queue.live_worker_telemetry);
  const queueTelemetryRun = record(queueTelemetry.run);
  const workerActive = Boolean(queue.active_process_running || queueTelemetry.active_process_running || chat?.runner_active);
  const cancelableWorkerActive = Boolean(queue.active_process_running || queueTelemetry.active_process_running || queueTelemetryRun.active_process_running);
  const queueDispatchActive = Boolean(messageQueueDispatchingId);
  const workerElapsedSeconds = durationSeconds(queueTelemetry.elapsed_seconds || queueTelemetryRun.elapsed_seconds || queue.start_request_age_seconds);
  const workerDuration = workerElapsedSeconds > 0 ? formatElapsedDuration(workerElapsedSeconds) : '';
  const workerStatus = text(queueTelemetry.phase_status || queueTelemetry.run_status || queue.verdict || chat?.latest_response_status, 'idle');
  const defaultModelLabel = text(record(chat?.response_carrier).selected_model || record(record(settings.project_config)).default_model || queueTelemetry.model || queueTelemetryRun.model || 'codex', 'codex');
  const activeModelLabel = selectedModelOverride || defaultModelLabel;
  const activeModelChoiceLabel = selectedModelOverride ? activeModelLabel : `auto / ${defaultModelLabel}`;
  const thinkingModeOption = thinkingModeOptions.find((option) => option.id === thinkingMode) ?? thinkingModeOptions[0];
  const queuedRequestCount = numberValue(queue.queued_request_count);
  const diffCheckpointCount = numberValue(record(rollback?.summary).checkpoint_count);
  const currentWorktree = record(rollback?.current_worktree);
  const currentWorktreeStats = record(currentWorktree.diff_stats);
  const currentEditCount = numberValue(currentWorktreeStats.file_count)
    || records(currentWorktree.file_edits).length
    || numberValue(record(rollback?.current_git).scoped_porcelain_count);
  const capsuleHealth = capsuleHealthState(record(chat?.capsule));
  const rolePhaseContract = record(agents.role_phase_contract);
  const agentIdentity = resolveCodexChatAgentIdentity(runtime, queueTelemetry, queueTelemetryRun, rolePhaseContract, agents);
  const agentModeOption = agentModeOptions.find((option) => option.id === agentMode) ?? agentModeOptions[0];
  const executionModeOption = executionModes.find((option) => option.id === executionMode) ?? executionModes[0];
  const queueTone = queueDispatchActive ? 'playing' : queuePaused ? 'paused' : queuedRequestCount || messageQueueState.items.length ? 'ready' : 'empty';
  const promptStatusLabel = sending
    ? executionMode === 'auto'
      ? 'routing'
      : executionMode === 'respond_only'
        ? 'prompting'
        : executionMode === 'queue_and_start'
          ? 'running'
          : 'queuing'
    : workerActive
      ? `can prompt / working ${workerDuration || 'now'}`
      : 'ready';
  const primarySendLabel = sending ? promptStatusLabel : executionModeOption.label;
  const primarySendTitle = executionMode === 'auto'
    ? 'Send with auto route selection. The chat engine can answer directly or route bounded implementation prompts into the Codex queue.'
    : executionMode === 'respond_only'
      ? 'Send as direct response mode; the model replies and the result appears in the current chat.'
      : executionMode === 'queue_and_start'
        ? 'Queue this message and request a bounded Codex runner start when the bridge permits it.'
        : 'Queue this message as bounded Codex work without starting the runner.';
  const queuePlayLabel = queueDispatchActive ? 'PAUSE' : queuePaused ? 'RESUME' : 'PLAY';
  const queuePlayDisabled = Boolean(sending && !queueDispatchActive)
    || (!queueDispatchActive && !composer.trim() && !messageQueueState.items.length)
    || (workerActive && !queueDispatchActive);
  const composerQueueDisabled = Boolean(sending || messageQueueDispatchingId || !composer.trim());
  const contextMapSizeIndex = CODEX_CONTEXT_MAP_SIZES.indexOf(contextMapSize);
  const modelOptions = useMemo(
    () => modelOptionList(defaultModelLabel, archive?.sessions ?? [], chat, queueTelemetry, queueTelemetryRun),
    [archive, chat, defaultModelLabel, queueTelemetry, queueTelemetryRun],
  );
  const cliContext = record(cli?.context);
  const contextSurfaces = records(cliContext.surfaces);
  const contextTimeline = record(cliContext.timeline);
  const contextTimelineSummary = record(contextTimeline.summary);
  const contextTimelineSurfaces = records(contextTimeline.surfaces);
  const contextTimelineEvents = records(contextTimeline.timeline);
  const contextTimelineLanes = records(contextTimeline.lanes);
  const contextBoundaries = records(contextTimeline.boundaries);
  const contextTopology = record(contextTimeline.topology);
  const agentControlPlane = record(runtime.agent_control_plane);
  const contextAgentRows = records(agentControlPlane.agents);
  const contextAgentSummary = record(agentControlPlane.summary);
  const contextAgentDiagnostics = record(agentControlPlane.diagnostics);
  const agentControlChain = record(agentControlPlane.chain);
  const agentControlComms = record(agentControlPlane.communications);
  const agentControlDomainWeaver = record(agentControlPlane.domain_weaver);
  const agentControlDispatcher = record(agentControlPlane.dispatcher);
  const agentControlRuns = record(agentControlPlane.runs);
  const agentChainSteps = records(agentControlChain.steps);
  const agentCommsTimeline = records(agentControlComms.timeline);
  const agentCommsRelays = records(agentControlComms.relays);
  const agentCommsPendingRelays = records(agentControlComms.pending_relays);
  const agentCommsReceipts = records(agentControlComms.receipts);
  const agentTeamComms = record(agentControlComms.team_comms);
  const mcpCarrierMessages = records(mcpSummary.latest_carrier_messages);
  const mcpTaskReturns = records(mcpSummary.latest_task_returns);
  const mcpAgentInvocations = records(mcpSummary.latest_agent_invocations);
  const rolePhaseRows = stringList(rolePhaseContract.role_phase_sequence);
  const groups = records(chat?.conversation_turn_groups);
  const ionCommsTurnGroups = records(chat?.ion_comms_turn_groups);
  const ionPipelineRuns = records(chat?.pipeline_runs);
  const latestIonPipelineRun = ionPipelineRuns[ionPipelineRuns.length - 1] ?? {};
  const latestIonPipelineStages = records(latestIonPipelineRun.stages);
  const transcriptGroups = groups.filter((group) => record(group.user_turn).message || records(group.assistant_turns).length || records(group.execution_turns).length).slice(-80);
  const serverUserTurnReceipts = useMemo(
    () => transcriptGroups.map((group) => {
      const userTurn = record(group.user_turn);
      return {
        message: text(userTurn.message, ''),
        createdAt: text(userTurn.created_at || group.created_at, ''),
        clientId: text(userTurn.client_id || userTurn.clientId, ''),
        turnId: text(userTurn.turn_id, ''),
        hasServerWork: serverTurnGroupHasWork(group),
      };
    }).filter((receipt) => receipt.message),
    [transcriptGroups],
  );
  const ionServerUserTurnReceipts = useMemo(
    () => ionCommsTurnGroups.map((group) => {
      const userTurn = record(group.user_turn);
      return {
        message: text(userTurn.message, ''),
        createdAt: text(userTurn.created_at || group.created_at, ''),
        clientId: text(userTurn.client_id || userTurn.clientId, ''),
        turnId: text(userTurn.turn_id, ''),
        hasServerWork: serverTurnGroupHasWork(group),
      };
    }).filter((receipt) => receipt.message),
    [ionCommsTurnGroups],
  );
  const latestResponseRuns = records(chat?.latest_response_runs);
  const visiblePendingChatTurns = useMemo(
    () => pendingChatTurns.filter((turn) => {
      const receipts = turn.laneId === 'ion_system' ? ionServerUserTurnReceipts : serverUserTurnReceipts;
      return turn.status === 'failed' || !pendingTurnHasServerReceipt(turn, receipts);
    }),
    [ionServerUserTurnReceipts, pendingChatTurns, serverUserTurnReceipts],
  );
  const visiblePendingCodexChatTurns = useMemo(
    () => visiblePendingChatTurns.filter((turn) => turn.laneId !== 'ion_system'),
    [visiblePendingChatTurns],
  );
  const visiblePendingIonChatTurns = useMemo(
    () => visiblePendingChatTurns.filter((turn) => turn.laneId === 'ion_system'),
    [visiblePendingChatTurns],
  );
  const pendingChatActive = visiblePendingChatTurns.some((turn) => turn.status === 'sending');
  const liveTranscriptGroups = useMemo(
    () => [
      ...transcriptGroups,
      ...visiblePendingCodexChatTurns.map((turn) => pendingChatTurnGroup(turn, pendingClockTick, {
        workerActive,
        workerStatus,
        workerDuration,
        queuedRequestCount,
        responseRun: latestResponseRunForPendingTurn(turn, latestResponseRuns),
      })),
    ].slice(-80),
    [latestResponseRuns, pendingClockTick, queuedRequestCount, transcriptGroups, visiblePendingCodexChatTurns, workerActive, workerDuration, workerStatus],
  );
  const ionLiveTranscriptGroups = useMemo(
    () => [
      ...ionCommsTurnGroups,
      ...visiblePendingIonChatTurns.map((turn) => pendingChatTurnGroup(turn, pendingClockTick, {
        workerActive,
        workerStatus,
        workerDuration,
        queuedRequestCount,
        responseRun: latestResponseRunForPendingTurn(turn, latestResponseRuns),
      })),
    ].slice(-80),
    [ionCommsTurnGroups, latestResponseRuns, pendingClockTick, queuedRequestCount, visiblePendingIonChatTurns, workerActive, workerDuration, workerStatus],
  );
  const latestAssistant = latestAssistantText(liveTranscriptGroups);
  const latestAssistantKey = latestAssistantTurnKey(liveTranscriptGroups);
  const latestIonAssistantKey = latestAssistantTurnKey(ionLiveTranscriptGroups);
  const liveNewestKey = liveTranscriptNewestKey(liveTranscriptGroups, latestAssistantKey);
  const chatBranches = records(chat?.chat_branches).slice().reverse();
  const activeChatTab = useMemo(
    () => openChatTabs.find((tab) => tab.id === activeChatTabId) ?? null,
    [activeChatTabId, openChatTabs],
  );
  const activeMessageQueueGroup = useMemo(
    () => messageQueueState.groups.find((group) => group.id === messageQueueState.activeGroupId) ?? null,
    [messageQueueState.activeGroupId, messageQueueState.groups],
  );
  const allSessions = archive?.sessions ?? [];
  const favoriteChatIdSet = useMemo(
    () => new Set(favoriteChatIds),
    [favoriteChatIds],
  );
  const chatHistoryEntries = useMemo(
    () => buildChatHistoryEntries(allSessions, openChatTabs, chatTitleOverrides, chatHistoryMeta, chatHistorySort),
    [allSessions, chatHistoryMeta, chatHistorySort, chatTitleOverrides, openChatTabs],
  );
  const openChatSessionIds = useMemo(
    () => new Set(openChatTabs.map((tab) => tab.sessionId)),
    [openChatTabs],
  );
  const shortFilteredSessions = useMemo(
    () => allSessions.filter((session) => sessionVisibleByShortFilter(session, {
      currentSessionId: text(archive?.current_session_id, ''),
      favoriteIds: favoriteChatIdSet,
      openIds: openChatSessionIds,
      prefs: chatDrawerPrefs,
      selectedSessionId,
    })),
    [allSessions, archive?.current_session_id, chatDrawerPrefs, favoriteChatIdSet, openChatSessionIds, selectedSessionId],
  );
  const hiddenShortChatCount = allSessions.length - shortFilteredSessions.length;
  const visibleSessions = useMemo(
    () => filterSessions(shortFilteredSessions, archiveSearch),
    [archiveSearch, shortFilteredSessions],
  );
  const visibleConversationSessions = useMemo(
    () => visibleSessions.filter((session) => !isQueueRunnerPacket(session)),
    [visibleSessions],
  );
  const visiblePacketSessions = useMemo(
    () => visibleSessions.filter(isQueueRunnerPacket),
    [visibleSessions],
  );
  const latestVisibleSession = useMemo(
    () => sortByRecent(visibleConversationSessions)[0] ?? sortByRecent(visibleSessions)[0] ?? null,
    [visibleConversationSessions, visibleSessions],
  );
  const archiveOverview = useMemo(
    () => buildArchiveOverview(allSessions),
    [allSessions],
  );
  const visibleArchiveOverview = useMemo(
    () => buildArchiveOverview(visibleSessions),
    [visibleSessions],
  );
  const archiveSessionGroups = useMemo(
    () => archiveGroups(archiveView, visibleSessions),
    [archiveView, visibleSessions],
  );
  const selectedSession = useMemo(
    () => allSessions.find((session) => session.session_id === selectedSessionId) ?? sessionFromOpenChatTab(activeChatTab),
    [activeChatTab, allSessions, selectedSessionId],
  );
  const rawSelectedExcerpt = archive?.selected_session_excerpt ?? null;
  const rawSelectedExcerptSessionId = text(rawSelectedExcerpt?.session_id, '');
  const selectedSessionTargetId = (chatViewMode === 'archive' || activeChatTab)
    ? text(selectedSession?.session_id || selectedSessionId || activeChatTab?.sessionId || rawSelectedExcerptSessionId, '')
    : '';
  const selectedExcerpt = rawSelectedExcerpt && (
    !selectedSessionTargetId
    || !rawSelectedExcerptSessionId
    || rawSelectedExcerptSessionId === selectedSessionTargetId
  ) ? rawSelectedExcerpt : null;
  const selectedExcerptItemCount = records(selectedExcerpt?.items).length;
  const selectedExcerptSessionId = text(selectedExcerpt?.session_id, '');
  const currentArchiveSessionId = text(archive?.current_session_id, '');
  const currentArchiveSession = useMemo(
    () => allSessions.find((session) => session.is_current_session || (currentArchiveSessionId && session.session_id === currentArchiveSessionId)),
    [allSessions, currentArchiveSessionId],
  );
  const selectedArchiveSessionId = text(selectedSession?.session_id || selectedSessionId || selectedExcerptSessionId, '');
  const selectedArchiveIsCurrent = Boolean(
    selectedSession?.is_current_session
    || selectedExcerpt?.is_current_session
    || (currentArchiveSessionId && selectedArchiveSessionId === currentArchiveSessionId),
  );
  const showingArchiveChat = chatViewMode === 'archive' && Boolean(selectedSessionId || selectedExcerpt);

  useEffect(() => {
    setSttSupported(Boolean(speechRecognitionConstructor()));
    if (typeof document !== 'undefined') {
      setContextMapBottomBarSlot(document.getElementById('ion-codex-context-map-bottom-slot'));
    }
    return () => {
      messageQueuePointerCleanupRef.current?.();
      speechRecognitionRef.current?.abort();
      speechRecognitionRef.current = null;
      setContextMapBottomBarSlot(null);
    };
  }, []);

  useEffect(() => {
    persistOpenChatTabs({ activeTabId: activeChatTabId, tabs: openChatTabs });
  }, [activeChatTabId, openChatTabs]);

  useEffect(() => {
    persistChatTitleOverrides(chatTitleOverrides);
  }, [chatTitleOverrides]);

  useEffect(() => {
    persistChatHistoryMeta(chatHistoryMeta);
  }, [chatHistoryMeta]);

  useEffect(() => {
    persistFavoriteChatIds(favoriteChatIds);
  }, [favoriteChatIds]);

  useEffect(() => {
    persistChatDrawerPrefs(chatDrawerPrefs);
  }, [chatDrawerPrefs]);

  useEffect(() => {
    persistCodexMessageQueues(messageQueueState);
  }, [messageQueueState]);

  useEffect(() => {
    persistContextRefs(selectedContextRefs);
  }, [selectedContextRefs]);

  useEffect(() => {
    setPendingChatTurns((previous) => {
      const staleSettledCutoff = Date.now() - 8000;
      const next = previous.filter((turn) => {
        if (turn.status === 'failed') return true;
        const receipts = turn.laneId === 'ion_system' ? ionServerUserTurnReceipts : serverUserTurnReceipts;
        if (pendingTurnHasServerReceipt(turn, receipts)) return false;
        if (turn.status === 'settled' && Date.parse(turn.settledAt || turn.createdAt) < staleSettledCutoff) return false;
        return true;
      });
      return next.length === previous.length ? previous : next;
    });
  }, [ionServerUserTurnReceipts, pendingClockTick, serverUserTurnReceipts]);

  useEffect(() => {
    if (activeTab !== 'chat' && activeTab !== 'ion') return;
    if (!pendingChatActive && !sending && !workerActive && !queueDispatchActive) return;
    setPendingClockTick((tick) => tick + 1);
    const interval = window.setInterval(() => {
      setPendingClockTick((tick) => tick + 1);
      void Promise.resolve(onRuntimeRefresh?.());
    }, pendingChatActive || sending ? 1200 : 2200);
    return () => window.clearInterval(interval);
  }, [activeTab, onRuntimeRefresh, pendingChatActive, queueDispatchActive, sending, workerActive]);

  useEffect(() => {
    if (archiveProjection || (runtime.codex_conversation_archive?.sessions?.length ?? 0) > 0) return;
    let ignore = false;
    const run = async () => {
      setArchiveBackgroundBusy(true);
      try {
        const response = await fetch(chatApiPath('/archive.json'), {
          headers: { Accept: 'application/json' },
          cache: 'no-store',
        });
        const payload = await response.json() as IonCodexConversationArchive;
        if (!response.ok) throw new Error(`archive_http_${response.status}`);
        if (!ignore) setArchiveProjection(payload);
      } catch (error) {
        if (!ignore) setArchiveAction(error instanceof Error ? error.message : 'archive_index_failed');
      } finally {
        if (!ignore) setArchiveBackgroundBusy(false);
      }
    };
    void run();
    return () => {
      ignore = true;
    };
  }, [archiveProjection, runtime.codex_conversation_archive?.sessions?.length]);

  useEffect(() => {
    if (!filePickerOpen) return;
    let ignore = false;
    const run = async () => {
      setFileTreeBusy(true);
      setFileTreeError('');
      try {
        const response = await fetch(chatApiPath('/file-tree'), {
          method: 'POST',
          headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
          body: JSON.stringify(withPublicToken({
            path: fileTreeRoot || 'ION',
            max_depth: fileTreeDepth,
            limit: 700,
          })),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok || payload.ok === false) {
          throw new Error(text(payload.finding || payload.error, `file_tree_http_${response.status}`));
        }
        const data = record(payload.data || payload);
        const entries = records(data.entries).map(sanitizeFileTreeEntry).filter((entry): entry is CodexFileTreeEntry => Boolean(entry));
        if (!ignore) setFileTreeEntries(entries);
      } catch (error) {
        if (!ignore) {
          setFileTreeEntries([]);
          setFileTreeError(error instanceof Error ? error.message : 'file_tree_failed');
        }
      } finally {
        if (!ignore) setFileTreeBusy(false);
      }
    };
    void run();
    return () => {
      ignore = true;
    };
  }, [filePickerOpen, fileTreeDepth, fileTreeRefreshVersion, fileTreeRoot]);

  useEffect(() => {
    if (activeTab !== 'chat' || chatArchiveDrawerPrimed) return;
    setLeftDrawer('sessions');
    setLeftDrawerOpen(true);
    setChatArchiveDrawerPrimed(true);
  }, [activeTab, chatArchiveDrawerPrimed]);

  useEffect(() => {
    persistConnectionState(connectionState);
  }, [connectionState]);

  useEffect(() => {
    if (!activeChatTabId || openChatTabs.some((tab) => tab.id === activeChatTabId)) return;
    setActiveChatTabId(openChatTabs[0]?.id ?? '');
  }, [activeChatTabId, openChatTabs]);

  useEffect(() => {
    if (activeTab !== 'chat' || showingArchiveChat || !openChatTabs.length) return;
    const fallbackTab = openChatTabs.find((tab) => tab.id === activeChatTabId) ?? openChatTabs[0];
    if (!fallbackTab) return;
    selectOpenChatTab(fallbackTab);
  }, [activeTab, activeChatTabId, openChatTabs, showingArchiveChat]);

  useEffect(() => {
    if (!rightDrawerOpen || rightDrawer !== 'rollback') return;
    void refreshRollbackProjection(selectedArchiveSessionId);
  }, [rightDrawerOpen, rightDrawer, selectedArchiveSessionId]);

  useEffect(() => {
    if (!rightDrawerOpen || rightDrawer !== 'missionProfile') return;
    void refreshMissionCommsThreads({ silent: missionCommsThreads.length > 0 });
    const interval = window.setInterval(() => {
      void refreshMissionCommsThreads({ silent: true });
    }, workerActive ? 3500 : 12000);
    return () => window.clearInterval(interval);
  }, [rightDrawerOpen, rightDrawer, workerActive]);

  useEffect(() => {
    if (!rightDrawerOpen || rightDrawer !== 'missionProfile' || !selectedMissionThreadId) return;
    void refreshMissionCommsThread(selectedMissionThreadId, {
      silent: text(missionCommsThreadDetail.thread?.thread_id, '') === selectedMissionThreadId,
    });
  }, [rightDrawerOpen, rightDrawer, selectedMissionThreadId]);

  useLayoutEffect(() => {
    if (activeTab !== 'chat' || chatViewMode !== 'live') return;
    const node = transcriptRef.current;
    if (!node) return;
    if (liveNewestKey && liveNewestKeyRef.current !== liveNewestKey) {
      liveNewestKeyRef.current = liveNewestKey;
      livePinnedToBottomRef.current = false;
      scrollLiveTranscriptToNewest(node, { repeat: true });
      return;
    }
    if (livePinnedToBottomRef.current) {
      scrollTranscriptToPosition(node, 'bottom', { repeat: true });
    }
  }, [activeTab, chatViewMode, latestAssistant, liveNewestKey, liveTranscriptGroups.length]);

  useEffect(() => {
    if (activeTab !== 'chat' || chatViewMode !== 'live') return;
    const node = transcriptRef.current;
    if (!node) return;
    if (isTranscriptNearBottom(node, LIVE_BOTTOM_STICKY_PX)) {
      livePinnedToBottomRef.current = true;
    }

    const stickIfPinned = () => {
      if (!livePinnedToBottomRef.current) return;
      scrollTranscriptToPosition(node, 'bottom', { repeat: true });
    };
    let resizeObserver: ResizeObserver | null = null;
    const observeTranscript = () => {
      resizeObserver?.disconnect();
      if (!resizeObserver) return;
      resizeObserver.observe(node);
      Array.from(node.children).forEach((child) => resizeObserver?.observe(child));
    };
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(stickIfPinned);
      observeTranscript();
    }
    const mutationObserver = typeof MutationObserver !== 'undefined'
      ? new MutationObserver((mutations) => {
        observeTranscript();
        const addedTurn = mutations.some((mutation) => Array.from(mutation.addedNodes).some((child) => (
          child instanceof HTMLElement && child.classList.contains('ion-codex-turn-group')
        )));
        if (addedTurn && livePinnedToBottomRef.current) {
          livePinnedToBottomRef.current = false;
          scrollLiveTranscriptToNewest(node, { repeat: true });
          return;
        }
        stickIfPinned();
      })
      : null;
    mutationObserver?.observe(node, { childList: true, characterData: true, subtree: true });
    return () => {
      resizeObserver?.disconnect();
      mutationObserver?.disconnect();
    };
  }, [activeTab, chatViewMode]);

  useEffect(() => {
    if (activeTab !== 'chat' || chatViewMode !== 'archive') return;
    if (archiveBusy) return;
    if (archiveSuppressNextAutoScrollRef.current) {
      archiveSuppressNextAutoScrollRef.current = false;
      return;
    }
    archiveProgrammaticScrollUntilRef.current = Date.now() + 400;
    scrollArchiveTranscriptToLoadedWindow(archiveTranscriptRef.current, archiveScrollTargetRef.current, { repeat: true });
    syncArchiveScrollAnchor();
  }, [activeTab, archiveBusy, chatViewMode, selectedExcerptItemCount, selectedExcerptSessionId, selectedSessionId]);

  useLayoutEffect(() => {
    if (activeTab !== 'chat') return;
    syncChatTimelineScrollRatio(showingArchiveChat ? archiveTranscriptRef.current : transcriptRef.current);
  }, [activeTab, showingArchiveChat, liveTranscriptGroups.length, selectedExcerptItemCount, archiveBusy]);

  useLayoutEffect(() => {
    const virtualRestoreTop = archiveVirtualRestoreTopRef.current;
    if (virtualRestoreTop !== null) {
      const node = archiveTranscriptRef.current;
      if (node) {
        const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
        node.scrollTop = Math.min(Math.max(0, virtualRestoreTop), maxTop);
        archiveLastScrollTopRef.current = node.scrollTop;
        archiveProgrammaticScrollUntilRef.current = Date.now() + 80;
      }
      archiveVirtualRestoreTopRef.current = null;
    }
    const promotionTop = archiveBufferPromotionTopRef.current;
    if (promotionTop !== null) {
      const node = archiveTranscriptRef.current;
      if (node) {
        const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
        node.scrollTop = Math.min(Math.max(0, promotionTop), maxTop);
        archiveLastScrollTopRef.current = node.scrollTop;
        archiveProgrammaticScrollUntilRef.current = Date.now() + 120;
      }
      archiveBufferPromotionTopRef.current = null;
    }
    const node = archiveTranscriptRef.current;
    const renderAdjustment = archiveBufferRenderAdjustmentRef.current;
    if (node && archivePrefetch && renderAdjustment && archivePrefetchKey(archivePrefetch) === renderAdjustment.key) {
      const delta = Math.max(0, node.scrollHeight - renderAdjustment.beforeHeight);
      archiveBufferPixelSizeRef.current = delta;
      if (archivePrefetch.direction === 'older' && delta > 0) {
        node.scrollTop = renderAdjustment.beforeTop + delta;
      }
      archiveLastScrollTopRef.current = node.scrollTop;
      archiveBufferRenderAdjustmentRef.current = null;
      archiveProgrammaticScrollUntilRef.current = Date.now() + 120;
    }
    const removalAdjustment = archiveBufferRemovalAdjustmentRef.current;
    if (node && !archivePrefetch && removalAdjustment) {
      const delta = Math.max(0, removalAdjustment.beforeHeight - node.scrollHeight);
      if (removalAdjustment.direction === 'older' && delta > 0) {
        node.scrollTop = Math.max(0, removalAdjustment.beforeTop - delta);
      }
      archiveLastScrollTopRef.current = node.scrollTop;
      archiveBufferPixelSizeRef.current = 0;
      archiveBufferRemovalAdjustmentRef.current = null;
      archiveProgrammaticScrollUntilRef.current = Date.now() + 120;
    }
  }, [archivePrefetch, archiveProjection]);

  useEffect(() => {
    clearArchivePrefetch();
    archiveVirtualPendingLoadRef.current = null;
    archiveVirtualLoadingKeyRef.current = '';
  }, [archiveSearch, selectedSessionId]);

  function activeComposerLaneId(): CodexChatLaneId {
    return activeTab === 'ion' ? 'ion_system' : 'codex_general';
  }

  async function sendCodexMessage(message: string, mode: ExecutionModeId, options: { restoreComposerOnError?: boolean; noticeLabel?: string; contextRefs?: string[]; laneId?: CodexChatLaneId } = {}) {
    const body = message.trim();
    if (!body) return false;
    const laneId = options.laneId ?? activeComposerLaneId();
    const contextRefs = normalizeContextRefs(options.contextRefs ?? selectedContextRefs);
    const targetSessionId = laneId === 'codex_general' ? selectedSessionTargetId : '';
    const newCodexSession = laneId === 'codex_general' && !targetSessionId && newCodexSessionRequested;
    const codexSessionTransport: PendingChatTurn['codexSessionTransport'] = targetSessionId ? 'app_server' : 'raw_cli';
    const targetSessionTitle = targetSessionId
      ? chatTitleForSessionId(targetSessionId, selectedSession?.thread_name || activeChatTab?.title || targetSessionId)
      : '';
    const pendingTurn: PendingChatTurn = {
      clientId: createClientId('pending_chat_turn'),
      message: body,
      mode,
      laneId,
      agentMode,
      selectedModel: selectedModelOverride || 'auto',
      thinkingMode,
      contextRefs,
      targetSessionId,
      targetSessionTitle,
      newCodexSession,
      codexSessionTransport,
      createdAt: new Date().toISOString(),
      status: 'sending',
    };
    setPendingChatTurns((previous) => [
      ...previous.filter((turn) => !(turn.status === 'failed' && turn.message === body)),
      pendingTurn,
    ]);
    setExecutionMode(mode);
    setSending(true);
    setSendError('');
    setActionNotice(laneId === 'ion_system'
      ? 'Recording ION pipeline prompt; waiting for server receipt'
      : targetSessionId
        ? `Resuming Codex session ${sessionShortText(targetSessionId)} through Codex thread API; waiting for server receipt`
        : newCodexSession
          ? 'Starting a new Codex CLI session; waiting for server receipt'
        : 'Sending prompt to Codex CLI bridge; waiting for server receipt');
    livePinnedToBottomRef.current = true;
    setChatViewMode('live');
    try {
      const response = await fetch(chatApiPath('/turn'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          client_id: pendingTurn.clientId,
          target_session_id: targetSessionId,
          new_codex_session: newCodexSession,
          codex_session_transport: codexSessionTransport,
          lane_id: laneId,
          message: body,
          author: 'operator',
          execution_mode: mode,
          agent_mode: agentMode,
          selected_model: selectedModelOverride || 'auto',
          thinking_mode: thinkingMode,
          context_refs: contextRefs,
          ide_context_bridge: ideContextBridge,
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `chat_turn_http_${response.status}`));
      }
      const assistantTurn = record(payload.assistant_turn);
      const codexAppServer = record(assistantTurn.codex_app_server);
      const appServerRun = record(codexAppServer.run);
      const rawCodexCli = record(assistantTurn.raw_codex_cli);
      const rawCodexRun = record(rawCodexCli.run);
      const responseCarrier = record(assistantTurn.response_carrier);
      const responseRun = record(responseCarrier.run);
      const queueLink = record(record(payload.queue_result).queue_link);
      const pipelineRun = record(payload.pipeline_run);
      const assistantPreview = text(assistantTurn.message || record(assistantTurn.chat_engine).assistant_response, '');
      const responseStatus = text(codexAppServer.status || rawCodexCli.status || responseCarrier.status || queueLink.status || pipelineRun.status || payload.queue_execution_mode || payload.execution_mode || 'turn_recorded', 'turn_recorded');
      const responseRunPath = text(appServerRun.run_packet_path || appServerRun.receipt_path || rawCodexRun.run_packet_path || responseRun.run_packet_path || responseCarrier.run_packet_path || queueLink.packet_path, '');
      const responseMode = text(assistantTurn.response_mode || codexAppServer.response_mode || rawCodexCli.response_mode || responseCarrier.response_mode || '', '');
      const responseSurface = text(appServerRun.codex_cli_surface || rawCodexRun.codex_cli_surface || responseCarrier.codex_cli_surface || '', '');
      const responseThreadId = text(codexAppServer.active_thread_id || appServerRun.active_thread_id_after || rawCodexCli.active_thread_id || rawCodexRun.active_thread_id_after || rawCodexRun.active_thread_id_before || '', '');
      setPendingChatTurns((previous) => previous.map((turn) => (
        turn.clientId === pendingTurn.clientId
          ? { ...turn, status: 'settled', settledAt: new Date().toISOString(), assistantPreview, responseStatus, responseRunPath, responseMode, responseSurface, responseThreadId }
          : turn
      )));
      void Promise.resolve(onRuntimeRefresh?.()).catch(() => {});
      if (newCodexSession) setNewCodexSessionRequested(false);
      if (options.noticeLabel) {
        setActionNotice(options.noticeLabel);
      } else if (responseMode === 'codex_app_server') {
        setActionNotice(`Codex thread API response recorded${responseRunPath ? `: ${responseRunPath}` : responseStatus ? `: ${responseStatus}` : ''}`);
      } else if (responseMode === 'raw_codex_cli' || responseSurface) {
        setActionNotice(`Codex CLI response recorded${responseRunPath ? `: ${responseRunPath}` : responseStatus ? `: ${responseStatus}` : ''}`);
      } else if (queueLink.packet_path) {
        setActionNotice(`Codex queue request recorded: ${queueLink.packet_path}`);
      } else if (laneId === 'ion_system') {
        setActionNotice('ION pipeline prompt accepted; showing role/comms activity');
      } else {
        setActionNotice(responseStatus ? `Chat turn accepted: ${responseStatus}` : 'Chat turn accepted');
      }
      return true;
    } catch (error) {
      if (options.restoreComposerOnError) setComposer(body);
      const errorMessage = error instanceof Error ? error.message : 'chat_turn_failed';
      setPendingChatTurns((previous) => previous.map((turn) => (
        turn.clientId === pendingTurn.clientId
          ? { ...turn, status: 'failed', error: errorMessage, settledAt: new Date().toISOString() }
          : turn
      )));
      setSendError(errorMessage);
      return false;
    } finally {
      setSending(false);
    }
  }

  async function stopCodexAgent() {
    if (agentStopBusy || !cancelableWorkerActive) return;
    setAgentStopBusy(true);
    setSendError('');
    try {
      const response = await fetch(chatApiPath('/agent/stop'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          confirmation: 'ION_STOP_CODEX_AGENT_CONFIRMED',
          reason: 'operator_stop_from_codex_chat_composer',
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `agent_stop_http_${response.status}`));
      }
      setActionNotice(`Stop requested for ${text(payload.stopped_count, '1')} Codex worker`);
      await Promise.resolve(onRuntimeRefresh?.());
    } catch (error) {
      setSendError(error instanceof Error ? error.message : 'agent_stop_failed');
    } finally {
      setAgentStopBusy(false);
    }
  }

  async function submitTurn(event: FormEvent<HTMLFormElement> | undefined, mode?: ExecutionModeId, laneId: CodexChatLaneId = activeComposerLaneId()) {
    event?.preventDefault();
    const message = composer.trim();
    if (!message || sending || messageQueueDispatchingId) return;
    setComposer('');
    await sendCodexMessage(message, mode ?? executionMode, { restoreComposerOnError: true, laneId });
  }

  function stageMessageInQueue(message: string, mode: ExecutionModeId, title = '', insertIndex?: number, contextRefs: string[] = selectedContextRefs, laneId: CodexChatLaneId = activeComposerLaneId()) {
    const body = message.trim();
    if (!body) return null;
    const item = createMessageQueueItem(body, mode, title, contextRefs, laneId);
    updateMessageQueueItems((items) => {
      if (typeof insertIndex !== 'number') return [...items, item];
      const next = [...items];
      const index = Math.min(Math.max(0, insertIndex), next.length);
      next.splice(index, 0, item);
      return next;
    });
    setRightDrawer('messageQueue');
    setRightDrawerOpen(true);
    return item;
  }

  function stageComposerAtQueueIndex(index: number) {
    const body = composer.trim();
    if (!body) return;
    const item = stageMessageInQueue(body, 'queue_for_codex', '', index);
    if (!item) return;
    setExecutionMode('queue_for_codex');
    setComposer('');
    setQueueInsertOpen(false);
    setActionNotice(`Inserted queue message: ${item.title}`);
  }

  function openComposerQueueInsertPanel() {
    if (composerQueueDisabled) return;
    setQueueInsertOpen(true);
  }

  function handleComposerQueueDragStart(event: DragEvent<HTMLButtonElement>) {
    if (composerQueueDisabled) {
      event.preventDefault();
      return;
    }
    setQueueInsertOpen(true);
    event.dataTransfer.effectAllowed = 'copy';
    event.dataTransfer.setData('text/plain', '__codex_composer_queue_message__');
  }

  function handleComposerQueueDropAtIndex(event: DragEvent<HTMLElement>, index: number) {
    event.preventDefault();
    event.stopPropagation();
    if (composerQueueDisabled) return;
    stageComposerAtQueueIndex(index);
  }

  function updateMessageQueueItems(updater: (items: CodexMessageQueueItem[]) => CodexMessageQueueItem[]) {
    setMessageQueueState((previous) => ({
      ...previous,
      items: updater(previous.items).map(sanitizeMessageQueueItem).filter((item): item is CodexMessageQueueItem => Boolean(item)),
    }));
  }

  function addMessageQueueDraft() {
    const body = messageQueueDraftBody.trim();
    if (!body) return;
    const item = stageMessageInQueue(body, messageQueueDraftMode, messageQueueDraftTitle);
    if (!item) return;
    setMessageQueueDraftTitle('');
    setMessageQueueDraftBody('');
    setActionNotice(`Added queue message: ${item.title}`);
  }

  function stageComposerInMessageQueue(mode: ExecutionModeId = 'queue_for_codex') {
    const body = composer.trim();
    if (!body) return;
    const item = stageMessageInQueue(body, mode);
    if (!item) return;
    setExecutionMode(mode);
    setComposer('');
    setQueueInsertOpen(false);
    setActionNotice(`Staged composer message: ${item.title}`);
  }

  async function runComposerThroughMessageQueue() {
    if (queuePaused) setQueuePaused(false);
    if (sending || messageQueueDispatchingId) return;
    const body = composer.trim();
    if (!body) {
      if (messageQueueState.items.length) await dispatchAllMessageQueueItems();
      return;
    }
    const item = stageMessageInQueue(body, 'queue_and_start');
    if (!item) return;
    setExecutionMode('queue_and_start');
    setComposer('');
    setMessageQueueDispatchingId(item.id);
    const ok = await sendCodexMessage(item.message, item.mode, { noticeLabel: `Running queue message: ${item.title}`, restoreComposerOnError: true, contextRefs: item.contextRefs, laneId: codexChatLaneId(item.laneId) });
    if (ok) markMessageQueueItemDispatched(item.id);
    setMessageQueueDispatchingId('');
  }

  async function toggleRunPause() {
    if (messageQueueDispatchingId) {
      setQueuePaused((previous) => !previous);
      setActionNotice(queuePaused ? 'Queue resume requested' : 'Staged queue paused after the active queue message');
      return;
    }
    if (workerActive) {
      setActionNotice('Codex agent is already working; prompt remains available and queue play waits for the worker to stop');
      return;
    }
    if (queuePaused) setQueuePaused(false);
    await runComposerThroughMessageQueue();
  }

  function beginEditMessageQueueItem(item: CodexMessageQueueItem) {
    setEditingMessageQueueItemId(item.id);
    setMessageQueueEditTitle(item.title);
    setMessageQueueEditBody(item.message);
    setMessageQueueEditMode(item.mode);
  }

  function cancelEditMessageQueueItem() {
    setEditingMessageQueueItemId('');
    setMessageQueueEditTitle('');
    setMessageQueueEditBody('');
    setMessageQueueEditMode('queue_for_codex');
  }

  function commitMessageQueueItemEdit() {
    const body = messageQueueEditBody.trim();
    if (!editingMessageQueueItemId || !body) return;
    const title = cleanQueueTitle(messageQueueEditTitle, body);
    updateMessageQueueItems((items) => items.map((item) => (
      item.id === editingMessageQueueItemId
        ? {
            ...item,
            title,
            message: body,
            mode: messageQueueEditMode,
            updatedAt: new Date().toISOString(),
          }
        : item
    )));
    setActionNotice(`Edited queue message: ${title}`);
    cancelEditMessageQueueItem();
  }

  function deleteMessageQueueItem(itemId: string) {
    updateMessageQueueItems((items) => items.filter((item) => item.id !== itemId));
    if (editingMessageQueueItemId === itemId) cancelEditMessageQueueItem();
  }

  function duplicateMessageQueueItem(item: CodexMessageQueueItem) {
    const duplicate = {
      ...item,
      id: createClientId('codex_queue_item'),
      title: `${item.title} copy`.slice(0, 120),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      lastDispatchedAt: undefined,
    };
    updateMessageQueueItems((items) => {
      const index = items.findIndex((candidate) => candidate.id === item.id);
      const next = [...items];
      next.splice(index >= 0 ? index + 1 : next.length, 0, duplicate);
      return next;
    });
  }

  function moveMessageQueueItem(draggedId: string, targetId: string) {
    if (!draggedId || draggedId === targetId) return;
    updateMessageQueueItems((items) => {
      const fromIndex = items.findIndex((item) => item.id === draggedId);
      const targetIndex = items.findIndex((item) => item.id === targetId);
      if (fromIndex < 0 || targetIndex < 0) return items;
      const next = [...items];
      const [moved] = next.splice(fromIndex, 1);
      next.splice(targetIndex, 0, moved);
      return next;
    });
  }

  function nudgeMessageQueueItem(itemId: string, direction: -1 | 1) {
    updateMessageQueueItems((items) => {
      const index = items.findIndex((item) => item.id === itemId);
      const target = index + direction;
      if (index < 0 || target < 0 || target >= items.length) return items;
      const next = [...items];
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  }

  function reorderMessageQueueDragOver(targetId: string) {
    const draggedId = messageQueueDraggingIdRef.current || messageQueueDraggingId;
    if (!draggedId || draggedId === targetId) return;
    moveMessageQueueItem(draggedId, targetId);
  }

  function handleMessageQueueDragStart(event: DragEvent<HTMLElement>, itemId: string) {
    messageQueueDraggingIdRef.current = itemId;
    setMessageQueueDraggingId(itemId);
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', itemId);
  }

  function beginMessageQueueCoordinateDrag(itemId: string) {
    messageQueuePointerCleanupRef.current?.();
    messageQueueDraggingIdRef.current = itemId;
    setMessageQueueDraggingId(itemId);
    let active = true;
    const moveTo = (clientX: number, clientY: number) => {
      if (!active) return;
      const element = document.elementFromPoint(clientX, clientY);
      const target = element instanceof Element
        ? element.closest<HTMLElement>('[data-message-queue-item-id]')
        : null;
      const targetId = target?.dataset.messageQueueItemId || '';
      if (targetId && targetId !== itemId) moveMessageQueueItem(itemId, targetId);
    };
    const pointerMove = (moveEvent: PointerEvent) => moveTo(moveEvent.clientX, moveEvent.clientY);
    const mouseMove = (moveEvent: MouseEvent) => moveTo(moveEvent.clientX, moveEvent.clientY);
    const finish = () => {
      if (!active) return;
      active = false;
      document.removeEventListener('pointermove', pointerMove);
      document.removeEventListener('mousemove', mouseMove);
      document.removeEventListener('pointerup', finish);
      document.removeEventListener('pointercancel', finish);
      document.removeEventListener('mouseup', finish);
      window.setTimeout(() => {
        messageQueueDraggingIdRef.current = '';
        setMessageQueueDraggingId('');
        messageQueuePointerCleanupRef.current = null;
      }, 0);
    };
    document.addEventListener('pointermove', pointerMove);
    document.addEventListener('mousemove', mouseMove);
    document.addEventListener('pointerup', finish, { once: true });
    document.addEventListener('pointercancel', finish, { once: true });
    document.addEventListener('mouseup', finish, { once: true });
    messageQueuePointerCleanupRef.current = finish;
  }

  function handleMessageQueuePointerDragStart(event: ReactPointerEvent<HTMLElement>, itemId: string) {
    if (event.button !== 0) return;
    event.preventDefault();
    beginMessageQueueCoordinateDrag(itemId);
  }

  function handleMessageQueueMouseDragStart(event: ReactMouseEvent<HTMLElement>, itemId: string) {
    if (event.button !== 0) return;
    event.preventDefault();
    beginMessageQueueCoordinateDrag(itemId);
  }

  function handleMessageQueueDragEnter(event: DragEvent<HTMLElement>, targetId: string) {
    event.preventDefault();
    const draggedId = messageQueueDraggingIdRef.current || messageQueueDraggingId;
    if (!draggedId || draggedId === targetId) return;
    moveMessageQueueItem(draggedId, targetId);
  }

  function handleMessageQueueDrop(event: DragEvent<HTMLElement>, targetId: string) {
    event.preventDefault();
    const draggedId = event.dataTransfer.getData('text/plain') || messageQueueDraggingIdRef.current || messageQueueDraggingId;
    moveMessageQueueItem(draggedId, targetId);
    messageQueueDraggingIdRef.current = '';
    setMessageQueueDraggingId('');
  }

  function saveMessageQueueGroup(options: { asNew?: boolean } = {}) {
    if (!messageQueueState.items.length) return;
    const now = new Date().toISOString();
    const existing = options.asNew ? null : activeMessageQueueGroup;
    const groupId = existing?.id || createClientId('codex_queue_group');
    const groupName = cleanQueueGroupName(messageQueueGroupName || existing?.name || '', messageQueueState.groups.length + 1);
    const group: CodexMessageQueueGroup = {
      id: groupId,
      name: groupName,
      items: messageQueueState.items.map(cloneMessageQueueItem),
      createdAt: existing?.createdAt || now,
      updatedAt: now,
    };
    setMessageQueueState((previous) => ({
      ...previous,
      activeGroupId: groupId,
      groups: [
        group,
        ...previous.groups.filter((candidate) => candidate.id !== groupId),
      ].slice(0, 30),
    }));
    setMessageQueueGroupName(groupName);
    setActionNotice(`Saved message queue group: ${groupName}`);
  }

  function loadMessageQueueGroup(group: CodexMessageQueueGroup) {
    setMessageQueueState((previous) => ({
      ...previous,
      activeGroupId: group.id,
      items: group.items.map(cloneMessageQueueItem),
    }));
    setMessageQueueGroupName(group.name);
    cancelEditMessageQueueItem();
    setActionNotice(`Loaded message queue group: ${group.name}`);
  }

  function deleteMessageQueueGroup(groupId: string) {
    setMessageQueueState((previous) => ({
      ...previous,
      activeGroupId: previous.activeGroupId === groupId ? '' : previous.activeGroupId,
      groups: previous.groups.filter((group) => group.id !== groupId),
    }));
  }

  function clearMessageQueue() {
    setMessageQueueState((previous) => ({ ...previous, activeGroupId: '', items: [] }));
    setMessageQueueGroupName('');
    cancelEditMessageQueueItem();
  }

  async function dispatchMessageQueueItem(item: CodexMessageQueueItem) {
    if (sending || messageQueueDispatchingId || !item.message.trim()) return;
    setMessageQueueDispatchingId(item.id);
    const ok = await sendCodexMessage(item.message, item.mode, { noticeLabel: `Dispatched queue message: ${item.title}`, contextRefs: item.contextRefs, laneId: codexChatLaneId(item.laneId) });
    if (ok) markMessageQueueItemDispatched(item.id);
    setMessageQueueDispatchingId('');
  }

  async function dispatchAllMessageQueueItems() {
    if (sending || messageQueueDispatchingId || !messageQueueState.items.length) return;
    if (queuePaused) {
      setActionNotice('Queue is paused');
      return;
    }
    setMessageQueueDispatchingId('__all__');
    const snapshot = messageQueueState.items.filter((item) => item.message.trim());
    const dispatchedIds: string[] = [];
    for (const item of snapshot) {
      const ok = await sendCodexMessage(item.message, item.mode, { contextRefs: item.contextRefs, laneId: codexChatLaneId(item.laneId) });
      if (!ok) break;
      dispatchedIds.push(item.id);
    }
    if (dispatchedIds.length) {
      const now = new Date().toISOString();
      updateMessageQueueItems((items) => items.map((item) => (
        dispatchedIds.includes(item.id) ? { ...item, lastDispatchedAt: now, updatedAt: now } : item
      )));
      setActionNotice(`Dispatched ${dispatchedIds.length} queue messages`);
    }
    setMessageQueueDispatchingId('');
  }

  function markMessageQueueItemDispatched(itemId: string) {
    const now = new Date().toISOString();
    updateMessageQueueItems((items) => items.map((item) => (
      item.id === itemId ? { ...item, lastDispatchedAt: now, updatedAt: now } : item
    )));
  }

  function startSpeechInput() {
    const Recognition = speechRecognitionConstructor();
    if (!Recognition) {
      setSttSupported(false);
      setSttStatus('speech api unavailable');
      return;
    }
    speechRecognitionRef.current?.abort();
    const recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = sttLanguage;
    recognition.maxAlternatives = 1;
    recognition.onstart = () => {
      setSttListening(true);
      setSttInterim('');
      setSttStatus('listening');
    };
    recognition.onerror = (event) => {
      setSttListening(false);
      setSttStatus(`voice ${text(event.error || event.message, 'error')}`);
    };
    recognition.onend = () => {
      if (speechRecognitionRef.current === recognition) speechRecognitionRef.current = null;
      setSttListening(false);
      setSttInterim('');
      setSttStatus((previous) => (previous === 'listening' ? 'voice idle' : previous));
    };
    recognition.onresult = (event) => {
      const finalChunks: string[] = [];
      const interimChunks: string[] = [];
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = text(result?.[0]?.transcript, '').trim();
        if (!transcript) continue;
        if (result?.isFinal) finalChunks.push(transcript);
        else interimChunks.push(transcript);
      }
      if (finalChunks.length) {
        const finalText = finalChunks.join(' ');
        setComposer((previous) => appendDictationText(previous, finalText));
        setSttStatus(`captured ${wordCount(finalText)} words`);
      }
      setSttInterim(interimChunks.join(' '));
    };
    speechRecognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (error) {
      speechRecognitionRef.current = null;
      setSttListening(false);
      setSttStatus(error instanceof Error ? error.message : 'voice start failed');
    }
  }

  function stopSpeechInput() {
    const recognition = speechRecognitionRef.current;
    if (!recognition) {
      setSttListening(false);
      setSttInterim('');
      setSttStatus('voice idle');
      return;
    }
    setSttStatus('stopping');
    recognition.stop();
  }

  function commitInterimSpeech() {
    const interim = sttInterim.trim();
    if (!interim) return;
    setComposer((previous) => appendDictationText(previous, interim));
    setSttInterim('');
    setSttStatus(`inserted ${wordCount(interim)} words`);
  }

  async function openSession(
    session: IonCodexConversationArchiveSession,
    options: {
      activateArchive?: boolean;
      addTab?: boolean;
      showInChat?: boolean;
      windowStart?: number;
      windowCount?: number;
      scrollTarget?: 'top' | 'bottom';
    } = {},
  ) {
    if (!session.session_id) return;
    clearArchivePrefetch();
    archiveVirtualPendingLoadRef.current = null;
    archiveVirtualLoadingKeyRef.current = '';
    const requestKey = `${session.session_id}:${Date.now()}:${Math.random().toString(16).slice(2)}`;
    archiveRequestKeyRef.current = requestKey;
    setArchiveBusy(true);
    setArchiveBackgroundBusy(false);
    setArchiveAction('');
    setSelectedSessionId(session.session_id);
    archiveScrollTargetRef.current = options.scrollTarget ?? 'bottom';
    if (options.showInChat) {
      setChatViewMode('archive');
      setActiveCodexTab('chat');
      if (options.addTab ?? true) {
        upsertOpenChatTab(session, { windowStart: options.windowStart });
      } else {
        setActiveChatTabId(tabIdForSession(session.session_id));
      }
    } else if (options.activateArchive ?? true) {
      setActiveCodexTab('archive');
    }
    const shouldFastOpen = Boolean(options.showInChat) && !options.windowStart && !options.windowCount;
    try {
      const payload = await fetchArchiveProjection(
        session.session_id,
        options.windowStart,
        shouldFastOpen ? ARCHIVE_FAST_OPEN_CHUNK_SIZE : options.windowCount ?? ARCHIVE_TRANSCRIPT_CHUNK_SIZE,
      );
      if (archiveRequestKeyRef.current !== requestKey) return;
      setArchiveProjection(payload);
      if (shouldFastOpen) {
        setArchiveAction(`Latest ${ARCHIVE_FAST_OPEN_CHUNK_SIZE} loaded. Older 500-item chunks stage as you scroll up.`);
      } else {
        setArchiveAction('');
      }
    } catch (error) {
      if (archiveRequestKeyRef.current === requestKey) {
        setSendError(error instanceof Error ? error.message : 'archive_fetch_failed');
      }
    } finally {
      if (archiveRequestKeyRef.current === requestKey) {
        setArchiveBusy(false);
        setArchiveBackgroundBusy(false);
      }
    }
  }

  function openSessionInArchive(session: IonCodexConversationArchiveSession) {
    setLeftDrawer('sessions');
    setLeftDrawerOpen(true);
    void openSession(session, { activateArchive: false, showInChat: true });
  }

  function openPastChatsDrawer() {
    setLeftDrawer('sessions');
    setChatDrawerPage('active');
    setLeftDrawerOpen(true);
    setActiveCodexTab('chat');
  }

  function toggleDrawerSession(key: string) {
    setExpandedDrawerSessionIds((previous) => {
      const next = new Set(previous);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  function toggleDrawerSessionPreview(session: IonCodexConversationArchiveSession) {
    const sessionId = text(session.session_id, '');
    if (!sessionId) return;
    const willExpand = !expandedDrawerSessionIds.has(sessionId);
    toggleDrawerSession(sessionId);
    if (willExpand && selectedExcerptSessionId !== sessionId) {
      void openSession(session, {
        activateArchive: false,
        addTab: false,
        showInChat: false,
        windowCount: 24,
        scrollTarget: 'bottom',
      });
    }
  }

  function showLiveChat() {
    setActiveChatTabId('');
    livePinnedToBottomRef.current = true;
    setChatViewMode('live');
    setActiveCodexTab('chat');
  }

  function startNewCodexCliThread() {
    setActiveChatTabId('');
    setSelectedSessionId('');
    livePinnedToBottomRef.current = true;
    setChatViewMode('live');
    setActiveCodexTab('chat');
    setNewCodexSessionRequested(true);
    setActionNotice('Next Codex prompt will start a new real Codex CLI session.');
  }

  function selectCodexTab(tabId: CodexTabId) {
    if (tabId === 'chat') {
      showLiveChat();
      return;
    }
    if (tabId === 'context') {
      setLeftDrawerOpen(false);
      setRightDrawerOpen(false);
    }
    setActiveCodexTab(tabId);
  }

  function syncArchiveScrollAnchor() {
    const node = archiveTranscriptRef.current;
    if (!node) return;
    const sync = () => {
      archiveLastScrollTopRef.current = node.scrollTop;
    };
    if (typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function') {
      window.requestAnimationFrame(sync);
      return;
    }
    sync();
  }

  function loadArchiveWindow(direction: 'older' | 'newer') {
    if (archiveBusy || !selectedSession) return;
    const nextStart = archiveWindowStartForDirection(direction, selectedExcerpt);
    if (!nextStart) return;
    if (
      archivePrefetch
      && archivePrefetch.sessionId === selectedSession.session_id
      && archivePrefetch.direction === direction
      && archivePrefetch.startIndex === nextStart
    ) {
      applyArchivePrefetch(archivePrefetch);
      return;
    }
    void openSession(selectedSession, {
      activateArchive: false,
      showInChat: true,
      windowStart: nextStart,
      windowCount: ARCHIVE_TRANSCRIPT_CHUNK_SIZE,
      scrollTarget: direction === 'older' ? 'bottom' : 'top',
    });
  }

  function handleArchiveScroll(event: UIEvent<HTMLDivElement>) {
    const node = event.currentTarget;
    syncChatTimelineScrollRatio(node);
    if (!selectedSession) return;
    if (Date.now() < archiveProgrammaticScrollUntilRef.current) return;
    if (requestArchiveVirtualWindowForScroll(node)) return;
    if (archiveBusy) return;
    const bottomDistance = node.scrollHeight - node.clientHeight - node.scrollTop;
    const bufferHandled = maybeStageArchiveBuffer(node, bottomDistance);
    if (bufferHandled) return;
    if (node.scrollTop <= 18 && Boolean(selectedExcerpt?.has_older_items)) {
      loadArchiveWindow('older');
      return;
    }
    if (bottomDistance <= 18 && Boolean(selectedExcerpt?.has_newer_items)) {
      loadArchiveWindow('newer');
    }
  }

  function requestArchiveVirtualWindowForScroll(node: HTMLDivElement) {
    if (!selectedSession || !selectedExcerpt) return false;
    const metrics = archiveVirtualMetrics(selectedExcerpt);
    if (!metrics.enabled) return false;
    const viewportStartIndex = Math.max(1, Math.floor(node.scrollTop / ARCHIVE_VIRTUAL_ITEM_PX) + 1);
    const viewportEndIndex = Math.min(metrics.total, Math.ceil((node.scrollTop + node.clientHeight) / ARCHIVE_VIRTUAL_ITEM_PX) + 1);
    const coversStart = viewportStartIndex >= Math.max(1, metrics.oldest - ARCHIVE_VIRTUAL_OVERSCAN_ITEMS);
    const coversEnd = viewportEndIndex <= Math.min(metrics.total, metrics.newest + ARCHIVE_VIRTUAL_OVERSCAN_ITEMS);
    archiveLastScrollTopRef.current = node.scrollTop;
    if (coversStart && coversEnd) return true;
    const maxStart = Math.max(1, metrics.total - ARCHIVE_TRANSCRIPT_CHUNK_SIZE + 1);
    const centeredStart = viewportStartIndex - Math.floor(ARCHIVE_TRANSCRIPT_CHUNK_SIZE / 2);
    const startIndex = Math.min(Math.max(1, centeredStart), maxStart);
    if (startIndex === metrics.oldest) return true;
    const request = {
      sessionId: selectedSession.session_id,
      startIndex,
      scrollTop: node.scrollTop,
    };
    if (archiveBusy || archiveBackgroundBusy || archiveVirtualLoadingKeyRef.current) {
      archiveVirtualPendingLoadRef.current = request;
      return true;
    }
    void loadArchiveVirtualWindow(request);
    return true;
  }

  async function loadArchiveVirtualWindow(request: ArchiveVirtualLoadRequest) {
    const session = selectedSession && selectedSession.session_id === request.sessionId ? selectedSession : null;
    if (!session || !session.session_id) return;
    const requestKey = `archive-virtual:${session.session_id}:${request.startIndex}:${archiveSearch}`;
    archiveVirtualLoadingKeyRef.current = requestKey;
    archiveVirtualPendingLoadRef.current = null;
    setArchiveBackgroundBusy(true);
    setArchiveAction('');
    try {
      const payload = await fetchArchiveProjection(session.session_id, request.startIndex, ARCHIVE_TRANSCRIPT_CHUNK_SIZE);
      if (archiveVirtualLoadingKeyRef.current !== requestKey) return;
      archiveVirtualRestoreTopRef.current = request.scrollTop;
      archiveSuppressNextAutoScrollRef.current = true;
      setArchiveProjection(payload);
      updateOpenChatTabWindowStart(session.session_id, request.startIndex);
    } catch {
      if (archiveVirtualLoadingKeyRef.current === requestKey) setArchiveAction('Archive range load failed');
    } finally {
      if (archiveVirtualLoadingKeyRef.current === requestKey) {
        archiveVirtualLoadingKeyRef.current = '';
        setArchiveBackgroundBusy(false);
        const pending = archiveVirtualPendingLoadRef.current;
        if (pending && pending.sessionId === session.session_id && pending.startIndex !== request.startIndex) {
          archiveVirtualPendingLoadRef.current = null;
          void loadArchiveVirtualWindow(pending);
        }
      }
    }
  }

  function handleLiveTranscriptScroll(event: UIEvent<HTMLDivElement>) {
    syncChatTimelineScrollRatio(event.currentTarget);
    livePinnedToBottomRef.current = isTranscriptNearBottom(event.currentTarget, LIVE_BOTTOM_STICKY_PX);
  }

  async function fetchArchiveProjection(sessionId: string, windowStart?: number, windowCount = ARCHIVE_TRANSCRIPT_CHUNK_SIZE) {
    const archiveQuery: Record<string, string> = {
      session_id: sessionId,
      q: archiveSearch,
      count: String(windowCount),
    };
    if (windowStart && windowStart > 0) archiveQuery.start = String(windowStart);
    const response = await fetch(chatApiPath('/archive.json', archiveQuery), {
      headers: { Accept: 'application/json' },
      cache: 'no-store',
    });
    const payload = await response.json() as IonCodexConversationArchive;
    if (!response.ok) throw new Error(`archive_http_${response.status}`);
    return payload;
  }

  async function refreshRollbackProjection(sessionId = selectedArchiveSessionId) {
    setRollbackBusy(true);
    try {
      const query: Record<string, string> = {};
      if (sessionId) query.session_id = sessionId;
      const response = await fetch(chatApiPath('/diffs.json', query), {
        headers: { Accept: 'application/json' },
        cache: 'no-store',
      });
      const payload = await response.json() as IonCodexGitRollback;
      if (!response.ok) throw new Error(`rollback_model_http_${response.status}`);
      setRollbackProjection(payload);
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'rollback_model_failed');
    } finally {
      setRollbackBusy(false);
    }
  }

  async function refreshMissionCommsThreads(options: { silent?: boolean } = {}) {
    if (!options.silent) setMissionCommsLoading(true);
    setMissionCommsError('');
    try {
      const response = await fetch(agentCommsApiPath('/list'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          limit: 80,
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `agent_comms_list_http_${response.status}`));
      }
      const threads = records(payload.threads).map(coerceJocCommsThread).filter((thread): thread is JocCommsThread => Boolean(thread));
      setMissionCommsThreads(threads);
      setSelectedMissionThreadId((previous) => {
        if (previous && threads.some((thread) => text(thread.thread_id, '') === previous)) return previous;
        return text(threads[0]?.thread_id, previous);
      });
    } catch (error) {
      setMissionCommsError(error instanceof Error ? error.message : 'agent_comms_list_failed');
    } finally {
      if (!options.silent) setMissionCommsLoading(false);
    }
  }

  async function refreshMissionCommsThread(threadId: string, options: { silent?: boolean } = {}) {
    const normalizedThreadId = text(threadId, '');
    if (!normalizedThreadId) return;
    const requestKey = `mission-thread:${normalizedThreadId}:${Date.now()}`;
    missionCommsThreadRequestRef.current = requestKey;
    if (!options.silent) setMissionCommsThreadLoading(true);
    setMissionCommsError('');
    try {
      const response = await fetch(agentCommsApiPath('/thread'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          thread_id: normalizedThreadId,
          limit: 240,
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `agent_comms_thread_http_${response.status}`));
      }
      if (missionCommsThreadRequestRef.current !== requestKey) return;
      const thread = coerceJocCommsThread(record(payload.thread));
      const messages = records(payload.messages).map(coerceJocCommsMessage).filter((message): message is JocCommsMessage => Boolean(message));
      setMissionCommsThreadDetail({
        thread,
        messages,
        source: 'agent comms api',
        loadedAt: new Date().toISOString(),
      });
    } catch (error) {
      if (missionCommsThreadRequestRef.current === requestKey) {
        setMissionCommsError(error instanceof Error ? error.message : 'agent_comms_thread_failed');
      }
    } finally {
      if (missionCommsThreadRequestRef.current === requestKey && !options.silent) setMissionCommsThreadLoading(false);
    }
  }

  async function captureCurrentDiffCheckpoint() {
    setRollbackBusy(true);
    setRollbackPreview(null);
    try {
      const response = await fetch(chatApiPath('/git/rollback/capture'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          confirmation: WRITE_CONFIRMATION_TOKEN,
          session_id: selectedArchiveSessionId,
          turn_id: latestAssistantKey,
          label: selectedSession ? chatTitleForSession(selectedSession) : 'codex chat current diff',
          source: 'codex_cockpit_rollback_drawer',
        }),
      });
      const payload = await response.json() as Record<string, unknown>;
      if (!response.ok || !payload.ok) throw new Error(text(payload.finding || record(payload.data).finding, `rollback_capture_http_${response.status}`));
      setActionNotice(`Captured diff checkpoint ${text(record(payload.data).checkpoint_id, 'checkpoint')}`);
      await refreshRollbackProjection(selectedArchiveSessionId);
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'rollback_capture_failed');
    } finally {
      setRollbackBusy(false);
    }
  }

  async function previewRollback(checkpoint: Record<string, unknown>) {
    setRollbackBusy(true);
    try {
      const response = await fetch(chatApiPath('/git/rollback/preview'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          checkpoint_id: text(checkpoint.checkpoint_id, ''),
          receipt_path: text(checkpoint.receipt_path, ''),
        }),
      });
      const payload = await response.json() as Record<string, unknown>;
      if (!response.ok || !payload.ok) throw new Error(text(payload.finding, `rollback_preview_http_${response.status}`));
      setRollbackPreview(record(payload.data));
      setActionNotice(text(record(payload.data).status, 'rollback preview ready'));
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'rollback_preview_failed');
    } finally {
      setRollbackBusy(false);
    }
  }

  async function applyRollback(checkpoint: Record<string, unknown>) {
    setRollbackBusy(true);
    try {
      const response = await fetch(chatApiPath('/git/rollback/apply'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          confirmation: WRITE_CONFIRMATION_TOKEN,
          checkpoint_id: text(checkpoint.checkpoint_id, ''),
          receipt_path: text(checkpoint.receipt_path, ''),
        }),
      });
      const payload = await response.json() as Record<string, unknown>;
      if (!response.ok || !payload.ok) throw new Error(text(payload.finding || record(payload.preview).status, `rollback_apply_http_${response.status}`));
      setRollbackPreview(record(payload.data));
      setActionNotice(`Rollback applied: ${text(record(payload.data).receipt_path, 'receipt written')}`);
      await refreshRollbackProjection(selectedArchiveSessionId);
      onRuntimeRefresh?.();
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'rollback_apply_failed');
    } finally {
      setRollbackBusy(false);
    }
  }

  function maybeStageArchiveBuffer(node: HTMLDivElement, bottomDistance: number) {
    if (!selectedSession || !selectedExcerpt) return false;
    const prefetchDistance = Math.max(
      ARCHIVE_PREFETCH_MIN_PX,
      node.clientHeight * ARCHIVE_PREFETCH_VIEWPORT_MULTIPLIER,
      node.scrollHeight * ARCHIVE_PREFETCH_SCROLL_RATIO,
    );
    const despawnDistance = Math.max(
      prefetchDistance + node.clientHeight,
      node.clientHeight * ARCHIVE_PREFETCH_DESPAWN_VIEWPORT_MULTIPLIER,
    );
    if (archivePrefetch && archivePrefetch.sessionId === selectedSession.session_id) {
      const bufferPixels = archiveBufferPixelSizeRef.current;
      if (archivePrefetch.direction === 'older') {
        if (bufferPixels > 0 && node.scrollTop <= Math.max(0, bufferPixels - ARCHIVE_BUFFER_PROMOTION_PX)) {
          applyArchivePrefetch(archivePrefetch, { preserveViewportTop: node.scrollTop });
          return true;
        }
        if (bufferPixels > 0 && node.scrollTop > bufferPixels + despawnDistance) {
          clearArchivePrefetch({ compensateRemoval: true });
          return true;
        }
      }
      if (archivePrefetch.direction === 'newer') {
        if (bufferPixels > 0 && bottomDistance <= Math.max(0, bufferPixels - ARCHIVE_BUFFER_PROMOTION_PX)) {
          const currentWindowPixels = Math.max(0, node.scrollHeight - bufferPixels);
          applyArchivePrefetch(archivePrefetch, { preserveViewportTop: node.scrollTop - currentWindowPixels });
          return true;
        }
        if (bufferPixels > 0 && bottomDistance > bufferPixels + despawnDistance) {
          clearArchivePrefetch({ compensateRemoval: true });
          return true;
        }
      }
      return true;
    }
    const scrollingDown = node.scrollTop >= archiveLastScrollTopRef.current;
    archiveLastScrollTopRef.current = node.scrollTop;
    const nearTop = node.scrollTop <= prefetchDistance;
    const nearBottom = bottomDistance <= prefetchDistance;
    if (scrollingDown && nearBottom) {
      void prefetchArchiveWindow('newer');
    } else if (!scrollingDown && nearTop) {
      void prefetchArchiveWindow('older');
    } else {
      if (nearBottom) void prefetchArchiveWindow('newer');
      if (nearTop) void prefetchArchiveWindow('older');
    }
    return false;
  }

  async function prefetchArchiveWindow(direction: ArchiveBufferDirection) {
    if (archiveBusy || archivePrefetchBusy || !selectedSession || !selectedSession.session_id) return;
    const nextStart = archiveWindowStartForDirection(direction, selectedExcerpt);
    if (!nextStart) return;
    if (
      archivePrefetch
      && archivePrefetch.sessionId === selectedSession.session_id
      && archivePrefetch.direction === direction
      && archivePrefetch.startIndex === nextStart
    ) return;
    if (archivePrefetch) clearArchivePrefetch({ compensateRemoval: true });
    else setArchivePrefetch(null);
    const requestKey = `${selectedSession.session_id}:${direction}:${nextStart}:${archiveSearch}`;
    archivePrefetchKeyRef.current = requestKey;
    setArchivePrefetchBusy(direction);
    try {
      const projection = await fetchArchiveProjection(selectedSession.session_id, nextStart, ARCHIVE_TRANSCRIPT_CHUNK_SIZE);
      if (archivePrefetchKeyRef.current !== requestKey) return;
      const excerpt = projection.selected_session_excerpt;
      const buffer: ArchiveTranscriptBuffer = {
        direction,
        sessionId: selectedSession.session_id,
        startIndex: numberValue(excerpt?.oldest_item_index) || nextStart,
        endIndex: numberValue(excerpt?.newest_item_index),
        items: records(excerpt?.items),
        projection,
        createdAt: new Date().toISOString(),
      };
      const node = archiveTranscriptRef.current;
      archiveBufferRenderAdjustmentRef.current = node
        ? {
            direction,
            beforeHeight: node.scrollHeight,
            beforeTop: node.scrollTop,
            key: archivePrefetchKey(buffer),
          }
        : null;
      setArchivePrefetch(buffer);
    } catch {
      if (archivePrefetchKeyRef.current === requestKey) setArchiveAction('Archive buffer prefetch failed');
    } finally {
      if (archivePrefetchKeyRef.current === requestKey) setArchivePrefetchBusy('');
    }
  }

  function applyArchivePrefetch(buffer: ArchiveTranscriptBuffer, options: { preserveViewportTop?: number } = {}) {
    if (typeof options.preserveViewportTop === 'number') {
      archiveBufferPromotionTopRef.current = options.preserveViewportTop;
      archiveSuppressNextAutoScrollRef.current = true;
    } else {
      archiveScrollTargetRef.current = buffer.direction === 'older' ? 'bottom' : 'top';
    }
    setSelectedSessionId(buffer.sessionId);
    setArchiveProjection(buffer.projection);
    updateOpenChatTabWindowStart(buffer.sessionId, buffer.startIndex);
    clearArchivePrefetch();
  }

  function clearArchivePrefetch(options: { compensateRemoval?: boolean } = {}) {
    if (options.compensateRemoval && archivePrefetch) {
      const node = archiveTranscriptRef.current;
      archiveBufferRemovalAdjustmentRef.current = node
        ? {
            direction: archivePrefetch.direction,
            beforeHeight: node.scrollHeight,
            beforeTop: node.scrollTop,
            key: archivePrefetchKey(archivePrefetch),
          }
        : null;
    } else {
      archiveBufferRemovalAdjustmentRef.current = null;
    }
    archivePrefetchKeyRef.current = '';
    archiveBufferRenderAdjustmentRef.current = null;
    if (!options.compensateRemoval) archiveBufferPixelSizeRef.current = 0;
    setArchivePrefetch(null);
    setArchivePrefetchBusy('');
  }

  function updateOpenChatTabWindowStart(sessionId: string, windowStart?: number) {
    const tabId = tabIdForSession(sessionId);
    setOpenChatTabs((previous) => previous.map((tab) => (
      tab.id === tabId
        ? { ...tab, windowStart: windowStart && windowStart > 0 ? windowStart : undefined, lastViewedAt: new Date().toISOString() }
        : tab
    )));
  }

  function chatTitleForSessionId(sessionId: string, fallback: unknown) {
    return text(chatTitleOverrides[sessionId] || fallback, text(sessionId, 'chat'));
  }

  function chatTitleForSession(session: IonCodexConversationArchiveSession) {
    return chatTitleForSessionId(session.session_id, sessionTitle(session));
  }

  function showChatTabInfo(event: ReactMouseEvent<HTMLElement>, sessionId: string) {
    if (renamingChatId) return;
    const rect = event.currentTarget.getBoundingClientRect();
    const viewportWidth = typeof window !== 'undefined' ? window.innerWidth : 1024;
    const viewportHeight = typeof window !== 'undefined' ? window.innerHeight : 768;
    const width = Math.min(Math.max(rect.width + 92, 286), Math.max(286, viewportWidth - 16), 390);
    const left = Math.min(Math.max(8, rect.left), Math.max(8, viewportWidth - width - 8));
    const top = Math.min(Math.max(8, rect.bottom + 6), Math.max(8, viewportHeight - 178));
    setChatTabHoverInfo({ sessionId, left, top, width });
  }

  function hideChatTabInfo() {
    setChatTabHoverInfo(null);
  }

  function startRenameChat(sessionId: string, fallback: unknown) {
    const normalizedSessionId = text(sessionId, '');
    if (!normalizedSessionId) return;
    hideChatTabInfo();
    setRenamingChatId(normalizedSessionId);
    setRenameDraft(chatTitleForSessionId(normalizedSessionId, fallback));
  }

  function commitRenameChat() {
    const sessionId = text(renamingChatId, '');
    const nextTitle = renameDraft.trim();
    if (!sessionId) return;
    if (nextTitle) {
      setChatTitleOverrides((previous) => ({ ...previous, [sessionId]: nextTitle }));
      setOpenChatTabs((previous) => previous.map((tab) => (
        tab.sessionId === sessionId ? { ...tab, title: nextTitle, lastViewedAt: new Date().toISOString() } : tab
      )));
    }
    setRenamingChatId('');
    setRenameDraft('');
  }

  function cancelRenameChat() {
    setRenamingChatId('');
    setRenameDraft('');
  }

  function selectOpenChatTab(tab: OpenChatTab) {
    if (tab.kind !== 'archive') return;
    const session = sessionFromOpenChatTab(tab);
    if (!session) return;
    setActiveChatTabId(tab.id);
    updateOpenChatTabWindowStart(tab.sessionId);
    void openSession(session, {
      activateArchive: false,
      addTab: false,
      showInChat: true,
    });
  }

  function markChatHistory(sessionId: string, patch: ChatHistoryMeta) {
    const normalizedSessionId = text(sessionId, '');
    if (!normalizedSessionId) return;
    setChatHistoryMeta((previous) => ({
      ...previous,
      [normalizedSessionId]: {
        ...(previous[normalizedSessionId] ?? {}),
        ...patch,
      },
    }));
  }

  function toggleFavoriteChat(sessionId: string) {
    const normalizedSessionId = text(sessionId, '');
    if (!normalizedSessionId) return;
    setFavoriteChatIds((previous) => {
      const exists = previous.includes(normalizedSessionId);
      const next = exists
        ? previous.filter((item) => item !== normalizedSessionId)
        : [normalizedSessionId, ...previous];
      return uniqueStrings(next).slice(0, 240);
    });
  }

  function closeOpenChatTab(tabId: string) {
    const closingIndex = openChatTabs.findIndex((tab) => tab.id === tabId);
    const closingTab = openChatTabs[closingIndex];
    if (closingTab?.sessionId) {
      markChatHistory(closingTab.sessionId, { lastClosedAt: new Date().toISOString() });
    }
    const nextTabs = openChatTabs.filter((tab) => tab.id !== tabId);
    setOpenChatTabs(nextTabs);
    if (activeChatTabId !== tabId) return;
    const replacement = nextTabs[Math.min(Math.max(closingIndex, 0), nextTabs.length - 1)] ?? null;
    if (replacement) {
      const replacementSession = sessionFromOpenChatTab(replacement);
      if (!replacementSession) {
        setActiveChatTabId('');
        showLiveChat();
        return;
      }
      setActiveChatTabId(replacement.id);
      void openSession(replacementSession, {
        activateArchive: false,
        addTab: false,
        showInChat: true,
      });
      return;
    }
    setActiveChatTabId('');
    showLiveChat();
  }

  function upsertOpenChatTab(session: IonCodexConversationArchiveSession, options: { windowStart?: number } = {}) {
    const openedAt = new Date().toISOString();
    const tab = {
      ...openChatTabFromSession(session, options),
      title: chatTitleForSession(session),
      lastOpenedAt: openedAt,
      lastViewedAt: openedAt,
    };
    markChatHistory(session.session_id, { lastOpenedAt: openedAt });
    setActiveChatTabId(tab.id);
    setOpenChatTabs((previous) => {
      const existing = previous.find((item) => item.id === tab.id);
      if (!existing) return [...previous, tab];
      return previous.map((item) => (
        item.id === tab.id
          ? { ...existing, ...tab, openedAt: existing.openedAt, lastClosedAt: existing.lastClosedAt }
          : item
      ));
    });
  }

  async function attachSession(session: IonCodexConversationArchiveSession) {
    if (!session.session_id || archiveBusy) return;
    setArchiveBusy(true);
    setArchiveAction('');
    try {
      const response = await fetch(chatApiPath('/archive/attach'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          session_id: session.session_id,
          confirmation: WRITE_CONFIRMATION_TOKEN,
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `archive_attach_http_${response.status}`));
      }
      setArchiveAction(`Attached ${chatTitleForSession(session)}`);
      await Promise.resolve(onRuntimeRefresh?.());
    } catch (error) {
      setArchiveAction(error instanceof Error ? error.message : 'archive_attach_failed');
    } finally {
      setArchiveBusy(false);
    }
  }

  async function copySessionCommand(session: IonCodexConversationArchiveSession, mode: 'resume' | 'fork') {
    const command = `codex ${mode} ${session.session_id}`;
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(command);
      setArchiveAction(`Copied: ${command}`);
    } else {
      setArchiveAction(command);
    }
  }

  function continueSessionInComposer(session: IonCodexConversationArchiveSession) {
    const title = chatTitleForSession(session);
    void attachSession(session);
    setExecutionMode('auto');
    setComposer([
      `Continue from attached Codex chat ${session.session_id}: ${title}`,
      `Project: ${projectLabel(session)}`,
      `Updated: ${formatSessionTime(session)}`,
      '',
    ].join('\n'));
    setChatViewMode('live');
    setActiveCodexTab('chat');
    setLeftDrawer('compose');
    setLeftDrawerOpen(true);
    setActionNotice(`Continuing from ${title}`);
  }

  async function createBranch(source: BranchSource) {
    setActionNotice('Creating branch...');
    try {
      const response = await fetch(chatApiPath('/branch'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          confirmation: WRITE_CONFIRMATION_TOKEN,
          lane_id: 'codex_general',
          parent_kind: source.kind,
          title: source.title || (source.kind === 'archive_session' ? 'Branch from past chat' : 'Branch from message'),
          objective: source.objective || source.message || source.title || '',
          prompt: source.prompt || '',
          parent_turn_id: text(source.turnId, ''),
          parent_session_id: source.sessionId || '',
          parent_role: source.role || '',
          parent_message: source.message || '',
          parent_message_sha256: source.messageSha256 || '',
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `branch_http_${response.status}`));
      }
      setActionNotice(`Branch drafted: ${text(record(payload.branch).title, 'branch')}`);
      setRightDrawer('branches');
      setRightDrawerOpen(true);
      await Promise.resolve(onRuntimeRefresh?.());
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'branch_failed');
    }
  }

  function branchSession(session: IonCodexConversationArchiveSession) {
    void createBranch({
      kind: 'archive_session',
      title: `Branch: ${chatTitleForSession(session)}`,
      objective: `Continue from archived Codex session ${session.session_id}: ${chatTitleForSession(session)}`,
      sessionId: session.session_id,
      role: 'archive_session',
      message: text(session.latest_user_snippet || session.first_user_snippet, ''),
    });
  }

  function branchMessage(source: BranchSource) {
    void createBranch(source);
  }

  async function copyBranchCommand(branch: Record<string, unknown>) {
    const command = text(record(branch.codex_fork).command_text, '') || text(branch.prompt, '');
    if (!command) return;
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(command);
      setActionNotice(record(branch.codex_fork).command_text ? `Copied: ${command}` : 'Copied branch prompt');
    } else {
      setActionNotice(command);
    }
  }

  function useBranchPrompt(branch: Record<string, unknown>) {
    const prompt = text(branch.prompt, '');
    if (!prompt) return;
    setComposer(prompt);
    setChatViewMode('live');
    setActiveCodexTab('chat');
    setRightDrawerOpen(false);
  }

  async function queueBranch(branch: Record<string, unknown>) {
    const prompt = text(branch.prompt, '');
    if (!prompt) return;
    setActionNotice('Queueing branch...');
    try {
      const response = await fetch(chatApiPath('/queue'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          lane_id: 'codex_general',
          objective: prompt,
          confirmation: WRITE_CONFIRMATION_TOKEN,
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `branch_queue_http_${response.status}`));
      }
      setActionNotice(`Queued branch: ${text(branch.title, 'branch')}`);
      await Promise.resolve(onRuntimeRefresh?.());
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'branch_queue_failed');
    }
  }

  function attachBranchSource(branch: Record<string, unknown>) {
    const sessionId = text(record(branch.parent).session_id, '');
    const session = allSessions.find((item) => item.session_id === sessionId);
    if (!session) {
      setActionNotice(sessionId ? `Session not loaded: ${sessionId}` : 'Branch has no archive session');
      return;
    }
    void attachSession(session);
  }

  function selectLeftDrawer(id: LeftDrawerId) {
    const sameDrawer = leftDrawer === id;
    setLeftDrawer(id);
    setLeftDrawerOpen(!sameDrawer || !leftDrawerOpen);
  }

  function setConnectionConnected(id: ConnectionId, connected: boolean) {
    const profile = connectionProfiles.find((item) => item.id === id);
    setConnectionState((previous) => ({ ...previous, [id]: connected }));
    setActionNotice(`${profile?.label ?? id} ${connected ? 'connected in cockpit' : 'disconnected from cockpit'}`);
  }

  function openConnectionDrawer(id: ConnectionId) {
    setLeftDrawer(connectionDrawerId(id));
    setLeftDrawerOpen(true);
  }

  function selectRightDrawer(id: RightDrawerId) {
    const sameDrawer = rightDrawer === id;
    setRightDrawer(id);
    setRightDrawerOpen(!sameDrawer || !rightDrawerOpen);
    if (id === 'missionProfile' && (!sameDrawer || !rightDrawerOpen)) {
      void refreshMissionCommsThreads({ silent: missionCommsThreads.length > 0 });
    }
  }

  if (surface === 'chat-cell') {
    return (
      <section className="ion-codex-workbench-shell ion-codex-chat-cell-shell" aria-label="Codex chat cell">
        <div className={`ion-codex-chat-cell-grid${rightDrawerOpen ? ' has-right-drawer-open' : ''}${rightDrawerOpen && rightDrawer === 'missionProfile' ? ' has-mission-right-drawer' : ''}`}>
          <main className="ion-codex-main-pane">
            <div className="ion-codex-active-pane">
              {renderChatPane()}
            </div>
          </main>
          <aside className="ion-codex-rail ion-codex-right-rail" aria-label="Chat drawer controls">
            <IconBar items={rightDrawers} active={rightDrawerOpen ? rightDrawer : undefined} onSelect={selectRightDrawer} />
          </aside>
          <aside className={`ion-codex-drawer-panel ion-codex-right-drawer${rightDrawerOpen ? ' is-open' : ''}${rightDrawer === 'missionProfile' ? ' is-mission-profile-drawer' : ''}`} aria-hidden={!rightDrawerOpen} aria-label="Chat drawer">
            <div className="ion-codex-drawer-head">
              <span>{drawerTitle(rightDrawers, rightDrawer)}</span>
              <button aria-label="Close chat drawer" onClick={() => setRightDrawerOpen(false)} title="Close chat drawer" type="button">
                <CloseIcon className="ion-close-icon" />
              </button>
            </div>
            <div className="ion-codex-drawer-body">{renderRightDrawer(rightDrawer)}</div>
          </aside>
        </div>
      </section>
    );
  }

  return (
    <section className={`ion-codex-workbench-shell${hideSubtabs ? ' has-external-subnav' : ''}`} aria-label="Codex cockpit workbench">
      {!hideSubtabs ? (
        <nav className="ion-codex-subtabs" aria-label="Codex workbench tabs">
          {codexWorkbenchTabs.map((tab) => (
            <button className={activeTab === tab.id ? 'is-active' : undefined} key={tab.id} onClick={() => selectCodexTab(tab.id)} type="button">
              {tab.label}
            </button>
          ))}
        </nav>
      ) : null}

      <div className={`ion-codex-workbench-grid${leftDrawerOpen ? ' has-left-drawer-open' : ''}${leftDrawerOpen && leftDrawer === 'files' ? ' has-file-drawer-open' : ''}${rightDrawerOpen ? ' has-right-drawer-open' : ''}${rightDrawerOpen && rightDrawer === 'missionProfile' ? ' has-mission-right-drawer' : ''}`}>
        <aside className="ion-codex-rail ion-codex-left-rail" aria-label="Left drawer controls">
          <IconBar items={leftRailItems} active={leftDrawerOpen ? leftDrawer : undefined} onSelect={selectLeftDrawer} />
        </aside>
        <aside className={`ion-codex-drawer-panel ion-codex-left-drawer${leftDrawerOpen ? ' is-open' : ''}${leftDrawer === 'files' ? ' is-files-drawer' : ''}`} aria-hidden={!leftDrawerOpen} aria-label="Left drawer">
          <div className="ion-codex-drawer-head">
            <span>{drawerTitle(leftRailItems, leftDrawer)}</span>
            <button aria-label="Close left drawer" onClick={() => setLeftDrawerOpen(false)} title="Close left drawer" type="button">
              <CloseIcon className="ion-close-icon" />
            </button>
          </div>
          <div className="ion-codex-drawer-body">{renderLeftDrawer(leftDrawer)}</div>
        </aside>

        <main className="ion-codex-main-pane">
          <div className="ion-codex-active-pane">
            {activeTab === 'chat' && renderChatPane()}
            {activeTab === 'ion' && renderIonOrchestrationPane()}
            {activeTab === 'ide' && renderIdePane()}
            {activeTab === 'archive' && renderArchivePane()}
            {activeTab === 'context' && renderContextPane()}
            {activeTab === 'settings' && renderSettingsPane()}
            {activeTab === 'hooks' && renderHooksPane()}
            {activeTab === 'skills' && renderSkillsPane()}
            {activeTab === 'tools' && renderToolsPane()}
            {activeTab === 'traces' && renderTracesPane()}
            {activeTab === 'queue' && renderQueuePane()}
          </div>
        </main>

        <aside className="ion-codex-rail ion-codex-right-rail" aria-label="Right drawer controls">
          <IconBar items={rightDrawers} active={rightDrawerOpen ? rightDrawer : undefined} onSelect={selectRightDrawer} />
        </aside>
        <aside className={`ion-codex-drawer-panel ion-codex-right-drawer${rightDrawerOpen ? ' is-open' : ''}${rightDrawer === 'missionProfile' ? ' is-mission-profile-drawer' : ''}`} aria-hidden={!rightDrawerOpen} aria-label="Right drawer">
          <div className="ion-codex-drawer-head">
            <span>{drawerTitle(rightDrawers, rightDrawer)}</span>
            <button aria-label="Close right drawer" onClick={() => setRightDrawerOpen(false)} title="Close right drawer" type="button">
              <CloseIcon className="ion-close-icon" />
            </button>
          </div>
          <div className="ion-codex-drawer-body">{renderRightDrawer(rightDrawer)}</div>
        </aside>
      </div>
      {contextMapBottomBarSlot && (activeTab === 'chat' || activeTab === 'ion') ? createPortal(renderContextMapBottomControls(), contextMapBottomBarSlot) : null}
    </section>
  );

  function toggleCommandPanel(panel: ChatCommandPanelId) {
    setCommandPanel((previous) => (previous === panel ? '' : panel));
  }

  function mentionAttachment(attachment: Record<string, unknown>) {
    const sessionId = text(attachment.session_id || attachment.codex_session_id || attachment.id, '');
    const label = text(attachment.title || attachment.label || attachment.name || sessionId, 'attachment');
    const mention = sessionId ? `@${sessionShortText(sessionId)}` : `@${label.replace(/\s+/g, '_')}`;
    setComposer((previous) => appendDictationText(previous, mention));
  }

  function mentionContextRef(ref: string) {
    setComposer((previous) => appendDictationText(previous, contextRefMention(ref)));
  }

  function mentionAllContextRefs() {
    const mentions = selectedContextRefs.map(contextRefMention).join(' ');
    setComposer((previous) => appendDictationText(previous, mentions));
  }

  function addContextRefs(refs: string[]) {
    setSelectedContextRefs((previous) => normalizeContextRefs([...previous, ...refs]));
  }

  function removeContextRefs(refs: string[]) {
    const remove = new Set(refs);
    setSelectedContextRefs((previous) => previous.filter((ref) => !remove.has(ref)));
  }

  function fileTreeEntryRefs(entry: CodexFileTreeEntry) {
    if (entry.kind === 'file') return [entry.path];
    const prefix = `${entry.path.replace(/\/+$/, '')}/`;
    return fileTreeEntries.filter((candidate) => candidate.kind === 'file' && candidate.path.startsWith(prefix)).map((candidate) => candidate.path);
  }

  function toggleFileTreeEntry(entry: CodexFileTreeEntry) {
    const refs = fileTreeEntryRefs(entry);
    if (!refs.length) return;
    const selected = refs.every((ref) => selectedContextRefs.includes(ref));
    if (selected) removeContextRefs(refs);
    else addContextRefs(refs);
  }

  function toggleContextAtlasNode(node: CodexAtlasNode) {
    if (!node.ref) return;
    setSelectedContextAtlasNodeId(node.id);
    if (selectedContextRefs.includes(node.ref)) removeContextRefs([node.ref]);
    else addContextRefs([node.ref]);
  }

  function renderFilePickerPanel() {
    const fileQuery = fileTreeSearch.trim().toLowerCase();
    const visibleEntries = fileQuery
      ? fileTreeEntries.filter((entry) => entry.path.toLowerCase().includes(fileQuery))
      : fileTreeEntries;
    const visibleFileCount = visibleEntries.filter((entry) => entry.kind === 'file').length;
    const visibleDirCount = visibleEntries.filter((entry) => entry.kind === 'dir').length;
    const graphBranches = records(runtime.context_package_graph?.branches);
    const browserDom = record(runtime.extension_micro_shell?.browser_gpt_dom);
    const pagePerception = record(runtime.extension_micro_shell?.page_perception);
    const graphStatus = text(runtime.context_package_graph?.status, 'context graph');
    const graphBlockedCount = numberValue(runtime.context_package_graph?.blocked_count);
    const graphReadyCount = numberValue(runtime.context_package_graph?.candidate_review_ready_count);
    const trunkNodes: CodexAtlasNode[] = [
      {
        id: 'trunk:codex-chat',
        kind: 'trunk',
        title: 'Codex Chat',
        detail: `${text(chat?.capsule?.entry_count, 0)} context floor rows / ${text(record(chat?.conversation_summary).turn_count || runtime.top_bar.codex_capsule_chat_turn_count || 0, 0)} turns`,
        meta: text(chat?.verdict || runtime.top_bar.codex_capsule_chat_verdict || capsuleHealth.label, 'ready'),
        ref: 'ION/05_context/current/codex_solo',
        tone: capsuleHealth.tone as CodexAtlasTone,
        icon: <CodexIcon />,
      },
      {
        id: 'trunk:browser-gpt',
        kind: 'trunk',
        title: 'Browser GPT',
        detail: `${text(browserDom.status || runtime.top_bar.browser_gpt_dom_status, 'dom profile')} / ${text(browserDom.profile_count || 0, 0)} profiles`,
        meta: text(browserDom.latest_profile_id || browserDom.target_url || 'DOM bridge'),
        ref: 'browser_extension',
        tone: text(browserDom.status || runtime.top_bar.browser_gpt_dom_status, '').toLowerCase().includes('blocked') ? 'blocked' : 'ready',
        icon: <LensIcon />,
      },
      {
        id: 'trunk:cockpit-ui',
        kind: 'trunk',
        title: 'Cockpit UI',
        detail: 'chat shell / drawers / context controls',
        meta: text(runtime.top_bar.local_service_status || runtime.top_bar.helixion_rebuild_status || 'local surface'),
        ref: 'ION/08_ui/joc_cockpit_shell',
        tone: 'active',
        icon: <ProjectsIcon />,
      },
      {
        id: 'trunk:kernel',
        kind: 'trunk',
        title: 'Kernel Model',
        detail: `${text(runtime.top_bar.codex_cli_workbench_tool_count || 0, 0)} tools / ${text(runtime.top_bar.codex_cli_workbench_hook_group_count || 0, 0)} hook groups`,
        meta: text(cli?.verdict || runtime.top_bar.codex_cli_workbench_verdict || 'projection'),
        ref: 'ION/04_packages/kernel',
        tone: 'ready',
        icon: <SettingsIcon />,
      },
      {
        id: 'trunk:current-context',
        kind: 'trunk',
        title: 'Current Context',
        detail: `${text(runtime.top_bar.context_package_count || graphBranches.length, 0)} packages / ${text(graphReadyCount, 0)} ready`,
        meta: graphStatus,
        ref: 'ION/05_context/current',
        tone: graphBlockedCount ? 'blocked' : graphReadyCount ? 'ready' : 'watch',
        icon: <ArchiveIcon />,
      },
      {
        id: 'trunk:domain-weaver',
        kind: 'trunk',
        title: 'Domain Weaver',
        detail: `${text(pagePerception.domain_count || runtime.top_bar.page_perception_domain_count || 0, 0)} domains / branch map`,
        meta: 'projection graph',
        ref: 'ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json',
        tone: 'watch',
        icon: <BranchIcon />,
      },
    ];
    const branchNodes: CodexAtlasNode[] = graphBranches.map((branch, index) => {
      const branchPath = text(branch.path || branch.candidate_capsule_path || branch.accepted_capsule_path, `branch ${index + 1}`);
      const blockers = stringList(branch.blockers);
      const gaps = stringList(branch.gaps);
      const readFirst = stringList(branch.read_first);
      const surfaceCounts = record(branch.surface_counts);
      const surfaceCountLabel = Object.entries(surfaceCounts)
        .filter(([, value]) => numberValue(value))
        .slice(0, 3)
        .map(([key, value]) => `${key}:${numberValue(value)}`)
        .join(' / ');
      const ref = text(branch.candidate_capsule_path || branch.accepted_capsule_path || branchPath, branchPath);
      return {
        id: `branch:${branchPath}`,
        kind: 'branch',
        title: branchPath,
        detail: text(branch.package_type || branch.maturity_level || branch.classification || branch.promotion_readiness, 'context branch'),
        meta: blockers.length ? `${blockers.length} blockers` : gaps.length ? `${gaps.length} gaps` : readFirst.length ? `${readFirst.length} read-first` : surfaceCountLabel || 'candidate branch',
        ref,
        parent: text(branch.parent_ref, ''),
        tone: blockers.length ? 'blocked' : gaps.length ? 'watch' : 'ready',
        icon: <BranchIcon />,
      };
    });
    const chatNodes: CodexAtlasNode[] = sortByRecent(allSessions).slice(0, 72).map((session) => {
      const packet = isQueueRunnerPacket(session);
      const latest = formatCompactDate(sessionTimestamp(session));
      const sessionPath = text(session.session_path, '');
      const ref = sessionPath && !sessionPath.startsWith('/') ? sessionPath : `archive:${session.session_id}`;
      const open = openChatSessionIds.has(session.session_id) || selectedArchiveSessionId === session.session_id;
      return {
        id: `chat:${session.session_id}`,
        kind: packet ? 'queue' : 'chat',
        title: chatTitleForSession(session),
        detail: `${projectLabel(session)} / ${text(session.model, 'model unknown')}`,
        meta: [packet ? 'packet' : 'chat', latest || sessionShortText(session.session_id)].filter(Boolean).join(' / '),
        ref,
        tone: open ? 'active' : packet ? 'watch' : 'ready',
        icon: packet ? <QueueIcon /> : <SessionsIcon />,
      };
    });
    const timelineNodes: CodexAtlasNode[] = (runtime.timeline ?? []).slice(-80).reverse().map((event, index) => {
      const raw = record(event);
      const path = text(raw.path, '');
      const status = text(raw.status, '');
      const safePath = path && !path.startsWith('/') ? path : '';
      const time = text(raw.time, '');
      return {
        id: `timeline:${time || index}`,
        kind: 'timeline',
        title: text(raw.event_type || raw.source || `event ${index + 1}`, `event ${index + 1}`).replaceAll('_', ' '),
        detail: text(raw.detail || raw.source || status, 'timeline event'),
        meta: [status, formatCompactDate(time)].filter(Boolean).join(' / ') || 'timeline',
        ref: safePath || `atlas:timeline:${index}`,
        tone: status.toLowerCase().includes('blocked') || status.toLowerCase().includes('fail') ? 'blocked' : status.toLowerCase().includes('warn') ? 'watch' : 'muted',
        icon: <StatusIcon />,
      };
    });
    const atlasNodesByLens: Record<CodexAtlasLensId, CodexAtlasNode[]> = {
      trunks: trunkNodes,
      branches: branchNodes,
      chats: chatNodes.filter((node) => node.kind === 'chat'),
      timeline: [...chatNodes.filter((node) => node.kind === 'queue'), ...timelineNodes],
      files: visibleEntries.map((entry) => ({
        id: `file:${entry.path}`,
        kind: 'file',
        title: entry.path,
        detail: entry.kind === 'file' ? formatBytes(entry.bytes) : `${fileTreeEntryRefs(entry).length} files`,
        meta: entry.kind,
        ref: entry.path,
        tone: 'ready',
        icon: entry.kind === 'dir' ? <ProjectsIcon /> : <DocsIcon />,
      })),
    };
    const atlasQuery = (contextAtlasLens === 'files' ? fileTreeSearch : contextAtlasQuery).trim().toLowerCase();
    const atlasNodes = atlasNodesByLens[contextAtlasLens] ?? [];
    const visibleAtlasNodes = contextAtlasLens === 'files'
      ? atlasNodes
      : atlasQuery
        ? atlasNodes.filter((node) => [node.title, node.detail, node.meta, node.ref, node.parent].join(' ').toLowerCase().includes(atlasQuery))
        : atlasNodes;
    const selectedAtlasNode = visibleAtlasNodes.find((node) => node.id === selectedContextAtlasNodeId) ?? visibleAtlasNodes[0];
    const atlasLenses: Array<{ id: CodexAtlasLensId; label: string; icon: ReactNode; count: number; title: string }> = [
      { id: 'trunks', label: 'trunks', icon: <CodexIcon />, count: trunkNodes.length, title: 'Core trunks' },
      { id: 'branches', label: 'branches', icon: <BranchIcon />, count: branchNodes.length, title: 'Context package branches' },
      { id: 'chats', label: 'chats', icon: <SessionsIcon />, count: chatNodes.filter((node) => node.kind === 'chat').length, title: 'Archived chats' },
      { id: 'timeline', label: 'timeline', icon: <StatusIcon />, count: timelineNodes.length + chatNodes.filter((node) => node.kind === 'queue').length, title: 'Timeline and queue packets' },
      { id: 'files', label: 'files', icon: <DocsIcon />, count: visibleFileCount, title: 'Filesystem refs' },
    ];
    return (
      <div className="ion-codex-file-picker-drawer ion-codex-context-atlas-drawer" aria-label="Context atlas reference drawer">
        <div className="ion-codex-context-atlas-map" aria-label="Context atlas map">
          <button className={contextAtlasLens === 'trunks' ? 'is-active' : undefined} onClick={() => setContextAtlasLens('trunks')} title="Core trunks" type="button">
            <span><CodexIcon /></span>
            <b>{trunkNodes.length}</b>
            <em>trunks</em>
          </button>
          <button className={contextAtlasLens === 'branches' ? 'is-active' : undefined} onClick={() => setContextAtlasLens('branches')} title="Branch graph" type="button">
            <span><BranchIcon /></span>
            <b>{branchNodes.length}</b>
            <em>{graphBlockedCount ? `${graphBlockedCount} blocked` : `${graphReadyCount} ready`}</em>
          </button>
          <button className={contextAtlasLens === 'chats' ? 'is-active' : undefined} onClick={() => setContextAtlasLens('chats')} title="Chat archives" type="button">
            <span><SessionsIcon /></span>
            <b>{chatNodes.filter((node) => node.kind === 'chat').length}</b>
            <em>saved chats</em>
          </button>
          <button className={selectedContextRefCount ? 'is-selected' : undefined} onClick={mentionAllContextRefs} disabled={!selectedContextRefCount} title="Mention selected context refs" type="button">
            <span><DocsIcon /></span>
            <b>{selectedContextRefCount}</b>
            <em>bundle</em>
          </button>
        </div>
        <div className="ion-codex-context-atlas-lenses" role="tablist" aria-label="Context atlas lenses">
          {atlasLenses.map((lens) => (
            <button
              aria-selected={contextAtlasLens === lens.id}
              className={contextAtlasLens === lens.id ? 'is-active' : undefined}
              key={lens.id}
              onClick={() => setContextAtlasLens(lens.id)}
              role="tab"
              title={lens.title}
              type="button"
            >
              <span aria-hidden="true">{lens.icon}</span>
              <b>{lens.count}</b>
              <em>{lens.label}</em>
            </button>
          ))}
        </div>
        <div className="ion-codex-file-picker-search ion-codex-context-atlas-search">
          <input
            aria-label="Search context atlas"
            onChange={(event) => {
              if (contextAtlasLens === 'files') setFileTreeSearch(event.currentTarget.value);
              else setContextAtlasQuery(event.currentTarget.value);
            }}
            placeholder={contextAtlasLens === 'files' ? '@ file or folder' : '@ trunk, branch, chat, packet'}
            value={contextAtlasLens === 'files' ? fileTreeSearch : contextAtlasQuery}
          />
          <b>{contextAtlasLens === 'files' ? (fileTreeBusy && !fileTreeEntries.length ? '...' : `${visibleDirCount}/${visibleFileCount}`) : `${visibleAtlasNodes.length}/${atlasNodes.length}`}</b>
          <b>{selectedContextRefCount}</b>
        </div>
        {contextAtlasLens === 'files' ? (
          <div className="ion-codex-context-atlas-file-controls">
            <div className="ion-codex-file-picker-head">
              <label>
                <span>root</span>
                <input aria-label="File picker root" onChange={(event) => setFileTreeRoot(event.currentTarget.value)} value={fileTreeRoot} />
              </label>
              <label>
                <span>depth</span>
                <input aria-label="File picker depth" max={6} min={1} onChange={(event) => setFileTreeDepth(Math.min(6, Math.max(1, Number(event.currentTarget.value) || 1)))} type="number" value={fileTreeDepth} />
              </label>
              <button onClick={() => setFileTreeRefreshVersion((previous) => previous + 1)} title="Refresh file tree" type="button">REFRESH</button>
            </div>
            <div className="ion-codex-file-picker-roots">
              {FILE_PICKER_ROOTS.map((root) => (
                <button className={fileTreeRoot === root ? 'is-active' : undefined} key={root} onClick={() => setFileTreeRoot(root)} title={root} type="button">{fileRootLabel(root)}</button>
              ))}
            </div>
          </div>
        ) : (
          <div className="ion-codex-context-atlas-branch-preview" aria-label="Selected atlas branch">
            <span>{selectedAtlasNode?.icon}</span>
            <div>
              <b>{selectedAtlasNode?.title ?? 'No atlas node'}</b>
              <em>{selectedAtlasNode ? `${selectedAtlasNode.detail} / ${selectedAtlasNode.meta}` : 'No refs in this lens'}</em>
            </div>
            <code>{selectedAtlasNode?.ref ?? 'empty'}</code>
          </div>
        )}
        <div className="ion-codex-file-picker-grid">
          <div className={`ion-codex-file-tree${contextAtlasLens === 'files' ? ' is-files' : ' is-atlas'}`} aria-label={contextAtlasLens === 'files' ? 'Available files' : 'Available context atlas refs'}>
            {contextAtlasLens === 'files' ? (
              <>
                {fileTreeBusy && !fileTreeEntries.length ? <div className="ion-codex-file-picker-empty">SCANNING {fileTreeRoot}</div> : null}
                {fileTreeBusy && fileTreeEntries.length ? <div className="ion-codex-file-picker-inline-status">REFRESHING</div> : null}
                {fileTreeError ? <div className="ion-codex-file-picker-empty is-error">{fileTreeError}</div> : null}
                {!fileTreeBusy && !fileTreeError && !visibleEntries.length ? <div className="ion-codex-file-picker-empty">NO FILES</div> : null}
                {visibleEntries.map((entry) => {
                  const refs = fileTreeEntryRefs(entry);
                  const selected = refs.length > 0 && refs.every((ref) => selectedContextRefs.includes(ref));
                  const partial = !selected && refs.some((ref) => selectedContextRefs.includes(ref));
                  return (
                    <button
                      aria-checked={partial ? 'mixed' : selected}
                      className={`ion-codex-file-tree-row is-${entry.kind}${selected ? ' is-selected' : ''}${partial ? ' is-partial' : ''}`}
                      key={entry.path}
                      onClick={() => toggleFileTreeEntry(entry)}
                      role="checkbox"
                      style={{ '--file-depth': fileTreeDepthLevel(entry.path) } as CSSProperties}
                      title={entry.path}
                      type="button"
                    >
                      <span className="ion-codex-file-check">{selected ? <CheckIcon /> : partial ? '+' : ''}</span>
                      {entry.kind === 'dir' ? <ProjectsIcon className="ion-codex-file-kind-icon" /> : <DocsIcon className="ion-codex-file-kind-icon" />}
                      <span>{entry.path}</span>
                      <em>{entry.kind === 'file' ? formatBytes(entry.bytes) : `${refs.length} files`}</em>
                    </button>
                  );
                })}
              </>
            ) : (
              <>
                {!visibleAtlasNodes.length ? <div className="ion-codex-file-picker-empty">NO ATLAS REFS</div> : null}
                {visibleAtlasNodes.map((node) => {
                  const selected = selectedContextRefs.includes(node.ref);
                  return (
                    <button
                      aria-checked={selected}
                      className={`ion-codex-context-atlas-node is-${node.kind} is-${node.tone}${selected ? ' is-selected' : ''}${selectedContextAtlasNodeId === node.id ? ' is-focused' : ''}`}
                      key={node.id}
                      onClick={() => toggleContextAtlasNode(node)}
                      onMouseEnter={() => setSelectedContextAtlasNodeId(node.id)}
                      role="checkbox"
                      title={node.ref}
                      type="button"
                    >
                      <span className="ion-codex-file-check">{selected ? <CheckIcon /> : '+'}</span>
                      <span className="ion-codex-context-atlas-node-icon" aria-hidden="true">{node.icon}</span>
                      <span className="ion-codex-context-atlas-node-copy">
                        <b>{node.title}</b>
                        <em>{node.detail}</em>
                      </span>
                      <span className="ion-codex-context-atlas-node-meta">{node.meta}</span>
                    </button>
                  );
                })}
              </>
            )}
          </div>
          <aside className="ion-codex-file-selected" aria-label="Selected file references">
            <div className="ion-codex-file-selected-head">
              <span>bundle</span>
              <b>{selectedContextRefCount}</b>
              <button disabled={!selectedContextRefCount} onClick={mentionAllContextRefs} type="button">@</button>
              <button disabled={!selectedContextRefCount} onClick={() => setSelectedContextRefs([])} type="button">CLEAR</button>
            </div>
            <div className="ion-codex-file-selected-list">
              {selectedContextRefs.map((ref) => (
                <div className="ion-codex-file-selected-row" key={ref}>
                  <button onClick={() => mentionContextRef(ref)} title={`Insert ${contextRefMention(ref)}`} type="button">{contextRefMention(ref)}</button>
                  <span title={ref}>{ref}</span>
                  <button aria-label={`Remove ${ref}`} onClick={() => removeContextRefs([ref])} title={`Remove ${ref}`} type="button">
                    <CloseIcon className="ion-close-icon" />
                  </button>
                </div>
              ))}
              {!selectedContextRefs.length ? <div className="ion-codex-file-picker-empty">NO REFS</div> : null}
            </div>
          </aside>
        </div>
      </div>
    );
  }

  function renderChatCommandBar() {
    const carrierLabel = text(record(chat?.response_carrier).uses_codex_cli ? 'Codex CLI' : record(runtime.carrier).mode || 'Codex CLI', 'Codex CLI');
    const queueLabel = queueTone === 'playing' ? 'playing' : queueTone === 'paused' ? 'paused' : queuedRequestCount ? 'queued' : workerActive ? 'worker active' : 'empty';
    const contextCommand = currentContextCommandProjection();
    const commandCell = (panel: Exclude<ChatCommandPanelId, ''>, className: string, body: ReactNode, title: string) => (
      <div className={`ion-codex-command-cell${commandPanel === panel ? ' is-expanded' : ''}`} onMouseEnter={() => setCommandPanel(panel)} onMouseLeave={() => setCommandPanel('')} key={panel}>
        <button aria-label={title} className={`${className}${commandPanel === panel ? ' is-active' : ''}`} onClick={() => toggleCommandPanel(panel)} onFocus={() => setCommandPanel(panel)} title={title} type="button">
          {body}
        </button>
        {commandPanel === panel ? renderChatCommandPanel(panel) : null}
      </div>
    );
    return (
      <div className="ion-codex-command-bar">
        {commandCell('agent', 'ion-codex-command-card is-agent', <b>{agentIdentity.displayName}</b>, agentIdentity.title)}
        <div className="ion-codex-command-cell is-control">
          <label className="ion-codex-command-select is-mode" title={`Mode: ${agentModeOption.label}. ${agentModeOption.detail}`}>
            <span>mode</span>
            <select
              aria-label="Agent mode"
              onChange={(event) => {
                const nextMode = event.currentTarget.value as AgentModeId;
                const option = agentModeOptions.find((item) => item.id === nextMode) ?? agentModeOptions[0];
                setAgentMode(nextMode);
                setExecutionMode(option.executionMode);
              }}
              value={agentMode}
            >
              {agentModeOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
        </div>
        {commandCell('context', `ion-codex-command-card is-${contextCommand.tone}`, <b>{contextCommand.label}</b>, `Context system: ${contextCommand.detail}`)}
        {commandCell('attachments', `ion-codex-command-card${totalAttachmentCount ? ' is-ready' : ' is-empty'}`, (
          <>
            <ArchiveIcon className="ion-codex-command-icon" />
            <b>{totalAttachmentCount}</b>
          </>
        ), `Attachments: ${totalAttachmentCount} ${totalAttachmentCount ? 'hot refs' : 'none'}`)}
        {commandCell('queue', `ion-codex-command-card is-queue-${queueTone}`, (
          <>
            <QueueIcon className="ion-codex-command-icon" />
            <b>{queuedRequestCount}</b>
          </>
        ), `Queue: ${queuedRequestCount} / ${queueLabel}`)}
        {commandCell('staged', `ion-codex-command-card${messageQueueState.items.length ? ' is-ready' : ' is-empty'}`, (
          <>
            <CodexIcon className="ion-codex-command-icon" />
            <b>{messageQueueState.items.length}</b>
          </>
        ), `Staged: ${messageQueueState.items.length} / ${activeMessageQueueGroup?.name || 'working'}`)}
        {commandCell('diffs', `ion-codex-command-card${diffCheckpointCount ? ' is-ready' : ' is-empty'}`, (
          <>
            <RollbackIcon className="ion-codex-command-icon" />
            <b>{diffCheckpointCount}</b>
          </>
        ), `Diffs: ${diffCheckpointCount} / ${text(record(rollback?.current_git).branch || 'git', 'git')}`)}
        <div className="ion-codex-command-cell is-control">
          <label className="ion-codex-command-select is-model" title={`Model: ${activeModelChoiceLabel}`}>
            <span>model</span>
            <select aria-label="Codex model" onChange={(event) => {
              const nextModel = event.currentTarget.value;
              setSelectedModelOverride(nextModel === 'auto' ? '' : nextModel);
            }} value={selectedModelOverride || 'auto'}>
              <option value="auto">Auto / {defaultModelLabel}</option>
              {modelOptions.map((option) => <option key={option} value={option}>{option}</option>)}
            </select>
          </label>
        </div>
        <div className="ion-codex-command-cell is-control">
          <label className="ion-codex-command-select is-thinking" title={`Thinking: ${thinkingModeOption.label}`}>
            <span>thinking</span>
            <select aria-label="Thinking mode" onChange={(event) => setThinkingMode(event.currentTarget.value as ThinkingModeId)} value={thinkingMode}>
              {thinkingModeOptions.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
            </select>
          </label>
        </div>
        {commandCell('carrier', 'ion-codex-command-card is-carrier', <b>{carrierLabel}</b>, `Carrier: ${carrierLabel} / ${workerActive ? workerDuration || 'active' : 'ready'}`)}
      </div>
    );
  }

  function currentContextCommandProjection() {
    const rows = buildContextSystemInventoryRows();
    const row = selectedContextSystemInventoryRow(rows);
    const status = text(row?.status, 'pending');
    const statusLower = status.toLowerCase();
    const tone = row
      ? statusLower.includes('block') || statusLower.includes('missing')
        ? 'blocked'
        : statusLower.includes('pending') || statusLower.includes('watch')
          ? 'watch'
          : 'ready'
      : capsuleHealth.tone;
    const fallbackLabel = text(agentIdentity.displayName || agentIdentity.roleId || 'context system', 'context system');
    const label = text(row?.displayName || row?.roleId || row?.domainId || fallbackLabel, fallbackLabel);
    const detail = row
      ? `${text(row.domainId, 'domain pending')} / ${text(row.roleId, 'role pending')} / ${status}`
      : `${text(agentIdentity.domain, 'domain pending')} / ${text(agentIdentity.roleId, 'role pending')} / context system pending`;
    const reference = text(row?.cardPath, row ? 'context card unmapped' : 'context system pending');
    const counts = row
      ? `${row.contextRefCount} refs / ${row.mappedBindings.length} bindings / ${row.mappedFreshChats.length} chats / ${row.mappedOpenTabs.length} tabs`
      : 'no projected context-system inventory row';
    return { row, label, detail, reference, counts, tone };
  }

  function renderChatCommandPanel(panel: ChatCommandPanelId) {
    if (panel === 'agent') {
      return (
        <div className="ion-codex-command-popover">
          <b>{agentIdentity.displayName}</b>
          <span>{agentIdentity.roleId} / {agentIdentity.instanceId}</span>
          <span>{agentIdentity.domain} / {agentIdentity.carrier} / {agentIdentity.source}</span>
          <span>{agentModeOption.detail}</span>
          <code>{agentIdentity.detail}</code>
          <code>{text(rolePhaseContract.authority_claim, 'bounded carrier mode')}</code>
        </div>
      );
    }
    if (panel === 'context') {
      const contextCommand = currentContextCommandProjection();
      return (
        <div className={`ion-codex-command-popover is-${contextCommand.tone}`}>
          <b>{contextCommand.label}</b>
          <span>{contextCommand.detail}</span>
          <span>{contextCommand.counts}</span>
          <code>{contextCommand.reference}</code>
          <button onClick={() => { setLeftDrawer('context'); setLeftDrawerOpen(true); }} type="button">OPEN CONTEXT</button>
        </div>
      );
    }
    if (panel === 'attachments') {
      return (
        <div className="ion-codex-command-popover">
          <b>{totalAttachmentCount} context refs</b>
          {selectedContextRefs.slice(0, 12).map((ref) => (
            <button key={ref} onClick={() => mentionContextRef(ref)} type="button">
              {contextRefMention(ref)} / {ref}
            </button>
          ))}
          {archiveAttachments.slice(0, 8).map((attachment, index) => (
            <button key={`${text(attachment.session_id || attachment.id, 'attachment')}-${index}`} onClick={() => mentionAttachment(attachment)} type="button">
              @{sessionShortText(text(attachment.session_id || attachment.codex_session_id || attachment.id, `attachment-${index}`))} / {text(attachment.title || attachment.label || attachment.name, 'attached chat')}
            </button>
          ))}
          {!totalAttachmentCount ? <span>No context refs selected.</span> : null}
        </div>
      );
    }
    if (panel === 'queue') {
      return (
        <div className={`ion-codex-command-popover is-queue-${queueTone}`}>
          <b>{queuedRequestCount} queued / {messageQueueState.items.length} staged</b>
          <span>{queueTone === 'paused' ? 'Queue is paused locally.' : workerActive ? `Worker active ${workerDuration || 'now'}.` : text(queue.verdict, 'queue ready')}</span>
          <button onClick={() => setQueuePaused((previous) => !previous)} type="button">{queuePaused ? 'RESUME QUEUE' : 'PAUSE QUEUE'}</button>
          <button onClick={() => { setRightDrawer('messageQueue'); setRightDrawerOpen(true); }} type="button">OPEN QUEUE</button>
        </div>
      );
    }
    if (panel === 'staged') {
      return (
        <div className="ion-codex-command-popover">
          <b>{messageQueueState.items.length} staged messages</b>
          {messageQueueState.items.slice(0, 8).map((item, index) => <span key={item.id}>#{index + 1} {item.title}</span>)}
          {!messageQueueState.items.length ? <span>No staged messages.</span> : null}
        </div>
      );
    }
    if (panel === 'diffs') {
      return (
        <div className="ion-codex-command-popover">
          <b>{currentEditCount} current edits / {diffCheckpointCount} checkpoints</b>
          <span>{text(record(rollback?.current_git).branch, 'branch unknown')} / dirty {text(record(rollback?.current_git).dirty, 'unknown')}</span>
          <button onClick={() => { setRightDrawer('rollback'); setRightDrawerOpen(true); setEditDrawerView('current'); }} type="button">OPEN EDITS</button>
        </div>
      );
    }
    if (panel === 'model') {
      return (
        <div className="ion-codex-command-popover">
          <b>{activeModelChoiceLabel}</b>
          <span>Thinking: {thinkingModeOption.label}</span>
          <span>Model and thinking selections are included in chat turn payloads for the Codex carrier.</span>
        </div>
      );
    }
    if (panel === 'carrier') {
      return (
        <div className="ion-codex-command-popover">
          <b>Codex CLI carrier</b>
          <span>{text(record(chat?.response_carrier).verdict, 'response carrier ready')}</span>
          <code>{text(settings.codex_binary_ref, '/usr/local/bin/codex')}</code>
        </div>
      );
    }
    return null;
  }

  function openContextSubwayNodeAction(action: CodexSubwayMapNode['action']) {
    if (action === 'queue') {
      setRightDrawer('messageQueue');
      setRightDrawerOpen(true);
      return;
    }
    if (action === 'rollback') {
      setRightDrawer('rollback');
      setRightDrawerOpen(true);
      setEditDrawerView('current');
      return;
    }
    if (action === 'carrier') {
      setRightDrawer('status');
      setRightDrawerOpen(true);
      return;
    }
    setLeftDrawer('context');
    setLeftDrawerOpen(true);
  }

  function adjustContextMapSize(direction: -1 | 1) {
    setContextMapOpen(true);
    setContextMapSize((previous) => {
      const index = CODEX_CONTEXT_MAP_SIZES.indexOf(previous);
      const nextIndex = Math.min(CODEX_CONTEXT_MAP_SIZES.length - 1, Math.max(0, index + direction));
      return CODEX_CONTEXT_MAP_SIZES[nextIndex];
    });
  }

  function renderContextTimelineIcon(event: CodexTimelineEvent) {
    const className = 'ion-codex-timeline-icon';
    if (event.track === 'context') return <ArchiveIcon className={className} />;
    if (event.track === 'diff') return <RollbackIcon className={className} />;
    if (event.track === 'tools') return <IdeIcon className={className} />;
    if (event.track === 'queue') return <QueueIcon className={className} />;
    if (event.track === 'carrier') return <CodexIcon className={className} />;
    return <EvidenceIcon className={className} />;
  }

  function renderContextMapBottomControls() {
    const currentGit = record(rollback?.current_git);
    const currentGitSample = records(currentGit.sample);
    const dirty = Boolean(currentGit.dirty);
    const dirtyCount = numberValue(currentGit.scoped_porcelain_count || currentGitSample.length);
    const contextCommand = currentContextCommandProjection();
    return (
      <div className="ion-codex-context-map-bottom-bar">
        <div className="ion-codex-context-map-status">
          <b>CONTEXT DIFF</b>
          <span>{contextMapOpen ? contextMapView : 'closed'} / {contextCommand.label} / {dirty ? `${dirtyCount} dirty` : 'clean'} / queue {queuedRequestCount}</span>
        </div>
        <div aria-label="Context diff map view" className="ion-codex-context-map-tabs" role="tablist">
          <button
            aria-selected={contextMapView === 'subway'}
            className={contextMapView === 'subway' ? 'is-active' : undefined}
            onClick={() => {
              setContextMapOpen(true);
              setContextMapView('subway');
              setSelectedContextSubwayNodeId('');
            }}
            role="tab"
            title="Show subway node map"
            type="button"
          >
            MAP
          </button>
          <button
            aria-selected={contextMapView === 'timeline'}
            className={contextMapView === 'timeline' ? 'is-active' : undefined}
            onClick={() => {
              setContextMapOpen(true);
              setContextMapView('timeline');
              setSelectedContextSubwayNodeId('');
            }}
            role="tab"
            title="Show animation timeline map"
            type="button"
          >
            TIMELINE
          </button>
        </div>
        <div className="ion-codex-context-map-size-controls">
          <button aria-label="Decrease context diff map size" disabled={contextMapSizeIndex <= 0} onClick={() => adjustContextMapSize(-1)} title="Decrease context diff map size" type="button">-</button>
          <code>{CODEX_CONTEXT_MAP_SIZE_LABELS[contextMapSize]}</code>
          <button aria-label="Increase context diff map size" disabled={contextMapSizeIndex >= CODEX_CONTEXT_MAP_SIZES.length - 1} onClick={() => adjustContextMapSize(1)} title="Increase context diff map size" type="button">+</button>
          <button aria-expanded={contextMapOpen} onClick={() => setContextMapOpen((previous) => !previous)} title={contextMapOpen ? 'Close context diff map' : 'Open context diff map'} type="button">
            {contextMapOpen ? 'CLOSE' : 'OPEN'}
          </button>
        </div>
        <div className="ion-codex-timeline-legend-wrap" onMouseLeave={() => setContextTimelineLegendOpen(false)}>
          <button
            aria-expanded={contextTimelineLegendOpen}
            aria-label="Show timeline color legend"
            className="ion-codex-timeline-legend-button"
            onClick={() => setContextTimelineLegendOpen((previous) => !previous)}
            title="Show timeline color legend"
            type="button"
          >
            <LensIcon />
          </button>
          {contextTimelineLegendOpen ? (
            <div className="ion-codex-timeline-legend-popover" role="dialog" aria-label="Timeline color legend">
              <span className="is-context-read">context read</span>
              <span className="is-diff-add">diff add/change</span>
              <span className="is-diff-remove">diff remove</span>
              <span className="is-tool">tools</span>
              <span className="is-queue">queue</span>
              <span className="is-carrier">carrier</span>
            </div>
          ) : null}
        </div>
      </div>
    );
  }

  function renderContextDiffSubwayMap() {
    const capsule = record(chat?.capsule);
    const recentRows = records(capsule.recent_rows);
    const latestCapsuleRow = record(recentRows[recentRows.length - 1]);
    const rollbackSummary = record(rollback?.summary);
    const currentGit = record(rollback?.current_git);
    const treeDiscipline = record(rollback?.tree_discipline);
    const currentGitSample = records(currentGit.sample);
    const archiveDiffEvidence = records(rollback?.archive_diff_evidence);
    const dirty = Boolean(currentGit.dirty);
    const dirtyCount = numberValue(currentGit.scoped_porcelain_count || currentGitSample.length);
    const checkpointCount = diffCheckpointCount || numberValue(rollbackSummary.visible_checkpoint_count);
    const rollbackReadyCount = numberValue(rollbackSummary.rollback_ready_count);
    const branch = text(currentGit.branch, 'branch unknown');
    const branchShort = branch.length > 24 ? `${branch.slice(0, 10)}...${branch.slice(-10)}` : branch;
    const contextTone: CodexSubwayMapNode['tone'] = capsuleHealth.tone === 'blocked' ? 'blocked' : capsuleHealth.tone === 'watch' ? 'watch' : 'ready';
    const queueNodeTone: CodexSubwayMapNode['tone'] = queueDispatchActive ? 'active' : queuePaused ? 'watch' : queuedRequestCount ? 'ready' : 'empty';
    const nodes: CodexSubwayMapNode[] = [
      {
        id: 'capsule',
        lane: 'context',
        label: 'Context Floor',
        value: capsuleHealth.label,
        detail: capsuleHealth.detail,
        meta: text(capsule.path, 'context floor path pending'),
        x: 7,
        y: 24,
        tone: contextTone,
        action: 'context',
      },
      {
        id: 'hot-context',
        lane: 'context',
        label: 'Hot Context',
        value: text(latestCapsuleRow.id, `${recentRows.length} rows`),
        detail: text(latestCapsuleRow.summary, 'Recent context floor rows are projected from the Codex solo context package.'),
        meta: `entries ${text(capsule.entry_count, 0)} / ${text(latestCapsuleRow.date, 'date unknown')}`,
        x: 22,
        y: 24,
        tone: contextTone,
        action: 'context',
      },
      {
        id: 'attached',
        lane: 'context',
        label: 'Attached',
        value: text(archiveAttachments.length, 0),
        detail: archiveAttachments.length ? 'Archive attachments are available for @ mention context.' : 'No archive attachments are staged for this chat.',
        meta: archiveAttachments.slice(0, 2).map((attachment) => text(attachment.title || attachment.label || attachment.name || attachment.session_id, '')).filter(Boolean).join(' / ') || 'none',
        x: 38,
        y: 24,
        tone: archiveAttachments.length ? 'ready' : 'empty',
        action: 'attachments',
      },
      {
        id: 'carrier',
        lane: 'carrier',
        label: 'Carrier',
        value: 'Codex CLI',
        detail: text(record(chat?.response_carrier).verdict, 'response carrier ready'),
        meta: `${agentIdentity.displayName} / ${agentIdentity.instanceId}`,
        x: 56,
        y: 24,
        tone: workerActive ? 'active' : 'ready',
        action: 'carrier',
      },
      {
        id: 'model',
        lane: 'carrier',
        label: 'Model',
        value: activeModelChoiceLabel,
        detail: `Thinking ${thinkingModeOption.label}. Prompt status ${promptStatusLabel}.`,
        meta: agentIdentity.title,
        x: 77,
        y: 24,
        tone: workerActive ? 'active' : 'ready',
        action: 'carrier',
      },
      {
        id: 'prompt',
        lane: 'queue',
        label: 'Prompt',
        value: workerActive ? 'can prompt' : 'ready',
        detail: workerActive ? `Codex worker active ${workerDuration || 'now'}; direct prompt remains available.` : 'Direct prompt mode is ready.',
        meta: executionMode.replaceAll('_', ' '),
        x: 15,
        y: 52,
        tone: workerActive ? 'active' : 'ready',
        action: 'queue',
      },
      {
        id: 'staged',
        lane: 'queue',
        label: 'Staged',
        value: text(messageQueueState.items.length, 0),
        detail: messageQueueState.items.length ? `${messageQueueState.items.length} local queue messages are staged.` : 'No local staged messages.',
        meta: activeMessageQueueGroup?.name || 'working queue',
        x: 34,
        y: 52,
        tone: messageQueueState.items.length ? 'ready' : 'empty',
        action: 'queue',
      },
      {
        id: 'queue',
        lane: 'queue',
        label: 'Queue',
        value: text(queuedRequestCount, 0),
        detail: queuePaused ? 'Queue dispatch is paused locally.' : queueDispatchActive ? 'Queue dispatch is playing.' : text(queue.verdict, 'queue ready'),
        meta: queueDispatchActive ? 'playing' : queuePaused ? 'paused' : 'ready',
        x: 52,
        y: 52,
        tone: queueNodeTone,
        action: 'queue',
      },
      {
        id: 'worker',
        lane: 'queue',
        label: 'Worker',
        value: workerActive ? workerDuration || 'active' : 'idle',
        detail: workerStatus,
        meta: text(queueTelemetry.active_run_id || queueTelemetryRun.run_id || queueTelemetry.request_id, 'no active run'),
        x: 71,
        y: 52,
        tone: workerActive ? 'active' : 'empty',
        action: 'queue',
      },
      {
        id: 'git',
        lane: 'diff',
        label: 'Git',
        value: branchShort,
        detail: dirty ? `${dirtyCount} scoped porcelain paths are dirty.` : 'Git tree is clean for the projected scope.',
        meta: text(currentGit.git_root, 'git root unknown'),
        x: 8,
        y: 78,
        tone: dirty ? 'watch' : 'ready',
        action: 'rollback',
      },
      {
        id: 'checkpoints',
        lane: 'diff',
        label: 'Checkpoints',
        value: text(checkpointCount, 0),
        detail: checkpointCount ? 'Rollback checkpoints are available for review.' : 'No rollback checkpoints are currently projected.',
        meta: `${text(rollbackSummary.archive_diff_evidence_count, 0)} archive evidence rows`,
        x: 31,
        y: 78,
        tone: checkpointCount ? 'ready' : 'empty',
        action: 'rollback',
      },
      {
        id: 'diffs',
        lane: 'diff',
        label: 'Diffs',
        value: text(dirtyCount, 0),
        detail: currentGitSample.slice(0, 3).map((item) => `${text(item.status, '').trim() || '??'} ${text(item.path, '')}`).join(' / ') || 'No diff sample in projection.',
        meta: text(treeDiscipline.active_chat_mode, 'dirty tree compatible'),
        x: 56,
        y: 78,
        tone: dirty ? 'watch' : archiveDiffEvidence.length ? 'ready' : 'empty',
        action: 'rollback',
      },
      {
        id: 'rollback',
        lane: 'diff',
        label: 'Rollback',
        value: text(rollbackReadyCount, 0),
        detail: text(treeDiscipline.active_chat_policy, 'Existing Codex chats preserve diff evidence and block unsafe rollback.'),
        meta: `${text(rollbackSummary.rollback_receipt_count, 0)} receipts`,
        x: 80,
        y: 78,
        tone: rollbackReadyCount ? 'ready' : dirty ? 'watch' : 'empty',
        action: 'rollback',
      },
    ];
    const toolRows = [
      ...records(tools.tools),
      ...records(tools.available_tools),
      ...records(tools.tool_specs),
      ...records(tools.items),
    ];
    const toolCount = numberValue(tools.tool_count || tools.available_tool_count || tools.enabled_count) || toolRows.length;
    const timelineDiffEvents = currentGitSample.slice(0, 5).map((item, index): CodexTimelineEvent => {
      const status = text(item.status, '').trim();
      const path = text(item.path || item.raw_path, 'path unknown');
      const deleted = Boolean(item.deleted) || status.includes('D');
      const added = Boolean(item.untracked) || status.includes('A') || status.includes('??');
      const tone: CodexTimelineEvent['tone'] = deleted ? 'diff-remove' : added ? 'diff-add' : 'diff-change';
      return {
        id: `timeline-diff-${index}`,
        track: 'diff',
        label: deleted ? 'Remove' : added ? 'Add' : 'Change',
        value: path.split('/').pop() || path,
        detail: `${status || '??'} ${path}`,
        meta: branch,
        start: 2 + (index * 3),
        span: index % 2 ? 3 : 4,
        tone,
        texture: deleted ? 'hatch' : added ? 'stripe' : 'mesh',
        action: 'rollback',
      };
    });
    const timelineEvents: CodexTimelineEvent[] = [
      {
        id: 'timeline-context-capsule',
        track: 'context',
        label: 'Context floor read',
        value: capsuleHealth.label,
        detail: capsuleHealth.detail,
        meta: text(capsule.path, 'context floor path pending'),
        start: 1,
        span: 5,
        tone: 'context-read',
        texture: 'dot',
        action: 'context',
      },
      {
        id: 'timeline-context-hot',
        track: 'context',
        label: 'Hot context',
        value: text(latestCapsuleRow.id, `${recentRows.length} rows`),
        detail: text(latestCapsuleRow.summary, 'Recent context floor rows are projected from the Codex solo context package.'),
        meta: `entries ${text(capsule.entry_count, 0)} / ${text(latestCapsuleRow.date, 'date unknown')}`,
        start: 7,
        span: 6,
        tone: 'context-read',
        texture: 'stripe',
        action: 'context',
      },
      {
        id: 'timeline-context-attached',
        track: 'context',
        label: 'Attached refs',
        value: text(archiveAttachments.length, 0),
        detail: archiveAttachments.length ? 'Archive attachments are available for @ mention context.' : 'No archive attachments are staged for this chat.',
        meta: archiveAttachments.slice(0, 2).map((attachment) => text(attachment.title || attachment.label || attachment.name || attachment.session_id, '')).filter(Boolean).join(' / ') || 'none',
        start: 14,
        span: 4,
        tone: 'context-read',
        texture: 'dash',
        action: 'attachments',
      },
      ...timelineDiffEvents,
      {
        id: 'timeline-tools',
        track: 'tools',
        label: 'Tools',
        value: text(toolCount, 0),
        detail: toolRows.slice(0, 3).map((item) => text(item.name || item.id || item.title, '')).filter(Boolean).join(' / ') || 'Tool surface ready.',
        meta: 'blue operational tool lane',
        start: 5,
        span: 7,
        tone: 'tool',
        texture: 'dot',
        action: 'carrier',
      },
      {
        id: 'timeline-queue-staged',
        track: 'queue',
        label: 'Staged',
        value: text(messageQueueState.items.length, 0),
        detail: messageQueueState.items.length ? `${messageQueueState.items.length} local queue messages are staged.` : 'No local staged messages.',
        meta: activeMessageQueueGroup?.name || 'working queue',
        start: 4,
        span: 5,
        tone: 'queue',
        texture: 'dash',
        action: 'queue',
      },
      {
        id: 'timeline-queue-worker',
        track: 'queue',
        label: 'Worker',
        value: workerActive ? workerDuration || 'active' : 'idle',
        detail: workerStatus,
        meta: text(queueTelemetry.active_run_id || queueTelemetryRun.run_id || queueTelemetry.request_id, 'no active run'),
        start: 11,
        span: workerActive ? 7 : 3,
        tone: workerActive ? 'queue' : 'evidence',
        texture: workerActive ? 'stripe' : 'solid',
        action: 'queue',
      },
      {
        id: 'timeline-carrier',
        track: 'carrier',
        label: 'Carrier',
        value: 'Codex CLI',
        detail: text(record(chat?.response_carrier).verdict, 'response carrier ready'),
        meta: `${agentIdentity.displayName} / ${agentIdentity.instanceId}`,
        start: 2,
        span: 6,
        tone: 'carrier',
        texture: 'mesh',
        action: 'carrier',
      },
      {
        id: 'timeline-model',
        track: 'carrier',
        label: 'Model',
        value: activeModelChoiceLabel,
        detail: `Thinking ${thinkingModeOption.label}. Prompt status ${promptStatusLabel}.`,
        meta: agentIdentity.title,
        start: 10,
        span: 8,
        tone: 'carrier',
        texture: 'stripe',
        action: 'carrier',
      },
      {
        id: 'timeline-checkpoints',
        track: 'evidence',
        label: 'Checkpoints',
        value: text(checkpointCount, 0),
        detail: checkpointCount ? 'Rollback checkpoints are available for review.' : 'No rollback checkpoints are currently projected.',
        meta: `${text(rollbackSummary.archive_diff_evidence_count, 0)} archive evidence rows / ${text(rollbackSummary.rollback_receipt_count, 0)} receipts`,
        start: 6,
        span: 5,
        tone: checkpointCount ? 'evidence' : 'blocked',
        texture: 'hatch',
        action: 'rollback',
      },
      {
        id: 'timeline-tree-policy',
        track: 'evidence',
        label: 'Tree policy',
        value: dirty ? `${dirtyCount} dirty` : 'clean',
        detail: text(treeDiscipline.active_chat_policy, 'Existing Codex chats preserve diff evidence and block unsafe rollback.'),
        meta: text(treeDiscipline.active_chat_mode, 'dirty tree compatible'),
        start: 13,
        span: 8,
        tone: dirty ? 'evidence' : 'carrier',
        texture: 'dot',
        action: 'rollback',
      },
    ];
    const selectedNode = nodes.find((node) => node.id === selectedContextSubwayNodeId) ?? null;
    const selectedTimelineEvent = timelineEvents.find((event) => event.id === selectedContextSubwayNodeId) ?? null;
    const contextTimelineDensity = CODEX_CONTEXT_TIMELINE_DENSITY_BY_SIZE[contextMapSize];
    const timelineTracks: Array<{ id: CodexTimelineEvent['track']; label: string; detail: string }> = [
      { id: 'context', label: 'Context Read', detail: 'yellow' },
      { id: 'diff', label: 'Diffs', detail: 'green add / red remove' },
      { id: 'tools', label: 'Tools', detail: 'blue' },
      { id: 'queue', label: 'Queue', detail: 'purple' },
      { id: 'carrier', label: 'Carrier', detail: 'cyan' },
      { id: 'evidence', label: 'Evidence', detail: 'gray' },
    ];
    return (
      <div className={`ion-codex-subway-map${contextMapOpen ? ' is-open' : ' is-closed'}${selectedNode || selectedTimelineEvent ? ' has-selected-node' : ''} is-${contextMapView} is-map-size-${contextMapSize}`}>
        {contextMapOpen ? (
        contextMapView === 'subway' ? (
        <div className="ion-codex-subway-stage">
          <div className="ion-codex-subway-viewport">
            <div className="ion-codex-subway-canvas">
              <svg aria-hidden="true" className="ion-codex-subway-lines" preserveAspectRatio="none" viewBox="0 0 1000 160">
                <path className="is-context" d="M60 38 H230 C280 38 270 76 324 76 H520 C572 76 562 38 620 38 H860" />
                <path className="is-queue" d="M145 82 H710 C760 82 758 38 818 38" />
                <path className="is-diff" d="M70 124 H325 C392 124 376 82 430 82 H650 C718 82 700 124 900 124" />
                <path className="is-carrier" d="M558 38 C608 58 626 82 710 82" />
              </svg>
              {nodes.map((node) => (
                <button
                  className={`ion-codex-subway-node is-${node.lane} is-${node.tone}${selectedNode?.id === node.id ? ' is-selected' : ''}`}
                  key={node.id}
                  onClick={() => {
                    setSelectedContextSubwayNodeId(node.id);
                    setContextMapOpen(true);
                    setContextMapSize('full');
                  }}
                  style={{ left: `${node.x}%`, top: `${node.y}%` }}
                  title={`${node.label}: ${node.value}. ${node.detail}`}
                  type="button"
                >
                  <span />
                  <b>{node.label}</b>
                  <em>{node.value}</em>
                  <div className="ion-codex-subway-hover">
                    <b>{node.label}</b>
                    <span>{node.detail}</span>
                    <code>{node.meta}</code>
                  </div>
                </button>
              ))}
            </div>
          </div>
          {selectedNode ? (
            <aside className={`ion-codex-subway-detail is-${selectedNode.lane}`}>
              <button aria-label="Close map node detail" className="ion-codex-subway-detail-close" onClick={() => setSelectedContextSubwayNodeId('')} type="button">
                <CloseIcon />
              </button>
              <b>{selectedNode.label}</b>
              <span>{selectedNode.detail}</span>
              <code>{selectedNode.meta}</code>
              <button onClick={() => openContextSubwayNodeAction(selectedNode.action)} type="button">OPEN {selectedNode.action.toUpperCase()}</button>
            </aside>
          ) : null}
        </div>
        ) : (
        <div className={`ion-codex-timeline-stage is-density-${contextTimelineDensity}`}>
          <div className="ion-codex-timeline-ruler">
            {Array.from({ length: 12 }, (_, index) => (
              <span key={`frame-${index}`}>{String(index * 10).padStart(2, '0')}</span>
            ))}
          </div>
          <div className="ion-codex-timeline-tracks">
            {timelineTracks.map((track) => {
              const trackEvents = timelineEvents.filter((event) => event.track === track.id);
              return (
                <section className={`ion-codex-timeline-track is-${track.id}`} key={track.id}>
                  <header>
                    <b>{track.label}</b>
                    <span>{track.detail}</span>
                  </header>
                  <div className="ion-codex-timeline-lane">
                    {trackEvents.map((event) => (
                      <button
                        className={`ion-codex-timeline-clip is-${event.tone} is-texture-${event.texture}${selectedTimelineEvent?.id === event.id ? ' is-selected' : ''}`}
                        key={event.id}
                        onClick={() => {
                          setSelectedContextSubwayNodeId(event.id);
                          setContextMapOpen(true);
                          setContextMapSize((size) => (size === 'mini' ? 'mid' : size));
                        }}
                        style={{ '--timeline-start': event.start, '--timeline-span': event.span } as CSSProperties}
                        title={`${event.label}: ${event.value}. ${event.detail}`}
                        type="button"
                      >
                        {renderContextTimelineIcon(event)}
                        <b>{event.label}</b>
                        <span>{event.value}</span>
                      </button>
                    ))}
                  </div>
                </section>
              );
            })}
          </div>
          {selectedTimelineEvent ? (
            <aside className={`ion-codex-subway-detail ion-codex-timeline-detail is-${selectedTimelineEvent.track}`}>
              <button aria-label="Close timeline detail" className="ion-codex-subway-detail-close" onClick={() => setSelectedContextSubwayNodeId('')} type="button">
                <CloseIcon />
              </button>
              <b>{selectedTimelineEvent.label}</b>
              <span>{selectedTimelineEvent.detail}</span>
              <code>{selectedTimelineEvent.meta}</code>
              <button onClick={() => openContextSubwayNodeAction(selectedTimelineEvent.action)} type="button">{selectedTimelineEvent.action === 'rollback' ? 'OPEN EDITS' : `OPEN ${selectedTimelineEvent.action.toUpperCase()}`}</button>
            </aside>
          ) : null}
        </div>
        )
        ) : null}
      </div>
    );
  }

  function renderComposerUtilityActions() {
    return (
      <div className="ion-codex-composer-utility-stack">
        <button
          aria-expanded={filePickerOpen}
          aria-label="Open file reference drawer"
          className={filePickerOpen ? 'is-active' : undefined}
          onClick={() => {
            const sameDrawer = leftDrawer === 'files';
            setLeftDrawer('files');
            setLeftDrawerOpen(!sameDrawer || !leftDrawerOpen);
          }}
          title="Open file reference drawer"
          type="button"
        >
          <DocsIcon />
          {selectedContextRefCount ? <b>{selectedContextRefCount}</b> : null}
        </button>
        <button aria-label="Open chats drawer" className={leftDrawerOpen && leftDrawer === 'sessions' ? 'is-active' : undefined} onClick={openPastChatsDrawer} title="Open chats drawer" type="button">
          <SessionsIcon />
        </button>
        <button aria-label="Open message queues" className={rightDrawerOpen && rightDrawer === 'messageQueue' ? 'is-active' : undefined} onClick={() => { setRightDrawer('messageQueue'); setRightDrawerOpen(true); }} title="Open message queues" type="button">
          <QueueIcon />
        </button>
        <button aria-label="Open edits drawer" className={rightDrawerOpen && rightDrawer === 'rollback' ? 'is-active' : undefined} onClick={() => { setRightDrawer('rollback'); setRightDrawerOpen(true); setEditDrawerView('current'); }} title="Open edits drawer" type="button">
          <RollbackIcon />
        </button>
        <button
          aria-label="Open mission profile drawer"
          className={rightDrawerOpen && rightDrawer === 'missionProfile' ? 'is-active' : undefined}
          onClick={() => { setRightDrawer('missionProfile'); setRightDrawerOpen(true); }}
          title="Open mission profile"
          type="button"
        >
          <AgentsIcon />
        </button>
      </div>
    );
  }

  function renderMissionProfileDrawer() {
    const targetLiveSessionId = CODEX_LIVE_SESSION_ID;
    const targetSession = selectedSession ?? null;
    const targetSessionId = text(targetSession?.session_id || (showingArchiveChat ? selectedArchiveSessionId : ''), showingArchiveChat ? targetSession?.session_id || 'session' : targetLiveSessionId);
    const targetThreadLabel = showingArchiveChat && targetSession ? chatTitleForSession(targetSession) : CODEX_CURRENT_SESSION_TITLE;
    const targetMode = showingArchiveChat ? 'ARCHIVE THREAD' : 'LIVE THREAD';
    const targetModel = text(targetSession?.model || activeModelLabel, activeModelLabel);
    const liveRecentRows = records(record(chat?.capsule).recent_rows);
    const liveFallbackSnippet = liveRecentRows.find((row) => text(row.snippet || row.text, '').trim());
    const selectedExcerptRecord = record(selectedExcerpt);
    const targetSnippet = showingArchiveChat
      ? text(targetSession?.latest_user_snippet || targetSession?.first_user_snippet || selectedExcerptRecord.query, 'No snippet captured for this thread yet.')
      : text(liveFallbackSnippet?.snippet || liveFallbackSnippet?.text || chat?.mini?.text_excerpt, 'No live snippet captured for this thread yet.');
    const targetPath = showingArchiveChat
      ? text(targetSession?.session_path || selectedExcerpt?.session_path, 'runtime session')
      : text(record(chat?.capsule).path || record(chat?.mini).path, 'codex cli live');
    const targetThreadMeta = [targetMode, targetModel, targetSessionId ? sessionShortText(targetSessionId) : 'thread'].filter(Boolean).join(' / ');
    const missionLabels = records(targetSession?.mission_labels);
    const agentProfileLabels = records(targetSession?.agent_labels);
    const attachedTools = records(targetSession?.tool_summary).slice(0, 6);

    const projectedThreads = mergeJocCommsThreads([
      ...missionCommsThreads,
      ...records(runtime.joc_comms?.threads).map(coerceJocCommsThread).filter((thread): thread is JocCommsThread => Boolean(thread)),
      ...records(agentTeamComms.threads).map(coerceJocCommsThread).filter((thread): thread is JocCommsThread => Boolean(thread)),
    ]);
    const matchedMissionThreadId = matchedMissionThreadIdForTarget(projectedThreads, [
      targetSessionId,
      targetSession?.session_path,
      selectedExcerpt?.session_path,
      showingArchiveChat ? selectedArchiveSessionId : '',
      currentArchiveSessionId,
    ]);
    const activeMissionThreadId = selectedMissionThreadId || matchedMissionThreadId || text(projectedThreads[0]?.thread_id, '');
    const detailThreadId = text(missionCommsThreadDetail.thread?.thread_id, '');
    const activeMissionThread = detailThreadId === activeMissionThreadId
      ? missionCommsThreadDetail.thread
      : projectedThreads.find((thread) => text(thread.thread_id, '') === activeMissionThreadId) ?? null;
    const projectedMessages = [
      ...records(runtime.joc_comms?.messages).map(coerceJocCommsMessage).filter((message): message is JocCommsMessage => Boolean(message)),
      ...records(agentTeamComms.recent_messages).map(coerceJocCommsMessage).filter((message): message is JocCommsMessage => Boolean(message)),
    ];
    const activeThreadMessages = detailThreadId === activeMissionThreadId && missionCommsThreadDetail.messages.length
      ? missionCommsThreadDetail.messages
      : projectedMessages.filter((message) => text(message.thread_id, '') === activeMissionThreadId).slice(-80);
    const chainSteps = records(agentControlChain.steps);
    const chainActiveStep = chainSteps.find((step) => text(step.active, '').toLowerCase() === 'true' || Boolean(step.is_active));
    const chainStepIndex = chainActiveStep ? chainSteps.indexOf(chainActiveStep) + 1 : 0;
    const chainStepCount = chainSteps.length;
    const runs = record(agentControlRuns);
    const latestRun = record(runs.active_run || queueTelemetry.run || queueTelemetryRun);
    const latestRunState = record(runs.latest_state);
    const runStatus = text(latestRun.status || latestRun.verdict || latestRunState.status || workerStatus, 'standby');
    const runId = shortOperationalId(text(latestRun.run_id || latestRun.request_id || text(runs.next_agent_codex_work_request_path, ''), 'n/a'));
    const dispatcherSummary = record(agentControlDispatcher.summary);
    const automationControl = record(runtime.automation_control_plane);
    const kernelProjection = record(runtime.runtime_debug_overlay?.kernel);
    const schedulerProjection = record(automationControl.scheduler || automationControl.kernel_scheduler || kernelProjection.scheduler);
    const schedulerStatus = text(schedulerProjection.status || schedulerProjection.verdict || schedulerProjection.state || agentControlDispatcher.scheduler_status || 'projected', 'projected');
    const commsSummary = record(agentControlComms.summary);
    const teamCommsSummary = record(agentTeamComms.summary);
    const receiptCount = agentCommsReceipts.length || numberValue(commsSummary.receipt_count);
    const activeRoleId = text(chainActiveStep?.role_id || chainActiveStep?.role || queueTelemetry.agent_role_id || queueTelemetryRun.agent_role_id || agentIdentity.roleId, agentIdentity.roleId);
    const missionOps: Array<{ id: string; label: string; value: string; detail: string; tone: MissionTimelineEvent['tone']; onClick: () => void }> = [
      {
        id: 'agent',
        label: 'agent',
        value: agentIdentity.displayName,
        detail: `${agentIdentity.roleId} / ${agentIdentity.instanceId}`,
        tone: workerActive ? 'active' : 'ready',
        onClick: () => {
          setLeftDrawer('agents');
          setLeftDrawerOpen(true);
        },
      },
      {
        id: 'run',
        label: 'run',
        value: workerActive ? `working ${workerDuration || 'now'}` : runStatus,
        detail: runId || text(runs.next_agent_codex_work_request_path, 'no active run'),
        tone: workerActive ? 'active' : runStatus.toLowerCase().includes('block') ? 'blocked' : 'empty',
        onClick: () => {
          setRightDrawer('assistant');
          setRightDrawerOpen(true);
          setAssistantDrawerView('runs');
        },
      },
      {
        id: 'scheduler',
        label: 'scheduler',
        value: schedulerStatus,
        detail: `${text(dispatcherSummary.pending_directive_count || contextAgentSummary.dispatcher_pending_directive_count, 0)} pending directives`,
        tone: schedulerStatus.toLowerCase().includes('block') ? 'blocked' : schedulerStatus.toLowerCase().includes('active') ? 'active' : 'ready',
        onClick: () => setCommandPanel('carrier'),
      },
      {
        id: 'queue',
        label: 'queue',
        value: `${queuedRequestCount} waiting`,
        detail: queuePaused ? 'paused' : queueDispatchActive ? 'playing' : text(queueTelemetry.request_id || queueTelemetryRun.request_id || runs.next_agent_codex_work_request_path, 'empty'),
        tone: queueDispatchActive ? 'active' : queuedRequestCount ? 'watch' : 'empty',
        onClick: () => {
          setRightDrawer('messageQueue');
          setRightDrawerOpen(true);
        },
      },
      {
        id: 'context',
        label: 'context',
        value: capsuleHealth.label,
        detail: capsuleHealth.detail,
        tone: capsuleHealth.tone as MissionTimelineEvent['tone'],
        onClick: () => setCommandPanel('context'),
      },
      {
        id: 'comms',
        label: 'comms',
        value: `${projectedThreads.length || teamCommsSummary.thread_count || commsSummary.team_thread_count || 0} threads`,
        detail: `${activeThreadMessages.length || text(activeMissionThread?.message_count, 0)} messages / ${receiptCount} receipts`,
        tone: projectedThreads.length || activeThreadMessages.length ? 'ready' : 'empty',
        onClick: () => {
          if (activeMissionThreadId) setSelectedMissionThreadId(activeMissionThreadId);
        },
      },
    ];
    const timelineRows: MissionTimelineEvent[] = [
      ...activeThreadMessages.map((message, index): MissionTimelineEvent => ({
        id: text(message.message_id, `thread-message-${index}`),
        kind: text(message.message_kind || message.message_type || 'message', 'message'),
        title: text(message.subject || message.from_role || message.sender_id || 'Thread message', 'Thread message'),
        status: missionMessageRouteLabel(message),
        detail: text(message.body || record(message.work_panel).summary || message.source_path, 'No body captured.'),
        source: text(message.source_path || message.channel_id, 'agent comms thread'),
        at: text(message.created_at, ''),
        tone: missionToneFromStatus(message.status || message.message_kind || message.message_type),
      })),
      ...agentCommsTimeline.slice(-12).map((row, index): MissionTimelineEvent => ({
        id: text(row.id || row.event_id || row.path || row.created_at, `agent-timeline-${index}`),
        kind: 'timeline',
        title: text(row.title || row.event_type || row.summary, 'Agent comms'),
        status: text(row.to_role || row.from_role || row.path || row.created_at, ''),
        detail: text(row.detail || row.summary || row.message, ''),
        tone: missionToneFromStatus(row.status || row.verdict || row.state),
        source: 'agent comms',
        at: text(row.created_at || row.updated_at, ''),
      })),
      ...agentCommsRelays.slice(-8).map((row, index): MissionTimelineEvent => ({
        id: text(row.id || row.message_id || row.route_id || row.path || row.created_at, `relay-${index}`),
        kind: 'relay',
        title: text(row.title || row.label || row.route_id || row.message_id, 'Relay event'),
        status: text(row.status || row.state || row.updated_at, ''),
        detail: text(row.summary || row.detail || row.path || row.from_role, ''),
        tone: missionToneFromStatus(row.status || row.state || 'watch'),
        source: 'agent relay',
        at: text(row.created_at || row.updated_at, ''),
      })),
      ...agentCommsPendingRelays.slice(-8).map((row, index): MissionTimelineEvent => ({
        id: text(row.id || row.message_id || row.route_id || row.path || row.created_at, `pending-relay-${index}`),
        kind: 'pending relay',
        title: text(row.title || row.label || row.route_id || row.message_id, 'Pending relay'),
        status: text(row.status || row.state || row.created_at, ''),
        detail: text(row.summary || row.detail || row.path || row.request_id, ''),
        tone: 'watch',
        source: 'pending relay',
        at: text(row.created_at || row.updated_at, ''),
      })),
      ...mcpCarrierMessages.slice(-8).map((row, index): MissionTimelineEvent => ({
        id: text(row.id || row.message_id || row.path || row.created_at, `carrier-${index}`),
        kind: 'carrier',
        title: text(row.title || row.event_type || row.tool_name || 'Carrier message'),
        status: text(row.status || row.state || row.path, ''),
        detail: text(row.message || row.detail, ''),
        tone: missionToneFromStatus(row.status || row.state || 'active'),
        source: 'carrier',
        at: text(row.created_at || row.updated_at, ''),
      })),
      ...mcpAgentInvocations.slice(-8).map((row, index): MissionTimelineEvent => ({
        id: text(row.id || row.call_id || row.request_id || row.path || row.created_at, `agent-call-${index}`),
        kind: 'agent call',
        title: text(row.agent_role_id || row.role_id || row.agent || 'Agent call'),
        status: text(row.status || row.verdict || row.state, ''),
        detail: text(row.path || row.request_id || row.call_id, ''),
        tone: missionToneFromStatus(row.verdict || row.status || row.state),
        source: 'agent invocation',
        at: text(row.created_at || row.updated_at, ''),
      })),
      ...latestIonPipelineStages.slice(-12).map((row, index): MissionTimelineEvent => ({
        id: text(row.stage_id || row.role_id || row.created_at, `pipeline-${index}`),
        kind: 'role',
        title: text(row.label || row.role_id || row.phase || `Role phase ${index + 1}`, `Role phase ${index + 1}`),
        status: text(row.status || row.verdict || row.state || row.phase, ''),
        detail: text(row.summary || row.detail || row.objective || row.role_id, ''),
        tone: missionToneFromStatus(row.status || row.verdict || row.state),
        source: 'ION pipeline',
        at: text(row.created_at || row.updated_at || latestIonPipelineRun.created_at, ''),
      })),
    ]
      .filter((row) => row.title || row.detail)
      .sort((left, right) => missionEventSortValue(left) - missionEventSortValue(right))
      .slice(-36)
      .reverse();
    const missionGoalRows = uniqueStrings([
      ...missionLabels.map((label) => `${text(label.label, 'goal')} ${text(label.source, '')}`.trim()),
      ...stringList(activeMissionThread?.next_allowed_actions).map((action) => `next: ${action}`),
      text(activeMissionThread?.latest_summary, ''),
      targetSnippet,
    ]).filter(Boolean).slice(0, 7);
    const missionRoleRows = chainSteps.length
      ? chainSteps.map((step, index) => ({
        id: text(step.role_id || step.role || step.id || `chain-${index}`),
        label: text(step.label || step.phase || step.role_id || step.role || `Phase ${index + 1}`),
        detail: text(step.status || step.verdict || step.summary || step.detail, ''),
        active: step === chainActiveStep || text(step.role_id || step.role, '') === activeRoleId,
      }))
      : rolePhaseRows.map((roleId, index) => ({
        id: roleId,
        label: roleId.replace(/_/g, ' '),
        detail: index === 0 ? 'persona ingress' : index === rolePhaseRows.length - 1 ? 'persona response' : 'internal role phase',
        active: roleId === activeRoleId,
      }));
    const authority = record(agentControlPlane.authority);
    const openCurrentTarget = () => {
      if (showingArchiveChat && targetSession) {
        void openSession(targetSession, { activateArchive: false, showInChat: true });
      } else {
        showLiveChat();
      }
    };
    const openMissionThreadTarget = (thread: JocCommsThread | null) => {
      if (!thread) {
        openCurrentTarget();
        return;
      }
      const matchingSession = archiveSessionForMissionThread(thread, allSessions);
      if (matchingSession) {
        void openSession(matchingSession, { activateArchive: false, showInChat: true });
        return;
      }
      const threadId = text(thread.thread_id, '');
      if (threadId && typeof window !== 'undefined') {
        window.location.hash = `scope?thread_id=${encodeURIComponent(threadId)}`;
      }
    };

    return (
      <div className="ion-codex-mission-profile-drawer">
        <DrawerTitle title="mission profile" value={targetThreadLabel} />
        <div className="ion-codex-mission-profile-head">
          <div className={`ion-codex-selected-head is-${workerActive ? 'active' : 'ready'}`}>
            <div>
              <span>{targetThreadMeta}</span>
              <b>{targetThreadLabel}</b>
              <code>{targetPath}</code>
            </div>
            <button onClick={openCurrentTarget} title="Open current chat thread in the main pane" type="button">OPEN</button>
          </div>
          <div className="ion-codex-mission-profile-snippet">{targetSnippet}</div>
        </div>
        <section className="ion-codex-mission-op-grid" aria-label="Mission operations">
          {missionOps.map((op) => (
            <button className={`is-${op.tone}`} key={op.id} onClick={op.onClick} title={`${op.label}: ${op.value}. ${op.detail}`} type="button">
              <span>{op.label}</span>
              <b>{op.value}</b>
              <em>{op.detail}</em>
            </button>
          ))}
        </section>
        <section className="ion-codex-mission-role-rail" aria-label="ION role pipeline">
          {missionRoleRows.slice(0, 12).map((role, index) => (
            <button className={role.active ? 'is-active' : undefined} key={`${role.id}-${index}`} title={`${role.label}: ${role.detail}`} type="button">
              <span>{String(index + 1).padStart(2, '0')}</span>
              <b>{role.label}</b>
              <em>{role.detail || 'projected'}</em>
            </button>
          ))}
        </section>
        <div className="ion-codex-kpi-strip is-drawer">
          <Metric label="run id" value={runId} />
          <Metric label="chain" value={chainStepIndex ? `${chainStepIndex}/${chainStepCount}` : chainStepCount || rolePhaseRows.length} />
          <Metric label="threads" value={projectedThreads.length || teamCommsSummary.thread_count || 0} />
          <Metric label="messages" value={activeThreadMessages.length || text(activeMissionThread?.message_count, 0)} />
          <Metric label="model" value={targetModel} />
        </div>
        <section className="ion-codex-mission-thread-deck" aria-label="Agent comms threads">
          <div className="ion-codex-mission-profile-subtitle">
            <span>THREAD LEDGER</span>
            <button disabled={missionCommsLoading} onClick={() => { void refreshMissionCommsThreads(); }} type="button">{missionCommsLoading ? 'LOADING' : 'REFRESH'}</button>
          </div>
          <div className="ion-codex-mission-thread-list">
            {projectedThreads.length ? projectedThreads.slice(0, 40).map((thread) => {
              const threadId = text(thread.thread_id, '');
              const active = threadId === activeMissionThreadId;
              const tone = missionToneFromStatus(thread.status);
              return (
                <button
                  className={`is-${tone}${active ? ' is-active' : ''}`}
                  key={threadId}
                  onClick={() => setSelectedMissionThreadId(threadId)}
                  onDoubleClick={() => openMissionThreadTarget(thread)}
                  title="Click to inspect, double click to open linked chat or scope thread."
                  type="button"
                >
                  <span>{text(thread.channel_id, 'team')} / {text(thread.status, 'active')}</span>
                  <b>{missionThreadTitle(thread)}</b>
                  <em>{text(thread.message_count, 0)} msgs</em>
                  <small>{text(thread.latest_summary || thread.authority_boundary || thread.thread_kind, 'No summary projected.')}</small>
                </button>
              );
            }) : (
              <div className="ion-empty-state">{missionCommsLoading ? 'LOADING AGENT COMMS' : 'NO AGENT COMMS THREADS PROJECTED'}</div>
            )}
          </div>
          {missionCommsError ? <div className="ion-codex-mission-error">{missionCommsError}</div> : null}
        </section>
        <section className="ion-codex-mission-thread-detail" aria-label="Selected mission thread">
          <header>
            <div>
              <span>{activeMissionThread ? `${text(activeMissionThread.channel_id, 'team')} / ${text(activeMissionThread.thread_kind, 'thread')}` : 'current chat thread'}</span>
              <b>{activeMissionThread ? missionThreadTitle(activeMissionThread) : targetThreadLabel}</b>
              <code>{activeMissionThread ? text(activeMissionThread.thread_id, '') : targetSessionId}</code>
            </div>
            <div className="ion-codex-mission-thread-actions">
              <button onClick={() => openMissionThreadTarget(activeMissionThread)} type="button">OPEN</button>
              <button disabled={!activeMissionThreadId} onClick={() => {
                if (activeMissionThreadId && typeof window !== 'undefined') window.location.hash = `scope?thread_id=${encodeURIComponent(activeMissionThreadId)}`;
              }} type="button">SCOPE</button>
            </div>
          </header>
          <div className="ion-codex-mission-thread-summary">
            <span>{text(activeMissionThread?.latest_summary || targetSnippet, 'No thread summary projected yet.')}</span>
            <code>{missionCommsThreadLoading ? 'loading detail' : missionCommsThreadDetail.loadedAt ? `loaded ${formatCompactDate(missionCommsThreadDetail.loadedAt)}` : 'projection only'}</code>
          </div>
          <div className="ion-codex-mission-authority-strip">
            <code>prod {text(authority.production_authority ?? agentControlPlane.production_authority, false)}</code>
            <code>live {text(authority.live_execution_authority ?? agentControlPlane.live_execution_authority, false)}</code>
            <code>accepted {text(authority.accepted_state_authority ?? agentControlPlane.accepted_state_authority, false)}</code>
            <code>secrets {text(authority.secrets_authority ?? agentControlPlane.secrets_authority, false)}</code>
          </div>
        </section>
        <div className="ion-codex-mission-profile-goals">
          <label className="ion-codex-mission-profile-subtitle">MISSION GOALS</label>
          <div className="ion-codex-mission-goal-list">
            {missionGoalRows.length ? missionGoalRows.map((goal, index) => (
              <span key={`${goal}-${index}`}>{goal}</span>
            )) : <span>No stored mission goals for this thread.</span>}
          </div>
          {agentProfileLabels.length ? <LabelRow labels={agentProfileLabels.slice(0, 5)} /> : <div className="ion-empty-state">NO AGENT LABELS</div>}
          {attachedTools.length ? (
            <div className="ion-codex-mission-profile-tools">
              {attachedTools.map((tool, index) => (
                <span key={`${text(tool.name, `tool-${index}`)}-${index}`}>{text(tool.name)}:{text(tool.count, 0)}</span>
              ))}
            </div>
          ) : null}
        </div>
        <section className="ion-codex-mission-profile-timeline" aria-label="Mission timeline">
          <div className="ion-codex-mission-profile-subtitle">
            <span>MISSION TIMELINE</span>
            <b>{timelineRows.length}</b>
          </div>
          {timelineRows.length ? timelineRows.map((row, index) => (
            <button
              className={`ion-codex-mission-profile-row is-${safeClass(row.tone)}`}
              key={`${row.id}-${index}`}
              onClick={() => {
                if (row.kind === 'relay') {
                  setRightDrawer('assistant');
                  setRightDrawerOpen(true);
                }
              }}
              title={`${row.kind}: ${row.detail}`}
              type="button"
            >
              <i>{row.kind}</i>
              <b>{row.title}</b>
              <span>{row.status || row.source}</span>
              <small>{row.detail}</small>
            </button>
          )) : <div className="ion-empty-state">No mission timeline activity currently projected.</div>}
        </section>
        <div className="ion-codex-selected-actions">
          <button onClick={() => { setRightDrawer('messageQueue'); setRightDrawerOpen(true); }} type="button">QUEUE</button>
          <button onClick={() => { setRightDrawer('assistant'); setRightDrawerOpen(true); }} type="button">ASSISTANT</button>
          <button onClick={() => { setRightDrawer('status'); setRightDrawerOpen(true); }} type="button">STATUS</button>
        </div>
      </div>
    );
  }

  function renderCodexComposer(laneId: CodexChatLaneId = 'codex_general') {
    return (
        <form className="ion-codex-composer" onSubmit={(event) => { void submitTurn(event, undefined, laneId); }}>
          <div className="ion-codex-composer-body">
            {renderComposerUtilityActions()}
            <div className={`ion-codex-composer-input${sttListening ? ' is-listening' : ''}`}>
              <div className="ion-codex-voice-bar">
                <button
                  className={sttListening ? 'is-active' : undefined}
                  disabled={!sttSupported}
                  onClick={() => (sttListening ? stopSpeechInput() : startSpeechInput())}
                  title={sttSupported ? 'Toggle live browser speech to text' : 'Browser speech recognition unavailable'}
                  type="button"
                >
                  {sttListening ? 'STOP' : 'MIC'}
                </button>
                <select
                  aria-label="Speech language"
                  disabled={sttListening}
                  onChange={(event) => setSttLanguage(event.currentTarget.value)}
                  value={sttLanguage}
                >
                  {STT_LANGUAGES.map((language) => <option key={language.value} value={language.value}>{language.label}</option>)}
                </select>
                <button disabled={!sttInterim.trim()} onClick={commitInterimSpeech} type="button">USE</button>
                <span>{sttSupported ? sttStatus : 'speech api unavailable'}</span>
                <code>{sttInterim || 'browser stt'}</code>
              </div>
              <textarea
                aria-label="Codex message"
                onKeyDown={(event) => {
                  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
                onChange={(event) => setComposer(event.currentTarget.value)}
                placeholder={laneId === 'ion_system' ? 'Message ION Persona' : 'Message Codex CLI'}
                value={composer}
              />
            </div>
            <div className={`ion-codex-composer-action-stack${cancelableWorkerActive ? ' is-worker-active' : ''}`}>
              {cancelableWorkerActive ? (
                <button
                  className="ion-codex-agent-cancel-button"
                  disabled={agentStopBusy}
                  onClick={() => { void stopCodexAgent(); }}
                  title="Cancel the active Codex queue-runner worker recorded in local runner state."
                  type="button"
                >
                  <span>{agentStopBusy ? 'CANCELING' : 'CANCEL'}</span>
                </button>
              ) : null}
              <div className="ion-codex-queue-action-row">
                <button
                  aria-label={queuePlayLabel.toLowerCase()}
                  className={`ion-codex-queue-play-button${executionMode === 'queue_and_start' ? ' is-active' : ''}`}
                  data-mode="queue_and_start"
                  disabled={queuePlayDisabled}
                  onClick={() => { void toggleRunPause(); }}
                  title={queueDispatchActive ? 'Pause staged queue dispatch after the active queue message.' : workerActive ? 'Codex is already working; queue play waits until the worker stops.' : composer.trim() ? 'Stage this message in the queue drawer and play the queue.' : 'Play the staged message queue.'}
                  type="button"
                >
                  {queueDispatchActive ? <PauseIcon className="ion-codex-composer-action-icon" /> : <RunIcon className="ion-codex-composer-action-icon" />}
                </button>
                <div
	                  className="ion-codex-queue-button-wrap"
	                  onFocus={openComposerQueueInsertPanel}
	                  onMouseEnter={openComposerQueueInsertPanel}
	                  onMouseLeave={(event) => {
	                    const next = event.relatedTarget as Node | null;
	                    if (!next || !event.currentTarget.contains(next)) {
	                      setQueueInsertOpen(false);
	                    }
	                  }}
	                  onPointerEnter={openComposerQueueInsertPanel}
	                  onPointerLeave={(event) => {
	                    const next = event.relatedTarget as Node | null;
	                    if (!next || !event.currentTarget.contains(next)) {
	                      setQueueInsertOpen(false);
	                    }
	                  }}
	                >
                  <button
                    className={`ion-codex-queue-button${executionMode === 'queue_for_codex' ? ' is-active' : ''}`}
                    data-mode="queue_for_codex"
                    disabled={composerQueueDisabled}
                    draggable={!composerQueueDisabled}
                    onDragEnd={() => setQueueInsertOpen(false)}
                    onDragStart={handleComposerQueueDragStart}
                    onClick={() => stageComposerInMessageQueue('queue_for_codex')}
                    title="Click to add this message to the end of the queue. Drag into the hover panel to choose a queue position."
                    type="button"
                  >
                    <span className="ion-codex-queue-label">QUEUE</span>
                    <span className={`ion-codex-queue-count${queuedRequestCount ? ' is-queued' : ' is-empty'}`}>
                      <span className="ion-codex-queue-count-value">{queuedRequestCount}</span>
                      <span className="ion-codex-queue-count-add">+</span>
                    </span>
                  </button>
                  {queueInsertOpen ? (
                    <div className="ion-codex-queue-insert-popover">
                      <b>{messageQueueState.items.length ? 'Drop into queue' : 'Empty queue'}</b>
                      <button
                        onClick={() => stageComposerAtQueueIndex(0)}
                        onDragOver={(event) => event.preventDefault()}
                        onDrop={(event) => handleComposerQueueDropAtIndex(event, 0)}
                        type="button"
                      >
                        {messageQueueState.items.length ? 'TOP OF QUEUE' : 'ADD FIRST'}
                      </button>
                      {messageQueueState.items.slice(0, 10).map((item, index) => (
                        <button
                          key={item.id}
                          onClick={() => stageComposerAtQueueIndex(index + 1)}
                          onDragOver={(event) => event.preventDefault()}
                          onDrop={(event) => handleComposerQueueDropAtIndex(event, index + 1)}
                          type="button"
                        >
                          AFTER #{index + 1} {item.title}
                        </button>
                      ))}
                      {messageQueueState.items.length > 10 ? <span>{messageQueueState.items.length - 10} more rows in queue drawer</span> : null}
                    </div>
                  ) : null}
                </div>
              </div>
              <button
                className={`ion-codex-prompt-button${executionMode === 'auto' || executionMode === 'respond_only' ? ' is-active' : ''}${workerActive ? ' is-worker-active' : ''}`}
                data-mode={executionMode}
                disabled={sending || Boolean(messageQueueDispatchingId) || !composer.trim()}
                title={workerActive && executionMode === 'respond_only' ? 'Send a direct prompt while the Codex queue agent continues working.' : primarySendTitle}
                type="submit"
              >
                <span>{primarySendLabel}</span>
                <b>{activeModelChoiceLabel} / {thinkingModeOption.label}</b>
                <em>{promptStatusLabel}</em>
              </button>
            </div>
          </div>
        </form>
    );
  }

  function renderChatPane() {
    const chatConsoleClassName = [
      'ion-codex-chat-console',
      'is-transcript',
      showingArchiveChat ? 'is-showing-archive-chat' : 'is-live-chat',
      showingArchiveChat && archiveBusy ? 'is-archive-loading' : '',
    ].filter(Boolean).join(' ');
    return (
      <section className={chatConsoleClassName}>
        {renderOpenChatTabs()}
        {showingArchiveChat ? renderSelectedArchiveChat() : renderLiveTranscript()}
        {renderChatCommandBar()}
        {renderCodexComposer('codex_general')}
        {renderContextDiffSubwayMap()}
      </section>
    );
  }

  async function createNewCapsuleChat(contextSystem?: Record<string, unknown>) {
    if (newCapsuleChatBusy) return;
    const activeTabSession = sessionFromOpenChatTab(activeChatTab) ?? selectedSession;
    const liveBinding = record(record(chat?.chat_context).active_binding);
    const archiveBinding = record(record(activeTabSession).chat_context_binding);
    const binding = activeChatTab ? archiveBinding : liveBinding;
    const agentIdentity = record(binding.agent_identity);
    const missionLabels = records(activeTabSession?.mission_labels);
    const agentLabels = records(activeTabSession?.agent_labels);
    const selectedSystem = record(contextSystem);
    const selectedSystemEvidence = record(selectedSystem.agent_page_evidence);
    const selectedSystemIdentity = record(selectedSystemEvidence.identity);
    const selectedSystemRole = text(selectedSystem.role_id || selectedSystem.agent_id || selectedSystemIdentity.role_id || agentRecordId(selectedSystem), '');
    const selectedSystemDomain = text(selectedSystem.registry_primary_domain || selectedSystemIdentity.domain_id || selectedSystem.role_domain_label, '');
    const selectedSystemName = text(selectedSystem.display_name || selectedSystemRole, '');
    const fallbackTitle = activeChatTab
      ? chatTitleForSessionId(activeChatTab.sessionId, activeChatTab.title)
      : selectedSystemName
        ? `${selectedSystemName} context chat`
        : 'Fresh Codex context chat';
    const title = text(composer.trim() || fallbackTitle, fallbackTitle).slice(0, 180);
    const domainId = text(selectedSystemDomain || binding.domain_id || missionLabels[0]?.label || 'domain.codex_carrier_sync', 'domain.codex_carrier_sync');
    const roleId = text(selectedSystemRole || agentIdentity.clone_of_role_id || binding.role_id || agentLabels[0]?.role_id || agentLabels[0]?.label || 'role.codex_cli', 'role.codex_cli');
    setNewCapsuleChatBusy(true);
    setActionNotice('Creating fresh context system chat...');
    try {
      const response = await fetch(chatApiPath('/context-starter/create'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          confirmation: WRITE_CONFIRMATION_TOKEN,
          title,
          domain_id: domainId,
          role_id: roleId,
        }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `context_starter_http_${response.status}`));
      }
      const fresh = record(payload.fresh_agent_capsule_chat);
      const freshBinding = record(payload.chat_context_binding);
      const refs = stringList(freshBinding.context_floor_refs).filter((ref) => !ref.startsWith('/')).slice(0, 18);
      if (refs.length) {
        setSelectedContextRefs((previous) => uniqueStrings([...previous, ...refs]).slice(-36));
      }
      setLeftDrawer('context');
      setLeftDrawerOpen(true);
      setActionNotice(`Fresh context chat ready: ${text(fresh.target_ref, 'new context folder')} / ${text(fresh.launch_command, 'codex -C <folder>')}`);
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'fresh_context_chat_failed');
    } finally {
      setNewCapsuleChatBusy(false);
    }
  }

  function buildContextSystemInventoryRows(): ContextSystemInventoryRow[] {
    const bindings = records(record(chat?.chat_context).bindings);
    const freshChats = records(chat?.fresh_agent_capsule_chats);
    const activeTabSession = sessionFromOpenChatTab(activeChatTab) ?? selectedSession;
    const activeTabContextBinding = record(record(activeTabSession).chat_context_binding);
    const activeUsesArchive = Boolean(activeChatTab || showingArchiveChat);
    const activeChatContextBinding = Object.keys(activeTabContextBinding).length
      ? activeTabContextBinding
      : activeUsesArchive
        ? {}
        : record(record(chat?.chat_context).active_binding);
    const activeChatIdentity = record(activeChatContextBinding.agent_identity);
    const activeTabMissionLabels = records(activeTabSession?.mission_labels);
    const activeTabAgentLabels = records(activeTabSession?.agent_labels);
    const activeRoleId = text(
      activeChatIdentity.clone_of_role_id
      || activeChatIdentity.role_id
      || activeChatContextBinding.role_id
      || activeTabAgentLabels[0]?.role_id
      || activeTabAgentLabels[0]?.agent_id
      || activeTabAgentLabels[0]?.label,
      '',
    );
    const activeDomainId = text(
      activeChatContextBinding.domain_id
      || activeTabMissionLabels[0]?.domain_id
      || activeTabMissionLabels[0]?.label,
      '',
    );

    return contextAgentRows.map((agent) => {
      const agentId = agentRecordId(agent);
      const evidence = record(agent.agent_page_evidence);
      const identity = record(evidence.identity);
      const contextSystem = record(evidence.context_system);
      const contextCard = record(contextSystem.card);
      const proof = record(evidence.proof);
      const roleId = text(agent.role_id || agent.agent_id || identity.role_id || agentId, '');
      const domainId = text(agent.registry_primary_domain || identity.domain_id || agent.role_domain_label, '');
      const displayName = text(agent.display_name || identity.display_name || roleId || agentId, 'context system');
      const packageClass = text(contextSystem.default_active_package_class || agent.default_active_package_class, 'UNCLASSIFIED_CONTEXT_PACKAGE');
      const packageStrategy = text(contextSystem.package_strategy || agent.package_strategy, 'strategy pending');
      const status = Boolean(proof.critical_ready) ? 'proven' : text(contextSystem.status || agent.context_system_status, 'projected');
      const cardPath = text(contextCard.relpath || contextCard.path || agent.context_system_card, '');
      const contextPaths = records(contextSystem.context_paths).length
        ? records(contextSystem.context_paths)
        : records(agent.context_paths);
      const isIonContextSystem = Boolean(identity.is_ion_context_system);
      const isCapsuleAgent = Boolean(identity.is_capsule_agent || record(evidence.capsule).is_capsule_agent);
      const isCodexNativeMount = Boolean(identity.is_codex_native_mount);
      const isPortablePackageAgent = Boolean(identity.is_portable_package_agent);
      const mappedBindings = bindings.filter((binding) => {
        const branchIdentity = record(binding.agent_identity);
        const bindingRole = text(branchIdentity.clone_of_role_id || branchIdentity.role_id || binding.role_id, '');
        const bindingDomain = text(binding.domain_id, '');
        return Boolean((roleId && bindingRole === roleId) || (domainId && bindingDomain === domainId));
      });
      const mappedFreshChats = freshChats.filter((fresh) => {
        const freshBinding = record(fresh.chat_context_binding);
        const branchIdentity = record(freshBinding.agent_identity);
        const freshRole = text(fresh.role_id || branchIdentity.clone_of_role_id || branchIdentity.role_id || freshBinding.role_id, '');
        const freshDomain = text(fresh.domain_id || freshBinding.domain_id, '');
        return Boolean((roleId && freshRole === roleId) || (domainId && freshDomain === domainId));
      });
      const mappedOpenTabs = openChatTabs.filter((tab) => {
        const session = allSessions.find((candidate) => candidate.session_id === tab.sessionId) ?? sessionFromOpenChatTab(tab);
        const tabAgents = records(session?.agent_labels);
        const tabMissions = records(session?.mission_labels);
        return tabAgents.some((label) => text(label.role_id || label.agent_id || label.label, '') === roleId)
          || tabMissions.some((label) => domainId && text(label.domain_id || label.label, '') === domainId);
      });
      const variationTags = uniqueStrings([
        packageClass,
        status,
        isIonContextSystem ? 'ION_CONTEXT_SYSTEM' : '',
        isCapsuleAgent ? 'LOCAL_CONTEXT_AGENT' : '',
        isCodexNativeMount ? 'CODEX_NATIVE_MOUNT' : '',
        isPortablePackageAgent ? 'PORTABLE_PACKAGE' : '',
        cardPath ? 'CONTEXT_CARD' : 'CARD_MISSING',
      ]).slice(0, 8);
      return {
        agent,
        agentId,
        roleId,
        domainId,
        displayName,
        status,
        packageClass,
        packageStrategy,
        cardPath,
        cardExists: Boolean(contextCard.exists || cardPath),
        contextRefCount: contextPaths.length,
        variationTags,
        mappedBindings,
        mappedFreshChats,
        mappedOpenTabs,
        activeForCurrentChat: Boolean((roleId && activeRoleId === roleId) || (domainId && activeDomainId === domainId)),
      };
    });
  }

  function selectedContextSystemInventoryRow(rows: ContextSystemInventoryRow[]) {
    const selectedId = text(selectedContextAgentId, '');
    return rows.find((row) => row.agentId === selectedId || row.roleId === selectedId)
      ?? rows.find((row) => row.activeForCurrentChat)
      ?? rows[0]
      ?? null;
  }

  function renderContextSystemSetupPanel(rows: ContextSystemInventoryRow[], options: { compact?: boolean } = {}) {
    const compact = Boolean(options.compact);
    const selectedRow = selectedContextSystemInventoryRow(rows);
    const selectedAgent = selectedRow?.agent;
    const selectedValue = selectedRow?.agentId || '';
    return (
      <article className={`ion-codex-context-system-setup${compact ? ' is-compact' : ''}`}>
        <header>
          <div>
            <span>new chat context system</span>
            <b>{selectedRow?.displayName ?? 'no context systems'}</b>
            <code>{selectedRow?.packageClass ?? 'inventory unavailable'}</code>
          </div>
          <button
            disabled={!selectedAgent || newCapsuleChatBusy}
            onClick={() => {
              if (selectedAgent) void createNewCapsuleChat(selectedAgent);
            }}
            type="button"
          >
            {newCapsuleChatBusy ? 'STARTING' : 'START CHAT'}
          </button>
        </header>
        <label className="ion-codex-context-system-select">
          <span>context system</span>
          <select
            aria-label="Select context system for new Codex chat"
            disabled={!rows.length || newCapsuleChatBusy}
            onChange={(event) => setSelectedContextAgentId(event.currentTarget.value)}
            value={selectedValue}
          >
            {!rows.length ? <option value="">No context systems projected</option> : null}
            {rows.map((row) => (
              <option key={row.agentId || row.roleId || row.displayName} value={row.agentId}>
                {row.displayName} / {row.roleId || row.domainId || 'role pending'}
              </option>
            ))}
          </select>
        </label>
        {selectedRow ? (
          <div className="ion-codex-context-system-setup-detail">
            <div className="ion-codex-context-system-tags">
              {selectedRow.variationTags.map((tag) => <span key={tag}>{tag}</span>)}
            </div>
            <DataBlock title="setup target" compact rows={[
              ['domain', selectedRow.domainId || 'domain pending'],
              ['role', selectedRow.roleId || 'role pending'],
              ['context card', selectedRow.cardPath || 'unmapped'],
              ['package strategy', selectedRow.packageStrategy],
            ]} />
          </div>
        ) : null}
      </article>
    );
  }

  function renderContextSystemInventory(rows: ContextSystemInventoryRow[], options: { compact?: boolean; includeSetup?: boolean } = {}) {
    const compact = Boolean(options.compact);
    const freshChatCount = rows.reduce((count, row) => count + row.mappedFreshChats.length, 0);
    const bindingCount = rows.reduce((count, row) => count + row.mappedBindings.length, 0);
    const openTabCount = rows.reduce((count, row) => count + row.mappedOpenTabs.length, 0);
    const packageClasses = uniqueStrings(rows.map((row) => row.packageClass).filter(Boolean));
    const selectedRow = selectedContextSystemInventoryRow(rows);
    return (
      <article className={`ion-codex-context-system-inventory${compact ? ' is-compact' : ' is-full'}`}>
        <header>
          <div>
            <span>context system inventory</span>
            <b>{rows.length} systems / {packageClasses.length} variations</b>
            <code>{packageClasses.slice(0, 4).join(' / ') || 'no package classes projected'}</code>
          </div>
          <div className="ion-codex-context-system-inventory-metrics">
            <ContextPill label="bindings" value={bindingCount} />
            <ContextPill label="fresh chats" value={freshChatCount} />
            <ContextPill label="open tabs" value={openTabCount} />
          </div>
        </header>
        {options.includeSetup ? renderContextSystemSetupPanel(rows, { compact }) : null}
        <div className="ion-codex-context-system-inventory-grid">
          {rows.map((row) => (
            <section
              className={`ion-codex-context-system-row${row.activeForCurrentChat ? ' is-active-chat' : ''}${selectedRow?.agentId === row.agentId ? ' is-selected' : ''}`}
              key={row.agentId || row.roleId || row.domainId}
            >
              <header>
                <div>
                  <span>{row.domainId || 'domain pending'}</span>
                  <b>{row.displayName}</b>
                  <code>{row.roleId || row.agentId || 'role pending'}</code>
                </div>
                <em>{row.status}</em>
              </header>
              <div className="ion-codex-context-system-tags">
                {row.variationTags.slice(0, compact ? 4 : 7).map((tag) => <span key={tag}>{tag}</span>)}
              </div>
              <div className="ion-codex-context-system-counts">
                <ContextPill label="refs" value={row.contextRefCount} />
                <ContextPill label="bindings" value={row.mappedBindings.length} />
                <ContextPill label="fresh" value={row.mappedFreshChats.length} />
                <ContextPill label="tabs" value={row.mappedOpenTabs.length} />
              </div>
              <code className="ion-codex-context-system-card-ref">{row.cardPath || 'context card unmapped'}</code>
              {compact ? null : (
                <div className="ion-codex-context-system-chat-links">
                  {row.mappedFreshChats.slice(0, 3).map((fresh) => (
                    <code key={text(fresh.fresh_chat_id || fresh.target_ref, 'fresh')}>{text(fresh.title || fresh.target_ref || fresh.launch_command, 'fresh context chat')}</code>
                  ))}
                  {row.mappedOpenTabs.slice(0, 3).map((tab) => (
                    <button key={tab.id} onClick={() => selectOpenChatTab(tab)} type="button">{chatTitleForSessionId(tab.sessionId, tab.title)}</button>
                  ))}
                  {!row.mappedFreshChats.length && !row.mappedOpenTabs.length ? <small>no mapped chats</small> : null}
                </div>
              )}
              <div className="ion-codex-context-system-actions">
                <button
                  onClick={() => {
                    setSelectedContextAgentId(row.agentId);
                    setLeftDrawer('context');
                    setLeftDrawerOpen(true);
                  }}
                  type="button"
                >
                  INSPECT
                </button>
                <button disabled={newCapsuleChatBusy} onClick={() => void createNewCapsuleChat(row.agent)} type="button">
                  CHAT
                </button>
              </div>
            </section>
          ))}
          {rows.length === 0 ? <div className="ion-empty-state">NO CONTEXT SYSTEMS PROJECTED</div> : null}
        </div>
      </article>
    );
  }

  function renderContextSystemChatMap() {
    const rows = buildContextSystemInventoryRows();
    return renderContextSystemInventory(rows, { includeSetup: true });
  }

  function renderIonOrchestrationPane() {
    const pipelineStatus = text(latestIonPipelineRun.status, latestIonPipelineStages.length ? 'pipeline projected' : 'waiting for ION prompt');
    const chainMode = text(agentControlChain.single_carrier_sequential, false) === 'true' ? 'single carrier sequential' : text(record(chat?.ion_comms).mode || 'full ION comms projection', 'full ION comms projection');
    return (
      <section className="ion-codex-ion-console">
        {renderOpenChatTabs()}
        <div className="ion-codex-ion-workspace">
          <section className="ion-codex-ion-primary">
            {renderIonTruthPanel({ chainMode, pipelineStatus })}
            <div className="ion-codex-ion-chat-stage">
              <div className="ion-codex-ion-section-head">
                <div>
                  <span>persona chat</span>
                  <b>{ionLiveTranscriptGroups.length ? `${ionLiveTranscriptGroups.length} ION turns` : 'ready for ION'}</b>
                </div>
                <code>{text(record(chat?.lanes).ion_system ? record(record(chat?.lanes).ion_system).label : 'ION Comms Adapter', 'ION Comms Adapter')}</code>
              </div>
              <div className="ion-codex-transcript is-live ion-codex-ion-transcript">
                {ionLiveTranscriptGroups.map((group, index) => (
                  <TurnGroup
                    key={text(group.group_id, `ion-turn-${index}`)}
                    group={group}
                    latestAssistantKey={latestIonAssistantKey}
                    onBranch={branchMessage}
                    onCopy={copyMessageText}
                    onPin={pinMessageText}
                    onQuote={quoteMessageText}
                    onRun={runMessageText}
                  />
                ))}
                {ionLiveTranscriptGroups.length === 0 && <div className="ion-empty-state">NO ION PIPELINE TURNS</div>}
              </div>
            </div>
          </section>
          <aside className="ion-codex-ion-side-stack">
            {renderIonPhaseMap()}
            {renderIonTeamComms()}
            {renderIonProtocolStatus()}
          </aside>
        </div>
        {renderChatCommandBar()}
        {renderCodexComposer('ion_system')}
        {renderContextDiffSubwayMap()}
      </section>
    );
  }

  function renderIonTruthPanel({ chainMode, pipelineStatus }: { chainMode: string; pipelineStatus: string }) {
    const topBar = runtime.top_bar;
    const rawServiceStatus = text(topBar.local_service_status || record(runtime.local_services).status || record(runtime.service_console).verdict, 'served cockpit');
    const serviceStatus = rawServiceStatus.toLowerCase().includes('missing_template') ? 'served' : rawServiceStatus;
    const serviceDetail = rawServiceStatus === serviceStatus ? 'served bundle and local preview surface' : `served bundle / console ${rawServiceStatus}`;
    const serviceLower = serviceStatus.toLowerCase();
    const cockpitTone: IonTruthTone = serviceLower.includes('fail') || serviceLower.includes('error') || serviceLower.includes('missing') ? 'blocked' : 'ready';
    const chatReady = verdictClass(chat?.verdict || topBar.codex_capsule_chat_verdict) === 'ready';
    const cliReady = verdictClass(cli?.verdict || topBar.codex_cli_workbench_verdict) === 'ready';
    const agentCount = contextAgentRows.length || numberValue(contextAgentSummary.agent_count || topBar.agent_control_plane_agent_count);
    const domainCount = numberValue(contextAgentSummary.domain_count || topBar.agent_control_plane_domain_count);
    const controlReady = verdictClass(agentControlPlane.verdict || (agentCount ? 'ready' : '')) === 'ready';
    const readySurfaceCount = [cockpitTone === 'ready', chatReady, cliReady, controlReady].filter(Boolean).length;
    const truthWorkerActive = workerActive;
    const activeWorkerLabel = truthWorkerActive ? workerDuration || 'active' : 'idle';
    const activeWorkerRequest = shortOperationalId(
      queueTelemetry.active_request_id
      || queueTelemetry.request_id
      || queueTelemetryRun.request_id
      || queueTelemetryRun.run_id
    );
    const dispatcherSummary = record(agentControlDispatcher.summary);
    const pendingDirectives = numberValue(
      dispatcherSummary.pending_directive_count
      || agentControlDispatcher.pending_directive_count
      || contextAgentSummary.dispatcher_pending_directive_count
    );
    const activeWorkers = Math.max(
      numberValue(dispatcherSummary.active_worker_count || contextAgentSummary.dispatcher_active_worker_count),
      truthWorkerActive ? 1 : 0,
    );
    const schedulerValue = truthWorkerActive ? 'running' : queuedRequestCount || pendingDirectives ? 'ready' : 'idle';
    const schedulerTone: IonTruthTone = truthWorkerActive ? 'active' : queuedRequestCount || pendingDirectives ? 'watch' : 'ready';
    const nextRequest = record(queue.next_request);
    const nextRequestLabel = shortOperationalId(
      queue.next_request_path
      || nextRequest.path
      || queueTelemetry.active_request_id
      || queueTelemetryRun.request_id
      || chat?.codex_queue_path
    ) || (queuedRequestCount ? 'queue head' : 'none');
    const returnRows = [...records(chat?.latest_task_returns), ...mcpTaskReturns];
    const latestReturn = returnRows[returnRows.length - 1] ?? {};
    const latestReturnLabel = shortOperationalId(latestReturn.latest_return_path || latestReturn.path || latestReturn.status || latestReturn.summary) || 'none';
    const receiptCount = agentCommsReceipts.length || numberValue(record(agentControlComms.summary).receipt_count);
    const overallTone: IonTruthTone = truthWorkerActive ? 'active' : readySurfaceCount >= 3 ? 'ready' : readySurfaceCount > 0 ? 'watch' : 'blocked';
    const overallValue = truthWorkerActive ? 'ION is working' : readySurfaceCount >= 3 ? 'ION is running' : 'ION needs attention';
    const plainState = truthWorkerActive
      ? `Mounted and executing ${activeWorkerRequest || 'worker from queue runner'} for ${activeWorkerLabel}. The persona chat remains usable while the worker runs.`
      : queuedRequestCount
        ? `Mounted with ${agentCount || 0} agents, ${domainCount || 0} domains, and ${queuedRequestCount} queued request${queuedRequestCount === 1 ? '' : 's'}. No worker is active.`
        : `Mounted with ${agentCount || 0} agents and ${domainCount || 0} domains. Queue is empty and the persona front door is ready.`;
    const truthCards: Array<{
      id: string;
      label: string;
      value: string;
      detail: string;
      tone: IonTruthTone;
      onClick: () => void;
    }> = [
      {
        id: 'core',
        label: 'core',
        value: readySurfaceCount >= 3 ? 'running' : `${readySurfaceCount}/4 ready`,
        detail: `chat ${chatReady ? 'ready' : 'check'} / cli ${cliReady ? 'ready' : 'check'} / control ${controlReady ? 'ready' : 'check'}`,
        tone: overallTone,
        onClick: () => {
          setRightDrawer('status');
          setRightDrawerOpen(true);
        },
      },
      {
        id: 'cockpit',
        label: 'cockpit',
        value: serviceStatus,
        detail: serviceDetail,
        tone: cockpitTone,
        onClick: () => setCommandPanel('carrier'),
      },
      {
        id: 'agents',
        label: 'agents',
        value: `${agentCount || 0} agents`,
        detail: `${domainCount || 0} domains / ${activeWorkers} active`,
        tone: activeWorkers ? 'active' : agentCount ? 'ready' : 'watch',
        onClick: () => {
          setLeftDrawer('agents');
          setLeftDrawerOpen(true);
        },
      },
      {
        id: 'scheduler',
        label: 'scheduler',
        value: schedulerValue,
        detail: `${pendingDirectives} pending / kernel projection`,
        tone: schedulerTone,
        onClick: () => setCommandPanel('carrier'),
      },
      {
        id: 'queue',
        label: 'queue',
        value: `${queuedRequestCount} waiting`,
        detail: nextRequestLabel,
        tone: queueDispatchActive ? 'active' : queuedRequestCount ? 'watch' : 'empty',
        onClick: () => {
          setRightDrawer('messageQueue');
          setRightDrawerOpen(true);
        },
      },
      {
        id: 'context',
        label: 'context',
        value: capsuleHealth.label,
        detail: capsuleHealth.detail,
        tone: capsuleHealth.tone as IonTruthTone,
        onClick: () => setCommandPanel('context'),
      },
      {
        id: 'receipts',
        label: 'receipts',
        value: String(receiptCount),
        detail: latestReturnLabel,
        tone: receiptCount ? 'ready' : 'empty',
        onClick: () => {
          setRightDrawer('evidence');
          setRightDrawerOpen(true);
        },
      },
      {
        id: 'next',
        label: 'next action',
        value: truthWorkerActive ? 'monitor' : queuedRequestCount ? 'start queue' : 'prompt',
        detail: pipelineStatus,
        tone: truthWorkerActive ? 'active' : queuedRequestCount ? 'watch' : 'ready',
        onClick: () => setCommandPanel(queuedRequestCount ? 'queue' : 'agent'),
      },
    ];
    const truthFlow: Array<{ id: string; label: string; value: string; detail: string; tone: IonTruthTone }> = [
      { id: 'built', label: 'built', value: 'bundle', detail: 'cockpit shell loaded', tone: 'ready' },
      { id: 'served', label: 'served', value: serviceStatus, detail: 'preview route', tone: cockpitTone },
      { id: 'mounted', label: 'mounted', value: `${agentCount || 0} agents`, detail: `${domainCount || 0} domains`, tone: agentCount ? 'ready' : 'watch' },
      { id: 'context', label: 'context', value: capsuleHealth.label, detail: capsuleHealth.detail, tone: capsuleHealth.tone as IonTruthTone },
      { id: 'queued', label: 'queued', value: String(queuedRequestCount), detail: nextRequestLabel, tone: queuedRequestCount ? 'watch' : 'empty' },
      { id: 'running', label: 'running', value: activeWorkerLabel, detail: activeWorkerRequest || workerStatus, tone: truthWorkerActive ? 'active' : 'empty' },
      { id: 'returned', label: 'returned', value: String(returnRows.length), detail: latestReturnLabel, tone: returnRows.length ? 'ready' : 'empty' },
      { id: 'settled', label: 'settled', value: String(receiptCount), detail: `${agentCommsRelays.length} relays`, tone: receiptCount ? 'ready' : 'empty' },
    ];
    return (
      <section className={`ion-codex-ion-truth is-${overallTone}`} aria-label="ION operational truth">
        <div className="ion-codex-ion-truth-answer">
          <span>ION state</span>
          <b>{overallValue}</b>
          <p>{plainState}</p>
          <code>{chainMode} / refreshed {text(runtime.generated_at, 'now')}</code>
        </div>
        <div className="ion-codex-ion-truth-grid">
          {truthCards.map((card) => (
            <button
              className={`ion-codex-ion-truth-card is-${card.tone}`}
              key={card.id}
              onClick={card.onClick}
              title={`${card.label}: ${card.value}. ${card.detail}`}
              type="button"
            >
              <span>{card.label}</span>
              <b>{card.value}</b>
              <em>{card.detail}</em>
            </button>
          ))}
        </div>
        <div className="ion-codex-ion-truth-flow" aria-label="ION state ladder">
          {truthFlow.map((step) => (
            <button
              className={`ion-codex-ion-truth-step is-${step.tone}`}
              key={step.id}
              title={`${step.label}: ${step.value}. ${step.detail}`}
              type="button"
            >
              <span>{step.label}</span>
              <b>{step.value}</b>
            </button>
          ))}
        </div>
      </section>
    );
  }

  function renderIonPhaseMap() {
    const phaseRows = ionPipelinePhaseRows(latestIonPipelineStages, agentChainSteps, workerActive);
    return (
      <section className="ion-codex-ion-panel ion-codex-ion-phase-panel" aria-label="ION role pipeline">
        <div className="ion-codex-ion-panel-head">
          <span>role pipeline</span>
          <b>{text(latestIonPipelineRun.run_id, 'projected chain')}</b>
        </div>
        <div className="ion-codex-ion-phase-track">
          {phaseRows.map((phase, index) => (
            <button
              className={`ion-codex-ion-phase-card is-${phase.tone}`}
              key={`${phase.stageId}-${index}`}
              onClick={() => {
                setCommandPanel('agent');
              }}
              title={`${phase.label}: ${phase.roleId}. ${phase.detail}`}
              type="button"
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              <b>{phase.label}</b>
              <em>{phase.roleId}</em>
              <code>{phase.status}</code>
            </button>
          ))}
        </div>
      </section>
    );
  }

  function renderIonTeamComms() {
    const commRows = [
      ...agentCommsPendingRelays.map((row) => ({ ...row, _ion_kind: 'pending relay' })),
      ...agentCommsRelays.slice(-6).map((row) => ({ ...row, _ion_kind: 'relay' })),
      ...agentCommsTimeline.slice(-8).map((row) => ({ ...row, _ion_kind: 'timeline' })),
      ...mcpCarrierMessages.slice(-4).map((row) => ({ ...row, _ion_kind: 'carrier' })),
      ...mcpAgentInvocations.slice(-4).map((row) => ({ ...row, _ion_kind: 'agent call' })),
      ...mcpTaskReturns.slice(-4).map((row) => ({ ...row, _ion_kind: 'return' })),
    ].slice(-18).reverse();
    return (
      <section className="ion-codex-ion-panel ion-codex-ion-comms-panel" aria-label="ION team communications">
        <div className="ion-codex-ion-panel-head">
          <span>team comms</span>
          <b>{agentCommsTimeline.length + agentCommsRelays.length + mcpCarrierMessages.length}</b>
        </div>
        <div className="ion-codex-ion-comms-list">
          {commRows.map((row, index) => (
            <button
              className={`ion-codex-ion-comms-row is-${safeClass(text(row._ion_kind, 'event'))}`}
              key={`${text(row.id || row.message_id || row.receipt_id || row.path || row.created_at, 'comm')}-${index}`}
              onClick={() => {
                setRightDrawer('assistant');
                setRightDrawerOpen(true);
              }}
              title={text(row.summary || row.message || row.detail || row.path || row.status, 'ION communication event')}
              type="button"
            >
              <span>{text(row._ion_kind, 'event')}</span>
              <b>{text(row.title || row.label || row.from_role || row.agent_role_id || row.role_id || row.status || row.event_type, 'ION event')}</b>
              <em>{text(row.to_role || row.target_role || row.packet_id || row.path || row.created_at || row.updated_at, 'visible comm evidence')}</em>
            </button>
          ))}
          {commRows.length === 0 && <div className="ion-empty-state">NO TEAM COMMS PROJECTED</div>}
        </div>
      </section>
    );
  }

  function renderIonProtocolStatus() {
    const domainWeaverSummary = record(agentControlDomainWeaver.summary);
    const dispatcherSummary = record(agentControlDispatcher.summary);
    const commsSummary = record(agentControlComms.summary);
    const authority = record(agentControlPlane.authority);
    const teamCommsSummary = record(agentTeamComms.summary);
    return (
      <section className="ion-codex-ion-panel ion-codex-ion-protocol-panel" aria-label="ION context and authority">
        <div className="ion-codex-ion-panel-head">
          <span>context protocol</span>
          <b>{capsuleHealth.label}</b>
        </div>
        <div className="ion-codex-ion-protocol-grid">
            <ContextPill label="floor" value={capsuleHealth.label} />
          <ContextPill label="domains" value={domainWeaverSummary.domain_count || contextAgentSummary.domain_count || 0} />
          <ContextPill label="gaps" value={domainWeaverSummary.gap_count || contextAgentSummary.domain_weaver_gap_count || 0} />
          <ContextPill label="threads" value={teamCommsSummary.thread_count || commsSummary.team_thread_count || 0} />
          <ContextPill label="receipts" value={agentCommsReceipts.length || commsSummary.receipt_count || 0} />
          <ContextPill label="dispatcher" value={dispatcherSummary.active_worker_count || contextAgentSummary.dispatcher_active_worker_count || 0} />
        </div>
        <div className="ion-codex-ion-authority-strip">
          <code>production {text(authority.production_authority ?? agentControlPlane.production_authority, false)}</code>
          <code>live {text(authority.live_execution_authority ?? agentControlPlane.live_execution_authority, false)}</code>
          <code>accepted {text(authority.accepted_state_authority ?? agentControlPlane.accepted_state_authority, false)}</code>
          <code>secrets {text(authority.secrets_authority ?? agentControlPlane.secrets_authority, false)}</code>
        </div>
      </section>
    );
  }

  function renderOpenChatTabs() {
    return (
      <div className="ion-codex-open-chat-tabs" role="tablist" aria-label="Open Codex chats">
        <div className="ion-codex-open-chat-history" onMouseLeave={() => setChatHistoryMenuOpen(false)}>
          <button
            aria-expanded={chatHistoryMenuOpen}
            aria-label="Open chat history menu"
            className={`ion-codex-open-chat-history-button${chatHistoryMenuOpen ? ' is-open' : ''}`}
            onClick={() => setChatHistoryMenuOpen((open) => !open)}
            title="Chat history"
            type="button"
          >
            <ArchiveIcon />
          </button>
          {chatHistoryMenuOpen ? (
            <div className="ion-codex-open-chat-history-menu" role="menu">
              <div className="ion-codex-open-chat-history-head">
                <b>CHAT HISTORY</b>
                <span>{chatHistoryEntries.length} chats</span>
              </div>
              <div className="ion-codex-open-chat-history-sort" aria-label="Chat history order">
                {chatHistorySortOptions.map((option) => (
                  <button
                    className={chatHistorySort === option.id ? 'is-active' : ''}
                    key={option.id}
                    onClick={() => setChatHistorySort(option.id)}
                    type="button"
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              <div className="ion-codex-open-chat-history-list">
                {chatHistoryEntries.length ? chatHistoryEntries.slice(0, 48).map((entry) => (
                  <button
                    key={entry.session.session_id}
                    onClick={() => {
                      setChatHistoryMenuOpen(false);
                      void openSession(entry.session, { activateArchive: false, showInChat: true });
                    }}
                    role="menuitem"
                    type="button"
                  >
                    <b>{entry.title}</b>
                    <span>{entry.detail}</span>
                  </button>
                )) : (
                  <div className="ion-codex-open-chat-history-empty">NO SAVED CHATS</div>
                )}
              </div>
            </div>
          ) : null}
        </div>
        <div className="ion-codex-open-chat-tab-scroll">
          {openChatTabs.map((tab) => {
            const tabTitle = chatTitleForSessionId(tab.sessionId, tab.title);
            return (
              <div
                className={`ion-codex-open-chat-tab${activeChatTabId === tab.id && showingArchiveChat ? ' is-active' : ''}`}
                key={tab.id}
                onBlur={hideChatTabInfo}
                onFocus={(event) => showChatTabInfo(event, tab.sessionId)}
                onMouseEnter={(event) => showChatTabInfo(event, tab.sessionId)}
                onMouseLeave={hideChatTabInfo}
                role="presentation"
              >
                {renamingChatId === tab.sessionId ? (
                  <form className="ion-codex-open-chat-tab-edit" onSubmit={(event) => { event.preventDefault(); commitRenameChat(); }}>
                    <input
                      aria-label={`Rename ${tabTitle}`}
                      autoFocus
                      onChange={(event) => setRenameDraft(event.currentTarget.value)}
                      onKeyDown={(event) => {
                        if (event.key === 'Escape') {
                          event.preventDefault();
                          cancelRenameChat();
                        }
                      }}
                      value={renameDraft}
                    />
                    <button aria-label="Save chat name" title="Save chat name" type="submit">
                      <CheckIcon className="ion-codex-rename-icon" />
                    </button>
                    <button aria-label="Cancel rename" onClick={cancelRenameChat} title="Cancel rename" type="button">
                      <CloseIcon className="ion-close-icon" />
                    </button>
                  </form>
                ) : (
                  <>
                    <button
                      className="ion-codex-open-chat-tab-main"
                      onClick={() => selectOpenChatTab(tab)}
                      onDoubleClick={() => startRenameChat(tab.sessionId, tabTitle)}
                      role="tab"
                      title="Double click to rename. Hover for chat details."
                      type="button"
                    >
                      <b>{tabTitle}</b>
                      <span>{tab.isCurrent ? 'CURRENT' : sessionShortText(tab.sessionId)} / {tab.model || 'model unknown'}</span>
                    </button>
                  </>
                )}
                <button aria-label={`Close ${tabTitle}`} className="ion-codex-open-chat-tab-close" onClick={() => closeOpenChatTab(tab.id)} title={`Close ${tabTitle}`} type="button">
                  <CloseIcon className="ion-close-icon" />
                </button>
              </div>
            );
          })}
          {openChatTabs.length === 0 ? <span className="ion-codex-open-chat-empty">ARCHIVE TABS CLOSED</span> : null}
        </div>
        {renderChatTabHoverPanel()}
      </div>
    );
  }

  function renderChatTabHoverPanel() {
    const hoverInfo = chatTabHoverInfo;
    if (!hoverInfo) return null;
    const sessionId = hoverInfo.sessionId;
    const isLive = sessionId === 'live:codex';
    const tab = openChatTabs.find((candidate) => candidate.sessionId === sessionId) ?? null;
    const session = isLive
      ? currentArchiveSession
      : allSessions.find((candidate) => candidate.session_id === sessionId) ?? sessionFromOpenChatTab(tab);
    const sourceSessionId = text((isLive ? currentArchiveSessionId : '') || session?.session_id || tab?.sessionId || sessionId, sessionId);
    const isCurrent = Boolean(isLive || session?.is_current_session || (currentArchiveSessionId && sourceSessionId === currentArchiveSessionId));
    const title = isLive
      ? CODEX_CURRENT_SESSION_TITLE
      : session
        ? chatTitleForSession(session)
        : chatTitleForSessionId(sessionId, tab?.title || 'Past chat');
    const model = text(session?.model || tab?.model || record(chat?.response_carrier).selected_model || record(record(settings.project_config)).default_model || 'model unknown', 'model unknown');
    const hoverExcerpt = !isLive && sourceSessionId === selectedArchiveSessionId ? selectedExcerpt : null;
    const windowSummary = hoverExcerpt
      ? archiveTranscriptWindowLabel(hoverExcerpt)
      : session
        ? `${text(session.history_prompt_count, 0)} prompts / ${text(session.line_count_sampled, 0)} events`
        : text(tab?.subtitle, 'not loaded');
    const rows: Array<[string, unknown]> = [
      ['id', sessionShortText(sourceSessionId)],
      ['project', session ? projectLabel(session) : tab?.projectLabel || 'Project Unknown'],
      ['model', model],
      ['time', session ? formatSessionTime(session) : tab?.lastViewedAt || tab?.openedAt || 'not loaded'],
      ['cwd', session?.cwd || 'not loaded'],
      ['items', windowSummary],
    ];
    return (
      <div
        className="ion-codex-open-chat-tab-hover"
        style={{
          left: hoverInfo.left,
          top: hoverInfo.top,
          width: hoverInfo.width,
        } as CSSProperties}
      >
        <span>{isLive ? 'LIVE CODEX CLI CHAT' : isCurrent ? 'CURRENT CODEX CLI CHAT' : 'PAST CODEX CLI CHAT'}</span>
        <b>{title}</b>
        <code>{sourceSessionId} / {model}</code>
        <div>
          {rows.map(([label, value]) => (
            <p key={label}>
              <em>{label}</em>
              <strong>{text(value)}</strong>
            </p>
          ))}
        </div>
      </div>
    );
  }

  function scrollChatTimelineTarget(mode: 'live' | 'archive', targetIndex: number) {
    const node = mode === 'archive' ? archiveTranscriptRef.current : transcriptRef.current;
    if (!node) return;
    const target = node.querySelector<HTMLElement>(`[data-turn-index="${targetIndex}"]`);
    if (target) {
      target.scrollIntoView({ block: 'center', behavior: 'smooth' });
      return;
    }
    const denominator = mode === 'archive'
      ? Math.max(1, records(selectedExcerpt?.items).length)
      : Math.max(1, liveTranscriptGroups.length);
    const progress = denominator <= 1 ? 0 : targetIndex / Math.max(1, denominator - 1);
    node.scrollTop = Math.max(0, (node.scrollHeight - node.clientHeight) * progress);
    syncChatTimelineScrollRatio(node);
  }

  function transcriptNodeForTimelineMode(mode: 'live' | 'archive') {
    return mode === 'archive' ? archiveTranscriptRef.current : transcriptRef.current;
  }

  function syncChatTimelineScrollRatio(node: HTMLDivElement | null) {
    if (!node) return;
    const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
    setChatTimelineScrollRatio(maxTop > 0 ? Math.max(0, Math.min(1, node.scrollTop / maxTop)) : 0);
  }

  function scrollTranscriptTimelineToRatio(mode: 'live' | 'archive', ratio: number) {
    const node = transcriptNodeForTimelineMode(mode);
    if (!node) return;
    const nextRatio = Math.max(0, Math.min(1, ratio));
    const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
    node.scrollTop = maxTop * nextRatio;
    if (mode === 'live') {
      livePinnedToBottomRef.current = isTranscriptNearBottom(node, LIVE_BOTTOM_STICKY_PX);
    } else {
      archiveLastScrollTopRef.current = node.scrollTop;
    }
    syncChatTimelineScrollRatio(node);
  }

  function scrollTranscriptTimelineFromPointer(mode: 'live' | 'archive', event: ReactPointerEvent<HTMLDivElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    const ratio = rect.height > 0 ? (event.clientY - rect.top) / rect.height : 0;
    scrollTranscriptTimelineToRatio(mode, ratio);
  }

  function handleVerticalChatTimelinePointerDown(mode: 'live' | 'archive', event: ReactPointerEvent<HTMLDivElement>) {
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    scrollTranscriptTimelineFromPointer(mode, event);
  }

  function handleVerticalChatTimelinePointerMove(mode: 'live' | 'archive', event: ReactPointerEvent<HTMLDivElement>) {
    if (!event.currentTarget.hasPointerCapture(event.pointerId)) return;
    scrollTranscriptTimelineFromPointer(mode, event);
  }

  function handleVerticalChatTimelinePointerEnd(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  }

  function handleVerticalChatTimelineKeyDown(mode: 'live' | 'archive', event: ReactKeyboardEvent<HTMLDivElement>) {
    const node = transcriptNodeForTimelineMode(mode);
    if (!node) return;
    const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
    const currentRatio = maxTop > 0 ? node.scrollTop / maxTop : 0;
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      scrollTranscriptTimelineToRatio(mode, currentRatio - 0.04);
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      scrollTranscriptTimelineToRatio(mode, currentRatio + 0.04);
    } else if (event.key === 'PageUp') {
      event.preventDefault();
      scrollTranscriptTimelineToRatio(mode, currentRatio - 0.18);
    } else if (event.key === 'PageDown') {
      event.preventDefault();
      scrollTranscriptTimelineToRatio(mode, currentRatio + 0.18);
    } else if (event.key === 'Home') {
      event.preventDefault();
      scrollTranscriptTimelineToRatio(mode, 0);
    } else if (event.key === 'End') {
      event.preventDefault();
      scrollTranscriptTimelineToRatio(mode, 1);
    }
  }

  function renderVerticalChatTimelineScrollbar({
    groups,
    mode,
    label,
    sequenceItems,
    sequenceWindow,
  }: {
    groups: Array<Record<string, unknown>>;
    mode: 'live' | 'archive';
    label: string;
    sequenceItems?: Array<Record<string, unknown>>;
    sequenceWindow?: CodexChatScrollSequenceWindow;
  }) {
    const sequenceMarkers = buildCodexChatScrollSequenceMarkers({ groups, items: sequenceItems, window: sequenceWindow });
    const tracks: Array<{ id: CodexChatScrollTrackId; label: string; shortLabel: string }> = [
      { id: 'edit', label: 'edits', shortLabel: 'E' },
      { id: 'thread', label: 'thread', shortLabel: 'T' },
      { id: 'work', label: 'work', shortLabel: 'W' },
    ];
    return (
      <div
        aria-label={`${label} timeline scroll`}
        aria-valuemax={100}
        aria-valuemin={0}
        aria-valuenow={Math.round(chatTimelineScrollRatio * 100)}
        aria-valuetext={`${Math.round(chatTimelineScrollRatio * 100)} percent`}
        className="ion-codex-chat-scroll-timeline-v2"
        onKeyDown={(event) => handleVerticalChatTimelineKeyDown(mode, event)}
        onPointerCancel={handleVerticalChatTimelinePointerEnd}
        onPointerDown={(event) => handleVerticalChatTimelinePointerDown(mode, event)}
        onPointerMove={(event) => handleVerticalChatTimelinePointerMove(mode, event)}
        onPointerUp={handleVerticalChatTimelinePointerEnd}
        role="slider"
        tabIndex={0}
        title="Drag the V2 timeline rail to scroll the chat"
      >
        <div className="ion-codex-chat-scroll-v2-labels" aria-hidden="true">
          {tracks.map((track) => <span className={`is-${track.id}`} key={track.id}>{track.shortLabel}</span>)}
        </div>
        <div className="ion-codex-chat-scroll-lanes-v2" aria-hidden="true">
          {tracks.map((track) => {
            const trackSequenceMarkers = sequenceMarkers.filter((marker) => marker.scrollTrack === track.id);
            return (
              <div className={`ion-codex-chat-scroll-track-v2 is-${track.id}`} key={track.id} title={track.label}>
                {trackSequenceMarkers.map((marker) => (
                  <span
                    className={`ion-codex-chat-scroll-marker-v2 is-sequence is-${marker.tone}`}
                    key={marker.id}
                    style={{ top: `${marker.top}%` } as CSSProperties}
                    title={marker.detail}
                  />
                ))}
              </div>
            );
          })}
        </div>
        <div className="ion-codex-chat-scroll-v2-redline" style={{ top: `${chatTimelineScrollRatio * 100}%` }} />
        <div className="ion-codex-chat-scroll-v2-thumb" style={{ top: `${chatTimelineScrollRatio * 100}%` }}>
          <span />
        </div>
      </div>
    );
  }

  function renderChatTimelineV3({
    groups,
    mode,
    label,
    windowLabel,
  }: {
    groups: Array<Record<string, unknown>>;
    mode: 'live' | 'archive';
    label: string;
    windowLabel: string;
  }) {
    const model = buildCodexChatTimelineModel(groups);
    const tracks: Array<{ id: CodexChatTimelineTrackId; label: string; detail: string }> = [
      { id: 'diff', label: 'DIFF', detail: 'green + / red -' },
      { id: 'chat', label: 'CHAT', detail: 'user + assistant' },
      { id: 'context', label: 'CONTEXT', detail: 'capsules + refs' },
      { id: 'reads', label: 'READS', detail: 'files + refs' },
      { id: 'tools', label: 'TOOLS', detail: 'tool calls' },
      { id: 'agents', label: 'AGENTS', detail: 'spawn + roles' },
      { id: 'queue', label: 'QUEUE', detail: 'runs + queue' },
    ];
    return (
      <section className={`ion-codex-chat-timeline-v3 is-${mode}`} aria-label="Codex chat timeline overview">
        <header className="ion-codex-chat-timeline-v3-head">
          <div>
            <span>chat timeline v3</span>
            <b>{label}</b>
            <code>{windowLabel}</code>
          </div>
          <div className="ion-codex-chat-timeline-v3-metrics">
            <span>{model.summary.turnCount} turns</span>
            <span>{model.summary.diffCount} diffs</span>
            <span>{model.summary.toolCount} tools</span>
            <span>{model.summary.readCount} reads</span>
            <span>{model.summary.agentCount} agents</span>
          </div>
        </header>
        <div className="ion-codex-chat-timeline-v3-ruler" style={{ gridTemplateColumns: `repeat(${model.frames}, minmax(0, 1fr))` }}>
          {Array.from({ length: 12 }, (_, index) => (
            <span key={`chat-v3-ruler-${index}`} style={{ gridColumn: `${Math.max(1, Math.round((index * model.frames) / 12) + 1)} / span 1` }}>{index + 1}</span>
          ))}
        </div>
        <div className="ion-codex-chat-timeline-v3-tracks">
          {tracks.map((track) => {
            const clips = model.clips.filter((clip) => clip.track === track.id);
            return (
              <section className={`ion-codex-chat-timeline-v3-track is-${track.id}`} key={track.id}>
                <header>
                  <b>{track.label}</b>
                  <span>{track.detail}</span>
                </header>
                <div className="ion-codex-chat-timeline-v3-lane" style={{ gridTemplateColumns: `repeat(${model.frames}, minmax(0, 1fr))` }}>
                  {clips.map((clip) => (
                    <button
                      className={`ion-codex-chat-timeline-v3-clip is-${clip.tone} is-texture-${clip.texture}`}
                      key={clip.id}
                      onClick={() => scrollChatTimelineTarget(mode, clip.targetIndex)}
                      style={{ gridColumn: `${clip.start} / span ${clip.span}` }}
                      title={`${clip.label}: ${clip.value}. ${clip.detail}`}
                      type="button"
                    >
                      <b>{clip.label}</b>
                      <span>{clip.value}</span>
                    </button>
                  ))}
                </div>
              </section>
            );
          })}
        </div>
      </section>
    );
  }

  function renderLiveTranscript() {
    return (
      <section className="ion-codex-transcript-frame is-live">
        <div className="ion-codex-transcript is-live" onScroll={handleLiveTranscriptScroll} ref={transcriptRef}>
          {liveTranscriptGroups.map((group, index) => (
            <TurnGroup
              key={text(group.group_id, `turn-${index}`)}
              group={group}
              latestAssistantKey={latestAssistantKey}
              onBranch={branchMessage}
              onCopy={copyMessageText}
              onPin={pinMessageText}
              onQuote={quoteMessageText}
              onRun={runMessageText}
              turnIndex={index}
            />
          ))}
          {liveTranscriptGroups.length === 0 && <div className="ion-empty-state">NO CODEX CHAT TURNS</div>}
        </div>
        {renderVerticalChatTimelineScrollbar({
          groups: liveTranscriptGroups,
          mode: 'live',
          label: CODEX_CURRENT_SESSION_TITLE,
        })}
      </section>
    );
  }

  function renderSelectedArchiveChat() {
    const excerptItems = records(selectedExcerpt?.items);
    const title = selectedSession ? chatTitleForSession(selectedSession) : text(selectedExcerpt?.session_id || selectedSessionId, 'Past chat');
    const selectedCodexId = selectedArchiveSessionId;
    const archiveTurnGroups = archiveConversationTurnGroups(excerptItems);
    const displayedCount = numberValue(selectedExcerpt?.displayed_item_count ?? selectedExcerpt?.item_count ?? excerptItems.length);
    const totalDisplayable = numberValue(selectedExcerpt?.total_displayable_items ?? displayedCount);
    const omittedOlder = numberValue(selectedExcerpt?.omitted_older_items);
    const omittedNewer = numberValue(selectedExcerpt?.omitted_newer_items);
    const oldestIndex = numberValue(selectedExcerpt?.oldest_item_index);
    const newestIndex = numberValue(selectedExcerpt?.newest_item_index);
    const hasOlder = Boolean(selectedExcerpt?.has_older_items) || oldestIndex > 1;
    const hasNewer = Boolean(selectedExcerpt?.has_newer_items) || (newestIndex > 0 && newestIndex < totalDisplayable);
    const transcriptWindow = omittedOlder > 0 || omittedNewer > 0
      ? `items ${oldestIndex || 0}-${newestIndex || 0} of ${totalDisplayable} safe items`
      : `${displayedCount} safe items`;
    const archiveVirtual = archiveVirtualMetrics(selectedExcerpt);
    const bufferStatus = archiveBufferStatus(archivePrefetch, archivePrefetchBusy, selectedCodexId);
    const scrollStatus = [transcriptWindow, archiveVirtual.enabled ? 'stable virtual scroll' : '', archiveBackgroundBusy ? 'background hydrate' : '', bufferStatus].filter(Boolean).join(' / ');
    const archiveTranscriptKey = [
      'archive-transcript',
      selectedCodexId || 'none',
    ].join(':');
    const archiveLatestAssistantKey = latestAssistantTurnKey(archiveTurnGroups);
    const archiveSessionId = selectedSession?.session_id || text(selectedExcerpt?.session_id || selectedSessionId, '');
    const branchArchiveMessage = (source: BranchSource) => branchMessage({
      ...source,
      kind: 'archive_session',
      title: `Branch: ${title}`,
      objective: text(source.objective || source.message, ''),
      sessionId: archiveSessionId,
    });
    const pinArchiveMessage = (message: unknown, sourceTurnId?: unknown) => (
      pinMessageText(message, `archive:${archiveSessionId}:${text(sourceTurnId, 'turn')}`)
    );
    return (
      <section className="ion-codex-selected-chat">
        <section className="ion-codex-transcript-frame is-archive">
          <div className={`ion-codex-transcript is-archive${archiveVirtual.enabled ? ' is-virtual' : ''}`} key={archiveTranscriptKey} onScroll={handleArchiveScroll} ref={archiveTranscriptRef}>
            <div className="ion-codex-scroll-popover">
              <span>{scrollStatus}</span>
              <small>{hasOlder ? 'scroll up for older' : 'oldest loaded'} / {hasNewer ? 'scroll down for newer' : 'newest loaded'}</small>
            </div>
            {archiveVirtual.enabled ? (
              <div className="ion-codex-archive-virtual-space" style={{ height: `${archiveVirtual.height}px` }}>
                <div className="ion-codex-archive-window" style={{ transform: `translateY(${archiveVirtual.topOffset}px)` }}>
                  {archiveTurnGroups.map((group, index) => (
                    <TurnGroup
                      group={group}
                      key={`${archiveTranscriptKey}:${text(group.group_id, `archive-turn-${index}`)}`}
                      latestAssistantKey={archiveLatestAssistantKey}
                      onBranch={branchArchiveMessage}
                      onCopy={copyMessageText}
                      onPin={pinArchiveMessage}
                      onQuote={quoteMessageText}
                      onRun={runMessageText}
                      turnIndex={index}
                    />
                  ))}
                  {archiveBusy && <div className="ion-empty-state">LOADING PAST CHAT</div>}
                  {!archiveBusy && archiveTurnGroups.length === 0 && <div className="ion-empty-state">NO SAFE EXCERPT ITEMS FOR THIS CHAT</div>}
                </div>
              </div>
            ) : (
              <>
                {archiveTurnGroups.map((group, index) => (
                  <TurnGroup
                    group={group}
                    key={`${archiveTranscriptKey}:${text(group.group_id, `archive-turn-${index}`)}`}
                    latestAssistantKey={archiveLatestAssistantKey}
                    onBranch={branchArchiveMessage}
                    onCopy={copyMessageText}
                    onPin={pinArchiveMessage}
                    onQuote={quoteMessageText}
                    onRun={runMessageText}
                    turnIndex={index}
                  />
                ))}
                {archiveBusy && <div className="ion-empty-state">LOADING PAST CHAT</div>}
                {!archiveBusy && archiveTurnGroups.length === 0 && <div className="ion-empty-state">NO SAFE EXCERPT ITEMS FOR THIS CHAT</div>}
              </>
            )}
          </div>
          {renderVerticalChatTimelineScrollbar({
            groups: archiveTurnGroups,
            mode: 'archive',
            label: title,
            sequenceItems: excerptItems,
            sequenceWindow: {
              total: totalDisplayable,
              oldest: oldestIndex,
              newest: newestIndex,
            },
          })}
        </section>
      </section>
    );
  }

  async function copyMessageText(value: unknown) {
    const message = text(value, '');
    if (!message) return;
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(message);
      setActionNotice('Copied message');
    } else {
      setActionNotice('Copy unavailable');
    }
  }

  function quoteMessageText(value: unknown) {
    const message = text(value, '');
    if (!message) return;
    setComposer((previous) => `${previous.trim() ? `${previous.trim()}\n\n` : ''}> ${message.replace(/\n/g, '\n> ')}\n\n`);
    setChatViewMode('live');
    setLeftDrawer('compose');
    setLeftDrawerOpen(true);
  }

  function runMessageText(value: unknown) {
    const message = text(value, '');
    if (!message) return;
    setExecutionMode('queue_for_codex');
    setComposer(`Run this as bounded Codex work:\n\n${message}`);
    setChatViewMode('live');
    setLeftDrawer('compose');
    setLeftDrawerOpen(true);
  }

  async function pinMessageText(value: unknown, sourceTurnId?: unknown) {
    const message = text(value, '');
    if (!message) return;
    setActionNotice('Pinning...');
    try {
      const response = await fetch(chatApiPath('/memory'), {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(withPublicToken({
          lane_id: 'codex_general',
          text: message,
          source_turn_id: text(sourceTurnId, ''),
          confirmation: WRITE_CONFIRMATION_TOKEN,
        })),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok === false) {
        throw new Error(text(payload.finding || payload.error, `pin_http_${response.status}`));
      }
      setActionNotice('Pinned to Codex memory');
      await Promise.resolve(onRuntimeRefresh?.());
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : 'pin_failed');
    }
  }

  function useCommandTemplate(template: string, mode: ExecutionModeId = 'auto') {
    setExecutionMode(mode);
    setComposer(template);
    setChatViewMode('live');
    setActiveCodexTab('chat');
    setLeftDrawer('compose');
    setLeftDrawerOpen(true);
  }

  function renderIdePane() {
    const responseCarrier = record(chat?.response_carrier);
    return (
      <section className="ion-codex-ide-pane">
        <div className="ion-codex-ide-column">
          <div className="ion-codex-ide-section-head"><span>ACTIVE CONTEXT</span><b>{contextSurfaces.length + archiveAttachments.length}</b></div>
          <DataBlock title="workspace" rows={[
            ['root', cli?.shell_root],
            ['content', cli?.content_root],
            ['route ok', project.route_ok],
            ['attached chats', archiveAttachments.length],
          ]} />
          <RecordPanel title="context files" records={contextSurfaces.slice(0, 10)} />
          <RecordPanel title="attached chats" records={archiveAttachments} />
        </div>

        <div className="ion-codex-ide-column">
          <div className="ion-codex-ide-section-head"><span>COMMAND DECK</span><b>templates</b></div>
          <div className="ion-codex-command-grid">
            <CommandButton label="Answer With Context" onClick={() => useCommandTemplate('Answer using active context and any attached past chats.')} />
            <CommandButton label="Review Current State" onClick={() => useCommandTemplate('Review the current Codex cockpit state, attached chats, queue, and context. Lead with issues and concrete next actions.')} />
            <CommandButton label="Run Implementation" onClick={() => useCommandTemplate('Implement the requested change as bounded Codex work. Use active context and attached past chats as witness material. Return proof and tests.', 'queue_for_codex')} />
            <CommandButton label="Proof Repair" onClick={() => useCommandTemplate('Perform a proof-repair pass for the current Codex/ION work. Verify context refs, tests, receipts, and missing evidence.', 'queue_for_codex')} />
            <CommandButton label="Explain Tools" onClick={() => useCommandTemplate('Explain which Codex CLI tools, hooks, skills, and MCP surfaces are active in this cockpit state.')} />
            <CommandButton label="Plan IDE Upgrade" onClick={() => useCommandTemplate('Plan the next Codex IDE cockpit upgrade with implementation steps, boundaries, and verification.')} />
          </div>
          <JsonPanel title="execution bridge" value={chat?.execution_bridge} />
          <JsonPanel title="response carrier" value={responseCarrier} />
        </div>

        <div className="ion-codex-ide-column">
          <div className="ion-codex-ide-section-head"><span>RUN + TOOL INSPECTOR</span><b>{text(queue.verdict)}</b></div>
          <RecordPanel title="work requests" records={records(chat?.latest_work_requests)} />
          <RecordPanel title="response runs" records={records(chat?.latest_response_runs)} />
          <RecordPanel title="turn traces" records={records(record(chat?.turn_traces).records).slice(0, 12)} />
          <RecordPanel title="mcp read-only tools" records={records(tools.mcp_read_only_tools).slice(0, 16)} />
        </div>
      </section>
    );
  }

  function renderArchivePane() {
    const excerpt = archive?.selected_session_excerpt;
    const selectedCodexId = text(selectedSession?.session_id || excerpt?.session_id || selectedSessionId, '');
    const selectedIsCurrent = Boolean(selectedSession?.is_current_session || excerpt?.is_current_session || (currentArchiveSessionId && selectedCodexId === currentArchiveSessionId));
    const displayedCount = numberValue(excerpt?.displayed_item_count ?? excerpt?.item_count ?? records(excerpt?.items).length);
    const totalDisplayable = numberValue(excerpt?.total_displayable_items ?? displayedCount);
    const omittedOlder = numberValue(excerpt?.omitted_older_items);
    return (
      <section className="ion-codex-archive-pane">
        <div className="ion-codex-archive-library">
          {archiveSessionGroups.filter((group) => group.sessions.length > 0).map((group) => (
            <section className="ion-codex-session-section" key={group.id}>
              <div className="ion-codex-session-section-head">
                <span>{group.title}</span>
                <b>{group.sessions.length}</b>
              </div>
              <div className="ion-codex-session-stack">
                {group.sessions.map((session) => (
                  <SessionButton
                    active={selectedSessionId === session.session_id}
                    key={session.session_id}
                    onOpen={() => openSession(session)}
                    session={session}
                    title={chatTitleForSession(session)}
                  />
                ))}
              </div>
            </section>
          ))}
          {archiveSessionGroups.every((group) => group.sessions.length === 0) && (
            <div className="ion-empty-state">{archiveView === 'packets' ? 'NO MATCHING WORK PACKETS' : 'NO MATCHING CHATS'}</div>
          )}
        </div>
        <div className="ion-codex-archive-excerpt">
          <div className="ion-codex-selected-head">
            <div>
              <span>{selectedIsCurrent ? 'CURRENT CODEX CLI CHAT' : 'SELECTED CODEX CLI CHAT'}</span>
              <b>{archiveBusy ? 'Loading...' : text(selectedSession ? chatTitleForSession(selectedSession) : excerpt?.session_id || selectedSessionId, 'No chat selected')}</b>
              <code>codex session id: {selectedCodexId || 'unknown'}</code>
              <code>cwd: {text(selectedSession?.cwd || 'unknown')}</code>
            </div>
            {selectedSession ? (
              <div className="ion-codex-selected-actions">
                <button onClick={() => openSession(selectedSession)} type="button">REFRESH</button>
                <button onClick={() => copyMessageText(selectedSession.session_id)} type="button">COPY ID</button>
                <button onClick={() => continueSessionInComposer(selectedSession)} type="button">CONTINUE</button>
                <button onClick={() => attachSession(selectedSession)} type="button">ATTACH</button>
                <button onClick={() => openSession(selectedSession, { activateArchive: false, showInChat: true })} type="button">OPEN IN CHAT</button>
                <button onClick={() => branchSession(selectedSession)} type="button">BRANCH</button>
                <button onClick={() => copySessionCommand(selectedSession, 'resume')} type="button">RESUME CMD</button>
                <button onClick={() => copySessionCommand(selectedSession, 'fork')} type="button">FORK CMD</button>
                <button onClick={() => referenceSession(selectedSession)} type="button">REFERENCE</button>
              </div>
            ) : null}
          </div>
          <div className="ion-queue-gateway-strip compact">
            <span>SAFE TRANSCRIPT: {excerpt?.safe_transcript_exported ? `${displayedCount}/${totalDisplayable} ITEMS` : 'SELECT CHAT'}</span>
            {omittedOlder > 0 ? <span>OLDER OMITTED: {omittedOlder}</span> : null}
            <span>RAW: {excerpt?.raw_transcript_exported ? 'EXPORTED' : 'REDACTED'}</span>
            <span>SECRETS: {archive?.secrets_authority ? 'AUTHORIZED' : 'REDACTED'}</span>
            <span>ACTIVITY: {selectedSession ? sessionActivity(selectedSession) : 0}</span>
          </div>
          {selectedSession ? (
            <div className="ion-codex-selected-metadata">
              {selectedIsCurrent ? <span>CURRENT</span> : null}
              <span>{sessionShortId(selectedSession)}</span>
              <span>CODEX ID {selectedSession.session_id}</span>
              <span>{formatSessionTime(selectedSession)}</span>
              <span>{text(selectedSession.model, 'model unknown')}</span>
              <span>{text(selectedSession.history_prompt_count, 0)} prompts</span>
              <span>{text(selectedSession.line_count_sampled, 0)} events</span>
            </div>
          ) : null}
          <div className="ion-codex-session-preview-text">
            {archiveAction || (selectedSession ? text(selectedSession.latest_user_snippet || selectedSession.first_user_snippet, 'No prompt snippet available') : 'Pick a chat from Recent, Most Active, Projects, Models, or Work Packets.')}
          </div>
          <div className="ion-codex-excerpt-stack">
            {records(excerpt?.items).map((item, index) => (
              <article className={`ion-codex-message is-${safeClass(item.role)}`} key={`${text(item.timestamp)}-${index}`}>
                <div><span>{text(item.role)}</span><time>{text(item.timestamp, '')}</time></div>
                <p>{text(item.text || item.snippet, '')}</p>
              </article>
            ))}
            {!excerpt && <div className="ion-empty-state">SELECT A SESSION</div>}
          </div>
        </div>
      </section>
    );
  }

  function referenceSession(session: IonCodexConversationArchiveSession) {
    const snippet = text(session.latest_user_snippet || session.first_user_snippet, '');
    setComposer([
      `Reference past Codex chat ${session.session_id}.`,
      `Title: ${chatTitleForSession(session)}`,
      `Updated: ${formatSessionTime(session)}`,
      `Project: ${projectLabel(session)}`,
      snippet ? `Relevant snippet: ${snippet}` : '',
      '',
    ].filter(Boolean).join('\n'));
    setActiveCodexTab('chat');
    setLeftDrawer('compose');
    setLeftDrawerOpen(true);
  }

  function renderContextPane() {
    const surfaces = contextTimelineSurfaces.length ? contextTimelineSurfaces : contextSurfaces;
    const activeSurfaceId = surfaces.some((surface) => text(surface.surface_id, '') === contextSurfaceId)
      ? contextSurfaceId
      : text(surfaces[0]?.surface_id, 'context-floor');
    const activeSurface = surfaces.find((surface) => text(surface.surface_id, '') === activeSurfaceId) ?? {};
    const activeLane = contextTimelineLanes.find((lane) => text(lane.surface_id, '') === activeSurfaceId) ?? {};
    const surfaceEvents = contextTimelineEvents.filter((event) => Boolean(surfaceChangeForEvent(event, activeSurfaceId)));
    const selectedEvent = contextTimelineEvents.find((event) => text(event.event_id, '') === contextEventId)
      ?? surfaceEvents[0]
      ?? contextTimelineEvents[0]
      ?? {};
    const selectedChange = surfaceChangeForEvent(selectedEvent, activeSurfaceId) ?? records(selectedEvent.surface_changes)[0] ?? {};
    const diffExcerpt = text(selectedChange.diff_excerpt, '');
    const routeEntries = records(contextTopology.route_entries);
    const packageRows = records(contextTopology.packages);
    const selectedPackages = stringList(contextTopology.selected_packages);
    const contextAgentAudit = record(contextAgentDiagnostics.agent_context_system_audit);
    const contextAgentReadyCount = Boolean(contextAgentAudit.accepted)
      ? contextAgentRows.length
      : contextAgentRows.filter((agent) => {
        const proof = record(record(agent.agent_page_evidence).proof);
        return Boolean(proof.critical_ready) || text(agent.context_system_status, '') === 'ready';
      }).length;
    const activeContextAgentId = text(selectedContextAgentId || agentIdentity.roleId, '');
    const selectedContextAgent = contextAgentRows.find((agent) => agentRecordId(agent) === activeContextAgentId)
      ?? findAgentIdentityRecord(contextAgentRows, activeContextAgentId)
      ?? findAgentIdentityRecord(contextAgentRows, agentIdentity.roleId)
      ?? contextAgentRows[0]
      ?? {};
    const selectedAgentId = agentRecordId(selectedContextAgent);
    const selectedAgentEvidence = record(selectedContextAgent.agent_page_evidence);
    const selectedAgentIdentity = record(selectedAgentEvidence.identity);
    const selectedAgentAuthority = record(selectedAgentEvidence.authority);
    const selectedAgentContextSystem = record(selectedAgentEvidence.context_system);
    const selectedAgentContextCard = record(selectedAgentContextSystem.card);
    const selectedAgentProof = record(selectedAgentEvidence.proof);
    const selectedAgentProofChecks = records(selectedAgentProof.checks);
    const selectedAgentCodexMount = record(selectedAgentEvidence.codex_mount);
    const selectedAgentMount = record(selectedContextAgent.native_codex_mount);
    const selectedAgentCapsule = record(selectedAgentEvidence.capsule);
    const selectedAgentAddressBook = record(selectedAgentEvidence.address_book);
    const selectedAgentAddressSummary = record(selectedAgentAddressBook.summary);
    const selectedAgentContactGroups = record(selectedAgentAddressBook.contact_groups);
    const selectedAgentMountFiles = records(selectedAgentCodexMount.files);
    const selectedAgentCapsuleFiles = records(selectedAgentCapsule.files);
    const selectedAgentContextPaths = records(selectedAgentContextSystem.context_paths);
    const selectedAgentPackageProbe = rowByLabel(selectedAgentMountFiles, 'active_context_package_md');
    const selectedAgentPortablePackageProbe = rowByLabel(selectedAgentCapsuleFiles, 'active_context_package_md');
    const selectedAgentPackageExcerpt = text(selectedAgentPackageProbe.excerpt || selectedAgentPortablePackageProbe.excerpt, 'No active context package excerpt available');
    const selectedAgentContextExcerpt = text(selectedAgentContextCard.excerpt, 'No context system card excerpt available');
    const selectedAgentReadZones = uniqueStrings([
      ...stringList(selectedAgentContextSystem.read_zones),
      ...stringList(selectedContextAgent.default_read_zones),
    ]).slice(0, 12);
    const selectedAgentProofObligations = uniqueStrings([
      ...stringList(selectedAgentContextSystem.proof_obligations),
      ...stringList(selectedContextAgent.default_proof_obligations),
    ]).slice(0, 12);
    const selectedAgentTemplates = uniqueStrings([
      ...stringList(selectedAgentContextSystem.primary_templates),
      ...stringList(selectedContextAgent.primary_templates),
    ]).slice(0, 12);
    const selectedAgentContactRows = Object.entries(selectedAgentContactGroups)
      .map(([label, value]) => ({ label, contacts: stringList(value).slice(0, 6) }))
      .filter((row) => row.contacts.length);
    const selectedAgentKind = text(selectedAgentIdentity.agent_kind || selectedContextAgent.context_system_status || selectedContextAgent.backend_carrier_id, 'context_system_agent');
    const selectedAgentReady = Boolean(selectedAgentProof.critical_ready);
    const activeTabSession = sessionFromOpenChatTab(activeChatTab) ?? selectedSession;
    const activeTabSessionId = text(activeTabSession?.session_id || activeChatTab?.sessionId, '');
    const activeTabTitle = activeChatTab
      ? chatTitleForSessionId(activeChatTab.sessionId, activeChatTab.title)
      : 'No remembered chat tab selected';
    const activeTabMissionLabels = records(activeTabSession?.mission_labels).slice(0, 4);
    const activeTabAgentLabels = records(activeTabSession?.agent_labels).slice(0, 4);
    const chatContext = record(chat?.chat_context);
    const activeTabContextBinding = record(record(activeTabSession).chat_context_binding);
    const activeChatContextBinding = Object.keys(activeTabContextBinding).length
      ? activeTabContextBinding
      : activeChatTab ? {} : record(chatContext.active_binding);
    const activeChatAgentIdentity = record(activeChatContextBinding.agent_identity);
    const activeChatMinimumContext = record(activeChatContextBinding.minimum_context);
    const activeChatAgentLookup = text(
      activeChatAgentIdentity.role_id
      || activeChatContextBinding.role_id
      || activeTabAgentLabels[0]?.role_id
      || activeTabAgentLabels[0]?.agent_id
      || activeTabAgentLabels[0]?.label,
      '',
    );
    const activeChatContextAgent = activeChatAgentLookup ? findAgentIdentityRecord(contextAgentRows, activeChatAgentLookup) ?? {} : {};
    const activeChatContextAgentId = agentRecordId(activeChatContextAgent);
    const activeChatAgentAvailable = Boolean(activeChatContextAgentId);
    const activeChatAgentDisplay = text(
      activeChatAgentIdentity.agent_true_name
      || activeChatAgentIdentity.agent_instance_id
      || activeChatContextAgent.display_name
      || activeChatContextAgent.role_id
      || activeTabAgentLabels[0]?.label
      || activeChatContextBinding.role_id,
      'agent unavailable',
    );
    const activeChatDomain = text(
      activeChatContextBinding.domain_id
      || activeTabMissionLabels[0]?.label
      || activeChatContextAgent.registry_primary_domain
      || activeChatContextAgent.role_domain_label,
      'domain unknown',
    );
    const activeChatBranch = text(activeChatContextBinding.branch_title || activeChatContextBinding.branch_id || activeTabSessionId, 'branch unknown');
    const activeChatBindingId = text(activeChatAgentIdentity.agent_instance_id || activeChatContextBinding.binding_id, 'binding pending');
    const activeChatFloorRefs = records(activeChatContextBinding.context_floor_refs).slice(0, 6);
    const activeChatMountedRefs = records(activeChatContextBinding.mounted_context_refs).slice(0, 6);
    const activeChatAttachedRefs = records(activeChatContextBinding.attached_archive_refs).slice(0, 6);
    const activeChatSiblingBindingIds = stringList(activeChatContextBinding.same_domain_sibling_binding_ids).slice(0, 6);
    const activeChatAuthorityRows = [
      ['context floor', text(activeChatMinimumContext.capsule_ref, 'minimum floor required')],
      ['mini', text(activeChatMinimumContext.mini_ref, 'lookup witness only')],
      ['role archetype', text(activeChatAgentIdentity.clone_of_role_id || activeChatContextBinding.role_id, 'role pending')],
      ['agent instance', text(activeChatAgentIdentity.agent_instance_id, 'instance pending')],
      ['archives', activeChatAttachedRefs.length ? 'explicit attachments only' : 'not attached'],
      ['siblings', activeChatSiblingBindingIds.length ? 'same-domain awareness only' : 'none linked'],
      ['shared raw context', 'disabled'],
    ];
    const renderProbeRows = (rows: Array<Record<string, unknown>>, limit = 8) => (
      <div className="ion-codex-context-probe-grid">
        {rows.slice(0, limit).map((row, index) => (
          <div className={`ion-codex-context-probe${row.exists ? ' is-ok' : ' is-missing'}`} key={`${text(row.label || row.path || row.relpath, 'probe')}-${index}`}>
            <span>{text(row.label || row.kind, `ref ${index + 1}`)}</span>
            <b>{row.exists ? 'ok' : 'missing'}</b>
            <code>{text(row.relpath || row.path, '')}</code>
          </div>
        ))}
        {rows.length === 0 ? <div className="ion-empty-state">NO REFS</div> : null}
      </div>
    );

    return (
      <section className="ion-codex-context-workbench">
        <header className="ion-codex-context-overview">
          <div className="ion-codex-context-title">
            <span>codex context</span>
            <b>{text(contextTimeline.verdict, 'context timeline unavailable')}</b>
            <code>{text(contextTimeline.context_root || record(cliContext.active_context).minimum_context_path || chat?.capsule?.path, '')}</code>
          </div>
          <div className="ion-codex-context-metrics">
            <Metric label="surfaces" value={contextTimelineSummary.surface_count ?? surfaces.length} />
            <Metric label="checkpoints" value={contextTimelineSummary.history_snapshot_count ?? 0} />
            <Metric label="diff events" value={contextTimelineSummary.diff_event_count ?? 0} />
            <Metric label="boundaries" value={contextTimelineSummary.boundary_event_count ?? contextBoundaries.length} />
            <Metric label="route refs" value={contextTimelineSummary.route_entry_count ?? contextTopology.route_entry_count ?? 0} />
            <Metric label="packages" value={contextTimelineSummary.context_package_count ?? contextTopology.package_count ?? 0} />
            <Metric label="agents" value={contextAgentSummary.agent_count ?? contextAgentRows.length} />
            <Metric label="context sys" value={contextAgentReadyCount} />
          </div>
        </header>

        <article className={`ion-codex-current-chat-context${activeChatTab ? ' has-chat-tab' : ' is-empty'}`}>
          <header>
            <div>
              <span>current chat tab context</span>
              <b>{activeTabTitle}</b>
              <code>{activeTabSessionId || 'open a remembered chat tab'}</code>
            </div>
            <button disabled={!activeChatAgentAvailable} onClick={() => setSelectedContextAgentId(activeChatContextAgentId)} type="button">
              {activeChatAgentAvailable ? 'SHOW TAB AGENT' : 'AGENT UNMAPPED'}
            </button>
          </header>
          <div className="ion-codex-current-chat-context-metrics">
            <ContextPill label="domain" value={activeChatDomain} />
            <ContextPill label="agent" value={activeChatAgentDisplay} />
            <ContextPill label="branch" value={activeChatBranch} />
            <ContextPill label="binding" value={activeChatBindingId} />
            <ContextPill label="siblings" value={activeChatSiblingBindingIds.length} />
          </div>
          <div className="ion-codex-current-chat-context-grid">
            <div>
              <span>authority model</span>
              {activeChatAuthorityRows.map(([label, value]) => (
                <p key={label}><b>{label}</b><em>{value}</em></p>
              ))}
            </div>
            <div>
              <span>floor refs</span>
              {activeChatFloorRefs.length ? activeChatFloorRefs.map((ref, index) => (
                <code key={`${text(ref.label || ref.path || ref.relpath, 'floor')}-${index}`}>{text(ref.label || ref.path || ref.relpath, 'context floor')}</code>
              )) : <small>Context floor refs pending for this tab.</small>}
            </div>
            <div>
              <span>mounted refs</span>
              {activeChatMountedRefs.length ? activeChatMountedRefs.map((ref, index) => (
                <code key={`${text(ref.label || ref.path || ref.relpath, 'mounted')}-${index}`}>{text(ref.label || ref.path || ref.relpath, 'mounted context')}</code>
              )) : <small>No selected mounted context refs recorded for this tab.</small>}
            </div>
            <div>
              <span>attached archives</span>
              {activeChatAttachedRefs.length ? activeChatAttachedRefs.map((ref, index) => (
                <code key={`${text(ref.session_id || ref.label || ref.path, 'archive')}-${index}`}>{sessionShortText(text(ref.session_id || ref.label || ref.path, 'attached archive'))}</code>
              )) : <small>No historical chats attached as context.</small>}
            </div>
          </div>
          </article>

          {renderContextSystemChatMap()}

          <div className="ion-codex-context-surface-rail" aria-label="Codex context surfaces">
          {surfaces.map((surface) => {
            const surfaceId = text(surface.surface_id, '');
            const lane = contextTimelineLanes.find((item) => text(item.surface_id, '') === surfaceId) ?? {};
            return (
              <button
                className={surfaceId === activeSurfaceId ? 'is-active' : undefined}
                key={surfaceId || text(surface.path, 'surface')}
                onClick={() => { setContextSurfaceId(surfaceId); setContextEventId(''); }}
                type="button"
              >
                <span>{text(surface.label || surface.surface_id, 'surface')}</span>
                <b>{text(surface.lane || lane.lane || surface.role, 'context')}</b>
                <small>{text(surface.path, '')}</small>
                <em>{text(lane.change_count ?? 0)} diffs</em>
              </button>
            );
          })}
        </div>

        <div className="ion-codex-context-agent-console">
          <aside className="ion-codex-context-agent-roster" aria-label="Agent context systems">
            <div className="ion-codex-context-panel-head">
              <span>agent context systems</span>
              <b>{contextAgentRows.length}</b>
            </div>
            <label className="ion-codex-context-agent-select">
              <span>selected agent</span>
              <select
                aria-label="Select agent context system"
                disabled={!contextAgentRows.length}
                onChange={(event) => setSelectedContextAgentId(event.currentTarget.value)}
                value={selectedAgentId}
              >
                {contextAgentRows.map((agent) => {
                  const agentId = agentRecordId(agent);
                  return (
                    <option key={agentId || text(agent.display_name, 'agent')} value={agentId}>
                      {text(agent.display_name || agent.role_id, 'agent')} / {text(agent.role_id || agent.agent_id, '')}
                    </option>
                  );
                })}
              </select>
            </label>
            <div className="ion-codex-context-agent-list">
              {contextAgentRows.map((agent) => {
                const agentId = agentRecordId(agent);
                const evidence = record(agent.agent_page_evidence);
                const identity = record(evidence.identity);
                const proof = record(evidence.proof);
                return (
                  <button
                    className={`${agentId === selectedAgentId ? 'is-active' : ''}${agentId === agentIdentity.roleId ? ' is-current-carrier' : ''}`}
                    key={agentId || text(agent.display_name, 'agent')}
                    onClick={() => setSelectedContextAgentId(agentId)}
                    type="button"
                  >
                    <span>{text(agent.display_name || agent.role_id, 'agent')}</span>
                    <b>{text(agent.role_id || agent.agent_id, '')}</b>
                    <small>{text(agent.registry_primary_domain || record(identity).domain_id || agent.role_domain_label, 'domain pending')}</small>
                    <em>{Boolean(proof.critical_ready) ? 'proven' : text(agent.context_system_status || agent.default_active_package_class, 'context')}</em>
                  </button>
                );
              })}
              {contextAgentRows.length === 0 ? <div className="ion-empty-state">NO AGENTS</div> : null}
            </div>
          </aside>

          <article className="ion-codex-context-agent-system">
            <header>
              <div>
                <span>{selectedAgentKind}</span>
                <b>{text(selectedContextAgent.display_name || selectedContextAgent.role_id, 'agent')}</b>
                <code>{text(selectedAgentContextCard.relpath || selectedAgentContextCard.path || selectedContextAgent.context_system_card, '')}</code>
              </div>
              <div className="ion-codex-context-agent-lenses" role="tablist" aria-label="Agent context lenses">
                {(['card', 'package', 'proof', 'files'] as CodexContextAgentLens[]).map((lens) => (
                  <button className={contextAgentLens === lens ? 'is-active' : undefined} key={lens} onClick={() => setContextAgentLens(lens)} type="button">
                    {lens}
                  </button>
                ))}
              </div>
            </header>
            <div className="ion-codex-context-agent-metrics">
              <ContextPill label="ready" value={selectedAgentReady ? 'yes' : 'no'} />
              <ContextPill label="ION" value={Boolean(selectedAgentIdentity.is_ion_context_system) ? 'yes' : 'no'} />
              <ContextPill label="local floor" value={Boolean(selectedAgentIdentity.is_capsule_agent) ? 'yes' : 'no'} />
              <ContextPill label="codex" value={Boolean(selectedAgentIdentity.is_codex_native_mount) ? 'yes' : 'no'} />
              <ContextPill label="package" value={Boolean(selectedAgentIdentity.is_portable_package_agent) ? 'yes' : 'no'} />
              <ContextPill label="contacts" value={selectedAgentAddressSummary.contact_count ?? 0} />
            </div>
            <div className={`ion-codex-context-agent-lens-body is-${contextAgentLens}`}>
              {contextAgentLens === 'card' ? (
                <>
                  <div className="ion-codex-context-agent-paths">
                    <PathChip label="role" value={selectedAgentId} />
                    <PathChip label="domain" value={selectedAgentIdentity.domain_id || selectedContextAgent.registry_primary_domain} />
                    <PathChip label="class" value={selectedAgentContextSystem.default_active_package_class || selectedContextAgent.default_active_package_class} />
                    <PathChip label="strategy" value={selectedAgentContextSystem.package_strategy || selectedContextAgent.package_strategy} />
                  </div>
                  <pre>{selectedAgentContextExcerpt}</pre>
                </>
              ) : null}
              {contextAgentLens === 'package' ? (
                <>
                  <div className="ion-codex-context-agent-paths">
                    <PathChip label="mount package" value={selectedAgentPackageProbe.relpath || selectedAgentMount.active_context_package_md_path} />
                    <PathChip label="portable package" value={selectedAgentPortablePackageProbe.relpath || selectedAgentMount.portable_active_context_package_md_path} />
                  </div>
                  <pre>{selectedAgentPackageExcerpt}</pre>
                </>
              ) : null}
              {contextAgentLens === 'proof' ? (
                <div className="ion-codex-context-agent-proof-grid">
                  <div>
                    <span>proof checks</span>
                    {selectedAgentProofChecks.slice(0, 10).map((check, index) => (
                      <code className={Boolean(check.ok) ? 'is-ok' : 'is-missing'} key={`${text(check.label, 'check')}-${index}`}>
                        {Boolean(check.ok) ? 'ok' : 'missing'} / {text(check.label, 'check')}
                      </code>
                    ))}
                  </div>
                  <div>
                    <span>read zones</span>
                    {selectedAgentReadZones.map((item) => <code key={item}>{item}</code>)}
                  </div>
                  <div>
                    <span>proof obligations</span>
                    {selectedAgentProofObligations.map((item) => <code key={item}>{item}</code>)}
                  </div>
                  <div>
                    <span>templates</span>
                    {selectedAgentTemplates.map((item) => <code key={item}>{item}</code>)}
                  </div>
                </div>
              ) : null}
              {contextAgentLens === 'files' ? (
                <div className="ion-codex-context-agent-files">
                  {renderProbeRows(selectedAgentContextPaths, 6)}
                  {renderProbeRows(selectedAgentMountFiles, 6)}
                  {renderProbeRows(selectedAgentCapsuleFiles, 8)}
                </div>
              ) : null}
            </div>
          </article>

          <aside className="ion-codex-context-agent-proof">
            <div className="ion-codex-context-panel-head">
              <span>phase weave</span>
              <b>{rolePhaseRows.length}</b>
            </div>
            <div className="ion-codex-context-phase-ladder">
              {rolePhaseRows.map((phase, index) => (
                <button
                  className={phase.toLowerCase().includes(text(selectedContextAgent.display_name || selectedContextAgent.role_id, '').toLowerCase().replace(/^role\./, '')) ? 'is-active' : undefined}
                  key={`${phase}-${index}`}
                  type="button"
                >
                  <span>{index + 1}</span>
                  <b>{phase.replaceAll('_', ' ')}</b>
                </button>
              ))}
            </div>
            <div className="ion-codex-context-authority-grid">
              <ContextPill label="production" value={Boolean(selectedAgentAuthority.production_authority) ? 'yes' : 'no'} />
              <ContextPill label="live exec" value={Boolean(selectedAgentAuthority.live_execution_authority) ? 'yes' : 'no'} />
              <ContextPill label="accepted" value={Boolean(selectedAgentAuthority.accepted_state_authority) ? 'yes' : 'no'} />
              <ContextPill label="write" value={selectedAgentAuthority.write_posture || selectedContextAgent.write_posture || 'none'} />
            </div>
            <div className="ion-codex-context-contact-groups">
              {selectedAgentContactRows.slice(0, 6).map((row) => (
                <div key={row.label}>
                  <span>{row.label}</span>
                  <code>{row.contacts.join(' / ')}</code>
                </div>
              ))}
              {selectedAgentContactRows.length === 0 ? <div className="ion-empty-state">NO CONTACT GROUPS</div> : null}
            </div>
          </aside>
        </div>

        <div className="ion-codex-context-main-grid">
          <aside className="ion-codex-context-timeline" aria-label="Context timeline">
            <div className="ion-codex-context-panel-head">
              <span>timeline</span>
              <b>{contextTimelineEvents.length}</b>
            </div>
            <div className="ion-codex-context-event-stack">
              {contextTimelineEvents.map((event) => {
                const eventId = text(event.event_id, text(event.checkpoint_id, 'event'));
                const changes = records(event.surface_changes);
                const activeChange = surfaceChangeForEvent(event, activeSurfaceId);
                return (
                  <button
                    className={`${eventId === text(selectedEvent.event_id, '') ? 'is-active' : ''}${activeChange ? ' has-surface-change' : ''}`}
                    key={eventId}
                    onClick={() => setContextEventId(eventId)}
                    type="button"
                  >
                    <span>{formatContextTime(event.created_at)}</span>
                    <b>{text(event.capsule_entry_id || event.checkpoint_id, 'checkpoint')}</b>
                    <small>{text(event.summary, 'context checkpoint')}</small>
                    <em>{changes.length ? `${changes.length} surfaces / +${text(event.added_lines, 0)} -${text(event.removed_lines, 0)}` : 'baseline'}</em>
                  </button>
                );
              })}
              {contextTimelineEvents.length === 0 && <div className="ion-empty-state">NO CONTEXT CHECKPOINTS FOUND</div>}
            </div>
          </aside>

          <article className="ion-codex-context-diff-console">
            <header>
              <div>
                <span>{text(activeSurface.label || activeSurface.surface_id, 'context surface')}</span>
                <b>{text(selectedEvent.capsule_entry_id || selectedEvent.checkpoint_id, 'current surface')}</b>
                <code>{text(activeSurface.path, '')}</code>
              </div>
              <div className="ion-codex-context-actions">
                <button onClick={() => copyMessageText(diffExcerpt || activeSurface.excerpt || selectedEvent.summary)} type="button">COPY</button>
                <button onClick={() => quoteMessageText(diffExcerpt || selectedEvent.summary || activeSurface.excerpt)} type="button">QUOTE</button>
              </div>
            </header>
            <div className="ion-codex-context-diff-stats">
              <ContextPill label="basis" value={selectedChange.basis || activeSurface.comparison_basis || 'text'} />
              <ContextPill label="added" value={`+${text(selectedChange.added_lines, 0)}`} />
              <ContextPill label="removed" value={`-${text(selectedChange.removed_lines, 0)}`} />
              <ContextPill label="line delta" value={selectedChange.line_delta ?? 0} />
              <ContextPill label="surface sha" value={text(activeSurface.sha256, '').slice(0, 12) || 'none'} />
            </div>
            {diffExcerpt ? (
              <pre className="ion-codex-diff-block is-context-timeline">
                {diffExcerpt.split('\n').map((line, index) => (
                  <span className={diffLineClass(line)} key={`${index}-${line.slice(0, 24)}`}>{line || ' '}</span>
                ))}
              </pre>
            ) : (
              <div className="ion-codex-context-empty-diff">
                <b>{text(selectedEvent.baseline, false) === 'true' ? 'baseline checkpoint' : 'no diff for selected surface'}</b>
                <span>{text(selectedEvent.summary || activeSurface.summary, 'Select another timeline event or surface to inspect context movement.')}</span>
              </div>
            )}
            <div className="ion-codex-context-current-surface">
              <div className="ion-codex-context-panel-head">
                <span>current surface</span>
                <b>{text(activeSurface.line_count, 0)} lines</b>
              </div>
              <div className="ion-codex-context-surface-meta">
                <PathChip label="path" value={activeSurface.path} />
                <PathChip label="mtime" value={activeSurface.mtime} />
              </div>
              <pre>{text(activeSurface.excerpt, 'No current excerpt available')}</pre>
            </div>
          </article>

          <aside className="ion-codex-context-topology" aria-label="Context topology">
            <div className="ion-codex-context-panel-head">
              <span>topology</span>
              <b>{text(contextTopology.missing_required_route_ref_count, 0)} missing</b>
            </div>
            <div className="ion-codex-context-topology-metrics">
              <ContextPill label="required refs" value={contextTopology.required_route_ref_count ?? 0} />
              <ContextPill label="selected" value={contextTopology.selected_package_count ?? selectedPackages.length} />
              <ContextPill label="route entries" value={routeEntries.length} />
              <ContextPill label="packages" value={packageRows.length} />
            </div>
            <div className="ion-codex-context-package-strip">
              {selectedPackages.slice(0, 10).map((item) => <code key={item}>{item}</code>)}
              {selectedPackages.length === 0 && <span>no selected package projection</span>}
            </div>
            <RecordPanel title="route refs" records={routeEntries.slice(0, 12)} compact />
            <RecordPanel title="packages" records={packageRows.slice(0, 8)} compact />
          </aside>
        </div>

        <div className="ion-codex-context-bottom-grid">
          <RecordPanel title="context boundaries" records={contextBoundaries.slice(0, 10)} compact />
          <RecordPanel title="visible windows" records={records(memory.visible_windows)} compact />
          <RecordPanel title="memory segments" records={records(memory.memory_segments).slice(0, 12)} compact />
          <JsonPanel title="agent context audit" value={contextAgentDiagnostics.agent_context_system_audit ?? {}} />
        </div>
      </section>
    );
  }

  function renderSettingsPane() {
    const projectConfig = record(record(settings.project_config));
    const codexHome = record(settings.codex_home);
    return (
      <section className="ion-codex-data-grid">
        <DataBlock title="cli" rows={[
          ['available', settings.codex_cli_available],
          ['binary', settings.codex_binary_ref],
          ['codex home', codexHome.path_ref],
          ['profiles', records(projectConfig.profile_names).length],
          ['mcp servers', records(projectConfig.mcp_server_names).length],
        ]} />
        <RecordPanel title="profiles" records={records(projectConfig.profile_names)} />
        <RecordPanel title="mcp servers" records={records(projectConfig.mcp_server_names)} />
        <JsonPanel title="redacted config shape" value={projectConfig.redacted_shape} />
        <RecordPanel title="project context" records={records(project.route_entries)} />
      </section>
    );
  }

  function renderHooksPane() {
    const requiredRefs = record(hooks.required_refs);
    const runtimeReceipts = record(hooks.runtime_receipts);
    return (
      <section className="ion-codex-data-grid">
        <DataBlock title="hook status" rows={[
          ['refs', `${text(requiredRefs.required_refs_present, '0')}/${text(requiredRefs.required_ref_count, '0')}`],
          ['groups', runtimeReceipts.hook_group_count],
          ['adapter', record(hooks.shared_adapter).status],
        ]} />
        <RecordPanel title="missing refs" records={records(requiredRefs.missing_required_refs)} />
        <RecordPanel title="receipt groups" records={records(runtimeReceipts.groups)} />
        <JsonPanel title="hook config" value={hooks.config_shape} />
      </section>
    );
  }

  function renderSkillsPane() {
    return (
      <section className="ion-codex-data-grid">
        <DataBlock title="skills" rows={[
          ['chat verdict', record(chat?.skills).verdict],
          ['count', record(chat?.skills).skill_count],
          ['activation', record(chat?.skills).current_activation_verdict],
          ['native installed', cliSummary.native_skill_installed_count],
        ]} />
        <RecordPanel title="required refs" records={records(skills.required_refs)} />
        <JsonPanel title="native installation" value={skills.native_codex_skill_installation} />
        <JsonPanel title="current activation" value={chat?.skills} />
      </section>
    );
  }

  function renderToolsPane() {
    return (
      <section className="ion-codex-data-grid">
        <RecordPanel title="mcp read-only tools" records={records(tools.mcp_read_only_tools)} />
        <RecordPanel title="slash commands" records={records(tools.slash_commands)} />
        <RecordPanel title="capability bindings" records={records(record(cli?.carrier_os).codex_native_capability_bindings)} />
        <JsonPanel title="visibility contract" value={cli?.visibility_contract} />
      </section>
    );
  }

  function renderTracesPane() {
    const traceRecords = records(record(chat?.turn_traces).records);
    return (
      <section className="ion-codex-data-grid">
        <RecordPanel title="turn traces" records={traceRecords} />
        <RecordPanel title="response runs" records={records(chat?.latest_response_runs)} />
        <RecordPanel title="return hydration" records={records(record(chat?.return_hydration).records)} />
        <RecordPanel title="carrier phase events" records={records(memory.carrier_phase_events)} />
      </section>
    );
  }

  function renderQueuePane() {
    return (
      <section className="ion-codex-data-grid">
        <DataBlock title="queue runner" rows={[
          ['verdict', queue.verdict],
          ['active', queue.active_process_running],
          ['queued', queue.queued_request_count],
          ['next', queue.next_request_path],
        ]} />
        <RecordPanel title="work requests" records={records(chat?.latest_work_requests)} />
        <RecordPanel title="automation diagnoses" records={records(chat?.latest_task_return_automation_diagnoses)} />
        <RecordPanel title="machine receipts" records={records(chat?.latest_task_return_machine_receipts)} />
        <RecordPanel title="task returns" records={records(chat?.latest_task_returns)} />
        <JsonPanel title="reconciliation" value={queue.reconciliation} />
      </section>
    );
  }

  function renderActiveLiveChats() {
    return (
      <div className="ion-codex-active-live-chats">
        <div className="ion-codex-drawer-section-head">
          <span>remembered chat tabs</span>
          <b>{openChatTabs.length}</b>
        </div>
        {openChatTabs.length === 0 ? (
          <div className="ion-codex-remembered-tabs-empty">
            <b>No remembered chat tabs open</b>
            <span>Open a past chat from the drawer to make it the current context-inspectable tab.</span>
          </div>
        ) : null}
        {openChatTabs.map((tab) => {
          const tabTitle = chatTitleForSessionId(tab.sessionId, tab.title);
          return (
            <ActiveLiveChatCard
              active={activeChatTabId === tab.id}
              expanded={expandedDrawerSessionIds.has(tab.id)}
              key={tab.id}
              meta={`${tab.isCurrent ? 'current' : sessionShortText(tab.sessionId)} / ${tab.model || 'model unknown'}`}
              onDoubleOpen={() => selectOpenChatTab(tab)}
              onRename={() => startRenameChat(tab.sessionId, tabTitle)}
              onRenameCancel={cancelRenameChat}
              onRenameCommit={commitRenameChat}
              onRenameDraftChange={setRenameDraft}
              onToggle={() => toggleDrawerSession(tab.id)}
              renameDraft={renameDraft}
              renaming={renamingChatId === tab.sessionId}
              status={activeChatTabId === tab.id ? 'active tab' : 'open'}
              subtitle={tab.subtitle || tab.projectLabel || 'open archive chat'}
              title={tabTitle}
              working={false}
            />
          );
        })}
      </div>
    );
  }

  function renderLeftDrawer(id: LeftDrawerId): ReactNode {
    if (id === 'connections') {
      const connectedCount = connectedConnections.length;
      return (
        <div className="ion-codex-connections-drawer">
          <DrawerTitle title="connections" value={`${connectedCount}/${connectionProfiles.length}`} />
          <div className="ion-codex-connection-grid">
            {connectionProfiles.map((profile) => {
              const connected = connectionState[profile.id];
              return (
                <article className={`ion-codex-connection-card${connected ? ' is-connected' : ''}`} key={profile.id}>
                  <header>
                    <span className="ion-codex-connection-card-icon" aria-hidden="true">{profile.icon}</span>
                    <div>
                      <b>{profile.label}</b>
                      <span>{profile.category}</span>
                    </div>
                    <em>{connected ? 'connected' : 'available'}</em>
                  </header>
                  <div className="ion-codex-connection-meta">
                    <span>{profile.mode}</span>
                    <span>{profile.storage}</span>
                  </div>
                  <div className="ion-codex-connection-actions">
                    <button onClick={() => setConnectionConnected(profile.id, !connected)} type="button">
                      {connected ? 'DISCONNECT' : 'CONNECT'}
                    </button>
                    <button onClick={() => openConnectionDrawer(profile.id)} type="button">SETTINGS</button>
                  </div>
                </article>
              );
            })}
          </div>
          <DataBlock title="connection boundary" rows={[
            ['authority', 'candidate UI state'],
            ['credential storage', 'none in browser'],
            ['rail behavior', 'connected icons render above connections'],
          ]} compact />
        </div>
      );
    }
    const connectionProfile = connectionProfileForDrawer(id);
    if (connectionProfile) {
      const connected = connectionState[connectionProfile.id];
      return (
        <div className="ion-codex-connector-settings">
          <DrawerTitle title={connectionProfile.label} value={connected ? 'connected' : 'available'} />
          <section className={`ion-codex-connector-hero${connected ? ' is-connected' : ''}`}>
            <span className="ion-codex-connection-card-icon" aria-hidden="true">{connectionProfile.icon}</span>
            <div>
              <b>{connectionProfile.label}</b>
              <span>{connectionProfile.category}</span>
            </div>
            <button onClick={() => setConnectionConnected(connectionProfile.id, !connected)} type="button">
              {connected ? 'DISCONNECT' : 'CONNECT'}
            </button>
          </section>
          <DataBlock title="settings" rows={[
            ['mode', connectionProfile.mode],
            ['storage', connectionProfile.storage],
            ['left rail icon', connected ? 'visible' : 'hidden'],
            ['status', connected ? 'cockpit connected' : 'not connected'],
          ]} compact />
          <RecordPanel
            title="scopes"
            records={connectionProfile.scopes.map((scope) => ({
              name: scope,
              status: connected ? 'enabled after auth' : 'draft',
            }))}
            compact
          />
          <DataBlock title="authority" rows={[
            ['live external access', false],
            ['secret handling', 'external vault required'],
            ['accepted-state claim', false],
          ]} compact />
        </div>
      );
    }
    if (id === 'sessions') {
      const activeArchiveViewLabel = archiveViews.find((view) => view.id === archiveView)?.label ?? archiveView;
      const visibleGroupCount = archiveSessionGroups.reduce((count, group) => count + group.sessions.length, 0);
      const latestDrawerSession = latestVisibleSession;
      const drawerPacketSessions = archiveSearch ? visiblePacketSessions : shortFilteredSessions.filter(isQueueRunnerPacket);
      const drawerConversationSessions = archiveSearch ? visibleConversationSessions : shortFilteredSessions.filter((session) => !isQueueRunnerPacket(session));
      const favoriteSessions = favoriteChatIds
        .map((sessionId) => allSessions.find((session) => session.session_id === sessionId))
        .filter((session): session is IonCodexConversationArchiveSession => Boolean(session));
      const visibleFavoriteSessions = favoriteSessions.filter((session) => sessionVisibleByShortFilter(session, {
        currentSessionId: currentArchiveSessionId,
        favoriteIds: favoriteChatIdSet,
        openIds: openChatSessionIds,
        prefs: chatDrawerPrefs,
        selectedSessionId,
      }));
      const activeArchiveTabSession = activeChatTab
        ? allSessions.find((session) => session.session_id === activeChatTab.sessionId) ?? sessionFromOpenChatTab(activeChatTab)
        : null;
      const spotlightSession = activeArchiveTabSession ?? selectedSession ?? currentArchiveSession ?? latestDrawerSession;
      const activeSpotlightSessions = uniqueSessionsById([
        activeArchiveTabSession,
        selectedSession,
        currentArchiveSession,
        latestDrawerSession,
      ]);
      const idNeedle = chatDrawerIdSearch.trim().toLowerCase();
      const defaultFindSessions = uniqueSessionsById([
        ...activeSpotlightSessions,
        ...openChatTabs.map(sessionFromOpenChatTab),
        ...sortByRecent(drawerConversationSessions).slice(0, 10),
      ]);
      const idSearchSessions = idNeedle
        ? sortByRecent(shortFilteredSessions.filter((session) => sessionMatchesIdLookup(session, idNeedle))).slice(0, 80)
        : defaultFindSessions;
      const idExactSession = idNeedle
        ? shortFilteredSessions.find((session) => text(session.session_id, '').toLowerCase() === idNeedle) ?? null
        : null;
      const groupedDrawerSessions = chatDrawerGroupView === 'models'
        ? groupedSessions(drawerConversationSessions, (session) => text(session.model, 'Model Unknown'), true)
        : chatDrawerGroupView === 'agents'
          ? groupedSessions(drawerConversationSessions, sessionAgentLabel, true)
          : chatDrawerGroupView === 'context'
            ? groupedSessions(drawerConversationSessions, sessionContextLabel, true)
            : groupedSessions(drawerConversationSessions, projectLabel, true);
      const activeFocusTitle = showingArchiveChat && spotlightSession
        ? chatTitleForSession(spotlightSession)
        : CODEX_CURRENT_SESSION_TITLE;
      const activeFocusId = showingArchiveChat
        ? text(spotlightSession?.session_id || selectedArchiveSessionId, 'archive chat pending')
        : CODEX_LIVE_SESSION_ID;
      const activeFocusMeta = showingArchiveChat && spotlightSession
        ? `${projectLabel(spotlightSession)} / ${text(spotlightSession.model, 'model unknown')}`
        : `${agentIdentity.displayName} / ${activeModelChoiceLabel}`;
      const chatContextSurface = record(chat?.chat_context);
      const activeBinding = record(chatContextSurface.active_binding);
      const activeBindingId = text(activeBinding.binding_id || chatContextSurface.active_binding_id || '', '');
      const attachedSessionRows = archiveAttachments.map((attachment) => {
        const sessionId = text(attachment.session_id || attachment.source_session_id || attachment.id || attachment.ref, '');
        return {
          attachment,
          session: sessionId ? allSessions.find((session) => session.session_id === sessionId) ?? null : null,
          sessionId,
        };
      });
      const chatDrawerPageCounts: Record<ChatDrawerPageId, number> = {
        active: Math.max(1, activeSpotlightSessions.length + openChatTabs.length + visibleFavoriteSessions.length),
        all: visibleGroupCount,
        find: idNeedle ? idSearchSessions.length : defaultFindSessions.length,
        groups: groupedDrawerSessions.reduce((count, group) => count + group.sessions.length, 0),
        work: drawerPacketSessions.length + messageQueueState.items.length,
        attached: totalAttachmentCount,
      };
      const renderSessionCard = (session: IonCodexConversationArchiveSession) => {
        const busy = archiveBusy && selectedSessionId === session.session_id;
        const current = Boolean(session.is_current_session || (currentArchiveSessionId && session.session_id === currentArchiveSessionId));
        const open = openChatSessionIds.has(session.session_id) || selectedArchiveSessionId === session.session_id || activeChatTab?.sessionId === session.session_id;
        const working = current && workerActive;
        const previewItems = drawerSessionPreviewItems(session, selectedExcerpt);
        const cardSession = current ? { ...session, is_current_session: true } : session;
        return (
          <DrawerSessionCard
            active={open}
            attached={sessionAttached(session, archiveAttachments)}
            busy={busy}
            expanded={expandedDrawerSessionIds.has(session.session_id)}
            key={session.session_id}
            onAttach={() => attachSession(session)}
            onContinue={() => continueSessionInComposer(session)}
            onFork={() => copySessionCommand(session, 'fork')}
            onFavorite={() => toggleFavoriteChat(session.session_id)}
            onOpen={() => openSessionInArchive(session)}
            onBranch={() => branchSession(session)}
            onReference={() => referenceSession(session)}
            onRename={() => startRenameChat(session.session_id, chatTitleForSession(session))}
            onRenameCancel={cancelRenameChat}
            onRenameCommit={commitRenameChat}
            onRenameDraftChange={setRenameDraft}
            onResume={() => copySessionCommand(session, 'resume')}
            onToggle={() => toggleDrawerSessionPreview(session)}
            packet={isQueueRunnerPacket(session)}
            favorite={favoriteChatIdSet.has(session.session_id)}
            previewItems={previewItems}
            renameDraft={renameDraft}
            renaming={renamingChatId === session.session_id}
            session={cardSession}
            statusLabel={sessionDrawerStatus(cardSession, busy, open, working, workerDuration)}
            title={chatTitleForSession(session)}
            working={working}
          />
        );
      };
      const renderSessionGroups = (groupsToRender: ArchiveGroup[], emptyLabel: string) => {
        const normalizedGroups = groupsToRender.map((group) => ({
          ...group,
          sessions: group.id === 'favorite-chats'
            ? group.sessions
            : group.sessions.filter((session) => !favoriteChatIdSet.has(session.session_id)),
        }));
        const total = normalizedGroups.reduce((count, group) => count + group.sessions.length, 0) + visibleFavoriteSessions.length;
        return (
          <div className="ion-codex-session-drawer-stack">
            {visibleFavoriteSessions.length && normalizedGroups.some((group) => group.id !== 'favorite-chats') ? (
              <section className="ion-codex-project-session-section is-favorites">
                <div className="ion-codex-project-session-head">
                  <span>Favorites</span>
                  <b>{visibleFavoriteSessions.length}</b>
                </div>
                <div className="ion-codex-drawer-session-stack">
                  {visibleFavoriteSessions.map(renderSessionCard)}
                </div>
              </section>
            ) : null}
            {normalizedGroups.filter((group) => group.sessions.length > 0).map((projectGroup) => (
              <section className="ion-codex-project-session-section" key={projectGroup.id}>
                <div className="ion-codex-project-session-head">
                  <span>{projectGroup.title}</span>
                  <b>{projectGroup.sessions.length}</b>
                </div>
                <div className="ion-codex-drawer-session-stack">
                  {projectGroup.sessions.map(renderSessionCard)}
                </div>
              </section>
            ))}
            {total === 0 && <div className="ion-empty-state">{emptyLabel}</div>}
          </div>
        );
      };
      const renderDrawerPage = () => {
        if (chatDrawerPage === 'find') {
          return (
            <>
              <label className="ion-codex-field ion-codex-session-search is-id-lookup">
                <span>search by session id</span>
                <input
                  placeholder="019e..., archive path, project key, cwd"
                  value={chatDrawerIdSearch}
                  onChange={(event) => setChatDrawerIdSearch(event.currentTarget.value)}
                />
              </label>
              <section className={`ion-codex-session-id-panel${idExactSession ? ' has-exact-match' : ''}`}>
                <div>
                  <span>exact match</span>
                  <b>{idExactSession ? chatTitleForSession(idExactSession) : idNeedle ? 'none' : 'enter id'}</b>
                  <code>{idExactSession?.session_id || chatDrawerIdSearch || 'session id pending'}</code>
                </div>
                <button disabled={!idExactSession} onClick={() => { if (idExactSession) openSessionInArchive(idExactSession); }} type="button">OPEN</button>
                <button disabled={!idExactSession} onClick={() => { if (idExactSession) attachSession(idExactSession); }} type="button">ATTACH</button>
                <button disabled={!chatDrawerIdSearch.trim()} onClick={() => copyMessageText(chatDrawerIdSearch.trim())} type="button">COPY</button>
              </section>
              {renderSessionGroups([{ id: 'id-search', title: idNeedle ? 'ID / path matches' : 'Current and recent IDs', sessions: idSearchSessions }], 'NO MATCHING SESSION ID')}
            </>
          );
        }
        if (chatDrawerPage === 'groups') {
          return (
            <>
              <div className="ion-codex-chat-drawer-segment" role="tablist" aria-label="Chat grouping lens">
                {chatDrawerGroupViews.map((view) => (
                  <button
                    className={chatDrawerGroupView === view.id ? 'is-active' : undefined}
                    key={view.id}
                    onClick={() => setChatDrawerGroupView(view.id)}
                    type="button"
                  >
                    {view.label}
                  </button>
                ))}
              </div>
              {renderSessionGroups(groupedDrawerSessions, 'NO GROUPED CHATS')}
            </>
          );
        }
        if (chatDrawerPage === 'work') {
          return (
            <>
              <section className="ion-codex-session-drawer-summary is-work">
                <div>
                  <span>work surface</span>
                  <b>{workerActive ? `working ${workerDuration || 'now'}` : workerStatus}</b>
                  <small>{queuedRequestCount} queued / {messageQueueState.items.length} staged / {drawerPacketSessions.length} packet chats</small>
                </div>
                <button onClick={() => { setRightDrawer('messageQueue'); setRightDrawerOpen(true); }} type="button">QUEUE</button>
              </section>
              {messageQueueState.items.length ? (
                <section className="ion-codex-chat-drawer-work-list">
                  <div className="ion-codex-drawer-section-head">
                    <span>staged messages</span>
                    <b>{messageQueueState.items.length}</b>
                  </div>
                  {messageQueueState.items.slice(0, 8).map((item) => (
                    <article className="ion-codex-chat-drawer-work-card" key={item.id}>
                      <b>{item.title}</b>
                      <span>{item.mode} / {item.laneId}</span>
                      <code>{item.message}</code>
                    </article>
                  ))}
                </section>
              ) : null}
              {renderSessionGroups([{ id: 'work-packets', title: 'Queue-runner work packets', sessions: sortByRecent(drawerPacketSessions) }], 'NO WORK PACKET CHATS')}
            </>
          );
        }
        if (chatDrawerPage === 'attached') {
          return (
            <>
              <section className="ion-codex-session-drawer-summary is-attached">
                <div>
                  <span>attached chat context</span>
                  <b>{archiveAttachments.length} archives</b>
                  <small>{selectedContextRefCount} selected refs / explicit attachments only</small>
                </div>
                <button onClick={() => { setLeftDrawer('context'); setLeftDrawerOpen(true); }} type="button">CONTEXT</button>
              </section>
              <section className="ion-codex-session-attachment-list">
                <div className="ion-codex-drawer-section-head">
                  <span>attached archives</span>
                  <b>{archiveAttachments.length}</b>
                </div>
                {attachedSessionRows.map((row, index) => (
                  row.session ? renderSessionCard(row.session) : (
                    <article className="ion-codex-attached-ref-card" key={`${row.sessionId || index}-attached`}>
                      <b>{text(row.attachment.title || row.attachment.label || row.attachment.name || row.sessionId, `attached ${index + 1}`)}</b>
                      <span>{text(row.attachment.status || row.attachment.kind || 'archive attachment', 'archive attachment')}</span>
                      <code>{text(row.sessionId || row.attachment.path || row.attachment.ref, 'archive ref')}</code>
                    </article>
                  )
                ))}
                {!archiveAttachments.length ? <div className="ion-empty-state">NO ATTACHED CHAT ARCHIVES</div> : null}
              </section>
              <section className="ion-codex-session-attachment-list">
                <div className="ion-codex-drawer-section-head">
                  <span>selected refs</span>
                  <b>{selectedContextRefs.length}</b>
                </div>
                {selectedContextRefs.slice(0, 18).map((ref) => (
                  <article className="ion-codex-attached-ref-card" key={ref}>
                    <b>{shortPath(ref)}</b>
                    <span>selected context ref</span>
                    <code>{ref}</code>
                  </article>
                ))}
                {!selectedContextRefs.length ? <div className="ion-empty-state">NO SELECTED CONTEXT REFS</div> : null}
              </section>
            </>
          );
        }
        if (chatDrawerPage === 'all') {
          return (
            <>
              <label className="ion-codex-field ion-codex-session-search">
                <span>search chats</span>
                <input placeholder="Project, mission, agent, title, prompt, model" value={archiveSearch} onChange={(event) => setArchiveSearch(event.currentTarget.value)} />
              </label>
              <div className="ion-codex-archive-viewbar is-drawer" role="tablist" aria-label="Past chat organization">
                {archiveViews.map((view) => (
                  <button
                    aria-label={view.label}
                    className={archiveView === view.id ? 'is-active' : undefined}
                    key={view.id}
                    onClick={() => setArchiveView(view.id)}
                    title={view.label}
                    type="button"
                  >
                    <span className="ion-codex-archive-view-icon" aria-hidden="true">{view.icon}</span>
                  </button>
                ))}
              </div>
              <div className="ion-codex-drawer-section-head">
                <span>{archiveView === 'packets' ? 'Queue-runner work packets' : `${activeArchiveViewLabel} chats`}</span>
                <b>{visibleGroupCount}</b>
              </div>
              {renderSessionGroups(archiveSessionGroups, archiveView === 'packets' ? 'NO MATCHING WORK PACKETS' : 'NO MATCHING CHATS')}
            </>
          );
        }
        return (
          <>
            <section className={`ion-codex-session-active-focus${showingArchiveChat ? ' is-archive' : ' is-live'}`}>
              <header>
                <span>current active</span>
                <b>{showingArchiveChat ? 'archive chat' : 'live Codex chat'}</b>
              </header>
              <div>
                <b>{activeFocusTitle}</b>
                <span>{activeFocusMeta}</span>
                <code>{activeFocusId}</code>
                {activeBindingId ? <code>{activeBindingId}</code> : null}
              </div>
              <footer>
                <button onClick={showLiveChat} type="button">LIVE</button>
                <button disabled={!spotlightSession} onClick={() => { if (spotlightSession) openSessionInArchive(spotlightSession); }} type="button">OPEN ACTIVE</button>
                <button onClick={startNewCodexCliThread} type="button">{newCodexSessionRequested ? 'NEW CLI ARMED' : 'NEW CLI THREAD'}</button>
                <button disabled={newCapsuleChatBusy} onClick={() => void createNewCapsuleChat()} type="button">{newCapsuleChatBusy ? 'STARTING' : 'NEW CHAT'}</button>
              </footer>
            </section>
            {activeSpotlightSessions.length ? renderSessionGroups([{ id: 'active-sessions', title: 'Active / selected archive chats', sessions: activeSpotlightSessions }], 'NO ACTIVE ARCHIVE CHAT') : null}
            {renderActiveLiveChats()}
            {latestDrawerSession ? renderSessionGroups([{ id: 'latest-session', title: 'Latest matching chat', sessions: [latestDrawerSession] }], 'NO LATEST CHAT') : null}
          </>
        );
      };
      return (
        <div className="ion-codex-session-drawer">
          <DrawerTitle title="chat navigator" value={archiveOverview.total} />
          <div className="ion-codex-chat-drawer-tabs" role="tablist" aria-label="Chat drawer pages">
            {chatDrawerPages.map((page) => (
              <button
                aria-label={page.label}
                className={chatDrawerPage === page.id ? 'is-active' : undefined}
                key={page.id}
                onClick={() => setChatDrawerPage(page.id)}
                type="button"
              >
                <span className="ion-codex-archive-view-icon" aria-hidden="true">{page.icon}</span>
                <b>{page.label}</b>
                <em>{chatDrawerPageCounts[page.id]}</em>
              </button>
            ))}
          </div>
          <section className="ion-codex-session-drawer-summary" aria-label="Past chat summary">
            <div>
              <span>{showingArchiveChat ? 'archive active' : 'live active'}</span>
              <b>{activeFocusTitle}</b>
              <small>{latestDrawerSession ? `latest ${formatSessionTime(latestDrawerSession)} / ${chatTitleForSession(latestDrawerSession)}` : 'archive has no matching chat sessions'}</small>
            </div>
            <button
              disabled={!latestDrawerSession}
              onClick={() => {
                if (latestDrawerSession) openSessionInArchive(latestDrawerSession);
              }}
              type="button"
            >
              OPEN LATEST
            </button>
          </section>
          <div className="ion-codex-drawer-mini-metrics">
            <span>{visibleSessions.length}/{archiveOverview.total} shown</span>
            <span>{visibleFavoriteSessions.length} fav</span>
            <span>{visibleArchiveOverview.chatCount} chats</span>
            <span>{visibleArchiveOverview.packetCount} packets</span>
            <span>{hiddenShortChatCount} hidden</span>
            <span>{visibleArchiveOverview.projectCount} projects</span>
            <span>{visibleArchiveOverview.modelCount} models</span>
            <span>{visibleArchiveOverview.agentCount} agents</span>
            <span>{visibleArchiveOverview.contextCount} contexts</span>
            <span>{visibleArchiveOverview.today} today</span>
            <span>{visibleArchiveOverview.thisWeek} week</span>
          </div>
          <section className="ion-codex-chat-drawer-filter" aria-label="Past chat filters">
            <label className="ion-codex-chat-drawer-filter-toggle">
              <input
                checked={chatDrawerPrefs.hideShortChats}
                onChange={(event) => setChatDrawerPrefs((previous) => ({
                  ...previous,
                  hideShortChats: event.currentTarget.checked,
                }))}
                type="checkbox"
              />
              <span>hide &lt;= {chatDrawerPrefs.shortChatMaxUserPrompts} user prompts</span>
            </label>
            <label className="ion-codex-chat-drawer-filter-range">
                <span>hide cutoff</span>
              <input
                max={12}
                min={0}
                onChange={(event) => setChatDrawerPrefs((previous) => ({
                  ...previous,
                  shortChatMaxUserPrompts: clampInteger(event.currentTarget.value, 0, 12, 2),
                }))}
                step={1}
                type="range"
                value={chatDrawerPrefs.shortChatMaxUserPrompts}
              />
              <input
                aria-label="Short chat user prompt cutoff"
                max={12}
                min={0}
                onChange={(event) => setChatDrawerPrefs((previous) => ({
                  ...previous,
                  shortChatMaxUserPrompts: clampInteger(event.currentTarget.value, 0, 12, 2),
                }))}
                type="number"
                value={chatDrawerPrefs.shortChatMaxUserPrompts}
              />
            </label>
          </section>
          <div className="ion-codex-chat-drawer-page">{renderDrawerPage()}</div>
        </div>
      );
    }
    if (id === 'context') {
      const activeTabSession = sessionFromOpenChatTab(activeChatTab) ?? selectedSession;
      const activeTabContextBinding = record(record(activeTabSession).chat_context_binding);
      const activeUsesArchive = Boolean(activeChatTab || showingArchiveChat);
      const activeChatContextBinding = Object.keys(activeTabContextBinding).length
        ? activeTabContextBinding
        : activeUsesArchive
          ? {}
          : record(record(chat?.chat_context).active_binding);
      const activeChatBindingIdentity = record(activeChatContextBinding.agent_identity);
      const activeChatMinimumContext = record(activeChatContextBinding.minimum_context);
      const activeTabMissionLabels = records(activeTabSession?.mission_labels);
      const activeTabAgentLabels = records(activeTabSession?.agent_labels);
      const activeChatRoleLookup = text(
        activeChatBindingIdentity.clone_of_role_id
        || activeChatBindingIdentity.role_id
        || activeChatContextBinding.role_id
        || activeTabAgentLabels[0]?.role_id
        || activeTabAgentLabels[0]?.agent_id
        || activeTabAgentLabels[0]?.label,
        '',
      );
      const activeChatContextAgent = activeChatRoleLookup ? findAgentIdentityRecord(contextAgentRows, activeChatRoleLookup) ?? {} : {};
      const activeChatContextAgentId = agentRecordId(activeChatContextAgent);
      const activeChatContextEvidence = record(activeChatContextAgent.agent_page_evidence);
      const activeChatContextSystem = record(activeChatContextEvidence.context_system);
      const activeChatContextCard = record(activeChatContextSystem.card);
      const activeChatContextProof = record(activeChatContextEvidence.proof);
      const activeChatHasContextBinding = Boolean(
        Object.keys(activeChatContextBinding).length
        && (
          activeChatContextBinding.binding_id
          || activeChatContextBinding.role_id
          || activeChatContextBinding.domain_id
          || activeChatContextBinding.branch_id
          || activeChatMinimumContext.floor
          || activeChatMinimumContext.capsule_ref
        ),
      );
      const activeChatContextState = activeChatHasContextBinding
        ? 'CONTEXT SYSTEM BOUND'
        : activeUsesArchive
          ? 'PAST CHAT HAS NO CONTEXT BINDING'
          : 'NO CONTEXT SYSTEM BOUND';
      const activeChatContextDisplay = text(
        activeChatContextAgent.display_name
        || activeChatContextAgent.role_id
        || activeChatRoleLookup
        || activeChatBindingIdentity.agent_true_name
        || activeChatBindingIdentity.agent_instance_id,
        activeChatHasContextBinding ? 'context system mapped' : 'no context system bound',
      );
      const activeChatContextCardPath = text(
        activeChatContextCard.relpath
        || activeChatContextCard.path
        || activeChatContextAgent.context_system_card,
        '',
      );
      const activeChatTitle = activeTabSession
        ? chatTitleForSession(activeTabSession)
        : activeChatContextBinding.branch_title
          ? text(activeChatContextBinding.branch_title, '')
          : 'Current mounted Codex chat';
      const activeChatDomain = text(
        activeChatContextBinding.domain_id
        || activeTabMissionLabels[0]?.domain_id
        || activeTabMissionLabels[0]?.label
        || activeChatContextAgent.registry_primary_domain
        || activeChatContextAgent.role_domain_label,
        'domain unknown',
      );
      const activeChatContextRefs = [
        ...records(activeChatContextBinding.context_floor_refs),
        ...records(activeChatContextBinding.mounted_context_refs),
        ...records(activeChatContextBinding.branch_context_refs),
      ].slice(0, 14);
      const contextSystemRows = buildContextSystemInventoryRows();
      const selectedRow = selectedContextSystemInventoryRow(contextSystemRows);
      const selectedValue = selectedRow?.agentId || '';
      const selectedVariationTags = selectedRow?.variationTags ?? [];
      const packageClasses = uniqueStrings(contextSystemRows.map((row) => row.packageClass).filter(Boolean));
      const bindingCount = contextSystemRows.reduce((count, row) => count + row.mappedBindings.length, 0);
      const freshChatCount = contextSystemRows.reduce((count, row) => count + row.mappedFreshChats.length, 0);
      const openTabCount = contextSystemRows.reduce((count, row) => count + row.mappedOpenTabs.length, 0);
      const activeChatInventoryRow = contextSystemRows.find((row) => row.activeForCurrentChat)
        ?? contextSystemRows.find((row) => row.agentId === activeChatContextAgentId || row.roleId === activeChatRoleLookup)
        ?? null;
      const activeChatInspectId = activeChatInventoryRow?.agentId || activeChatContextAgentId;
      const activeChatStateClass = activeChatHasContextBinding ? 'is-bound' : activeUsesArchive ? 'is-unknown' : 'is-unbound';
      const selectedUsageLabel = selectedRow
        ? `${selectedRow.mappedBindings.length} bindings / ${selectedRow.mappedFreshChats.length} chats / ${selectedRow.mappedOpenTabs.length} tabs`
        : 'no selected context system';
      const refLabel = (row: Record<string, unknown>, fallback: string) => text(row.label || row.name || row.ref || row.relpath || row.path || row.id, fallback);
      const renderDrawerRefs = (title: string, rows: Array<Record<string, unknown>>, empty: string) => (
        <div className="ion-codex-context-drawer-ref-panel">
          <header>
            <span>{title}</span>
            <b>{rows.length}</b>
          </header>
          <div className="ion-codex-context-drawer-ref-list">
            {rows.slice(0, 8).map((row, index) => (
              <code key={`${title}-${refLabel(row, `ref-${index}`)}-${index}`}>{refLabel(row, `ref ${index + 1}`)}</code>
            ))}
            {!rows.length ? <span>{empty}</span> : null}
          </div>
        </div>
      );
      return (
        <div className="ion-codex-context-drawer">
          <DrawerTitle title="context drawer" value={activeChatContextState} />
          <section className={`ion-codex-context-drawer-binding ${activeChatStateClass}`}>
            <header>
              <div>
                <span>chat binding</span>
                <b>{activeChatContextState}</b>
                <code>{activeChatTitle}</code>
              </div>
              <em>{activeUsesArchive ? 'archive chat' : 'live chat'}</em>
            </header>
            <div className="ion-codex-context-drawer-data">
              <div><span>context system</span><b>{activeChatContextDisplay}</b></div>
              <div><span>domain</span><b>{activeChatDomain}</b></div>
              <div><span>role</span><b>{activeChatRoleLookup || text(activeChatContextBinding.role_id, 'role pending')}</b></div>
              <div><span>binding</span><b>{text(activeChatContextBinding.binding_id || activeChatBindingIdentity.agent_instance_id, 'none')}</b></div>
              <div><span>minimum floor</span><b>{text(activeChatMinimumContext.floor || activeChatMinimumContext.capsule_ref, 'not projected')}</b></div>
              <div><span>context card</span><b>{activeChatContextCardPath || 'unmapped'}</b></div>
              <div><span>proof</span><b>{activeChatContextProof.critical_ready ? 'critical ready' : text(activeChatContextSystem.status || activeChatContextAgent.context_system_status, 'pending')}</b></div>
            </div>
            <div className="ion-codex-context-drawer-actions">
              <button
                disabled={!activeChatInspectId}
                onClick={() => {
                  setSelectedContextAgentId(activeChatInspectId);
                  setLeftDrawer('context');
                  setLeftDrawerOpen(true);
                }}
                type="button"
              >
                INSPECT
              </button>
              <button onClick={() => setActiveCodexTab('context')} type="button">CONTEXT PAGE</button>
            </div>
          </section>

          <section className="ion-codex-context-drawer-overview">
            <header>
              <div>
                <span>all context systems</span>
                <b>{contextSystemRows.length ? `${contextSystemRows.length} systems / ${packageClasses.length} variations` : 'no context systems projected'}</b>
                <code>{packageClasses.slice(0, 4).join(' / ') || 'inventory missing from projection'}</code>
              </div>
            </header>
            <div className="ion-codex-context-drawer-metrics">
              <ContextPill label="systems" value={contextSystemRows.length} />
              <ContextPill label="variations" value={packageClasses.length} />
              <ContextPill label="bindings" value={bindingCount} />
              <ContextPill label="fresh chats" value={freshChatCount} />
              <ContextPill label="open tabs" value={openTabCount} />
            </div>
          </section>

          <section className="ion-codex-context-drawer-setup">
            <header>
              <div>
                <span>start chat with context system</span>
                <b>{selectedRow?.displayName ?? 'no context system available'}</b>
                <code>{selectedUsageLabel}</code>
              </div>
              <button
                disabled={!selectedRow?.agent || newCapsuleChatBusy}
                onClick={() => {
                  if (selectedRow?.agent) void createNewCapsuleChat(selectedRow.agent);
                }}
                type="button"
              >
                {newCapsuleChatBusy ? 'STARTING' : 'START'}
              </button>
            </header>
            <label className="ion-codex-context-drawer-select">
              <span>context system</span>
              <select
                aria-label="Select context system for a new Codex chat"
                disabled={!contextSystemRows.length || newCapsuleChatBusy}
                onChange={(event) => setSelectedContextAgentId(event.currentTarget.value)}
                value={selectedValue}
              >
                {!contextSystemRows.length ? <option value="">No context systems projected</option> : null}
                {contextSystemRows.map((row) => (
                  <option key={row.agentId || row.roleId || row.displayName} value={row.agentId}>
                    {row.displayName} / {row.roleId || row.domainId || 'role pending'}
                  </option>
                ))}
              </select>
            </label>
            {selectedRow ? (
              <>
                <div className="ion-codex-context-drawer-tags">
                  {selectedVariationTags.slice(0, 7).map((tag) => <span key={tag}>{tag}</span>)}
                </div>
                <div className="ion-codex-context-drawer-data is-setup">
                  <div><span>domain</span><b>{selectedRow.domainId || 'domain pending'}</b></div>
                  <div><span>role</span><b>{selectedRow.roleId || 'role pending'}</b></div>
                  <div><span>package</span><b>{selectedRow.packageClass}</b></div>
                  <div><span>strategy</span><b>{selectedRow.packageStrategy}</b></div>
                  <div><span>context card</span><b>{selectedRow.cardPath || 'unmapped'}</b></div>
                </div>
              </>
            ) : null}
          </section>

          <section className="ion-codex-context-drawer-systems">
            <header>
              <span>inventory</span>
              <b>{contextSystemRows.length}</b>
            </header>
            <div className="ion-codex-context-drawer-system-list">
              {contextSystemRows.map((row) => (
                <section
                  className={`ion-codex-context-drawer-system${row.activeForCurrentChat ? ' is-active-chat' : ''}${selectedRow?.agentId === row.agentId ? ' is-selected' : ''}`}
                  key={row.agentId || row.roleId || row.domainId}
                >
                  <header>
                    <div>
                      <span>{row.domainId || 'domain pending'}</span>
                      <b>{row.displayName}</b>
                      <code>{row.roleId || row.agentId || 'role pending'}</code>
                    </div>
                    <em>{row.status}</em>
                  </header>
                  <div className="ion-codex-context-drawer-tags">
                    {row.variationTags.slice(0, 5).map((tag) => <span key={tag}>{tag}</span>)}
                  </div>
                  <div className="ion-codex-context-drawer-metrics is-row">
                    <ContextPill label="refs" value={row.contextRefCount} />
                    <ContextPill label="bindings" value={row.mappedBindings.length} />
                    <ContextPill label="fresh" value={row.mappedFreshChats.length} />
                    <ContextPill label="tabs" value={row.mappedOpenTabs.length} />
                  </div>
                  <code className="ion-codex-context-drawer-card-ref">{row.cardPath || 'context card unmapped'}</code>
                  <div className="ion-codex-context-drawer-actions">
                    <button onClick={() => setSelectedContextAgentId(row.agentId)} type="button">SELECT</button>
                    <button onClick={() => {
                      setSelectedContextAgentId(row.agentId);
                      setActiveCodexTab('context');
                    }} type="button">PAGE</button>
                    <button disabled={newCapsuleChatBusy} onClick={() => void createNewCapsuleChat(row.agent)} type="button">CHAT</button>
                  </div>
                </section>
              ))}
              {!contextSystemRows.length ? <div className="ion-empty-state">NO CONTEXT SYSTEMS PROJECTED</div> : null}
            </div>
          </section>

          <section className="ion-codex-context-drawer-evidence">
            <header>
              <span>evidence</span>
              <b>paths / refs / receipts</b>
            </header>
            <div className="ion-codex-context-drawer-paths">
              <PathChip label="context floor" value={chat?.capsule?.path} />
              <PathChip label="hot" value={record(chat?.hot_context).path} />
              <PathChip label="queue" value={chat?.codex_queue_path} />
              {activeChatContextCardPath ? <PathChip label="active card" value={activeChatContextCardPath} /> : null}
            </div>
            {renderDrawerRefs('active chat refs', activeChatContextRefs, 'no refs bound to this chat')}
            {renderDrawerRefs('recent receipts', records(chat?.capsule?.recent_rows), 'no recent context receipts')}
            {renderDrawerRefs('attached chats', archiveAttachments, 'no attached chats')}
          </section>
        </div>
      );
    }
    if (id === 'files') {
      return renderFilePickerPanel();
    }
    if (id === 'projects') {
      return (
        <>
          <DrawerTitle title="project" value={text(project.route_ok)} />
          <PathChip label="root" value={cli?.shell_root} />
          <PathChip label="content" value={cli?.content_root} />
          <RecordPanel title="route entries" records={records(project.route_entries)} compact />
        </>
      );
    }
    if (id === 'agents') {
      return (
        <>
          <DrawerTitle title="agents" value={runtime.agents.spawn_rows.length} />
          <RecordPanel title="spawn rows" records={runtime.agents.spawn_rows as Array<Record<string, unknown>>} compact />
          <RecordPanel title="role phases" records={records(record(agents.role_phase_contract).role_phase_sequence)} compact />
        </>
      );
    }
    return (
      <>
        <DrawerTitle title="compose" value={executionMode} />
        <div className="ion-codex-side-modes">
          {executionModes.map((mode) => (
            <button className={executionMode === mode.id ? 'is-active' : undefined} key={mode.id} onClick={() => setExecutionMode(mode.id)} type="button">
              {mode.label}
            </button>
          ))}
        </div>
        <DataBlock title="bridge" rows={[
          ['default', record(chat?.execution_bridge).default_mode],
          ['runner start', record(chat?.execution_bridge).runner_start_enabled],
          ['response carrier', record(chat?.response_carrier).enabled],
        ]} compact />
      </>
    );
  }

  function renderMessageQueueDrawer(): ReactNode {
    const items = messageQueueState.items;
    const groups = messageQueueState.groups;
    const dispatchingAll = messageQueueDispatchingId === '__all__';
    const busy = sending || Boolean(messageQueueDispatchingId);
    const draftReady = Boolean(messageQueueDraftBody.trim());
    const composerReady = Boolean(composer.trim());
    return (
      <div className="ion-codex-message-queue-drawer">
        <DrawerTitle title="message queues" value={`${items.length} staged / ${groups.length} groups`} />
        <div className="ion-codex-message-queue-toolbar">
          <button disabled={!composerReady} onClick={stageComposerInMessageQueue} title="Move the current composer text into the staged message queue." type="button">
            ADD COMPOSER
          </button>
          <button disabled={!items.length || busy} onClick={() => { void dispatchAllMessageQueueItems(); }} title="Dispatch every staged queue message in order." type="button">
            {dispatchingAll ? 'DISPATCHING' : 'DISPATCH ALL'}
          </button>
          <button disabled={!items.length} onClick={clearMessageQueue} title="Clear the working message queue." type="button">
            CLEAR
          </button>
        </div>
        {(sendError || actionNotice) ? <div className={`ion-codex-message-queue-notice${sendError ? ' is-error' : ''}`}>{sendError || actionNotice}</div> : null}
        <section className="ion-codex-message-queue-form" aria-label="Add queue message">
          <label className="ion-codex-field">
            <span>queue title</span>
            <input onChange={(event) => setMessageQueueDraftTitle(event.currentTarget.value)} placeholder="Optional label" value={messageQueueDraftTitle} />
          </label>
          <label className="ion-codex-field">
            <span>message</span>
            <textarea onChange={(event) => setMessageQueueDraftBody(event.currentTarget.value)} placeholder="Stage a Codex message for later queue/run dispatch" value={messageQueueDraftBody} />
          </label>
          <div className="ion-codex-message-queue-mode-row">
            <select aria-label="Queue message execution mode" onChange={(event) => setMessageQueueDraftMode(event.currentTarget.value as ExecutionModeId)} value={messageQueueDraftMode}>
              {executionModes.map((mode) => <option key={mode.id} value={mode.id}>{mode.label}</option>)}
            </select>
            <button disabled={!draftReady} onClick={addMessageQueueDraft} type="button">ADD</button>
          </div>
        </section>
        <section className="ion-codex-message-queue-save" aria-label="Save and load queue groups">
          <div className="ion-codex-drawer-section-head">
            <span>saved queue groups</span>
            <b>{activeMessageQueueGroup?.name || 'working'}</b>
          </div>
          <label className="ion-codex-field">
            <span>group name</span>
            <input onChange={(event) => setMessageQueueGroupName(event.currentTarget.value)} placeholder={activeMessageQueueGroup?.name || 'Queue group name'} value={messageQueueGroupName} />
          </label>
          <div className="ion-codex-message-queue-toolbar">
            <button disabled={!items.length} onClick={() => saveMessageQueueGroup()} title="Save over the active group or create one if none is loaded." type="button">SAVE GROUP</button>
            <button disabled={!items.length} onClick={() => saveMessageQueueGroup({ asNew: true })} title="Save the current staged queue as a separate group." type="button">SAVE AS NEW</button>
          </div>
          <div className="ion-codex-message-queue-groups">
            {groups.map((group) => (
              <article className={`ion-codex-message-queue-group${group.id === messageQueueState.activeGroupId ? ' is-active' : ''}`} key={group.id}>
                <button className="ion-codex-message-queue-group-main" onClick={() => loadMessageQueueGroup(group)} title={`Load ${group.name}`} type="button">
                  <b>{group.name}</b>
                  <span>{group.items.length} messages / {formatCompactDate(group.updatedAt)}</span>
                </button>
                <button aria-label={`Delete ${group.name}`} className="ion-codex-message-queue-icon-button" onClick={() => deleteMessageQueueGroup(group.id)} title={`Delete ${group.name}`} type="button">
                  <CloseIcon className="ion-close-icon" />
                </button>
              </article>
            ))}
            {groups.length === 0 ? <div className="ion-empty-state">NO SAVED QUEUE GROUPS</div> : null}
          </div>
        </section>
        <section className="ion-codex-message-queue-stack" aria-label="Working message queue">
          <div className="ion-codex-drawer-section-head">
            <span>working queue</span>
            <b>{items.length}</b>
          </div>
          {items.map((item, index) => {
            const editing = editingMessageQueueItemId === item.id;
            const itemBusy = messageQueueDispatchingId === item.id || dispatchingAll;
            return (
              <article
                className={`ion-codex-message-queue-item${messageQueueDraggingId === item.id ? ' is-dragging' : ''}${item.lastDispatchedAt ? ' is-dispatched' : ''}`}
                data-message-queue-item-id={item.id}
                draggable={false}
                key={item.id}
                onDragEnd={() => { messageQueueDraggingIdRef.current = ''; setMessageQueueDraggingId(''); }}
                onDragEnter={(event) => handleMessageQueueDragEnter(event, item.id)}
                onDragOver={(event) => event.preventDefault()}
                onDragStart={(event) => handleMessageQueueDragStart(event, item.id)}
                onDrop={(event) => handleMessageQueueDrop(event, item.id)}
                onMouseEnter={() => reorderMessageQueueDragOver(item.id)}
                onMouseMove={() => reorderMessageQueueDragOver(item.id)}
                onMouseUp={() => reorderMessageQueueDragOver(item.id)}
                onPointerEnter={() => reorderMessageQueueDragOver(item.id)}
                onPointerMove={() => reorderMessageQueueDragOver(item.id)}
                onPointerUp={() => reorderMessageQueueDragOver(item.id)}
              >
                {editing ? (
                  <div className="ion-codex-message-queue-edit">
                    <input aria-label="Edit queue message title" onChange={(event) => setMessageQueueEditTitle(event.currentTarget.value)} value={messageQueueEditTitle} />
                    <select aria-label="Edit queue message execution mode" onChange={(event) => setMessageQueueEditMode(event.currentTarget.value as ExecutionModeId)} value={messageQueueEditMode}>
                      {executionModes.map((mode) => <option key={mode.id} value={mode.id}>{mode.label}</option>)}
                    </select>
                    <textarea aria-label="Edit queue message body" onChange={(event) => setMessageQueueEditBody(event.currentTarget.value)} value={messageQueueEditBody} />
                    <div className="ion-codex-message-queue-item-actions">
                      <button disabled={!messageQueueEditBody.trim()} onClick={commitMessageQueueItemEdit} type="button">SAVE</button>
                      <button onClick={cancelEditMessageQueueItem} type="button">CANCEL</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="ion-codex-message-queue-item-head">
                      <button
                        className="ion-codex-message-queue-drag"
                        onMouseDown={(event) => handleMessageQueueMouseDragStart(event, item.id)}
                        onPointerDown={(event) => handleMessageQueuePointerDragStart(event, item.id)}
                        title="Drag to rearrange"
                        type="button"
                      >
                        #{index + 1}
                      </button>
                      <div>
                        <b>{item.title}</b>
                        <span>{item.mode.replaceAll('_', ' ')} / {wordCount(item.message)} words{item.contextRefs?.length ? ` / ${item.contextRefs.length} refs` : ''}{item.lastDispatchedAt ? ` / sent ${formatCompactDate(item.lastDispatchedAt)}` : ''}</span>
                      </div>
                    </div>
                    <p>{item.message}</p>
                    <div className="ion-codex-message-queue-item-actions">
                      <button disabled={busy} onClick={() => { void dispatchMessageQueueItem(item); }} type="button">{itemBusy ? 'SENDING' : 'SEND'}</button>
                      <button onClick={() => beginEditMessageQueueItem(item)} type="button">EDIT</button>
                      <button onClick={() => duplicateMessageQueueItem(item)} type="button">COPY</button>
                      <button disabled={index === 0} onClick={() => nudgeMessageQueueItem(item.id, -1)} type="button">UP</button>
                      <button disabled={index === items.length - 1} onClick={() => nudgeMessageQueueItem(item.id, 1)} type="button">DOWN</button>
                      <button onClick={() => deleteMessageQueueItem(item.id)} type="button">DELETE</button>
                    </div>
                  </>
                )}
              </article>
            );
          })}
          {items.length === 0 ? <div className="ion-empty-state">NO STAGED CODEX MESSAGES</div> : null}
        </section>
      </div>
    );
  }

  function renderEditsDrawer(): ReactNode {
    const rollbackSummary = record(rollback?.summary);
    const checkpoints = records(rollback?.checkpoints);
    const archiveDiffEvidence = records(rollback?.archive_diff_evidence);
    const rollbackReceipts = records(rollback?.rollback_receipts);
    const currentGit = record(rollback?.current_git);
    const treeDiscipline = record(rollback?.tree_discipline);
    const worktree = record(rollback?.current_worktree);
    const worktreeStats = record(worktree.diff_stats);
    const fileEdits = records(worktree.file_edits);
    const statusSample = records(worktree.status_sample || currentGit.sample);
    const currentFiles = numberValue(worktreeStats.file_count) || fileEdits.length || numberValue(currentGit.scoped_porcelain_count);
    const addedLines = numberValue(worktreeStats.added_lines);
    const removedLines = numberValue(worktreeStats.removed_lines);
    const dirty = Boolean(worktree.dirty ?? currentGit.dirty);
    const views: Array<{ id: EditDrawerViewId; label: string; count: number }> = [
      { id: 'current', label: 'CURRENT', count: currentFiles },
      { id: 'checkpoints', label: 'CHECKPOINTS', count: checkpoints.length },
      { id: 'archive', label: 'ARCHIVE', count: archiveDiffEvidence.length },
      { id: 'receipts', label: 'RECEIPTS', count: rollbackReceipts.length },
    ];
    const activeView = views.some((view) => view.id === editDrawerView) ? editDrawerView : 'current';
    return (
      <div className={`ion-codex-edits-drawer is-${activeView}${dirty ? ' is-dirty' : ' is-clean'}`}>
        <DrawerTitle title="edits" value={rollbackBusy ? 'syncing' : `${currentFiles} files`} />
        <section className="ion-codex-edits-hero" aria-label="Current git edit summary">
          <div className="ion-codex-edits-branch">
            <span>{dirty ? 'worktree has edits' : 'worktree clean'}</span>
            <b>{text(worktree.branch || currentGit.branch, 'branch unknown')}</b>
            <code>{text(worktree.scope_prefix || currentGit.scope_prefix || '.', '.')}</code>
          </div>
          <div className="ion-codex-edits-metrics">
            <EditDrawerStat label="files" value={currentFiles} tone={dirty ? 'watch' : 'ready'} />
            <EditDrawerStat label="added" value={`+${addedLines}`} tone="add" />
            <EditDrawerStat label="removed" value={`-${removedLines}`} tone="remove" />
            <EditDrawerStat label="ready" value={text(rollbackSummary.rollback_ready_count, 0)} tone="ready" />
          </div>
        </section>
        <div className="ion-codex-edits-command-row">
          <button disabled={rollbackBusy} onClick={() => refreshRollbackProjection(selectedArchiveSessionId)} type="button">REFRESH</button>
          <button disabled={rollbackBusy} onClick={captureCurrentDiffCheckpoint} type="button">CAPTURE CHECKPOINT</button>
        </div>
        <div className="ion-codex-edits-viewbar" role="tablist" aria-label="Edit drawer sections">
          {views.map((view) => (
            <button
              aria-selected={activeView === view.id}
              className={activeView === view.id ? 'is-active' : undefined}
              key={view.id}
              onClick={() => setEditDrawerView(view.id)}
              role="tab"
              type="button"
            >
              <span>{view.label}</span>
              <b>{view.count}</b>
            </button>
          ))}
        </div>
        <div className="ion-codex-edits-body">
          {activeView === 'current' ? (
            <section className="ion-codex-edits-section">
              <div className="ion-codex-edits-section-head">
                <span>current worktree</span>
                <b>{dirty ? `${currentFiles} changed paths` : 'clean'}</b>
              </div>
              {Boolean(worktree.diff_truncated) ? (
                <div className="ion-codex-edits-notice is-warning">Diff output is truncated at the cockpit projection limit.</div>
              ) : null}
              {numberValue(worktree.secret_risk_path_count) ? (
                <div className="ion-codex-edits-notice is-warning">Secret-risk paths are redacted from diff excerpts.</div>
              ) : null}
              <div className="ion-codex-edit-file-stack">
                {fileEdits.map((edit, index) => (
                  <EditFileCard edit={edit} index={index} key={`${text(edit.path, 'edit')}-${text(edit.source, 'current')}-${index}`} onCopy={copyMessageText} />
                ))}
                {fileEdits.length === 0 ? <div className="ion-empty-state">{dirty ? 'NO DIFF EXCERPTS AVAILABLE' : 'NO CURRENT FILE EDITS'}</div> : null}
              </div>
              {statusSample.length ? <RecordPanel title="status sample" records={statusSample} compact /> : null}
              <DataBlock title="tree discipline" rows={[
                ['active chat', treeDiscipline.active_chat_mode || 'dirty_tree_compatible'],
                ['new projects', treeDiscipline.new_project_mode || 'clean_tree_required'],
                ['chat blocked by dirt', treeDiscipline.current_tree_blocks_chat],
                ['new start blocked by dirt', treeDiscipline.current_tree_blocks_new_project_start],
              ]} compact />
            </section>
          ) : null}
          {activeView === 'checkpoints' ? (
            <section className="ion-codex-edits-section">
              <div className="ion-codex-edits-section-head">
                <span>rollback checkpoints</span>
                <b>{checkpoints.length}</b>
              </div>
              {rollbackPreview ? <RollbackPreviewPanel preview={rollbackPreview} onCopy={copyMessageText} /> : null}
              <div className="ion-codex-rollback-stack">
                {checkpoints.map((checkpoint, index) => (
                  <RollbackCheckpointCard
                    checkpoint={checkpoint}
                    key={text(checkpoint.checkpoint_id || checkpoint.receipt_path, `checkpoint-${index}`)}
                    onApply={() => applyRollback(checkpoint)}
                    onCopy={() => copyMessageText(text(checkpoint.receipt_path, ''))}
                    onPreview={() => previewRollback(checkpoint)}
                  />
                ))}
                {checkpoints.length === 0 && <div className="ion-empty-state">NO DIFF CHECKPOINTS SAVED</div>}
              </div>
            </section>
          ) : null}
          {activeView === 'archive' ? (
            <section className="ion-codex-edits-section">
              <div className="ion-codex-edits-section-head">
                <span>selected chat diff evidence</span>
                <b>{archiveDiffEvidence.length}</b>
              </div>
              <div className="ion-codex-edit-file-stack">
                {archiveDiffEvidence.map((evidence, index) => (
                  <ArchiveDiffEvidenceCard evidence={evidence} index={index} key={`${text(evidence.diff_sha256 || evidence.item_index, 'archive-diff')}-${index}`} onCopy={copyMessageText} />
                ))}
                {archiveDiffEvidence.length === 0 ? <div className="ion-empty-state">NO DIFF EVIDENCE IN SELECTED CHAT</div> : null}
              </div>
            </section>
          ) : null}
          {activeView === 'receipts' ? (
            <section className="ion-codex-edits-section">
              <div className="ion-codex-edits-section-head">
                <span>rollback receipts</span>
                <b>{rollbackReceipts.length}</b>
              </div>
              <RecordPanel title="rollback receipts" records={rollbackReceipts} compact />
              <RecordPanel title="archive diff evidence" records={archiveDiffEvidence} compact />
            </section>
          ) : null}
        </div>
      </div>
    );
  }

  function renderAssistantDrawer(): ReactNode {
    const traceEvents = liveTranscriptGroups.flatMap((group) => records(record(group.turn_trace).events));
    const returnRecords = liveTranscriptGroups.flatMap((group) => records(group.return_records));
    const assistantTurns = liveTranscriptGroups.flatMap((group) => records(group.assistant_turns));
    const executionTurns = liveTranscriptGroups.flatMap((group) => records(group.execution_turns));
    const contextTurns = liveTranscriptGroups.flatMap((group) => records(group.context_turns));
    const otherTurns = liveTranscriptGroups.flatMap((group) => records(group.other_turns));
    const latestRuns = records(chat?.latest_response_runs);
    const currentFileEditRecords = records(record(rollback?.current_worktree).file_edits).map((file) => {
      const path = text(file.path || file.file_path, 'file');
      return {
        ...file,
        event_type: 'file_edit',
        label: path,
        status: text(file.change_kind || file.status, 'modified'),
        detail: text(file.diff_excerpt || file.summary || path, ''),
        touched_paths: [path],
        source_refs: [path],
      };
    });
    const thinkingRecords = dedupeEventsBySignature([
      ...traceEvents.filter((event) => assistantEventBucket(event) === 'thinking'),
      ...assistantTurns.flatMap((turn) => assistantThinkingRecords({
        assistantTurns: [turn],
        traceEvents: [],
        turnTrace: {},
        userTurn: {},
      }).filter((event) => text(event.event_type, '') !== 'thinking_policy')),
      ...latestRuns
        .filter((run) => text(run.selected_reasoning_effort, ''))
        .map((run) => ({
          ...run,
          event_type: 'thinking_status',
          label: 'Response run thinking/status',
          status: text(run.selected_reasoning_effort, 'unknown'),
          detail: [
            `model ${text(run.selected_model, 'unknown')}`,
            `status ${text(run.status, 'unknown')}`,
            `capture ${text(run.thinking_capture_status, 'status unknown')}`,
            text(run.reasoning_output_tokens || record(run.usage).reasoning_output_tokens, '') ? `reasoning tokens ${text(run.reasoning_output_tokens || record(run.usage).reasoning_output_tokens, '')}` : '',
            text(run.finding, ''),
          ].filter(Boolean).join(' / '),
          source_refs: [
            text(run.path, ''),
            text(run.prompt_path, ''),
            text(run.latest_return_path, ''),
          ].filter(Boolean),
        })),
      {
        event_type: 'thinking_policy',
        label: 'Thinking capture',
        status: memory.raw_hidden_reasoning_exposed || cli?.hidden_reasoning_exposed ? 'raw text present' : 'status/usage',
        detail: 'Shows captured Codex CLI thinking/status events when present; otherwise shows model move, effort, route, tool, usage, and receipt telemetry.',
      },
    ]);
    const editRecords = dedupeEventsBySignature([
      ...currentFileEditRecords,
      ...assistantEditRecords(returnRecords, traceEvents),
    ]);
    const runRecords = dedupeEventsBySignature([
      ...assistantRunRecords({ assistantTurns, executionTurns, traceEvents }),
      ...latestRuns.map((run) => ({
        ...run,
        event_type: 'response_run',
        label: text(run.run_id, 'Response run'),
        status: text(run.status, 'recorded'),
        detail: text(run.finding || run.latest_return_path || run.path, ''),
        source_refs: [
          text(run.path, ''),
          text(run.prompt_path, ''),
          text(run.latest_return_path, ''),
          text(run.events_path, ''),
          text(run.stdout_path, ''),
          text(run.stderr_path, ''),
        ].filter(Boolean),
        tool_name: 'codex exec',
      })),
    ]);
    const proofRecords = dedupeEventsBySignature([
      ...assistantProofRecords(returnRecords, traceEvents),
      ...records(chat?.latest_task_returns).map((item) => ({
        ...item,
        event_type: 'task_return',
        label: text(item.name || item.id || item.path, 'Task return'),
        status: text(item.status || item.decision || item.mtime, 'returned'),
        detail: text(item.summary || item.path, ''),
        source_refs: [text(item.path, '')].filter(Boolean),
      })),
      ...records(chat?.latest_task_return_machine_receipts).map((item) => ({
        ...item,
        event_type: 'machine_receipt',
        label: text(item.name || item.path, 'Machine receipt'),
        status: text(item.status || item.receipt_source || item.mtime, 'receipt'),
        detail: text(item.summary || item.path, ''),
        source_refs: [text(item.path, '')].filter(Boolean),
      })),
    ]);
    const contextRecords = dedupeEventsBySignature([
      ...contextTurns.map(contextTurnEvent),
      ...traceEvents.filter((event) => assistantEventBucket(event) === 'context'),
      ...records(memory.visible_windows).map((windowRecord) => ({
        ...windowRecord,
        event_type: 'context_window',
        label: text(windowRecord.window_id || windowRecord.label || windowRecord.path, 'Context window'),
        status: text(windowRecord.status || windowRecord.kind, 'visible'),
        detail: text(windowRecord.summary || windowRecord.detail || windowRecord.path, ''),
        source_refs: uniqueStrings([
          text(windowRecord.path, ''),
          ...stringList(windowRecord.source_refs),
        ]),
      })),
      ...records(memory.context_matryoshka_layers).map((layer) => ({
        ...layer,
        event_type: 'context_layer',
        label: text(layer.layer_id || layer.label || layer.kind, 'Context layer'),
        status: text(layer.status || layer.kind, 'visible'),
        detail: text(layer.summary || layer.detail || layer.path, ''),
      })),
    ]);
    const eventRecords = dedupeEventsBySignature([
      ...traceEvents.filter((event) => ['events', 'agents', 'tools'].includes(assistantEventBucket(event))),
      ...otherTurns.map(otherTurnEvent),
      ...records(memory.carrier_phase_events).map((event) => ({
        ...event,
        event_type: text(event.event_type || event.kind || 'carrier_phase_event'),
        label: text(event.label || event.phase || event.event_type, 'Carrier phase'),
        status: text(event.status || event.verdict, ''),
        detail: text(event.detail || event.summary || event.path, ''),
      })),
    ]);
    const rawRecords = [
      { label: 'telemetry_inventory', status: 'summary', payload: record(chat?.telemetry_inventory) },
      { label: 'raw_codex_cli', status: text(record(chat?.raw_codex_cli).latest_status, 'raw'), payload: record(chat?.raw_codex_cli) },
      { label: 'model_moves', status: text(record(chat?.model_moves).routing_posture, 'models'), payload: record(chat?.model_moves) },
      { label: 'assistant_work_routes', status: text(record(chat?.assistant_work_routes).verdict, 'routes'), payload: record(chat?.assistant_work_routes) },
      { label: 'turn_traces', status: text(record(chat?.turn_traces).trace_count, 0), payload: record(chat?.turn_traces) },
      { label: 'response_runs', status: latestRuns.length, payload: latestRuns },
      { label: 'return_hydration', status: text(record(chat?.return_hydration).record_count, 0), payload: record(chat?.return_hydration) },
      { label: 'current_worktree', status: text(record(record(rollback?.current_worktree).diff_stats).file_count, 0), payload: record(rollback?.current_worktree) },
      { label: 'service_console', status: text(record(chat?.service_console).verdict, 'service'), payload: record(chat?.service_console) },
    ];
    const tabs: Array<{ id: AssistantDrawerViewId; label: string; count: number }> = [
      { id: 'response', label: 'RESPONSE', count: latestAssistant ? 1 : 0 },
      { id: 'thinking', label: 'THINKING', count: thinkingRecords.length },
      { id: 'edits', label: 'EDITS', count: editRecords.length },
      { id: 'runs', label: 'RUNS', count: runRecords.length },
      { id: 'proof', label: 'PROOF', count: proofRecords.length },
      { id: 'context', label: 'CONTEXT', count: contextRecords.length },
      { id: 'events', label: 'EVENTS', count: eventRecords.length },
      { id: 'raw', label: 'RAW', count: rawRecords.length },
    ];
    return (
      <div className="ion-codex-assistant-drawer">
        <DrawerTitle title="assistant telemetry" value={text(chat?.latest_response_status, 'ready')} />
        <div className="ion-codex-assistant-viewbar" role="tablist" aria-label="Assistant telemetry tabs">
          {tabs.map((tab) => (
            <button
              className={assistantDrawerView === tab.id ? 'is-active' : undefined}
              key={tab.id}
              onClick={() => setAssistantDrawerView(tab.id)}
              role="tab"
              type="button"
            >
              <span>{tab.label}</span>
              <b>{tab.count}</b>
            </button>
          ))}
        </div>
        <div className="ion-codex-assistant-drawer-body">
          {assistantDrawerView === 'response' ? (
            <>
              <article className="ion-codex-assistant-card">
                <span>LATEST RESPONSE</span>
                <p>{latestAssistant || 'No assistant response in current cockpit state.'}</p>
              </article>
              <DataBlock title="chat engine" rows={[
                ['verdict', record(chat?.chat_engine).verdict],
                ['quality', record(chat?.chat_engine).quality_target],
                ['lenses', record(chat?.chat_engine).lens_count],
                ['carrier', record(chat?.response_carrier).verdict],
              ]} compact />
            </>
          ) : null}
          {assistantDrawerView === 'thinking' ? <AssistantEventList emptyLabel="NO THINKING TELEMETRY" records={thinkingRecords} /> : null}
          {assistantDrawerView === 'edits' ? <AssistantEventList emptyLabel="NO FILE EDIT TELEMETRY" records={editRecords} /> : null}
          {assistantDrawerView === 'runs' ? <AssistantEventList emptyLabel="NO RESPONSE RUN TELEMETRY" records={runRecords} /> : null}
          {assistantDrawerView === 'proof' ? <AssistantEventList emptyLabel="NO PROOF TELEMETRY" records={proofRecords} /> : null}
          {assistantDrawerView === 'context' ? <AssistantEventList emptyLabel="NO CONTEXT TELEMETRY" records={contextRecords} /> : null}
          {assistantDrawerView === 'events' ? <AssistantEventList emptyLabel="NO EVENT TELEMETRY" records={eventRecords} /> : null}
          {assistantDrawerView === 'raw' ? <AssistantRawDataPanel records={rawRecords} /> : null}
        </div>
      </div>
    );
  }

  function renderRightDrawer(id: RightDrawerId): ReactNode {
    if (id === 'missionProfile') {
      return renderMissionProfileDrawer();
    }
    if (id === 'branches') {
      return (
        <>
          <DrawerTitle title="branches" value={chatBranches.length} />
          <div className="ion-codex-branch-stack">
            {chatBranches.map((branch, index) => (
              <BranchCard
                branch={branch}
                key={text(branch.branch_id, `branch-${index}`)}
                onAttach={() => attachBranchSource(branch)}
                onCopy={() => copyBranchCommand(branch)}
                onQueue={() => queueBranch(branch)}
                onUse={() => useBranchPrompt(branch)}
              />
            ))}
            {chatBranches.length === 0 && <div className="ion-empty-state">NO BRANCH DRAFTS</div>}
          </div>
        </>
      );
    }
    if (id === 'rollback') {
      return renderEditsDrawer();
    }
    if (id === 'status') {
      return (
        <>
          <DrawerTitle title="codex context" value={text(chat?.verdict || cli?.verdict)} />
          <div className={`ion-runtime-verdict is-${verdictClass(chat?.verdict || cli?.verdict)}`}>{text(chat?.verdict || cli?.verdict)}</div>
          <div className="ion-codex-kpi-strip is-drawer">
            <Metric label="turns" value={record(chat?.conversation_summary).turn_count} />
            <Metric label="sessions" value={archive?.source_counts?.session_files_total ?? 0} />
            <Metric label="attached" value={chatMemory.archive_attachment_count ?? archiveAttachments.length} />
            <Metric label="branches" value={chatBranches.length} />
            <Metric label="tools" value={cliSummary.mcp_read_only_tool_count} />
            <Metric label="hooks" value={cliSummary.hook_group_count} />
          </div>
          <DataBlock title="chat surface" rows={[
            ['mode', executionMode],
            ['context floor', chat?.capsule?.entry_count],
            ['queue', queue.queued_request_count],
            ['model', record(record(settings.project_config)).default_model || record(chat?.response_carrier).selected_model || 'codex'],
          ]} compact />
        </>
      );
    }
    if (id === 'messageQueue') return renderMessageQueueDrawer();
    if (id === 'evidence') {
      return (
        <>
          <DrawerTitle title="evidence" value={chat?.response_run_count ?? 0} />
          <RecordPanel title="response runs" records={records(chat?.latest_response_runs)} compact />
          <RecordPanel title="attached chats" records={archiveAttachments} compact />
          <RecordPanel title="task returns" records={records(chat?.latest_task_returns)} compact />
          <RecordPanel title="receipts" records={runtime.receipts.slice(0, 8)} compact />
        </>
      );
    }
    if (id === 'ide') {
      return (
        <>
          <DrawerTitle title="codex ide" value={text(cli?.verdict)} />
          <PathChip label="root" value={cli?.shell_root} />
          <PathChip label="config" value={record(record(settings.project_config)).path_ref} />
          <RecordPanel title="context files" records={contextSurfaces.slice(0, 6)} compact />
          <RecordPanel title="commands" records={[
            { name: 'codex resume', status: 'terminal', path: selectedSessionId ? `codex resume ${selectedSessionId}` : 'select past chat' },
            { name: 'codex fork', status: 'terminal', path: selectedSessionId ? `codex fork ${selectedSessionId}` : 'select past chat' },
            { name: 'queue work', status: executionMode, path: chat?.codex_queue_path },
          ]} compact />
        </>
      );
    }
    if (id === 'authority') {
      return (
        <>
          <DrawerTitle title="authority" value="scoped" />
          <div className="ion-codex-authority-stack">
            <span>PRODUCTION: {chat?.production_authority || cli?.production_authority ? 'TRUE' : 'FALSE'}</span>
            <span>LIVE EXEC: {chat?.live_execution_authority || cli?.live_execution_authority ? 'TRUE' : 'FALSE'}</span>
            <span>SECRETS: {chat?.secrets_authority || cli?.secrets_authority ? 'TRUE' : 'FALSE'}</span>
            <span>THINKING CAPTURE: {memory.raw_hidden_reasoning_exposed || cli?.hidden_reasoning_exposed ? 'RAW TEXT' : 'STATUS/USAGE'}</span>
            <span>RAW ARCHIVE: {archive?.raw_transcript_exported ? 'EXPORTED' : 'BLOCKED'}</span>
          </div>
        </>
      );
    }
    if (id === 'settings') {
      return (
        <>
          <DrawerTitle title="settings" value={text(settings.codex_cli_available)} />
          <PathChip label="binary" value={settings.codex_binary_ref} />
          <PathChip label="codex home" value={record(settings.codex_home).path_ref} />
          <RecordPanel title="profiles" records={records(record(record(settings.project_config)).profile_names)} compact />
        </>
      );
    }
    return renderAssistantDrawer();
  }
}

function IconBar<T extends string>({
  items,
  active,
  onSelect,
}: {
  items: Array<IconBarItem<T>>;
  active?: T;
  onSelect: (id: T) => void;
}) {
  return (
    <div className="ion-codex-iconbar">
      {items.map((item) => (
        <button
          aria-label={item.title}
          className={[active === item.id ? 'is-active' : '', item.className ?? ''].filter(Boolean).join(' ') || undefined}
          key={item.id}
          onClick={() => onSelect(item.id)}
          title={item.title}
          type="button"
        >
          <span className="ion-rail-icon" aria-hidden="true">{item.icon}</span>
        </button>
      ))}
    </div>
  );
}

function drawerTitle<T extends string>(items: Array<IconBarItem<T>>, active: T) {
  return items.find((item) => item.id === active)?.title ?? connectionProfileForDrawer(active)?.label ?? active;
}

function EditDrawerStat({ label, tone, value }: { label: string; tone: 'ready' | 'watch' | 'add' | 'remove'; value: unknown }) {
  return (
    <div className={`ion-codex-edit-stat is-${tone}`}>
      <span>{label}</span>
      <b>{text(value)}</b>
    </div>
  );
}

function EditFileCard({
  edit,
  index,
  onCopy,
}: {
  edit: Record<string, unknown>;
  index: number;
  onCopy: (value: unknown) => void | Promise<void>;
}) {
  const stats = record(edit.diff_stats);
  const path = text(edit.path || stringList(stats.files)[0], 'path unknown');
  const source = text(edit.source, 'current');
  const status = text(edit.status || edit.change_kind, source);
  const added = numberValue(edit.added_lines || stats.added_lines);
  const removed = numberValue(edit.removed_lines || stats.removed_lines);
  const hunkCount = numberValue(edit.hunk_count);
  const excerpt = text(edit.safe_diff_excerpt || edit.diff_excerpt || edit.saved_diff_excerpt, '');
  const redacted = Boolean(edit.secret_risk);
  const tone = redacted ? 'redacted' : editFileTone(status, source, added, removed);
  return (
    <article className={`ion-codex-edit-file-card is-${safeClass(source)} is-${tone}`}>
      <header>
        <div className="ion-codex-edit-file-title">
          <span>#{index + 1} / {source} / {status}</span>
          <b>{path}</b>
        </div>
        <div className="ion-codex-edit-file-actions">
          <button onClick={() => { void onCopy(path); }} type="button">COPY PATH</button>
          <button disabled={!excerpt} onClick={() => { void onCopy(excerpt); }} type="button">COPY DIFF</button>
        </div>
      </header>
      <div className="ion-codex-edit-file-stats">
        <span className="is-add">+{added}</span>
        <span className="is-remove">-{removed}</span>
        <span>{hunkCount} hunks</span>
        <span>{text(edit.change_kind, 'modified')}</span>
      </div>
      {excerpt ? <EditDiffBlock value={excerpt} /> : <div className="ion-codex-edits-notice">No diff excerpt exported for this file.</div>}
    </article>
  );
}

function ArchiveDiffEvidenceCard({
  evidence,
  index,
  onCopy,
}: {
  evidence: Record<string, unknown>;
  index: number;
  onCopy: (value: unknown) => void | Promise<void>;
}) {
  const stats = record(evidence.diff_stats);
  const files = uniqueStrings([...stringList(stats.files), ...stringList(evidence.path_refs)]).slice(0, 10);
  const diff = text(evidence.safe_text_excerpt || evidence.safe_diff_excerpt || evidence.message, '');
  return (
    <article className="ion-codex-edit-file-card is-archive">
      <header>
        <div className="ion-codex-edit-file-title">
          <span>#{index + 1} / archive evidence / {text(evidence.detail_label, 'chat diff')}</span>
          <b>{files[0] || `item ${text(evidence.item_index, index + 1)}`}</b>
        </div>
        <div className="ion-codex-edit-file-actions">
          <button disabled={!files.length} onClick={() => { void onCopy(files.join('\n')); }} type="button">COPY PATHS</button>
          <button disabled={!diff} onClick={() => { void onCopy(diff); }} type="button">COPY DIFF</button>
        </div>
      </header>
      <div className="ion-codex-edit-file-stats">
        <span>FILES {text(stats.file_count ?? files.length, 0)}</span>
        <span className="is-add">+{text(stats.added_lines, 0)}</span>
        <span className="is-remove">-{text(stats.removed_lines, 0)}</span>
        <span>{formatCompactDate(evidence.timestamp)}</span>
      </div>
      {files.length ? <DetailChipRow values={files} /> : null}
      {diff ? <EditDiffBlock value={diff} /> : <div className="ion-codex-edits-notice">No safe diff excerpt exported for this archive row.</div>}
    </article>
  );
}

function EditDiffBlock({ value, maxLines = 260 }: { value: string; maxLines?: number }) {
  const lines = value.split('\n');
  const visibleLines = lines.slice(0, maxLines);
  const truncated = lines.length > maxLines;
  return (
    <pre className="ion-codex-diff-block ion-codex-edit-diff-block">
      {visibleLines.map((line, index) => (
        <span className={diffLineClass(line)} key={`${index}-${line.slice(0, 32)}`}>
          <i>{index + 1}</i>
          <code>{line || ' '}</code>
        </span>
      ))}
      {truncated ? (
        <span className="is-hunk">
          <i>{visibleLines.length + 1}</i>
          <code>{`... ${lines.length - visibleLines.length} more diff lines`}</code>
        </span>
      ) : null}
    </pre>
  );
}

function editFileTone(status: string, source: string, added: number, removed: number) {
  const joined = `${status} ${source}`.toLowerCase();
  const statusCode = status.trim().toUpperCase();
  if (joined.includes('untracked') || joined.includes('??') || statusCode.startsWith('A') || joined.includes('added')) return 'add';
  if (statusCode.startsWith('D') || joined.includes('deleted') || joined.includes('remove')) return 'remove';
  if (added && !removed) return 'add';
  if (removed && !added) return 'remove';
  return 'change';
}

function ArchiveMetric({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-codex-archive-metric">
      <span>{label}</span>
      <b>{text(value)}</b>
    </div>
  );
}

function RollbackCheckpointCard({
  checkpoint,
  onApply,
  onCopy,
  onPreview,
}: {
  checkpoint: Record<string, unknown>;
  onApply: () => void;
  onCopy: () => void | Promise<void>;
  onPreview: () => void;
}) {
  const stats = record(checkpoint.diff_stats);
  const files = stringList(stats.files).slice(0, 6);
  const supported = Boolean(checkpoint.rollback_supported) && !numberValue(checkpoint.secret_risk_path_count);
  const status = text(checkpoint.rollback_status, supported ? 'available' : 'evidence_only');
  return (
    <article className={`ion-codex-rollback-card is-${safeClass(status)}`}>
      <header>
        <div>
          <span>{supported ? 'rollback ready' : 'diff evidence'}</span>
          <b>{text(checkpoint.label || checkpoint.checkpoint_id, 'Codex diff checkpoint')}</b>
        </div>
        <em>{formatCompactDate(checkpoint.created_at)}</em>
      </header>
      <div className="ion-codex-detail-strip">
        <span>FILES {text(stats.file_count ?? files.length, 0)}</span>
        <span>+{text(stats.added_lines, 0)}</span>
        <span>-{text(stats.removed_lines, 0)}</span>
        <span>{status}</span>
      </div>
      {files.length ? <DetailChipRow values={files} /> : null}
      <p>{text(checkpoint.receipt_path, 'saved diff receipt')}</p>
      <div className="ion-codex-rollback-actions">
        <button onClick={onPreview} type="button">PREVIEW</button>
        <button disabled={!supported} onClick={onApply} type="button">APPLY</button>
        <button onClick={() => { void onCopy(); }} type="button">COPY REF</button>
      </div>
    </article>
  );
}

function RollbackPreviewPanel({
  onCopy,
  preview,
}: {
  onCopy: (value: unknown) => void | Promise<void>;
  preview: Record<string, unknown>;
}) {
  const ready = Boolean(preview.rollback_ready);
  const blockers = stringList(preview.blockers);
  const diff = text(preview.saved_diff_excerpt, '');
  return (
    <article className={`ion-codex-rollback-preview${ready ? ' is-ready' : ' is-blocked'}`}>
      <header>
        <div>
          <span>{ready ? 'rollback preview clean' : 'rollback blocked'}</span>
          <b>{text(preview.checkpoint_id, 'checkpoint')}</b>
        </div>
        <button onClick={() => { void onCopy(diff); }} type="button">COPY DIFF</button>
      </header>
      {blockers.length ? <DetailChipRow values={blockers} /> : null}
      <pre className="ion-codex-diff-block">
        {diff.split('\n').slice(0, 220).map((line, index) => (
          <span className={diffLineClass(line)} key={`${index}-${line.slice(0, 24)}`}>{line || ' '}</span>
        ))}
      </pre>
    </article>
  );
}

function SessionButton({
  active,
  onOpen,
  session,
  title,
}: {
  active: boolean;
  onOpen: () => void;
  session: IonCodexConversationArchiveSession;
  title: string;
}) {
  const current = Boolean(session.is_current_session);
  return (
    <button className={[active ? 'is-active' : '', current ? 'is-current' : ''].filter(Boolean).join(' ') || undefined} onClick={onOpen} type="button">
      <div className="ion-codex-session-row-top">
        <b>{title}</b>
        <em>{sessionActivity(session)}</em>
      </div>
      <span>{formatSessionTime(session)} / {projectLabel(session)}</span>
      <small>{text(session.latest_user_snippet || session.first_user_snippet, 'no prompt snippet')}</small>
      <div className="ion-codex-session-tags">
        {current ? <span>CURRENT</span> : null}
        <span>{sessionShortId(session)}</span>
        <span>{text(session.model, 'model unknown')}</span>
        <span>{text(session.history_prompt_count, 0)} prompts</span>
        <span>{text(session.line_count_sampled, 0)} events</span>
      </div>
    </button>
  );
}

function ActiveLiveChatCard({
  active,
  expanded,
  meta,
  onDoubleOpen,
  onRename,
  onRenameCancel,
  onRenameCommit,
  onRenameDraftChange,
  onToggle,
  renameDraft,
  renaming,
  status,
  subtitle,
  title,
  working,
}: {
  active: boolean;
  expanded: boolean;
  meta: string;
  onDoubleOpen: () => void;
  onRename: () => void;
  onRenameCancel: () => void;
  onRenameCommit: () => void;
  onRenameDraftChange: (value: string) => void;
  onToggle: () => void;
  renameDraft: string;
  renaming: boolean;
  status: string;
  subtitle: string;
  title: string;
  working: boolean;
}) {
  return (
    <article className={`ion-codex-active-live-card${active ? ' is-active' : ''}${working ? ' is-working' : ''}${expanded ? ' is-expanded' : ' is-collapsed'}`}>
      {renaming ? (
        <form className="ion-codex-active-live-card-edit" onSubmit={(event) => { event.preventDefault(); onRenameCommit(); }}>
          <input
            aria-label={`Rename ${title}`}
            autoFocus
            onChange={(event) => onRenameDraftChange(event.currentTarget.value)}
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                event.preventDefault();
                onRenameCancel();
              }
            }}
            value={renameDraft}
          />
          <button aria-label="Save chat name" title="Save chat name" type="submit">
            <CheckIcon className="ion-codex-rename-icon" />
          </button>
          <button aria-label="Cancel rename" onClick={onRenameCancel} title="Cancel rename" type="button">
            <CloseIcon className="ion-close-icon" />
          </button>
          <span>{meta}</span>
        </form>
      ) : (
        <>
          <button
            onClick={(event) => {
              if (event.detail > 1) return;
              onToggle();
            }}
            onDoubleClick={onDoubleOpen}
            title="Double click to open in main chat"
            type="button"
          >
            <div className="ion-codex-session-row-top">
              <b
                onDoubleClick={(event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  onRename();
                }}
                title="Double click title to rename"
              >
                {title}
              </b>
              <em>{status}</em>
            </div>
            <span>{meta}</span>
            {expanded ? <small>{subtitle}</small> : null}
          </button>
          <button
            aria-label={`Rename ${title}`}
            className="ion-codex-chat-rename-icon-button"
            onClick={onRename}
            title={`Rename ${title}`}
            type="button"
          >
            <ComposeIcon className="ion-codex-rename-icon" />
          </button>
        </>
      )}
    </article>
  );
}

function DrawerSessionCard({
  active,
  attached,
  busy,
  expanded,
  favorite,
  onAttach,
  onBranch,
  onContinue,
  onFavorite,
  onFork,
  onOpen,
  onReference,
  onRename,
  onRenameCancel,
  onRenameCommit,
  onRenameDraftChange,
  onResume,
  onToggle,
  packet = false,
  previewItems,
  renameDraft,
  renaming,
  session,
  statusLabel,
  title,
  working,
}: {
  active: boolean;
  attached: boolean;
  busy: boolean;
  expanded: boolean;
  favorite: boolean;
  onAttach: () => void;
  onBranch: () => void;
  onContinue: () => void;
  onFavorite: () => void;
  onFork: () => void;
  onOpen: () => void;
  onReference: () => void;
  onRename: () => void;
  onRenameCancel: () => void;
  onRenameCommit: () => void;
  onRenameDraftChange: (value: string) => void;
  onResume: () => void;
  onToggle: () => void;
  packet?: boolean;
  previewItems: DrawerSessionPreviewItem[];
  renameDraft: string;
  renaming: boolean;
  session: IonCodexConversationArchiveSession;
  statusLabel: string;
  title: string;
  working: boolean;
}) {
  const missionLabels = records(session.mission_labels).slice(0, 3);
  const agentLabels = records(session.agent_labels).slice(0, 4);
  const tools = records(session.tool_summary).slice(0, 3);
  const current = Boolean(session.is_current_session);
  const promptCount = numberValue(session.history_prompt_count);
  const eventCount = numberValue(session.line_count_sampled);
  const activity = sessionActivity(session);
  const primaryMission = text(missionLabels[0]?.label, 'domain unknown');
  const primaryAgent = sessionAgentLabel(session);
  const carrierLabel = sessionCarrierLabel(session);
  const contextLabel = sessionContextLabel(session);
  return (
    <article aria-busy={busy} className={`ion-codex-drawer-session-card${attached ? ' is-attached' : ''}${packet ? ' is-packet' : ''}${current ? ' is-current' : ''}${active ? ' is-active-chat' : ''}${favorite ? ' is-favorite' : ''}${working ? ' is-working' : ''}${expanded ? ' is-expanded' : ' is-collapsed'}`}>
      {renaming ? (
        <form className="ion-codex-drawer-session-rename" onSubmit={(event) => { event.preventDefault(); onRenameCommit(); }}>
          <input
            aria-label={`Rename ${title}`}
            autoFocus
            onChange={(event) => onRenameDraftChange(event.currentTarget.value)}
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                event.preventDefault();
                onRenameCancel();
              }
            }}
            value={renameDraft}
          />
          <button aria-label="Save chat name" title="Save chat name" type="submit">
            <CheckIcon className="ion-codex-rename-icon" />
          </button>
          <button aria-label="Cancel rename" onClick={onRenameCancel} title="Cancel rename" type="button">
            <CloseIcon className="ion-close-icon" />
          </button>
          <span>{formatSessionTime(session)} / {projectLabel(session)}</span>
        </form>
      ) : (
        <>
          <button
            className="ion-codex-drawer-session-main"
            onClick={(event) => {
              if (event.detail > 1) return;
              onToggle();
            }}
            onDoubleClick={onOpen}
            title="Click to expand or minimize. Double click to open in main chat."
            type="button"
          >
            <div className="ion-codex-session-row-top">
              <b
                onDoubleClick={(event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  onRename();
                }}
                title="Double click title to rename"
              >
                {title}
              </b>
              <em>{statusLabel}</em>
            </div>
            <span>{formatSessionTime(session)} / {projectLabel(session)}</span>
            <div className="ion-codex-drawer-session-identity" aria-label="Agent and context classification">
              <span>{primaryAgent}</span>
              <span>{contextLabel}</span>
            </div>
            <div className="ion-codex-drawer-session-facts">
              <span>last {formatSessionTime(session)}</span>
              <span>{promptCount} prompts</span>
              <span>{eventCount} events</span>
              <span>activity {activity}</span>
              <span>{primaryMission}</span>
              <span>{primaryAgent}</span>
            </div>
            {expanded ? <small>{text(session.latest_user_snippet || session.first_user_snippet, 'no prompt snippet')}</small> : null}
            <div className="ion-codex-session-tags">
              {current ? <span>CURRENT</span> : null}
              {active ? <span>OPEN</span> : null}
              {favorite ? <span>FAV</span> : null}
              {working ? <span>{statusLabel}</span> : null}
              <span>{sessionShortId(session)}</span>
              <span>{text(session.model, 'model unknown')}</span>
              <span>{carrierLabel}</span>
              <span>{contextLabel}</span>
              {expanded ? <span>{text(session.history_prompt_count, 0)} prompts</span> : null}
              {expanded ? <span>{text(session.line_count_sampled, 0)} events</span> : null}
              {attached && <span>attached</span>}
            </div>
            {expanded ? <LabelRow labels={missionLabels} /> : null}
            {expanded ? <LabelRow labels={agentLabels} /> : null}
            {expanded && tools.length ? (
              <div className="ion-codex-inline-tool-row">
                {tools.map((tool, index) => (
                  <span key={`${text(tool.name)}-${index}`}>{text(tool.name)}:{text(tool.count, 0)}</span>
                ))}
              </div>
            ) : null}
            {expanded ? (
              <div className="ion-codex-drawer-session-preview" aria-label={`Recent messages for ${title}`}>
                <div className="ion-codex-drawer-session-preview-head">
                  <span>recent messages</span>
                  <b>{previewItems.length || (busy ? 'loading' : 0)}</b>
                </div>
                {previewItems.length ? previewItems.map((item, index) => (
                  <article className={`ion-codex-drawer-message-preview is-${safeClass(item.role)}`} key={`${item.role}-${index}-${item.text.slice(0, 16)}`}>
                    <header>
                      <span>{item.role}</span>
                      {item.timestamp ? <time>{formatCompactDate(item.timestamp)}</time> : null}
                    </header>
                    <p>{item.text}</p>
                  </article>
                )) : (
                  <span className="ion-codex-drawer-session-preview-empty">
                    {busy ? 'Loading recent transcript window...' : 'No recent message preview available yet.'}
                  </span>
                )}
              </div>
            ) : null}
          </button>
          <button
            aria-label={`Rename ${title}`}
            className="ion-codex-chat-rename-icon-button"
            onClick={onRename}
            title={`Rename ${title}`}
            type="button"
          >
            <ComposeIcon className="ion-codex-rename-icon" />
          </button>
        </>
      )}
      {!renaming ? <div className="ion-codex-drawer-row-actions is-primary">
        <button onClick={onOpen} type="button">OPEN CHAT</button>
        <button className={favorite ? 'is-favorite-action' : undefined} onClick={onFavorite} type="button">{favorite ? 'UNFAV' : 'FAV'}</button>
        <button onClick={onContinue} type="button">CONTINUE</button>
        <button onClick={onAttach} type="button">{attached ? 'ATTACHED' : 'ATTACH'}</button>
        <button aria-label={`Rename ${title}`} onClick={onRename} title={`Rename ${title}`} type="button">
          <ComposeIcon className="ion-codex-rename-icon" />
        </button>
      </div> : null}
      {expanded && !renaming ? <div className="ion-codex-drawer-row-actions is-secondary">
        <button onClick={onOpen} type="button">VIEW</button>
        <button onClick={onContinue} type="button">CONTINUE</button>
        <button onClick={onAttach} type="button">ATTACH</button>
        <button onClick={onBranch} type="button">BRANCH</button>
        <button onClick={onReference} type="button">REF</button>
        <button onClick={onResume} type="button">RESUME</button>
        <button onClick={onFork} type="button">FORK</button>
      </div> : null}
    </article>
  );
}

function BranchCard({
  branch,
  onAttach,
  onCopy,
  onQueue,
  onUse,
}: {
  branch: Record<string, unknown>;
  onAttach: () => void;
  onCopy: () => void | Promise<void>;
  onQueue: () => void | Promise<void>;
  onUse: () => void;
}) {
  const parent = record(branch.parent);
  const command = text(record(branch.codex_fork).command_text, '');
  return (
    <article className="ion-codex-branch-card">
      <div className="ion-codex-branch-head">
        <b>{text(branch.title, 'Branch draft')}</b>
        <em>{text(branch.status, 'draft')}</em>
      </div>
      <p>{text(branch.objective || branch.prompt, 'No branch prompt')}</p>
      <div className="ion-codex-session-tags">
        <span>{text(parent.kind, 'parent')}</span>
        {parent.session_id ? <span>{text(parent.session_id)}</span> : null}
        {parent.turn_id ? <span>{text(parent.turn_id)}</span> : null}
        <span>{command ? 'fork command' : 'prompt only'}</span>
      </div>
      {command ? <code>{command}</code> : null}
      <div className="ion-codex-branch-actions">
        <button onClick={onUse} type="button">USE PROMPT</button>
        <button onClick={onCopy} type="button">{command ? 'COPY CMD' : 'COPY PROMPT'}</button>
        <button onClick={onQueue} type="button">QUEUE</button>
        <button onClick={onAttach} type="button">ATTACH</button>
      </div>
    </article>
  );
}

function LabelRow({ labels, fallback = '' }: { labels: Array<Record<string, unknown>>; fallback?: string }) {
  if (labels.length === 0 && !fallback) return null;
  return (
    <div className="ion-codex-label-row">
      {labels.map((label, index) => (
        <SignalBadge
          confidence={text(label.confidence, 'weak')}
          key={`${text(label.label)}-${index}`}
          label={text(label.label)}
          source={text(label.source, '')}
        />
      ))}
      {labels.length === 0 && fallback ? <SignalBadge confidence="weak" label={fallback} /> : null}
    </div>
  );
}

function SignalBadge({ label, confidence, source = '' }: { label: string; confidence: string; source?: string }) {
  return (
    <span className={`ion-codex-signal-badge is-${safeClass(confidence)}`} title={source ? `${confidence}: ${source}` : confidence}>
      {label}
    </span>
  );
}

type MessageActions = {
  onBranch: (source: BranchSource) => void;
  onCopy: (value: unknown) => void | Promise<void>;
  onQuote: (value: unknown) => void;
  onRun: (value: unknown) => void;
  onPin: (value: unknown, sourceTurnId?: unknown) => void | Promise<void>;
};

function TurnGroup({
  group,
  latestAssistantKey,
  onBranch,
  onCopy,
  onQuote,
  onRun,
  onPin,
  turnIndex,
}: {
  group: Record<string, unknown>;
  latestAssistantKey: string;
  turnIndex?: number;
} & MessageActions) {
  const userTurn = record(group.user_turn);
  const assistantTurns = records(group.assistant_turns);
  const executionTurns = records(group.execution_turns);
  const contextTurns = records(group.context_turns);
  const otherTurns = records(group.other_turns);
  const returnRecords = records(group.return_records);
  const turnTrace = record(group.turn_trace);
  const hasAssistantWork = assistantTurns.length
    || executionTurns.length
    || contextTurns.length
    || otherTurns.length
    || returnRecords.length
    || records(turnTrace.events).length;
  return (
    <article
      className={`ion-codex-turn-group${group.pending || group.pending_client_turn ? ' is-pending' : ''}${group.pending_status ? ` is-${safeClass(group.pending_status)}` : ''}`}
      data-turn-index={typeof turnIndex === 'number' ? turnIndex : undefined}
    >
      {userTurn.message ? (
        <Message
          role="operator"
          time={userTurn.created_at}
          text={userTurn.message}
          turn={userTurn}
          latestAssistantKey={latestAssistantKey}
          onBranch={onBranch}
          onCopy={onCopy}
          onPin={onPin}
          onQuote={onQuote}
          onRun={onRun}
        />
      ) : null}
      {hasAssistantWork ? (
        <AssistantWorkPanel
          assistantTurns={assistantTurns}
          contextTurns={contextTurns}
          executionTurns={executionTurns}
          latestAssistantKey={latestAssistantKey}
          onBranch={onBranch}
          onCopy={onCopy}
          onPin={onPin}
          onQuote={onQuote}
          onRun={onRun}
          otherTurns={otherTurns}
          returnRecords={returnRecords}
          turnTrace={turnTrace}
          userTurn={userTurn}
        />
      ) : null}
    </article>
  );
}

type AssistantWorkTabId = 'assistant' | 'thinking' | 'tools' | 'context' | 'edits' | 'runs' | 'proof' | 'agents' | 'events' | 'raw';

function AssistantWorkPanel({
  assistantTurns,
  executionTurns,
  contextTurns,
  otherTurns,
  returnRecords,
  turnTrace,
  userTurn,
  latestAssistantKey,
  onBranch,
  onCopy,
  onQuote,
  onRun,
  onPin,
}: {
  assistantTurns: Array<Record<string, unknown>>;
  executionTurns: Array<Record<string, unknown>>;
  contextTurns: Array<Record<string, unknown>>;
  otherTurns: Array<Record<string, unknown>>;
  returnRecords: Array<Record<string, unknown>>;
  turnTrace: Record<string, unknown>;
  userTurn: Record<string, unknown>;
  latestAssistantKey: string;
} & MessageActions) {
  const traceEvents = records(turnTrace.events);
  const toolEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'tools');
  const contextEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'context');
  const agentEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'agents');
  const generalEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'events');
  const editRecords = assistantEditRecords(returnRecords, traceEvents);
  const thinkingRecords = assistantThinkingRecords({ assistantTurns, traceEvents, turnTrace, userTurn });
  const runRecords = assistantRunRecords({ assistantTurns, executionTurns, traceEvents });
  const proofRecords = assistantProofRecords(returnRecords, traceEvents);
  const rawRecords = assistantRawDataRecords({ assistantTurns, contextTurns, executionTurns, otherTurns, returnRecords, traceEvents, turnTrace, userTurn });
  const tabs = assistantWorkTabs({
    assistantCount: assistantTurns.length,
    thinkingCount: thinkingRecords.length,
    toolCount: toolEvents.length + executionTurns.length,
    contextCount: contextEvents.length + contextTurns.length,
    eventCount: generalEvents.length + otherTurns.length,
    editCount: editRecords.length,
    runCount: runRecords.length,
    proofCount: proofRecords.length,
    agentCount: agentEvents.length,
    rawCount: rawRecords.length,
  });
  const defaultTab = tabs[0]?.id ?? 'assistant';
  const [activeTab, setActiveTab] = useState<AssistantWorkTabId>(defaultTab);
  useEffect(() => {
    if (!tabs.some((tab) => tab.id === activeTab)) setActiveTab(defaultTab);
  }, [activeTab, defaultTab, tabs]);
  const assistantText = assistantTurns
    .map((turn) => text(turn.message || record(turn.chat_engine).assistant_response, ''))
    .filter(Boolean)
    .join('\n\n');
  const fullPanelText = assistantWorkPanelCopyText({
    agentEvents,
    assistantTurns,
    contextEvents,
    contextTurns,
    editRecords,
    executionTurns,
    generalEvents,
    otherTurns,
    proofRecords,
    rawRecords,
    runRecords,
    thinkingRecords,
    toolEvents,
    traceEvents,
    turnTrace,
  });
  const primaryText = fullPanelText || assistantText || assistantPanelSummary({ executionTurns, contextTurns, otherTurns, returnRecords, traceEvents });
  const sourceTurnId = assistantTurns[assistantTurns.length - 1]?.turn_id || userTurn.turn_id || turnTrace.turn_id;
  const latestTime = text(
    assistantTurns[assistantTurns.length - 1]?.created_at
    || executionTurns[executionTurns.length - 1]?.created_at
    || contextTurns[contextTurns.length - 1]?.created_at
    || userTurn.created_at,
    '',
  );
  return (
    <section className="ion-codex-assistant-work-panel">
      <div className="ion-codex-work-tabbar">
        <div className="ion-codex-work-tabs" role="tablist" aria-label="Assistant work detail tabs">
          {tabs.map((tab) => (
            <button
              className={activeTab === tab.id ? 'is-active' : undefined}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              type="button"
            >
              <span>{tab.label}</span>
              <b>{tab.count}</b>
            </button>
          ))}
        </div>
        <div className="ion-codex-work-tab-actions">
          <MessageActionButtons
            iconOnly
            message={primaryText}
            payloadLabel="assistant work block"
            onBranch={() => onBranch({
              kind: 'current_turn',
              title: 'Branch: assistant work',
              objective: primaryText,
              turnId: sourceTurnId,
              role: 'assistant',
              message: primaryText,
              messageSha256: text(assistantTurns[assistantTurns.length - 1]?.message_sha256, ''),
            })}
            onCopy={onCopy}
            onPin={() => onPin(primaryText, sourceTurnId)}
            onQuote={onQuote}
            onRun={onRun}
          />
          <time>{latestTime}</time>
        </div>
      </div>
      <div className="ion-codex-work-body">
        {activeTab === 'assistant' ? (
          assistantTurns.length ? assistantTurns.map((turn, index) => (
            <Message
              key={`assistant-${index}`}
              latestAssistantKey={latestAssistantKey}
              onBranch={onBranch}
              onCopy={onCopy}
              onPin={onPin}
              onQuote={onQuote}
              onRun={onRun}
              role={text(turn.author, 'assistant')}
              text={turn.message || record(turn.chat_engine).assistant_response}
              time={turn.created_at}
              turn={turn}
            />
          )) : <AssistantEventList emptyLabel="NO DIRECT ASSISTANT MESSAGE YET" records={[]} />
        ) : null}
        {activeTab === 'tools' ? (
          <AssistantEventList
            emptyLabel="NO TOOL OR RUNNER EVENTS"
            records={[
              ...executionTurns.map(executionTurnEvent),
              ...toolEvents,
            ]}
          />
        ) : null}
        {activeTab === 'thinking' ? (
          <AssistantEventList emptyLabel="NO THINKING TELEMETRY" records={thinkingRecords} />
        ) : null}
        {activeTab === 'context' ? (
          <AssistantEventList
            emptyLabel="NO CONTEXT EVENTS"
            records={[
              ...contextTurns.map(contextTurnEvent),
              ...contextEvents,
            ]}
          />
        ) : null}
        {activeTab === 'events' ? (
          <AssistantEventList
            emptyLabel="NO ADDITIONAL EVENTS"
            records={[
              ...generalEvents,
              ...otherTurns.map(otherTurnEvent),
            ]}
          />
        ) : null}
        {activeTab === 'edits' ? (
          <AssistantEventList emptyLabel="NO FILE OR PROOF RECORDS" records={editRecords} />
        ) : null}
        {activeTab === 'runs' ? (
          <AssistantEventList emptyLabel="NO RESPONSE RUNS" records={runRecords} />
        ) : null}
        {activeTab === 'proof' ? (
          <AssistantEventList emptyLabel="NO PROOF OR RETURN RECORDS" records={proofRecords} />
        ) : null}
        {activeTab === 'agents' ? (
          <AssistantEventList emptyLabel="NO AGENT ROUTE EVENTS" records={agentEvents} />
        ) : null}
        {activeTab === 'raw' ? (
          <AssistantRawDataPanel records={rawRecords} />
        ) : null}
      </div>
    </section>
  );
}

function AssistantEventList({ records: eventRecords, emptyLabel }: { records: Array<Record<string, unknown>>; emptyLabel: string }) {
  return (
    <div className="ion-codex-work-event-stack">
      {eventRecords.map((event, index) => <AssistantEventCard event={event} key={`${assistantEventTitle(event)}-${index}`} />)}
      {eventRecords.length === 0 ? <div className="ion-empty-state">{emptyLabel}</div> : null}
    </div>
  );
}

function AssistantEventCard({ event }: { event: Record<string, unknown> }) {
  const title = assistantEventTitle(event);
  const status = text(event.status || event.verdict || event.proof_status || event.queue_status || event.result, '');
  const detail = text(event.detail || event.message || event.summary || event.finding || event.path || event.packet_path || event.latest_return_path, '');
  const refs = uniqueStrings([
    ...stringList(event.source_refs),
    ...stringList(event.path_refs),
    text(event.path || event.packet_path || event.latest_return_path || event.latest_run_path || event.session_path, ''),
  ]).slice(0, 8);
  const modelMove = record(event.model_move || event.codex_model_move);
  const diffStats = record(event.diff_stats);
  const touchedPaths = uniqueStrings([
    ...stringList(event.touched_paths),
    ...stringList(diffStats.files),
  ]).slice(0, 12);
  return (
    <div className={`ion-codex-work-event is-${safeClass(text(event.event_type || event.kind || event.type || 'event', 'event'))}`}>
      <div>
        <span>{title}</span>
        {status ? <b>{status}</b> : null}
      </div>
      {detail ? <p>{compactEventDetail(detail)}</p> : null}
      {touchedPaths.length ? <DetailChipRow values={touchedPaths} /> : null}
      {refs.length ? <DetailChipRow values={refs} /> : null}
      {Object.keys(modelMove).length ? <AssistantModelMoveDetail modelMove={modelMove} /> : null}
      {event.tool_name ? <code>{text(event.tool_name)}</code> : null}
    </div>
  );
}

function AssistantModelMoveDetail({ modelMove }: { modelMove: Record<string, unknown> }) {
  const selectionReasons = stringList(modelMove.selection_reason).slice(0, 8);
  const claimBoundary = stringList(modelMove.claim_boundary).slice(0, 6);
  const commandPreview = stringList(modelMove.command_preview).join(' ');
  return (
    <div className="ion-codex-model-move">
      <div className="ion-codex-detail-strip">
        <span>{text(modelMove.selected_model, 'model unknown')}</span>
        <span>thinking {text(modelMove.selected_reasoning_effort, 'unknown')}</span>
        <span>{text(modelMove.work_class, 'work class unknown')}</span>
        <span>{text(modelMove.ion_stage_id, 'stage unknown')}</span>
        <span>{text(modelMove.usage_pool_authority, 'not authoritative')}</span>
      </div>
      {selectionReasons.length ? <DetailChipRow values={selectionReasons} /> : null}
      {claimBoundary.length ? <DetailChipRow values={claimBoundary} /> : null}
      {commandPreview ? <code>{commandPreview}</code> : null}
    </div>
  );
}

function AssistantRawDataPanel({ records: rawRecords }: { records: Array<Record<string, unknown>> }) {
  return (
    <div className="ion-codex-raw-data-stack">
      {rawRecords.map((item, index) => (
        <article className="ion-codex-raw-data-card" key={`${text(item.label || item.event_type || item.kind, 'raw')}-${index}`}>
          <div>
            <span>{text(item.label || item.event_type || item.kind, `raw-${index + 1}`)}</span>
            <b>{text(item.status || item.schema_id || item.kind, 'json')}</b>
          </div>
          <pre>{safeJsonPreview(item.payload ?? item)}</pre>
        </article>
      ))}
      {rawRecords.length === 0 ? <div className="ion-empty-state">NO RAW SAFE DATA</div> : null}
    </div>
  );
}

function ArchiveWorkPanel({
  block,
  latestAssistantKey,
  onBranch,
  onCopy,
  onPin,
  onQuote,
  onRun,
}: {
  block: Extract<ArchiveTranscriptBlock, { kind: 'work' }>;
  latestAssistantKey: string;
  onBranch: (message: string, role: string) => void;
  onCopy: (value: unknown) => void | Promise<void>;
  onQuote: (value: unknown) => void;
  onRun: (value: unknown) => void;
  onPin: (value: unknown) => void | Promise<void>;
}) {
  const tabs = assistantWorkTabs({
    assistantCount: block.assistantItems.length,
    thinkingCount: block.thinkingItems.length,
    toolCount: block.toolItems.length,
    contextCount: block.contextItems.length,
    eventCount: block.eventItems.length,
    editCount: block.editItems.length,
    runCount: block.runItems.length,
    proofCount: block.proofItems.length,
    agentCount: 0,
    rawCount: block.rawItems.length,
  }).filter((tab) => tab.id !== 'agents');
  const defaultTab = tabs[0]?.id ?? 'assistant';
  const [activeTab, setActiveTab] = useState<AssistantWorkTabId>(defaultTab);
  useEffect(() => {
    if (!tabs.some((tab) => tab.id === activeTab)) setActiveTab(defaultTab);
  }, [activeTab, defaultTab, tabs]);
  const activeItems = archiveWorkItemsForTab(block, activeTab);
  const primaryText = archiveWorkPanelCopyText(block) || 'archived assistant work';
  return (
    <section className="ion-codex-assistant-work-panel is-archive-work">
      <div className="ion-codex-work-tabbar">
        <div className="ion-codex-work-tabs" role="tablist" aria-label="Archived assistant work detail tabs">
          {tabs.map((tab) => (
            <button
              className={activeTab === tab.id ? 'is-active' : undefined}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              type="button"
            >
              <span>{tab.label}</span>
              <b>{tab.count}</b>
            </button>
          ))}
        </div>
        <div className="ion-codex-work-tab-actions">
          <MessageActionButtons
            iconOnly
            message={primaryText}
            payloadLabel="archived work block"
            onBranch={() => onBranch(primaryText, 'assistant')}
            onCopy={onCopy}
            onPin={() => onPin(primaryText)}
            onQuote={onQuote}
            onRun={onRun}
          />
          <time>{text(block.items[block.items.length - 1]?.timestamp, '')}</time>
        </div>
      </div>
      <div className="ion-codex-work-body">
        {activeTab === 'assistant' ? (
          block.assistantItems.length ? block.assistantItems.map((item, index) => {
            const role = text(item.role, 'assistant');
            const message = archiveItemText(item);
            return (
              <Message
                key={`${archiveMessageKey(item, index)}-assistant-message`}
                latestAssistantKey={latestAssistantKey}
                onBranch={(source) => onBranch(text(source.message || source.objective, message), text(source.role, role))}
                onCopy={onCopy}
                onPin={(value) => onPin(value)}
                onQuote={onQuote}
                onRun={onRun}
                role={role}
                text={message}
                time={item.timestamp}
                turn={{ ...item, turn_id: archiveItemSourceKey(item) }}
              />
            );
          }) : <AssistantEventList emptyLabel="NO DIRECT ASSISTANT MESSAGE" records={[]} />
        ) : (
          <div className="ion-codex-work-event-stack">
            {activeItems.map((item, index) => (
              <ArchiveWorkItemCard item={item} key={`${archiveMessageKey(item, index)}-${activeTab}`} />
            ))}
            {activeItems.length === 0 ? <div className="ion-empty-state">NO ITEMS</div> : null}
          </div>
        )}
      </div>
    </section>
  );
}

function ArchiveWorkItemCard({ item }: { item: Record<string, unknown> }) {
  const role = text(item.role, 'archive');
  const message = archiveItemText(item);
  const roleGroup = archiveMessageRoleGroup(item, role);
  const refs = uniqueStrings([
    ...stringList(item.path_refs),
    ...stringList(item.context_refs),
    ...stringList(record(item.diff_stats).files),
  ]).slice(0, 8);
  const modelMove = record(item.model_move || item.codex_model_move);
  return (
    <div className={`ion-codex-work-event is-${safeClass(text(item.message_kind || role, 'event'))}`}>
      <div>
        <span>{archiveMessageLabel(item, role, roleGroup)}</span>
        <b>{text(item.detail_label || item.source_type, '')}</b>
      </div>
      {roleGroup === 'diff' ? <ArchiveDiffDetail item={item} message={message} /> : null}
      {roleGroup === 'context' ? <ArchiveContextDetail item={item} message={message} /> : null}
      {roleGroup === 'compaction' ? <ArchiveCompactionDetail item={item} message={message} /> : null}
      {!['diff', 'context', 'compaction'].includes(roleGroup) ? <p>{message}</p> : null}
      {refs.length ? <DetailChipRow values={refs} /> : null}
      {Object.keys(modelMove).length ? <AssistantModelMoveDetail modelMove={modelMove} /> : null}
    </div>
  );
}

function Message({
  role,
  time,
  text: value,
  turn,
  latestAssistantKey,
  onBranch,
  onCopy,
  onQuote,
  onRun,
  onPin,
}: {
  role: string;
  time: unknown;
  text: unknown;
  turn?: Record<string, unknown>;
  latestAssistantKey: string;
} & MessageActions) {
  const message = text(value, '');
  const sourceTurnId = turn?.turn_id || turn?.id || turn?.event_id || turn?.attachment_id || time;
  const sourceKey = messageSourceKey(turn, time);
  const roleGroup = messageRoleGroup(role);
  const defaultExpanded = latestAssistantKey === sourceKey && roleGroup === 'ai';
  const [expanded, setExpanded] = useState(defaultExpanded);
  const displayMessage = expanded ? message : compactNonDirectMessage(role, message, turn, roleGroup);
  useEffect(() => {
    if (defaultExpanded) setExpanded(true);
  }, [defaultExpanded]);
  const actionButtons = (
    <MessageActionButtons
      expanded={expanded}
      iconOnly={roleGroup === 'ai'}
      message={message}
      onBranch={() => onBranch({
        kind: 'current_turn',
        title: `Branch: ${role}`,
        objective: message,
        turnId: sourceTurnId,
        role,
        message,
        messageSha256: text(turn?.message_sha256, ''),
      })}
      onCopy={onCopy}
      onPin={() => onPin(message, sourceTurnId)}
      onQuote={onQuote}
      onRun={onRun}
      onToggleExpand={() => setExpanded((previous) => !previous)}
    />
  );
  return (
    <div className={`ion-codex-message is-${safeClass(role)} is-${roleGroup}${expanded ? ' is-expanded' : ' is-compact'}`} onClick={() => setExpanded((previous) => !previous)}>
      <div className="ion-codex-message-head">
        <div className="ion-codex-message-title">
          <span>{messageRoleLabel(role, roleGroup)}</span>
          {roleGroup !== 'ai' ? <time>{text(time, '')}</time> : null}
        </div>
        {roleGroup === 'ai' ? (
          <div className="ion-codex-message-head-actions">
            {actionButtons}
            <time>{text(time, '')}</time>
          </div>
        ) : actionButtons}
      </div>
      <div className={`ion-codex-message-content is-${safeClass(role)} is-${roleGroup} ${expanded ? 'is-expanded' : 'is-compact'}`}>
        <p>{displayMessage}</p>
      </div>
    </div>
  );
}

function ArchiveMessage({
  item,
  onBranch,
  onCopy,
  onPin,
  onQuote,
  onRun,
}: {
  item: Record<string, unknown>;
  onBranch: (message: string, role: string) => void;
  onCopy: (value: unknown) => void | Promise<void>;
  onQuote: (value: unknown) => void;
  onRun: (value: unknown) => void;
  onPin: (value: unknown) => void | Promise<void>;
}) {
  const role = text(item.role, 'archive');
  const message = text(item.text || item.snippet, '');
  const roleGroup = archiveMessageRoleGroup(item, role);
  const [expanded, setExpanded] = useState(roleGroup === 'ai');
  const displayMessage = expanded ? message : compactNonDirectMessage(role, message, item, roleGroup);
  const actionButtons = (
    <MessageActionButtons
      expanded={expanded}
      iconOnly={roleGroup === 'ai'}
      message={message}
      onBranch={() => onBranch(message, role)}
      onCopy={onCopy}
      onPin={() => onPin(message)}
      onQuote={onQuote}
      onRun={onRun}
      onToggleExpand={() => setExpanded((previous) => !previous)}
    />
  );
  return (
    <article className={`ion-codex-message is-${safeClass(role)} is-${roleGroup}${expanded ? ' is-expanded' : ' is-compact'}`} onClick={() => setExpanded((previous) => !previous)}>
      <div className="ion-codex-message-head">
        <div className="ion-codex-message-title">
          <span>{archiveMessageLabel(item, role, roleGroup)}</span>
          {roleGroup !== 'ai' ? <time>{text(item.timestamp, '')}</time> : null}
        </div>
        {roleGroup === 'ai' ? (
          <div className="ion-codex-message-head-actions">
            {actionButtons}
            <time>{text(item.timestamp, '')}</time>
          </div>
        ) : actionButtons}
      </div>
      <ArchiveMessageBody displayMessage={displayMessage} expanded={expanded} item={item} message={message} role={role} roleGroup={roleGroup} />
    </article>
  );
}

type MessageActionIconName = 'expand' | 'compact' | 'copy' | 'quote' | 'run' | 'pin' | 'branch';

function MessageActionButtons({
  expanded,
  iconOnly = false,
  message,
  payloadLabel = 'message',
  onBranch,
  onCopy,
  onPin,
  onQuote,
  onRun,
  onToggleExpand,
}: {
  expanded?: boolean;
  iconOnly?: boolean;
  message: string;
  payloadLabel?: string;
  onBranch: () => void;
  onCopy: (value: unknown) => void | Promise<void>;
  onPin: () => void | Promise<void>;
  onQuote: (value: unknown) => void;
  onRun: (value: unknown) => void;
  onToggleExpand?: () => void;
}) {
  const payloadSize = formatPayloadSize(message);
  const payloadHint = `${payloadLabel} / ${payloadSize}`;
  const buttons: Array<{
    icon: MessageActionIconName;
    label: string;
    onClick: () => void | Promise<void>;
    text: string;
  }> = [
    ...(onToggleExpand ? [{
      icon: expanded ? 'compact' as const : 'expand' as const,
      label: expanded ? 'Compact message' : 'Expand message',
      onClick: onToggleExpand,
      text: expanded ? 'COMPACT' : 'EXPAND',
    }] : []),
    { icon: 'copy', label: `Copy ${payloadHint}`, onClick: () => onCopy(message), text: 'COPY' },
    { icon: 'quote', label: `Quote ${payloadHint}`, onClick: () => onQuote(message), text: 'QUOTE' },
    { icon: 'run', label: `Run ${payloadHint}`, onClick: () => onRun(message), text: 'RUN' },
    { icon: 'pin', label: `Pin ${payloadHint}`, onClick: onPin, text: 'PIN' },
    { icon: 'branch', label: `Branch ${payloadHint}`, onClick: onBranch, text: 'BRANCH' },
  ];
  return (
    <div className={`ion-codex-message-actions is-inline${iconOnly ? ' is-icon-row' : ''}`} onClick={(event) => event.stopPropagation()}>
      {buttons.map((button) => (
        <button aria-label={button.label} key={button.label} onClick={() => { void button.onClick(); }} title={button.label} type="button">
          {iconOnly ? <MessageActionIcon name={button.icon} /> : button.text}
        </button>
      ))}
    </div>
  );
}

function MessageActionIcon({ name }: { name: MessageActionIconName }) {
  return (
    <svg aria-hidden="true" focusable="false" viewBox="0 0 20 20">
      {name === 'expand' ? (
        <>
          <path d="M8 4H4v4" />
          <path d="M4 4l5 5" />
          <path d="M12 16h4v-4" />
          <path d="M16 16l-5-5" />
        </>
      ) : null}
      {name === 'compact' ? (
        <>
          <path d="M4 9h5V4" />
          <path d="M9 9L4 4" />
          <path d="M16 11h-5v5" />
          <path d="M11 11l5 5" />
        </>
      ) : null}
      {name === 'copy' ? (
        <>
          <path d="M7 7h9v9H7z" />
          <path d="M4 13V4h9" />
        </>
      ) : null}
      {name === 'quote' ? (
        <>
          <path d="M8 8h3v6H6v-4c0-3 2-5 5-6" />
          <path d="M15 8h3v6h-5v-4c0-3 2-5 5-6" />
        </>
      ) : null}
      {name === 'run' ? <path d="M7 4l10 6-10 6z" /> : null}
      {name === 'pin' ? <path d="M7 4h6l-1 5 3 3v1h-5l-3 4v-4H5v-1l3-3z" /> : null}
      {name === 'branch' ? (
        <>
          <path d="M5 4v5a5 5 0 0 0 5 5h5" />
          <path d="M10 14a5 5 0 0 0 5-5V4" />
          <path d="M13 6l2-2 2 2" />
        </>
      ) : null}
    </svg>
  );
}

function ArchiveMessageBody({
  displayMessage,
  expanded,
  item,
  message,
  role,
  roleGroup,
}: {
  displayMessage: string;
  expanded: boolean;
  item: Record<string, unknown>;
  message: string;
  role: string;
  roleGroup: string;
}) {
  const messageKind = text(item.message_kind, '');
  if (!expanded) {
    return (
      <div className={`ion-codex-message-content is-${safeClass(role)} is-${roleGroup} is-compact`}>
        <p>{displayMessage}</p>
      </div>
    );
  }
  if (roleGroup === 'diff' || ['diff', 'file_edit'].includes(messageKind)) {
    return (
      <div className={`ion-codex-message-content is-${safeClass(role)} is-${roleGroup} is-expanded`}>
        <ArchiveDiffDetail item={item} message={message} />
      </div>
    );
  }
  if (roleGroup === 'context' || messageKind === 'capsule_context') {
    return (
      <div className={`ion-codex-message-content is-${safeClass(role)} is-${roleGroup} is-expanded`}>
        <ArchiveContextDetail item={item} message={message} />
      </div>
    );
  }
  if (roleGroup === 'compaction' || ['compaction', 'truncated'].includes(messageKind)) {
    return (
      <div className={`ion-codex-message-content is-${safeClass(role)} is-${roleGroup} is-expanded`}>
        <ArchiveCompactionDetail item={item} message={message} />
      </div>
    );
  }
  return (
    <div className={`ion-codex-message-content is-${safeClass(role)} is-${roleGroup} is-expanded`}>
      <p>{message}</p>
    </div>
  );
}

function ArchiveDiffDetail({ item, message }: { item: Record<string, unknown>; message: string }) {
  const stats = record(item.diff_stats);
  const files = uniqueStrings([...stringList(stats.files), ...stringList(item.path_refs)]).slice(0, 8);
  const added = numberValue(stats.added_lines);
  const removed = numberValue(stats.removed_lines);
  return (
    <div className="ion-codex-message-detail is-diff-detail">
      <div className="ion-codex-detail-strip">
        <span>FILES {files.length || numberValue(stats.file_count)}</span>
        <span>+{added}</span>
        <span>-{removed}</span>
        <span>{text(item.detail_label, 'file evidence')}</span>
        <span>DIFF EVIDENCE</span>
      </div>
      {files.length ? <DetailChipRow values={files} /> : null}
      <pre className="ion-codex-diff-block">
        {message.split('\n').map((line, index) => (
          <span className={diffLineClass(line)} key={`${index}-${line.slice(0, 24)}`}>{line || ' '}</span>
        ))}
      </pre>
    </div>
  );
}

function ArchiveContextDetail({ item, message }: { item: Record<string, unknown>; message: string }) {
  const refs = uniqueStrings([...stringList(item.context_refs), ...stringList(item.path_refs)]).slice(0, 10);
  const markers = uniqueStrings(stringList(item.compaction_markers)).slice(0, 8);
  return (
    <div className="ion-codex-message-detail is-context-detail">
      <div className="ion-codex-detail-strip">
        <span>{text(item.detail_label, 'context')}</span>
        <span>REFS {refs.length}</span>
        {markers.map((marker) => <span key={marker}>{marker}</span>)}
      </div>
      {refs.length ? <DetailChipRow values={refs} /> : null}
      <pre className="ion-codex-context-block">{message}</pre>
    </div>
  );
}

function ArchiveCompactionDetail({ item, message }: { item: Record<string, unknown>; message: string }) {
  const refs = uniqueStrings([...stringList(item.context_refs), ...stringList(item.path_refs)]).slice(0, 10);
  const markers = uniqueStrings(stringList(item.compaction_markers)).slice(0, 8);
  return (
    <div className="ion-codex-message-detail is-compaction-detail">
      <div className="ion-codex-detail-strip">
        <span>{text(item.detail_label, 'context boundary')}</span>
        {item.synthetic ? <span>HOOK RECEIPT</span> : null}
        {markers.length ? markers.map((marker) => <span key={marker}>{marker}</span>) : <span>BOUNDARY</span>}
      </div>
      {refs.length ? <DetailChipRow values={refs} /> : null}
      <pre className="ion-codex-context-block">{message}</pre>
    </div>
  );
}

function DetailChipRow({ values }: { values: string[] }) {
  return (
    <div className="ion-codex-detail-chip-row">
      {values.map((value) => <code key={value}>{value}</code>)}
    </div>
  );
}

function ContextPill({ label, value }: { label: string; value: unknown }) {
  return (
    <span className="ion-codex-context-pill">
      <b>{text(value)}</b>
      <small>{label}</small>
    </span>
  );
}

function CommandButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button className="ion-codex-command-button" onClick={onClick} type="button">
      {label}
    </button>
  );
}

function Metric({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-runtime-metric">
      <span>{label}</span>
      <b>{text(value)}</b>
    </div>
  );
}

function DrawerTitle({ title, value }: { title: string; value: unknown }) {
  return <div className="ion-codex-drawer-title"><span>{title}</span><b>{text(value)}</b></div>;
}

function PathChip({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-codex-path-chip">
      <span>{label}</span>
      <code>{text(value, '')}</code>
    </div>
  );
}

function DataBlock({ title, rows, compact = false }: { title: string; rows: Array<[string, unknown]>; compact?: boolean }) {
  return (
    <div className={`ion-runtime-card ion-codex-data-block${compact ? ' is-compact' : ''}`}>
      <div className="ion-runtime-card-head"><span>{title}</span><b>{rows.length}</b></div>
      <div className="ion-codex-data-rows">
        {rows.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <b>{text(value)}</b>
          </div>
        ))}
      </div>
    </div>
  );
}

function RecordPanel({
  title,
  records: sourceRecords,
  compact = false,
}: {
  title: string;
  records?: Array<Record<string, unknown>>;
  compact?: boolean;
}) {
  const items = sourceRecords ?? [];
  return (
    <div className={`ion-runtime-card ion-codex-record-panel${compact ? ' is-compact' : ''}`}>
      <div className="ion-runtime-card-head"><span>{title}</span><b>{items.length}</b></div>
      <div className="ion-codex-record-stack">
        {items.map((item, index) => (
          <div className="ion-codex-record" key={`${title}-${text(item.id || item.name || item.path || item.run_id || item.attachment_id || item.session_id || index)}`}>
            <b>{text(item.thread_name || item.name || item.id || item.run_id || item.attachment_id || item.session_id || item.status || item.path, `item-${index + 1}`)}</b>
            <span>{text(item.status || item.verdict || item.role || item.mode || item.updated_at || item.created_at, '')}</span>
            <code>{text(item.path || item.session_path || item.latest_return_path || item.cwd || item.error, '')}</code>
          </div>
        ))}
        {items.length === 0 && <div className="ion-empty-state">NONE</div>}
      </div>
    </div>
  );
}

function JsonPanel({ title, value }: { title: string; value: unknown }) {
  return (
    <div className="ion-runtime-card ion-codex-json-panel">
      <div className="ion-runtime-card-head"><span>{title}</span><b>json</b></div>
      <pre>{JSON.stringify(value ?? {}, null, 2)}</pre>
    </div>
  );
}

function surfaceChangeForEvent(event: Record<string, unknown> | undefined, surfaceId: string) {
  if (!event || !surfaceId) return null;
  return records(event.surface_changes).find((change) => text(change.surface_id, '') === surfaceId) ?? null;
}

function rowByLabel(rows: Array<Record<string, unknown>>, label: string) {
  return rows.find((row) => text(row.label, '') === label) ?? {};
}

function agentRecordId(agent: Record<string, unknown>) {
  return text(agent.role_id || agent.agent_id || agent.participant_id || agent.display_name, '');
}

function formatContextTime(value: unknown) {
  const raw = text(value, '');
  if (!raw) return 'unknown time';
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function filterSessions(sessions: IonCodexConversationArchiveSession[], query: string) {
  const needle = query.trim().toLowerCase();
  if (!needle) return sessions;
  return sessions.filter((session) => (
    [
      session.session_id,
      session.thread_name,
      session.display_title,
      session.cwd,
      session.project_label,
      session.project_key,
      session.model,
      session.first_user_snippet,
      session.latest_user_snippet,
      session.latest_assistant_snippet,
      sessionAgentLabel(session),
      sessionCarrierLabel(session),
      sessionContextLabel(session),
      ...records(session.mission_labels).map((label) => `${text(label.label, '')} ${text(label.source, '')} ${text(label.confidence, '')}`),
      ...records(session.agent_labels).map((label) => `${text(label.label, '')} ${text(label.source, '')} ${text(label.confidence, '')}`),
      ...records(session.tool_summary).map((tool) => text(tool.name, '')),
    ].join(' ').toLowerCase().includes(needle)
  ));
}

function uniqueSessionsById(sessions: Array<IonCodexConversationArchiveSession | null | undefined>) {
  const seen = new Set<string>();
  const unique: IonCodexConversationArchiveSession[] = [];
  for (const session of sessions) {
    const sessionId = text(session?.session_id, '');
    if (!sessionId || seen.has(sessionId)) continue;
    seen.add(sessionId);
    unique.push(session);
  }
  return unique;
}

function primaryAgentLabel(session: IonCodexConversationArchiveSession) {
  return sessionAgentLabel(session);
}

function sessionAgentLabel(session: IonCodexConversationArchiveSession) {
  const labels = records(session.agent_labels);
  const preferred = labels.find((label) => {
    const source = text(label.source, '').toLowerCase();
    const value = text(label.label, '');
    return Boolean(value) && (
      source.includes('selected')
      || source.includes('active')
      || source.includes('suggested_skill')
      || source.includes('specialist')
      || source.includes('context_system')
      || source.includes('agent_identity')
    );
  }) ?? labels.find((label) => {
    const source = text(label.source, '').toLowerCase();
    const value = text(label.label, '');
    return Boolean(value) && source.includes('suggested_domain');
  }) ?? labels.find((label) => {
    const value = text(label.label, '');
    return Boolean(value) && !genericArchiveAgentLabel(value);
  });
  const fallback = labels.find((label) => text(label.label, '')) ?? {};
  return compactClassificationLabel(preferred?.label || fallback.label || session.project_label || 'agent unknown', 'agent unknown');
}

function sessionCarrierLabel(session: IonCodexConversationArchiveSession) {
  const carrier = records(session.agent_labels).find((label) => text(label.source, '').toLowerCase() === 'carrier');
  return compactClassificationLabel(carrier?.label || session.model || 'carrier unknown', 'carrier unknown');
}

function sessionContextLabel(session: IonCodexConversationArchiveSession) {
  if (isQueueRunnerPacket(session)) return 'queue packet context';
  const binding = record((session as unknown as Record<string, unknown>).chat_context_binding);
  const contextSystem = record(binding.context_system);
  const agentIdentity = record(binding.agent_identity);
  const minimumContext = record(binding.minimum_context);
  const missionLabels = records(session.mission_labels);
  const contextValue = text(
    contextSystem.default_active_package_class
    || contextSystem.package_class
    || contextSystem.package_strategy
    || binding.default_active_package_class
    || binding.package_class
    || binding.context_type
    || binding.domain_id
    || agentIdentity.domain_id
    || missionLabels[0]?.label
    || minimumContext.capsule_ref
    || session.project_label,
    'context unknown',
  );
  return compactClassificationLabel(readableContextLabel(contextValue), 'context unknown');
}

function genericArchiveAgentLabel(value: unknown) {
  const normalized = text(value, '').toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  return [
    'codex',
    'codex_cli',
    'persona',
    'relay',
    'steward',
    'vizier',
    'mason',
    'nemesis',
    'scribe',
    'developer',
    'function_call_output',
    'custom_tool_call_output',
    'tool_using_codex',
  ].includes(normalized) || normalized.startsWith('gpt_');
}

function readableContextLabel(value: unknown) {
  const raw = text(value, 'context unknown').replace(/\s+/g, ' ').trim();
  if (/^maintain the primary codex capsule chat profile/i.test(raw)) return 'Codex Capsule Profile';
  if (/^build domain weaver into a codex cli/i.test(raw)) return 'Domain Weaver Stewarded Autonomy';
  if (/domain_weaver_stewarded_autonomy/i.test(raw)) return 'Domain Weaver Stewarded Autonomy';
  if (/^PCKT-DOMAIN-WEAVER/i.test(raw)) {
    const parts = raw.split(/[-\s]+/).filter(Boolean);
    return parts.slice(0, 5).join(' ');
  }
  return raw;
}

function compactClassificationLabel(value: unknown, fallback: string) {
  const normalized = text(value, fallback)
    .replace(/[_/]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (!normalized) return fallback;
  return normalized.length > 58 ? `${normalized.slice(0, 55)}...` : normalized;
}

function sessionMatchesIdLookup(session: IonCodexConversationArchiveSession, needle: string) {
  if (!needle) return true;
  const haystack = [
    session.session_id,
    session.session_path,
    session.project_key,
    session.project_label,
    session.cwd,
    session.model,
    session.thread_name,
    session.display_title,
    sessionAgentLabel(session),
    sessionCarrierLabel(session),
    sessionContextLabel(session),
  ].map((value) => text(value, '')).join(' ').toLowerCase();
  return haystack.includes(needle);
}

function isQueueRunnerPacket(session: IonCodexConversationArchiveSession) {
  if (numberValue(session.history_prompt_count) !== 0) return false;
  const haystack = [
    session.thread_name,
    session.display_title,
    session.first_user_snippet,
    session.latest_user_snippet,
    session.latest_assistant_snippet,
    session.session_path,
  ].map((value) => text(value, '')).join(' ').toLowerCase();
  return (
    haystack.includes('ion codex queue runner work packet')
    || haystack.includes('queue runner work packet')
    || haystack.includes('carrier_mount')
    || haystack.includes('request_kind: "codex_work"')
    || haystack.includes("request_kind: 'codex_work'")
  );
}

function buildArchiveOverview(sessions: IonCodexConversationArchiveSession[]) {
  const sorted = sortByRecent(sessions);
  const active = [...sessions].sort((left, right) => sessionActivity(right) - sessionActivity(left) || sessionTimestamp(right) - sessionTimestamp(left));
  const projectNames = new Set(sessions.map(projectLabel).filter(Boolean));
  const modelNames = new Set(sessions.map((session) => text(session.model, '')).filter(Boolean));
  const agentNames = new Set(sessions.map(sessionAgentLabel).filter(Boolean));
  const contextNames = new Set(sessions.map(sessionContextLabel).filter(Boolean));
  const packetCount = sessions.filter(isQueueRunnerPacket).length;
  return {
    total: sessions.length,
    chatCount: sessions.length - packetCount,
    packetCount,
    today: sessions.filter((session) => ageBucket(session) === 'Today').length,
    thisWeek: sessions.filter((session) => ['Today', 'Yesterday', 'Previous 7 Days'].includes(ageBucket(session))).length,
    projectCount: projectNames.size,
    modelCount: modelNames.size,
    agentCount: agentNames.size,
    contextCount: contextNames.size,
    recent: sorted,
    active,
  };
}

function archiveGroups(view: ArchiveViewId, sessions: IonCodexConversationArchiveSession[]): ArchiveGroup[] {
  const packetSessions = sessions.filter(isQueueRunnerPacket);
  const conversationSessions = sessions.filter((session) => !isQueueRunnerPacket(session));
  if (view === 'packets') {
    return [{
      id: 'work-packets',
      title: 'Queue-Runner Work Packets',
      sessions: sortByRecent(packetSessions),
    }];
  }
  if (view === 'active') {
    return [{
      id: 'most-active',
      title: 'Most Active Chats',
      sessions: [...conversationSessions].sort((left, right) => sessionActivity(right) - sessionActivity(left) || sessionTimestamp(right) - sessionTimestamp(left)),
    }];
  }
  if (view === 'projects') {
    return groupedSessions(conversationSessions, projectLabel, true);
  }
  if (view === 'models') {
    return groupedSessions(conversationSessions, (session) => text(session.model, 'Model Unknown'), true);
  }
  const orderedBuckets = ['Today', 'Yesterday', 'Previous 7 Days', 'Older'];
  return orderedBuckets
    .map((bucket) => ({
      id: safeClass(bucket),
      title: bucket,
      sessions: sortByRecent(conversationSessions.filter((session) => ageBucket(session) === bucket)),
    }))
    .filter((group) => group.sessions.length > 0);
}

function groupedSessions(
  sessions: IonCodexConversationArchiveSession[],
  labelForSession: (session: IonCodexConversationArchiveSession) => string,
  sortByActivity = false,
): ArchiveGroup[] {
  const groups = new Map<string, IonCodexConversationArchiveSession[]>();
  for (const session of sessions) {
    const label = labelForSession(session) || 'Unknown';
    groups.set(label, [...(groups.get(label) ?? []), session]);
  }
  return [...groups.entries()]
    .map(([label, grouped]) => ({
      id: safeClass(label),
      title: label,
      sessions: sortByActivity
        ? [...grouped].sort((left, right) => sessionActivity(right) - sessionActivity(left) || sessionTimestamp(right) - sessionTimestamp(left))
        : sortByRecent(grouped),
    }))
    .sort((left, right) => right.sessions.length - left.sessions.length || left.title.localeCompare(right.title));
}

function sortByRecent(sessions: IonCodexConversationArchiveSession[]) {
  return [...sessions].sort((left, right) => sessionTimestamp(right) - sessionTimestamp(left));
}

function timestampFromValue(value: unknown) {
  const parsed = Date.parse(text(value, ''));
  return Number.isFinite(parsed) ? parsed : 0;
}

function sessionTimestamp(session: IonCodexConversationArchiveSession) {
  return timestampFromValue(session.updated_at || session.history_latest_ts || session.created_at || '');
}

function sessionFirstTimestamp(session: IonCodexConversationArchiveSession) {
  return timestampFromValue(session.created_at || '') || sessionTimestamp(session);
}

function buildChatHistoryEntries(
  sessions: IonCodexConversationArchiveSession[],
  openTabs: OpenChatTab[],
  titleOverrides: Record<string, string>,
  meta: Record<string, ChatHistoryMeta>,
  sortId: ChatHistorySortId,
): ChatHistoryEntry[] {
  const sessionById = new Map<string, IonCodexConversationArchiveSession>();
  for (const session of sessions) {
    if (session.session_id) sessionById.set(session.session_id, session);
  }
  for (const tab of openTabs) {
    if (!tab.sessionId || sessionById.has(tab.sessionId)) continue;
    const session = sessionFromOpenChatTab(tab);
    if (session) sessionById.set(tab.sessionId, session);
  }
  const tabBySessionId = new Map(openTabs.map((tab) => [tab.sessionId, tab]));
  return [...sessionById.values()]
    .map((session) => {
      const sessionId = session.session_id;
      const sessionMeta = meta[sessionId] ?? {};
      const tab = tabBySessionId.get(sessionId);
      const lastOpenedAt = sessionMeta.lastOpenedAt || tab?.lastOpenedAt || tab?.openedAt || tab?.lastViewedAt || '';
      const lastClosedAt = sessionMeta.lastClosedAt || tab?.lastClosedAt || '';
      let timestamp = sessionTimestamp(session);
      let detailLabel = 'last message';
      if (sortId === 'first_message') {
        timestamp = sessionFirstTimestamp(session);
        detailLabel = 'first message';
      } else if (sortId === 'last_opened') {
        timestamp = timestampFromValue(lastOpenedAt);
        detailLabel = 'last opened';
      } else if (sortId === 'last_closed') {
        timestamp = timestampFromValue(lastClosedAt);
        detailLabel = 'last closed';
      }
      return {
        session,
        title: text(titleOverrides[sessionId] || sessionTitle(session), sessionId),
        timestamp,
        detail: `${detailLabel} / ${formatHistoryTimestamp(timestamp)}`,
      };
    })
    .sort((left, right) => right.timestamp - left.timestamp || left.title.localeCompare(right.title));
}

function formatHistoryTimestamp(timestamp: number) {
  if (!timestamp) return 'not recorded';
  return new Date(timestamp).toLocaleString(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function ageBucket(session: IonCodexConversationArchiveSession) {
  const timestamp = sessionTimestamp(session);
  if (!timestamp) return 'Older';
  const now = new Date();
  const then = new Date(timestamp);
  const startToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const startYesterday = startToday - 24 * 60 * 60 * 1000;
  if (timestamp >= startToday) return 'Today';
  if (timestamp >= startYesterday) return 'Yesterday';
  if (now.getTime() - then.getTime() <= 7 * 24 * 60 * 60 * 1000) return 'Previous 7 Days';
  return 'Older';
}

function sessionActivity(session: IonCodexConversationArchiveSession) {
  if (typeof session.activity_score === 'number' && Number.isFinite(session.activity_score)) return session.activity_score;
  return (
    numberValue(session.history_prompt_count)
    + numberValue(session.line_count_sampled)
    + sumCounts(session.event_counts)
    + sumCounts(session.role_counts)
    + sumCounts(session.tool_counts)
  );
}

function sumCounts(counts: Record<string, number> | undefined) {
  return Object.values(counts ?? {}).reduce((total, value) => total + numberValue(value), 0);
}

function numberValue(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0;
}

function archiveVirtualMetrics(
  excerpt: IonCodexConversationArchive['selected_session_excerpt'] | null | undefined,
) {
  const displayed = numberValue(excerpt?.displayed_item_count ?? excerpt?.item_count ?? records(excerpt?.items).length);
  const total = Math.max(displayed, numberValue(excerpt?.total_displayable_items));
  const oldest = Math.max(1, numberValue(excerpt?.oldest_item_index) || 1);
  const newest = Math.max(oldest, numberValue(excerpt?.newest_item_index) || (displayed ? oldest + displayed - 1 : oldest));
  const hasOlder = Boolean(excerpt?.has_older_items) || oldest > 1;
  const hasNewer = Boolean(excerpt?.has_newer_items) || (newest > 0 && newest < total);
  const enabled = total > displayed && hasOlder && hasNewer;
  return {
    displayed,
    enabled,
    height: Math.max(total * ARCHIVE_VIRTUAL_ITEM_PX, ARCHIVE_VIRTUAL_ITEM_PX),
    newest,
    oldest,
    topOffset: Math.max(0, (oldest - 1) * ARCHIVE_VIRTUAL_ITEM_PX),
    total,
  };
}

function archiveWindowStartForDirection(
  direction: ArchiveBufferDirection,
  excerpt: IonCodexConversationArchive['selected_session_excerpt'] | null | undefined,
) {
  const total = numberValue(excerpt?.total_displayable_items);
  const oldest = numberValue(excerpt?.oldest_item_index);
  const newest = numberValue(excerpt?.newest_item_index);
  if (direction === 'older' && oldest > 1) return Math.max(1, oldest - ARCHIVE_TRANSCRIPT_CHUNK_SIZE);
  if (direction === 'newer' && newest > 0 && newest < total) return newest + 1;
  return 0;
}

function archivePrefetchKey(buffer: ArchiveTranscriptBuffer) {
  return `${buffer.sessionId}:${buffer.direction}:${buffer.startIndex}:${buffer.endIndex}:${buffer.createdAt}`;
}

function archiveRenderedItems(
  currentItems: Array<Record<string, unknown>>,
  buffer: ArchiveTranscriptBuffer | null,
  sessionId: string,
) {
  if (!buffer || buffer.sessionId !== sessionId || buffer.items.length === 0) return currentItems;
  if (buffer.direction === 'older') return [...buffer.items, ...currentItems];
  return [...currentItems, ...buffer.items];
}

function archiveMessageKey(item: Record<string, unknown>, index: number) {
  const itemIndex = numberValue(item.item_index ?? item.index ?? item.ordinal);
  if (itemIndex > 0) return `item-${itemIndex}`;
  const timestamp = text(item.timestamp, '');
  const role = text(item.role || item.kind || item.type, '');
  return `${timestamp || 'archive-item'}-${role}-${index}`;
}

function archiveConversationTurnGroups(items: Array<Record<string, unknown>>): Array<Record<string, unknown>> {
  const groups: ArchiveConversationGroup[] = [];
  let current: ArchiveConversationGroup | null = null;
  const ensureGroup = (item: Record<string, unknown>, index: number) => {
    if (current) return current;
    current = createArchiveConversationGroup(null, item, index);
    groups.push(current);
    return current;
  };
  items.forEach((item, index) => {
    const role = text(item.role, 'archive');
    const roleGroup = archiveMessageRoleGroup(item, role);
    if (roleGroup === 'user') {
      current = createArchiveConversationGroup(item, item, index);
      groups.push(current);
      return;
    }
    const group = ensureGroup(item, index);
    if (roleGroup === 'ai') {
      group.assistant_turns.push(archiveAssistantTurn(item));
    } else if (roleGroup === 'trace') {
      group.turn_trace.events.push(archiveTraceEvent(item, roleGroup));
    } else if (roleGroup === 'context' || roleGroup === 'compaction') {
      group.context_turns.push(archiveContextTurn(item, roleGroup));
    } else if (roleGroup === 'diff') {
      group.return_records.push(archiveReturnRecord(item, roleGroup));
    } else {
      group.other_turns.push(archiveOtherTurn(item, roleGroup));
    }
  });
  return groups as Array<Record<string, unknown>>;
}

function buildCodexChatTimelineModel(groups: Array<Record<string, unknown>>): CodexChatTimelineModel {
  const turnCount = groups.length;
  const frames = Math.max(
    CODEX_CHAT_TIMELINE_MIN_FRAMES,
    Math.min(CODEX_CHAT_TIMELINE_MAX_FRAMES, Math.max(1, turnCount) * 2),
  );
  const clips: CodexChatTimelineClip[] = [];
  const addClip = (
    index: number,
    track: CodexChatTimelineTrackId,
    tone: CodexChatTimelineTone,
    label: string,
    value: string,
    detail: string,
    magnitude: number,
    offset = 0,
    texture: CodexTimelineEvent['texture'] = 'solid',
  ) => {
    const base = chatTimelineFrameForIndex(index, turnCount, frames);
    const start = Math.max(1, Math.min(frames, base + offset));
    const span = Math.max(1, Math.min(frames - start + 1, chatTimelineSpan(magnitude)));
    clips.push({
      id: `${track}-${tone}-${index}-${clips.length}`,
      track,
      label,
      value,
      detail,
      start,
      span,
      targetIndex: index,
      tone,
      texture,
    });
  };

  groups.forEach((group, index) => {
    const userTurn = record(group.user_turn);
    const assistantTurns = records(group.assistant_turns);
    const executionTurns = records(group.execution_turns);
    const contextTurns = records(group.context_turns);
    const otherTurns = records(group.other_turns);
    const returnRecords = records(group.return_records);
    const turnTrace = record(group.turn_trace);
    const traceEvents = records(turnTrace.events);
    const assistantText = assistantTurns.map((turn) => text(turn.message || record(turn.chat_engine).assistant_response, '')).join(' ');
    const userText = text(userTurn.message, '');
    if (userText) {
      addClip(index, 'chat', 'chat-user', 'user', compactTimelineValue(userText, 'prompt'), userText, userText.length, 0, 'solid');
    }
    if (assistantTurns.length || group.pending || group.pending_client_turn) {
      const label = group.pending || group.pending_client_turn ? 'pending' : 'assistant';
      addClip(index, 'chat', 'chat-assistant', label, `${assistantTurns.length || 1}`, compactTimelineValue(assistantText, 'assistant response'), assistantText.length || 1, 1, 'stripe');
    }

    const diff = codexTimelineDiffStats([...returnRecords, ...traceEvents, ...otherTurns]);
    if (diff.added > 0) {
      addClip(index, 'diff', 'diff-add', '+', `+${diff.added}`, diff.detail, diff.added, 0, 'stripe');
    }
    if (diff.removed > 0) {
      addClip(index, 'diff', 'diff-remove', '-', `-${diff.removed}`, diff.detail, diff.removed, diff.added > 0 ? 1 : 0, 'hatch');
    }
    if (diff.changed > 0 || (!diff.added && !diff.removed && diff.fileCount > 0)) {
      addClip(index, 'diff', 'diff-change', 'chg', String(diff.changed || diff.fileCount), diff.detail, diff.changed || diff.fileCount, diff.added || diff.removed ? 2 : 0, 'mesh');
    }

    const contextEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'context');
    const contextRefCount = uniqueStrings([
      ...stringList(userTurn.context_refs),
      ...assistantTurns.flatMap((turn) => stringList(turn.context_refs)),
      ...contextTurns.flatMap((turn) => stringList(turn.context_refs)),
      ...contextEvents.flatMap((event) => stringList(event.context_refs)),
      ...contextEvents.flatMap((event) => stringList(event.source_refs)),
    ]).length;
    const contextCount = contextTurns.length + contextEvents.length + contextRefCount;
    if (contextCount > 0) {
      addClip(index, 'context', 'context-read', 'ctx', String(contextCount), `${contextTurns.length} context turns / ${contextRefCount} refs`, contextCount, 0, 'dot');
    }

    const readCount = codexTimelineReadCount([...traceEvents, ...contextTurns, ...returnRecords]);
    if (readCount > 0) {
      addClip(index, 'reads', 'read', 'read', String(readCount), `${readCount} read/ref signals`, readCount, 0, 'dash');
    }

    const toolEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'tools');
    const toolCount = toolEvents.length + executionTurns.length;
    if (toolCount > 0) {
      const label = executionTurns.length ? 'run' : 'tool';
      addClip(index, 'tools', 'tool', label, String(toolCount), codexTimelineEventNames([...executionTurns, ...toolEvents], 'tool events'), toolCount, 0, 'dot');
    }

    const agentEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'agents');
    const agentSignalCount = agentEvents.length + otherTurns.filter(codexTimelineLooksLikeAgentEvent).length;
    if (agentSignalCount > 0) {
      addClip(index, 'agents', 'agent', 'agent', String(agentSignalCount), codexTimelineEventNames(agentEvents, 'agent events'), agentSignalCount, 0, 'mesh');
    }

    const queueEvents = traceEvents.filter(codexTimelineLooksLikeQueueEvent);
    const queueCount = executionTurns.length + queueEvents.length + (group.pending || group.pending_client_turn ? 1 : 0);
    if (queueCount > 0) {
      const blocked = [...executionTurns, ...queueEvents].some((event) => codexTimelineStatusIsBlocked(event));
      addClip(index, 'queue', blocked ? 'blocked' : 'queue', blocked ? 'block' : 'queue', String(queueCount), codexTimelineEventNames([...executionTurns, ...queueEvents], 'queue/run events'), queueCount, 0, blocked ? 'hatch' : 'stripe');
    }
  });

  return {
    frames,
    clips,
    summary: {
      turnCount,
      diffCount: clips.filter((clip) => clip.track === 'diff').length,
      toolCount: clips.filter((clip) => clip.track === 'tools').length,
      readCount: clips.filter((clip) => clip.track === 'reads').length,
      agentCount: clips.filter((clip) => clip.track === 'agents').length,
    },
  };
}

function buildCodexChatScrollSequenceMarkers({
  groups,
  items,
  window,
}: {
  groups: Array<Record<string, unknown>>;
  items?: Array<Record<string, unknown>>;
  window?: CodexChatScrollSequenceWindow;
}): CodexChatScrollSequenceMarker[] {
  const archiveItems = records(items);
  if (archiveItems.length) {
    return archiveItems.map((item, index) => {
      const signal = codexChatScrollArchiveItemSignal(item, index, window);
      const archiveIndex = codexChatScrollArchiveItemIndex(item, index, window);
      return {
        id: `item-${archiveIndex || index + 1}-${signal.scrollTrack}-${signal.tone}-${index}`,
        targetIndex: Math.max(0, archiveIndex - 1),
        top: codexChatScrollSequenceTop(index, archiveItems.length),
        ...signal,
      };
    });
  }
  return groups.map((group, index) => {
    const signal = codexChatScrollGroupSignal(group, index, groups.length);
    return {
      id: `group-${index}-${signal.scrollTrack}-${signal.tone}`,
      targetIndex: index,
      top: codexChatScrollSequenceTop(index, groups.length),
      ...signal,
    };
  });
}

function codexChatScrollSequenceTop(index: number, count: number) {
  if (count <= 1) return 50;
  return Math.max(2, Math.min(98, 2 + (index / Math.max(1, count - 1)) * 96));
}

function codexChatScrollArchiveItemIndex(
  item: Record<string, unknown>,
  index: number,
  window?: CodexChatScrollSequenceWindow,
) {
  const direct = numberValue(item.item_index ?? item.index ?? item.ordinal);
  if (direct > 0) return direct;
  const oldest = numberValue(window?.oldest);
  return oldest > 0 ? oldest + index : index + 1;
}

function codexChatScrollArchiveItemSignal(
  item: Record<string, unknown>,
  index: number,
  window?: CodexChatScrollSequenceWindow,
): Omit<CodexChatScrollSequenceMarker, 'id' | 'targetIndex' | 'top'> {
  const role = text(item.role || item.author || item.kind, 'archive');
  const roleGroup = archiveMessageRoleGroup(item, role);
  const workBucket = archiveWorkBucket(item);
  const label = archiveMessageLabel(item, role, roleGroup);
  const archiveIndex = codexChatScrollArchiveItemIndex(item, index, window);
  const total = numberValue(window?.total);
  const position = total > 0 ? `item ${archiveIndex} of ${total}` : `item ${archiveIndex}`;
  const body = compactTimelineValue(archiveItemText(item), label);
  const detail = `${position} / ${label}: ${body}`;
  const diff = codexTimelineDiffStats([item]);

  if (roleGroup === 'diff' || workBucket === 'edits' || diff.added > 0 || diff.removed > 0 || diff.changed > 0 || diff.fileCount > 0) {
    return { scrollTrack: 'edit', tone: codexChatScrollDiffTone(diff), detail };
  }
  if (roleGroup === 'user') return { scrollTrack: 'thread', tone: 'chat-user', detail };
  if (roleGroup === 'ai' || workBucket === 'assistant' || workBucket === 'thinking') {
    return { scrollTrack: 'thread', tone: 'chat-assistant', detail };
  }
  if (workBucket === 'tools' || roleGroup === 'trace') return { scrollTrack: 'work', tone: 'tool', detail };
  if (workBucket === 'context' || roleGroup === 'context' || roleGroup === 'compaction') {
    return { scrollTrack: 'work', tone: 'context-read', detail };
  }
  if (workBucket === 'runs' || codexTimelineLooksLikeQueueEvent(item)) {
    return { scrollTrack: 'work', tone: codexTimelineStatusIsBlocked(item) ? 'blocked' : 'queue', detail };
  }
  if (codexTimelineLooksLikeAgentEvent(item)) return { scrollTrack: 'work', tone: 'agent', detail };
  if (codexTimelineReadCount([item]) > 0) return { scrollTrack: 'work', tone: 'read', detail };
  if (workBucket === 'proof') return { scrollTrack: 'work', tone: 'evidence', detail };
  return { scrollTrack: 'work', tone: 'evidence', detail };
}

function codexChatScrollGroupSignal(
  group: Record<string, unknown>,
  index: number,
  count: number,
): Omit<CodexChatScrollSequenceMarker, 'id' | 'targetIndex' | 'top'> {
  const userTurn = record(group.user_turn);
  const assistantTurns = records(group.assistant_turns);
  const executionTurns = records(group.execution_turns);
  const contextTurns = records(group.context_turns);
  const otherTurns = records(group.other_turns);
  const returnRecords = records(group.return_records);
  const traceEvents = records(record(group.turn_trace).events);
  const eventPool = [...returnRecords, ...traceEvents, ...otherTurns, ...executionTurns, ...contextTurns];
  const diff = codexTimelineDiffStats(eventPool);
  const headline = compactTimelineValue(
    text(userTurn.message || assistantTurns[0]?.message || group.group_id, 'turn marker'),
    'turn marker',
  );
  const detail = `turn ${Math.min(index + 1, count)} of ${count}: ${headline}`;

  if (diff.added > 0 || diff.removed > 0 || diff.changed > 0 || diff.fileCount > 0) {
    return { scrollTrack: 'edit', tone: codexChatScrollDiffTone(diff), detail };
  }

  const queueEvents = traceEvents.filter(codexTimelineLooksLikeQueueEvent);
  if (queueEvents.length || executionTurns.length || group.pending || group.pending_client_turn) {
    const blocked = [...executionTurns, ...queueEvents].some((event) => codexTimelineStatusIsBlocked(event));
    return { scrollTrack: 'work', tone: blocked ? 'blocked' : 'queue', detail };
  }

  const agentEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'agents');
  if (agentEvents.length || otherTurns.some(codexTimelineLooksLikeAgentEvent)) {
    return { scrollTrack: 'work', tone: 'agent', detail };
  }

  const toolEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'tools');
  if (toolEvents.length) {
    return { scrollTrack: 'work', tone: 'tool', detail };
  }

  const readCount = codexTimelineReadCount(eventPool);
  if (readCount > 0) {
    return { scrollTrack: 'work', tone: 'read', detail };
  }

  const contextEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'context');
  if (contextEvents.length || contextTurns.length || stringList(userTurn.context_refs).length) {
    return { scrollTrack: 'work', tone: 'context-read', detail };
  }

  if (assistantTurns.length || group.pending || group.pending_client_turn) {
    return { scrollTrack: 'thread', tone: 'chat-assistant', detail };
  }
  return { scrollTrack: 'thread', tone: 'chat-user', detail };
}

function codexChatScrollDiffTone(diff: ReturnType<typeof codexTimelineDiffStats>): CodexChatTimelineTone {
  if (diff.removed > diff.added && diff.removed > 0) return 'diff-remove';
  if (diff.added > 0) return 'diff-add';
  return 'diff-change';
}

function chatTimelineFrameForIndex(index: number, turnCount: number, frames: number) {
  if (turnCount <= 1) return 1;
  return Math.max(1, Math.min(frames, 1 + Math.floor((index / Math.max(1, turnCount - 1)) * (frames - 1))));
}

function chatTimelineSpan(magnitude: number) {
  const value = Math.max(1, numberValue(magnitude));
  return Math.max(1, Math.min(10, Math.ceil(Math.sqrt(value))));
}

function compactTimelineValue(value: unknown, fallback: string) {
  const normalized = text(value, fallback).replace(/\s+/g, ' ').trim();
  if (!normalized) return fallback;
  return normalized.length > 24 ? `${normalized.slice(0, 22)}...` : normalized;
}

function codexTimelineDiffStats(events: Array<Record<string, unknown>>) {
  let added = 0;
  let removed = 0;
  let changed = 0;
  let fileCount = 0;
  const files: string[] = [];
  for (const event of events) {
    const stats = record(event.diff_stats || event.file_diff || event.diff);
    added += numberValue(stats.added_lines ?? stats.added_count ?? stats.added);
    removed += numberValue(stats.removed_lines ?? stats.removed_count ?? stats.removed);
    changed += numberValue(stats.changed_lines ?? stats.changed_count ?? stats.modified_count ?? stats.changed);
    fileCount += numberValue(stats.file_count ?? stats.files_changed ?? stats.touched_file_count);
    files.push(
      ...stringList(stats.files),
      ...stringList(event.touched_paths),
      ...stringList(event.path_refs),
      text(event.path || event.file || event.latest_return_path, ''),
    );
    const joined = [
      text(event.event_type || event.kind || event.type, ''),
      text(event.label, ''),
      text(event.detail || event.message || event.summary, ''),
    ].join(' ').toLowerCase();
    if (!Object.keys(stats).length && (joined.includes('diff') || joined.includes('edit') || joined.includes('patch') || joined.includes('file change'))) {
      changed += 1;
    }
  }
  const uniqueFiles = uniqueStrings(files.filter(Boolean));
  fileCount = Math.max(fileCount, uniqueFiles.length);
  return {
    added,
    removed,
    changed,
    fileCount,
    detail: `${fileCount || uniqueFiles.length || 0} files / +${added} / -${removed} / changed ${changed}`,
  };
}

function codexTimelineReadCount(events: Array<Record<string, unknown>>) {
  let count = 0;
  for (const event of events) {
    const joined = [
      text(event.event_type || event.kind || event.type, ''),
      text(event.label, ''),
      text(event.tool_name, ''),
      text(event.detail || event.message || event.summary, ''),
      ...stringList(event.source_refs),
      ...stringList(event.context_refs),
      ...stringList(event.path_refs),
    ].join(' ').toLowerCase();
    if (/\b(read|open|cat|sed|rg|find|ls|view|context ref|source ref)\b/.test(joined)) count += 1;
  }
  return count;
}

function codexTimelineLooksLikeAgentEvent(event: Record<string, unknown>) {
  const joined = [
    text(event.event_type || event.kind || event.type, ''),
    text(event.label, ''),
    text(event.role || event.agent_role || event.agent_role_id || event.role_id, ''),
    text(event.detail || event.message || event.summary, ''),
  ].join(' ').toLowerCase();
  return /\b(agent|spawn|worker|role|relay|persona|steward|mason|nemesis|ionologist)\b/.test(joined);
}

function codexTimelineLooksLikeQueueEvent(event: Record<string, unknown>) {
  const joined = [
    text(event.event_type || event.kind || event.type, ''),
    text(event.label, ''),
    text(event.tool_name, ''),
    text(event.detail || event.message || event.summary || event.packet_path || event.request_id, ''),
  ].join(' ').toLowerCase();
  return /\b(queue|runner|run|request|packet|dispatch|workpack|response_run)\b/.test(joined);
}

function codexTimelineStatusIsBlocked(event: Record<string, unknown>) {
  const status = text(event.status || event.verdict || event.result || event.state, '').toLowerCase();
  return status.includes('block') || status.includes('fail') || status.includes('error') || status.includes('denied');
}

function codexTimelineEventNames(events: Array<Record<string, unknown>>, fallback: string) {
  const names = uniqueStrings(events.map((event) => text(event.label || event.event_type || event.kind || event.tool_name || event.packet_path, '')).filter(Boolean));
  return names.slice(0, 4).join(' / ') || fallback;
}

function createArchiveConversationGroup(
  userItem: Record<string, unknown> | null,
  seedItem: Record<string, unknown> | null,
  index: number,
): ArchiveConversationGroup {
  const key = userItem ? archiveItemSourceKey(userItem) : `archive-orphan-${index}-${archiveItemSourceKey(seedItem ?? {})}`;
  return {
    group_id: `archive-group-${key}`,
    user_turn: userItem ? archiveUserTurn(userItem) : {},
    assistant_turns: [],
    execution_turns: [],
    context_turns: [],
    other_turns: [],
    return_records: [],
    turn_trace: {
      turn_id: `archive-trace-${key}`,
      events: [],
    },
  };
}

function archiveUserTurn(item: Record<string, unknown>) {
  return {
    ...item,
    author: 'operator',
    turn_id: archiveItemSourceKey(item),
    created_at: item.timestamp,
    message: archiveItemText(item),
  };
}

function archiveAssistantTurn(item: Record<string, unknown>) {
  return {
    ...item,
    author: text(item.role, 'assistant'),
    turn_id: archiveItemSourceKey(item),
    created_at: item.timestamp,
    message: archiveItemText(item),
  };
}

function archiveContextTurn(item: Record<string, unknown>, roleGroup: string) {
  return {
    ...item,
    kind: text(item.message_kind || roleGroup, 'context'),
    turn_id: archiveItemSourceKey(item),
    created_at: item.timestamp,
    message: archiveItemText(item),
    status: text(item.detail_label, 'ready'),
  };
}

function archiveOtherTurn(item: Record<string, unknown>, roleGroup: string) {
  return {
    ...item,
    kind: text(item.message_kind || roleGroup, 'event'),
    turn_id: archiveItemSourceKey(item),
    created_at: item.timestamp,
    author: text(item.role, 'archive'),
    message: archiveItemText(item),
    summary: text(item.detail_label, ''),
  };
}

function archiveTraceEvent(item: Record<string, unknown>, roleGroup: string) {
  const role = text(item.role, 'archive');
  return {
    ...item,
    id: archiveItemSourceKey(item),
    event_type: text(item.message_kind || roleGroup, 'archive_event'),
    label: archiveMessageLabel(item, role, roleGroup),
    detail: archiveItemText(item),
    source_refs: archiveItemSourceRefs(item),
  };
}

function archiveReturnRecord(item: Record<string, unknown>, roleGroup: string) {
  const event = archiveTraceEvent(item, roleGroup);
  return {
    ...event,
    kind: text(item.message_kind || 'archive_edit', 'archive_edit'),
    task_output_preview: archiveItemText(item),
    latest_return_path: text(item.path || item.packet_path || item.latest_return_path, ''),
  };
}

function archiveItemSourceRefs(item: Record<string, unknown>) {
  return uniqueStrings([
    ...stringList(item.source_refs),
    ...stringList(item.path_refs),
    ...stringList(item.context_refs),
    ...stringList(record(item.diff_stats).files),
    text(item.path || item.packet_path || item.latest_return_path || item.session_path, ''),
  ]).slice(0, 12);
}

function archiveItemSourceKey(item: Record<string, unknown>) {
  return messageSourceKey(item, item.timestamp || item.item_index || item.index || archiveItemText(item));
}

function latestArchiveAssistantKey(blocks: ArchiveTranscriptBlock[]) {
  for (let blockIndex = blocks.length - 1; blockIndex >= 0; blockIndex -= 1) {
    const block = blocks[blockIndex];
    if (block.kind !== 'work') continue;
    for (let itemIndex = block.assistantItems.length - 1; itemIndex >= 0; itemIndex -= 1) {
      const item = block.assistantItems[itemIndex];
      if (item) return archiveItemSourceKey(item);
    }
  }
  return '';
}

function archiveBufferStatus(buffer: ArchiveTranscriptBuffer | null, busy: ArchiveBufferDirection | '', sessionId: string) {
  if (busy) return `${busy} buffer loading`;
  if (!buffer || buffer.sessionId !== sessionId) return '';
  const range = buffer.endIndex > 0 ? `${buffer.startIndex}-${buffer.endIndex}` : `${buffer.startIndex}+`;
  return `${buffer.direction} ${range} rendered`;
}

function archiveTranscriptWindowLabel(excerpt: IonCodexConversationArchive['selected_session_excerpt'] | null | undefined) {
  const excerptItems = records(excerpt?.items);
  const displayedCount = numberValue(excerpt?.displayed_item_count ?? excerpt?.item_count ?? excerptItems.length);
  const totalDisplayable = numberValue(excerpt?.total_displayable_items ?? displayedCount);
  const omittedOlder = numberValue(excerpt?.omitted_older_items);
  const omittedNewer = numberValue(excerpt?.omitted_newer_items);
  const oldestIndex = numberValue(excerpt?.oldest_item_index);
  const newestIndex = numberValue(excerpt?.newest_item_index);
  if (omittedOlder > 0 || omittedNewer > 0) {
    return `items ${oldestIndex || 0}-${newestIndex || 0} of ${totalDisplayable} safe items`;
  }
  return `${displayedCount} safe items`;
}

function scrollTranscriptToPosition(node: HTMLDivElement | null, target: 'top' | 'bottom', options: { repeat?: boolean } = {}) {
  if (!node) return;
  const apply = () => {
    node.scrollTop = target === 'top' ? 0 : Math.max(0, node.scrollHeight - node.clientHeight);
  };
  scheduleTranscriptScroll(apply, options.repeat);
}

function scrollArchiveTranscriptToLoadedWindow(node: HTMLDivElement | null, target: 'top' | 'bottom', options: { repeat?: boolean } = {}) {
  if (!node) return;
  const apply = () => {
    if (!node.classList.contains('is-virtual')) {
      node.scrollTop = target === 'top' ? 0 : Math.max(0, node.scrollHeight - node.clientHeight);
      return;
    }
    const windowNode = node.querySelector<HTMLElement>('.ion-codex-archive-window');
    if (!windowNode) {
      node.scrollTop = target === 'top' ? 0 : Math.max(0, node.scrollHeight - node.clientHeight);
      return;
    }
    const transformOffset = archiveWindowTransformOffset(windowNode);
    const windowHeight = Math.max(windowNode.scrollHeight, windowNode.getBoundingClientRect().height);
    const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
    const targetTop = target === 'top'
      ? transformOffset
      : transformOffset + windowHeight - node.clientHeight + 16;
    node.scrollTop = Math.min(Math.max(0, targetTop), maxTop);
  };
  scheduleTranscriptScroll(apply, options.repeat);
}

function archiveWindowTransformOffset(node: HTMLElement) {
  const transform = node.style.transform;
  const match = /translateY\((-?\d+(?:\.\d+)?)px\)/.exec(transform);
  if (!match) return node.offsetTop;
  const value = Number(match[1]);
  return Number.isFinite(value) ? value : node.offsetTop;
}

function scrollLiveTranscriptToNewest(node: HTMLDivElement | null, options: { repeat?: boolean } = {}) {
  if (!node) return;
  const apply = () => {
    const newest = node.querySelector<HTMLElement>('.ion-codex-turn-group:last-of-type');
    if (!newest) {
      node.scrollTop = Math.max(0, node.scrollHeight - node.clientHeight);
      return;
    }
    const nodeRect = node.getBoundingClientRect();
    const newestRect = newest.getBoundingClientRect();
    const targetTop = Math.max(0, node.scrollTop + newestRect.top - nodeRect.top - 8);
    const maxTop = Math.max(0, node.scrollHeight - node.clientHeight);
    node.scrollTop = Math.min(targetTop, maxTop);
  };
  scheduleTranscriptScroll(apply, options.repeat);
}

function scheduleTranscriptScroll(apply: () => void, repeat = false) {
  if (typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function') {
    window.requestAnimationFrame(() => {
      apply();
      if (repeat) window.requestAnimationFrame(apply);
    });
    return;
  }
  apply();
}

function isTranscriptNearBottom(node: HTMLDivElement, threshold = 0) {
  return node.scrollHeight - node.clientHeight - node.scrollTop <= threshold;
}

function projectLabel(session: IonCodexConversationArchiveSession) {
  if (session.project_label) return session.project_label;
  const cwd = text(session.cwd, '');
  if (!cwd) return 'Project Unknown';
  const parts = cwd.split('/').filter(Boolean);
  return parts.slice(-2).join('/') || cwd;
}

function sessionTitle(session: IonCodexConversationArchiveSession) {
  return text(session.display_title || session.thread_name || session.session_id);
}

function sessionShortId(session: IonCodexConversationArchiveSession) {
  const value = text(session.session_id, '');
  return value ? `id ${value.slice(0, 8)}` : 'id unknown';
}

function sessionShortText(sessionId: string) {
  const value = text(sessionId, '');
  return value ? `id ${value.slice(0, 8)}` : 'id unknown';
}

function tabIdForSession(sessionId: string) {
  return `archive:${sessionId}`;
}

function openChatTabFromSession(session: IonCodexConversationArchiveSession, options: { windowStart?: number } = {}): OpenChatTab {
  const now = new Date().toISOString();
  return {
    id: tabIdForSession(session.session_id),
    kind: 'archive',
    sessionId: session.session_id,
    title: sessionTitle(session),
    subtitle: text(session.latest_user_snippet || session.first_user_snippet, ''),
    projectLabel: projectLabel(session),
    model: text(session.model, ''),
    isCurrent: Boolean(session.is_current_session),
    windowStart: options.windowStart,
    openedAt: now,
    lastOpenedAt: now,
    lastViewedAt: now,
  };
}

function sessionFromOpenChatTab(tab: OpenChatTab | null | undefined): IonCodexConversationArchiveSession | undefined {
  if (!tab?.sessionId) return undefined;
  return {
    session_id: tab.sessionId,
    display_title: tab.title,
    thread_name: tab.title,
    latest_user_snippet: tab.subtitle,
    project_label: tab.projectLabel,
    model: tab.model,
    is_current_session: tab.isCurrent,
  };
}

function drawerSessionPreviewItems(session: IonCodexConversationArchiveSession, selectedExcerpt: unknown): DrawerSessionPreviewItem[] {
  const excerpt = record(selectedExcerpt);
  const excerptItems = text(excerpt.session_id, '') === session.session_id
    ? records(excerpt.items)
    : [];
  const transcriptItems = excerptItems
    .map(drawerPreviewItem)
    .filter((item): item is DrawerSessionPreviewItem => Boolean(item))
    .slice(-8);
  if (transcriptItems.length) return transcriptItems;
  const timestamp = text(session.history_latest_ts || session.updated_at || session.created_at, '');
  return [
    {
      role: 'user',
      text: compactPreviewText(session.latest_user_snippet || session.first_user_snippet),
      timestamp,
    },
    {
      role: 'assistant',
      text: compactPreviewText(session.latest_assistant_snippet),
      timestamp,
    },
  ].filter((item) => item.text).slice(-6);
}

function drawerPreviewItem(item: Record<string, unknown>): DrawerSessionPreviewItem | null {
  const body = compactPreviewText(item.text || item.snippet || item.message || record(item.chat_engine).assistant_response);
  if (!body) return null;
  return {
    role: text(item.role || item.author || item.kind, 'message'),
    text: body,
    timestamp: text(item.timestamp || item.created_at || item.updated_at, ''),
  };
}

function compactPreviewText(value: unknown) {
  const normalized = text(value, '').replace(/\s+/g, ' ').trim();
  return normalized.length > 420 ? `${normalized.slice(0, 420)}...` : normalized;
}

function connectionDrawerId(id: ConnectionId): ConnectionDrawerId {
  return `connection:${id}`;
}

function connectionProfileForDrawer(id: string): ConnectionProfile | undefined {
  if (!id.startsWith('connection:')) return undefined;
  const connectionId = id.slice('connection:'.length) as ConnectionId;
  return connectionProfiles.find((profile) => profile.id === connectionId);
}

function defaultConnectionState(): Record<ConnectionId, boolean> {
  return connectionProfiles.reduce((state, profile) => {
    state[profile.id] = false;
    return state;
  }, {} as Record<ConnectionId, boolean>);
}

function loadPersistedConnectionState(): Record<ConnectionId, boolean> {
  const state = defaultConnectionState();
  if (typeof window === 'undefined') return state;
  try {
    const raw = window.localStorage.getItem(CONNECTIONS_STORAGE_KEY);
    if (!raw) return state;
    const parsed = record(JSON.parse(raw));
    for (const profile of connectionProfiles) {
      state[profile.id] = Boolean(parsed[profile.id]);
    }
  } catch {
    return state;
  }
  return state;
}

function persistConnectionState(state: Record<ConnectionId, boolean>) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CONNECTIONS_STORAGE_KEY, JSON.stringify({
      schema_id: CONNECTIONS_STORAGE_KEY,
      ...state,
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function loadPersistedOpenChatTabs(): PersistedOpenChatTabs {
  if (typeof window === 'undefined') return { activeTabId: '', tabs: [] };
  try {
    const raw = window.localStorage.getItem(CHAT_TAB_STORAGE_KEY);
    if (!raw) return { activeTabId: '', tabs: [] };
    const parsed = record(JSON.parse(raw)) as Partial<PersistedOpenChatTabs>;
    const tabs = Array.isArray(parsed.tabs)
      ? parsed.tabs.map(sanitizeOpenChatTab).filter((tab): tab is OpenChatTab => Boolean(tab))
      : [];
    const activeTabId = text(parsed.activeTabId, '');
    return {
      activeTabId: tabs.some((tab) => tab.id === activeTabId) ? activeTabId : tabs[0]?.id ?? '',
      tabs,
    };
  } catch {
    return { activeTabId: '', tabs: [] };
  }
}

function persistOpenChatTabs(state: PersistedOpenChatTabs) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CHAT_TAB_STORAGE_KEY, JSON.stringify({
      schema_id: CHAT_TAB_STORAGE_KEY,
      activeTabId: state.tabs.some((tab) => tab.id === state.activeTabId) ? state.activeTabId : state.tabs[0]?.id ?? '',
      tabs: state.tabs,
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function loadPersistedChatHistoryMeta(): Record<string, ChatHistoryMeta> {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(CHAT_HISTORY_META_STORAGE_KEY);
    if (!raw) return {};
    const parsed = record(JSON.parse(raw));
    const entries = record(parsed.entries && typeof parsed.entries === 'object' ? parsed.entries : parsed);
    const state: Record<string, ChatHistoryMeta> = {};
    for (const [sessionId, value] of Object.entries(entries)) {
      if (sessionId === 'schema_id' || sessionId === 'entries') continue;
      const entry = sanitizeChatHistoryMeta(value);
      if (entry.lastOpenedAt || entry.lastClosedAt) state[sessionId] = entry;
    }
    return state;
  } catch {
    return {};
  }
}

function persistChatHistoryMeta(state: Record<string, ChatHistoryMeta>) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CHAT_HISTORY_META_STORAGE_KEY, JSON.stringify({
      schema_id: CHAT_HISTORY_META_STORAGE_KEY,
      entries: state,
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function sanitizeChatHistoryMeta(value: unknown): ChatHistoryMeta {
  const raw = record(value);
  return {
    lastOpenedAt: text(raw.lastOpenedAt || raw.last_opened_at, ''),
    lastClosedAt: text(raw.lastClosedAt || raw.last_closed_at, ''),
  };
}

function loadPersistedChatTitleOverrides(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(CHAT_TITLE_OVERRIDES_STORAGE_KEY);
    if (!raw) return {};
    const parsed = record(JSON.parse(raw));
    const source = record(parsed.titles || parsed.overrides || parsed);
    return Object.entries(source).reduce((titles, [key, value]) => {
      const sessionId = text(key, '').trim();
      const title = text(value, '').trim();
      if (sessionId && title && sessionId !== 'schema_id') titles[sessionId] = title.slice(0, 160);
      return titles;
    }, {} as Record<string, string>);
  } catch {
    return {};
  }
}

function persistChatTitleOverrides(overrides: Record<string, string>) {
  if (typeof window === 'undefined') return;
  try {
    const titles = Object.entries(overrides).reduce((next, [sessionId, title]) => {
      const normalizedSessionId = text(sessionId, '').trim();
      const normalizedTitle = text(title, '').trim();
      if (normalizedSessionId && normalizedTitle) next[normalizedSessionId] = normalizedTitle.slice(0, 160);
      return next;
    }, {} as Record<string, string>);
    window.localStorage.setItem(CHAT_TITLE_OVERRIDES_STORAGE_KEY, JSON.stringify({
      schema_id: CHAT_TITLE_OVERRIDES_STORAGE_KEY,
      titles,
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function loadPersistedFavoriteChatIds(): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(CHAT_FAVORITES_STORAGE_KEY);
    if (!raw) return [];
    const parsed = record(JSON.parse(raw));
    const values = Array.isArray(parsed.session_ids) ? parsed.session_ids : parsed.favorites;
    return uniqueStrings(stringList(values).map((value) => value.trim()).filter(Boolean)).slice(0, 240);
  } catch {
    return [];
  }
}

function persistFavoriteChatIds(sessionIds: string[]) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CHAT_FAVORITES_STORAGE_KEY, JSON.stringify({
      schema_id: CHAT_FAVORITES_STORAGE_KEY,
      session_ids: uniqueStrings(sessionIds.map((value) => text(value, '').trim()).filter(Boolean)).slice(0, 240),
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function defaultChatDrawerPrefs(): ChatDrawerPrefs {
  return {
    hideShortChats: false,
    shortChatMaxUserPrompts: 2,
  };
}

function loadPersistedChatDrawerPrefs(): ChatDrawerPrefs {
  const fallback = defaultChatDrawerPrefs();
  if (typeof window === 'undefined') return fallback;
  try {
    const raw = window.localStorage.getItem(CHAT_DRAWER_PREFS_STORAGE_KEY);
    if (!raw) return fallback;
    const parsed = record(JSON.parse(raw));
    return {
      hideShortChats: parsed.hideShortChats === undefined ? fallback.hideShortChats : Boolean(parsed.hideShortChats),
      shortChatMaxUserPrompts: clampInteger(parsed.shortChatMaxUserPrompts ?? parsed.short_chat_max_user_prompts, 0, 12, fallback.shortChatMaxUserPrompts),
    };
  } catch {
    return fallback;
  }
}

function persistChatDrawerPrefs(prefs: ChatDrawerPrefs) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CHAT_DRAWER_PREFS_STORAGE_KEY, JSON.stringify({
      schema_id: CHAT_DRAWER_PREFS_STORAGE_KEY,
      hideShortChats: Boolean(prefs.hideShortChats),
      shortChatMaxUserPrompts: clampInteger(prefs.shortChatMaxUserPrompts, 0, 12, 2),
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function clampInteger(value: unknown, min: number, max: number, fallback: number) {
  const parsed = Number.parseInt(text(value, ''), 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(Math.max(parsed, min), max);
}

function sessionUserPromptCount(session: IonCodexConversationArchiveSession) {
  return numberValue(session.history_prompt_count);
}

function sessionVisibleByShortFilter(
  session: IonCodexConversationArchiveSession,
  options: {
    currentSessionId: string;
    favoriteIds: Set<string>;
    openIds: Set<string>;
    prefs: ChatDrawerPrefs;
    selectedSessionId: string;
  },
) {
  if (!options.prefs.hideShortChats) return true;
  if (isQueueRunnerPacket(session)) return true;
  if (session.is_current_session || session.session_id === options.currentSessionId) return true;
  if (session.session_id === options.selectedSessionId) return true;
  if (options.openIds.has(session.session_id)) return true;
  if (options.favoriteIds.has(session.session_id)) return true;
  return sessionUserPromptCount(session) > options.prefs.shortChatMaxUserPrompts;
}

function loadPersistedCodexMessageQueues(): PersistedCodexMessageQueues {
  if (typeof window === 'undefined') return { activeGroupId: '', items: [], groups: [] };
  try {
    const raw = window.localStorage.getItem(MESSAGE_QUEUE_STORAGE_KEY);
    if (!raw) return { activeGroupId: '', items: [], groups: [] };
    const parsed = record(JSON.parse(raw));
    const items = Array.isArray(parsed.items)
      ? parsed.items.map(sanitizeMessageQueueItem).filter((item): item is CodexMessageQueueItem => Boolean(item))
      : [];
    const groups = Array.isArray(parsed.groups)
      ? parsed.groups.map(sanitizeMessageQueueGroup).filter((group): group is CodexMessageQueueGroup => Boolean(group))
      : [];
    const activeGroupId = text(parsed.activeGroupId, '');
    return {
      activeGroupId: groups.some((group) => group.id === activeGroupId) ? activeGroupId : '',
      items,
      groups,
    };
  } catch {
    return { activeGroupId: '', items: [], groups: [] };
  }
}

function persistCodexMessageQueues(state: PersistedCodexMessageQueues) {
  if (typeof window === 'undefined') return;
  try {
    const items = state.items.map(sanitizeMessageQueueItem).filter((item): item is CodexMessageQueueItem => Boolean(item));
    const groups = state.groups.map(sanitizeMessageQueueGroup).filter((group): group is CodexMessageQueueGroup => Boolean(group)).slice(0, 30);
    window.localStorage.setItem(MESSAGE_QUEUE_STORAGE_KEY, JSON.stringify({
      schema_id: MESSAGE_QUEUE_STORAGE_KEY,
      activeGroupId: groups.some((group) => group.id === state.activeGroupId) ? state.activeGroupId : '',
      items,
      groups,
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function loadPersistedContextRefs(): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(CONTEXT_REFS_STORAGE_KEY);
    if (!raw) return [];
    const parsed = record(JSON.parse(raw));
    return normalizeContextRefs(Array.isArray(parsed.refs) ? parsed.refs : parsed.context_refs);
  } catch {
    return [];
  }
}

function persistContextRefs(refs: string[]) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CONTEXT_REFS_STORAGE_KEY, JSON.stringify({
      schema_id: CONTEXT_REFS_STORAGE_KEY,
      refs: normalizeContextRefs(refs),
    }));
  } catch {
    // localStorage can be unavailable in private or restricted browser contexts.
  }
}

function createMessageQueueItem(message: string, mode: ExecutionModeId, title = '', contextRefs: string[] = [], laneId: CodexChatLaneId = 'codex_general'): CodexMessageQueueItem {
  const body = message.trim();
  const now = new Date().toISOString();
  return {
    id: createClientId('codex_queue_item'),
    title: cleanQueueTitle(title, body),
    message: body,
    mode,
    laneId,
    contextRefs: normalizeContextRefs(contextRefs),
    createdAt: now,
    updatedAt: now,
  };
}

function sanitizeMessageQueueGroup(value: unknown): CodexMessageQueueGroup | null {
  const raw = record(value);
  const id = text(raw.id, '').trim();
  const name = cleanQueueGroupName(text(raw.name, ''), 1);
  const items = Array.isArray(raw.items)
    ? raw.items.map(sanitizeMessageQueueItem).filter((item): item is CodexMessageQueueItem => Boolean(item))
    : [];
  if (!id || !items.length) return null;
  return {
    id,
    name,
    items,
    createdAt: text(raw.createdAt || raw.created_at, new Date().toISOString()),
    updatedAt: text(raw.updatedAt || raw.updated_at, new Date().toISOString()),
  };
}

function sanitizeMessageQueueItem(value: unknown): CodexMessageQueueItem | null {
  const raw = record(value);
  const message = text(raw.message, '').trim();
  if (!message) return null;
  const mode = executionModeId(raw.mode) || 'queue_for_codex';
  const now = new Date().toISOString();
  return {
    id: text(raw.id, '') || createClientId('codex_queue_item'),
    title: cleanQueueTitle(text(raw.title, ''), message),
    message,
    mode,
    laneId: text(raw.laneId || raw.lane_id, 'codex_general'),
    contextRefs: normalizeContextRefs(raw.contextRefs || raw.context_refs),
    createdAt: text(raw.createdAt || raw.created_at, now),
    updatedAt: text(raw.updatedAt || raw.updated_at, now),
    lastDispatchedAt: text(raw.lastDispatchedAt || raw.last_dispatched_at, ''),
  };
}

function cloneMessageQueueItem(item: CodexMessageQueueItem): CodexMessageQueueItem {
  return {
    ...item,
    title: cleanQueueTitle(item.title, item.message),
    message: item.message.trim(),
    mode: executionModeId(item.mode) || 'queue_for_codex',
    laneId: text(item.laneId, 'codex_general'),
    contextRefs: normalizeContextRefs(item.contextRefs),
  };
}

function cleanQueueTitle(title: string, message: string) {
  const cleanTitle = title.trim().replace(/\s+/g, ' ');
  if (cleanTitle) return cleanTitle.slice(0, 120);
  return message
    .split('\n')
    .map((line) => line.trim())
    .find(Boolean)
    ?.replace(/\s+/g, ' ')
    .slice(0, 120) || 'Codex queue message';
}

function cleanQueueGroupName(name: string, fallbackIndex: number) {
  const cleanName = name.trim().replace(/\s+/g, ' ');
  return (cleanName || `Queue Group ${fallbackIndex}`).slice(0, 120);
}

function normalizeContextRefs(value: unknown): string[] {
  const source = Array.isArray(value) ? value : typeof value === 'string' ? value.split(/\n|,/) : [];
  const refs: string[] = [];
  const seen = new Set<string>();
  for (const item of source) {
    const ref = text(item, '').trim().replace(/^@+/, '');
    if (!ref || ref.startsWith('/') || ref.includes('\0') || ref.split('/').includes('..')) continue;
    if (seen.has(ref)) continue;
    refs.push(ref);
    seen.add(ref);
  }
  return refs;
}

function sanitizeFileTreeEntry(value: unknown): CodexFileTreeEntry | null {
  const raw = record(value);
  const path = text(raw.path, '').trim();
  const kind = text(raw.kind, '') === 'dir' ? 'dir' : text(raw.kind, '') === 'file' ? 'file' : '';
  if (!path || !kind) return null;
  const bytes = Number(raw.bytes);
  return {
    path,
    kind,
    bytes: Number.isFinite(bytes) ? bytes : undefined,
  };
}

function contextRefMention(ref: string) {
  const name = pathBasename(ref).replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9_-]+/g, '_').replace(/^_+|_+$/g, '');
  return `@${name || ref.replace(/[^a-zA-Z0-9_-]+/g, '_')}`;
}

function pathBasename(path: string) {
  const clean = path.trim().replace(/\/+$/, '');
  return clean.split('/').pop() || clean || 'ref';
}

function fileRootLabel(root: string) {
  if (root === 'ION/04_packages/kernel') return 'KERNEL';
  if (root === 'ION/08_ui') return 'UI';
  return pathBasename(root).toUpperCase();
}

function fileTreeDepthLevel(path: string) {
  return Math.max(0, path.split('/').filter(Boolean).length - 1);
}

function formatBytes(value: unknown) {
  const bytes = Number(value);
  if (!Number.isFinite(bytes) || bytes < 0) return '';
  if (bytes < 1024) return `${bytes}b`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)}kb`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}mb`;
}

function executionModeId(value: unknown): ExecutionModeId | '' {
  const mode = text(value, '');
  return executionModes.some((candidate) => candidate.id === mode) ? mode as ExecutionModeId : '';
}

function codexChatLaneId(value: unknown): CodexChatLaneId {
  return text(value, '') === 'ion_system' ? 'ion_system' : 'codex_general';
}

function ionPipelinePhaseRows(
  stages: Array<Record<string, unknown>>,
  chainSteps: Array<Record<string, unknown>>,
  workerActive: boolean,
) {
  const fallbackStages = [
    { stage_id: 'persona_ingress', label: 'PERSONA IN', role_id: 'role.persona_interface', description: 'Operator intake through the persona front door.', status: 'ready' },
    { stage_id: 'relay_ingress', label: 'RELAY', role_id: 'role.relay', description: 'Packetize and relay the request into ION.', status: 'pending' },
    { stage_id: 'steward_route', label: 'STEWARD', role_id: 'role.steward', description: 'Route, classify authority, and integrate evidence.', status: 'pending' },
    { stage_id: 'vizier_plan', label: 'VIZIER', role_id: 'role.vizier', description: 'Shape architecture and planning pressure.', status: 'pending' },
    { stage_id: 'mason_codex_work', label: 'MASON', role_id: 'role.mason', description: 'Execute bounded implementation work through Codex.', status: workerActive ? 'working' : 'pending' },
    { stage_id: 'nemesis_verify', label: 'NEMESIS', role_id: 'role.nemesis', description: 'Audit proof, contradictions, regressions, and gates.', status: 'pending' },
    { stage_id: 'relay_return', label: 'RELAY RETURN', role_id: 'role.relay', description: 'Package the proof return back to the front door.', status: 'pending' },
    { stage_id: 'persona_response', label: 'PERSONA OUT', role_id: 'role.persona_interface', description: 'Answer the operator with visible protocol boundaries.', status: 'pending' },
  ];
  const sourceStages = stages.length ? stages : fallbackStages;
  return sourceStages.map((stage, index) => {
    const stageId = text(stage.stage_id || stage.step_id, `stage_${index}`);
    const chain = chainSteps.find((step) => text(step.step_id || step.stage_id, '') === stageId)
      || chainSteps.find((step) => text(step.label, '').toLowerCase() === text(stage.label, '').toLowerCase())
      || {};
    const label = text(stage.label || chain.label || stageId, stageId).toUpperCase();
    const roleId = text(stage.role_id || chain.role_id || ionRoleForStage(stageId, label), 'role.steward');
    const status = text(stage.status || chain.status || (workerActive && stageId.includes('mason') ? 'working' : index === 0 ? 'ready' : 'pending'), 'pending');
    const normalizedStatus = status.toLowerCase();
    const tone = normalizedStatus.includes('block') || normalizedStatus.includes('fail')
      ? 'blocked'
      : normalizedStatus.includes('work') || normalizedStatus.includes('queue') || normalizedStatus.includes('active')
        ? 'active'
        : normalizedStatus.includes('ready') || normalizedStatus.includes('project')
          ? 'ready'
          : 'pending';
    return {
      stageId,
      label,
      roleId,
      status,
      tone,
      detail: text(stage.description || chain.phase || chain.detail || chain.summary, 'ION role phase'),
    };
  });
}

function ionRoleForStage(stageId: string, label: string) {
  const source = `${stageId} ${label}`.toLowerCase();
  if (source.includes('persona')) return 'role.persona_interface';
  if (source.includes('relay')) return 'role.relay';
  if (source.includes('vizier')) return 'role.vizier';
  if (source.includes('mason')) return 'role.mason';
  if (source.includes('nemesis')) return 'role.nemesis';
  if (source.includes('scribe')) return 'role.scribe';
  return 'role.steward';
}

function createClientId(prefix: string) {
  const cryptoApi = typeof globalThis !== 'undefined' ? globalThis.crypto : undefined;
  if (cryptoApi && typeof cryptoApi.randomUUID === 'function') return `${prefix}_${cryptoApi.randomUUID()}`;
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
}

function pendingTurnHasServerReceipt(turn: PendingChatTurn, receipts: ServerUserTurnReceipt[]) {
  const pendingClientId = text(turn.clientId, '');
  if (pendingClientId && receipts.some((receipt) => text(receipt.clientId, '') === pendingClientId && receipt.hasServerWork)) return true;
  const pendingMessage = normalizeReceiptMessage(turn.message);
  if (!pendingMessage) return false;
  const pendingTime = Date.parse(text(turn.createdAt, '')) || 0;
  return receipts.some((receipt) => {
    if (!receipt.hasServerWork) return false;
    if (normalizeReceiptMessage(receipt.message) !== pendingMessage) return false;
    const receiptTime = Date.parse(text(receipt.createdAt, '')) || 0;
    if (!pendingTime || !receiptTime) return true;
    return receiptTime >= pendingTime - 5000;
  });
}

function normalizeReceiptMessage(value: unknown) {
  return text(value, '').replace(/\s+/g, ' ').trim();
}

function serverTurnGroupHasWork(group: Record<string, unknown>) {
  return Boolean(
    records(group.assistant_turns).length
    || records(group.execution_turns).length
    || records(group.context_turns).length
    || records(group.other_turns).length
    || records(group.return_records).length
    || records(record(group.turn_trace).events).length,
  );
}

function sanitizeOpenChatTab(value: unknown): OpenChatTab | null {
  const raw = record(value);
  const sessionId = text(raw.sessionId, '');
  if (!sessionId) return null;
  const openedAt = text(raw.openedAt, new Date().toISOString());
  return {
    id: text(raw.id, tabIdForSession(sessionId)),
    kind: 'archive',
    sessionId,
    title: text(raw.title || raw.thread_name || sessionId, sessionId),
    subtitle: text(raw.subtitle, ''),
    projectLabel: text(raw.projectLabel, ''),
    model: text(raw.model, ''),
    isCurrent: raw.isCurrent === true || text(raw.isCurrent, '').toLowerCase() === 'true',
    windowStart: undefined,
    openedAt,
    lastOpenedAt: text(raw.lastOpenedAt || raw.last_opened_at, openedAt),
    lastClosedAt: text(raw.lastClosedAt || raw.last_closed_at, ''),
    lastViewedAt: text(raw.lastViewedAt, new Date().toISOString()),
  };
}

function sessionAttached(session: IonCodexConversationArchiveSession, attachments: Array<Record<string, unknown>>) {
  return attachments.some((attachment) => text(attachment.session_id, '') === session.session_id && text(attachment.status, 'active') === 'active');
}

function formatSessionTime(session: IonCodexConversationArchiveSession) {
  const timestamp = sessionTimestamp(session);
  if (!timestamp) return text(session.updated_at || session.history_latest_ts || session.created_at, 'time unknown');
  const date = new Date(timestamp);
  return date.toLocaleString(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatCompactDate(value: unknown) {
  const raw = text(value, '');
  if (!raw) return '';
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleString(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function resolveCodexChatAgentIdentity(
  runtime: IonCockpitViewModel,
  queueTelemetry: Record<string, unknown>,
  queueTelemetryRun: Record<string, unknown>,
  rolePhaseContract: Record<string, unknown>,
  agentsAndRoles: Record<string, unknown>,
): CodexChatAgentIdentity {
  const agentControlPlane = record(runtime.agent_control_plane);
  const rosterAgents = records(agentControlPlane.agents);
  const participants = records(runtime.joc_comms?.participants);
  const activeRun = record(queueTelemetry.run || queueTelemetryRun);
  const lifecycle = record(queueTelemetry.latest_worker_lifecycle_event || activeRun.latest_worker_lifecycle_event);
  const activeRoleId = text(
    queueTelemetry.agent_role_id
    || queueTelemetryRun.agent_role_id
    || activeRun.agent_role_id
    || lifecycle.agent_role_id
    || '',
    '',
  );
  const activeDisplayName = text(
    queueTelemetry.agent_display_name
    || queueTelemetryRun.agent_display_name
    || activeRun.agent_display_name
    || lifecycle.agent_display_name
    || '',
    '',
  );
  const activeAgent = activeRoleId ? findAgentIdentityRecord(rosterAgents, activeRoleId) : null;
  const fallbackAgent = findAgentIdentityRecord(rosterAgents, 'role.codex_carrier_steward')
    || findAgentIdentityRecord(participants, 'role.codex_carrier_steward')
    || rosterAgents.find((agent) => text(agent.display_name, '').toLowerCase() === 'codex_carrier_steward')
    || participants.find((participant) => text(participant.display_name, '').toLowerCase() === 'codex_carrier_steward')
    || null;
  const sourceRecord = activeAgent || fallbackAgent || {};
  const roleId = text(activeRoleId || sourceRecord.role_id || sourceRecord.agent_id || sourceRecord.participant_id || 'role.codex_carrier_steward', 'role.codex_carrier_steward');
  const displayName = compactAgentDisplayName(text(activeDisplayName || sourceRecord.display_name || roleId, 'ION CODEX CARRIER'));
  const workerPid = text(queueTelemetry.active_worker_pid || activeRun.pid || lifecycle.worker_pid || lifecycle.pid || '', '');
  const runId = text(queueTelemetry.active_run_id || activeRun.run_id || lifecycle.run_id || '', '');
  const requestId = text(queueTelemetry.request_id || activeRun.request_id || lifecycle.request_id || '', '');
  const instanceId = workerPid ? `pid ${workerPid}` : runId ? shortOperationalId(runId) : shortOperationalId(roleId);
  const domain = text(
    sourceRecord.registry_primary_domain
    || sourceRecord.primary_domain
    || sourceRecord.domain_id
    || sourceRecord.domain_display
    || 'domain.codex_carrier_sync',
    'domain.codex_carrier_sync',
  );
  const carrier = text(sourceRecord.backend_carrier_id || sourceRecord.carrier_id || record(agentsAndRoles.spawn_plan).carrier || 'codex_cli', 'codex_cli');
  const source = activeRoleId ? 'worker telemetry' : sourceRecord.display_name ? 'agent registry' : 'carrier fallback';
  const roleMode = text(rolePhaseContract.mode || rolePhaseContract.role_phase_mode || 'single_carrier_sequential', 'single_carrier_sequential').replaceAll('_', ' ');
  const runDetail = runId ? `${shortOperationalId(runId)}${requestId ? ` / ${shortOperationalId(requestId)}` : ''}` : 'no active worker id';
  const detail = `${roleMode} / ${runDetail}`;
  return {
    displayName,
    roleId,
    instanceId,
    carrier,
    domain,
    source,
    detail,
    title: `${displayName} / ${roleId} / ${instanceId} / ${carrier}`,
  };
}

function findAgentIdentityRecord(recordsToSearch: Array<Record<string, unknown>>, roleId: string) {
  const normalizedRoleId = text(roleId, '').toLowerCase();
  if (!normalizedRoleId) return null;
  return recordsToSearch.find((recordToSearch) => {
    const candidates = [
      recordToSearch.role_id,
      recordToSearch.agent_id,
      recordToSearch.participant_id,
      record(recordToSearch.communication_profile).role_id,
    ].map((candidate) => text(candidate, '').toLowerCase());
    return candidates.includes(normalizedRoleId);
  }) ?? null;
}

function compactAgentDisplayName(value: string) {
  const normalized = text(value, 'ION CODEX CARRIER').replace(/[._-]+/g, ' ').replace(/\s+/g, ' ').trim();
  if (!normalized) return 'ION CODEX CARRIER';
  if (normalized.toLowerCase() === 'codex') return 'ION CODEX CARRIER';
  return normalized;
}

function shortOperationalId(value: unknown) {
  const normalized = text(value, '');
  if (!normalized) return '';
  const last = normalized.split('/').filter(Boolean).pop() || normalized;
  if (last.length <= 34) return last;
  return `${last.slice(0, 18)}...${last.slice(-10)}`;
}

function capsuleHealthState(capsule: Record<string, unknown>) {
  const ok = Boolean(capsule.ok);
  const recentRows = records(capsule.recent_rows);
  const latestDate = text(recentRows[recentRows.length - 1]?.date, '');
  const ageDays = latestDate ? Math.floor((Date.now() - new Date(`${latestDate}T00:00:00`).getTime()) / 86400000) : 999;
  if (!ok) {
    return {
      detail: text(capsule.path, 'context floor projection missing'),
      kind: 'context_floor',
      label: 'blocked',
      tone: 'blocked',
    };
  }
  if (ageDays > 1) {
    return {
      detail: `${text(capsule.entry_count, 0)} entries / last row ${latestDate || 'unknown'}`,
      kind: 'context_floor',
      label: 'stale',
      tone: 'watch',
    };
  }
  return {
    detail: `${text(capsule.entry_count, 0)} entries / hot context current`,
    kind: 'context_floor',
    label: 'healthy',
    tone: 'ready',
  };
}

function modelOptionList(
  fallback: string,
  sessions: IonCodexConversationArchiveSession[],
  chat: IonCockpitViewModel['codex_capsule_chat'],
  queueTelemetry: Record<string, unknown>,
  queueTelemetryRun: Record<string, unknown>,
) {
  const profileSurface = record(record(chat?.model_moves).profiles);
  const profileMap = record(profileSurface.profiles);
  const profileModels = Object.entries(profileMap).map(([slug, profile]) => text(record(profile).codex_model_slug || slug, ''));
  return uniqueStrings([
    fallback,
    text(record(chat?.response_carrier).selected_model, ''),
    text(record(record(chat?.chat_engine).model_move).selected_model, ''),
    ...profileModels,
    'gpt-5.5',
    'gpt-5.4',
    'gpt-5.4-mini',
    'gpt-5.3-codex',
    'gpt-5.3-codex-spark',
    text(queueTelemetry.model, ''),
    text(queueTelemetryRun.model, ''),
    ...sessions.map((session) => text(session.model, '')),
  ]).filter((option) => !['auto', 'default', 'codex default'].includes(option.toLowerCase())).slice(0, 16);
}

function durationSeconds(value: unknown) {
  if (typeof value === 'number' && Number.isFinite(value)) return Math.max(0, Math.floor(value));
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? Math.max(0, Math.floor(parsed)) : 0;
  }
  return 0;
}

function formatElapsedDuration(seconds: number) {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) return remainingSeconds ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

function sessionDrawerStatus(
  session: IonCodexConversationArchiveSession,
  busy: boolean,
  open: boolean,
  working: boolean,
  workingDuration: string,
) {
  if (busy) return 'loading';
  if (working) return `working ${workingDuration || 'now'}`;
  if (session.is_current_session) return 'live active';
  if (open) return 'open';
  return sessionActivity(session);
}

function latestAssistantText(groups: Array<Record<string, unknown>>) {
  for (const group of [...groups].reverse()) {
    const assistantTurns = records(group.assistant_turns);
    for (const turn of [...assistantTurns].reverse()) {
      const value = text(turn.message || record(turn.chat_engine).assistant_response, '');
      if (value) return value;
    }
  }
  return '';
}

function latestAssistantTurnKey(groups: Array<Record<string, unknown>>) {
  for (const group of [...groups].reverse()) {
    const assistantTurns = records(group.assistant_turns);
    for (const turn of [...assistantTurns].reverse()) {
      return messageSourceKey(turn, turn.created_at);
    }
  }
  return '';
}

function liveTranscriptNewestKey(groups: Array<Record<string, unknown>>, latestAssistantKey: string) {
  const latestGroup = groups[groups.length - 1];
  if (!latestGroup) return latestAssistantKey;
  const userTurn = record(latestGroup.user_turn);
  const groupKey = text(latestGroup.group_id || latestGroup.turn_id || userTurn.turn_id || userTurn.created_at, '');
  return [groupKey, latestAssistantKey].filter(Boolean).join(':');
}

function pendingChatTurnGroup(turn: PendingChatTurn, tick: number, activity?: PendingChatActivitySnapshot) {
  const elapsed = pendingElapsedLabel(turn.createdAt, tick);
  const status = pendingChatTurnStatus(turn);
  const snapshot = activity ?? {
    workerActive: false,
    workerStatus: 'idle',
    workerDuration: '',
    queuedRequestCount: 0,
  };
  const responseRunRefs = pendingActivityRefs(snapshot, turn);
  const events = pendingChatTurnEvents(turn, elapsed, snapshot);
  const assistantPreview = text(turn.assistantPreview, '');
  return {
    group_id: turn.clientId,
    pending: true,
    pending_status: status,
    created_at: turn.createdAt,
    user_turn: {
      turn_id: `${turn.clientId}:user`,
      lane_id: turn.laneId,
      author: 'operator',
      kind: 'chat_turn',
      message: turn.message,
      created_at: turn.createdAt,
      execution_mode: turn.mode,
      agent_mode: turn.agentMode,
      codex_model_override: {
        selected_model: turn.selectedModel,
        selected_reasoning_effort: turn.thinkingMode,
      },
      target_session_id: turn.targetSessionId,
      codex_session_target_mode: turn.targetSessionId ? 'resume_selected_session' : turn.newCodexSession ? 'new_cockpit_session' : 'cockpit_active_session',
      codex_session_transport: turn.codexSessionTransport,
      selected_context_refs: turn.contextRefs,
      pending: true,
      production_authority: false,
      live_execution_authority: false,
    },
    assistant_turns: assistantPreview ? [{
      turn_id: `${turn.clientId}:assistant-preview`,
      lane_id: turn.laneId,
      author: 'codex_cli',
      kind: 'assistant_response',
      message: assistantPreview,
      created_at: turn.settledAt || turn.createdAt,
      response_status: turn.responseStatus,
      source_refs: responseRunRefs,
      pending_preview: true,
      production_authority: false,
      live_execution_authority: false,
    }] : [],
    execution_turns: isQueueExecutionMode(turn.mode) ? [{
      turn_id: `${turn.clientId}:execution`,
      lane_id: turn.laneId,
      kind: 'execution_status',
      author: 'codex_context',
      created_at: turn.createdAt,
      queue_status: turn.status === 'failed' ? 'failed' : turn.status === 'settled' ? 'syncing' : 'pending',
      status: snapshot.workerActive ? 'running' : status,
      message: pendingExecutionMessage(turn, elapsed, snapshot),
      request_id: turn.clientId,
      source_refs: uniqueStrings([...turn.contextRefs, ...responseRunRefs]),
    }] : [],
    context_turns: [],
    other_turns: [],
    return_records: [],
    turn_trace: {
      turn_id: turn.clientId,
      event_count: events.length,
      events,
    },
  };
}

function pendingChatTurnEvents(turn: PendingChatTurn, elapsed: string, activity: PendingChatActivitySnapshot) {
  const responseRun = record(activity.responseRun);
  const responseRunPath = text(responseRun.path || responseRun.run_packet_path || turn.responseRunPath, '');
  const responseStatus = text(responseRun.status || turn.responseStatus, '');
  const responseSurface = text(turn.responseSurface || responseRun.codex_cli_surface, '');
  const targetSessionId = text(turn.targetSessionId, '');
  const transport = turn.codexSessionTransport || (targetSessionId ? 'app_server' : 'raw_cli');
  const responseRefs = pendingActivityRefs(activity, turn);
  const events: Array<Record<string, unknown>> = [
    {
      id: `${turn.clientId}:prompt-visible`,
      event_type: 'user_prompt_visible',
      label: 'Prompt visible',
      status: 'local',
      detail: 'The prompt is rendered in the chat immediately while the server records the turn.',
      source_refs: [],
    },
    {
      id: `${turn.clientId}:codex-session-target`,
      event_type: 'codex_session_target',
      label: 'Codex session target',
      status: targetSessionId ? 'resume selected saved session via thread API' : turn.newCodexSession ? 'start new Codex session' : 'active cockpit Codex session',
      detail: targetSessionId
        ? `This prompt is being sent through Codex app-server turn/start for ${targetSessionId}${turn.targetSessionTitle ? ` (${turn.targetSessionTitle})` : ''}; this is Codex thread API control, not terminal key injection.`
        : turn.newCodexSession
          ? 'This prompt is being sent through a fresh codex exec session, equivalent to starting a new Codex CLI thread.'
          : 'No saved session tab is selected; this prompt uses the cockpit Codex CLI active thread.',
      source_refs: targetSessionId ? [`codex-session:${targetSessionId}`] : [],
      tool_name: targetSessionId && transport === 'app_server' ? 'codex app-server turn/start' : targetSessionId ? 'codex exec resume' : 'codex exec',
    },
    {
      id: `${turn.clientId}:context`,
      event_type: 'context_mount',
      label: 'Context mount',
      status: turn.contextRefs.length ? `${turn.contextRefs.length} refs` : 'default context',
      detail: turn.contextRefs.length ? 'Selected context refs are attached to this prompt.' : 'Default Codex context floor will be mounted by the chat engine.',
      source_refs: turn.contextRefs,
    },
    {
      id: `${turn.clientId}:thinking`,
      event_type: 'thinking_status',
      label: 'Thinking/status',
      status: turn.thinkingMode,
      detail: 'Reasoning effort is requested as status telemetry; captured Codex CLI thinking/status events and usage tokens will appear when present.',
      source_refs: [],
    },
  ];
  if (pendingWorkerActivityVisible(activity)) {
    events.push({
      id: `${turn.clientId}:worker`,
      event_type: 'runner_live_status',
      label: 'Live worker',
      status: activity.workerActive ? `working ${activity.workerDuration || elapsed}` : activity.workerStatus,
      detail: pendingWorkerActivityDetail(activity),
      source_refs: responseRefs,
    });
  }
  if (responseRunPath) {
    events.push({
      id: `${turn.clientId}:response-run`,
      event_type: 'response_run',
      label: responseSurface === 'codex_app_server_turn_start' ? 'Codex thread API run' : responseSurface ? 'Codex CLI run' : 'Response run',
      status: responseStatus || 'recorded',
      detail: pendingResponseRunDetail(responseRun, turn),
      source_refs: responseRefs,
      tool_name: responseSurface === 'codex_app_server_turn_start' ? 'codex app-server turn/start' : responseSurface === 'codex_exec_resume' ? 'codex exec resume' : 'codex exec',
    });
  }
  if (isQueueExecutionMode(turn.mode)) {
    events.push({
      id: `${turn.clientId}:queue`,
      event_type: 'queue_dispatch',
      label: turn.mode === 'queue_and_start' ? 'Queue + runner' : 'Queue',
      status: turn.status === 'failed' ? 'failed' : turn.status === 'settled' ? 'syncing' : `pending ${elapsed}`,
      detail: pendingExecutionMessage(turn, elapsed, activity),
      source_refs: uniqueStrings([...turn.contextRefs, ...responseRefs]),
      tool_name: 'ion_request_codex_work_packet',
    });
  } else {
    events.push({
      id: `${turn.clientId}:carrier`,
      event_type: 'codex_chat_response_carrier',
      label: turn.responseMode === 'codex_app_server' ? 'Codex thread API working' : turn.responseMode === 'raw_codex_cli' ? 'Codex CLI working' : 'AI working',
      status: turn.status === 'failed' ? 'failed' : turn.status === 'settled' ? (turn.responseStatus || 'syncing') : `working ${elapsed}`,
      detail: pendingCarrierActivityDetail(turn, elapsed, activity),
      source_refs: responseRefs,
    });
  }
  if (turn.status === 'failed') {
    events.push({
      id: `${turn.clientId}:failed`,
      event_type: 'chat_turn_failed',
      label: 'Request failed',
      status: 'failed',
      detail: turn.error || 'chat_turn_failed',
      source_refs: [],
    });
  } else if (turn.status === 'settled') {
    events.push({
      id: `${turn.clientId}:settled`,
      event_type: 'chat_turn_sync',
      label: 'Response recorded',
      status: 'refreshing',
      detail: 'The server accepted the turn; the cockpit projection is refreshing into the durable transcript.',
      source_refs: [],
    });
  }
  return events;
}

function pendingExecutionMessage(turn: PendingChatTurn, elapsed: string, activity?: PendingChatActivitySnapshot) {
  if (turn.status === 'failed') return turn.error || 'Chat turn failed before queue status was returned.';
  if (turn.status === 'settled') return 'Turn accepted; refreshing queue and transcript projection.';
  if (activity?.workerActive) return `Codex worker is active (${activity.workerDuration || elapsed}); ${activity.workerStatus || 'status pending'}.`;
  if (turn.mode === 'queue_and_start') return `Queue packet is being recorded and runner start is being requested (${elapsed}).`;
  return `Queue packet is being recorded (${elapsed}).`;
}

function pendingCarrierActivityDetail(turn: PendingChatTurn, elapsed: string, activity: PendingChatActivitySnapshot) {
  const base = `Mode ${turn.mode}; model ${turn.selectedModel}; thinking ${turn.thinkingMode}.`;
  if (turn.status === 'settled' && turn.assistantPreview) return `${base} Response captured; refreshing the durable transcript projection.`;
  if (turn.codexSessionTransport === 'app_server') return `${base} Codex app-server thread API is handling the selected saved session (${elapsed}). Output will appear when the response lands.`;
  if (activity.workerActive) return `${base} Codex worker is active (${activity.workerDuration || elapsed}); output will appear when the response lands.`;
  return `${base} Output will replace this pending card when the response lands.`;
}

function pendingWorkerActivityVisible(activity: PendingChatActivitySnapshot) {
  const status = text(activity.workerStatus, '').toLowerCase();
  return Boolean(
    activity.workerActive
    || activity.workerDuration
    || activity.queuedRequestCount > 0
    || status.includes('running')
    || status.includes('started')
    || status.includes('prepared')
  );
}

function pendingWorkerActivityDetail(activity: PendingChatActivitySnapshot) {
  const parts = [
    activity.workerActive ? 'active worker' : '',
    activity.workerDuration ? `elapsed ${activity.workerDuration}` : '',
    activity.queuedRequestCount ? `${activity.queuedRequestCount} queued` : '',
    activity.workerStatus ? `status ${activity.workerStatus}` : '',
  ].filter(Boolean);
  return parts.join(' / ') || 'Waiting for live worker telemetry.';
}

function pendingResponseRunDetail(run: Record<string, unknown>, turn: PendingChatTurn) {
  const model = text(run.selected_model || turn.selectedModel, '');
  const effort = text(run.selected_reasoning_effort || turn.thinkingMode, '');
  const finding = text(run.finding, '');
  return [
    model ? `model ${model}` : '',
    effort ? `thinking ${effort}` : '',
    finding ? `finding ${finding}` : '',
  ].filter(Boolean).join(' / ') || 'Codex response run is visible in the cockpit projection.';
}

function pendingActivityRefs(activity: PendingChatActivitySnapshot, turn?: PendingChatTurn) {
  const run = record(activity.responseRun);
  return uniqueStrings([
    text(turn?.responseRunPath, ''),
    text(run.path || run.run_packet_path, ''),
    text(run.receipt_path, ''),
    text(run.latest_status_path, ''),
    text(run.latest_return_path, ''),
    text(run.events_path, ''),
    text(run.stdout_path, ''),
    text(run.stderr_path, ''),
  ].filter(Boolean));
}

function latestResponseRunForPendingTurn(turn: PendingChatTurn, runs: Array<Record<string, unknown>>) {
  if (!runs.length) return undefined;
  const explicitPath = text(turn.responseRunPath, '');
  if (explicitPath) {
    const explicit = runs.find((run) => text(run.path || run.run_packet_path, '') === explicitPath);
    if (explicit) return explicit;
    return {
      path: explicitPath,
      status: turn.responseStatus || 'recorded',
      selected_model: turn.selectedModel,
      selected_reasoning_effort: turn.thinkingMode,
      codex_cli_surface: turn.responseSurface,
      active_thread_id: turn.responseThreadId,
    };
  }
  const started = Date.parse(turn.createdAt);
  if (Number.isFinite(started)) {
    const windowStart = started - 15000;
    const visibleRun = runs.find((run) => {
      const created = Date.parse(text(run.created_at, ''));
      return Number.isFinite(created) && created >= windowStart;
    });
    if (visibleRun) return visibleRun;
  }
  return undefined;
}

function pendingChatTurnStatus(turn: PendingChatTurn) {
  if (turn.status === 'failed') return 'failed';
  if (turn.status === 'settled') return 'syncing';
  return 'working';
}

function pendingElapsedLabel(createdAt: string, tick: number) {
  void tick;
  const started = Date.parse(createdAt);
  if (!Number.isFinite(started)) return 'now';
  return formatElapsedDuration(Math.max(0, Math.floor((Date.now() - started) / 1000)));
}

function isQueueExecutionMode(mode: ExecutionModeId) {
  return mode === 'queue_for_codex' || mode === 'queue_and_start';
}

function messageSourceKey(turn: Record<string, unknown> | undefined, fallback: unknown) {
  return text(turn?.turn_id || turn?.id || turn?.event_id || turn?.attachment_id || fallback, '');
}

function messageRoleGroup(role: string) {
  const value = safeClass(role).replaceAll('_', '-');
  if (['operator', 'user', 'human'].includes(value)) return 'user';
  if (['assistant', 'codex-chat-engine', 'codex-cli', 'agent-message', 'codex', 'ai'].includes(value)) return 'ai';
  if (['tool-call', 'tool-result', 'function-call', 'function-call-output', 'execution', 'execution-status', 'custom-tool-call'].includes(value)) return 'trace';
  if (['mini-auto-post', 'context', 'ion-context', 'developer-context'].includes(value)) return 'context';
  return 'event';
}

function archiveMessageRoleGroup(item: Record<string, unknown>, role: string) {
  const lane = safeClass(text(item.visual_lane, '')).replaceAll('_', '-');
  if (['user', 'ai', 'trace', 'context', 'event', 'diff', 'compaction'].includes(lane)) return lane;
  return messageRoleGroup(role);
}

function messageRoleLabel(role: string, roleGroup: string) {
  const cleaned = text(role, 'event').replaceAll('_', ' ');
  if (roleGroup === 'trace') return `trace / ${cleaned}`;
  if (roleGroup === 'context') return `context / ${cleaned}`;
  if (roleGroup === 'diff') return `diff / ${cleaned}`;
  if (roleGroup === 'compaction') return `compaction / ${cleaned}`;
  if (roleGroup === 'event') return `event / ${cleaned}`;
  return cleaned;
}

function archiveMessageLabel(item: Record<string, unknown>, role: string, roleGroup: string) {
  const kind = text(item.message_kind, '').replaceAll('_', ' ');
  const base = messageRoleLabel(role, roleGroup);
  if (!kind || ['assistant reply', 'user message'].includes(kind)) return base;
  return `${base} / ${kind}`;
}

function archiveTranscriptBlocks(items: Array<Record<string, unknown>>): ArchiveTranscriptBlock[] {
  const blocks: ArchiveTranscriptBlock[] = [];
  let currentWork: Array<Record<string, unknown>> = [];
  const flushWork = () => {
    if (!currentWork.length) return;
    blocks.push(createArchiveWorkBlock(currentWork, blocks.length));
    currentWork = [];
  };
  items.forEach((item, index) => {
    const roleGroup = archiveMessageRoleGroup(item, text(item.role, 'archive'));
    if (roleGroup === 'user') {
      flushWork();
      blocks.push({ kind: 'message', item, key: archiveMessageKey(item, index) });
      return;
    }
    currentWork.push(item);
  });
  flushWork();
  return blocks;
}

function createArchiveWorkBlock(items: Array<Record<string, unknown>>, index: number): ArchiveTranscriptBlock {
  return {
    kind: 'work',
    key: `archive-work-${index}-${archiveMessageKey(items[0] ?? {}, index)}`,
    items,
    assistantItems: items.filter((item) => archiveWorkBucket(item) === 'assistant'),
    toolItems: items.filter((item) => archiveWorkBucket(item) === 'tools'),
    contextItems: items.filter((item) => archiveWorkBucket(item) === 'context'),
    eventItems: items.filter((item) => archiveWorkBucket(item) === 'events'),
    editItems: items.filter((item) => archiveWorkBucket(item) === 'edits'),
    thinkingItems: items.filter((item) => archiveWorkBucket(item) === 'thinking'),
    runItems: items.filter((item) => archiveWorkBucket(item) === 'runs'),
    proofItems: items.filter((item) => archiveWorkBucket(item) === 'proof'),
    rawItems: items,
  };
}

function archiveWorkBucket(item: Record<string, unknown>): AssistantWorkTabId {
  const roleGroup = archiveMessageRoleGroup(item, text(item.role, 'archive'));
  const eventType = safeClass(text(item.message_kind || item.event_type || item.kind || item.type || item.detail_label, '')).replaceAll('_', '-');
  const joined = [
    eventType,
    text(item.role, ''),
    text(item.detail_label, ''),
    text(item.source_type, ''),
    text(item.text || item.snippet || item.message || item.summary, ''),
  ].join(' ').toLowerCase();
  if (roleGroup === 'ai') return 'assistant';
  if (joined.includes('thinking') || joined.includes('reasoning') || joined.includes('model-move') || joined.includes('model move')) return 'thinking';
  if (joined.includes('response-run') || joined.includes('response run') || joined.includes('runner') || joined.includes('carrier')) return 'runs';
  if (joined.includes('proof') || joined.includes('task-return') || joined.includes('task return') || joined.includes('return')) return 'proof';
  if (roleGroup === 'trace') return 'tools';
  if (roleGroup === 'diff') return 'edits';
  if (roleGroup === 'context' || roleGroup === 'compaction') return 'context';
  return 'events';
}

function archiveWorkItemsForTab(block: Extract<ArchiveTranscriptBlock, { kind: 'work' }>, tab: AssistantWorkTabId) {
  if (tab === 'assistant') return block.assistantItems;
  if (tab === 'thinking') return block.thinkingItems;
  if (tab === 'tools') return block.toolItems;
  if (tab === 'context') return block.contextItems;
  if (tab === 'edits') return block.editItems;
  if (tab === 'runs') return block.runItems;
  if (tab === 'proof') return block.proofItems;
  if (tab === 'raw') return block.rawItems;
  return block.eventItems;
}

function archiveWorkSummary(block: Extract<ArchiveTranscriptBlock, { kind: 'work' }>) {
  return [
    block.assistantItems.length ? `${block.assistantItems.length} replies` : '',
    block.thinkingItems.length ? `${block.thinkingItems.length} thinking` : '',
    block.toolItems.length ? `${block.toolItems.length} tools` : '',
    block.contextItems.length ? `${block.contextItems.length} context` : '',
    block.editItems.length ? `${block.editItems.length} edits` : '',
    block.runItems.length ? `${block.runItems.length} runs` : '',
    block.proofItems.length ? `${block.proofItems.length} proof` : '',
    block.eventItems.length ? `${block.eventItems.length} events` : '',
  ].filter(Boolean).join(' / ') || `${block.items.length} items`;
}

function archiveItemText(item: Record<string, unknown>) {
  return text(item.text || item.snippet || item.message || item.summary, '');
}

function assistantWorkTabs(counts: {
  assistantCount: number;
  thinkingCount: number;
  toolCount: number;
  contextCount: number;
  eventCount: number;
  editCount: number;
  runCount: number;
  proofCount: number;
  agentCount: number;
  rawCount: number;
}) {
  return [
    { id: 'assistant' as const, label: 'ASSISTANT', count: counts.assistantCount },
    { id: 'thinking' as const, label: 'THINKING', count: counts.thinkingCount },
    { id: 'tools' as const, label: 'TOOLS', count: counts.toolCount },
    { id: 'context' as const, label: 'CONTEXT', count: counts.contextCount },
    { id: 'edits' as const, label: 'EDITS', count: counts.editCount },
    { id: 'runs' as const, label: 'RUNS', count: counts.runCount },
    { id: 'proof' as const, label: 'PROOF', count: counts.proofCount },
    { id: 'agents' as const, label: 'AGENTS', count: counts.agentCount },
    { id: 'events' as const, label: 'EVENTS', count: counts.eventCount },
    { id: 'raw' as const, label: 'RAW', count: counts.rawCount },
  ];
}

function assistantEventBucket(event: Record<string, unknown>): AssistantWorkTabId {
  const eventType = safeClass(text(event.event_type || event.kind || event.type || event.label, '')).replaceAll('_', '-');
  const joined = [
    eventType,
    text(event.label, ''),
    text(event.tool_name, ''),
    text(event.detail, ''),
    text(event.status, ''),
  ].join(' ').toLowerCase();
  if (joined.includes('assistant-work-route') || joined.includes('agent')) return 'agents';
  if (
    joined.includes('thinking')
    || joined.includes('reasoning')
    || joined.includes('model-move')
    || joined.includes('model move')
    || Object.keys(record(event.model_move || event.codex_model_move)).length
  ) return 'thinking';
  if (
    joined.includes('response-run')
    || joined.includes('response run')
    || joined.includes('codex-chat-response-carrier')
    || joined.includes('response-carrier')
    || joined.includes('carrier')
    || joined.includes('stdout')
    || joined.includes('stderr')
    || text(event.latest_run_path || event.run_packet_path || event.events_path, '')
  ) return 'runs';
  if (
    joined.includes('proof')
    || joined.includes('task-return')
    || joined.includes('task return')
    || joined.includes('return-hydration')
    || text(event.latest_return_path, '')
  ) return 'proof';
  if (
    joined.includes('tool')
    || joined.includes('runner')
    || joined.includes('queue')
    || joined.includes('codex-exec')
    || joined.includes('execution')
  ) return 'tools';
  if (
    joined.includes('context')
    || joined.includes('capsule')
    || joined.includes('mini')
    || joined.includes('skill')
    || joined.includes('chat-engine')
    || joined.includes('route')
  ) return 'context';
  if (
    joined.includes('diff')
    || joined.includes('file')
    || joined.includes('edit')
    || stringList(event.touched_paths).length
    || stringList(event.path_refs).length
  ) return 'edits';
  return 'events';
}

function assistantEditRecords(returnRecords: Array<Record<string, unknown>>, traceEvents: Array<Record<string, unknown>>) {
  const traceEditEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'edits');
  const touchedPathRecords = returnRecords.flatMap((returnRecord) => {
    const touchedPaths = uniqueStrings([
      ...stringList(returnRecord.touched_paths),
      ...stringList(record(returnRecord.diff_stats).files),
    ]);
    return touchedPaths.map((path) => ({
      ...returnRecord,
      event_type: 'file_edit',
      label: 'Touched path',
      status: text(returnRecord.proof_status || returnRecord.status, 'recorded'),
      detail: path,
      source_refs: uniqueStrings([path, ...stringList(returnRecord.path_refs)]),
      touched_paths: [path],
    }));
  });
  return [
    ...touchedPathRecords,
    ...traceEditEvents,
  ];
}

function assistantProofRecords(returnRecords: Array<Record<string, unknown>>, traceEvents: Array<Record<string, unknown>>) {
  const traceProofEvents = traceEvents.filter((event) => assistantEventBucket(event) === 'proof');
  return [
    ...returnRecords.map((returnRecord) => ({
      ...returnRecord,
      event_type: text(returnRecord.event_type || returnRecord.kind, 'proof_return'),
      label: text(returnRecord.label || returnRecord.task_title || returnRecord.role, 'Task return / proof'),
      detail: text(returnRecord.task_output_preview || returnRecord.latest_return_path || returnRecord.summary || returnRecord.status, ''),
    })),
    ...traceProofEvents,
  ];
}

function assistantThinkingRecords({
  assistantTurns,
  traceEvents,
  turnTrace,
  userTurn,
}: {
  assistantTurns: Array<Record<string, unknown>>;
  traceEvents: Array<Record<string, unknown>>;
  turnTrace: Record<string, unknown>;
  userTurn: Record<string, unknown>;
}) {
  const recordsOut: Array<Record<string, unknown>> = [];
  for (const event of traceEvents) {
    if (assistantEventBucket(event) === 'thinking') recordsOut.push(event);
  }
  for (const turn of assistantTurns) {
    const modelMove = record(turn.codex_model_move || record(turn.chat_engine).model_move);
    if (!Object.keys(modelMove).length) continue;
    recordsOut.push({
      event_type: 'thinking_status',
      label: 'Model move',
      status: text(modelMove.selected_reasoning_effort, 'unknown'),
      detail: [
        `model ${text(modelMove.selected_model, 'unknown')}`,
        `work ${text(modelMove.work_class, 'unknown')}`,
        `stage ${text(modelMove.ion_stage_id, 'unknown')}`,
      ].join(' / '),
      model_move: modelMove,
      source_refs: stringList(turn.context_refs),
    });
  }
  const policyRecord = {
    event_type: 'thinking_policy',
    label: 'Thinking capture',
    status: record(turnTrace).raw_hidden_reasoning_exposed || userTurn.raw_hidden_reasoning_exposed ? 'raw text present' : 'status/usage',
    detail: 'Shows captured Codex CLI thinking/status events when present; otherwise shows model move, effort, route, tool, usage, and receipt telemetry.',
    raw_hidden_reasoning_exposed: Boolean(record(turnTrace).raw_hidden_reasoning_exposed || userTurn.raw_hidden_reasoning_exposed),
  };
  return dedupeEventsBySignature([...recordsOut, policyRecord]);
}

function assistantRunRecords({
  assistantTurns,
  executionTurns,
  traceEvents,
}: {
  assistantTurns: Array<Record<string, unknown>>;
  executionTurns: Array<Record<string, unknown>>;
  traceEvents: Array<Record<string, unknown>>;
}) {
  const runRecords = traceEvents.filter((event) => assistantEventBucket(event) === 'runs');
  for (const turn of assistantTurns) {
    const appServer = record(turn.codex_app_server);
    const appServerRun = record(appServer.run);
    if (Object.keys(appServer).length || Object.keys(appServerRun).length) {
      runRecords.push({
        ...appServerRun,
        event_type: 'response_run',
        label: 'Codex thread API run',
        status: text(appServer.status || appServerRun.status, 'recorded'),
        detail: text(appServer.finding || appServerRun.finding || appServerRun.receipt_path || appServerRun.latest_status_path, ''),
        response_mode: text(turn.response_mode || appServer.response_mode, 'codex_app_server'),
        active_thread_id: text(appServer.active_thread_id || appServerRun.active_thread_id_after || appServerRun.active_thread_id_before, ''),
        source_refs: uniqueStrings([
          text(appServerRun.run_packet_path || appServerRun.receipt_path, ''),
          text(appServerRun.latest_status_path, ''),
        ]),
        tool_name: 'codex app-server turn/start',
      });
    }
    const rawCodex = record(turn.raw_codex_cli);
    const rawRun = record(rawCodex.run);
    if (Object.keys(rawCodex).length || Object.keys(rawRun).length) {
      runRecords.push({
        ...rawRun,
        event_type: 'response_run',
        label: 'Codex CLI run',
        status: text(rawCodex.status || rawRun.status, 'recorded'),
        detail: text(rawCodex.finding || rawRun.finding || rawRun.run_packet_path || rawRun.latest_return_path, ''),
        response_mode: text(turn.response_mode || rawCodex.response_mode, 'raw_codex_cli'),
        active_thread_id: text(rawCodex.active_thread_id || rawRun.active_thread_id_after || rawRun.active_thread_id_before, ''),
        source_refs: uniqueStrings([
          text(rawRun.run_packet_path || rawRun.path, ''),
          text(rawRun.latest_return_path, ''),
          text(rawRun.stdout_path, ''),
          text(rawRun.stderr_path, ''),
          text(rawRun.prompt_path, ''),
        ]),
        tool_name: text(rawRun.codex_cli_surface, '') === 'codex_exec_resume' ? 'codex exec resume' : 'codex exec',
      });
    }
    const carrier = record(turn.response_carrier);
    const run = record(carrier.run);
    if (!Object.keys(carrier).length && !Object.keys(run).length) continue;
    runRecords.push({
      ...run,
      event_type: 'response_run',
      label: 'Response run',
      status: text(carrier.status || run.status, 'recorded'),
      detail: text(carrier.finding || carrier.response_text || run.run_packet_path || run.latest_return_path, ''),
      model_move: turn.codex_model_move,
      source_refs: uniqueStrings([
        text(run.run_packet_path || run.path, ''),
        text(run.latest_return_path, ''),
        text(run.events_path, ''),
        text(run.stdout_path, ''),
        text(run.stderr_path, ''),
      ]),
      tool_name: 'codex exec',
    });
  }
  for (const turn of executionTurns) {
    const runner = record(turn.runner_result);
    if (!Object.keys(runner).length) continue;
    runRecords.push({
      ...runner,
      event_type: 'runner',
      label: 'Runner result',
      status: text(runner.result || runner.finding || turn.status, 'recorded'),
      detail: text(runner.finding || runner.result || turn.packet_path, ''),
      source_refs: [text(turn.packet_path, '')].filter(Boolean),
      tool_name: 'ion_codex_queue_process_once',
    });
  }
  return dedupeEventsBySignature(runRecords);
}

function assistantRawDataRecords({
  assistantTurns,
  contextTurns,
  executionTurns,
  otherTurns,
  returnRecords,
  traceEvents,
  turnTrace,
  userTurn,
}: {
  assistantTurns: Array<Record<string, unknown>>;
  contextTurns: Array<Record<string, unknown>>;
  executionTurns: Array<Record<string, unknown>>;
  otherTurns: Array<Record<string, unknown>>;
  returnRecords: Array<Record<string, unknown>>;
  traceEvents: Array<Record<string, unknown>>;
  turnTrace: Record<string, unknown>;
  userTurn: Record<string, unknown>;
}) {
  return [
    { label: 'user_turn', status: text(userTurn.turn_id || userTurn.id, 'local'), payload: userTurn },
    { label: 'assistant_turns', status: assistantTurns.length, payload: assistantTurns },
    { label: 'execution_turns', status: executionTurns.length, payload: executionTurns },
    { label: 'context_turns', status: contextTurns.length, payload: contextTurns },
    { label: 'return_records', status: returnRecords.length, payload: returnRecords },
    { label: 'trace_events', status: traceEvents.length, payload: traceEvents },
    { label: 'turn_trace', status: text(turnTrace.turn_id, 'trace'), payload: turnTrace },
    { label: 'other_turns', status: otherTurns.length, payload: otherTurns },
  ].filter((item) => Object.keys(record(item.payload)).length || Array.isArray(item.payload));
}

function dedupeEventsBySignature(events: Array<Record<string, unknown>>) {
  const seen = new Set<string>();
  const deduped: Array<Record<string, unknown>> = [];
  for (const event of events) {
    const key = [
      text(event.event_type || event.kind || event.type, ''),
      text(event.label, ''),
      text(event.status, ''),
      text(event.detail, ''),
      text(event.path || event.packet_path || event.latest_return_path || event.latest_run_path, ''),
    ].join('|');
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(event);
  }
  return deduped;
}

function executionTurnEvent(turn: Record<string, unknown>) {
  return {
    ...turn,
    event_type: text(turn.kind || 'execution_status'),
    label: 'Execution request',
    status: text(turn.queue_status || turn.status || turn.result, ''),
    detail: text(turn.message || turn.request_id || turn.packet_path || turn.status, ''),
    source_refs: [text(turn.packet_path, '')].filter(Boolean),
    tool_name: 'ion_request_codex_work_packet',
  };
}

function contextTurnEvent(turn: Record<string, unknown>) {
  return {
    ...turn,
    event_type: text(turn.kind || 'context'),
    label: text(turn.kind, '') === 'mini_auto_post' ? 'Context refresh' : 'Context event',
    status: text(turn.status || turn.verdict, 'ready'),
    detail: contextTurnDisplayText(turn),
    source_refs: [
      text(turn.mini_ref, ''),
      text(turn.capsule_ref, ''),
    ].filter(Boolean),
  };
}

function otherTurnEvent(turn: Record<string, unknown>) {
  return {
    ...turn,
    event_type: text(turn.kind || turn.type || 'event'),
    label: text(turn.kind || turn.author || turn.role, 'Event'),
    status: text(turn.status || turn.verdict, ''),
    detail: text(turn.message || turn.summary || turn.path || turn.finding, ''),
  };
}

function assistantPanelSummary({
  executionTurns,
  contextTurns,
  otherTurns,
  returnRecords,
  traceEvents,
}: {
  executionTurns: Array<Record<string, unknown>>;
  contextTurns: Array<Record<string, unknown>>;
  otherTurns: Array<Record<string, unknown>>;
  returnRecords: Array<Record<string, unknown>>;
  traceEvents: Array<Record<string, unknown>>;
}) {
  return [
    executionTurns.length ? `${executionTurns.length} execution events` : '',
    contextTurns.length ? `${contextTurns.length} context events` : '',
    otherTurns.length ? `${otherTurns.length} other events` : '',
    returnRecords.length ? `${returnRecords.length} proof records` : '',
    traceEvents.length ? `${traceEvents.length} trace events` : '',
  ].filter(Boolean).join(', ') || 'assistant activity';
}

function assistantWorkPanelCopyText({
  agentEvents,
  assistantTurns,
  contextEvents,
  contextTurns,
  editRecords,
  executionTurns,
  generalEvents,
  otherTurns,
  proofRecords,
  rawRecords,
  runRecords,
  thinkingRecords,
  toolEvents,
  turnTrace,
}: {
  agentEvents: Array<Record<string, unknown>>;
  assistantTurns: Array<Record<string, unknown>>;
  contextEvents: Array<Record<string, unknown>>;
  contextTurns: Array<Record<string, unknown>>;
  editRecords: Array<Record<string, unknown>>;
  executionTurns: Array<Record<string, unknown>>;
  generalEvents: Array<Record<string, unknown>>;
  otherTurns: Array<Record<string, unknown>>;
  proofRecords: Array<Record<string, unknown>>;
  rawRecords: Array<Record<string, unknown>>;
  runRecords: Array<Record<string, unknown>>;
  thinkingRecords: Array<Record<string, unknown>>;
  toolEvents: Array<Record<string, unknown>>;
  traceEvents: Array<Record<string, unknown>>;
  turnTrace: Record<string, unknown>;
}) {
  return [
    'ASSISTANT WORK BLOCK',
    text(turnTrace.turn_id, '') ? `turn_id: ${text(turnTrace.turn_id)}` : '',
    formatCopySection('ASSISTANT', assistantTurns.map(assistantTurnCopyText)),
    formatCopySection('THINKING', thinkingRecords.map(assistantEventCopyText)),
    formatCopySection('TOOLS', [
      ...executionTurns.map(executionTurnEvent),
      ...toolEvents,
    ].map(assistantEventCopyText)),
    formatCopySection('CONTEXT', [
      ...contextTurns.map(contextTurnEvent),
      ...contextEvents,
    ].map(assistantEventCopyText)),
    formatCopySection('EDITS', editRecords.map(assistantEventCopyText)),
    formatCopySection('RUNS', runRecords.map(assistantEventCopyText)),
    formatCopySection('PROOF', proofRecords.map(assistantEventCopyText)),
    formatCopySection('AGENTS', agentEvents.map(assistantEventCopyText)),
    formatCopySection('EVENTS', [
      ...generalEvents,
      ...otherTurns.map(otherTurnEvent),
    ].map(assistantEventCopyText)),
    formatCopySection('RAW SAFE DATA', rawRecords.map((item, index) => `#${index + 1} ${text(item.label, 'raw')}\n${safeJsonPreview(item.payload ?? item, 1800)}`)),
  ].filter(Boolean).join('\n\n').trim();
}

function archiveWorkPanelCopyText(block: Extract<ArchiveTranscriptBlock, { kind: 'work' }>) {
  return [
    'ARCHIVED ASSISTANT WORK BLOCK',
    archiveWorkSummary(block),
    formatCopySection('ASSISTANT', block.assistantItems.map(archiveWorkItemCopyText)),
    formatCopySection('THINKING', block.thinkingItems.map(archiveWorkItemCopyText)),
    formatCopySection('TOOLS', block.toolItems.map(archiveWorkItemCopyText)),
    formatCopySection('CONTEXT', block.contextItems.map(archiveWorkItemCopyText)),
    formatCopySection('EDITS', block.editItems.map(archiveWorkItemCopyText)),
    formatCopySection('RUNS', block.runItems.map(archiveWorkItemCopyText)),
    formatCopySection('PROOF', block.proofItems.map(archiveWorkItemCopyText)),
    formatCopySection('EVENTS', block.eventItems.map(archiveWorkItemCopyText)),
    formatCopySection('RAW SAFE DATA', block.rawItems.map(archiveWorkItemCopyText)),
  ].filter(Boolean).join('\n\n').trim();
}

function assistantTurnCopyText(turn: Record<string, unknown>, index: number) {
  const body = text(turn.message || record(turn.chat_engine).assistant_response, '');
  return [
    `#${index + 1} ${text(turn.author, 'assistant')} ${text(turn.created_at, '')}`.trim(),
    text(turn.turn_id, '') ? `turn_id: ${text(turn.turn_id)}` : '',
    body,
  ].filter(Boolean).join('\n');
}

function assistantEventCopyText(event: Record<string, unknown>, index: number) {
  const status = text(event.status || event.verdict || event.proof_status || event.queue_status || event.result, '');
  const detail = text(event.detail || event.message || event.summary || event.finding || event.path || event.packet_path || event.latest_return_path, '');
  const refs = uniqueStrings([
    ...stringList(event.source_refs),
    ...stringList(event.path_refs),
    text(event.path || event.packet_path || event.latest_return_path || event.latest_run_path || event.session_path, ''),
  ]).slice(0, 12);
  return [
    `#${index + 1} ${assistantEventTitle(event)}`,
    status ? `status: ${status}` : '',
    event.tool_name ? `tool: ${text(event.tool_name)}` : '',
    refs.length ? `refs: ${refs.join(', ')}` : '',
    detail ? compactEventDetail(detail) : '',
  ].filter(Boolean).join('\n');
}

function archiveWorkItemCopyText(item: Record<string, unknown>, index: number) {
  const role = text(item.role, 'archive');
  const roleGroup = archiveMessageRoleGroup(item, role);
  const stats = record(item.diff_stats);
  const files = uniqueStrings([...stringList(stats.files), ...stringList(item.path_refs)]).slice(0, 12);
  const refs = uniqueStrings([
    ...files,
    ...stringList(item.context_refs),
  ]).slice(0, 12);
  return [
    `#${index + 1} ${archiveMessageLabel(item, role, roleGroup)} ${text(item.timestamp, '')}`.trim(),
    text(item.detail_label || item.source_type, '') ? `detail: ${text(item.detail_label || item.source_type)}` : '',
    refs.length ? `refs: ${refs.join(', ')}` : '',
    numberValue(stats.file_count) || files.length ? `diff: files ${text(stats.file_count ?? files.length, 0)} / +${text(stats.added_lines, 0)} / -${text(stats.removed_lines, 0)}` : '',
    archiveItemText(item),
  ].filter(Boolean).join('\n');
}

function formatCopySection(title: string, rows: string[]) {
  const cleanRows = rows.map((row) => row.trim()).filter(Boolean);
  if (!cleanRows.length) return '';
  return [`## ${title}`, ...cleanRows].join('\n\n');
}

function formatPayloadSize(value: string) {
  const chars = value.length;
  const bytes = typeof TextEncoder !== 'undefined'
    ? new TextEncoder().encode(value).length
    : chars;
  const byteLabel = bytes >= 1024 * 1024
    ? `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    : bytes >= 1024
      ? `${(bytes / 1024).toFixed(1)} KB`
      : `${bytes} B`;
  return `${byteLabel}, ${chars.toLocaleString()} chars`;
}

function safeJsonPreview(value: unknown, limit = 12000) {
  let rendered = '';
  try {
    rendered = JSON.stringify(value ?? {}, null, 2);
  } catch {
    rendered = text(value, '');
  }
  if (rendered.length <= limit) return rendered;
  return `${rendered.slice(0, limit).trimEnd()}\n...[truncated ${rendered.length - limit} chars]`;
}

function assistantEventTitle(event: Record<string, unknown>) {
  return text(event.label || event.event_type || event.kind || event.type || event.tool_name || event.id || event.path, 'event').replaceAll('_', ' ');
}

function compactEventDetail(value: string) {
  const lines = value.split('\n').map((line) => line.trim()).filter(Boolean);
  return lines.slice(0, 5).join('\n');
}

function stringList(value: unknown) {
  if (!Array.isArray(value)) return [];
  return value.map((item) => text(item, '')).filter(Boolean);
}

function uniqueStrings(values: string[]) {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const value of values) {
    const key = value.toLowerCase();
    if (!value || seen.has(key)) continue;
    seen.add(key);
    result.push(value);
  }
  return result;
}

function diffLineClass(line: string) {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'is-add';
  if (line.startsWith('-') && !line.startsWith('---')) return 'is-remove';
  if (line.startsWith('@@')) return 'is-hunk';
  if (line.startsWith('diff --git') || line.startsWith('*** ') || line.startsWith('+++') || line.startsWith('---')) return 'is-file';
  return 'is-context';
}

function compactNonDirectMessage(role: string, message: string, turn: Record<string, unknown> | undefined, roleGroup: string) {
  if (!['trace', 'context', 'event', 'diff', 'compaction'].includes(roleGroup)) return message;
  const firstLine = firstUsefulLine(message);
  const safeRole = safeClass(role).replaceAll('_', '-');
  if (roleGroup === 'trace') {
    if (safeRole.includes('tool-call') || safeRole.includes('function-call')) {
      return firstLine ? `tool call: ${firstLine}` : 'tool call';
    }
    if (safeRole.includes('tool-result') || safeRole.includes('function-call-output')) {
      return firstLine ? `tool result: ${firstLine}` : 'tool result';
    }
    return firstLine ? `execution: ${firstLine}` : 'execution trace';
  }
  if (roleGroup === 'context') {
    return firstLine || text(turn?.summary || turn?.status, 'context event');
  }
  if (roleGroup === 'diff') {
    return firstLine ? `file change: ${firstLine}` : 'file change / diff';
  }
  if (roleGroup === 'compaction') {
    return firstLine ? `context boundary: ${firstLine}` : 'context boundary';
  }
  return firstLine ? `${text(role, 'event')}: ${firstLine}` : text(role, 'event');
}

function firstUsefulLine(value: string) {
  return value
    .split('\n')
    .map((line) => line.trim())
    .find((line) => line && !line.startsWith('Original token count:')) ?? '';
}

function contextTurnDisplayText(turn: Record<string, unknown>) {
  if (text(turn.kind, '') === 'mini_auto_post') {
    return [
      'Context refreshed.',
      `mini_ref: ${text(turn.mini_ref || 'ION/05_context/current/codex_solo/MINI.md')}`,
      `context_floor_ref: ${text(turn.capsule_ref || 'ION/05_context/current/codex_solo/CAPSULE.md')}`,
      turn.mini_sha256 ? `mini_sha256: ${text(turn.mini_sha256)}` : '',
      'Full context-floor details are available in the context drawer.',
    ].filter(Boolean).join('\n');
  }
  return text(turn.message || turn.summary || turn.status || turn.path, '');
}

function coerceJocCommsThread(row: Record<string, unknown>): JocCommsThread | null {
  const threadId = text(row.thread_id, '');
  if (!threadId) return null;
  return {
    ...row,
    thread_id: threadId,
    channel_id: text(row.channel_id, 'team'),
    title: text(row.title, ''),
    subject: text(row.subject, ''),
    status: text(row.status, ''),
    latest_summary: text(row.latest_summary, ''),
    updated_at: text(row.updated_at, ''),
    created_at: text(row.created_at, ''),
    source_refs: stringList(row.source_refs),
    context_refs: stringList(row.context_refs),
    receipt_refs: stringList(row.receipt_refs),
    next_allowed_actions: stringList(row.next_allowed_actions),
  };
}

function coerceJocCommsMessage(row: Record<string, unknown>): JocCommsMessage | null {
  const messageId = text(row.message_id || row.id, '');
  const threadId = text(row.thread_id, '');
  if (!messageId || !threadId) return null;
  return {
    ...row,
    message_id: messageId,
    thread_id: threadId,
    channel_id: text(row.channel_id, 'team'),
    sender_id: text(row.sender_id, ''),
    sender_kind: text(row.sender_kind, ''),
    recipient: Array.isArray(row.recipient) ? stringList(row.recipient) : text(row.recipient, ''),
    body: text(row.body || row.message || row.detail || row.summary, ''),
    message_type: text(row.message_type, ''),
    message_kind: text(row.message_kind || row.kind, ''),
    subject: text(row.subject || row.title, ''),
    from_role: text(row.from_role || row.sender_id, ''),
    source_path: text(row.source_path || row.path, ''),
    source_refs: stringList(row.source_refs),
    context_refs: stringList(row.context_refs),
    receipt_refs: stringList(row.receipt_refs),
    status: text(row.status, ''),
    acked_by: stringList(row.acked_by),
    created_at: text(row.created_at || row.updated_at, ''),
    work_panel: record(row.work_panel),
  };
}

function mergeJocCommsThreads(threads: JocCommsThread[]) {
  const byId = new Map<string, JocCommsThread>();
  for (const thread of threads) {
    const threadId = text(thread.thread_id, '');
    if (!threadId) continue;
    const previous = byId.get(threadId);
    if (!previous) {
      byId.set(threadId, thread);
      continue;
    }
    byId.set(threadId, {
      ...previous,
      ...thread,
      source_refs: uniqueStrings([...(previous.source_refs ?? []), ...(thread.source_refs ?? [])]),
      context_refs: uniqueStrings([...(previous.context_refs ?? []), ...(thread.context_refs ?? [])]),
      receipt_refs: uniqueStrings([...(previous.receipt_refs ?? []), ...(thread.receipt_refs ?? [])]),
      next_allowed_actions: uniqueStrings([...(previous.next_allowed_actions ?? []), ...(thread.next_allowed_actions ?? [])]),
    });
  }
  return Array.from(byId.values()).sort((left, right) => {
    const rightTime = Date.parse(text(right.updated_at || right.created_at, '')) || 0;
    const leftTime = Date.parse(text(left.updated_at || left.created_at, '')) || 0;
    return rightTime - leftTime;
  });
}

function missionThreadTitle(thread: JocCommsThread) {
  return text(thread.subject || thread.title || thread.thread_id, 'thread');
}

function missionThreadRefs(thread: JocCommsThread) {
  return uniqueStrings([
    text(thread.thread_id, ''),
    text(thread.title, ''),
    text(thread.subject, ''),
    ...stringList(thread.source_refs),
    ...stringList(thread.context_refs),
    ...stringList(thread.receipt_refs),
  ]);
}

function matchedMissionThreadIdForTarget(threads: JocCommsThread[], targets: unknown[]) {
  const targetValues = uniqueStrings(targets.map((target) => text(target, '')).filter(Boolean));
  if (!targetValues.length) return '';
  const match = threads.find((thread) => {
    const refs = missionThreadRefs(thread);
    return refs.some((ref) => targetValues.some((target) => ref.includes(target) || target.includes(ref)));
  });
  return text(match?.thread_id, '');
}

function archiveSessionForMissionThread(thread: JocCommsThread, sessions: IonCodexConversationArchiveSession[]) {
  const refs = missionThreadRefs(thread);
  if (!refs.length) return null;
  return sessions.find((session) => {
    const sessionRecord = record(session);
    const candidates = [session.session_id, session.session_path, sessionRecord.title, sessionRecord.project_root].map((value) => text(value, '')).filter(Boolean);
    return candidates.some((candidate) => refs.some((ref) => ref.includes(candidate) || candidate.includes(ref)));
  }) ?? null;
}

function missionMessageRouteLabel(message: JocCommsMessage) {
  const sender = text(message.from_role || message.sender_id || message.sender_kind, 'unknown');
  const recipient = Array.isArray(message.recipient) ? message.recipient.join(', ') : text(message.recipient, '');
  return recipient ? `${sender} -> ${recipient}` : sender;
}

function missionToneFromStatus(value: unknown): MissionTimelineEvent['tone'] {
  const normalized = text(value, '').toLowerCase();
  if (normalized.includes('block') || normalized.includes('fail') || normalized.includes('error') || normalized.includes('deny')) return 'blocked';
  if (normalized.includes('active') || normalized.includes('running') || normalized.includes('working') || normalized.includes('started')) return 'active';
  if (normalized.includes('pending') || normalized.includes('queued') || normalized.includes('wait') || normalized.includes('stale')) return 'watch';
  if (normalized.includes('empty') || normalized.includes('none') || normalized.includes('idle')) return 'empty';
  return normalized ? 'ready' : 'empty';
}

function missionEventSortValue(event: MissionTimelineEvent) {
  const parsed = Date.parse(event.at);
  if (Number.isFinite(parsed)) return parsed;
  return 0;
}

function agentCommsApiPath(suffix: string, query: Record<string, string> = {}) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value) params.set(key, value);
  }
  const qs = params.toString();
  return `/cockpit/agents/comms${suffix}${qs ? `?${qs}` : ''}`;
}

function chatApiPath(suffix: string, query: Record<string, string> = {}) {
  const cockpit = typeof window !== 'undefined' && window.location.pathname.startsWith('/cockpit');
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value) params.set(key, value);
  }
  const base = cockpit ? '/cockpit/chat' : '/chat';
  const qs = params.toString();
  return `${base}${suffix}${qs ? `?${qs}` : ''}`;
}

function speechRecognitionConstructor(): SpeechRecognitionConstructorLike | null {
  if (typeof window === 'undefined') return null;
  return window.SpeechRecognition ?? window.webkitSpeechRecognition ?? null;
}

function appendDictationText(previous: string, next: string) {
  const clean = next.trim().replace(/\s+/g, ' ');
  if (!clean) return previous;
  if (!previous.trim()) return clean;
  const spacer = /[\s\n]$/.test(previous) ? '' : ' ';
  return `${previous}${spacer}${clean}`;
}

function wordCount(value: string) {
  return value.trim().split(/\s+/).filter(Boolean).length;
}

function publicToken() {
  return '';
}

function withPublicToken(payload: Record<string, unknown>) {
  return payload;
}

function records(value: unknown): Array<Record<string, unknown>> {
  if (!Array.isArray(value)) return [];
  return value.map((item) => (item && typeof item === 'object' && !Array.isArray(item) ? item as Record<string, unknown> : { name: item }));
}

function record(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function text(value: unknown, fallback: unknown = 'unknown') {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return String(fallback);
}

function verdictClass(value: unknown) {
  const normalized = text(value, '').toLowerCase();
  if (normalized.includes('ready') || normalized.includes('pass') || normalized.includes('ok')) return 'ready';
  if (normalized.includes('blocked') || normalized.includes('fail') || normalized.includes('error')) return 'blocked';
  return 'degraded';
}

function safeClass(value: unknown) {
  return text(value, 'unknown').toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-|-$/g, '') || 'unknown';
}
