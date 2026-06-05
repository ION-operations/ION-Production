import { useEffect, useMemo, useRef, useState, type ChangeEvent, type KeyboardEvent, type ReactNode } from 'react';
import type { IonCockpitViewModel } from './ionRuntimeCockpitTypes';
import {
  ArchiveIcon,
  AuthorityIcon,
  ChatIcon,
  CheckIcon,
  CloseIcon,
  ComposeIcon,
  EvidenceIcon,
  LensIcon,
  ReceiptIcon,
  RunIcon,
  SettingsIcon,
  StatusIcon,
  ToolsIcon,
  WorkSurfaceIcon,
} from './icons';

type LeftDrawerId = 'tabs' | 'merge' | 'chat' | 'actions' | 'native' | 'atlas' | 'capture' | 'surfaces' | 'profiles';
type RightDrawerId = 'status' | 'actions' | 'workers' | 'artifacts' | 'probe' | 'authority' | 'settings';
type IconBarItem<T extends string> = { id: T; icon: ReactNode; title: string; label: string };
type ToolbarTone = 'ready' | 'missing' | 'watch';
type BrowserGptAtlasLens = 'trunks' | 'native' | 'branches' | 'surfaces' | 'assistant';
type BrowserGptAtlasNode = {
  id: string;
  kind: 'trunk' | 'native' | 'custom-gpt' | 'branch' | 'surface' | 'assistant';
  title: string;
  detail: string;
  meta: string;
  ref: string;
  tone: 'ready' | 'watch' | 'blocked' | 'muted' | 'active';
  icon: ReactNode;
  url?: string;
};
type ActionSyncMatch = {
  kind: string;
  title: string;
  score: number;
  record: Record<string, unknown>;
};

const leftRailItems: Array<IconBarItem<LeftDrawerId>> = [
  { id: 'tabs', icon: <ChatIcon />, title: 'open ChatGPT tabs', label: 'TABS' },
  { id: 'merge', icon: <WorkSurfaceIcon />, title: 'visual merge room', label: 'MERGE' },
  { id: 'chat', icon: <ChatIcon />, title: 'chat mirror', label: 'CHAT' },
  { id: 'actions', icon: <AuthorityIcon />, title: 'actions and approvals', label: 'ACT' },
  { id: 'native', icon: <ArchiveIcon />, title: 'native chats and GPTs', label: 'NATIVE' },
  { id: 'atlas', icon: <LensIcon />, title: 'context atlas', label: 'ATLAS' },
  { id: 'capture', icon: <ComposeIcon />, title: 'capture flow', label: 'CAP' },
  { id: 'surfaces', icon: <LensIcon />, title: 'surface map', label: 'DOM' },
  { id: 'profiles', icon: <ArchiveIcon />, title: 'profiles', label: 'PRO' },
];

const rightRailItems: Array<IconBarItem<RightDrawerId>> = [
  { id: 'status', icon: <StatusIcon />, title: 'status', label: 'STAT' },
  { id: 'actions', icon: <AuthorityIcon />, title: 'action sync detail', label: 'ACT' },
  { id: 'workers', icon: <WorkSurfaceIcon />, title: 'spawned workers and comms', label: 'WRK' },
  { id: 'artifacts', icon: <ArchiveIcon />, title: 'large artifacts and transfer', label: 'ART' },
  { id: 'probe', icon: <EvidenceIcon />, title: 'probe evidence', label: 'PROBE' },
  { id: 'authority', icon: <AuthorityIcon />, title: 'authority', label: 'AUTH' },
  { id: 'settings', icon: <SettingsIcon />, title: 'settings', label: 'SET' },
];

const VISIBLE_CONVERSATION_LIMIT = 500;

const surfaceGroups = [
  {
    id: 'conversation',
    label: 'Conversation',
    surfaceIds: ['message_list', 'latest_user_message', 'latest_assistant_message', 'stop_button'],
  },
  {
    id: 'composer',
    label: 'Composer',
    surfaceIds: ['composer', 'send_button', 'file_attach_button', 'file_upload_menu_option', 'voice_mic_button', 'slash_command_menu', 'slash_command_option'],
  },
  {
    id: 'modes',
    label: 'Modes',
    surfaceIds: ['model_picker', 'model_menu_option', 'thinking_mode_control', 'thinking_effort_option', 'tools_menu_opener', 'tools_menu_option'],
  },
  {
    id: 'shell',
    label: 'Shell',
    surfaceIds: ['new_chat_button', 'left_sidebar_toggle', 'left_drawer', 'drawer_surface', 'native_action_cards'],
  },
];

const composerToolbar = ['file_attach_button', 'tools_menu_opener', 'thinking_mode_control', 'model_picker', 'voice_mic_button', 'slash_command_menu'];
const WRITE_CONFIRMATION_TOKEN = 'ION_BOUNDED_WRITE_CONFIRMED';

export function BrowserGptDomTwinPanel({
  runtime,
  onRuntimeRefresh,
}: {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
}) {
  const [leftDrawer, setLeftDrawer] = useState<LeftDrawerId>('tabs');
  const [rightDrawer, setRightDrawer] = useState<RightDrawerId>('status');
  const [leftDrawerOpen, setLeftDrawerOpen] = useState(true);
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [sendStatus, setSendStatus] = useState('idle');
  const [uploadStatus, setUploadStatus] = useState('ready');
  const [screenOpsStatus, setScreenOpsStatus] = useState('unchecked');
  const [screenOpsResult, setScreenOpsResult] = useState<Record<string, unknown> | null>(null);
  const [downloadAssets, setDownloadAssets] = useState<Array<Record<string, unknown>>>([]);
  const [liveTranscript, setLiveTranscript] = useState<Record<string, unknown> | null>(null);
  const [optimisticChatEvents, setOptimisticChatEvents] = useState<Array<Record<string, unknown>>>([]);
  const [clockNow, setClockNow] = useState(Date.now());
  const [chatGptTabs, setChatGptTabs] = useState<Array<Record<string, unknown>>>([]);
  const [chatGptTabsStatus, setChatGptTabsStatus] = useState('not loaded');
  const [relayStatus, setRelayStatus] = useState('not relayed');
  const [relayResult, setRelayResult] = useState<Record<string, unknown> | null>(null);
  const [approvalRequests, setApprovalRequests] = useState<Array<Record<string, unknown>>>([]);
  const [approvalStatus, setApprovalStatus] = useState('not checked');
  const [approvalResult, setApprovalResult] = useState<Record<string, unknown> | null>(null);
  const [nativeNavigation, setNativeNavigation] = useState<Record<string, unknown> | null>(null);
  const [nativeNavigationStatus, setNativeNavigationStatus] = useState('not loaded');
  const [nativeThreadAutoScroll, setNativeThreadAutoScroll] = useState(true);
  const [autoAcceptRuntime, setAutoAcceptRuntime] = useState<Record<string, unknown>>({});
  const [autoAcceptStatus, setAutoAcceptStatus] = useState('not synced');
  const [autoAcceptTtlMinutes, setAutoAcceptTtlMinutes] = useState('15');
  const [autoProceedCountInput, setAutoProceedCountInput] = useState('3');
  const [autoProceedRemaining, setAutoProceedRemaining] = useState(0);
  const [autoProceedAnchor, setAutoProceedAnchor] = useState('');
  const [autoProceedStatus, setAutoProceedStatus] = useState('off');
  const [agentCommsMessage, setAgentCommsMessage] = useState('');
  const [agentCommsSubject, setAgentCommsSubject] = useState('Browser GPT worker follow-up');
  const [agentCommsTarget, setAgentCommsTarget] = useState('');
  const [agentCommsThreadId, setAgentCommsThreadId] = useState('');
  const [agentCommsStatus, setAgentCommsStatus] = useState('idle');
  const [agentCommsBusy, setAgentCommsBusy] = useState(false);
  const [agentCommsRequestState, setAgentCommsRequestState] = useState<Record<string, unknown> | null>(null);
  const [mergeRoomName, setMergeRoomName] = useState('Browser GPT merge room');
  const [mergeTagsInput, setMergeTagsInput] = useState('browser-gpt, ion-actions, agent-comms');
  const [mergeContext, setMergeContext] = useState('Use the ION Agent Comms room and Action Gateway receipts as the coordination source. Treat the visual merge as operator UI, not shared model memory.');
  const [mergeSelectedTabIds, setMergeSelectedTabIds] = useState<string[]>([]);
  const [mergeSelectedCodexSessionIds, setMergeSelectedCodexSessionIds] = useState<string[]>([]);
  const [mergeSelectedAgentRoleIds, setMergeSelectedAgentRoleIds] = useState<string[]>([]);
  const [mergeArchiveAttachments, setMergeArchiveAttachments] = useState<Record<string, Record<string, unknown>>>({});
  const [mergeCommsTarget, setMergeCommsTarget] = useState('');
  const [mergeCommsStatus, setMergeCommsStatus] = useState('idle');
  const [mergeArchiveAttachStatus, setMergeArchiveAttachStatus] = useState('not attached');
  const [mergeArchiveAttachBusy, setMergeArchiveAttachBusy] = useState(false);
  const [mergeReworkStatus, setMergeReworkStatus] = useState('idle');
  const [mergeCommsRequestState, setMergeCommsRequestState] = useState<Record<string, unknown> | null>(null);
  const [mergeArchiveAttachRequestState, setMergeArchiveAttachRequestState] = useState<Record<string, unknown> | null>(null);
  const [mergeReworkRequestState, setMergeReworkRequestState] = useState<Record<string, unknown> | null>(null);
  const [largeArtifactPath, setLargeArtifactPath] = useState('ION/REPO_AUTHORITY.md');
  const [largeArtifactQuery, setLargeArtifactQuery] = useState('schema_id');
  const [largeArtifactHeading, setLargeArtifactHeading] = useState('Purpose');
  const [largeArtifactJsonPath, setLargeArtifactJsonPath] = useState('summary');
  const [largeArtifactSliceStart, setLargeArtifactSliceStart] = useState('1');
  const [largeArtifactSliceLines, setLargeArtifactSliceLines] = useState('80');
  const [artifactPackageLabel, setArtifactPackageLabel] = useState('browser-gpt-artifact');
  const [artifactMaxBytes, setArtifactMaxBytes] = useState('2000000');
  const [inferenceQuestion, setInferenceQuestion] = useState('What source ranges matter for this artifact?');
  const [largeArtifactStatus, setLargeArtifactStatus] = useState('idle');
  const [largeArtifactResults, setLargeArtifactResults] = useState<Record<string, Record<string, unknown>>>({});
  const [atlasLens, setAtlasLens] = useState<BrowserGptAtlasLens>('trunks');
  const [atlasSearch, setAtlasSearch] = useState('');
  const [atlasRefs, setAtlasRefs] = useState<string[]>([]);
  const [focusedAtlasNodeId, setFocusedAtlasNodeId] = useState('');
  const uploadInputRef = useRef<HTMLInputElement | null>(null);
  const nativeThreadRef = useRef<HTMLElement | null>(null);
  const nativeThreadBottomRef = useRef<HTMLDivElement | null>(null);
  const autoProceedBusyRef = useRef(false);

  const shell = runtime.extension_micro_shell ?? {};
  const codexBrowserAgent = (shell.codex_browser_agent ?? {}) as Record<string, unknown>;
  const codexBrowserAgentSummary = (codexBrowserAgent.summary ?? {}) as Record<string, unknown>;
  const codexBrowserAgentArtifacts = (codexBrowserAgent.artifacts ?? {}) as Record<string, unknown>;
  const computerAssistant = (shell.computer_assistant_capability_map ?? {}) as Record<string, unknown>;
  const assistantLanes = asRecords(computerAssistant.architecture_lanes);
  const assistantResearch = asRecords(computerAssistant.research_digest);
  const assistantReadyLaneCount = text(computerAssistant.ready_lane_count, '0');
  const assistantLaneCount = text(computerAssistant.lane_count, String(assistantLanes.length));
  const agentControlPlane = asRecord(runtime.agent_control_plane);
  const agentControlSummary = asRecord(agentControlPlane.summary);
  const agentControlAgents = asRecords(agentControlPlane.agents);
  const codexCliWorkbench = asRecord(runtime.codex_cli_workbench);
  const codexWorkbenchSummary = asRecord(codexCliWorkbench.summary);
  const codexConversationArchive = asRecord(runtime.codex_conversation_archive);
  const codexArchiveSourceCounts = asRecord(codexConversationArchive.source_counts);
  const archiveSessions = asRecords(codexConversationArchive.sessions);
  const agentControlCommunications = asRecord(agentControlPlane.communications);
  const agentTeamComms = asRecord(agentControlCommunications.team_comms);
  const agentCommsRuns = asRecord(agentTeamComms.runs);
  const agentRunRows = asRecords(agentCommsRuns.runs);
  const agentCommsChannels = asRecords(agentTeamComms.channels);
  const agentCommsThreads = asRecords(agentTeamComms.threads);
  const agentCommsMessages = latestByTimestamp(asRecords(agentTeamComms.recent_messages), 'created_at');
  const agentDispatcher = asRecord(agentControlPlane.dispatcher);
  const agentDispatcherSummary = asRecord(agentDispatcher.summary);
  const agentDispatcherNextAction = asRecord(agentDispatcher.next_action);
  const agentDispatcherQueue = asRecords(agentDispatcher.queue);
  const activeAgentRun = agentRunRows.find(browserGptRunHasActiveWorker) ?? agentRunRows.find(browserGptRunIsActionable) ?? agentRunRows[0] ?? {};
  const selectedAgentThread = agentCommsThreadId
    ? agentCommsThreads.find((thread) => text(thread.thread_id, '') === agentCommsThreadId) ?? {}
    : agentCommsThreads.find((thread) => text(thread.thread_id, '') === text(agentCommsMessages[0]?.thread_id, '')) ?? agentCommsThreads[0] ?? {};
  const selectedAgentThreadId = text(selectedAgentThread.thread_id, '');
  const selectedAgentChannelId = text(selectedAgentThread.channel_id ?? agentCommsChannels[0]?.channel_id, 'team');
  const selectedAgentMessages = selectedAgentThreadId
    ? agentCommsMessages.filter((message) => text(message.thread_id, '') === selectedAgentThreadId)
    : agentCommsMessages.slice(0, 12);
  const activeWorkerCount = agentRunRows.reduce((count, run) => count + (numericValue(asRecord(run.worker_runtime).active_worker_count) ?? 0), 0);
  const actionGatewaySync = (shell.action_gateway_sync ?? {}) as Record<string, unknown>;
  const actionGatewaySummary = (actionGatewaySync.summary ?? {}) as Record<string, unknown>;
  const actionGatewayRuntime = (actionGatewaySync.runtime ?? {}) as Record<string, unknown>;
  const actionGatewayQueue = (actionGatewaySync.browser_queue ?? {}) as Record<string, unknown>;
  const actionGatewayLedger = (actionGatewaySync.idempotency_ledger ?? {}) as Record<string, unknown>;
  const modelAutoAccept = asRecord(actionGatewayQueue.auto_accept_actions);
  const liveAutoAccept = asRecord(autoAcceptRuntime.auto_accept_actions ?? autoAcceptRuntime.queue_state);
  const autoAcceptActive = text(autoAcceptRuntime.autoAcceptActive ?? liveAutoAccept.enabled ?? modelAutoAccept.enabled, 'false') === 'true';
  const autoAcceptUntil = text(autoAcceptRuntime.autoAcceptUntil ?? liveAutoAccept.until ?? modelAutoAccept.until, '');
  const autoAcceptTtlSeconds = numericValue(autoAcceptRuntime.autoAcceptTtlSeconds ?? liveAutoAccept.ttl_seconds ?? modelAutoAccept.ttl_seconds) ?? 900;
  const recentActionReceipts = asRecords(actionGatewaySync.recent_action_receipts);
  const recentActionPackets = asRecords(actionGatewaySync.recent_action_packets);
  const recentServiceReceipts = asRecords(actionGatewaySync.recent_service_receipts);
  const recentTestReceipts = asRecords(actionGatewaySync.recent_test_receipts);
  const actionQueuePackets = asRecords(actionGatewayQueue.packets);
  const idempotencyEntries = asRecords(actionGatewayLedger.entries);
  const browserGptDom = (shell.browser_gpt_dom ?? {}) as Record<string, unknown>;
  const twin = (browserGptDom.chatgpt_dom_twin ?? {}) as Record<string, unknown>;
  const source = (twin.source ?? {}) as Record<string, unknown>;
  const composer = (twin.composer ?? {}) as Record<string, unknown>;
  const send = (twin.send ?? {}) as Record<string, unknown>;
  const state = (twin.state ?? {}) as Record<string, unknown>;
  const transcript = (twin.transcript ?? {}) as Record<string, unknown>;
  const issueResolution = (twin.issue_resolution ?? {}) as Record<string, unknown>;
  const authority = (twin.authority ?? browserGptDom.authority ?? {}) as Record<string, unknown>;
  const probeIntake = (browserGptDom.probe_intake ?? {}) as Record<string, unknown>;
  const latestProbe = (probeIntake.latest_usable_probe ?? {}) as Record<string, unknown>;
  const effectiveCoverage = (probeIntake.effective_surface_coverage ?? {}) as Record<string, unknown>;
  const controls = asRecords(twin.controls);
  const snapshotMessages = asRecords(transcript.messages);
  const liveMessages = asRecords(liveTranscript?.messages).filter(hasReadableMessage);
  const snapshotReadableMessages = snapshotMessages.filter(hasReadableMessage);
  const messages = liveMessages.length > 0 ? liveMessages : snapshotReadableMessages;
  const liveTimelineEvents = asRecords(liveTranscript?.timeline_events).filter(hasReadableTimelineEvent);
  const snapshotTimelineEvents = asRecords(transcript.timeline_events).filter(hasReadableTimelineEvent);
  const baseTimelineEvents = liveTimelineEvents.length > 0 ? liveTimelineEvents : snapshotTimelineEvents.length > 0 ? snapshotTimelineEvents : messages;
  const visibleOptimisticEvents = optimisticChatEvents.filter((event) => optimisticEventStillVisible(event, baseTimelineEvents));
  const timelineEvents = [...baseTimelineEvents, ...visibleOptimisticEvents];
  const timelineStatusEvents = timelineEvents.filter((event) => timelineEventType(event) !== 'message');
  const activeTimelineEvents = timelineEvents.filter((event) => timelineEventIsActive(event));
  const toolTimelineEvents = timelineEvents.filter((event) => timelineEventType(event).startsWith('tool_'));
  const pendingApprovalRequests = approvalRequests.filter((request) => text(request.status ?? request.state, 'pending') === 'pending');
  const nativeApprovalRequests = approvalRequests.filter((request) => text(request.approval_kind ?? request.kind, '').includes('native_action'));
  const bridgeApprovalRequests = approvalRequests.filter((request) => !text(request.approval_kind ?? request.kind, '').includes('native_action'));
  const nativeChats = asRecords(nativeNavigation?.chats);
  const nativeCustomGpts = asRecords(nativeNavigation?.custom_gpts);
  const nativeDirectories = asRecords(nativeNavigation?.gpt_directories);
  const nativeCurrent = (nativeNavigation?.current ?? {}) as Record<string, unknown>;
  const boundChatGptTab = chatGptTabs.find((tab) => text(tab.bound, 'false') === 'true');
  const activeChatGptTab = chatGptTabs.find((tab) => text(tab.active_browser_tab, 'false') === 'true' || text(tab.active, 'false') === 'true') ?? boundChatGptTab;
  const selectedChatGptTab = boundChatGptTab ?? activeChatGptTab;
  const transcriptSource = liveTimelineEvents.length > 0 ? 'live timeline' : liveMessages.length > 0 ? 'live bridge' : snapshotTimelineEvents.length > 0 ? 'snapshot timeline' : snapshotReadableMessages.length > 0 ? 'probe snapshot' : text(transcript.readability_status, 'empty');
  const controlBySurface = useMemo(() => new Map(controls.map((control) => [text(control.surface_id, ''), control])), [controls]);
  const coverageCount = `${String(effectiveCoverage.found_surface_count ?? 0)}/${controls.length || 0}`;
  const selectedModel = controlLabel(controlBySurface.get('model_picker'), 'model');
  const selectedThinking = controlLabel(controlBySurface.get('thinking_mode_control'), 'thinking');
  const blockingIssues = String(issueResolution.blocking_issue_count ?? 0);
  const sendIsGated = text(send.live_send_authority, 'false') !== 'true';
  const screenOpsAssessment = (screenOpsResult?.reuse_assessment ?? screenOpsResult?.assessment ?? {}) as Record<string, unknown>;
  const screenOpsReady = text(screenOpsAssessment.can_reuse, 'false') === 'true' || text(screenOpsResult?.status, '') === 'ready';
  const screenOpsPointSummary = screenOpsControlPointSummary(screenOpsAssessment);
  const threadHasActiveTurn = activeTimelineEvents.length > 0 || optimisticChatEvents.some((event) => ['pending', 'sending', 'streaming', 'active'].includes(timelineEventState(event))) || sendStatus === 'sending' || sendStatus.includes('sync') || sendStatus.includes('reply') || sendStatus.includes('awaiting');
  const latestTimelineEvent = timelineEvents[timelineEvents.length - 1] ?? {};
  const latestCompletedAssistantSignature = completedAssistantSignature(timelineEvents);
  const sendBusy = sendStatus === 'sending' || sendStatus.endsWith(' sending') || sendStatus.includes('syncing') || sendStatus.includes('awaiting') || sendStatus.includes('reply') || sendStatus.includes('pending') || sendStatus.includes('requested');
  const latestTimelineScrollKey = [
    timelineEvents.length,
    text(latestTimelineEvent.event_index ?? latestTimelineEvent.index, ''),
    timelineEventState(latestTimelineEvent),
    text(latestTimelineEvent.text_sha256 ?? latestTimelineEvent.text_full ?? latestTimelineEvent.text_preview, '').slice(0, 120),
    sendStatus,
  ].join('|');
  const browserGptTarget = text(browserGptDom.target_url ?? browserGptDom.origin, 'https://chatgpt.com');
  const browserGptProbePath = text(source.probe_snapshot ?? browserGptDom.latest_profile_path, 'no probe loaded');
  const activeStateLabel = activeTimelineEvents.length ? `${activeTimelineEvents.length} live` : text(liveTranscript?.latest_activity_state, 'quiet');
  const actionStateLabel = pendingApprovalRequests.length ? `${pendingApprovalRequests.length} pending` : text(approvalStatus, 'idle');
  const workerStateLabel = activeWorkerCount
    ? `${activeWorkerCount} live`
    : `${text(agentCommsRuns.active_run_count, '0')}/${text(agentCommsRuns.run_count, '0')}`;
  const mergeTabs = chatGptTabs.filter((tab) => mergeSelectedTabIds.includes(browserGptTabKey(tab)));
  const effectiveMergeTabs = mergeTabs.length ? mergeTabs : selectedChatGptTab ? [selectedChatGptTab] : [];
  const mergeTags = parseMergeTags(mergeTagsInput);
  const selectedCodexSessions = archiveSessions.filter((session) => mergeSelectedCodexSessionIds.includes(text(session.session_id, '')));
  const selectedMergeArchiveAttachments = selectedCodexSessions
    .map((session) => mergeArchiveAttachments[text(session.session_id, '')])
    .filter((attachment): attachment is Record<string, unknown> => Boolean(attachment));
  const selectedMergeAgents = agentControlAgents.filter((agent) => mergeSelectedAgentRoleIds.includes(mergeAgentRoleId(agent)));
  const mergeTargetRoles = uniqueStrings([...mergeSelectedAgentRoleIds, mergeCommsTarget].filter(Boolean));
  const mergeRunTargetRoles = uniqueStrings(mergeSelectedAgentRoleIds.length ? mergeSelectedAgentRoleIds : (mergeCommsTarget && mergeCommsTarget !== 'operator' ? [mergeCommsTarget] : []));
  const mergeSourceRefs = mergeRoomSourceRefs({
    browserGptProbePath,
    browserGptTarget,
    tabs: effectiveMergeTabs,
    threadId: selectedAgentThreadId,
    codexSessions: selectedCodexSessions,
    codexAttachments: selectedMergeArchiveAttachments,
    codexAgents: selectedMergeAgents,
  });
  const codexArchiveStatus = `${text(codexConversationArchive.verdict, 'deferred')} / ${text(codexArchiveSourceCounts.session_files_total, '0')} sessions`;
  const codexWorkbenchState = text(codexCliWorkbench.verdict ?? codexWorkbenchSummary.status, 'deferred');
  const mergeContextBlock = buildVisualMergeContextBlock({
    roomName: mergeRoomName,
    tags: mergeTags,
    tabs: effectiveMergeTabs,
    context: mergeContext,
    commsChannelId: selectedAgentChannelId,
    commsThreadId: selectedAgentThreadId,
    targetRole: mergeTargetRoles.join(', '),
    actionStatus: actionStateLabel,
    codexArchiveStatus,
    codexWorkbenchState,
    codexSessions: selectedCodexSessions,
    codexAttachments: selectedMergeArchiveAttachments,
    codexAgents: selectedMergeAgents,
  });
  const mergeRoomStatus = `${effectiveMergeTabs.length}/${chatGptTabs.length || 0} tabs / ${selectedCodexSessions.length} codex / ${mergeRunTargetRoles.length} agents`;
  const bridgeSummary = `${chatGptTabsStatus} / ${nativeNavigation ? `${nativeChats.length} chats` : nativeNavigationStatus} / ${timelineEvents.length} events / ${relayStatus}`;
  const largeArtifactProfile = delegatedBranchResult(largeArtifactResults.profile);
  const largeArtifactManifest = delegatedBranchResult(largeArtifactResults.manifest);
  const largeArtifactStream = delegatedBranchResult(largeArtifactResults.stream_start);
  const largeArtifactChunk = delegatedBranchResult(largeArtifactResults.stream_next);
  const artifactPreview = delegatedBranchResult(largeArtifactResults.zip_preview);
  const artifactZip = delegatedBranchResult(largeArtifactResults.zip_materialize);
  const artifactManifest = delegatedBranchResult(largeArtifactResults.zip_manifest);
  const inferenceStatus = delegatedBranchResult(largeArtifactResults.inference_status);
  const latestArtifactResult = delegatedBranchResult(largeArtifactResults.latest);
  const artifactPackageId = text(
    artifactZip.package_id ??
      artifactPreview.package_id ??
      artifactManifest.package_id ??
      latestArtifactResult.package_id,
    '',
  );
  const artifactCursor = text(largeArtifactChunk.next_cursor ?? largeArtifactStream.cursor, '');
  const artifactStatusTone = toolbarStatusTone(largeArtifactStatus, true);

  const postBridgeCommand = (payload: Record<string, unknown>, timeoutMs = 30000): Promise<Record<string, unknown>> => {
    const commandId = `browser-gpt-command-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
    return new Promise((resolve) => {
      const timeout = window.setTimeout(() => {
        window.removeEventListener('message', handleResult);
        resolve({ ok: false, finding: 'browser_gpt_command_timeout' });
      }, timeoutMs);
      function handleResult(event: MessageEvent) {
        if (event.source !== window) return;
        const data = event.data as Record<string, unknown> | null;
        if (!data || data.source !== 'ion-browser-gpt-cockpit-bridge' || data.command_id !== commandId) return;
        window.clearTimeout(timeout);
        window.removeEventListener('message', handleResult);
        resolve((data.response ?? {}) as Record<string, unknown>);
      }
      window.addEventListener('message', handleResult);
      window.postMessage({
        source: 'ion-browser-gpt-cockpit',
        command_id: commandId,
        payload,
      }, window.location.origin);
    });
  };

  const requestScreenAutomation = async (action: 'status' | 'learn' | 'reload-extension' | 'refresh-tabs', payload: Record<string, unknown> = {}) => {
    setScreenOpsStatus(action === 'status' ? 'checking' : `${action}...`);
    try {
      const endpoint = `/cockpit/browser-gpt/screen-automation/${action === 'status' ? 'status' : action}`;
      const response = await fetch(endpoint, action === 'status' ? {
        headers: { Accept: 'application/json' },
        cache: 'no-store',
      } : {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        cache: 'no-store',
      });
      const result = (await response.json()) as Record<string, unknown>;
      setScreenOpsResult(result);
      setScreenOpsStatus(text(result.status ?? result.finding, response.ok ? 'ready' : 'blocked'));
      if (response.ok && (action === 'reload-extension' || action === 'refresh-tabs')) {
        window.setTimeout(() => onRuntimeRefresh?.(), 1800);
      }
    } catch (error) {
      setScreenOpsStatus(error instanceof Error ? error.message : 'screen automation failed');
    }
  };

  const requestCurrentChatGptTabs = async () => {
    setChatGptTabsStatus('reading tabs');
    const response = await postBridgeCommand({ type: 'LIST_CHATGPT_TABS' }, 12000);
    const result = bridgePayload(response);
    const tabs = asRecords(result.tabs);
    if (response.ok === true && text(result.schema_id, '').includes('chatgpt_tabs')) {
      setChatGptTabs(tabs);
      setChatGptTabsStatus(`${tabs.length} open tab${tabs.length === 1 ? '' : 's'}`);
      return tabs;
    }
    setChatGptTabsStatus(sendFailureText(response));
    return [];
  };

  const focusChatGptTab = async (tab: Record<string, unknown>) => {
    const tabId = numericValue(tab.tab_id);
    if (!tabId) {
      setChatGptTabsStatus('tab id missing');
      return;
    }
    setChatGptTabsStatus(`focusing ${text(tab.title, 'ChatGPT')}`);
    const response = await postBridgeCommand({ type: 'FOCUS_CHATGPT_TAB', target_tab_id: tabId }, 16000);
    setChatGptTabsStatus(response.ok === true ? 'tab focused' : sendFailureText(response));
    await requestCurrentChatGptTabs();
  };

  const readChatGptTabHistory = (tab: Record<string, unknown>) => {
    const tabId = numericValue(tab.tab_id);
    setLeftDrawer('chat');
    setLeftDrawerOpen(true);
    setSendStatus(`reading ${text(tab.title, 'ChatGPT')}`);
    requestVisibleConversation({
      targetTabId: tabId,
      targetUrl: text(tab.url, ''),
      bindTab: Boolean(tabId),
      attempts: 1,
      intervalMs: 900,
    });
  };

  const relayVisibleConversation = async (tab?: Record<string, unknown>) => {
    const target = tab ?? selectedChatGptTab;
    const tabId = numericValue(target?.tab_id);
    setRelayStatus(tabId ? `relaying tab ${tabId}` : 'relaying visible history');
    const response = await postBridgeCommand({
      type: 'RELAY_VISIBLE_CONVERSATION',
      target_tab_id: tabId || undefined,
      target_url: text(target?.url, ''),
      limit: VISIBLE_CONVERSATION_LIMIT,
      allow_open_chatgpt_tab: !tabId,
    }, 42000);
    const commandResult = (response.result ?? {}) as Record<string, unknown>;
    const relay = (commandResult.result ?? commandResult) as Record<string, unknown>;
    const transcript = (commandResult.transcript ?? {}) as Record<string, unknown>;
    setRelayResult(relay);
    if (asRecords(transcript.messages).length > 0 || asRecords(transcript.timeline_events).length > 0) setLiveTranscript(transcript);
    setRelayStatus(response.ok === true ? text(relay.receipt_path ?? relay.finding, 'relayed') : sendFailureText(response));
    void requestCurrentChatGptTabs();
  };

  const requestApprovalRequests = async (openDrawer = true) => {
    if (openDrawer) {
      setLeftDrawer('actions');
      setLeftDrawerOpen(true);
    }
    setApprovalStatus('reading actions');
    const response = await postBridgeCommand({
      type: 'READ_APPROVAL_REQUESTS',
      allow_open_chatgpt_tab: true,
    }, 16000);
    const result = bridgePayload(response);
    const requests = asRecords(result.requests);
    setApprovalRequests(requests);
    setApprovalResult(result);
    setApprovalStatus(response.ok === true && text(result.schema_id, '').includes('approval_requests') ? `${requests.length} action request${requests.length === 1 ? '' : 's'}` : sendFailureText(response));
    return requests;
  };

  const readQueueState = async () => {
    setAutoAcceptStatus('syncing');
    const response = await postBridgeCommand({
      type: 'READ_QUEUE_STATE',
      allow_open_chatgpt_tab: true,
    }, 16000);
    const result = bridgePayload(response);
    setAutoAcceptRuntime(result);
    setAutoAcceptStatus(response.ok === true || result.ok === true ? text(result.status ?? result.gateway_status, 'synced') : sendFailureText(response));
    return result;
  };

  const setAutoAcceptActions = async (enabled: boolean) => {
    const ttlMinutes = clampInteger(Number(autoAcceptTtlMinutes), 1, 60, 15);
    setAutoAcceptStatus(enabled ? 'turning on' : 'turning off');
    const response = await postBridgeCommand({
      type: 'SET_AUTO_ACCEPT_ACTIONS',
      allow_open_chatgpt_tab: true,
      enabled,
      ttl_seconds: ttlMinutes * 60,
    }, 26000);
    const result = bridgePayload(response);
    setAutoAcceptRuntime(result);
    setAutoAcceptStatus(response.ok === true || result.ok === true ? text(result.finding ?? result.status, enabled ? 'auto approve on' : 'auto approve off') : sendFailureText(response));
    window.setTimeout(() => {
      void requestApprovalRequests(false);
      onRuntimeRefresh?.();
    }, 900);
    return result;
  };

  const beginOptimisticSend = (textToSend: string) => {
    const id = `optimistic-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
    const createdAt = new Date().toISOString();
    setOptimisticChatEvents((previous) => [
      ...previous.filter((event) => text(event.state, '') !== 'received').slice(-8),
      {
        event_type: 'message',
        role: 'user',
        label: 'user',
        state: 'sending',
        index: previous.length,
        optimistic: true,
        optimistic_kind: 'user_send',
        optimistic_id: id,
        optimistic_expected_text: textToSend,
        created_at: createdAt,
        text_full: textToSend,
        text_preview: textToSend.replace(/\s+/g, ' ').slice(0, 220),
        streaming: true,
      },
    ]);
    return id;
  };

  const markOptimisticSent = (optimisticId: string, textToSend: string) => {
    const createdAt = new Date().toISOString();
    setOptimisticChatEvents((previous) => {
      const hasAssistant = previous.some((event) => text(event.optimistic_id, '') === `${optimisticId}:assistant`);
      const updated = previous.map((event) => (
        text(event.optimistic_id, '') === optimisticId
          ? { ...event, state: 'sent', streaming: false, sent_at: createdAt }
          : event
      ));
      if (hasAssistant) return updated;
      return [
        ...updated,
        {
          event_type: 'activity_status',
          role: 'assistant_status',
          label: 'assistant pending',
          state: 'pending',
          optimistic: true,
          optimistic_kind: 'assistant_pending',
          optimistic_id: `${optimisticId}:assistant`,
          optimistic_parent_id: optimisticId,
          optimistic_expected_text: textToSend,
          created_at: createdAt,
          text_full: 'Waiting for ChatGPT response',
          text_preview: 'Waiting for ChatGPT response',
          streaming: true,
        },
      ];
    });
  };

  const syncOptimisticTurn = (expectedText: string, syncState: ReturnType<typeof conversationSyncState>) => {
    setOptimisticChatEvents((previous) => previous.map((event) => {
      if (text(event.optimistic_expected_text, '') !== expectedText) return event;
      if (text(event.optimistic_kind, '') === 'user_send') {
        if (syncState.sawExpectedText) return { ...event, state: 'received', streaming: false, received_at: new Date().toISOString() };
        return event;
      }
      if (text(event.optimistic_kind, '') === 'assistant_pending') {
        if (syncState.sawAssistantReplyAfterExpected) {
          return { ...event, state: 'received', streaming: false, text_full: 'Assistant response received', text_preview: 'Assistant response received', received_at: new Date().toISOString() };
        }
        if (syncState.sawAssistantTextAfterExpected) {
          return { ...event, state: 'streaming', streaming: true, text_full: 'Assistant response streaming', text_preview: 'Assistant response streaming' };
        }
      }
      return event;
    }));
  };

  const resolveApprovalRequest = async (request: Record<string, unknown>, choice: 'approve' | 'reject') => {
    const requestId = text(request.request_id, '');
    setApprovalStatus(`${choice} ${approvalTitle(request)}`);
    const response = await postBridgeCommand({
      type: 'RESOLVE_APPROVAL_REQUEST',
      allow_open_chatgpt_tab: true,
      request_id: requestId,
      choice,
      approval_kind: text(request.approval_kind ?? request.kind, ''),
      kind: text(request.kind, ''),
    }, 20000);
    const result = bridgePayload(response);
    setApprovalResult(result);
    setApprovalStatus(response.ok === true || result.ok === true ? text(result.finding, `${choice} sent`) : sendFailureText(response));
    window.setTimeout(() => {
      void requestApprovalRequests(false);
      requestVisibleConversation();
      onRuntimeRefresh?.();
    }, 900);
  };

  const requestVisibleConversation = (options: { expectedText?: string; attempts?: number; intervalMs?: number; waitForAssistantReply?: boolean; targetTabId?: number; targetUrl?: string; bindTab?: boolean } = {}) => {
    const commandId = `browser-gpt-read-${Date.now().toString(36)}`;
    const timeout = window.setTimeout(() => {
      window.removeEventListener('message', handleResult);
      if (options.expectedText && (options.attempts ?? 0) > 0) {
        window.setTimeout(() => requestVisibleConversation({ ...options, attempts: (options.attempts ?? 0) - 1 }), options.intervalMs ?? 1500);
      }
    }, 6000);
    function handleResult(event: MessageEvent) {
      if (event.source !== window) return;
      const data = event.data as Record<string, unknown> | null;
      if (!data || data.source !== 'ion-browser-gpt-cockpit-bridge' || data.command_id !== commandId) return;
      window.clearTimeout(timeout);
      window.removeEventListener('message', handleResult);
      const response = (data.response ?? {}) as Record<string, unknown>;
      const result = bridgePayload(response);
      if (response.ok !== true || (!Array.isArray(result.messages) && !Array.isArray(result.timeline_events))) return;
      setLiveTranscript(result);
      if (!options.expectedText) {
        setSendStatus((current) => (current.includes('sync') ? 'sent' : current));
        return;
      }
      const syncState = conversationSyncState(result, options.expectedText ?? '');
      syncOptimisticTurn(options.expectedText ?? '', syncState);
      if (syncState.sawExpectedText && (!options.waitForAssistantReply || syncState.sawAssistantReplyAfterExpected)) {
        setDraft('');
        setSendStatus('sent');
        onRuntimeRefresh?.();
        return;
      }
      if ((options.attempts ?? 0) > 0) {
        if (syncState.sawExpectedText) {
          setDraft('');
          setSendStatus(syncState.sawAssistantTextAfterExpected ? 'reply streaming' : 'sent; awaiting reply');
        } else {
          setSendStatus((current) => current === 'sending' || current.includes('sync') ? 'syncing chat' : current);
        }
        window.setTimeout(() => requestVisibleConversation({ ...options, attempts: (options.attempts ?? 0) - 1 }), options.intervalMs ?? 1500);
        return;
      }
      if (syncState.sawExpectedText) {
        setDraft('');
        setSendStatus(syncState.sawAssistantTextAfterExpected ? 'sent; reply still syncing' : 'sent; reply pending');
      }
    }
    window.addEventListener('message', handleResult);
    window.postMessage({
      source: 'ion-browser-gpt-cockpit',
      command_id: commandId,
      payload: {
        type: 'READ_VISIBLE_CONVERSATION',
        limit: VISIBLE_CONVERSATION_LIMIT,
        allow_open_chatgpt_tab: options.expectedText ? true : undefined,
        target_tab_id: options.targetTabId,
        target_url: options.targetUrl,
        bind_tab: options.bindTab,
      },
    }, window.location.origin);
  };

  const connectChatGptTab = async () => {
    setSendStatus('connecting');
    const response = await postBridgeCommand({ type: 'READ_COMPOSER_STATE', allow_open_chatgpt_tab: true, open_active: true }, 35000);
    const result = bridgePayload(response);
    setSendStatus(response.ok === true || result.present === true ? 'bridge ready' : sendFailureText(response));
    requestVisibleConversation();
  };

  const requestDownloadableAssets = async () => {
    const response = await postBridgeCommand({ type: 'READ_DOWNLOADABLE_ASSETS', limit: 30, allow_open_chatgpt_tab: true }, 20000);
    const result = bridgePayload(response);
    const assets = asRecords(result.assets);
    setDownloadAssets(assets);
    setRightDrawer('settings');
    setRightDrawerOpen(true);
  };

  const requestNativeNavigation = async (options: { openDrawer?: boolean } = {}) => {
    setNativeNavigationStatus(options.openDrawer ? 'opening native drawer' : 'reading native urls');
    const response = await postBridgeCommand({
      type: 'READ_NATIVE_NAVIGATION',
      allow_open_chatgpt_tab: true,
      open_drawer: options.openDrawer === true,
      limit: 80,
    }, options.openDrawer ? 30000 : 18000);
    const result = bridgePayload(response);
    if (response.ok === true && text(result.schema_id, '').includes('native_navigation')) {
      setNativeNavigation(result);
      setNativeNavigationStatus(`${text(result.chat_count, '0')} chats / ${text(result.custom_gpt_count, '0')} GPTs`);
      return;
    }
    setNativeNavigationStatus(sendFailureText(response));
  };

  const openNativeChatGptUrl = async (url: unknown, options: { label?: string; focus?: boolean } = {}) => {
    const targetUrl = text(url, '');
    if (!targetUrl.startsWith('https://chatgpt.com/')) {
      setNativeNavigationStatus('invalid ChatGPT URL');
      return;
    }
    setNativeNavigationStatus(options.focus ? `focusing ${options.label ?? 'ChatGPT'}` : `loading ${options.label ?? 'ChatGPT'}`);
    const response = await postBridgeCommand({
      type: 'OPEN_CHATGPT_URL',
      allow_open_chatgpt_tab: true,
      bind_tab: true,
      open_active: options.focus === true,
      target_url: targetUrl,
    }, 18000);
    const result = bridgePayload(response);
    setNativeNavigationStatus(response.ok === true && result.ok !== false ? text(result.finding, 'navigation requested') : sendFailureText(response));
    window.setTimeout(() => {
      void requestNativeNavigation();
      void requestCurrentChatGptTabs();
      requestVisibleConversation();
    }, 1600);
  };

  const exportVisibleTranscript = () => {
    const payload = {
      schema_id: 'ion.browser_gpt_cockpit_transcript_export.v1',
      exported_at: new Date().toISOString(),
      source: transcriptSource,
      message_count: messages.length,
      timeline_event_count: timelineEvents.length,
      status_event_count: timelineStatusEvents.length,
      active_event_count: activeTimelineEvents.length,
      messages,
      timeline_events: timelineEvents,
      downloadable_assets: downloadAssets,
    };
    downloadJson(`browser-gpt-transcript-${new Date().toISOString().replace(/[^0-9A-Za-z]+/g, '').slice(0, 15)}.json`, payload);
  };

  const handleUploadFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file) return;
    setUploadStatus('reading');
    try {
      const dataBase64 = await readFileAsBase64(file);
      setUploadStatus('uploading');
      const response = await postBridgeCommand({
        type: 'UPLOAD_FILE',
        allow_open_chatgpt_tab: true,
        open_active: true,
        file: {
          name: file.name,
          mime_type: file.type || 'application/octet-stream',
          size_bytes: file.size,
          data_base64: dataBase64,
        },
        approval_receipt_id: `browser-gpt-upload-${Date.now().toString(36)}`,
      }, 70000);
      const commandResult = (response.result ?? {}) as Record<string, unknown>;
      const uploadResult = bridgePayload(response);
      const verified = text(uploadResult.upload_chip_verified, 'false') === 'true' || text(uploadResult.uploaded, 'false') === 'true';
      const finding = text(commandResult.finding ?? uploadResult.finding ?? uploadResult.file_input_finding ?? uploadResult.drop_finding ?? response.finding ?? response.error, 'attempted');
      const error = text(commandResult.error ?? uploadResult.error ?? '', '');
      setUploadStatus(verified ? 'attached' : error ? `${finding}: ${error}` : finding);
    } catch (error) {
      setUploadStatus(error instanceof Error ? error.message : 'upload failed');
    }
  };

  useEffect(() => {
    const commandId = `browser-gpt-bridge-check-${Date.now().toString(36)}`;
    const timeout = window.setTimeout(() => {
      setSendStatus((current) => (current === 'idle' ? 'extension bridge not loaded' : current));
    }, 1800);
    function handleBridge(event: MessageEvent) {
      if (event.source !== window) return;
      const data = event.data as Record<string, unknown> | null;
      if (!data || data.source !== 'ion-browser-gpt-cockpit-bridge') return;
      if (data.command_id === 'bridge-ready') {
        setSendStatus('bridge ready');
        return;
      }
      if (data.command_id !== commandId) return;
      window.clearTimeout(timeout);
      const response = (data.response ?? {}) as Record<string, unknown>;
      const result = (response.result ?? {}) as Record<string, unknown>;
      setSendStatus(response.ok === true || result.ok === true ? 'bridge ready' : sendFailureText(response));
    }
    window.addEventListener('message', handleBridge);
    window.postMessage({
      source: 'ion-browser-gpt-cockpit',
      command_id: commandId,
      payload: { type: 'READ_COMPOSER_STATE' },
    }, window.location.origin);
    requestVisibleConversation();
    void requestCurrentChatGptTabs();
    void requestScreenAutomation('status');
    void readQueueState();
    return () => {
      window.clearTimeout(timeout);
      window.removeEventListener('message', handleBridge);
    };
  }, []);

  useEffect(() => {
    if (!optimisticChatEvents.length) return undefined;
    const interval = window.setInterval(() => setClockNow(Date.now()), 1000);
    return () => window.clearInterval(interval);
  }, [optimisticChatEvents.length]);

  useEffect(() => {
    const thread = nativeThreadRef.current;
    const bottom = nativeThreadBottomRef.current;
    if (!thread || !bottom) return undefined;
    if (!nativeThreadAutoScroll && !threadHasActiveTurn) return undefined;
    const frame = window.requestAnimationFrame(() => {
      bottom.scrollIntoView({ block: 'end' });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [latestTimelineScrollKey, nativeThreadAutoScroll, threadHasActiveTurn]);

  const handleNativeThreadScroll = () => {
    const thread = nativeThreadRef.current;
    if (!thread) return;
    const distanceFromBottom = thread.scrollHeight - thread.scrollTop - thread.clientHeight;
    setNativeThreadAutoScroll(distanceFromBottom < 96);
  };

  const selectLeftDrawer = (id: LeftDrawerId) => {
    const sameDrawer = leftDrawer === id;
    setLeftDrawer(id);
    setLeftDrawerOpen(!sameDrawer || !leftDrawerOpen);
  };

  const selectRightDrawer = (id: RightDrawerId) => {
    const sameDrawer = rightDrawer === id;
    setRightDrawer(id);
    setRightDrawerOpen(!sameDrawer || !rightDrawerOpen);
  };

  const workbenchGridClassName = [
    'ion-codex-workbench-grid',
    leftDrawerOpen ? 'has-left-drawer-open' : '',
    leftDrawerOpen && leftDrawer === 'atlas' ? 'has-file-drawer-open' : '',
    rightDrawerOpen ? 'has-right-drawer-open' : '',
  ].filter(Boolean).join(' ');

  const sendTextToChatGpt = async (
    rawText: string,
    options: { clearDraft?: boolean; statusLabel?: string; receiptLabel?: string } = {},
  ) => {
    const textToSend = rawText.trim();
    if (!textToSend || sendBusy) return false;
    const commandId = `browser-gpt-send-${Date.now().toString(36)}`;
    const optimisticId = beginOptimisticSend(textToSend);
    const label = options.statusLabel ?? 'send';
    setSendStatus(label === 'send' ? 'sending' : `${label} sending`);
    const response = await postBridgeCommand({
      type: 'APPROVED_SEND_DRAFT',
      allow_open_chatgpt_tab: true,
      text: textToSend,
      mode: 'replace',
      replace_existing: true,
      approval_receipt_id: `${options.receiptLabel ?? 'browser-gpt-send'}-${commandId}`,
    }, 18000);
    const result = (response.result ?? {}) as Record<string, unknown>;
    const nested = (result.result ?? {}) as Record<string, unknown>;
    const ok = response.ok === true && result.ok !== false && (result.ok === true || nested.send_clicked === true);
    if (ok || text(response.finding, '') === 'browser_gpt_command_timeout') {
      if (options.clearDraft) setDraft('');
      setSendStatus(ok ? 'sent; syncing' : 'send requested; syncing');
      markOptimisticSent(optimisticId, textToSend);
      requestVisibleConversation({ expectedText: textToSend, attempts: 20, intervalMs: 1500, waitForAssistantReply: true });
      window.setTimeout(() => requestVisibleConversation({ expectedText: textToSend, attempts: 24, intervalMs: 1500, waitForAssistantReply: true }), 1200);
      return true;
    }
    setOptimisticChatEvents((previous) => previous.map((event) => (
      text(event.optimistic_id, '') === optimisticId
        ? { ...event, state: 'blocked', streaming: false, text_full: textToSend, send_error: sendFailureText(response) }
        : event
    )));
    setSendStatus(sendFailureText(response));
    return false;
  };

  const sendDraftToChatGpt = () => {
    void sendTextToChatGpt(draft, { clearDraft: true, statusLabel: 'send', receiptLabel: 'browser-gpt-draft' });
  };

  const sendProceedMessage = async (source: 'manual' | 'auto' = 'manual') => {
    setAutoProceedStatus(source === 'auto' ? 'auto sending proceed' : 'manual proceed');
    const ok = await sendTextToChatGpt('proceed', {
      clearDraft: false,
      statusLabel: source === 'auto' ? 'auto proceed' : 'proceed',
      receiptLabel: source === 'auto' ? 'browser-gpt-auto-proceed' : 'browser-gpt-proceed',
    });
    setAutoProceedStatus(ok ? (source === 'auto' ? 'auto proceed sent' : 'proceed sent') : 'proceed blocked');
    return ok;
  };

  const armAutoProceed = () => {
    const count = clampInteger(Number(autoProceedCountInput), 0, 20, 3);
    if (count <= 0) {
      setAutoProceedRemaining(0);
      setAutoProceedStatus('off');
      return;
    }
    setAutoProceedAnchor(latestCompletedAssistantSignature);
    setAutoProceedRemaining(count);
    setAutoProceedStatus(`armed ${count}`);
  };

  const stopAutoProceed = () => {
    setAutoProceedRemaining(0);
    setAutoProceedStatus('off');
  };

  const sendAgentCommsMessage = async () => {
    const body = agentCommsMessage.trim();
    if (!body || agentCommsBusy) return;
    setAgentCommsBusy(true);
    setAgentCommsStatus('sending');
    try {
      const response = await fetch('/cockpit/agents/comms/send', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel_id: selectedAgentChannelId,
          thread_id: selectedAgentThreadId || undefined,
          from_role: 'operator',
          to_roles: agentCommsTarget ? [agentCommsTarget] : [],
          message_kind: 'operator_intent',
          subject: agentCommsSubject.trim() || 'Browser GPT worker follow-up',
          body,
          requires_response: true,
          source_refs: [
            text(selectedAgentThread.path, ''),
            browserGptTarget,
            browserGptProbePath,
          ].filter(Boolean),
        }),
        cache: 'no-store',
      });
      const result = (await response.json()) as Record<string, unknown>;
      setAgentCommsRequestState(result);
      setAgentCommsStatus(response.ok && (truth(result.ok) || !text(result.finding, '').includes('failed')) ? text(result.finding, 'sent') : text(result.finding ?? result.error, `http ${response.status}`));
      if (response.ok && truth(result.ok)) {
        setAgentCommsMessage('');
        setAgentCommsThreadId(text(result.thread_id ?? result.new_thread_id ?? selectedAgentThreadId, selectedAgentThreadId));
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setAgentCommsStatus(error instanceof Error ? error.message : 'agent comms send failed');
      setAgentCommsRequestState({ ok: false, finding: error instanceof Error ? error.message : 'agent_comms_send_failed' });
    } finally {
      setAgentCommsBusy(false);
    }
  };

  const toggleMergeTab = (tab: Record<string, unknown>) => {
    const key = browserGptTabKey(tab);
    if (!key) return;
    setMergeSelectedTabIds((previous) => previous.includes(key) ? previous.filter((item) => item !== key) : [...previous, key]);
  };

  const toggleMergeCodexSession = (session: Record<string, unknown>) => {
    const key = text(session.session_id, '');
    if (!key) return;
    setMergeSelectedCodexSessionIds((previous) => previous.includes(key) ? previous.filter((item) => item !== key) : [...previous, key]);
  };

  const toggleMergeAgent = (agent: Record<string, unknown>) => {
    const key = mergeAgentRoleId(agent);
    if (!key) return;
    setMergeSelectedAgentRoleIds((previous) => previous.includes(key) ? previous.filter((item) => item !== key) : [...previous, key]);
  };

  const stageMergeContextBlock = () => {
    setDraft((previous) => appendText(previous, mergeContextBlock));
    setMergeCommsStatus('staged for ChatGPT');
  };

  const sendMergeContextToChatGpt = async () => {
    setMergeCommsStatus('sending context tag');
    const ok = await sendTextToChatGpt(mergeContextBlock, {
      clearDraft: false,
      statusLabel: 'merge context',
      receiptLabel: 'browser-gpt-merge-context',
    });
    setMergeCommsStatus(ok ? 'context sent to active ChatGPT tab' : 'context send blocked');
  };

  const attachSelectedCodexChats = async () => {
    if (mergeArchiveAttachBusy || !selectedCodexSessions.length) return selectedMergeArchiveAttachments;
    setMergeArchiveAttachBusy(true);
    setMergeArchiveAttachStatus(`attaching ${selectedCodexSessions.length}`);
    const attached: Record<string, Record<string, unknown>> = {};
    const failures: string[] = [];
    try {
      for (const session of selectedCodexSessions) {
        const sessionId = text(session.session_id, '');
        if (!sessionId) continue;
        const existing = mergeArchiveAttachments[sessionId];
        if (existing) {
          attached[sessionId] = existing;
          continue;
        }
        const response = await fetch('/cockpit/chat/archive/attach', {
          method: 'POST',
          headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
          body: JSON.stringify(withPublicToken({
            session_id: sessionId,
            confirmation: WRITE_CONFIRMATION_TOKEN,
            prompt: `Browser GPT merge room: ${mergeRoomName.trim() || 'Browser GPT merge room'}`,
          })),
          cache: 'no-store',
        });
        const result = (await response.json().catch(() => ({}))) as Record<string, unknown>;
        if (!response.ok || result.ok === false) {
          failures.push(`${shortMiddle(sessionId, 16)}:${text(result.finding ?? result.error, `http ${response.status}`)}`);
          continue;
        }
        attached[sessionId] = normalizeMergeArchiveAttachment(result, session);
      }
      if (Object.keys(attached).length) {
        setMergeArchiveAttachments((previous) => ({ ...previous, ...attached }));
      }
      const resultState = {
        ok: failures.length === 0,
        attached_count: Object.keys(attached).length,
        requested_count: selectedCodexSessions.length,
        failures,
        attachments: Object.values(attached),
      };
      setMergeArchiveAttachRequestState(resultState);
      setMergeArchiveAttachStatus(failures.length ? `${Object.keys(attached).length} attached / ${failures.length} failed` : `${Object.keys(attached).length} attached`);
      await onRuntimeRefresh?.();
      return uniqueAttachmentRows([...selectedMergeArchiveAttachments, ...Object.values(attached)]);
    } catch (error) {
      setMergeArchiveAttachStatus(error instanceof Error ? error.message : 'archive attach failed');
      setMergeArchiveAttachRequestState({ ok: false, finding: error instanceof Error ? error.message : 'merge_archive_attach_failed' });
      return selectedMergeArchiveAttachments;
    } finally {
      setMergeArchiveAttachBusy(false);
    }
  };

  const sendMergeCommsRoomPacket = async () => {
    if (agentCommsBusy) return;
    setAgentCommsBusy(true);
    setMergeCommsStatus('sending room packet');
    try {
      const response = await fetch('/cockpit/agents/comms/send', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel_id: selectedAgentChannelId,
          thread_id: selectedAgentThreadId || undefined,
          from_role: 'operator',
          to_roles: mergeTargetRoles,
          message_kind: 'operator_intent',
          subject: `Visual merge: ${mergeRoomName.trim() || 'Browser GPT merge room'}`,
          body: mergeContextBlock,
          requires_response: true,
          source_refs: mergeSourceRefs,
          tags: uniqueStrings([...mergeTags, 'codex-cli', 'codex-agent', 'visual-merge']),
        }),
        cache: 'no-store',
      });
      const result = (await response.json()) as Record<string, unknown>;
      setMergeCommsRequestState(result);
      setAgentCommsRequestState(result);
      setMergeCommsStatus(response.ok && truth(result.ok) ? text(result.finding, 'room packet sent') : text(result.finding ?? result.error, `http ${response.status}`));
      if (response.ok && truth(result.ok)) {
        setAgentCommsThreadId(text(result.thread_id ?? result.new_thread_id ?? selectedAgentThreadId, selectedAgentThreadId));
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setMergeCommsStatus(error instanceof Error ? error.message : 'merge room packet failed');
      setMergeCommsRequestState({ ok: false, finding: error instanceof Error ? error.message : 'merge_room_packet_failed' });
    } finally {
      setAgentCommsBusy(false);
    }
  };

  const startMergeReworkRun = async () => {
    if (agentCommsBusy || mergeArchiveAttachBusy) return;
    if (!mergeRunTargetRoles.length) {
      setMergeReworkStatus('select a Codex agent');
      setMergeReworkRequestState({ ok: false, finding: 'merge_rework_target_required' });
      return;
    }
    setAgentCommsBusy(true);
    setMergeReworkStatus('starting rework run');
    try {
      const runAttachments = selectedCodexSessions.length ? await attachSelectedCodexChats() : selectedMergeArchiveAttachments;
      const runSourceRefs = mergeRoomSourceRefs({
        browserGptProbePath,
        browserGptTarget,
        tabs: effectiveMergeTabs,
        threadId: selectedAgentThreadId,
        codexSessions: selectedCodexSessions,
        codexAttachments: runAttachments,
        codexAgents: selectedMergeAgents,
      });
      const runContextBlock = buildVisualMergeContextBlock({
        roomName: mergeRoomName,
        tags: mergeTags,
        tabs: effectiveMergeTabs,
        context: mergeContext,
        commsChannelId: selectedAgentChannelId,
        commsThreadId: selectedAgentThreadId,
        targetRole: mergeTargetRoles.join(', '),
        actionStatus: actionStateLabel,
        codexArchiveStatus,
        codexWorkbenchState,
        codexSessions: selectedCodexSessions,
        codexAttachments: runAttachments,
        codexAgents: selectedMergeAgents,
      });
      const response = await fetch('/cockpit/agents/comms/run/start', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify({
          objective: `Rework visual merge room: ${mergeRoomName.trim() || 'Browser GPT merge room'}`,
          body: runContextBlock,
          from_role: 'operator',
          target_roles: mergeRunTargetRoles,
          dispatch_mode: 'queue_workpack',
          channel_id: selectedAgentChannelId,
          thread_id: selectedAgentThreadId || undefined,
          max_directives: Math.max(1, Math.min(mergeRunTargetRoles.length || 1, 8)),
          max_agents: Math.max(2, Math.min(mergeRunTargetRoles.length + 1, 12)),
          max_workpacks: Math.max(2, Math.min(mergeRunTargetRoles.length + selectedCodexSessions.length + 1, 25)),
          automation_prompt_limit: 8,
          automation_window_minutes: 60,
          automation_time_budget_minutes: 120,
          source_refs: runSourceRefs,
          tags: uniqueStrings([...mergeTags, 'codex-cli', 'codex-agent', 'visual-merge', 'rework-run']),
        }),
        cache: 'no-store',
      });
      const result = (await response.json()) as Record<string, unknown>;
      setMergeReworkRequestState(result);
      setAgentCommsRequestState(result);
      setMergeReworkStatus(response.ok && truth(result.ok) ? text(result.finding ?? result.status, 'rework run started') : text(result.finding ?? result.error, `http ${response.status}`));
      if (response.ok && truth(result.ok)) {
        setAgentCommsThreadId(text(result.thread_id ?? asStrings(result.thread_ids)[0] ?? selectedAgentThreadId, selectedAgentThreadId));
        setRightDrawer('workers');
        setRightDrawerOpen(true);
      }
      await onRuntimeRefresh?.();
    } catch (error) {
      setMergeReworkStatus(error instanceof Error ? error.message : 'merge rework run failed');
      setMergeReworkRequestState({ ok: false, finding: error instanceof Error ? error.message : 'merge_rework_run_failed' });
    } finally {
      setAgentCommsBusy(false);
    }
  };

  const runAgentCommsAction = async (action: 'continue' | 'worker' | 'audit', run: Record<string, unknown> = activeAgentRun) => {
    const runId = text(run.run_id, '');
    if (!runId || agentCommsBusy) return;
    const workpackPath = browserGptRunWorkpackPath(run);
    if (action === 'worker' && !workpackPath) {
      setAgentCommsStatus('workpack required');
      setAgentCommsRequestState({ ok: false, finding: 'run_workpack_required' });
      return;
    }
    setAgentCommsBusy(true);
    setAgentCommsStatus(`${action} requested`);
    const endpoint = action === 'continue'
      ? '/cockpit/agents/comms/run/continue'
      : action === 'worker'
        ? '/cockpit/agents/comms/run/start-worker'
        : '/cockpit/agents/comms/run/audit';
    const payload = action === 'continue'
      ? { run_id: runId, max_directives: 3, max_worker_starts: 1, start_workers: true, timeout_seconds: 1800 }
      : action === 'worker'
        ? { run_id: runId, workpack_path: workpackPath, timeout_seconds: 1800 }
        : { run_id: runId, strict_pristine: true, write_receipt: true };
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        cache: 'no-store',
      });
      const result = (await response.json()) as Record<string, unknown>;
      setAgentCommsRequestState(result);
      setAgentCommsStatus(response.ok ? text(result.finding ?? result.status, `${action} complete`) : text(result.finding ?? result.error, `http ${response.status}`));
      await onRuntimeRefresh?.();
    } catch (error) {
      setAgentCommsStatus(error instanceof Error ? error.message : `agent run ${action} failed`);
      setAgentCommsRequestState({ ok: false, finding: error instanceof Error ? error.message : `agent_comms_${action}_failed` });
    } finally {
      setAgentCommsBusy(false);
    }
  };

  const rememberLargeArtifactResult = (key: string, result: Record<string, unknown>) => {
    setLargeArtifactResults((previous) => ({
      ...previous,
      [key]: result,
      latest: result,
    }));
  };

  const invokeCockpitBranch = async (
    branchId: string,
    routeId: string,
    args: Record<string, unknown> = {},
    options: Record<string, unknown> = {},
  ) => {
    const response = await fetch('/cockpit/action-branch/invoke', {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(withPublicToken({
        branch_id: branchId,
        route_id: routeId,
        args,
        expected_route_schema_version: 'v0',
        ...options,
      })),
      cache: 'no-store',
    });
    const result = (await response.json().catch(() => ({}))) as Record<string, unknown>;
    return {
      ...result,
      http_status: response.status,
      ok: result.ok ?? response.ok,
    };
  };

  const runLargeArtifactRoute = async (
    key: string,
    branchId: string,
    routeId: string,
    args: Record<string, unknown> = {},
    options: Record<string, unknown> = {},
  ) => {
    setRightDrawer('artifacts');
    setRightDrawerOpen(true);
    setLargeArtifactStatus(routeId);
    try {
      const result = await invokeCockpitBranch(branchId, routeId, args, options);
      rememberLargeArtifactResult(key, result);
      setLargeArtifactStatus(text(result.finding ?? asRecord(result.delegated_result).finding ?? asRecord(result.delegated_result).status, truth(result.ok) ? 'ready' : 'blocked'));
      return result;
    } catch (error) {
      const result = { ok: false, finding: error instanceof Error ? error.message : `${routeId}_failed` };
      rememberLargeArtifactResult(key, result);
      setLargeArtifactStatus(text(result.finding, 'route failed'));
      return result;
    }
  };

  const profileLargeArtifact = () => runLargeArtifactRoute(
    'profile',
    'large_artifact_intelligence',
    'large_file_profile',
    { path: largeArtifactPath.trim() },
  );

  const manifestLargeArtifact = () => runLargeArtifactRoute(
    'manifest',
    'large_artifact_intelligence',
    'large_file_chunk_manifest',
    { path: largeArtifactPath.trim(), chunk_size_bytes: 32768 },
  );

  const searchLargeArtifact = () => runLargeArtifactRoute(
    'search',
    'large_artifact_intelligence',
    'large_file_anchor_search',
    { path: largeArtifactPath.trim(), query: largeArtifactQuery.trim(), max_hits: 8 },
  );

  const readLargeArtifactSlice = () => runLargeArtifactRoute(
    'slice',
    'large_artifact_intelligence',
    'large_file_slice_read',
    {
      path: largeArtifactPath.trim(),
      start_line: clampInteger(Number(largeArtifactSliceStart), 1, 20_000_000, 1),
      line_count: clampInteger(Number(largeArtifactSliceLines), 1, 400, 80),
      max_bytes: 32000,
    },
  );

  const startLargeArtifactStream = () => runLargeArtifactRoute(
    'stream_start',
    'large_artifact_intelligence',
    'large_file_stream_start',
    { path: largeArtifactPath.trim(), chunk_size_bytes: 32768 },
  );

  const nextLargeArtifactChunk = () => {
    if (!artifactCursor) {
      setLargeArtifactStatus('stream cursor missing');
      return Promise.resolve({ ok: false, finding: 'stream_cursor_missing' });
    }
    return runLargeArtifactRoute(
      'stream_next',
      'large_artifact_intelligence',
      'large_file_stream_next',
      { cursor: artifactCursor, max_response_bytes: 36000 },
    );
  };

  const rangeLargeArtifactChunks = () => {
    const artifactId = text(largeArtifactStream.artifact_id, '');
    if (!artifactId) {
      setLargeArtifactStatus('artifact id missing');
      return Promise.resolve({ ok: false, finding: 'artifact_id_missing' });
    }
    return runLargeArtifactRoute(
      'stream_range',
      'large_artifact_intelligence',
      'large_file_stream_range',
      { artifact_id: artifactId, chunk_start: 0, chunk_count: 2, chunk_size_bytes: 32768 },
    );
  };

  const readLargeArtifactJsonPath = () => runLargeArtifactRoute(
    'json_path',
    'large_artifact_intelligence',
    'large_file_json_path_read',
    { path: largeArtifactPath.trim(), json_path: largeArtifactJsonPath.trim(), limit: 40, max_bytes: 32000 },
  );

  const readLargeArtifactSection = () => runLargeArtifactRoute(
    'section',
    'large_artifact_intelligence',
    'large_file_section_read',
    { path: largeArtifactPath.trim(), heading: largeArtifactHeading.trim(), include_children: true, max_bytes: 32000 },
  );

  const checkLargeArtifactClaim = () => runLargeArtifactRoute(
    'claim',
    'large_artifact_intelligence',
    'large_artifact_claim_check',
    {
      claim: inferenceQuestion.trim(),
      evidence_refs: [{
        path: largeArtifactPath.trim(),
        start_line: clampInteger(Number(largeArtifactSliceStart), 1, 20_000_000, 1),
        line_count: clampInteger(Number(largeArtifactSliceLines), 1, 400, 80),
      }],
    },
  );

  const previewArtifactZip = () => runLargeArtifactRoute(
    'zip_preview',
    'artifact_transfer',
    'zip_request_preview',
    {
      paths: [largeArtifactPath.trim()],
      package_label: artifactPackageLabel.trim() || 'browser-gpt-artifact',
      max_bytes: clampInteger(Number(artifactMaxBytes), 1, 50_000_000, 2_000_000),
    },
  );

  const materializeArtifactZip = () => {
    const idempotencyKey = `browser-gpt-artifact-${Date.now().toString(36)}`;
    return runLargeArtifactRoute(
      'zip_materialize',
      'artifact_transfer',
      'zip_materialize_request',
      {
        paths: [largeArtifactPath.trim()],
        package_label: artifactPackageLabel.trim() || 'browser-gpt-artifact',
        max_bytes: clampInteger(Number(artifactMaxBytes), 1, 50_000_000, 2_000_000),
        confirmation: WRITE_CONFIRMATION_TOKEN,
        idempotency_key: idempotencyKey,
      },
      {
        confirmation: WRITE_CONFIRMATION_TOKEN,
        idempotency_key: idempotencyKey,
      },
    );
  };

  const readArtifactManifest = () => {
    if (!artifactPackageId) {
      setLargeArtifactStatus('package id missing');
      return Promise.resolve({ ok: false, finding: 'package_id_missing' });
    }
    return runLargeArtifactRoute(
      'zip_manifest',
      'artifact_transfer',
      'zip_manifest_read',
      { package_id: artifactPackageId },
    );
  };

  const readSandboxInstruction = () => {
    if (!artifactPackageId) {
      setLargeArtifactStatus('package id missing');
      return Promise.resolve({ ok: false, finding: 'package_id_missing' });
    }
    return runLargeArtifactRoute(
      'sandbox_instruction',
      'artifact_transfer',
      'sandbox_upload_instruction',
      { package_id: artifactPackageId },
    );
  };

  const runInferenceStatus = () => runLargeArtifactRoute(
    'inference_status',
    'large_artifact_inference_preview',
    'inference_provider_status',
    {},
  );

  const runInferencePlan = () => runLargeArtifactRoute(
    'inference_plan',
    'large_artifact_inference_preview',
    'inference_plan_preview',
    { path: largeArtifactPath.trim(), provider: 'codex_spark_preview', task: 'summarize' },
  );

  const runInferenceIndex = () => runLargeArtifactRoute(
    'inference_index',
    'large_artifact_inference_preview',
    'large_artifact_inference_index_preview',
    { path: largeArtifactPath.trim(), provider: 'codex_spark_preview' },
  );

  const runInferenceQuestion = () => runLargeArtifactRoute(
    'inference_question',
    'large_artifact_inference_preview',
    'large_artifact_inference_question_preview',
    { path: largeArtifactPath.trim(), question: inferenceQuestion.trim() },
  );

  const handleDraftKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return;
    event.preventDefault();
    if (!draft.trim() || sendBusy) return;
    sendDraftToChatGpt();
  };

  useEffect(() => {
    if (autoProceedRemaining <= 0 || !latestCompletedAssistantSignature) return undefined;
    if (latestCompletedAssistantSignature === autoProceedAnchor) return undefined;
    if (activeTimelineEvents.length > 0 || sendBusy || autoProceedBusyRef.current) return undefined;
    const timer = window.setTimeout(() => {
      if (autoProceedBusyRef.current) return;
      autoProceedBusyRef.current = true;
      setAutoProceedAnchor(latestCompletedAssistantSignature);
      void sendProceedMessage('auto')
        .then((ok) => {
          if (ok) setAutoProceedRemaining((previous) => Math.max(0, previous - 1));
        })
        .finally(() => {
          autoProceedBusyRef.current = false;
        });
    }, 1400);
    return () => window.clearTimeout(timer);
  }, [activeTimelineEvents.length, autoProceedAnchor, autoProceedRemaining, latestCompletedAssistantSignature, sendBusy]);

  return (
    <section className="ion-codex-workbench-shell has-external-subnav ion-browser-gpt-native-workbench" aria-label="Browser GPT DOM workbench">
      <div className={workbenchGridClassName}>
        <aside className="ion-codex-rail ion-codex-left-rail" aria-label="Browser GPT left drawers">
          <BrowserGptIconBar items={leftRailItems} active={leftDrawerOpen ? leftDrawer : undefined} onSelect={selectLeftDrawer} />
        </aside>
        <aside className={`ion-codex-drawer-panel ion-codex-left-drawer${leftDrawer === 'atlas' ? ' is-files-drawer' : ''}${leftDrawerOpen ? ' is-open' : ''}`} aria-hidden={!leftDrawerOpen} aria-label="Browser GPT left drawer">
          <div className="ion-codex-drawer-head">
            <span>{drawerTitle(leftRailItems, leftDrawer)}</span>
            <button aria-label="Close left drawer" onClick={() => setLeftDrawerOpen(false)} title="Close left drawer" type="button">
              <CloseIcon className="ion-close-icon" />
            </button>
          </div>
          <div className="ion-codex-drawer-body">{renderLeftDrawer(leftDrawer)}</div>
        </aside>

        <main className="ion-codex-main-pane">
          <section className="ion-browser-gpt-native-console">
            <header className="ion-browser-gpt-native-head is-compact">
              <div className="ion-browser-gpt-native-title is-compact" title={`ChatGPT DOM Twin / ${browserGptTarget} / ${browserGptProbePath}`}>
                <ChatIcon />
                <span>GPT DOM</span>
                <b>{text(twin.status, 'missing')}</b>
                <code>{shortMiddle(browserGptTarget, 46)}</code>
              </div>
              <div className="ion-browser-gpt-native-kpis is-compact" aria-label="Browser GPT compact status">
                <CompactStatusChip icon={<StatusIcon />} label="Twin" value={text(twin.status, 'missing')} tone={toolbarStatusTone(text(twin.status, 'missing'), text(twin.status, '') === 'ready')} />
                <CompactStatusChip icon={<LensIcon />} label="Coverage" value={coverageCount} tone={toolbarStatusTone(coverageCount, Number(effectiveCoverage.found_surface_count ?? 0) > 0)} />
                <CompactStatusChip icon={<ChatIcon />} label="Events" value={String(timelineEvents.length)} tone={timelineEvents.length ? 'ready' : 'watch'} />
                <CompactStatusChip icon={<RunIcon />} label="Active" value={activeStateLabel} tone={activeTimelineEvents.length ? 'ready' : 'watch'} />
                <CompactStatusChip icon={<ToolsIcon />} label="Tools" value={String(toolTimelineEvents.length)} tone={toolTimelineEvents.length ? 'ready' : 'watch'} />
                <CompactStatusChip icon={<AuthorityIcon />} label="Actions" value={actionStateLabel} tone={pendingApprovalRequests.length ? 'watch' : toolbarStatusTone(approvalStatus, true)} />
                <CompactStatusChip icon={<WorkSurfaceIcon />} label="Workers" value={workerStateLabel} tone={activeWorkerCount ? 'ready' : toolbarStatusTone(agentCommsRuns.active_run_count, Number(agentCommsRuns.run_count ?? 0) > 0)} />
                <CompactStatusChip icon={<WorkSurfaceIcon />} label="Merge" value={mergeRoomStatus} tone={effectiveMergeTabs.length ? 'ready' : 'watch'} />
                <CompactStatusChip icon={<ArchiveIcon />} label="Artifacts" value={text(largeArtifactProfile.oversize, '') === 'true' ? 'large' : largeArtifactStatus} tone={artifactStatusTone} />
                <CompactStatusChip icon={<SettingsIcon />} label="Model" value={selectedModel} tone={selectedModel === 'model' ? 'watch' : 'ready'} />
                <CompactStatusChip icon={<StatusIcon />} label="Thinking" value={selectedThinking} tone={selectedThinking === 'thinking' ? 'watch' : 'ready'} />
                <CompactStatusChip icon={<ChatIcon />} label="Tabs" value={String(chatGptTabs.length)} tone={chatGptTabs.length ? 'ready' : 'watch'} />
                <CompactStatusChip icon={<ComposeIcon />} label="Send" value={sendIsGated ? 'gated' : 'unsafe'} tone={sendIsGated ? 'watch' : 'missing'} />
                <CompactStatusChip icon={<EvidenceIcon />} label="Issues" value={blockingIssues} tone={Number(blockingIssues) ? 'missing' : 'ready'} />
                <CompactStatusChip icon={<LensIcon />} label="Agent" value={text(codexBrowserAgent.status, 'missing')} tone={toolbarStatusTone(codexBrowserAgent.status, Boolean(codexBrowserAgent.status))} />
                <CompactStatusChip icon={<WorkSurfaceIcon />} label="Assistant" value={`${assistantReadyLaneCount}/${assistantLaneCount}`} tone={assistantLanes.length ? 'ready' : 'watch'} />
              </div>
              <div className="ion-browser-gpt-native-bridge-strip is-compact" title={`Open tabs / native history / relay / ${bridgeSummary}`}>
                <CompactToolbarButton
                  icon={<ChatIcon />}
                  label="Read open tabs"
                  onClick={() => { setLeftDrawer('tabs'); setLeftDrawerOpen(true); void requestCurrentChatGptTabs(); }}
                  status={chatGptTabs.length ? `${chatGptTabs.length} open` : chatGptTabsStatus}
                  tone={chatGptTabs.length ? 'ready' : 'watch'}
                />
                <CompactToolbarButton
                  icon={<ArchiveIcon />}
                  label="Read native chats"
                  onClick={() => { setLeftDrawer('native'); setLeftDrawerOpen(true); void requestNativeNavigation({ openDrawer: true }); }}
                  status={nativeNavigation ? `${nativeChats.length} chats` : nativeNavigationStatus}
                  tone={nativeNavigation ? 'ready' : 'watch'}
                />
                <CompactToolbarButton
                  icon={<EvidenceIcon />}
                  label="Relay history"
                  onClick={() => void relayVisibleConversation()}
                  status={relayStatus}
                  tone={toolbarStatusTone(relayStatus, true)}
                />
                <CompactToolbarButton
                  icon={<AuthorityIcon />}
                  label="Actions"
                  onClick={() => { setRightDrawer('actions'); setRightDrawerOpen(true); void requestApprovalRequests(false); }}
                  status={actionStateLabel}
                  tone={pendingApprovalRequests.length ? 'watch' : toolbarStatusTone(approvalStatus, true)}
                />
                <CompactToolbarButton
                  icon={<WorkSurfaceIcon />}
                  label="Workers"
                  onClick={() => { setRightDrawer('workers'); setRightDrawerOpen(true); }}
                  status={workerStateLabel}
                  tone={activeWorkerCount ? 'ready' : toolbarStatusTone(agentCommsRuns.active_run_count, Number(agentCommsRuns.run_count ?? 0) > 0)}
                />
                <CompactToolbarButton
                  icon={<ArchiveIcon />}
                  label="Artifacts"
                  onClick={() => { setRightDrawer('artifacts'); setRightDrawerOpen(true); }}
                  status={largeArtifactStatus}
                  tone={artifactStatusTone}
                />
                <CompactToolbarButton
                  icon={<RunIcon />}
                  label="Focus GPT tab"
                  onClick={() => void openNativeChatGptUrl(nativeCurrent.url ?? browserGptDom.target_url ?? browserGptDom.origin ?? 'https://chatgpt.com/', { label: 'current ChatGPT', focus: true })}
                  status="focus"
                  tone="ready"
                />
              </div>
            </header>

            <section className="ion-browser-gpt-native-thread" aria-label="Visible ChatGPT conversation mirror" onScroll={handleNativeThreadScroll} ref={nativeThreadRef}>
              {timelineEvents.length > 0 ? (
                timelineEvents.slice(-VISIBLE_CONVERSATION_LIMIT).map((event, index) => {
                  const eventType = timelineEventType(event);
                  const eventState = timelineEventState(event);
                  const eventDetail = text(event.service_name ?? event.duration_text ?? optimisticElapsedLabel(event, clockNow), '');
                  return (
                  <article
                    className={`ion-browser-gpt-native-message is-${roleClass(event.role)} is-event-${timelineEventClass(eventType)} is-state-${timelineEventClass(eventState)}${text(event.optimistic, 'false') === 'true' ? ' is-optimistic' : ''}`}
                    key={`${eventType}-${text(event.event_index ?? event.index, String(index))}-${text(event.text_sha256 ?? event.dom_anchor, 'event')}`}
                  >
                    <div className="ion-browser-gpt-native-message-head">
                      <span>{timelineEventTitle(event)}</span>
                      <b>{timelineEventMeta(event, index)}</b>
                      {eventDetail ? <em>{eventDetail}</em> : null}
                    </div>
                    {hasThinkingDom(event) ? (
                      <details className="ion-browser-gpt-thinking-panel">
                        <summary>{text(event.thinking_preview, 'Thinking details')}</summary>
                        <pre>{text(event.thinking_full_text ?? event.thinking_preview, '')}</pre>
                      </details>
                    ) : null}
                    <p>{messageBody(event)}</p>
                  </article>
                  );
                })
              ) : (
                <div className="ion-browser-gpt-native-empty">
                  <WorkSurfaceIcon />
                  <b>{transcriptSource === 'unreadable_anchors' ? 'message anchors found without readable text' : text(transcript.message_list_selector, 'message list unavailable')}</b>
                  <span>{`events ${timelineEvents.length} / readable ${messages.length} / raw ${text(transcript.raw_visible_message_count ?? transcript.message_count, '0')}`}</span>
                </div>
              )}
              <div className="ion-browser-gpt-native-thread-bottom" ref={nativeThreadBottomRef} />
            </section>

            <div className="ion-browser-gpt-native-contextbar">
              {surfaceGroups.map((group) => (
                <button key={group.id} onClick={() => { setLeftDrawer('surfaces'); setLeftDrawerOpen(true); }} type="button">
                  <span>{group.label}</span>
                  <b>{group.surfaceIds.filter((surfaceId) => controlBySurface.get(surfaceId)?.present).length}/{group.surfaceIds.length}</b>
                </button>
              ))}
              <button onClick={() => { setRightDrawer('probe'); setRightDrawerOpen(true); }} type="button">
                <span>Probe</span>
                <b>{text(probeIntake.status, 'unknown')}</b>
              </button>
              <button onClick={onRuntimeRefresh} type="button">
                <span>Refresh</span>
                <b>model</b>
              </button>
              <button onClick={requestVisibleConversation} type="button">
                <span>Read</span>
                <b>{transcriptSource}</b>
              </button>
              <button onClick={() => { setLeftDrawer('chat'); setLeftDrawerOpen(true); }} type="button">
                <span>Events</span>
                <b>{timelineEvents.length}/{timelineStatusEvents.length}</b>
              </button>
              <button onClick={() => { setLeftDrawer('chat'); setLeftDrawerOpen(true); }} type="button">
                <span>Active</span>
                <b>{activeTimelineEvents.length ? `${activeTimelineEvents.length} live` : 'quiet'}</b>
              </button>
              <button onClick={() => { setRightDrawer('actions'); setRightDrawerOpen(true); void requestApprovalRequests(false); }} type="button">
                <span>Action sync</span>
                <b>{actionStateLabel}</b>
              </button>
              <button onClick={() => { setRightDrawer('workers'); setRightDrawerOpen(true); }} type="button">
                <span>Workers</span>
                <b>{workerStateLabel}</b>
              </button>
              <button onClick={() => { setRightDrawer('artifacts'); setRightDrawerOpen(true); }} type="button">
                <span>Artifacts</span>
                <b>{largeArtifactStatus}</b>
              </button>
              <button onClick={connectChatGptTab} type="button">
                <span>Connect</span>
                <b>tab</b>
              </button>
              <button onClick={() => { setLeftDrawer('native'); setLeftDrawerOpen(true); void requestNativeNavigation({ openDrawer: true }); }} type="button">
                <span>Native</span>
                <b>{nativeNavigation ? `${nativeChats.length}/${nativeCustomGpts.length}` : nativeNavigationStatus}</b>
              </button>
              <button onClick={() => { setLeftDrawer('tabs'); setLeftDrawerOpen(true); void requestCurrentChatGptTabs(); }} type="button">
                <span>Tabs</span>
                <b>{chatGptTabs.length ? `${chatGptTabs.length} open` : chatGptTabsStatus}</b>
              </button>
              <button onClick={() => { setLeftDrawer('merge'); setLeftDrawerOpen(true); }} type="button">
                <span>Merge</span>
                <b>{mergeRoomStatus}</b>
              </button>
              <button onClick={() => { setLeftDrawer('atlas'); setLeftDrawerOpen(true); }} type="button">
                <span>Atlas</span>
                <b>{atlasRefs.length}</b>
              </button>
              <button onClick={() => void relayVisibleConversation()} type="button">
                <span>Relay</span>
                <b>{relayStatus}</b>
              </button>
              <button onClick={() => void openNativeChatGptUrl('https://chatgpt.com/', { label: 'new chat' })} type="button">
                <span>New</span>
                <b>chat</b>
              </button>
              <button onClick={exportVisibleTranscript} type="button">
                <span>Export</span>
                <b>json</b>
              </button>
              <button onClick={requestDownloadableAssets} type="button">
                <span>Assets</span>
                <b>{downloadAssets.length}</b>
              </button>
              <button onClick={() => { setRightDrawer('settings'); setRightDrawerOpen(true); void requestScreenAutomation('status'); }} type="button">
                <span>Screen</span>
                <b>{screenOpsReady ? 'ready' : screenOpsStatus}</b>
              </button>
            </div>

            <footer className="ion-browser-gpt-native-composer">
              <input
                className="ion-browser-gpt-hidden-file"
                onChange={handleUploadFileChange}
                ref={uploadInputRef}
                type="file"
              />
              <div className="ion-browser-gpt-native-toolrow">
                {composerToolbar.map((surfaceId) => {
                  const control = controlBySurface.get(surfaceId);
                  const upload = surfaceId === 'file_attach_button';
                  return (
                    <CompactToolbarButton
                      icon={composerToolbarIcon(surfaceId)}
                      key={surfaceId}
                      label={toolLabel(surfaceId, control)}
                      onClick={() => {
                        if (upload) {
                          uploadInputRef.current?.click();
                          return;
                        }
                        setLeftDrawer('surfaces');
                        setLeftDrawerOpen(true);
                      }}
                      status={upload ? uploadStatus : text(control?.state, 'missing')}
                      title={`${toolLabel(surfaceId, control)} / ${upload ? uploadStatus : text(control?.state, 'missing')} / ${text(control?.selector, surfaceId)}`}
                      tone={toolbarStatusTone(upload ? uploadStatus : text(control?.state, 'missing'), Boolean(control?.present))}
                    />
                  );
                })}
                <label className="ion-browser-gpt-auto-count is-compact" title={`Auto proceed count / ${autoProceedCountInput}`}>
                  <ReceiptIcon />
                  <input
                    aria-label="Auto proceed count"
                    max={20}
                    min={0}
                    onChange={(event) => setAutoProceedCountInput(event.currentTarget.value)}
                    type="number"
                    value={autoProceedCountInput}
                  />
                </label>
                <CompactToolbarButton
                  disabled={sendBusy}
                  icon={<RunIcon />}
                  label="Proceed"
                  onClick={() => void sendProceedMessage('manual')}
                  status={sendBusy ? 'busy' : 'manual'}
                  title="Proceed / send proceed to the active ChatGPT tab"
                  tone={sendBusy ? 'watch' : 'ready'}
                />
                <CompactToolbarButton
                  icon={<WorkSurfaceIcon />}
                  label="Auto proceed"
                  onClick={autoProceedRemaining > 0 ? stopAutoProceed : armAutoProceed}
                  status={autoProceedRemaining > 0 ? `${autoProceedRemaining} left` : autoProceedStatus}
                  title={`Auto proceed / ${autoProceedRemaining > 0 ? `${autoProceedRemaining} left` : autoProceedStatus}`}
                  tone={autoProceedRemaining > 0 ? 'ready' : 'missing'}
                />
                <CompactToolbarButton
                  icon={<AuthorityIcon />}
                  label="Auto approve"
                  onClick={() => void setAutoAcceptActions(!autoAcceptActive)}
                  status={autoAcceptActive ? 'on' : 'off'}
                  title={`Auto approve / ${autoAcceptActive ? 'on' : 'off'}${autoAcceptUntil ? ` / ${autoAcceptUntil}` : ''}`}
                  tone={autoAcceptActive ? 'ready' : 'missing'}
                />
              </div>
              <div className="ion-browser-gpt-native-input">
                <textarea
                  aria-label="Browser GPT draft"
                  onChange={(event) => setDraft(event.currentTarget.value)}
                  onKeyDown={handleDraftKeyDown}
                  placeholder="Stage draft against mapped ChatGPT composer"
                  value={draft}
                />
                <div className="ion-browser-gpt-native-actions">
                  <button disabled={!draft.trim()} onClick={() => setDraft('')} type="button">CLEAR</button>
                  <button onClick={() => { setRightDrawer('authority'); setRightDrawerOpen(true); }} type="button">AUTH</button>
                  <button disabled={!draft.trim() || sendBusy} onClick={sendDraftToChatGpt} type="button" title="Send this draft to the active ChatGPT tab through the extension bridge">
                    {sendStatus === 'sending' ? 'SENDING' : 'SEND GPT'}
                  </button>
                </div>
              </div>
              <div className="ion-browser-gpt-native-send-status" aria-live="polite">{sendStatus}</div>
            </footer>
          </section>
        </main>

        <aside className="ion-codex-rail ion-codex-right-rail" aria-label="Browser GPT right drawers">
          <BrowserGptIconBar items={rightRailItems} active={rightDrawerOpen ? rightDrawer : undefined} onSelect={selectRightDrawer} />
        </aside>
        <aside className={`ion-codex-drawer-panel ion-codex-right-drawer${rightDrawerOpen ? ' is-open' : ''}`} aria-hidden={!rightDrawerOpen} aria-label="Browser GPT right drawer">
          <div className="ion-codex-drawer-head">
            <span>{drawerTitle(rightRailItems, rightDrawer)}</span>
            <button aria-label="Close right drawer" onClick={() => setRightDrawerOpen(false)} title="Close right drawer" type="button">
              <CloseIcon className="ion-close-icon" />
            </button>
          </div>
          <div className="ion-codex-drawer-body">{renderRightDrawer(rightDrawer)}</div>
        </aside>
      </div>
    </section>
  );

  function renderLeftDrawer(id: LeftDrawerId) {
    if (id === 'tabs') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <MetricTile label="open tabs" value={String(chatGptTabs.length)} />
          <MetricTile label="selected" value={text(selectedChatGptTab?.title, 'none')} />
          <MetricTile label="relay" value={relayStatus} />
          <div className="ion-browser-gpt-native-nav-actions">
            <button className="ion-browser-gpt-drawer-action" onClick={() => void requestCurrentChatGptTabs()} type="button">Read open tabs</button>
            <button className="ion-browser-gpt-drawer-action" onClick={() => requestVisibleConversation({ targetTabId: numericValue(selectedChatGptTab?.tab_id), targetUrl: text(selectedChatGptTab?.url, ''), bindTab: Boolean(selectedChatGptTab) })} type="button">Read selected</button>
            <button className="ion-browser-gpt-drawer-action" onClick={() => void relayVisibleConversation()} type="button">Relay selected</button>
          </div>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Current ChatGPT tabs</span>
              <b>{chatGptTabsStatus}</b>
            </div>
            {chatGptTabs.map((item, index) => (
              <CurrentChatGptTabRow
                item={item}
                key={`${text(item.tab_id, 'tab')}-${index}`}
                onFocus={focusChatGptTab}
                onOpen={openNativeChatGptUrl}
                onRead={readChatGptTabHistory}
                onRelay={relayVisibleConversation}
              />
            ))}
            {!chatGptTabs.length ? <SurfaceCard title="open ChatGPT tabs" state={chatGptTabsStatus} detail="The extension background will list every currently open chatgpt.com tab once the cockpit bridge is loaded." /> : null}
          </section>
        </div>
      );
    }
    if (id === 'merge') {
      return (
        <div className="ion-browser-gpt-drawer-stack ion-browser-gpt-merge-drawer">
          <div className="ion-browser-gpt-action-detail-topline">
            <MetricTile label="tabs" value={`${effectiveMergeTabs.length}/${chatGptTabs.length || 0}`} />
            <MetricTile label="codex" value={`${selectedCodexSessions.length}/${text(codexArchiveSourceCounts.session_files_total, '0')}`} />
            <MetricTile label="attach" value={`${selectedMergeArchiveAttachments.length}/${selectedCodexSessions.length || 0}`} />
            <MetricTile label="agents" value={`${mergeRunTargetRoles.length}/${agentControlAgents.length || 0}`} />
            <MetricTile label="room" value={selectedAgentChannelId} />
            <MetricTile label="status" value={mergeCommsStatus} />
            <MetricTile label="run" value={mergeReworkStatus} />
          </div>
          <section className="ion-browser-gpt-surface-block ion-browser-gpt-merge-control">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Visual merge room</span>
              <b>{mergeRoomName}</b>
            </div>
            <div className="ion-browser-gpt-merge-form-grid">
              <input aria-label="Merge room name" onChange={(event) => setMergeRoomName(event.currentTarget.value)} value={mergeRoomName} />
              <input aria-label="Merge tags" onChange={(event) => setMergeTagsInput(event.currentTarget.value)} value={mergeTagsInput} />
              <select aria-label="Merge comms thread" value={selectedAgentThreadId} onChange={(event) => setAgentCommsThreadId(event.currentTarget.value)}>
                <option value="">LATEST AGENT ROOM</option>
                {agentCommsThreads.slice(0, 50).map((thread) => (
                  <option key={text(thread.thread_id, '')} value={text(thread.thread_id, '')}>
                    {shortMiddle(`${text(thread.channel_id, 'team')} / ${text(thread.subject, 'thread')}`, 78)}
                  </option>
                ))}
              </select>
              <select aria-label="Merge comms target" value={mergeCommsTarget} onChange={(event) => setMergeCommsTarget(event.currentTarget.value)}>
                <option value="">@mentions in packet</option>
                <option value="operator">operator</option>
                {agentControlAgents.map((agent) => (
                  <option key={text(agent.role_id ?? agent.agent_id, '')} value={text(agent.role_id ?? agent.agent_id, '')}>
                    {text(agent.display_name ?? agent.role_id ?? agent.agent_id, 'agent')}
                  </option>
                ))}
              </select>
            </div>
            <textarea
              aria-label="Merge context"
              onChange={(event) => setMergeContext(event.currentTarget.value)}
              value={mergeContext}
            />
            <div className="ion-browser-gpt-native-nav-actions">
              <button className="ion-browser-gpt-drawer-action" onClick={stageMergeContextBlock} type="button">Stage context tag</button>
              <button className="ion-browser-gpt-drawer-action" disabled={sendBusy || !effectiveMergeTabs.length} onClick={() => void sendMergeContextToChatGpt()} type="button">Send to active GPT</button>
              <button className="ion-browser-gpt-drawer-action" disabled={mergeArchiveAttachBusy || !selectedCodexSessions.length} onClick={() => void attachSelectedCodexChats()} type="button">Attach Codex chats</button>
              <button className="ion-browser-gpt-drawer-action" disabled={agentCommsBusy} onClick={() => void sendMergeCommsRoomPacket()} type="button">Join room packet</button>
              <button className="ion-browser-gpt-drawer-action" disabled={agentCommsBusy || mergeArchiveAttachBusy || !mergeRunTargetRoles.length} onClick={() => void startMergeReworkRun()} type="button">Start rework run</button>
              <button className="ion-browser-gpt-drawer-action" onClick={() => { setRightDrawer('actions'); setRightDrawerOpen(true); }} type="button">Action sync</button>
              <button className="ion-browser-gpt-drawer-action" onClick={() => { setRightDrawer('workers'); setRightDrawerOpen(true); }} type="button">Workers</button>
              <button className="ion-browser-gpt-drawer-action" onClick={() => void requestCurrentChatGptTabs()} type="button">Read tabs</button>
            </div>
          </section>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Merged ChatGPT tabs</span>
              <b>{effectiveMergeTabs.length}</b>
            </div>
            {chatGptTabs.map((item, index) => (
              <MergeTabRow
                item={item}
                key={`${browserGptTabKey(item)}-${index}`}
                onFocus={focusChatGptTab}
                onRead={readChatGptTabHistory}
                onRelay={relayVisibleConversation}
                onToggle={toggleMergeTab}
                selected={mergeSelectedTabIds.includes(browserGptTabKey(item)) || (!mergeSelectedTabIds.length && browserGptTabKey(item) === browserGptTabKey(selectedChatGptTab ?? {}))}
              />
            ))}
            {!chatGptTabs.length ? <SurfaceCard title="tabs" state={chatGptTabsStatus} detail="No ChatGPT tabs are loaded into the merge selector yet." /> : null}
          </section>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Codex CLI chats</span>
              <b>{`${selectedCodexSessions.length}/${text(codexArchiveSourceCounts.session_files_returned, String(archiveSessions.length))}`}</b>
            </div>
            {archiveSessions.slice(0, 18).map((session, index) => (
              <MergeCodexSessionRow
                item={session}
                key={`${text(session.session_id, 'session')}-${index}`}
                attachment={mergeArchiveAttachments[text(session.session_id, '')]}
                onToggle={toggleMergeCodexSession}
                selected={mergeSelectedCodexSessionIds.includes(text(session.session_id, ''))}
              />
            ))}
            {!archiveSessions.length ? <SurfaceCard title="Codex archive" state={codexArchiveStatus} detail="No summarized Codex sessions are available to this Browser GPT route yet." /> : null}
          </section>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Codex agents</span>
              <b>{`${mergeRunTargetRoles.length}/${agentControlAgents.length || 0}`}</b>
            </div>
            {agentControlAgents.slice(0, 30).map((agent, index) => (
              <MergeAgentRow
                item={agent}
                key={`${mergeAgentRoleId(agent) || 'agent'}-${index}`}
                onToggle={toggleMergeAgent}
                selected={mergeSelectedAgentRoleIds.includes(mergeAgentRoleId(agent))}
              />
            ))}
            {!agentControlAgents.length ? <SurfaceCard title="Codex agents" state={text(agentControlPlane.verdict, 'deferred')} detail="No agent-control-plane roles are hydrated for this Browser GPT route yet." /> : null}
          </section>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Merge context packet</span>
              <b>{selectedAgentThreadId || 'room pending'}</b>
            </div>
            <pre className="ion-browser-gpt-merge-packet">{mergeContextBlock}</pre>
          </section>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Merged activity</span>
              <b>{timelineEvents.length + selectedAgentMessages.length}</b>
            </div>
            {timelineEvents.slice(-6).map((event, index) => (
              <SurfaceCard
                key={`merge-chat-${timelineEventType(event)}-${text(event.event_index ?? event.index, String(index))}-${index}`}
                title={`ChatGPT / ${timelineEventTitle(event)}`}
                state={timelineEventMeta(event, index)}
                detail={messageBody(event)}
              />
            ))}
            {selectedAgentMessages.slice(-6).map((message, index) => (
              <WorkerMessageCard key={`merge-agent-${text(message.message_id, 'message')}-${index}`} message={message} />
            ))}
          </section>
          {mergeCommsRequestState ? (
            <details className="ion-browser-gpt-action-sync-details">
              <summary>
                <span>Last merge packet result</span>
              <b>{text(mergeCommsRequestState.finding ?? mergeCommsRequestState.status, 'result')}</b>
              </summary>
              <pre>{stringifyPanelJson(mergeCommsRequestState)}</pre>
            </details>
          ) : null}
          {mergeArchiveAttachRequestState ? (
            <details className="ion-browser-gpt-action-sync-details">
              <summary>
                <span>Last Codex chat attachment</span>
                <b>{mergeArchiveAttachStatus}</b>
              </summary>
              <pre>{stringifyPanelJson(mergeArchiveAttachRequestState)}</pre>
            </details>
          ) : null}
          {mergeReworkRequestState ? (
            <details className="ion-browser-gpt-action-sync-details">
              <summary>
                <span>Last rework run result</span>
                <b>{text(mergeReworkRequestState.finding ?? mergeReworkRequestState.status, 'result')}</b>
              </summary>
              <pre>{stringifyPanelJson(mergeReworkRequestState)}</pre>
            </details>
          ) : null}
        </div>
      );
    }
    if (id === 'chat') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <MetricTile label="messages" value={String(liveMessages.length || transcript.message_count || messages.length)} />
          <MetricTile label="events" value={String(timelineEvents.length)} />
          <MetricTile label="status" value={String(timelineStatusEvents.length)} />
          <MetricTile label="active" value={activeTimelineEvents.length ? `${activeTimelineEvents.length} live` : 'quiet'} />
          <MetricTile label="list" value={text(transcript.message_list_selector, 'missing')} />
          <SurfaceCard title="relay" state={relayStatus} detail={text(relayResult?.receipt_path ?? relayResult?.latest_path, 'No local transcript relay receipt yet.')} />
          {timelineEvents.slice(-VISIBLE_CONVERSATION_LIMIT).map((event, index) => (
            <SurfaceCard
              key={`${timelineEventType(event)}-${text(event.event_index ?? event.index, String(index))}-${index}`}
              title={timelineEventTitle(event)}
              state={timelineEventMeta(event, index)}
              detail={messageBody(event)}
            />
          ))}
          {!timelineEvents.length ? <SurfaceCard title="transcript" state={transcriptSource} detail={`raw anchors ${text(transcript.raw_visible_message_count ?? transcript.message_count, '0')}`} /> : null}
        </div>
      );
    }
    if (id === 'actions') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <MetricTile label="pending" value={String(pendingApprovalRequests.length)} />
          <MetricTile label="native" value={String(nativeApprovalRequests.length)} />
          <MetricTile label="bridge" value={String(bridgeApprovalRequests.length)} />
          <MetricTile label="local" value={`${text(actionGatewaySummary.recent_action_receipt_count, '0')} receipts`} />
          <MetricTile label="auto approve" value={autoAcceptActive ? 'on' : 'off'} />
          <SurfaceCard title="approval lane" state={approvalStatus} detail={text(approvalResult?.gateway_status ?? approvalResult?.finding ?? approvalResult?.status, 'No approval scan has run yet.')} />
          <section className="ion-browser-gpt-surface-block ion-browser-gpt-automation-panel">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Action automation</span>
              <b>{autoAcceptStatus}</b>
            </div>
            <div className="ion-browser-gpt-automation-controls">
              <button className={autoAcceptActive ? 'is-ready' : undefined} onClick={() => void setAutoAcceptActions(!autoAcceptActive)} type="button">
                <span>Auto approve</span>
                <b>{autoAcceptActive ? 'on' : 'off'}</b>
              </button>
              <label>
                <span>TTL minutes</span>
                <input
                  max={60}
                  min={1}
                  onChange={(event) => setAutoAcceptTtlMinutes(event.currentTarget.value)}
                  type="number"
                  value={autoAcceptTtlMinutes}
                />
              </label>
              <button onClick={() => void readQueueState()} type="button">
                <span>Sync queue</span>
                <b>{autoAcceptUntil || `${Math.round(autoAcceptTtlSeconds / 60)}m`}</b>
              </button>
            </div>
            <div className="ion-browser-gpt-automation-controls">
              <button disabled={sendBusy} onClick={() => void sendProceedMessage('manual')} type="button">
                <span>Proceed</span>
                <b>manual</b>
              </button>
              <label>
                <span>Proceed count</span>
                <input
                  max={20}
                  min={0}
                  onChange={(event) => setAutoProceedCountInput(event.currentTarget.value)}
                  type="number"
                  value={autoProceedCountInput}
                />
              </label>
              <button className={autoProceedRemaining > 0 ? 'is-ready' : undefined} onClick={autoProceedRemaining > 0 ? stopAutoProceed : armAutoProceed} type="button">
                <span>{autoProceedRemaining > 0 ? 'Stop auto' : 'Auto proceed'}</span>
                <b>{autoProceedRemaining > 0 ? `${autoProceedRemaining} left` : autoProceedStatus}</b>
              </button>
            </div>
          </section>
          <ActionGatewaySyncPanel
            actionGatewaySync={actionGatewaySync}
            idempotencyEntries={idempotencyEntries}
            queuePackets={actionQueuePackets}
            recentActionPackets={recentActionPackets}
            recentActionReceipts={recentActionReceipts}
            recentServiceReceipts={recentServiceReceipts}
            recentTestReceipts={recentTestReceipts}
            runtime={actionGatewayRuntime}
          />
          <div className="ion-browser-gpt-native-nav-actions">
            <button className="ion-browser-gpt-drawer-action" onClick={() => void requestApprovalRequests(false)} type="button">Read actions</button>
            <button className="ion-browser-gpt-drawer-action" disabled={!pendingApprovalRequests.length} onClick={() => void resolveApprovalRequest(pendingApprovalRequests[0], 'approve')} type="button">Approve latest</button>
          </div>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Action requests</span>
              <b>{approvalRequests.length}</b>
            </div>
            {approvalRequests.map((item, index) => (
              <ApprovalRequestCard
                item={item}
                key={`${text(item.request_id, 'approval')}-${index}`}
                sync={actionGatewaySync}
                onApprove={(request) => void resolveApprovalRequest(request, 'approve')}
                onReject={(request) => void resolveApprovalRequest(request, 'reject')}
              />
            ))}
            {!approvalRequests.length ? <SurfaceCard title="actions" state={approvalStatus} detail="Read actions to mirror pending ChatGPT native confirmations and extension approval modals with full details." /> : null}
          </section>
        </div>
      );
    }
    if (id === 'native') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <SurfaceCard
            title="native ChatGPT state"
            state={text(nativeNavigation?.status, nativeNavigationStatus)}
            detail={text(nativeCurrent.url ?? browserGptDom.target_url ?? browserGptDom.origin, 'https://chatgpt.com/')}
          />
          <div className="ion-browser-gpt-native-nav-actions">
            <button className="ion-browser-gpt-drawer-action" onClick={() => void requestNativeNavigation({ openDrawer: true })} type="button">Read native list</button>
            <button className="ion-browser-gpt-drawer-action" onClick={() => void openNativeChatGptUrl('https://chatgpt.com/', { label: 'new chat' })} type="button">Start new chat</button>
            <button className="ion-browser-gpt-drawer-action" onClick={() => void openNativeChatGptUrl(nativeCurrent.url, { label: 'current page', focus: true })} type="button">Focus GPT tab</button>
          </div>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Saved chats</span>
              <b>{nativeChats.length}</b>
            </div>
            {nativeChats.map((item, index) => (
              <NativeNavRow item={item} key={`${text(item.url, 'chat')}-${index}`} onOpen={openNativeChatGptUrl} />
            ))}
            {!nativeChats.length ? <SurfaceCard title="native chats" state="empty" detail="Open the native drawer read to collect ChatGPT sidebar URLs." /> : null}
          </section>
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Custom GPTs</span>
              <b>{nativeCustomGpts.length}</b>
            </div>
            {nativeCustomGpts.map((item, index) => (
              <NativeNavRow item={item} key={`${text(item.url, 'gpt')}-${index}`} onOpen={openNativeChatGptUrl} />
            ))}
            {!nativeCustomGpts.length ? <SurfaceCard title="custom GPTs" state="empty" detail="Use ChatGPT native URLs as the discovery source; no credential or account data is read." /> : null}
          </section>
          {nativeDirectories.length ? (
            <section className="ion-browser-gpt-surface-block">
              <div className="ion-browser-gpt-surface-block-head">
                <span>GPT directory</span>
                <b>{nativeDirectories.length}</b>
              </div>
              {nativeDirectories.map((item, index) => (
                <NativeNavRow item={item} key={`${text(item.url, 'directory')}-${index}`} onOpen={openNativeChatGptUrl} />
              ))}
            </section>
          ) : null}
        </div>
      );
    }
    if (id === 'atlas') {
      return renderContextAtlasDrawer();
    }
    if (id === 'capture') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <SurfaceCard title="1 capture screen" state={text(latestProbe.status, text(probeIntake.status, 'unknown'))} detail={text(source.probe_snapshot ?? latestProbe.path, 'no current snapshot')} />
          <SurfaceCard title="2 pick surface" state="guided" detail="Hover/click/keyboard selection lives in the extension capture panel; cockpit receives the probe artifact." />
          <SurfaceCard title="3 replay profile" state={text(effectiveCoverage.status, 'unknown')} detail={text(browserGptDom.latest_profile_path, '')} />
          <button className="ion-browser-gpt-drawer-action" onClick={onRuntimeRefresh} type="button">Refresh projection</button>
        </div>
      );
    }
    if (id === 'profiles') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <PathLine label="profile" value={browserGptDom.latest_profile_path} />
          <PathLine label="health" value={browserGptDom.latest_health_path} />
          <PathLine label="receipt" value={browserGptDom.latest_receipt_path} />
          <PathLine label="probe" value={source.probe_snapshot ?? latestProbe.path} />
        </div>
      );
    }
    return (
      <div className="ion-browser-gpt-drawer-stack">
        {surfaceGroups.map((group) => (
          <section className="ion-browser-gpt-surface-block" key={group.id}>
            <div className="ion-browser-gpt-surface-block-head">
              <span>{group.label}</span>
              <b>{group.surfaceIds.filter((surfaceId) => controlBySurface.get(surfaceId)?.present).length}/{group.surfaceIds.length}</b>
            </div>
            {group.surfaceIds.map((surfaceId) => (
              <SurfaceRow control={controlBySurface.get(surfaceId)} key={surfaceId} surfaceId={surfaceId} />
            ))}
          </section>
        ))}
      </div>
    );
  }

  function toggleAtlasRef(ref: string) {
    if (!ref) return;
    setAtlasRefs((previous) => previous.includes(ref) ? previous.filter((item) => item !== ref) : [...previous, ref]);
  }

  function insertAtlasRefs() {
    const mentions = atlasRefs.map(contextMention).join(' ');
    if (!mentions) return;
    setDraft((previous) => appendText(previous, mentions));
  }

  function renderContextAtlasDrawer() {
    const branches = asRecords(runtime.context_package_graph?.branches);
    const trunkNodes: BrowserGptAtlasNode[] = [
      {
        id: 'trunk:chatgpt-native',
        kind: 'trunk',
        title: 'Native ChatGPT',
        detail: text(nativeCurrent.url ?? browserGptDom.target_url ?? browserGptDom.origin, 'https://chatgpt.com/'),
        meta: nativeNavigation ? `${nativeChats.length} chats / ${nativeCustomGpts.length} GPTs` : nativeNavigationStatus,
        ref: text(nativeCurrent.url ?? browserGptDom.target_url ?? browserGptDom.origin, 'https://chatgpt.com/'),
        tone: nativeNavigation ? 'ready' : 'watch',
        icon: <ChatIcon />,
        url: text(nativeCurrent.url ?? browserGptDom.target_url ?? browserGptDom.origin, ''),
      },
      {
        id: 'trunk:dom-twin',
        kind: 'trunk',
        title: 'DOM Twin',
        detail: `${text(twin.status, 'missing')} / coverage ${coverageCount}`,
        meta: text(browserGptDom.latest_profile_path ?? source.probe_snapshot, 'profile pending'),
        ref: text(browserGptDom.latest_profile_path ?? source.probe_snapshot, 'browser_extension'),
        tone: Number(blockingIssues) ? 'blocked' : 'ready',
        icon: <LensIcon />,
      },
      {
        id: 'trunk:extension',
        kind: 'trunk',
        title: 'Extension Bridge',
        detail: text(shell.status ?? browserGptDom.status, 'extension projection'),
        meta: text(shell.extension_root ?? 'browser_extension'),
        ref: text(shell.extension_root ?? 'browser_extension'),
        tone: text(browserGptDom.status, '').toLowerCase().includes('blocked') ? 'blocked' : 'ready',
        icon: <ToolsIcon />,
      },
      {
        id: 'trunk:codex-context',
        kind: 'trunk',
        title: 'Codex Context',
        detail: `${text(runtime.codex_capsule_chat?.capsule?.entry_count, 0)} capsule rows / ${text(runtime.top_bar.context_package_count ?? branches.length, 0)} packages`,
        meta: text(runtime.context_package_graph?.status ?? runtime.codex_capsule_chat?.verdict, 'context graph'),
        ref: 'ION/05_context/current/codex_solo',
        tone: numberValue(runtime.context_package_graph?.blocked_count) ? 'blocked' : 'ready',
        icon: <ArchiveIcon />,
      },
    ];
    const nativeNodes: BrowserGptAtlasNode[] = [
      ...nativeChats.map((item, index) => nativeAtlasNode(item, index, 'native')),
      ...nativeCustomGpts.map((item, index) => nativeAtlasNode(item, index, 'custom-gpt')),
    ];
    const branchNodes: BrowserGptAtlasNode[] = branches.map((branch, index) => {
      const branchPath = text(branch.path ?? branch.candidate_capsule_path ?? branch.accepted_capsule_path, `branch ${index + 1}`);
      const gaps = asStrings(branch.gaps);
      const blockers = asStrings(branch.blockers);
      return {
        id: `branch:${branchPath}`,
        kind: 'branch',
        title: branchPath,
        detail: text(branch.package_type ?? branch.maturity_level ?? branch.classification, 'context package'),
        meta: blockers.length ? `${blockers.length} blockers` : gaps.length ? `${gaps.length} gaps` : text(branch.promotion_readiness, 'ready'),
        ref: text(branch.candidate_capsule_path ?? branch.accepted_capsule_path ?? branchPath, branchPath),
        tone: blockers.length ? 'blocked' : gaps.length ? 'watch' : 'ready',
        icon: <ArchiveIcon />,
      };
    });
    const surfaceNodes: BrowserGptAtlasNode[] = [
      ...surfaceGroups.flatMap((group) => group.surfaceIds.map((surfaceId) => {
        const control = controlBySurface.get(surfaceId);
        return {
          id: `surface:${surfaceId}`,
          kind: 'surface' as const,
          title: controlLabel(control, surfaceId.replaceAll('_', ' ')),
          detail: text(control?.selector, surfaceId),
          meta: `${group.label} / ${text(control?.state, control?.present ? 'ready' : 'missing')}`,
          ref: `dom:${surfaceId}`,
          tone: control?.present ? 'ready' as const : 'watch' as const,
          icon: <WorkSurfaceIcon />,
        };
      })),
      ...archiveSessions.slice(0, 18).map((session) => ({
        id: `archive:${session.session_id}`,
        kind: 'native' as const,
        title: text(session.display_title ?? session.thread_name ?? session.session_id, 'Codex chat'),
        detail: text(session.cwd ?? session.project_label, 'local archive'),
        meta: text(session.model ?? session.history_latest_ts ?? session.updated_at, 'archive'),
        ref: `archive:${session.session_id}`,
        tone: 'muted' as const,
        icon: <ArchiveIcon />,
      })),
    ];
    const assistantNodes: BrowserGptAtlasNode[] = [
      ...assistantLanes.map((lane, index) => {
        const laneId = text(lane.lane_id, `assistant-lane-${index + 1}`);
        const status = text(lane.status, 'projected');
        const refs = asStrings(lane.local_refs);
        return {
          id: `assistant:${laneId}`,
          kind: 'assistant' as const,
          title: text(lane.title, laneId.replaceAll('_', ' ')),
          detail: text(lane.purpose, 'assistant capability lane'),
          meta: `${status} / ${text(lane.authority, 'candidate')}`,
          ref: refs[0] ?? `assistant:${laneId}`,
          tone: toolbarStatusTone(status, true) === 'missing' ? 'blocked' as const : toolbarStatusTone(status, true) === 'ready' ? 'ready' as const : 'watch' as const,
          icon: <WorkSurfaceIcon />,
        };
      }),
      ...assistantResearch.map((row, index) => ({
        id: `assistant-research:${text(row.source_id, String(index))}`,
        kind: 'assistant' as const,
        title: text(row.source_id, 'research').replaceAll('_', ' '),
        detail: text(row.finding, 'research finding'),
        meta: 'research',
        ref: text(row.source_url, `research:${index + 1}`),
        tone: 'muted' as const,
        icon: <EvidenceIcon />,
        url: text(row.source_url, '').startsWith('http') ? text(row.source_url, '') : undefined,
      })),
    ];
    const nodesByLens: Record<BrowserGptAtlasLens, BrowserGptAtlasNode[]> = {
      trunks: trunkNodes,
      native: nativeNodes,
      branches: branchNodes,
      surfaces: surfaceNodes,
      assistant: assistantNodes,
    };
    const nodes = nodesByLens[atlasLens];
    const query = atlasSearch.trim().toLowerCase();
    const visibleNodes = query ? nodes.filter((node) => [node.title, node.detail, node.meta, node.ref].join(' ').toLowerCase().includes(query)) : nodes;
    const focusedNode = visibleNodes.find((node) => node.id === focusedAtlasNodeId) ?? visibleNodes[0];
    const lenses: Array<{ id: BrowserGptAtlasLens; label: string; icon: ReactNode; count: number }> = [
      { id: 'trunks', label: 'trunks', icon: <LensIcon />, count: trunkNodes.length },
      { id: 'native', label: 'native', icon: <ChatIcon />, count: nativeNodes.length },
      { id: 'branches', label: 'branches', icon: <ArchiveIcon />, count: branchNodes.length },
      { id: 'surfaces', label: 'surfaces', icon: <WorkSurfaceIcon />, count: surfaceNodes.length },
      { id: 'assistant', label: 'assist', icon: <RunIcon />, count: assistantNodes.length },
    ];
    return (
      <div className="ion-codex-file-picker-drawer ion-codex-context-atlas-drawer ion-browser-gpt-context-atlas-drawer" aria-label="Browser GPT context atlas">
        <div className="ion-codex-context-atlas-map" aria-label="Browser GPT context atlas map">
          <button className={atlasLens === 'trunks' ? 'is-active' : undefined} onClick={() => setAtlasLens('trunks')} title="Core trunks" type="button">
            <span><LensIcon /></span>
            <b>{trunkNodes.length}</b>
            <em>trunks</em>
          </button>
          <button className={atlasLens === 'native' ? 'is-active' : undefined} onClick={() => setAtlasLens('native')} title="Native ChatGPT URLs" type="button">
            <span><ChatIcon /></span>
            <b>{nativeNodes.length}</b>
            <em>native</em>
          </button>
          <button className={atlasLens === 'branches' ? 'is-active' : undefined} onClick={() => setAtlasLens('branches')} title="Context branches" type="button">
            <span><ArchiveIcon /></span>
            <b>{branchNodes.length}</b>
            <em>branches</em>
          </button>
          <button className={atlasLens === 'assistant' ? 'is-active' : undefined} onClick={() => setAtlasLens('assistant')} title="Computer assistant capability map" type="button">
            <span><RunIcon /></span>
            <b>{assistantNodes.length}</b>
            <em>assist</em>
          </button>
          <button className={atlasRefs.length ? 'is-selected' : undefined} disabled={!atlasRefs.length} onClick={insertAtlasRefs} title="Insert selected atlas refs" type="button">
            <span><ComposeIcon /></span>
            <b>{atlasRefs.length}</b>
            <em>bundle</em>
          </button>
        </div>
        <div className="ion-codex-context-atlas-lenses" role="tablist" aria-label="Browser GPT atlas lenses">
          {lenses.map((lens) => (
            <button aria-selected={atlasLens === lens.id} className={atlasLens === lens.id ? 'is-active' : undefined} key={lens.id} onClick={() => setAtlasLens(lens.id)} role="tab" type="button">
              <span aria-hidden="true">{lens.icon}</span>
              <b>{lens.count}</b>
              <em>{lens.label}</em>
            </button>
          ))}
        </div>
        <div className="ion-codex-file-picker-search ion-codex-context-atlas-search">
          <input aria-label="Search Browser GPT context atlas" onChange={(event) => setAtlasSearch(event.currentTarget.value)} placeholder="@ native URL, GPT, branch, DOM surface, assistant lane" value={atlasSearch} />
          <b>{visibleNodes.length}/{nodes.length}</b>
          <b>{atlasRefs.length}</b>
        </div>
        <div className="ion-codex-context-atlas-branch-preview" aria-label="Focused Browser GPT atlas node">
          <span>{focusedNode?.icon}</span>
          <div>
            <b>{focusedNode?.title ?? 'No atlas node'}</b>
            <em>{focusedNode ? `${focusedNode.detail} / ${focusedNode.meta}` : 'Open native list or refresh projection'}</em>
          </div>
          <code>{focusedNode?.ref ?? 'empty'}</code>
        </div>
        <div className="ion-codex-file-picker-grid">
          <div className="ion-codex-file-tree is-atlas" aria-label="Browser GPT atlas refs">
            {!visibleNodes.length ? <div className="ion-codex-file-picker-empty">NO ATLAS REFS</div> : null}
            {visibleNodes.map((node) => {
              const selected = atlasRefs.includes(node.ref);
              return (
                <button
                  aria-checked={selected}
                  className={`ion-codex-context-atlas-node is-${node.kind} is-${node.tone}${selected ? ' is-selected' : ''}${focusedAtlasNodeId === node.id ? ' is-focused' : ''}`}
                  key={node.id}
                  onClick={() => toggleAtlasRef(node.ref)}
                  onDoubleClick={() => node.url ? void openNativeChatGptUrl(node.url, { label: node.title }) : undefined}
                  onMouseEnter={() => setFocusedAtlasNodeId(node.id)}
                  role="checkbox"
                  title={node.url ? `Double click to open ${node.url}` : node.ref}
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
          </div>
          <aside className="ion-codex-file-selected" aria-label="Selected Browser GPT atlas refs">
            <div className="ion-codex-file-selected-head">
              <span>bundle</span>
              <b>{atlasRefs.length}</b>
              <button disabled={!atlasRefs.length} onClick={insertAtlasRefs} type="button">@</button>
              <button disabled={!atlasRefs.length} onClick={() => setAtlasRefs([])} type="button">CLEAR</button>
            </div>
            <div className="ion-codex-file-selected-list">
              {atlasRefs.map((ref) => (
                <div className="ion-codex-file-selected-row" key={ref}>
                  <button onClick={() => setDraft((previous) => appendText(previous, contextMention(ref)))} title={`Insert ${contextMention(ref)}`} type="button">{contextMention(ref)}</button>
                  <span title={ref}>{ref}</span>
                  <button aria-label={`Remove ${ref}`} onClick={() => toggleAtlasRef(ref)} title={`Remove ${ref}`} type="button">
                    <CloseIcon className="ion-close-icon" />
                  </button>
                </div>
              ))}
              {!atlasRefs.length ? <div className="ion-codex-file-picker-empty">NO REFS</div> : null}
            </div>
          </aside>
        </div>
      </div>
    );
  }

  function renderActionDetailDrawer() {
    return (
      <div className="ion-browser-gpt-drawer-stack">
        <div className="ion-browser-gpt-action-detail-topline">
          <MetricTile label="pending" value={String(pendingApprovalRequests.length)} />
          <MetricTile label="native" value={String(nativeApprovalRequests.length)} />
          <MetricTile label="bridge" value={String(bridgeApprovalRequests.length)} />
          <MetricTile label="receipts" value={text(actionGatewaySummary.recent_action_receipt_count, '0')} />
        </div>
        <SurfaceCard
          title="ChatGPT action sync"
          state={approvalStatus}
          detail={text(approvalResult?.gateway_status ?? approvalResult?.finding ?? approvalResult?.status, 'Scan ChatGPT action panels to mirror full native request details and local Action Gateway artifacts.')}
        />
        <div className="ion-browser-gpt-native-nav-actions">
          <button className="ion-browser-gpt-drawer-action" onClick={() => void requestApprovalRequests(false)} type="button">Read action panels</button>
          <button className="ion-browser-gpt-drawer-action" disabled={!pendingApprovalRequests.length} onClick={() => void resolveApprovalRequest(pendingApprovalRequests[0], 'approve')} type="button">Approve latest</button>
          <button className="ion-browser-gpt-drawer-action" onClick={() => void readQueueState()} type="button">Sync local queue</button>
          <button className="ion-browser-gpt-drawer-action" onClick={() => void setAutoAcceptActions(!autoAcceptActive)} type="button">{autoAcceptActive ? 'Stop auto approve' : 'Auto approve'}</button>
        </div>
        <section className="ion-browser-gpt-surface-block">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Full native action requests</span>
            <b>{approvalRequests.length}</b>
          </div>
          {approvalRequests.map((item, index) => (
            <ApprovalRequestCard
              item={item}
              key={`${text(item.request_id, 'approval')}-${index}`}
              sync={actionGatewaySync}
              onApprove={(request) => void resolveApprovalRequest(request, 'approve')}
              onReject={(request) => void resolveApprovalRequest(request, 'reject')}
            />
          ))}
          {!approvalRequests.length ? <SurfaceCard title="no action cards loaded" state={approvalStatus} detail="Use Read action panels while a ChatGPT action request is visible. Expanded native details and local gateway matches are rendered here." /> : null}
        </section>
        <ActionGatewaySyncPanel
          actionGatewaySync={actionGatewaySync}
          idempotencyEntries={idempotencyEntries}
          queuePackets={actionQueuePackets}
          recentActionPackets={recentActionPackets}
          recentActionReceipts={recentActionReceipts}
          recentServiceReceipts={recentServiceReceipts}
          recentTestReceipts={recentTestReceipts}
          runtime={actionGatewayRuntime}
        />
      </div>
    );
  }

  function renderWorkersDrawer() {
    const visibleRuns = agentRunRows.slice(0, 8);
    const dispatcherState = text(agentDispatcher.dispatcher_state, 'idle');
    return (
      <div className="ion-browser-gpt-drawer-stack ion-browser-gpt-worker-drawer">
        <div className="ion-browser-gpt-action-detail-topline">
          <MetricTile label="agents" value={text(agentControlSummary.agent_count, String(agentControlAgents.length))} />
          <MetricTile label="runs" value={`${text(agentCommsRuns.active_run_count, '0')}/${text(agentCommsRuns.run_count, '0')}`} />
          <MetricTile label="workers" value={`${activeWorkerCount}/${text(agentCommsRuns.active_worker_count, '0')}`} />
          <MetricTile label="messages" value={String(agentCommsMessages.length)} />
        </div>
        <SurfaceCard
          title="Spawned worker relay"
          state={agentCommsStatus}
          detail={text(agentCommsRequestState?.finding ?? agentCommsRequestState?.status ?? agentDispatcherNextAction.next_action, 'Worker and comms projection is read from agent_control_plane; sends use existing /cockpit/agents/comms routes.')}
        />
        <section className="ion-browser-gpt-surface-block ion-browser-gpt-worker-command">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Worker command lane</span>
            <b>{dispatcherState}</b>
          </div>
          <div className="ion-browser-gpt-worker-command-grid">
            <StatusRow label="dispatcher" value={`${dispatcherState} / ${text(agentDispatcherSummary.actionable_run_count, '0')} actionable`} />
            <StatusRow label="next" value={text(agentDispatcherNextAction.next_action, 'observe')} />
            <StatusRow label="thread" value={selectedAgentThreadId || 'latest'} />
            <StatusRow label="channel" value={selectedAgentChannelId} />
          </div>
          <div className="ion-browser-gpt-native-nav-actions">
            <button className="ion-browser-gpt-drawer-action" onClick={() => onRuntimeRefresh?.()} type="button">Refresh workers</button>
            <button className="ion-browser-gpt-drawer-action" disabled={!text(activeAgentRun.run_id, '') || agentCommsBusy} onClick={() => void runAgentCommsAction('continue', activeAgentRun)} type="button">Continue active run</button>
            <button className="ion-browser-gpt-drawer-action" disabled={!browserGptCanStartRunWorker(activeAgentRun) || agentCommsBusy} onClick={() => void runAgentCommsAction('worker', activeAgentRun)} type="button">Start worker</button>
            <button className="ion-browser-gpt-drawer-action" disabled={!text(activeAgentRun.run_id, '') || agentCommsBusy} onClick={() => void runAgentCommsAction('audit', activeAgentRun)} type="button">Audit run</button>
          </div>
        </section>
        <section className="ion-browser-gpt-surface-block ion-browser-gpt-worker-composer">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Chat with worker / team</span>
            <b>{agentCommsBusy ? 'busy' : selectedAgentChannelId}</b>
          </div>
          <div className="ion-browser-gpt-worker-form-grid">
            <select aria-label="Worker comms thread" value={selectedAgentThreadId} onChange={(event) => setAgentCommsThreadId(event.currentTarget.value)}>
              <option value="">LATEST THREAD</option>
              {agentCommsThreads.slice(0, 40).map((thread) => (
                <option key={text(thread.thread_id, '')} value={text(thread.thread_id, '')}>
                  {shortMiddle(`${text(thread.channel_id, 'team')} / ${text(thread.subject, 'thread')}`, 72)}
                </option>
              ))}
            </select>
            <select aria-label="Worker comms target" value={agentCommsTarget} onChange={(event) => setAgentCommsTarget(event.currentTarget.value)}>
              <option value="">@mentions in message</option>
              <option value="operator">operator</option>
              {agentControlAgents.map((agent) => (
                <option key={text(agent.role_id ?? agent.agent_id, '')} value={text(agent.role_id ?? agent.agent_id, '')}>
                  {text(agent.display_name ?? agent.role_id ?? agent.agent_id, 'agent')}
                </option>
              ))}
            </select>
            <input aria-label="Worker comms subject" onChange={(event) => setAgentCommsSubject(event.currentTarget.value)} value={agentCommsSubject} />
          </div>
          <textarea
            aria-label="Worker comms message"
            onChange={(event) => setAgentCommsMessage(event.currentTarget.value)}
            placeholder="@ionologist inspect the current Browser GPT action/run state and report the next exact step"
            value={agentCommsMessage}
          />
          <button className="ion-browser-gpt-drawer-action" disabled={agentCommsBusy || !agentCommsMessage.trim()} onClick={() => void sendAgentCommsMessage()} type="button">
            {agentCommsBusy ? 'Sending' : 'Send worker message'}
          </button>
        </section>
        <section className="ion-browser-gpt-surface-block">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Spawned runs / workers</span>
            <b>{visibleRuns.length}</b>
          </div>
          <div className="ion-browser-gpt-worker-run-list">
            {visibleRuns.map((run, index) => (
              <WorkerRunCard
                key={`${text(run.run_id, 'run')}-${index}`}
                onAudit={(item) => void runAgentCommsAction('audit', item)}
                onContinue={(item) => void runAgentCommsAction('continue', item)}
                onStartWorker={(item) => void runAgentCommsAction('worker', item)}
                run={run}
                busy={agentCommsBusy}
              />
            ))}
            {!visibleRuns.length ? <SurfaceCard title="worker runs" state="empty" detail="No agent-comms run projection is currently available in the Browser GPT model." /> : null}
          </div>
        </section>
        <section className="ion-browser-gpt-surface-block">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Selected worker thread</span>
            <b>{selectedAgentMessages.length}</b>
          </div>
          {selectedAgentMessages.slice(-10).map((message, index) => (
            <WorkerMessageCard key={`${text(message.message_id, 'message')}-${index}`} message={message} />
          ))}
          {!selectedAgentMessages.length ? <SurfaceCard title="agent messages" state="empty" detail="Select a thread or refresh projection to load worker/team messages." /> : null}
        </section>
        {agentDispatcherQueue.length ? (
          <section className="ion-browser-gpt-surface-block">
            <div className="ion-browser-gpt-surface-block-head">
              <span>Dispatcher queue</span>
              <b>{agentDispatcherQueue.length}</b>
            </div>
            {agentDispatcherQueue.slice(0, 8).map((row, index) => (
              <SurfaceCard
                key={`${text(row.run_id, 'dispatcher')}-${index}`}
                title={text(row.next_action ?? row.state, 'dispatcher row')}
                state={text(row.state ?? row.status, 'queued')}
                detail={`${text(row.objective, '')} ${text(row.run_id, '')}`.trim()}
              />
            ))}
          </section>
        ) : null}
      </div>
    );
  }

  function renderLargeArtifactDrawer() {
    return (
      <div className="ion-browser-gpt-drawer-stack ion-browser-gpt-artifact-drawer">
        <div className="ion-browser-gpt-action-detail-topline">
          <MetricTile label="status" value={largeArtifactStatus} />
          <MetricTile label="profile" value={text(largeArtifactProfile.size_bytes, 'not read')} />
          <MetricTile label="chunks" value={text(largeArtifactManifest.chunk_count ?? largeArtifactStream.chunk_count, '0')} />
          <MetricTile label="cursor" value={artifactCursor ? 'ready' : 'none'} />
          <MetricTile label="package" value={artifactPackageId || text(artifactPreview.package_id, 'none')} />
          <MetricTile label="model" value={text(inferenceStatus.network_used, 'preview')} />
        </div>

        <section className="ion-browser-gpt-surface-block ion-browser-gpt-artifact-control">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Large artifact intelligence</span>
            <b>{text(largeArtifactProfile.content_returned, 'bounded')}</b>
          </div>
          <div className="ion-browser-gpt-artifact-form-grid">
            <label>
              <span>path</span>
              <input aria-label="Large artifact path" onChange={(event) => setLargeArtifactPath(event.currentTarget.value)} value={largeArtifactPath} />
            </label>
            <label>
              <span>query</span>
              <input aria-label="Large artifact query" onChange={(event) => setLargeArtifactQuery(event.currentTarget.value)} value={largeArtifactQuery} />
            </label>
            <label>
              <span>start</span>
              <input aria-label="Large artifact slice start line" onChange={(event) => setLargeArtifactSliceStart(event.currentTarget.value)} value={largeArtifactSliceStart} />
            </label>
            <label>
              <span>lines</span>
              <input aria-label="Large artifact slice line count" onChange={(event) => setLargeArtifactSliceLines(event.currentTarget.value)} value={largeArtifactSliceLines} />
            </label>
            <label>
              <span>heading</span>
              <input aria-label="Large artifact markdown heading" onChange={(event) => setLargeArtifactHeading(event.currentTarget.value)} value={largeArtifactHeading} />
            </label>
            <label>
              <span>json path</span>
              <input aria-label="Large artifact JSON path" onChange={(event) => setLargeArtifactJsonPath(event.currentTarget.value)} value={largeArtifactJsonPath} />
            </label>
          </div>
          <div className="ion-browser-gpt-artifact-actions">
            <button onClick={() => void profileLargeArtifact()} type="button">Profile</button>
            <button onClick={() => void manifestLargeArtifact()} type="button">Chunks</button>
            <button onClick={() => void searchLargeArtifact()} type="button">Search</button>
            <button onClick={() => void readLargeArtifactSlice()} type="button">Slice</button>
            <button onClick={() => void startLargeArtifactStream()} type="button">Stream</button>
            <button disabled={!artifactCursor} onClick={() => void nextLargeArtifactChunk()} type="button">Next</button>
            <button disabled={!text(largeArtifactStream.artifact_id, '')} onClick={() => void rangeLargeArtifactChunks()} type="button">Range</button>
            <button onClick={() => void readLargeArtifactJsonPath()} type="button">JSON</button>
            <button onClick={() => void readLargeArtifactSection()} type="button">Section</button>
            <button onClick={() => void checkLargeArtifactClaim()} type="button">Claim</button>
          </div>
        </section>

        <section className="ion-browser-gpt-surface-block ion-browser-gpt-artifact-control">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Artifact transfer package</span>
            <b>{text(artifactZip.upload_performed ?? artifactPreview.would_create_zip, 'preview')}</b>
          </div>
          <div className="ion-browser-gpt-artifact-form-grid">
            <label>
              <span>label</span>
              <input aria-label="Artifact package label" onChange={(event) => setArtifactPackageLabel(event.currentTarget.value)} value={artifactPackageLabel} />
            </label>
            <label>
              <span>max bytes</span>
              <input aria-label="Artifact package max bytes" onChange={(event) => setArtifactMaxBytes(event.currentTarget.value)} value={artifactMaxBytes} />
            </label>
          </div>
          <div className="ion-browser-gpt-artifact-actions">
            <button onClick={() => void previewArtifactZip()} type="button">Preview zip</button>
            <button onClick={() => void materializeArtifactZip()} type="button">Materialize</button>
            <button disabled={!artifactPackageId} onClick={() => void readArtifactManifest()} type="button">Manifest</button>
            <button disabled={!artifactPackageId} onClick={() => void readSandboxInstruction()} type="button">Upload note</button>
          </div>
          <div className="ion-browser-gpt-worker-command-grid">
            <StatusRow label="upload automation" value="not performed" />
            <StatusRow label="confirmation" value="bounded write token only" />
            <StatusRow label="package path" value={shortMiddle(text(artifactZip.zip_path, 'none'), 74)} />
            <StatusRow label="manifest path" value={shortMiddle(text(artifactZip.manifest_path, 'none'), 74)} />
          </div>
        </section>

        <section className="ion-browser-gpt-surface-block ion-browser-gpt-artifact-control">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Low-cost inference preview</span>
            <b>{text(inferenceStatus.network_used, 'no call')}</b>
          </div>
          <textarea
            aria-label="Large artifact inference question"
            onChange={(event) => setInferenceQuestion(event.currentTarget.value)}
            value={inferenceQuestion}
          />
          <div className="ion-browser-gpt-artifact-actions">
            <button onClick={() => void runInferenceStatus()} type="button">Providers</button>
            <button onClick={() => void runInferencePlan()} type="button">Plan</button>
            <button onClick={() => void runInferenceIndex()} type="button">Index</button>
            <button onClick={() => void runInferenceQuestion()} type="button">Question</button>
          </div>
          <div className="ion-browser-gpt-worker-command-grid">
            <StatusRow label="model call" value={text(latestArtifactResult.would_call_model, 'false')} />
            <StatusRow label="full text send" value={text(latestArtifactResult.would_send_full_text, 'false')} />
            <StatusRow label="accepted state" value={text(latestArtifactResult.accepted_state_claim, 'false')} />
            <StatusRow label="secrets exposed" value={text(latestArtifactResult.secrets_exposed, 'false')} />
          </div>
        </section>

        <section className="ion-browser-gpt-surface-block">
          <div className="ion-browser-gpt-surface-block-head">
            <span>Branch route results</span>
            <b>{Object.keys(largeArtifactResults).length}</b>
          </div>
          <div className="ion-browser-gpt-artifact-result-list">
            <BranchResultDetails title="profile" result={largeArtifactResults.profile} />
            <BranchResultDetails title="search" result={largeArtifactResults.search} />
            <BranchResultDetails title="slice" result={largeArtifactResults.slice} />
            <BranchResultDetails title="stream start" result={largeArtifactResults.stream_start} />
            <BranchResultDetails title="stream next" result={largeArtifactResults.stream_next} />
            <BranchResultDetails title="stream range" result={largeArtifactResults.stream_range} />
            <BranchResultDetails title="json path" result={largeArtifactResults.json_path} />
            <BranchResultDetails title="section" result={largeArtifactResults.section} />
            <BranchResultDetails title="claim" result={largeArtifactResults.claim} />
            <BranchResultDetails title="zip preview" result={largeArtifactResults.zip_preview} />
            <BranchResultDetails title="zip materialized" result={largeArtifactResults.zip_materialize} />
            <BranchResultDetails title="zip manifest" result={largeArtifactResults.zip_manifest} />
            <BranchResultDetails title="sandbox instruction" result={largeArtifactResults.sandbox_instruction} />
            <BranchResultDetails title="inference status" result={largeArtifactResults.inference_status} />
            <BranchResultDetails title="inference plan" result={largeArtifactResults.inference_plan} />
            <BranchResultDetails title="inference index" result={largeArtifactResults.inference_index} />
            <BranchResultDetails title="inference question" result={largeArtifactResults.inference_question} />
          </div>
        </section>
      </div>
    );
  }

  function renderRightDrawer(id: RightDrawerId) {
    if (id === 'actions') {
      return renderActionDetailDrawer();
    }
    if (id === 'workers') {
      return renderWorkersDrawer();
    }
    if (id === 'artifacts') {
      return renderLargeArtifactDrawer();
    }
    if (id === 'probe') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <MetricTile label="intake" value={text(probeIntake.status, 'unknown')} />
          <MetricTile label="usable" value={text(latestProbe.status, 'unknown')} />
          <PathLine label="snapshot" value={source.probe_snapshot ?? latestProbe.path} />
          <PathLine label="profile" value={browserGptDom.latest_profile_path} />
          <PathLine label="receipt" value={browserGptDom.latest_receipt_path} />
          <button className="ion-browser-gpt-drawer-action" onClick={onRuntimeRefresh} type="button">Refresh projection</button>
        </div>
      );
    }
    if (id === 'authority') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          {Object.entries(authority).map(([key, value]) => (
            <StatusRow key={key} label={key} value={text(value, '')} />
          ))}
          <StatusRow label="live send" value={sendIsGated ? 'approval gated' : 'unsafe'} />
        </div>
      );
    }
    if (id === 'settings') {
      return (
        <div className="ion-browser-gpt-drawer-stack">
          <SurfaceCard title="draft bridge" state={text(state.composer_editable, 'false') === 'true' ? 'available' : 'blocked'} detail={text(composer.selector, '')} />
          <SurfaceCard title="send bridge" state={sendIsGated ? 'approval gated' : 'unsafe'} detail={text(send.selector, '')} />
          <SurfaceCard title="operator action" state={text(twin.operator_action_required, 'false')} detail={text(issueResolution.next_action, 'none')} />
          <SurfaceCard title="downloadable assets" state={String(downloadAssets.length)} detail={downloadAssets.map((asset) => text(asset.filename, 'asset')).join(', ') || 'No asset scan run yet.'} />
          <SurfaceCard title="screen automation" state={screenOpsReady ? 'ready' : screenOpsStatus} detail={screenOpsPointSummary || text(screenOpsResult?.receipt_path, 'not checked')} />
          <button className="ion-browser-gpt-drawer-action" onClick={() => void requestScreenAutomation('status')} type="button">Screen status</button>
          <button className="ion-browser-gpt-drawer-action" onClick={() => void requestScreenAutomation('learn', { probe_tabs: true })} type="button">Learn screen state</button>
          <button className="ion-browser-gpt-drawer-action" onClick={() => void requestScreenAutomation('reload-extension', { execute: true })} type="button">Reload extension</button>
          <button className="ion-browser-gpt-drawer-action" onClick={() => void requestScreenAutomation('refresh-tabs', { execute: true, roles: ['chatgpt', 'cockpit'] })} type="button">Refresh GPT + cockpit</button>
        </div>
      );
    }
    return (
      <div className="ion-browser-gpt-drawer-stack">
        <StatusRow label="Twin" value={text(twin.status, 'missing')} />
        <StatusRow label="Coverage" value={coverageCount} />
        <StatusRow label="Blocking" value={blockingIssues} />
        <StatusRow label="Composer" value={text(state.composer_present, 'false')} />
        <StatusRow label="Send" value={text(state.send_available, 'false')} />
        <StatusRow label="Streaming" value={text(state.response_streaming, 'false')} />
        <StatusRow label="Timeline" value={`${timelineEvents.length} events / ${timelineStatusEvents.length} status`} />
        <StatusRow label="Active" value={activeTimelineEvents.length ? `${activeTimelineEvents.length} live` : 'quiet'} />
        <StatusRow label="Browser agent" value={text(codexBrowserAgent.status, 'missing')} />
        <StatusRow label="Agent surfaces" value={`${text(codexBrowserAgent.ready_surface_count ?? codexBrowserAgentSummary.ready_surface_count, '0')}/${text(codexBrowserAgent.surface_count ?? codexBrowserAgentSummary.surface_count, '0')}`} />
        <StatusRow label="Agent gaps" value={text(codexBrowserAgent.critical_gap_count ?? codexBrowserAgentSummary.critical_gap_count, '0')} />
        <StatusRow label="Assistant map" value={`${assistantReadyLaneCount}/${assistantLaneCount} lanes`} />
        <StatusRow label="Assistant gaps" value={text(computerAssistant.critical_gap_count, '0')} />
        <SurfaceCard
          title="Codex Browser Agent"
          state={text(codexBrowserAgent.finding ?? codexBrowserAgent.mode, 'not run')}
          detail={text(codexBrowserAgentArtifacts.latest_capsule ?? codexBrowserAgentArtifacts.latest_report, 'Run python3 -S -m kernel.ion_codex_browser_agent --ion-root . --plan --json')}
        />
        <SurfaceCard
          title="Computer Assistant Map"
          state={text(computerAssistant.status, 'missing')}
          detail={assistantLanes.map((lane) => text(lane.lane_id ?? lane.title, '')).filter(Boolean).join(' / ') || 'No assistant capability map projected yet.'}
        />
      </div>
    );
  }
}

function BrowserGptIconBar<T extends string>({
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
          className={active === item.id ? 'is-active' : undefined}
          key={item.id}
          onClick={() => onSelect(item.id)}
          title={item.title}
          type="button"
        >
          <span className="ion-nav-icon" aria-hidden="true">{item.icon}</span>
        </button>
      ))}
    </div>
  );
}

function MetricTile({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-browser-gpt-metric">
      <span>{label}</span>
      <b>{text(value, '')}</b>
    </div>
  );
}

function CompactStatusChip({ icon, label, value, tone }: { icon: ReactNode; label: string; value: unknown; tone: ToolbarTone }) {
  const valueText = text(value, '');
  return (
    <div aria-label={`${label}: ${valueText}`} className={`ion-browser-gpt-compact-chip is-${tone}`} title={`${label} / ${valueText}`}>
      <span className="ion-browser-gpt-toolbar-icon" aria-hidden="true">{icon}</span>
      <b>{valueText}</b>
      <ToolbarStatusMark tone={tone} />
    </div>
  );
}

function CompactToolbarButton({
  disabled = false,
  icon,
  label,
  onClick,
  status,
  title,
  tone,
}: {
  disabled?: boolean;
  icon: ReactNode;
  label: string;
  onClick: () => void;
  status: unknown;
  title?: string;
  tone: ToolbarTone;
}) {
  const statusText = text(status, '');
  const resolvedTitle = title ?? `${label} / ${statusText}`;
  return (
    <button
      aria-label={resolvedTitle}
      className={`ion-browser-gpt-compact-tool is-${tone}`}
      disabled={disabled}
      onClick={onClick}
      title={resolvedTitle}
      type="button"
    >
      <span className="ion-browser-gpt-toolbar-icon" aria-hidden="true">{icon}</span>
      <ToolbarStatusMark tone={tone} />
    </button>
  );
}

function ToolbarStatusMark({ tone }: { tone: ToolbarTone }) {
  if (tone === 'ready') {
    return <span className="ion-browser-gpt-toolbar-status is-ready" aria-hidden="true"><CheckIcon /></span>;
  }
  if (tone === 'missing') {
    return <span className="ion-browser-gpt-toolbar-status is-missing" aria-hidden="true"><CloseIcon /></span>;
  }
  return <span className="ion-browser-gpt-toolbar-status is-watch" aria-hidden="true" />;
}

function SurfaceCard({ title, state, detail }: { title: string; state: string; detail: string }) {
  return (
    <article className="ion-browser-gpt-surface-card">
      <div>
        <span>{title}</span>
        <b>{state}</b>
      </div>
      <p>{detail}</p>
    </article>
  );
}

function ActionGatewaySyncPanel({
  actionGatewaySync,
  runtime,
  recentActionReceipts,
  recentActionPackets,
  queuePackets,
  idempotencyEntries,
  recentServiceReceipts,
  recentTestReceipts,
}: {
  actionGatewaySync: Record<string, unknown>;
  runtime: Record<string, unknown>;
  recentActionReceipts: Array<Record<string, unknown>>;
  recentActionPackets: Array<Record<string, unknown>>;
  queuePackets: Array<Record<string, unknown>>;
  idempotencyEntries: Array<Record<string, unknown>>;
  recentServiceReceipts: Array<Record<string, unknown>>;
  recentTestReceipts: Array<Record<string, unknown>>;
}) {
  const summary = (actionGatewaySync.summary ?? {}) as Record<string, unknown>;
  const logTail = asStrings(runtime.log_tail);
  return (
    <section className="ion-browser-gpt-surface-block ion-browser-gpt-action-sync-panel">
      <div className="ion-browser-gpt-surface-block-head">
        <span>Local Action Gateway sync</span>
        <b>{text(actionGatewaySync.status, 'not loaded')}</b>
      </div>
      <div className="ion-browser-gpt-action-sync-metrics">
        <MetricTile label="pid" value={text(summary.pid_running, 'false') === 'true' ? `${text(summary.pid, '')} running` : text(summary.pid, 'missing')} />
        <MetricTile label="receipts" value={text(summary.recent_action_receipt_count, '0')} />
        <MetricTile label="packets" value={text(summary.recent_action_packet_count, '0')} />
        <MetricTile label="queue" value={text(summary.queued_packet_count, '0')} />
        <MetricTile label="ledger" value={text(summary.idempotency_entry_count, '0')} />
        <MetricTile label="runs" value={text(summary.recent_test_receipt_count, '0')} />
      </div>
      <div className="ion-browser-gpt-action-sync-columns">
        <ActionSyncRecordList title="recent receipts" rows={recentActionReceipts.slice(0, 5)} />
        <ActionSyncRecordList title="action packets" rows={recentActionPackets.slice(0, 4)} />
        <ActionSyncRecordList title="queue" rows={queuePackets.slice(0, 4)} />
        <ActionSyncRecordList title="ledger" rows={idempotencyEntries.slice(0, 4)} />
        <ActionSyncRecordList title="service/process" rows={recentServiceReceipts.slice(0, 3)} />
        <ActionSyncRecordList title="focused runs" rows={recentTestReceipts.slice(0, 3)} />
      </div>
      {logTail.length ? (
        <details className="ion-browser-gpt-action-sync-details">
          <summary>Action Gateway log tail</summary>
          <pre>{logTail.join('\n')}</pre>
        </details>
      ) : null}
    </section>
  );
}

function ActionSyncRecordList({ title, rows }: { title: string; rows: Array<Record<string, unknown>> }) {
  return (
    <div className="ion-browser-gpt-action-sync-list">
      <div className="ion-browser-gpt-action-sync-list-head">
        <span>{title}</span>
        <b>{rows.length}</b>
      </div>
      {rows.length ? rows.map((row, index) => (
        <ActionSyncRecord key={`${title}-${text(row.path ?? row.idempotency_key ?? row.packet_id, String(index))}`} row={row} />
      )) : <p>none</p>}
    </div>
  );
}

function ActionSyncRecord({ row }: { row: Record<string, unknown> }) {
  const payload = (row.payload && typeof row.payload === 'object') ? row.payload : row;
  return (
    <details className="ion-browser-gpt-action-sync-details">
      <summary>
        <span>{actionSyncRecordTitle(row)}</span>
        <b>{text(row.status ?? row.state ?? row.operation ?? row.intent ?? row.suite_id, 'record')}</b>
      </summary>
      <pre>{stringifyPanelJson(payload)}</pre>
    </details>
  );
}

function BranchResultDetails({ title, result }: { title: string; result?: Record<string, unknown> }) {
  if (!result || !Object.keys(result).length) return null;
  const delegated = delegatedBranchResult(result);
  const flags = [
    `ok=${text(result.ok ?? delegated.ok, 'unknown')}`,
    `mutates=${text(result.mutates_active_state ?? delegated.mutates_active_state, 'false')}`,
    `production=${text(delegated.production_authority ?? result.production_authority, 'false')}`,
    `live=${text(delegated.live_execution_authority ?? result.live_execution_authority, 'false')}`,
  ];
  return (
    <details className="ion-browser-gpt-action-sync-details ion-browser-gpt-branch-result">
      <summary>
        <span>{title}</span>
        <b>{text(result.finding ?? delegated.finding ?? delegated.status ?? result.status, 'result')}</b>
      </summary>
      <div className="ion-browser-gpt-branch-result-flags">
        {flags.map((flag) => <code key={flag}>{flag}</code>)}
      </div>
      <pre>{stringifyPanelJson(result)}</pre>
    </details>
  );
}

function ApprovalRequestCard({
  item,
  sync,
  onApprove,
  onReject,
}: {
  item: Record<string, unknown>;
  sync: Record<string, unknown>;
  onApprove: (item: Record<string, unknown>) => void;
  onReject: (item: Record<string, unknown>) => void;
}) {
  const kind = text(item.approval_kind ?? item.kind, 'approval');
  const isNative = kind.includes('native_action');
  const status = text(item.status ?? item.state, 'pending');
  const detail = approvalDetailText(item);
  const detailRows = approvalDetailRows(item);
  const localMatches = localActionSyncMatches(item, sync);
  const summary = text(item.detail_summary ?? item.action_summary ?? asRecord(item.details).action_summary ?? item.gateway_status ?? item.confirm_button_text, kind);
  return (
    <article className={`ion-browser-gpt-approval-card is-${timelineEventClass(kind)} is-${timelineEventClass(status)}`}>
      <div className="ion-browser-gpt-approval-card-head">
        <span>{approvalTitle(item)}</span>
        <b>{status}</b>
      </div>
      <div className="ion-browser-gpt-approval-meta">
        <code>{text(item.request_id, 'no request id')}</code>
        <em>{summary}</em>
      </div>
      <div className="ion-browser-gpt-approval-section-label">Page/native approval detail</div>
      {detailRows.length ? (
        <div className="ion-browser-gpt-approval-detail-grid">
          {detailRows.map((row, index) => {
            const label = text(row.label, `detail ${index + 1}`);
            const rowKind = text(row.kind, 'detail');
            const value = text(row.value, '');
            const selector = text(row.selector, '');
            return (
              <div className="ion-browser-gpt-approval-detail-row" key={`${rowKind}-${label}-${index}`}>
                <span>{label}</span>
                <b>{rowKind}</b>
                <code title={selector || value}>{value}</code>
              </div>
            );
          })}
        </div>
      ) : null}
      <details className="ion-browser-gpt-approval-json-details" open={!detailRows.length}>
        <summary>
          <span>Raw approval payload</span>
          <b>{detailRows.length ? `${detailRows.length} rows` : 'open'}</b>
        </summary>
        <pre>{detail}</pre>
      </details>
      {localMatches.length ? (
        <div className="ion-browser-gpt-approval-local-sync">
          <div className="ion-browser-gpt-approval-section-label">Matched local Action Gateway data</div>
          {localMatches.map((match, index) => (
            <details className="ion-browser-gpt-action-sync-details" key={`${match.kind}-${index}-${text(match.record.path ?? match.record.idempotency_key, '')}`}>
              <summary>
                <span>{match.title}</span>
                <b>{`${match.kind} / ${match.score}`}</b>
              </summary>
              <pre>{stringifyPanelJson(match.record.payload ?? match.record)}</pre>
            </details>
          ))}
        </div>
      ) : null}
      <div className="ion-browser-gpt-approval-actions">
        <button onClick={() => onApprove(item)} type="button">Approve</button>
        <button disabled={isNative} onClick={() => onReject(item)} type="button">Reject</button>
      </div>
    </article>
  );
}

function WorkerRunCard({
  busy,
  onAudit,
  onContinue,
  onStartWorker,
  run,
}: {
  busy: boolean;
  onAudit: (run: Record<string, unknown>) => void;
  onContinue: (run: Record<string, unknown>) => void;
  onStartWorker: (run: Record<string, unknown>) => void;
  run: Record<string, unknown>;
}) {
  const runtime = asRecord(run.worker_runtime);
  const workers = asRecords(runtime.workers);
  const activeWorkers = asRecords(runtime.active_workers);
  const latestWorker = asRecord(runtime.latest_worker ?? run.latest_worker);
  const workItems = asRecords(run.work_items);
  const workpackPath = browserGptRunWorkpackPath(run);
  const latestReturnPath = browserGptRunLatestReturnPath(run);
  const runId = text(run.run_id, '');
  return (
    <article className={`ion-browser-gpt-worker-run-card is-${timelineEventClass(text(run.operational_state, 'unknown'))}${activeWorkers.length ? ' is-worker-running' : ''}`}>
      <header>
        <div>
          <b>{text(run.objective, 'agent run')}</b>
          <span>{text(run.status, 'idle')} / {browserGptRunOperationalText(run)} / {browserGptRunWorkerText(run)}</span>
        </div>
        <code>{shortMiddle(runId || text(run.created_at, 'run'), 46)}</code>
      </header>
      <div className="ion-browser-gpt-worker-proof">
        <StatusRow label="worker" value={browserGptRunWorkerText(run)} />
        <StatusRow label="workpack" value={shortMiddle(workpackPath || 'missing', 58)} />
        <StatusRow label="return" value={shortMiddle(latestReturnPath || 'waiting', 58)} />
        <StatusRow label="policy" value={text(asRecord(run.policy_gate).state, 'policy unknown').replaceAll('_', ' ')} />
      </div>
      <div className="ion-browser-gpt-worker-actions">
        <button disabled={busy || !runId} onClick={() => onContinue(run)} type="button">CONTINUE</button>
        <button disabled={busy || !browserGptCanStartRunWorker(run)} onClick={() => onStartWorker(run)} type="button">WORKER</button>
        <button disabled={busy || !runId} onClick={() => onAudit(run)} type="button">AUDIT</button>
      </div>
      <details className="ion-browser-gpt-action-sync-details">
        <summary>
          <span>{`${workers.length} workers / ${workItems.length} work items`}</span>
          <b>{text(latestWorker.status, 'no worker')}</b>
        </summary>
        <pre>{stringifyPanelJson({
          run_id: runId,
          operational_state: run.operational_state,
          completion_state: run.completion_state,
          worker_runtime: runtime,
          work_items: workItems,
          graph: run.graph,
          latest_agent_message: run.latest_agent_message,
        })}</pre>
      </details>
    </article>
  );
}

function WorkerMessageCard({ message }: { message: Record<string, unknown> }) {
  const panel = asRecord(message.work_panel);
  const body = text(message.body ?? panel.summary, '');
  return (
    <article className={`ion-browser-gpt-worker-message is-${timelineEventClass(text(message.message_kind, 'message'))}`}>
      <header>
        <div>
          <b>{text(message.from_role ?? panel.from_role, 'agent')}</b>
          <span>{text(message.message_kind ?? panel.message_kind, 'message')} / {text(message.subject ?? panel.subject, 'worker thread')}</span>
        </div>
        <code>{shortMiddle(text(message.message_id ?? panel.message_id, ''), 42)}</code>
      </header>
      <p>{body.length > 900 ? `${body.slice(0, 900)}...` : body}</p>
      <details className="ion-browser-gpt-action-sync-details">
        <summary>
          <span>message payload</span>
          <b>{text(message.created_at ?? panel.created_at, 'time')}</b>
        </summary>
        <pre>{stringifyPanelJson(message)}</pre>
      </details>
    </article>
  );
}

function SurfaceRow({ control, surfaceId }: { control?: Record<string, unknown>; surfaceId: string }) {
  return (
    <div className={`ion-browser-gpt-surface-row ${control?.present ? 'is-ready' : 'is-missing'}`}>
      <span>{controlLabel(control, surfaceId.replaceAll('_', ' '))}</span>
      <b>{text(control?.state, 'missing')}</b>
      <code>{text(control?.selector, '')}</code>
    </div>
  );
}

function NativeNavRow({
  item,
  onOpen,
}: {
  item: Record<string, unknown>;
  onOpen: (url: unknown, options?: { label?: string; focus?: boolean }) => void;
}) {
  const title = text(item.title, text(item.id, 'ChatGPT page'));
  const url = text(item.url, '');
  const selected = text(item.selected, 'false') === 'true';
  return (
    <article className={`ion-browser-gpt-native-nav-row${selected ? ' is-selected' : ''}`}>
      <div className="ion-browser-gpt-native-nav-main">
        <span>{title}</span>
        <b>{text(item.kind, 'link')}</b>
      </div>
      <code>{url}</code>
      <div className="ion-browser-gpt-native-nav-buttons">
        <button onClick={() => onOpen(url, { label: title })} type="button">LOAD</button>
        <button onClick={() => onOpen(url, { label: title, focus: true })} type="button">FOCUS</button>
      </div>
    </article>
  );
}

function CurrentChatGptTabRow({
  item,
  onFocus,
  onOpen,
  onRead,
  onRelay,
}: {
  item: Record<string, unknown>;
  onFocus: (tab: Record<string, unknown>) => void;
  onOpen: (url: unknown, options?: { label?: string; focus?: boolean }) => void;
  onRead: (tab: Record<string, unknown>) => void;
  onRelay: (tab: Record<string, unknown>) => void;
}) {
  const title = text(item.title, text(item.native_id, 'ChatGPT tab'));
  const url = text(item.url, '');
  const selected = text(item.bound, 'false') === 'true' || text(item.active_browser_tab, 'false') === 'true';
  const state = [
    text(item.kind, 'tab'),
    text(item.status, ''),
    text(item.current_window, 'false') === 'true' ? 'current window' : '',
    text(item.bound, 'false') === 'true' ? 'bound' : '',
  ].filter(Boolean).join(' / ');
  return (
    <article className={`ion-browser-gpt-native-nav-row ion-browser-gpt-current-tab-row${selected ? ' is-selected' : ''}`}>
      <div className="ion-browser-gpt-native-nav-main">
        <span>{title}</span>
        <b>{state}</b>
      </div>
      <code>{url || `tab ${text(item.tab_id, '')}`}</code>
      <div className="ion-browser-gpt-current-tab-buttons">
        <button onClick={() => onFocus(item)} type="button">FOCUS</button>
        <button onClick={() => onRead(item)} type="button">READ</button>
        <button onClick={() => onRelay(item)} type="button">RELAY</button>
        <button disabled={!url} onClick={() => onOpen(url, { label: title, focus: true })} type="button">LOAD</button>
      </div>
    </article>
  );
}

function MergeTabRow({
  item,
  onFocus,
  onRead,
  onRelay,
  onToggle,
  selected,
}: {
  item: Record<string, unknown>;
  onFocus: (tab: Record<string, unknown>) => void;
  onRead: (tab: Record<string, unknown>) => void;
  onRelay: (tab: Record<string, unknown>) => void;
  onToggle: (tab: Record<string, unknown>) => void;
  selected: boolean;
}) {
  const title = text(item.title, text(item.native_id, 'ChatGPT tab'));
  const url = text(item.url, '');
  const state = [
    text(item.status, text(item.kind, 'tab')),
    text(item.bound, 'false') === 'true' ? 'bound' : '',
    text(item.active_browser_tab, 'false') === 'true' || text(item.active, 'false') === 'true' ? 'active' : '',
  ].filter(Boolean).join(' / ');
  return (
    <article className={`ion-browser-gpt-native-nav-row ion-browser-gpt-merge-tab-row${selected ? ' is-selected' : ''}`}>
      <button className="ion-browser-gpt-merge-check" onClick={() => onToggle(item)} title={selected ? 'Remove from visual merge' : 'Add to visual merge'} type="button">
        {selected ? <CheckIcon /> : '+'}
      </button>
      <div className="ion-browser-gpt-native-nav-main">
        <span>{title}</span>
        <b>{state}</b>
      </div>
      <code>{url || `tab ${text(item.tab_id, '')}`}</code>
      <div className="ion-browser-gpt-current-tab-buttons">
        <button onClick={() => onFocus(item)} type="button">FOCUS</button>
        <button onClick={() => onRead(item)} type="button">READ</button>
        <button onClick={() => onRelay(item)} type="button">RELAY</button>
      </div>
    </article>
  );
}

function MergeCodexSessionRow({
  attachment,
  item,
  onToggle,
  selected,
}: {
  attachment?: Record<string, unknown>;
  item: Record<string, unknown>;
  onToggle: (session: Record<string, unknown>) => void;
  selected: boolean;
}) {
  const title = text(item.display_title ?? item.thread_name ?? item.latest_user_snippet, 'Codex session');
  const attachmentPath = text(attachment?.packet_path, '');
  const state = [
    text(item.is_current_session, 'false') === 'true' ? 'current' : '',
    attachmentPath ? 'attached' : '',
    text(item.model, ''),
    text(item.history_latest_ts ?? item.updated_at ?? item.created_at, ''),
  ].filter(Boolean).join(' / ');
  const snippet = text(item.latest_user_snippet ?? item.latest_assistant_snippet ?? item.first_user_snippet, 'No safe snippet indexed.');
  const path = text(item.session_path ?? item.cwd ?? item.session_id, '');
  return (
    <article className={`ion-browser-gpt-native-nav-row ion-browser-gpt-merge-tab-row ion-browser-gpt-merge-source-row${selected ? ' is-selected' : ''}`}>
      <button className="ion-browser-gpt-merge-check" onClick={() => onToggle(item)} title={selected ? 'Remove Codex chat from merge' : 'Add Codex chat to merge'} type="button">
        {selected ? <CheckIcon /> : '+'}
      </button>
      <div className="ion-browser-gpt-native-nav-main">
        <span>{title}</span>
        <b>{state || text(item.session_id, 'session')}</b>
      </div>
      <p>{snippet}</p>
      <code>{path}</code>
      {attachmentPath ? <code>{attachmentPath}</code> : null}
    </article>
  );
}

function MergeAgentRow({
  item,
  onToggle,
  selected,
}: {
  item: Record<string, unknown>;
  onToggle: (agent: Record<string, unknown>) => void;
  selected: boolean;
}) {
  const mount = mergeAgentCodexMount(item);
  const identity = asRecord(item.identity);
  const nativeCodex = asRecord(mount.native_codex ?? asRecord(item.codex_mount).native_codex);
  const roleId = mergeAgentRoleId(item);
  const title = text(item.display_name ?? identity.display_name ?? mount.agent_display_name ?? roleId, 'Codex agent');
  const domain = text(item.domain_id ?? identity.domain_id ?? mount.domain_id, 'domain pending');
  const mountPath = text(mount.mount_path ?? mount.mount_abspath ?? nativeCodex.launch_cwd, '');
  const capsule = text(mount.portable_context_manifest_path ?? mount.portable_capsule_path ?? mount.active_context_package_md_path ?? mount.agents_md_path, '');
  const state = [
    roleId,
    text(mount.materialized, 'false') === 'true' ? 'mounted' : 'candidate',
    text(nativeCodex.uses_portable_ion_context_capsule, 'false') === 'true' ? 'capsule' : '',
  ].filter(Boolean).join(' / ');
  return (
    <article className={`ion-browser-gpt-native-nav-row ion-browser-gpt-merge-tab-row ion-browser-gpt-merge-source-row${selected ? ' is-selected' : ''}`}>
      <button className="ion-browser-gpt-merge-check" onClick={() => onToggle(item)} title={selected ? 'Remove Codex agent from merge' : 'Add Codex agent to merge'} type="button">
        {selected ? <CheckIcon /> : '+'}
      </button>
      <div className="ion-browser-gpt-native-nav-main">
        <span>{title}</span>
        <b>{state}</b>
      </div>
      <p>{domain}</p>
      <code>{mountPath || capsule || roleId}</code>
      {capsule && capsule !== mountPath ? <code>{capsule}</code> : null}
    </article>
  );
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="ion-browser-gpt-status-row">
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function PathLine({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-browser-gpt-path-v2">
      <span>{label}</span>
      <code>{text(value, '')}</code>
    </div>
  );
}

function drawerTitle<T extends string>(items: Array<IconBarItem<T>>, active: T) {
  return items.find((item) => item.id === active)?.title ?? active;
}

function controlLabel(control: Record<string, unknown> | undefined, fallback: string) {
  return text(control?.label, fallback);
}

function toolLabel(surfaceId: string, control: Record<string, unknown> | undefined) {
  const label = controlLabel(control, surfaceId.replaceAll('_', ' '));
  if (surfaceId === 'file_attach_button') return 'Upload';
  if (surfaceId === 'tools_menu_opener') return 'Tools';
  if (surfaceId === 'thinking_mode_control') return 'Thinking';
  if (surfaceId === 'model_picker') return label || 'Model';
  if (surfaceId === 'voice_mic_button') return 'Voice';
  return label;
}

function composerToolbarIcon(surfaceId: string) {
  if (surfaceId === 'file_attach_button') return <ComposeIcon />;
  if (surfaceId === 'tools_menu_opener') return <ToolsIcon />;
  if (surfaceId === 'thinking_mode_control') return <StatusIcon />;
  if (surfaceId === 'model_picker') return <SettingsIcon />;
  if (surfaceId === 'voice_mic_button') return <ChatIcon />;
  if (surfaceId === 'slash_command_menu') return <LensIcon />;
  return <WorkSurfaceIcon />;
}

function toolbarStatusTone(status: unknown, present = true): ToolbarTone {
  const clean = text(status, '').toLowerCase();
  if (!present || clean === 'false' || clean === 'off' || clean.includes('unsafe') || clean.includes('missing') || clean.includes('blocked') || clean.includes('error') || clean.includes('failed')) {
    return 'missing';
  }
  if (clean.startsWith('not ') || clean.includes('unchecked') || clean.includes('pending') || clean.includes('idle') || clean.includes('busy') || clean.includes('sync') || clean.includes('gated') || clean.includes('quiet')) {
    return 'watch';
  }
  if (clean === 'true' || clean.includes('ready') || clean.includes('available') || clean.includes('loaded') || clean.includes('relayed') || clean.includes('synced') || clean.includes('sent') || clean.includes('open') || clean.includes('on')) {
    return 'ready';
  }
  return 'watch';
}

function shortMiddle(value: unknown, limit = 48) {
  const raw = text(value, '');
  if (raw.length <= limit) return raw;
  const headLength = Math.max(8, Math.floor((limit - 3) * 0.58));
  const tailLength = Math.max(6, limit - 3 - headLength);
  return `${raw.slice(0, headLength)}...${raw.slice(-tailLength)}`;
}

function roleClass(value: unknown) {
  const role = text(value, 'unknown').toLowerCase();
  if (role.includes('user')) return 'user';
  if (role.includes('assistant')) return 'assistant';
  return 'unknown';
}

function sendFailureText(response: Record<string, unknown>) {
  const result = (response.result ?? {}) as Record<string, unknown>;
  const nested = (result.result ?? {}) as Record<string, unknown>;
  return text(nested.finding ?? nested.error ?? result.finding ?? result.error ?? response.finding ?? response.stage ?? response.error, 'send failed');
}

function bridgePayload(response: Record<string, unknown>) {
  const result = (response.result ?? {}) as Record<string, unknown>;
  const nested = (result.result ?? {}) as Record<string, unknown>;
  return Object.keys(nested).length > 0 ? nested : result;
}

function delegatedBranchResult(value: unknown) {
  const record = asRecord(value);
  return asRecord(record.delegated_result ?? record.result ?? record);
}

function screenOpsControlPointSummary(assessment: Record<string, unknown>) {
  const controlPoints = (assessment.control_points ?? {}) as Record<string, unknown>;
  const reload = ((controlPoints.extension_reload_button ?? {}) as Record<string, unknown>).current_screen_point as Record<string, unknown> | undefined;
  const upload = ((controlPoints.cockpit_upload_button ?? {}) as Record<string, unknown>).current_screen_point as Record<string, unknown> | undefined;
  const findings = Array.isArray(assessment.findings) ? assessment.findings.map((item) => text(item, '')).filter(Boolean) : [];
  const parts = [
    reload ? `reload ${text(reload.x, '?')},${text(reload.y, '?')}` : '',
    upload ? `upload ${text(upload.x, '?')},${text(upload.y, '?')}` : '',
    findings.length ? `findings ${findings.join(', ')}` : '',
  ].filter(Boolean);
  return parts.join(' / ');
}

function messagePreviews(transcript: Record<string, unknown>) {
  return asRecords(transcript.messages).map((message) => messageBody(message));
}

function conversationSyncState(transcript: Record<string, unknown>, expectedText: string) {
  const messages = asRecords(transcript.messages);
  const expected = expectedText.trim();
  let expectedIndex = -1;
  messages.forEach((message, index) => {
    const preview = messageBody(message);
    const role = text(message.role, '');
    if (expected && preview.includes(expected) && role !== 'assistant') expectedIndex = index;
  });
  const afterExpected = expectedIndex >= 0 ? messages.slice(expectedIndex + 1) : [];
  const assistantAfterExpected = afterExpected.filter((message) => text(message.role, '') === 'assistant');
    const sawAssistantTextAfterExpected = assistantAfterExpected.some((message) => isAssistantReplyText(messageBody(message)));
  const sawAssistantReplyAfterExpected = assistantAfterExpected.some((message) => (
    isAssistantReplyText(messageBody(message)) && text(message.streaming, 'false') !== 'true'
  ));
  return {
    sawExpectedText: expectedIndex >= 0 || messagePreviews(transcript).some((preview) => expected && preview.includes(expected)),
    sawAssistantTextAfterExpected,
    sawAssistantReplyAfterExpected,
  };
}

function isAssistantReplyText(value: string) {
  const normalized = value.replace(/\s+/g, ' ').trim();
  const lower = normalized.toLowerCase();
  if (!normalized) return false;
  if (lower === 'thinking' || lower === 'thinking...') return false;
  if (/^thought for (a couple of seconds|\d+\s*s|\d+\s*seconds?)\s*>?$/.test(lower)) return false;
  return true;
}

function hasThinkingDom(message: Record<string, unknown>) {
  return text(message.has_thinking, 'false') === 'true' && text(message.thinking_preview, '').length > 0;
}

function messageBody(message: Record<string, unknown>) {
  return text(message.text_full, text(message.text_preview, ''));
}

function readFileAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const value = String(reader.result ?? '');
      resolve(value.includes(',') ? value.split(',', 2)[1] : value);
    };
    reader.onerror = () => reject(reader.error ?? new Error('file_read_failed'));
    reader.readAsDataURL(file);
  });
}

function downloadJson(filename: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.rel = 'noopener';
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function asRecords(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === 'object' && !Array.isArray(item)) : [];
}

function asStrings(value: unknown) {
  return Array.isArray(value) ? value.map((item) => text(item, '')).filter(Boolean) : [];
}

function numberValue(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0;
}

function numericValue(value: unknown) {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && value.trim()) {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return undefined;
}

function clampInteger(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, Math.round(value)));
}

function completedAssistantSignature(events: Array<Record<string, unknown>>) {
  const candidates = events.filter((event) => (
    timelineEventType(event) === 'message' &&
    roleClass(event.role) === 'assistant' &&
    !timelineEventIsActive(event) &&
    isAssistantReplyText(messageBody(event))
  ));
  const latest = candidates[candidates.length - 1];
  if (!latest) return '';
  return [
    text(latest.message_id ?? latest.id ?? latest.event_index ?? latest.index, ''),
    text(latest.text_sha256, ''),
    messageBody(latest).slice(0, 240),
  ].filter(Boolean).join('|');
}

function nativeAtlasNode(item: Record<string, unknown>, index: number, kind: 'native' | 'custom-gpt'): BrowserGptAtlasNode {
  const title = text(item.title, text(item.id, kind === 'custom-gpt' ? `Custom GPT ${index + 1}` : `Chat ${index + 1}`));
  const url = text(item.url, '');
  return {
    id: `${kind}:${url || title}:${index}`,
    kind,
    title,
    detail: url || text(item.description, 'native ChatGPT entry'),
    meta: text(item.kind ?? item.selected, kind === 'custom-gpt' ? 'custom GPT' : 'chat'),
    ref: url || `${kind}:${title}`,
    tone: text(item.selected, 'false') === 'true' ? 'active' : 'ready',
    icon: kind === 'custom-gpt' ? <ArchiveIcon /> : <ChatIcon />,
    url,
  };
}

function contextMention(ref: string) {
  const label = ref
    .replace(/^https?:\/\/(www\.)?/i, '')
    .split(/[/?#]/)
    .filter(Boolean)
    .slice(-2)
    .join('_')
    .replace(/\.[^.]+$/, '')
    .replace(/[^a-zA-Z0-9_-]+/g, '_')
    .replace(/^_+|_+$/g, '');
  return `@${label || ref.replace(/[^a-zA-Z0-9_-]+/g, '_')}`;
}

function appendText(previous: string, next: string) {
  const clean = next.trim().replace(/\s+/g, ' ');
  if (!clean) return previous;
  if (!previous.trim()) return clean;
  return `${previous}${/\\s$/.test(previous) ? '' : ' '}${clean}`;
}

function hasReadableMessage(value: Record<string, unknown>) {
  return messageBody(value).length > 0;
}

function hasReadableTimelineEvent(value: Record<string, unknown>) {
  return messageBody(value).length > 0 || (timelineEventType(value) !== 'message' && timelineEventTitle(value).length > 0);
}

function timelineEventType(value: Record<string, unknown>) {
  return text(value.event_type, 'message').toLowerCase();
}

function timelineEventState(value: Record<string, unknown>) {
  if (text(value.streaming, 'false') === 'true') return 'active';
  return text(value.state, timelineEventType(value) === 'message' ? 'complete' : 'status').toLowerCase();
}

function timelineEventIsActive(value: Record<string, unknown>) {
  const state = timelineEventState(value);
  return state === 'active' || state === 'running' || state === 'thinking';
}

function timelineEventClass(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'unknown';
}

function timelineEventTitle(value: Record<string, unknown>) {
  const eventType = timelineEventType(value);
  if (eventType === 'message') return text(value.role, 'message');
  return text(value.label, eventType.replaceAll('_', ' '));
}

function timelineEventMeta(value: Record<string, unknown>, index: number) {
  const eventType = timelineEventType(value);
  const state = timelineEventState(value);
  if (eventType === 'message') return text(value.index, String(index + 1));
  const parent = text(value.parent_message_index, '');
  return [state, parent ? `msg ${parent}` : '', text(value.event_index, String(index + 1))].filter(Boolean).join(' / ');
}

function optimisticEventStillVisible(event: Record<string, unknown>, baseEvents: Array<Record<string, unknown>>) {
  if (text(event.optimistic, 'false') !== 'true') return true;
  const expected = text(event.optimistic_expected_text, '');
  const kind = text(event.optimistic_kind, '');
  const messageEvents = baseEvents.filter((item) => timelineEventType(item) === 'message');
  if (kind === 'user_send') {
    return !messageEvents.some((item) => roleClass(item.role) === 'user' && messageBody(item).trim() === expected);
  }
  if (kind === 'assistant_pending') {
    const syncState = conversationSyncState({ messages: messageEvents }, expected);
    return !syncState.sawAssistantReplyAfterExpected;
  }
  return true;
}

function optimisticElapsedLabel(event: Record<string, unknown>, nowMs: number) {
  if (text(event.optimistic, 'false') !== 'true') return '';
  const created = Date.parse(text(event.created_at, ''));
  if (!Number.isFinite(created)) return '';
  const seconds = Math.max(0, Math.floor((nowMs - created) / 1000));
  return `${seconds}s ${timelineEventState(event)}`;
}

function approvalTitle(value: Record<string, unknown>) {
  return text(value.title ?? value.operation ?? value.action_name ?? value.intent ?? value.action_id ?? value.request_id, 'approval request');
}

function approvalDetailText(value: Record<string, unknown>) {
  const direct = text(value.detail_text, '');
  if (direct) return direct;
  const details = value.details ?? value.detail ?? null;
  if (details && typeof details === 'object') return stringifyPanelJson(details);
  return stringifyPanelJson(value);
}

function approvalDetailRows(value: Record<string, unknown>) {
  const rows: Array<Record<string, unknown>> = [];
  const add = (kind: string, label: string, rowValue: unknown, selector = '') => {
    const detailValue = compactDetailValue(rowValue);
    if (!detailValue) return;
    rows.push({
      kind,
      label,
      value: detailValue.slice(0, 2400),
      selector,
    });
  };
  const details = asRecord(value.details ?? value.detail ?? value.payload);
  const identity = asRecord(value.identity ?? details.identity);
  const panelDetails = asRecord(details.panel_details);
  add('request', 'request id', value.request_id);
  add('state', 'status', value.status ?? value.state);
  add('kind', 'approval kind', value.approval_kind ?? value.kind);
  add('summary', 'action summary', value.detail_summary ?? value.action_summary ?? details.action_summary ?? identity.summary);
  add('host', 'action host', value.action_host ?? details.action_host ?? identity.host);
  add('operation', 'http operation', value.operation ?? details.operation ?? identity.operation);
  add('operation', 'http method', value.http_method ?? details.http_method ?? identity.http_method);
  add('operation', 'http path', value.http_path ?? details.http_path ?? identity.http_path);
  add('action', 'action name', value.action_name ?? details.action_name ?? identity.action_name);
  add('control', 'confirm button', value.confirm_button_text ?? details.confirm_button_text, text(details.button_selector, ''));
  add('host', 'gateway status', value.gateway_status ?? details.gateway_status);
  add('card', 'visible summary', value.text_full ?? value.text_preview ?? details.card_text, text(details.selector, ''));
  for (const row of [
    ...asRecords(value.detail_rows),
    ...asRecords(details.detail_rows),
    ...asRecords(panelDetails.detail_rows),
  ]) {
    add(text(row.kind, 'detail'), text(row.label, 'detail'), row.value ?? row.text_full ?? row.text_preview, text(row.selector, ''));
  }
  for (const panel of asRecords(panelDetails.panels).slice(0, 8)) {
    add('panel', text(panel.label, 'panel'), panel.text_full ?? panel.text_preview, text(panel.selector, ''));
  }
  for (const control of asRecords(panelDetails.controls).slice(0, 12)) {
    add('control', text(control.label, 'control'), control.text_full ?? control.text_preview, text(control.selector, ''));
  }
  for (const event of asRecords(details.expansion_events).slice(0, 5)) {
    add('expand', text(event.status, 'expanded'), event.label ?? event.selector, text(event.selector, ''));
  }
  const seen = new Set<string>();
  return rows.filter((row) => {
    const key = `${text(row.kind, '')}:${text(row.label, '')}:${text(row.value, '').slice(0, 160)}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 48);
}

function actionSyncRecordTitle(row: Record<string, unknown>) {
  const payload = asRecord(row.payload);
  const ionAction = asRecord(payload.ion_action);
  return text(
    row.action_id ??
      row.idempotency_key ??
      row.packet_id ??
      row.operation ??
      row.name ??
      row.path ??
      row.suite_id ??
      ionAction.action_id ??
      payload.action_id,
    'action record',
  );
}

function localActionSyncMatches(request: Record<string, unknown>, sync: Record<string, unknown>): ActionSyncMatch[] {
  const browserQueue = asRecord(sync.browser_queue);
  const ledger = asRecord(sync.idempotency_ledger);
  const candidates: Array<{ kind: string; rows: Array<Record<string, unknown>> }> = [
    { kind: 'receipt', rows: asRecords(sync.recent_action_receipts) },
    { kind: 'packet', rows: asRecords(sync.recent_action_packets) },
    { kind: 'queue', rows: asRecords(browserQueue.packets) },
    { kind: 'ledger', rows: asRecords(ledger.entries) },
    { kind: 'service', rows: asRecords(sync.recent_service_receipts) },
    { kind: 'run', rows: asRecords(sync.recent_test_receipts) },
  ];
  const tokens = actionSyncSearchTokens(request);
  if (!tokens.length) return [];
  const matches: ActionSyncMatch[] = [];
  for (const group of candidates) {
    for (const row of group.rows) {
      const searchable = actionSyncSearchText(row);
      const score = tokens.reduce((count, token) => count + (searchable.includes(token) ? 1 : 0), 0);
      if (score <= 0) continue;
      matches.push({ kind: group.kind, title: actionSyncRecordTitle(row), score, record: row });
    }
  }
  return matches
    .sort((a, b) => b.score - a.score || a.title.localeCompare(b.title))
    .slice(0, 8);
}

function actionSyncSearchTokens(value: unknown) {
  const raw = actionSyncSearchText(value);
  const tokens = new Set<string>();
  const common = new Set([
    'action',
    'actions',
    'approval',
    'approve',
    'button',
    'chatgpt',
    'gateway',
    'helixion',
    'native',
    'pending',
    'request',
    'status',
  ]);
  const add = (candidate: unknown) => {
    const normalized = text(candidate, '').toLowerCase();
    if (normalized.length >= 7 && !common.has(normalized)) tokens.add(normalized);
  };
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    const record = value as Record<string, unknown>;
    [
      'action_id',
      'idempotency_key',
      'operation',
      'intent',
      'service_name',
      'request_id',
      'title',
      'summary',
      'confirm_button_text',
      'text_full',
      'text_preview',
    ].forEach((key) => add(record[key]));
    const details = asRecord(record.details ?? record.detail ?? record.payload);
    [
      'action_id',
      'idempotency_key',
      'operation',
      'intent',
      'service_name',
      'card_text',
      'button_selector',
      'selector',
      'target',
    ].forEach((key) => add(details[key]));
  }
  const matches = raw.match(/[a-z0-9][a-z0-9_-]{6,}/g) ?? [];
  for (const match of matches) {
    const token = match.toLowerCase();
    if (!common.has(token)) tokens.add(token);
  }
  return Array.from(tokens).slice(0, 40);
}

function actionSyncSearchText(value: unknown) {
  try {
    return JSON.stringify(value).toLowerCase();
  } catch (_error) {
    return text(value, '').toLowerCase();
  }
}

function browserGptTabKey(tab: Record<string, unknown>) {
  return text(tab.tab_id ?? tab.url ?? tab.native_id ?? tab.title, '');
}

function publicToken() {
  return '';
}

function withPublicToken(payload: Record<string, unknown>) {
  return payload;
}

function uniqueStrings(values: unknown[]) {
  return Array.from(new Set(values.map((value) => text(value, '')).filter(Boolean)));
}

function uniqueAttachmentRows(rows: Array<Record<string, unknown>>) {
  const seen = new Set<string>();
  return rows.filter((row) => {
    const key = text(row.session_id ?? row.attachment_id ?? row.packet_path, '');
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function normalizeMergeArchiveAttachment(payload: Record<string, unknown>, session: Record<string, unknown>) {
  const attachment = asRecord(payload.attachment);
  const packet = asRecord(payload.packet);
  return {
    ...attachment,
    session_id: text(attachment.session_id ?? packet.session_id ?? session.session_id, ''),
    thread_name: text(attachment.thread_name ?? packet.thread_name ?? session.display_title ?? session.thread_name, ''),
    attachment_id: text(attachment.attachment_id ?? packet.attachment_id, ''),
    packet_path: text(attachment.packet_path ?? packet.packet_path, ''),
    source_session_path: text(packet.source_session_path ?? session.session_path, ''),
    attachment_sha256: text(packet.attachment_sha256, ''),
    excerpt_count: text(packet.excerpt_count, ''),
    raw_transcript_exported: false,
    hidden_reasoning_exposed: false,
    production_authority: false,
    live_execution_authority: false,
  };
}

function mergeAgentRoleId(agent: Record<string, unknown>) {
  const identity = asRecord(agent.identity);
  const mount = mergeAgentCodexMount(agent);
  return text(agent.role_id ?? agent.agent_id ?? identity.role_id ?? identity.agent_id ?? mount.agent_role_id ?? mount.mount_id, '');
}

function mergeAgentCodexMount(agent: Record<string, unknown>) {
  const pageEvidence = asRecord(agent.agent_page_evidence);
  const candidates = [
    asRecord(agent.codex_mount),
    asRecord(agent.native_codex_mount),
    asRecord(pageEvidence.codex_mount),
    asRecord(agent.mount),
  ];
  return candidates.find((candidate) => Object.keys(candidate).length > 0) ?? {};
}

function mergeCodexSessionSourceRefs(session: Record<string, unknown>) {
  return uniqueStrings([
    session.session_path,
    session.session_id,
    session.cwd,
  ]);
}

function mergeArchiveAttachmentSourceRefs(attachment: Record<string, unknown>) {
  return uniqueStrings([
    attachment.packet_path,
    attachment.source_session_path,
    attachment.session_id,
    attachment.attachment_id,
  ]);
}

function mergeAgentSourceRefs(agent: Record<string, unknown>) {
  const pageEvidence = asRecord(agent.agent_page_evidence);
  const contextSystem = asRecord(pageEvidence.context_system);
  const contextCard = asRecord(contextSystem.card);
  const mount = mergeAgentCodexMount(agent);
  const nativeCodex = asRecord(mount.native_codex ?? asRecord(agent.codex_mount).native_codex);
  return uniqueStrings([
    mergeAgentRoleId(agent),
    mount.mount_path,
    mount.mount_abspath,
    mount.manifest_path,
    mount.agents_md_path,
    mount.config_path,
    mount.active_context_package_path,
    mount.active_context_package_md_path,
    mount.portable_context_manifest_path,
    mount.portable_mini_path,
    mount.portable_capsule_path,
    nativeCodex.launch_cwd,
    contextCard.path,
    ...asStrings(mount.context_refs).slice(0, 8),
  ]);
}

function mergeRoomSourceRefs({
  browserGptProbePath,
  browserGptTarget,
  codexAgents,
  codexAttachments,
  codexSessions,
  tabs,
  threadId,
}: {
  browserGptProbePath: string;
  browserGptTarget: string;
  codexAgents: Array<Record<string, unknown>>;
  codexAttachments: Array<Record<string, unknown>>;
  codexSessions: Array<Record<string, unknown>>;
  tabs: Array<Record<string, unknown>>;
  threadId: string;
}) {
  return uniqueStrings([
    browserGptTarget,
    browserGptProbePath,
    threadId,
    ...tabs.map((tab) => text(tab.url ?? tab.title ?? tab.tab_id, '')).filter(Boolean),
    ...codexSessions.flatMap(mergeCodexSessionSourceRefs),
    ...codexAttachments.flatMap(mergeArchiveAttachmentSourceRefs),
    ...codexAgents.flatMap(mergeAgentSourceRefs),
  ]);
}

function parseMergeTags(value: string) {
  const tags = value
    .split(/[,\s]+/g)
    .map((item) => item.trim().replace(/^#+/, '').replace(/[^a-zA-Z0-9_-]+/g, '_').replace(/^_+|_+$/g, ''))
    .filter(Boolean);
  return Array.from(new Set(tags)).slice(0, 12);
}

function buildVisualMergeContextBlock({
  actionStatus,
  codexAgents,
  codexArchiveStatus,
  codexAttachments,
  codexSessions,
  codexWorkbenchState,
  commsChannelId,
  commsThreadId,
  context,
  roomName,
  tabs,
  tags,
  targetRole,
}: {
  actionStatus: string;
  codexAgents: Array<Record<string, unknown>>;
  codexArchiveStatus: string;
  codexAttachments: Array<Record<string, unknown>>;
  codexSessions: Array<Record<string, unknown>>;
  codexWorkbenchState: string;
  commsChannelId: string;
  commsThreadId: string;
  context: string;
  roomName: string;
  tabs: Array<Record<string, unknown>>;
  tags: string[];
  targetRole: string;
}) {
  const cleanName = text(roomName, 'Browser GPT merge room');
  const tagLine = tags.length ? tags.map((tag) => `#${tag}`).join(' ') : '#browser-gpt #ion-actions #agent-comms';
  const tabLines = tabs.length
    ? tabs.slice(0, 12).map((tab, index) => {
      const title = text(tab.title ?? tab.native_id, `ChatGPT tab ${index + 1}`);
      const url = text(tab.url, `tab ${text(tab.tab_id, index + 1)}`);
      return `- ${title}: ${url}`;
    }).join('\n')
    : '- No ChatGPT tab selected yet.';
  const codexSessionLines = codexSessions.length
    ? codexSessions.slice(0, 12).map((session, index) => {
      const title = text(session.display_title ?? session.thread_name ?? session.latest_user_snippet, `Codex session ${index + 1}`);
      const sessionId = text(session.session_id, 'session');
      const path = text(session.session_path ?? session.cwd, 'path unavailable');
      const latest = text(session.latest_user_snippet ?? session.latest_assistant_snippet, 'No safe snippet indexed.');
      return `- ${title}\n  session_id: ${sessionId}\n  path: ${path}\n  latest: ${latest}`;
    }).join('\n')
    : '- No prior Codex CLI chat selected yet.';
  const attachmentLines = codexAttachments.length
    ? codexAttachments.slice(0, 12).map((attachment) => {
      const sessionId = text(attachment.session_id, 'session');
      const title = text(attachment.thread_name, sessionId);
      const packetPath = text(attachment.packet_path, 'packet pending');
      const sourcePath = text(attachment.source_session_path, 'source pending');
      return `- ${title}\n  session_id: ${sessionId}\n  attachment_packet: ${packetPath}\n  source_session_path: ${sourcePath}`;
    }).join('\n')
    : '- No redacted Codex archive attachment generated yet.';
  const codexAgentLines = codexAgents.length
    ? codexAgents.slice(0, 12).map((agent) => {
      const mount = mergeAgentCodexMount(agent);
      const roleId = mergeAgentRoleId(agent);
      const title = text(agent.display_name ?? asRecord(agent.identity).display_name ?? mount.agent_display_name ?? roleId, 'Codex agent');
      const domain = text(agent.domain_id ?? asRecord(agent.identity).domain_id ?? mount.domain_id, 'domain pending');
      const mountPath = text(mount.mount_path ?? mount.mount_abspath, 'mount pending');
      const capsule = text(mount.portable_context_manifest_path ?? mount.portable_capsule_path ?? mount.active_context_package_md_path, 'capsule pending');
      return `- ${title} (${roleId})\n  domain: ${domain}\n  mount: ${mountPath}\n  capsule: ${capsule}`;
    }).join('\n')
    : '- No Codex agent selected yet.';
  return [
    `ION VISUAL MERGE ROOM: ${cleanName}`,
    `Tags: ${tagLine}`,
    `ION comms channel: ${text(commsChannelId, 'team')}`,
    `ION comms thread: ${text(commsThreadId, 'latest')}`,
    `Target role: ${text(targetRole, '@mentions in packet')}`,
    `Action sync: ${text(actionStatus, 'not checked')}`,
    `Codex archive: ${text(codexArchiveStatus, 'deferred')}`,
    `Codex workbench: ${text(codexWorkbenchState, 'deferred')}`,
    '',
    'Coordination rule:',
    'Use ION Actions and Agent Comms as the shared coordination source. The cockpit visual merge is an operator view only; do not assume the other ChatGPT tabs or Codex sessions share model memory.',
    'When a Codex CLI chat is listed, reopen or reference it through its session_id/session_path. When a Codex agent is listed, use its mount/capsule refs and queue-workpack route.',
    '',
    'Merged ChatGPT tabs:',
    tabLines,
    '',
    'Prior Codex CLI chats to rework:',
    codexSessionLines,
    '',
    'Redacted Codex archive attachments:',
    attachmentLines,
    '',
    'Codex agents and mounts to include:',
    codexAgentLines,
    '',
    'Context:',
    text(context, 'Use the selected ION comms room and action receipts for coordination.'),
  ].join('\n');
}

function latestByTimestamp(rows: Array<Record<string, unknown>>, key: string) {
  return [...rows].sort((left, right) => text(right[key], '').localeCompare(text(left[key], '')));
}

function browserGptRunCompletionState(run: Record<string, unknown>) {
  return text(asRecord(run.completion_state).state, '');
}

function browserGptRunHasActiveWorker(run: Record<string, unknown>) {
  const runtime = asRecord(run.worker_runtime);
  const latestWorker = asRecord(runtime.latest_worker ?? run.latest_worker);
  return truth(runtime.has_active_worker) || text(latestWorker.status, '') === 'running';
}

function browserGptRunIsActionable(run: Record<string, unknown>) {
  if (text(run.status, '') !== 'active') return false;
  const state = browserGptRunCompletionState(run);
  return ['worker_running', 'awaiting_return', 'ready_to_start_worker', 'pending_directive', 'workpack_active'].includes(state);
}

function browserGptRunOperationalText(run: Record<string, unknown>) {
  const state = text(run.operational_state, browserGptRunCompletionState(run) || 'unknown');
  if (state === 'response_observed') return 'response observed';
  if (state === 'workpack_active') return 'workpack active';
  if (state === 'messages_delivered') return 'messages delivered';
  if (state === 'blocked_by_policy') return 'blocked by policy';
  return state.replaceAll('_', ' ');
}

function browserGptRunWorkerState(run: Record<string, unknown>) {
  const runtime = asRecord(run.worker_runtime);
  const latestWorker = asRecord(runtime.latest_worker ?? run.latest_worker);
  if (truth(runtime.has_active_worker) || text(latestWorker.status, '') === 'running') return 'running';
  const state = text(latestWorker.status, '');
  if (state) return state.replaceAll('_', ' ');
  if ((numericValue(runtime.worker_count) ?? 0) > 0) return 'not running';
  return 'not started';
}

function browserGptRunWorkerText(run: Record<string, unknown>) {
  const runtime = asRecord(run.worker_runtime);
  const latestWorker = asRecord(runtime.latest_worker ?? run.latest_worker);
  const pid = text(latestWorker.pid, '');
  const agent = text(latestWorker.agent_display_name ?? latestWorker.agent_role_id, 'agent');
  const value = pid ? `pid ${pid} / ${agent}` : shortMiddle(text(latestWorker.workpack_path ?? latestWorker.run_packet_path, ''), 52);
  return value ? `${browserGptRunWorkerState(run)} / ${value}` : browserGptRunWorkerState(run);
}

function browserGptRunWorkpackPath(run: Record<string, unknown>) {
  const workItems = asRecords(run.work_items);
  const openWorkItem = workItems.find((item) => {
    const state = text(item.response_state, '');
    return text(item.workpack_path, '') && state !== 'returned' && !text(item.latest_return_packet_path, '');
  });
  const workpackPaths = asStrings(run.workpack_paths);
  return text(openWorkItem?.workpack_path ?? workItems[0]?.workpack_path ?? workpackPaths[0], '');
}

function browserGptCanStartRunWorker(run: Record<string, unknown>) {
  const status = text(run.status, '');
  const workItems = asRecords(run.work_items);
  const openWorkItem = workItems.find((item) => {
    const state = text(item.response_state, '');
    return text(item.workpack_path, '') && state !== 'returned' && !text(item.latest_return_packet_path, '');
  });
  return Boolean(text(run.run_id, '') && (openWorkItem || (!workItems.length && browserGptRunWorkpackPath(run))) && !status.includes('blocked'));
}

function browserGptRunLatestReturnPath(run: Record<string, unknown>) {
  const returnMessagePaths = asRecord(run.return_message_paths);
  const returnPaths = Object.keys(returnMessagePaths).map((item) => text(item, '')).filter(Boolean);
  return text(run.latest_return_packet_path ?? returnPaths[0], '');
}

function compactDetailValue(value: unknown) {
  if (value === null || typeof value === 'undefined') return '';
  if (typeof value === 'string') return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (typeof value === 'object') return stringifyPanelJson(value);
  return text(value, '');
}

function stringifyPanelJson(value: unknown) {
  try {
    return JSON.stringify(value, null, 2);
  } catch (_error) {
    return text(value, '');
  }
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {};
}

function truth(value: unknown) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') return ['1', 'true', 'yes', 'ready', 'on'].includes(value.trim().toLowerCase());
  return Boolean(value);
}

function text(value: unknown, fallback = 'unknown') {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}
