import { useEffect, useMemo, useState, type FormEvent, type MouseEvent, type ReactNode } from 'react';
import {
  AuthorityIcon,
  BlockersIcon,
  CloseIcon,
  GraphIcon,
  HorizonIcon,
  LensIcon,
  ProjectsIcon,
  QuestionsIcon,
  ReceiptIcon,
  RouteIcon,
  SourceIcon,
  StreamIcon,
  WorkSurfaceIcon,
} from './icons';
import type {
  IonCockpitViewModel,
  IonProjectCockpitBlocker,
  IonProjectCockpitMission,
  IonProjectCockpitProject,
  IonProjectCockpitQuestion,
  IonProjectCockpitTimelineEvent,
  IonProjectDocReference,
  IonProjectDocRow,
  IonProjectLauncherRecord,
  IonProjectOperatingSystem,
  IonProjectSpecialistProjection,
  IonProjectPortfolioDomain,
  IonProjectPortfolioDiff,
  IonProjectPortfolioFamily,
  IonProjectPortfolioVersion,
  IonVNextContextPackageProjection,
  IonVNextDocumentationSurfaces,
  IonVNextDriftGuard,
  IonVNextLane,
  IonVNextLongHorizonEpoch,
  IonVNextProtocolRow,
} from './ionRuntimeCockpitTypes';

export type ProjectTabId = 'projects' | 'vnext' | 'missions' | 'blockers' | 'questions' | 'timeline' | 'protocols' | 'context';
type DomainPanelTabId = 'overview' | 'builds' | 'changes' | 'ops' | 'docs' | 'workspace';
type DomainWorkspaceTabId = 'projects' | 'timeline' | 'chats' | 'diffs' | 'docs' | 'plans' | 'manage';
type LeftDrawerId = 'projects' | 'missions' | 'sources' | 'horizon';
type RightDrawerId = 'blockers' | 'questions' | 'receipts' | 'authority';
type VNextContextPackage = NonNullable<IonVNextContextPackageProjection['packages']>[number];
type VNextDocumentationSurface = NonNullable<IonVNextDocumentationSurfaces['surfaces']>[number];
type ProjectOrganizationState = NonNullable<NonNullable<IonCockpitViewModel['project_cockpit']>['organization_state']>;
type ProjectSpecialistLane = {
  laneId: string;
  role: string;
  label: string;
  objective: string;
};

const PROJECT_COCKPIT_CONFIRMATION = 'ION_PROJECT_COCKPIT_WRITE_CONFIRMED';

export const projectMissionTabs: Array<{ id: ProjectTabId; label: string }> = [
  { id: 'projects', label: 'PROJECTS' },
  { id: 'vnext', label: 'VNEXT' },
  { id: 'missions', label: 'MISSIONS' },
  { id: 'blockers', label: 'BLOCKERS' },
  { id: 'questions', label: 'QUESTIONS' },
  { id: 'timeline', label: 'TIMELINE' },
  { id: 'protocols', label: 'PROTOCOLS' },
  { id: 'context', label: 'CONTEXT' },
];

const leftDrawers: Array<{ id: LeftDrawerId; icon: ReactNode; title: string }> = [
  { id: 'projects', icon: <ProjectsIcon />, title: 'domains' },
  { id: 'missions', icon: <GraphIcon />, title: 'missions' },
  { id: 'sources', icon: <SourceIcon />, title: 'source truth' },
  { id: 'horizon', icon: <HorizonIcon />, title: 'long horizon' },
];

const rightDrawers: Array<{ id: RightDrawerId; icon: ReactNode; title: string }> = [
  { id: 'blockers', icon: <BlockersIcon />, title: 'blockers' },
  { id: 'questions', icon: <QuestionsIcon />, title: 'questions' },
  { id: 'receipts', icon: <ReceiptIcon />, title: 'receipts' },
  { id: 'authority', icon: <AuthorityIcon />, title: 'authority' },
];

const domainPanelTabs: Array<{ id: DomainPanelTabId; label: string }> = [
  { id: 'overview', label: 'OVERVIEW' },
  { id: 'builds', label: 'BUILDS' },
  { id: 'changes', label: 'CHANGES' },
  { id: 'ops', label: 'OPS' },
  { id: 'docs', label: 'DOCS' },
  { id: 'workspace', label: 'WORKSPACE' },
];

const domainWorkspaceTabs: Array<{ id: DomainWorkspaceTabId; label: string }> = [
  { id: 'projects', label: 'PROJECTS' },
  { id: 'timeline', label: 'TIMELINE' },
  { id: 'chats', label: 'CHATS' },
  { id: 'diffs', label: 'DIFFS' },
  { id: 'docs', label: 'DOCS' },
  { id: 'plans', label: 'PLANS' },
  { id: 'manage', label: 'MANAGE' },
];

const domainSpecialistLanes: ProjectSpecialistLane[] = [
  {
    laneId: 'domain_steward',
    role: 'role.steward',
    label: 'Domain Steward',
    objective: 'Placement, priority, gates, risks, and next actions.',
  },
  {
    laneId: 'domain_context_cartographer',
    role: 'role.context_cartographer',
    label: 'Context Cartographer',
    objective: 'Capsule, refs, docs, and project-to-chat binding map.',
  },
  {
    laneId: 'domain_nemesis_reviewer',
    role: 'role.nemesis',
    label: 'Nemesis Reviewer',
    objective: 'Duplicate collapse, missing docs, and false-claim audit.',
  },
];

const projectSpecialistLanes: ProjectSpecialistLane[] = [
  {
    laneId: 'project_steward',
    role: 'role.steward',
    label: 'Project Steward',
    objective: 'Family coherence, receipts, risks, gates, and next packet.',
  },
  {
    laneId: 'project_context_cartographer',
    role: 'role.context_cartographer',
    label: 'Context Cartographer',
    objective: 'Project capsule, refs, session bindings, and required reads.',
  },
  {
    laneId: 'project_mason_builder',
    role: 'role.mason',
    label: 'Mason Builder',
    objective: 'Bounded build/repair work from current source only.',
  },
  {
    laneId: 'project_diff_reviewer',
    role: 'role.nemesis',
    label: 'Diff Reviewer',
    objective: 'Adjacent version diff review before cleanup or promotion.',
  },
  {
    laneId: 'project_docs_curator',
    role: 'role.ionologist',
    label: 'Docs Curator',
    objective: 'README, architecture, runbook, decisions, notes, and screenshots.',
  },
];

export function ProjectMissionControlPanel({
  runtime,
  onRuntimeRefresh,
  activeTab: controlledActiveTab,
  hideSubtabs = false,
  onActiveTabChange,
}: {
  runtime: IonCockpitViewModel;
  onRuntimeRefresh?: () => void;
  activeTab?: ProjectTabId;
  hideSubtabs?: boolean;
  onActiveTabChange?: (tab: ProjectTabId) => void;
}) {
  const vnext = runtime.vnext_mission_control;
  const projectCockpit = runtime.project_cockpit;
  const [localActiveTab, setLocalActiveTab] = useState<ProjectTabId>('projects');
  const [leftDrawer, setLeftDrawer] = useState<LeftDrawerId>('projects');
  const [rightDrawer, setRightDrawer] = useState<RightDrawerId>('blockers');
  const [leftDrawerOpen, setLeftDrawerOpen] = useState(false);
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionMessage, setActionMessage] = useState<string>('');
  const [expandedDomainId, setExpandedDomainId] = useState('');
  const [domainPanelTab, setDomainPanelTab] = useState<DomainPanelTabId>('overview');
  const [domainWorkspaceTab, setDomainWorkspaceTab] = useState<DomainWorkspaceTabId>('projects');
  const [openProjectTabIds, setOpenProjectTabIds] = useState<string[]>([]);
  const [activeProjectWorkspaceTab, setActiveProjectWorkspaceTab] = useState('domain');
  const [portfolioSearch, setPortfolioSearch] = useState('');
  const [activePortfolioGroup, setActivePortfolioGroup] = useState('all');
  const [selectedFamilyId, setSelectedFamilyId] = useState('');
  const [selectedVersionId, setSelectedVersionId] = useState('');
  const [selectedDiffId, setSelectedDiffId] = useState('');
  const [favoriteFamilies, setFavoriteFamilies] = useState<string[]>(() => readStoredList('ion.projectPortfolio.favoriteFamilies'));
  const [familyNotes, setFamilyNotes] = useState<Record<string, string>>(() => readStoredTextRecord('ion.projectPortfolio.familyNotes'));
  const [familyScreenshots, setFamilyScreenshots] = useState<Record<string, string[]>>(() => readStoredImageRecord('ion.projectPortfolio.familyScreenshots'));
  const [projectLaunchRecords, setProjectLaunchRecords] = useState<IonProjectLauncherRecord[]>([]);
  const [launchBusyKey, setLaunchBusyKey] = useState('');
  const [launchDiagnostics, setLaunchDiagnostics] = useState<Record<string, Record<string, unknown>>>({});
  const [organizerBusy, setOrganizerBusy] = useState(false);
  const [organizerResult, setOrganizerResult] = useState<Record<string, unknown> | undefined>();
  const activeTab = controlledActiveTab ?? localActiveTab;
  const setActiveProjectTab = (tab: ProjectTabId) => {
    if (controlledActiveTab === undefined) setLocalActiveTab(tab);
    onActiveTabChange?.(tab);
  };

  useEffect(() => {
    setProjectLaunchRecords(projectCockpit?.launcher?.launches ?? []);
  }, [projectCockpit?.launcher?.generated_at, projectCockpit?.launcher?.launch_count]);

  useEffect(() => {
    if (activeTab !== 'projects' || !projectCockpit?.portfolio) return;
    setLeftDrawer('projects');
    setLeftDrawerOpen(true);
  }, [activeTab, projectCockpit?.portfolio?.generated_at]);

  if (!projectCockpit && (!vnext || vnext.status === 'missing')) {
    return (
      <section className="ion-vnext-workbench-shell is-missing">
        <div className="ion-vnext-empty">
          <WorkSurfaceIcon />
          <span>PROJECTS MISSION CONTROL</span>
          <b>project evidence missing</b>
        </div>
      </section>
    );
  }

  const projects = projectCockpit?.projects ?? [];
  const missions = projectCockpit?.missions ?? [];
  const blockers = projectCockpit?.blockers ?? [];
  const questions = projectCockpit?.questions ?? [];
  const timelineEvents = projectCockpit?.timeline_events ?? [];
  const latestReceipts = projectCockpit?.latest_receipts ?? [];
  const portfolio = projectCockpit?.portfolio;
  const portfolioDomains = portfolio?.canonical_domains ?? [];
  const portfolioGroups = portfolioDomains.length ? portfolioDomains : (portfolio?.groups ?? []);
  const portfolioFamilies = portfolio?.families ?? [];
  const portfolioProjects = portfolio?.projects ?? [];
  const projectLaunches = mergeLaunchRecords(projectCockpit?.launcher?.launches ?? [], projectLaunchRecords);
  const filteredPortfolioFamilies = useMemo(() => {
    const query = portfolioSearch.trim().toLowerCase();
    return portfolioFamilies.filter((family) => {
      const favorite = favoriteFamilies.includes(family.family_id);
      const hasProjectRoots = (family.project_count ?? 0) > 0;
      if (!query && !favorite && !hasProjectRoots) return false;
      if (activePortfolioGroup === 'favorites' && !favoriteFamilies.includes(family.family_id)) return false;
      const familyDomain = family.domain_id ?? family.group_id;
      if (activePortfolioGroup !== 'all' && activePortfolioGroup !== 'favorites' && familyDomain !== activePortfolioGroup) return false;
      if (!query) return true;
      const current = family.current ?? {};
      const haystack = [
        family.label,
        family.family_id,
        family.group_id,
        family.domain_id,
        family.domain_label,
        family.current_path,
        current.name,
        current.path,
        ...(family.versions ?? []).map((version) => `${version.label ?? ''} ${version.path ?? ''} ${version.version_token ?? ''}`),
      ].join(' ').toLowerCase();
      return haystack.includes(query);
    }).sort((left, right) => {
      const leftFavorite = favoriteFamilies.includes(left.family_id) ? 0 : 1;
      const rightFavorite = favoriteFamilies.includes(right.family_id) ? 0 : 1;
      if (leftFavorite !== rightFavorite) return leftFavorite - rightFavorite;
      const leftRoots = left.project_count ?? 0;
      const rightRoots = right.project_count ?? 0;
      if (leftRoots !== rightRoots) return rightRoots - leftRoots;
      const leftVersions = left.version_count ?? 0;
      const rightVersions = right.version_count ?? 0;
      if (leftVersions !== rightVersions) return rightVersions - leftVersions;
      return String(left.label ?? left.family_id).localeCompare(String(right.label ?? right.family_id));
    });
  }, [activePortfolioGroup, favoriteFamilies, portfolioFamilies, portfolioSearch]);
  const selectedPortfolioFamily = portfolioFamilies.find((family) => family.family_id === selectedFamilyId) ?? filteredPortfolioFamilies[0] ?? portfolioFamilies[0];
  const selectedDomainId = expandedDomainId
    || (activePortfolioGroup !== 'all' && activePortfolioGroup !== 'favorites' ? activePortfolioGroup : '')
    || (selectedPortfolioFamily?.domain_id ?? selectedPortfolioFamily?.group_id ?? '');
  const selectedPortfolioDomain = portfolioDomains.find((domain) => domain.domain_id === selectedDomainId)
    ?? portfolioDomains.find((domain) => domain.domain_id === activePortfolioGroup)
    ?? portfolioDomains[0];
  const selectedDomainFamilies = portfolioFamilies.filter((family) => (family.domain_id ?? family.group_id) === selectedPortfolioDomain?.domain_id).sort((left, right) => {
    const leftVersions = left.version_count ?? 0;
    const rightVersions = right.version_count ?? 0;
    if (leftVersions !== rightVersions) return rightVersions - leftVersions;
    return String(left.label ?? left.family_id).localeCompare(String(right.label ?? right.family_id));
  });
  const selectedFamilyVersions = selectedPortfolioFamily?.versions ?? [];
  const selectedFamilyDiffs = selectedPortfolioFamily?.diffs ?? [];
  const selectedPortfolioVersion = selectedFamilyVersions.find((version) => versionKey(version) === selectedVersionId)
    ?? selectedFamilyVersions.find((version) => version.is_current)
    ?? selectedFamilyVersions[selectedFamilyVersions.length - 1]
    ?? selectedFamilyVersions[0];
  const selectedPortfolioDiff = selectedFamilyDiffs.find((diff) => diff.diff_id === selectedDiffId)
    ?? selectedFamilyDiffs.find((diff) => diff.to_project_id === selectedPortfolioVersion?.project_id)
    ?? selectedFamilyDiffs[selectedFamilyDiffs.length - 1]
    ?? selectedFamilyDiffs[0];
  const selectedProject = projects.find((project) => project.project_id === projectCockpit?.selected_project_id) ?? projects[0];
  const openBlockers = blockers.filter((blocker) => isOpenStatus(blocker.status));
  const openQuestions = questions.filter((question) => isOpenStatus(question.status));
  const derivedBlockers = blockers.filter((blocker) => blocker.derived);
  const managedBlockers = blockers.filter((blocker) => !blocker.derived);
  const lanes = vnext?.lanes ?? [];
  const driftGuards = vnext?.drift_guards ?? [];
  const epochs = vnext?.long_horizon?.epochs ?? [];
  const latestEpochs = vnext?.long_horizon?.latest_epochs ?? epochs.slice(-6);
  const protocolRows = vnext?.protocol_index?.rows ?? [];
  const protocolGroups = vnext?.protocol_index?.groups ?? [];
  const contextPackages = vnext?.context_packages?.packages ?? [];
  const docSurfaces = vnext?.documentation_surfaces?.surfaces ?? [];
  const sourceRows = Object.entries({
    ...(vnext?.source_present ?? {}),
    ...(projectCockpit?.source_present ?? {}),
  });
  const writeConfirmation = projectCockpit?.write_confirmation ?? PROJECT_COCKPIT_CONFIRMATION;
  const localLaunchConfirmation = projectCockpit?.local_launch_confirmation ?? projectCockpit?.launcher?.confirmation ?? 'ION_PROJECT_LOCAL_LAUNCH_CONFIRMED';
  const projectSummary = projectCockpit?.summary ?? {};

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (window.location.hash === '#projects:vnext' || window.location.hash === '#vnext') {
      setActiveProjectTab('vnext');
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem('ion.projectPortfolio.favoriteFamilies', JSON.stringify(favoriteFamilies));
  }, [favoriteFamilies]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem('ion.projectPortfolio.familyNotes', JSON.stringify(familyNotes));
  }, [familyNotes]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem('ion.projectPortfolio.familyScreenshots', JSON.stringify(familyScreenshots));
  }, [familyScreenshots]);

  function selectLeftDrawer(id: LeftDrawerId) {
    const sameDrawer = leftDrawer === id;
    setLeftDrawer(id);
    setLeftDrawerOpen(!sameDrawer || !leftDrawerOpen);
  }

  function selectRightDrawer(id: RightDrawerId) {
    const sameDrawer = rightDrawer === id;
    setRightDrawer(id);
    setRightDrawerOpen(!sameDrawer || !rightDrawerOpen);
  }

  async function submitProjectAction(recordType: 'blocker' | 'question', action: 'create' | 'update' | 'resolve', event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = Object.fromEntries(Array.from(new FormData(form).entries()).map(([key, value]) => [key, String(value)]));
    payload.confirmation = writeConfirmation;
    payload.actor = payload.actor || 'project_cockpit_ui';
    setIsSubmitting(true);
    setActionMessage('');
    try {
      const response = await fetch(`/cockpit/projects/${recordType}/${action}`, {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'project action failed'));
        return;
      }
      setActionMessage(`${recordType} ${action} recorded`);
      if (action === 'create') form.reset();
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'project action failed');
    } finally {
      setIsSubmitting(false);
    }
  }

  function upsertProjectLaunch(record: IonProjectLauncherRecord | undefined) {
    if (!record?.launch_id) return;
    setProjectLaunchRecords((current) => {
      const next = current.filter((item) => item.launch_id !== record.launch_id);
      return [record, ...next].slice(0, 24);
    });
  }

  function launchRecordForVersion(version?: IonProjectPortfolioVersion) {
    if (!version) return undefined;
    const path = version.launch?.project_path ?? version.path;
    const versionId = version.launch?.version_id ?? version.version_id;
    const projectId = version.launch?.project_id ?? version.project_id;
    return projectLaunches.find((launch) => (
      Boolean(launch.running)
      && (
        (path && launch.path === path)
        || (versionId && launch.version_id === versionId)
        || (projectId && launch.project_id === projectId)
      )
    )) ?? projectLaunches.find((launch) => (
      (path && launch.path === path)
      || (versionId && launch.version_id === versionId)
      || (projectId && launch.project_id === projectId)
    ));
  }

  async function startProjectVersion(version: IonProjectPortfolioVersion | undefined, family: IonProjectPortfolioFamily | undefined) {
    if (!version) {
      setActionMessage('project launch failed: version missing');
      return;
    }
    const launch = version.launch ?? {};
    const launchPath = launch.project_path ?? version.path;
    if (!launchPath) {
      setActionMessage('project launch failed: path missing');
      return;
    }
    const busyKey = launchKeyForVersion(version);
    let openedWindow: Window | null = null;
    if (typeof window !== 'undefined') {
      openedWindow = window.open('about:blank', '_blank');
    }
    setLaunchBusyKey(busyKey);
    setActionMessage('');
    try {
      const payload: Record<string, unknown> = {
        confirmation: localLaunchConfirmation,
        path: launchPath,
        project_id: launch.project_id ?? version.project_id ?? family?.family_id,
        version_id: launch.version_id ?? version.version_id ?? versionKey(version),
        label: launch.label ?? version.display_label ?? version.label ?? family?.label ?? version.project_id,
        install_repair: launch.install_repair_on_launch !== false,
      };
      const response = await fetch(launch.action_path ?? '/cockpit/projects/launch/start', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        openedWindow?.close();
        setActionMessage(String(result.finding ?? result.error ?? 'project launch failed'));
        return;
      }
      upsertProjectLaunch(result.launch as IonProjectLauncherRecord);
      const openHref = String(result.open_href ?? result.launch?.open_href ?? result.url ?? '');
      if (openHref) {
        if (openedWindow) {
          openedWindow.location.href = openHref;
        } else if (typeof window !== 'undefined') {
          window.open(openHref, '_blank', 'noopener,noreferrer');
        }
      } else {
        openedWindow?.close();
      }
      setActionMessage(result.reused ? 'existing local launch opened' : 'local project launch started');
      onRuntimeRefresh?.();
    } catch (error) {
      openedWindow?.close();
      setActionMessage(error instanceof Error ? error.message : 'project launch failed');
    } finally {
      setLaunchBusyKey('');
    }
  }

  async function stopProjectLaunch(record: IonProjectLauncherRecord | undefined) {
    if (!record?.launch_id) {
      setActionMessage('project stop failed: launch missing');
      return;
    }
    setLaunchBusyKey(record.launch_id);
    setActionMessage('');
    try {
      const payload: Record<string, unknown> = {
        confirmation: localLaunchConfirmation,
        launch_id: record.launch_id,
      };
      const response = await fetch(record.stop_path ?? '/cockpit/projects/launch/stop', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'project stop failed'));
        return;
      }
      upsertProjectLaunch(result.launch as IonProjectLauncherRecord);
      setActionMessage('local project server stopped');
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'project stop failed');
    } finally {
      setLaunchBusyKey('');
    }
  }

  async function captureProjectLaunchDiagnostics(record: IonProjectLauncherRecord | undefined) {
    if (!record?.launch_id) {
      setActionMessage('diagnostics failed: launch missing');
      return;
    }
    setLaunchBusyKey(`diagnostics:${record.launch_id}`);
    setActionMessage('');
    try {
      const payload: Record<string, unknown> = {
        confirmation: localLaunchConfirmation,
        launch_id: record.launch_id,
        capture: true,
        width: 1365,
        height: 900,
      };
      const response = await fetch(record.diagnostics_path ?? '/cockpit/projects/launch/diagnostics', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (result.launch) upsertProjectLaunch(result.launch as IonProjectLauncherRecord);
      setLaunchDiagnostics((current) => ({ ...current, [record.launch_id as string]: result }));
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'diagnostics failed'));
        return;
      }
      setActionMessage('launch diagnostics captured');
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'diagnostics failed');
    } finally {
      setLaunchBusyKey('');
    }
  }

  async function materializePortfolioOrganizer() {
    if (!portfolio?.organizer) {
      setActionMessage('organizer sync failed: portfolio missing');
      return;
    }
    setOrganizerBusy(true);
    setActionMessage('');
    try {
      const payload: Record<string, unknown> = {
        confirmation: portfolio.organizer.materialize_confirmation ?? 'ION_PROJECT_PORTFOLIO_MATERIALIZE_CONFIRMED',
      };
      const response = await fetch(portfolio.organizer.materialize_path ?? '/cockpit/projects/organizer/materialize', {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      setOrganizerResult(result);
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'organizer sync failed'));
        return;
      }
      const summary = result.portfolio_summary as Record<string, unknown> | undefined;
      const families = summary?.family_count ?? result.family_count ?? 'projects';
      setActionMessage(`organizer synchronized: ${families} families`);
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'organizer sync failed');
    } finally {
      setOrganizerBusy(false);
    }
  }

  function toggleFavoriteFamily(familyId: string) {
    setFavoriteFamilies((current) => (
      current.includes(familyId) ? current.filter((item) => item !== familyId) : [...current, familyId]
    ));
  }

  function selectPortfolioDomain(domainId: string) {
    setActivePortfolioGroup(domainId);
    setExpandedDomainId(domainId);
    setDomainPanelTab('overview');
    setDomainWorkspaceTab('projects');
    setOpenProjectTabIds([]);
    setActiveProjectWorkspaceTab('domain');
    setLeftDrawerOpen(false);
    const firstFamily = portfolioFamilies.find((family) => (family.domain_id ?? family.group_id) === domainId);
    if (!firstFamily) {
      setSelectedFamilyId('');
      setSelectedVersionId('');
      setSelectedDiffId('');
      return;
    }
    setSelectedFamilyId(firstFamily.family_id);
    const versions = firstFamily.versions ?? [];
    const loadedVersion = versions.find((version) => version.is_current) ?? versions[versions.length - 1] ?? versions[0];
    setSelectedVersionId(loadedVersion ? versionKey(loadedVersion) : '');
    const diffs = firstFamily.diffs ?? [];
    const loadedDiff = diffs.find((diff) => diff.to_project_id === loadedVersion?.project_id) ?? diffs[diffs.length - 1] ?? diffs[0];
    setSelectedDiffId(loadedDiff?.diff_id ?? '');
  }

  function openProjectFamilyTab(familyId: string) {
    const family = portfolioFamilies.find((item) => item.family_id === familyId);
    if (!family) return;
    setOpenProjectTabIds((current) => (current.includes(familyId) ? current : [...current, familyId].slice(-8)));
    setActiveProjectWorkspaceTab(`project:${familyId}`);
    selectPortfolioFamily(familyId, 'overview');
  }

  function focusProjectFamilyTab(familyId: string) {
    setActiveProjectWorkspaceTab(`project:${familyId}`);
    selectPortfolioFamily(familyId, 'overview');
  }

  function closeProjectFamilyTab(familyId: string, event: MouseEvent<HTMLElement>) {
    event.stopPropagation();
    const nextTabs = openProjectTabIds.filter((item) => item !== familyId);
    setOpenProjectTabIds(nextTabs);
    if (activeProjectWorkspaceTab !== `project:${familyId}`) return;
    const replacement = nextTabs[nextTabs.length - 1];
    if (replacement) {
      focusProjectFamilyTab(replacement);
      return;
    }
    setActiveProjectWorkspaceTab('domain');
  }

  function selectPortfolioFamily(familyId: string, tab: DomainPanelTabId = 'builds') {
    const family = portfolioFamilies.find((item) => item.family_id === familyId);
    setSelectedFamilyId(familyId);
    const domainId = family?.domain_id ?? family?.group_id;
    if (domainId) {
      setActivePortfolioGroup(domainId);
      setExpandedDomainId(domainId);
    }
    setDomainPanelTab(tab);
    const versions = family?.versions ?? [];
    const loadedVersion = versions.find((version) => version.is_current) ?? versions[versions.length - 1] ?? versions[0];
    setSelectedVersionId(loadedVersion ? versionKey(loadedVersion) : '');
    const diffs = family?.diffs ?? [];
    const loadedDiff = diffs.find((diff) => diff.to_project_id === loadedVersion?.project_id) ?? diffs[diffs.length - 1] ?? diffs[0];
    setSelectedDiffId(loadedDiff?.diff_id ?? '');
  }

  function selectPortfolioVersion(version: IonProjectPortfolioVersion) {
    setSelectedVersionId(versionKey(version));
    const relatedDiff = selectedFamilyDiffs.find((diff) => diff.to_project_id === version.project_id) ?? selectedFamilyDiffs.find((diff) => diff.from_project_id === version.project_id);
    if (relatedDiff?.diff_id) setSelectedDiffId(relatedDiff.diff_id);
  }

  function selectPortfolioDiff(diff: IonProjectPortfolioDiff) {
    setSelectedDiffId(diff.diff_id ?? '');
    const targetVersion = selectedFamilyVersions.find((version) => version.project_id === diff.to_project_id);
    if (targetVersion) setSelectedVersionId(versionKey(targetVersion));
  }

  function attachFamilyScreenshot(familyId: string, files: FileList | null) {
    const file = files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = () => {
      const value = typeof reader.result === 'string' ? reader.result : '';
      if (!value) return;
      setFamilyScreenshots((current) => ({
        ...current,
        [familyId]: [...(current[familyId] ?? []), value].slice(-6),
      }));
    };
    reader.readAsDataURL(file);
  }

  return (
    <section className={`ion-vnext-workbench-shell ion-project-workbench-shell${hideSubtabs ? ' has-external-subnav' : ''}`} aria-label="Projects mission control">
      {!hideSubtabs ? (
        <nav className="ion-vnext-subtabs" aria-label="Project mission pages">
          {projectMissionTabs.map((tab) => (
            <button className={activeTab === tab.id ? 'is-active' : undefined} key={tab.id} onClick={() => setActiveProjectTab(tab.id)} type="button">
              {tab.label}
            </button>
          ))}
        </nav>
      ) : null}

      <div className="ion-vnext-workbench-grid">
        <aside className="ion-vnext-rail ion-vnext-left-rail" aria-label="Left drawer controls">
          <DrawerIconBar items={leftDrawers} active={leftDrawerOpen ? leftDrawer : undefined} onSelect={selectLeftDrawer} />
        </aside>
        <aside className={`ion-vnext-drawer-panel ion-vnext-left-drawer${leftDrawerOpen ? ' is-open' : ''}`} aria-hidden={!leftDrawerOpen} aria-label="Left drawer">
          <div className="ion-vnext-drawer-head">
            <span>{drawerTitle(leftDrawers, leftDrawer)}</span>
            <button aria-label="Close left drawer" onClick={() => setLeftDrawerOpen(false)} title="Close left drawer" type="button">
              <CloseIcon className="ion-close-icon" />
            </button>
          </div>
          <div className="ion-vnext-drawer-body">{renderLeftDrawer(leftDrawer)}</div>
        </aside>

        <main className="ion-vnext-main-pane">
          <div className="ion-vnext-active-pane">
            {activeTab === 'projects' && renderProjectsPane()}
            {activeTab === 'vnext' && renderVNextPane()}
            {activeTab === 'missions' && renderMissionsPane()}
            {activeTab === 'blockers' && renderBlockersPane()}
            {activeTab === 'questions' && renderQuestionsPane()}
            {activeTab === 'timeline' && renderTimelinePane()}
            {activeTab === 'protocols' && renderProtocolsPane()}
            {activeTab === 'context' && renderContextPane()}
          </div>
        </main>

        <aside className="ion-vnext-rail ion-vnext-right-rail" aria-label="Right drawer controls">
          <DrawerIconBar items={rightDrawers} active={rightDrawerOpen ? rightDrawer : undefined} onSelect={selectRightDrawer} />
        </aside>
        <aside className={`ion-vnext-drawer-panel ion-vnext-right-drawer${rightDrawerOpen ? ' is-open' : ''}`} aria-hidden={!rightDrawerOpen} aria-label="Right drawer">
          <div className="ion-vnext-drawer-head">
            <span>{drawerTitle(rightDrawers, rightDrawer)}</span>
            <button aria-label="Close right drawer" onClick={() => setRightDrawerOpen(false)} title="Close right drawer" type="button">
              <CloseIcon className="ion-close-icon" />
            </button>
          </div>
          <div className="ion-vnext-drawer-body">{renderRightDrawer(rightDrawer)}</div>
        </aside>
      </div>
    </section>
  );

  function renderProjectsPane() {
    if (portfolio) {
      return renderProjectCommandPane();
    }

    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand projectHub />
        {actionMessage && <div className={`ion-vnext-action-banner${actionMessage.includes('failed') || actionMessage.includes('required') ? ' is-blocked' : ''}`}>{actionMessage}</div>}
        <SectionHead icon={<WorkSurfaceIcon />} label="Project Directory" />
        <div className="ion-vnext-project-grid">
          {projects.map((project) => <ProjectCard project={project} key={project.project_id} onOpenVNext={() => setActiveProjectTab('vnext')} />)}
        </div>
        <div className="ion-vnext-map-grid">
          <section className="ion-vnext-map-band">
            <SectionHead icon={<StreamIcon />} label="Project Evolution" />
            <div className="ion-vnext-timeline-stack">
              {timelineEvents.slice(0, 10).map((event) => <TimelineCard event={event} key={event.event_id} />)}
            </div>
          </section>
          <section className="ion-vnext-side-stack">
            <SectionHead icon={<ReceiptIcon />} label="Open Issues" />
            <div className="ion-vnext-blocker-grid is-compact">
              {openBlockers.slice(0, 6).map((blocker) => <BlockerCard blocker={blocker} key={blocker.blocker_id} compact />)}
              {openBlockers.length === 0 && <div className="ion-vnext-empty-inline">NO OPEN BLOCKERS</div>}
            </div>
          </section>
        </div>
      </div>
    );
  }

  function renderProjectCommandPane() {
    if (!portfolio) return null;
    const organization = (projectCockpit?.organization_state ?? {}) as ProjectOrganizationState & Record<string, unknown>;
    const projectSpecialists = (organization.project_specialists ?? {}) as IonProjectSpecialistProjection;
    const organizer = portfolio.organizer ?? {};
    const latestReceipt = (organization.latest_receipt ?? organizer.latest_materialization_receipt ?? {}) as Record<string, unknown>;
    const loadMode = projectCockpit?.portfolio_load_mode ?? projectSummary.portfolio_load_mode ?? portfolio.load_mode ?? organization.load_mode ?? 'fresh_scan';
    const organizationReady = Boolean(organization.materialized_present ?? organizer.materialized_present);
    const specialistReady = projectSpecialists.status === 'project_specialist_contexts_ready';
    const specialistInvocationStatus = projectSpecialists.agent_invocation_status ?? (specialistReady ? 'prepared_not_invoked' : 'missing');
    const selectedDomain = selectedPortfolioDomain ?? ({
      domain_id: selectedPortfolioFamily?.domain_id ?? selectedPortfolioFamily?.group_id ?? 'portfolio',
      label: selectedPortfolioFamily?.domain_label ?? 'Project portfolio',
    } as IonProjectPortfolioDomain);
    const selectedDomainIdForRows = selectedDomain.domain_id;
    const commandDomainFamilies = portfolioFamilies.filter((family) => (family.domain_id ?? family.group_id) === selectedDomainIdForRows);
    const activeDomainFamilies = (commandDomainFamilies.length ? commandDomainFamilies : selectedDomainFamilies).slice().sort((left, right) => {
      const leftFavorite = favoriteFamilies.includes(left.family_id) ? 0 : 1;
      const rightFavorite = favoriteFamilies.includes(right.family_id) ? 0 : 1;
      if (leftFavorite !== rightFavorite) return leftFavorite - rightFavorite;
      const leftRoots = left.project_count ?? 0;
      const rightRoots = right.project_count ?? 0;
      if (leftRoots !== rightRoots) return rightRoots - leftRoots;
      return String(left.label ?? left.family_id).localeCompare(String(right.label ?? right.family_id));
    });
    const domainQuery = portfolioSearch.trim().toLowerCase();
    const domainVisibleFamilies = activeDomainFamilies.filter((family) => {
      if (!domainQuery) return true;
      const haystack = [
        family.label,
        family.family_id,
        family.domain_label,
        family.current_path,
        family.organized_path,
        ...(family.versions ?? []).map((version) => `${version.display_label ?? version.label ?? ''} ${version.path ?? ''} ${version.version_token ?? ''}`),
      ].join(' ').toLowerCase();
      return haystack.includes(domainQuery);
    }).slice(0, 80);
    const domainVersionCount = selectedDomain.version_count ?? activeDomainFamilies.reduce((total, family) => total + Number(family.version_count ?? 0), 0);
    const domainDiffRows = activeDomainFamilies.flatMap((family) => (family.diffs ?? []).map((diff) => ({ family, diff })));
    const domainDiffCount = selectedDomain.diff_count ?? domainDiffRows.length;
    const domainLaunchableCount = selectedDomain.launchable_count ?? activeDomainFamilies.reduce((total, family) => total + Number(family.launchable_count ?? 0), 0);
    const domainDocRows = compactDocRows([
      ...(selectedDomain.docs?.top_docs ?? []),
      ...(selectedDomain.docs?.primary_docs ?? []),
      ...(selectedDomain.docs?.docs ?? []),
      ...activeDomainFamilies.flatMap((family) => [
        ...(family.docs?.primary_docs ?? []),
        ...(family.docs?.docs ?? []),
      ]),
    ]).slice(0, 32);
    const domainDocCount = selectedDomain.doc_count ?? domainDocRows.length;
    const domainOps = selectedDomain.operating_system ?? {};
    const domainNeedles = Array.from(new Set([
      selectedDomain.domain_id,
      selectedDomain.label,
      selectedDomain.folder,
      selectedPortfolioFamily?.family_id,
      selectedPortfolioFamily?.label,
      selectedPortfolioFamily?.current_path,
      ...activeDomainFamilies.slice(0, 50).flatMap((family) => [family.family_id, family.label, family.current_path]),
    ].filter((value): value is string => Boolean(value && String(value).trim().length > 2)).map((value) => value.toLowerCase())));
    const matchesDomain = (values: unknown[]) => {
      if (!domainNeedles.length) return false;
      const haystack = values.map((value) => text(value, '')).join(' ').toLowerCase();
      return domainNeedles.some((needle) => haystack.includes(needle));
    };
    const domainTimelineEvents = timelineEvents.filter((event) => matchesDomain([
      event.project_id,
      event.event_type,
      event.title,
      event.detail,
      event.source,
      event.actor,
      ...(event.evidence_refs ?? []),
    ]));
    const timelineFallback = domainTimelineEvents.length === 0;
    const visibleTimelineEvents = (timelineFallback ? timelineEvents : domainTimelineEvents).slice(0, 24);
    const archiveSessions = runtime.codex_conversation_archive?.sessions ?? [];
    const domainChatSessions = archiveSessions.filter((session) => matchesDomain([
      session.project_key,
      session.project_label,
      session.display_title,
      session.thread_name,
      session.cwd,
      session.session_path,
      session.first_user_snippet,
      session.latest_user_snippet,
      session.latest_assistant_snippet,
      ...(session.mission_labels ?? []).map((item) => item.label),
      ...(session.agent_labels ?? []).map((item) => item.label),
    ])).slice(0, 16);
    const domainChatEvents = timelineEvents.filter((event) => {
      const haystack = [event.event_type, event.title, event.detail, event.source, event.actor].join(' ').toLowerCase();
      return /chat|conversation|codex|session|capsule|agent/.test(haystack) && matchesDomain([event.project_id, event.title, event.detail, event.source, ...(event.evidence_refs ?? [])]);
    }).slice(0, 12);
    const openProjectTabs = openProjectTabIds
      .map((familyId) => portfolioFamilies.find((family) => family.family_id === familyId))
      .filter((family): family is IonProjectPortfolioFamily => Boolean(family));
    const activeProjectFamily = activeProjectWorkspaceTab.startsWith('project:')
      ? portfolioFamilies.find((family) => family.family_id === activeProjectWorkspaceTab.slice('project:'.length)) ?? selectedPortfolioFamily
      : selectedPortfolioFamily;
    const activeProjectVersions = activeProjectFamily?.versions ?? [];
    const activeProjectVersion = activeProjectFamily?.family_id === selectedPortfolioFamily?.family_id
      ? selectedPortfolioVersion
      : activeProjectVersions.find((version) => version.is_current) ?? activeProjectVersions[activeProjectVersions.length - 1] ?? activeProjectVersions[0];
    const activeProjectDiffs = activeProjectFamily?.diffs ?? [];
    const activeProjectDiff = activeProjectFamily?.family_id === selectedPortfolioFamily?.family_id
      ? selectedPortfolioDiff
      : activeProjectDiffs.find((diff) => diff.to_project_id === activeProjectVersion?.project_id) ?? activeProjectDiffs[activeProjectDiffs.length - 1] ?? activeProjectDiffs[0];
    const activeProjectRoots = portfolioProjects.filter((project) => project.family_id === activeProjectFamily?.family_id);
    const activeLaunchRecord = launchRecordForVersion(activeProjectVersion);
    const activeOpenHref = activeLaunchRecord?.open_href ?? activeLaunchRecord?.url;
    const activeLaunchable = Boolean(activeProjectVersion?.launch?.launchable ?? activeProjectVersion?.launchable);
    const activeProjectDocs = compactDocRows([
      ...(activeProjectFamily?.docs?.primary_docs ?? []),
      ...(activeProjectFamily?.docs?.docs ?? []),
      ...(activeProjectVersion?.docs?.docs ?? []),
    ]).slice(0, 18);
    const activeProjectReferences = compactReferences([
      ...(activeProjectFamily?.docs?.references ?? []),
      ...(activeProjectVersion?.docs?.references ?? []),
    ]).slice(0, 12);
    const activeProjectOps = activeProjectFamily?.operating_system ?? {};
    const activeProjectPlanRows = [
      ...(activeProjectOps.lifecycle ?? []).map((row) => ({ kind: 'lifecycle', title: row.label, status: row.status, detail: row.objective })),
      ...(activeProjectOps.maintenance_lanes ?? []).map((row) => ({ kind: 'lane', title: row.label, status: row.status, detail: row.next_action ?? row.objective })),
      ...(activeProjectOps.quality_gates ?? []).map((row) => ({ kind: 'gate', title: row.label, status: row.status, detail: row.evidence })),
      ...(activeProjectOps.next_actions ?? []).map((row) => ({ kind: row.priority ?? 'action', title: row.label, status: row.lane, detail: row.detail })),
      ...(activeProjectOps.human_workflows ?? []).map((row) => ({ kind: row.cadence ?? 'workflow', title: row.label, status: row.output, detail: row.trigger })),
    ];

    const renderDomainHome = () => (
      <div className="ion-project-domain-home">
        <section className="ion-project-domain-project-browser">
          <div className="ion-project-domain-section-head">
            <div>
              <span>internal projects</span>
              <b>{selectedDomain.label ?? selectedDomain.domain_id}</b>
            </div>
            <small>{domainVisibleFamilies.length} visible / {activeDomainFamilies.length} total</small>
          </div>
          <label className="ion-project-search">
            <LensIcon />
            <input value={portfolioSearch} onChange={(event) => setPortfolioSearch(event.target.value)} placeholder="Search this domain" />
          </label>
          <div className="ion-project-domain-project-grid">
            {domainVisibleFamilies.map((family) => (
              <article className={`ion-project-browser-card${openProjectTabIds.includes(family.family_id) ? ' is-open' : ''}${selectedPortfolioFamily?.family_id === family.family_id ? ' is-selected' : ''}`} key={family.family_id}>
                <button className="ion-project-browser-card-main" onClick={() => openProjectFamilyTab(family.family_id)} type="button">
                  <span>{family.domain_label ?? selectedDomain.label ?? 'domain'}</span>
                  <b>{family.label ?? family.family_id}</b>
                  <div className="ion-vnext-packet-meta">
                    <small>{family.project_count ?? 0} roots</small>
                    <small>{family.version_count ?? 0} versions</small>
                    <small>{family.diff_count ?? 0} diffs</small>
                    <small>{family.launchable_count ?? 0} launch</small>
                    <small>{family.doc_count ?? 0} docs</small>
                    <small>{specialistReady ? '5 agents' : 'agents missing'}</small>
                  </div>
                  <code>{family.current_path ?? family.organized_path ?? family.family_id}</code>
                </button>
                <div className="ion-project-browser-card-actions">
                  <button onClick={() => openProjectFamilyTab(family.family_id)} type="button">Details Tab</button>
                  <a href={projectFamilyHref(family)} target="_blank" rel="noreferrer">Canon</a>
                  <button aria-pressed={favoriteFamilies.includes(family.family_id)} onClick={() => toggleFavoriteFamily(family.family_id)} type="button">
                    {favoriteFamilies.includes(family.family_id) ? 'Saved' : 'Save'}
                  </button>
                </div>
              </article>
            ))}
            {activeDomainFamilies.length > domainVisibleFamilies.length && <div className="ion-vnext-empty-inline">{activeDomainFamilies.length - domainVisibleFamilies.length} DOMAIN PROJECTS FILTERED</div>}
            {domainVisibleFamilies.length === 0 && <div className="ion-vnext-empty-inline">NO MATCHING PROJECTS IN DOMAIN</div>}
          </div>
        </section>
        <aside className="ion-project-domain-side">
          <section>
            <div className="ion-runtime-card-head"><span>domain</span><b>{selectedDomain.label ?? selectedDomain.domain_id}</b></div>
            <p>{selectedDomain.summary ?? 'Project domain'}</p>
            <div className="ion-project-domain-mini-metrics">
              <Metric label="projects" value={String(activeDomainFamilies.length)} tone="ready" />
              <Metric label="versions" value={String(domainVersionCount)} tone="watch" />
              <Metric label="diffs" value={String(domainDiffCount)} tone="active" />
              <Metric label="docs" value={String(domainDocCount)} tone="active" />
              <Metric label="launch" value={String(domainLaunchableCount)} tone="ready" />
            </div>
            <PathRow label="domain folder" value={selectedDomain.folder ?? selectedDomain.domain_id} />
            <PathRow label="organized domain" value={`${organizer.materialized_root ?? organization.materialized_root ?? ''}/domains/${selectedDomain.folder ?? selectedDomain.domain_id}`} />
          </section>
          <section className={`ion-project-specialist-panel${specialistReady ? ' is-ready' : ' is-missing'}`}>
            <div className="ion-runtime-card-head"><span>domain specialists</span><b>{specialistReady ? 'ready' : 'missing'}</b></div>
            <div className="ion-project-capsule-proof">
              <PathRow label="domain capsules" value={projectSpecialists.domain_specialist_capsule_count ?? 0} />
              <PathRow label="domain packets" value={projectSpecialists.domain_agent_packet_count ?? 0} />
              <PathRow label="packet status" value={specialistInvocationStatus} />
            </div>
            <SpecialistLaneList lanes={domainSpecialistLanes} packetStatus={specialistInvocationStatus} />
          </section>
          <section>
            <div className="ion-runtime-card-head"><span>recent timeline</span><b>{visibleTimelineEvents.length}</b></div>
            <div className="ion-vnext-timeline-stack">
              {visibleTimelineEvents.slice(0, 6).map((event) => <TimelineCard event={event} key={event.event_id} />)}
              {visibleTimelineEvents.length === 0 && <div className="ion-vnext-empty-inline">NO TIMELINE EVENTS PROJECTED</div>}
            </div>
          </section>
          <section>
            <div className="ion-runtime-card-head"><span>domain docs</span><b>{domainDocRows.length}</b></div>
            <DocRowList docs={domainDocRows.slice(0, 6)} emptyLabel="NO DOMAIN DOCS PROJECTED" />
          </section>
        </aside>
      </div>
    );

    const renderProjectDetailTab = () => {
      if (!activeProjectFamily) return <div className="ion-vnext-empty-inline">NO PROJECT TAB SELECTED</div>;
      return (
        <div className="ion-project-full-detail">
          <header className="ion-project-full-detail-head">
            <div>
              <span>{activeProjectFamily.domain_label ?? selectedDomain.label ?? 'domain'}</span>
              <b>{activeProjectFamily.label ?? activeProjectFamily.family_id}</b>
              <p>{activeProjectFamily.materialization_plan ?? 'Project source, preview, versions, diffs, docs, chats, plans, and organization state.'}</p>
            </div>
            <div className="ion-project-full-detail-actions">
              <a href={projectFamilyHref(activeProjectFamily)} target="_blank" rel="noreferrer"><LensIcon /> Canon</a>
              <a href={`${projectFamilyHref(activeProjectFamily)}.json`} target="_blank" rel="noreferrer"><SourceIcon /> JSON</a>
              {activeOpenHref && <a href={activeOpenHref} target="_blank" rel="noreferrer"><StreamIcon /> Preview</a>}
              <button disabled={!activeLaunchable || !activeProjectVersion || launchBusyKey === launchKeyForVersion(activeProjectVersion)} onClick={() => startProjectVersion(activeProjectVersion, activeProjectFamily)} type="button">
                <WorkSurfaceIcon /> {activeLaunchRecord?.running ? 'Open Running' : 'Repair & Launch'}
              </button>
            </div>
          </header>
          <div className="ion-project-detail-grid">
            <PathRow label="current source" value={activeProjectFamily.current_path} />
            <PathRow label="organized project" value={organizedProjectPath(activeProjectFamily, selectedDomain, String(organization.materialized_root ?? organizer.materialized_root ?? ''))} />
            <PathRow label="current version" value={activeProjectVersion?.display_label ?? activeProjectVersion?.label ?? activeProjectVersion?.version_id} />
            <PathRow label="active capsule" value={`${organizedProjectPath(activeProjectFamily, selectedDomain, String(organization.materialized_root ?? organizer.materialized_root ?? ''))}/.ion/ACTIVE_CONTEXT_PACKAGE.md`} />
          </div>
          <div className="ion-project-full-detail-grid">
            <section className={`ion-project-detail-panel ion-project-specialist-panel is-project${specialistReady ? ' is-ready' : ' is-missing'}`}>
              <div className="ion-runtime-card-head"><span>specialist agents</span><b>{projectSpecialistLanes.length}</b></div>
              <div className="ion-project-capsule-proof">
                <PathRow label="project capsules" value={projectSpecialists.project_specialist_capsule_count ?? 0} />
                <PathRow label="project packets" value={projectSpecialists.project_agent_packet_count ?? 0} />
                <PathRow label="packet status" value={specialistInvocationStatus} />
                <PathRow label="context capsule" value=".ion/ION_CONTEXT_CAPSULE.yaml" />
              </div>
              <SpecialistLaneList lanes={projectSpecialistLanes} packetStatus={specialistInvocationStatus} />
            </section>
            <section className="ion-project-detail-panel is-launch">
              <ProjectLaunchPanel version={activeProjectVersion} family={activeProjectFamily} />
            </section>
            <section className="ion-project-detail-panel">
              <LoadedVersionPanel version={activeProjectVersion} diff={activeProjectDiff} />
            </section>
            <section className="ion-project-detail-panel">
              <DenseDiffPanel diff={activeProjectDiff} version={activeProjectVersion} />
            </section>
            <section className="ion-project-detail-panel">
              <div className="ion-runtime-card-head"><span>versions</span><b>{activeProjectVersions.length}</b></div>
              <div className="ion-project-version-timeline">
                {activeProjectVersions.map((version, index) => (
                  <ProjectVersionRow version={version} index={index} key={versionKey(version)} selected={versionKey(version) === versionKey(activeProjectVersion)} onSelect={() => selectPortfolioVersion(version)} />
                ))}
                {activeProjectVersions.length === 0 && <div className="ion-vnext-empty-inline">NO VERSION ROOTS PROJECTED</div>}
              </div>
            </section>
            <section className="ion-project-detail-panel">
              <DiffDetailPanel diff={activeProjectDiff} version={activeProjectVersion} />
            </section>
            <section className="ion-project-detail-panel">
              <div className="ion-runtime-card-head"><span>docs</span><b>{activeProjectDocs.length}</b></div>
              <DocRowList docs={activeProjectDocs} emptyLabel="NO PROJECT DOCS PROJECTED" />
              <ReferenceList references={activeProjectReferences} />
            </section>
            <section className="ion-project-detail-panel">
              <div className="ion-runtime-card-head"><span>chats</span><b>{domainChatSessions.length + domainChatEvents.length}</b></div>
              <div className="ion-project-chat-list">
                {domainChatSessions.slice(0, 8).map((session) => (
                  <article className="ion-project-chat-row" key={session.session_id}>
                    <span>{session.updated_at ?? session.created_at ?? 'session'}</span>
                    <b>{session.display_title ?? session.thread_name ?? session.project_label ?? session.session_id}</b>
                    <p>{session.latest_user_snippet ?? session.first_user_snippet ?? session.latest_assistant_snippet ?? ''}</p>
                    <code>{session.cwd ?? session.session_path ?? session.session_id}</code>
                  </article>
                ))}
                {domainChatSessions.length === 0 && <div className="ion-vnext-empty-inline">NO PROJECT CHAT ATTACHMENT INDEXED YET</div>}
              </div>
              <div className="ion-project-detail-grid">
                <PathRow label="archive sessions" value={runtime.codex_conversation_archive?.source_counts?.session_files_total ?? 0} />
                <PathRow label="attachment status" value={domainChatSessions.length ? 'matched by domain/project signal' : 'project binding pending'} />
              </div>
            </section>
            <section className="ion-project-detail-panel">
              <div className="ion-runtime-card-head"><span>plans</span><b>{activeProjectPlanRows.length}</b></div>
              <div className="ion-project-plan-list">
                {activeProjectPlanRows.map((row, index) => (
                  <article className={`ion-project-plan-row is-${statusClass(row.status)}`} key={`${row.kind}-${row.title}-${index}`}>
                    <span>{row.kind}</span>
                    <b>{row.title ?? 'project plan'}</b>
                    <p>{row.detail ?? row.status ?? ''}</p>
                  </article>
                ))}
                {activeProjectPlanRows.length === 0 && <div className="ion-vnext-empty-inline">NO PROJECT PLAN ROWS PROJECTED</div>}
              </div>
            </section>
            <section className="ion-project-detail-panel">
              <RecordList title="project roots" records={activeProjectRoots} primary="label" secondary="stack" />
            </section>
            <section className="ion-project-detail-panel is-wide">
              <ProjectOrganizerPanel domain={selectedDomain} domainFamilies={activeDomainFamilies} />
            </section>
            <section className="ion-project-detail-panel is-wide">
              <ProjectAnnotationPanel />
            </section>
          </div>
        </div>
      );
    };

    return (
      <div className="ion-project-page-shell is-drawer-tabbed">
        <section className="ion-project-domain-shell-head" aria-label="Project domain page">
          <div>
            <span>domain page</span>
            <b>{selectedDomain.label ?? selectedDomain.domain_id}</b>
            <small>{activeDomainFamilies.length} projects / {domainVersionCount} versions / {domainDiffCount} diffs / {domainDocCount} docs</small>
          </div>
          <div className="ion-project-domain-shell-actions">
            <button onClick={() => { setLeftDrawer('projects'); setLeftDrawerOpen(true); }} type="button"><ProjectsIcon /> Domains</button>
            <a href="/projects" target="_blank" rel="noreferrer"><ProjectsIcon /> Public Canon</a>
            <button disabled={organizerBusy} onClick={materializePortfolioOrganizer} type="button"><RouteIcon /> {organizerBusy ? 'Syncing' : 'Sync Organizer'}</button>
          </div>
        </section>
        <div className="ion-project-action-slot">
          {actionMessage && <div className={`ion-vnext-action-banner${actionMessage.includes('failed') || actionMessage.includes('required') ? ' is-blocked' : ''}`}>{actionMessage}</div>}
        </div>
        <nav className="ion-project-workspace-tabbar" aria-label="Open project tabs">
          <button className={activeProjectWorkspaceTab === 'domain' ? 'is-active' : undefined} onClick={() => setActiveProjectWorkspaceTab('domain')} type="button">
            <span>Domain</span>
            <b>{activeDomainFamilies.length}</b>
          </button>
          {openProjectTabs.map((family) => (
            <button className={activeProjectWorkspaceTab === `project:${family.family_id}` ? 'is-active' : undefined} key={family.family_id} onClick={() => focusProjectFamilyTab(family.family_id)} type="button">
              <span>{family.label ?? family.family_id}</span>
              <b>{family.version_count ?? 0}</b>
              <i onClick={(event) => closeProjectFamilyTab(family.family_id, event)}>x</i>
            </button>
          ))}
          {openProjectTabs.length === 0 && <small>Click a project to open its detail tab</small>}
        </nav>
        <div className="ion-project-tab-page">
          {activeProjectWorkspaceTab === 'domain' ? renderDomainHome() : renderProjectDetailTab()}
        </div>
      </div>
    );
  }
  function renderExpandedDomainPanel(domain: IonProjectPortfolioDomain, domainFamilies: IonProjectPortfolioFamily[]) {
    if (!portfolio) return null;
    const activeFamily = domainFamilies.find((family) => family.family_id === selectedPortfolioFamily?.family_id) ?? domainFamilies[0];
    const activeFamilyProjects = portfolioProjects.filter((project) => project.family_id === activeFamily?.family_id);
    const domainVersionCount = domainFamilies.reduce((total, family) => total + Number(family.version_count ?? 0), 0);
    const domainBranchCount = domainFamilies.reduce((total, family) => total + Number(family.branch_count ?? 0), 0);
    const domainDiffCount = domainFamilies.reduce((total, family) => total + Number(family.diff_count ?? 0), 0);
    const domainLaunchableCount = domainFamilies.reduce((total, family) => total + Number(family.launchable_count ?? 0), 0);
    const domainDocCount = domain.doc_count ?? domainFamilies.reduce((total, family) => total + Number(family.doc_count ?? 0), 0);
    return (
      <div className="ion-project-domain-expanded-panel">
        <nav className="ion-project-domain-panel-tabs" aria-label={`${domain.label ?? domain.domain_id} domain views`}>
          {domainPanelTabs.map((tab) => (
            <button className={domainPanelTab === tab.id ? 'is-active' : undefined} key={tab.id} onClick={() => setDomainPanelTab(tab.id)} type="button">
              {tab.label}
            </button>
          ))}
        </nav>
        {domainPanelTab === 'overview' && (
          <div className="ion-project-domain-panel-body">
            <div className="ion-project-domain-overview-strip">
              <Metric label="projects" value={String(domainFamilies.length)} tone="ready" />
              <Metric label="versions" value={String(domainVersionCount)} tone="watch" />
              <Metric label="branches" value={String(domainBranchCount)} tone="active" />
              <Metric label="diffs" value={String(domainDiffCount)} tone="watch" />
              <Metric label="launchers" value={String(domainLaunchableCount)} tone="ready" />
              <Metric label="docs" value={String(domainDocCount)} tone="active" />
            </div>
            <div className="ion-project-domain-panel-grid">
              <section className="ion-project-family-detail">
                <div className="ion-runtime-card-head"><span>domain intelligence</span><b>{domain.label ?? domain.domain_id}</b></div>
                <p>{domain.summary ?? 'Project domain'}</p>
                <div className="ion-project-detail-grid">
                  <PathRow label="domain folder" value={domain.folder} />
                  <PathRow label="organized root" value={portfolio.organizer?.materialized_root} />
                  <PathRow label="copy policy" value={portfolio.organizer?.source_copy_policy} />
                </div>
                <div className="ion-project-recommendation-stack">
                  {(portfolio.recommendations ?? []).slice(0, 4).map((recommendation) => (
                    <article className={`ion-project-recommendation is-${statusClass(recommendation.status)}`} key={`${domain.domain_id}-${recommendation.title}-${recommendation.family_id ?? ''}`}>
                      <span>{recommendation.status ?? 'candidate'}</span>
                      <b>{recommendation.title ?? 'Organizer step'}</b>
                      <p>{recommendation.detail ?? recommendation.family_id ?? ''}</p>
                    </article>
                  ))}
                </div>
              </section>
              <section className="ion-vnext-side-stack">
                <div className="ion-runtime-card-head"><span>internal builds</span><b>{domainFamilies.length}</b></div>
                <div className="ion-project-domain-project-list">
                  {domainFamilies.map((family) => (
                    <ProjectDomainProjectCard
                      family={family}
                      key={family.family_id}
                      selected={activeFamily?.family_id === family.family_id}
                      onSelect={() => selectPortfolioFamily(family.family_id, 'builds')}
                    />
                  ))}
                  {domainFamilies.length === 0 && <div className="ion-vnext-empty-inline">NO BUILDS IN THIS DOMAIN</div>}
                </div>
              </section>
            </div>
          </div>
        )}
        {domainPanelTab === 'builds' && (
          <div className="ion-project-domain-panel-body">
            <SelectedFamilyHeader family={activeFamily} domain={domain} />
            <div className="ion-project-split-pane">
              <div className="ion-project-family-detail">
                <div className="ion-project-domain-project-list is-inline">
                  {domainFamilies.map((family) => (
                    <ProjectDomainProjectCard
                      family={family}
                      key={family.family_id}
                      selected={activeFamily?.family_id === family.family_id}
                      onSelect={() => selectPortfolioFamily(family.family_id, 'builds')}
                    />
                  ))}
                </div>
                <div className="ion-project-detail-grid">
                  <PathRow label="domain" value={activeFamily?.domain_label ?? domain.label} />
                  <PathRow label="current source" value={activeFamily?.current_path} />
                  <PathRow label="organized project" value={organizedProjectPath(activeFamily, domain, portfolio.organizer?.materialized_root)} />
                </div>
                <BranchStrip family={activeFamily} />
                <RecordList title="subprojects and roots" records={activeFamilyProjects} primary="label" secondary="stack" />
              </div>
              <div className="ion-project-annotation-panel">
                <LoadedVersionPanel version={selectedPortfolioVersion} diff={selectedPortfolioDiff} />
                <ProjectLaunchPanel version={selectedPortfolioVersion} family={activeFamily} />
                <ProjectAnnotationPanel />
              </div>
            </div>
          </div>
        )}
        {domainPanelTab === 'changes' && (
          <div className="ion-project-domain-panel-body">
            <SelectedFamilyHeader family={activeFamily} domain={domain} />
            <div className="ion-project-lineage-grid is-three">
              <div className="ion-project-version-timeline is-full">
                <div className="ion-runtime-card-head"><span>versions</span><b>{selectedFamilyVersions.length}</b></div>
                {selectedFamilyVersions.map((version, index) => (
                  <ProjectVersionRow
                    version={version}
                    index={index}
                    key={versionKey(version)}
                    selected={versionKey(version) === versionKey(selectedPortfolioVersion)}
                    onSelect={() => selectPortfolioVersion(version)}
                  />
                ))}
                {(activeFamily?.versions ?? []).length === 0 && <div className="ion-vnext-empty-inline">NO VERSION ROOTS PROJECTED</div>}
              </div>
              <div className="ion-project-diff-list">
                <div className="ion-runtime-card-head"><span>diffs / changes</span><b>{selectedFamilyDiffs.length}</b></div>
                {selectedFamilyDiffs.map((diff) => (
                  <ProjectDiffRow
                    diff={diff}
                    key={diff.diff_id ?? `${diff.from_project_id}-${diff.to_project_id}`}
                    selected={diff.diff_id === selectedPortfolioDiff?.diff_id}
                    onSelect={() => selectPortfolioDiff(diff)}
                  />
                ))}
                {selectedFamilyDiffs.length === 0 && <div className="ion-vnext-empty-inline">NO DIFF UNITS PROJECTED</div>}
              </div>
              <DiffDetailPanel diff={selectedPortfolioDiff} version={selectedPortfolioVersion} />
            </div>
          </div>
        )}
        {domainPanelTab === 'ops' && (
          <div className="ion-project-domain-panel-body">
            <SelectedFamilyHeader family={activeFamily} domain={domain} />
            <ProjectOpsPanel domain={domain} family={activeFamily} version={selectedPortfolioVersion} domainFamilies={domainFamilies} />
          </div>
        )}
        {domainPanelTab === 'docs' && (
          <div className="ion-project-domain-panel-body">
            <SelectedFamilyHeader family={activeFamily} domain={domain} />
            <ProjectDocsPanel domain={domain} family={activeFamily} version={selectedPortfolioVersion} domainFamilies={domainFamilies} />
          </div>
        )}
        {domainPanelTab === 'workspace' && (
          <div className="ion-project-domain-panel-body">
            <ProjectOrganizerPanel domain={domain} domainFamilies={domainFamilies} />
            <div className="ion-project-detail-grid">
              <PathRow label="domain folder" value={`${portfolio.organizer?.materialized_root ?? ''}/domains/${domain.folder ?? domain.domain_id}`} />
              <PathRow label="portfolio manifest" value={portfolio.organizer?.manifest_path} />
              <PathRow label="copy policy" value={portfolio.organizer?.source_copy_policy} />
            </div>
            <div className="ion-project-split-pane">
              <RecordList title="domain project workspaces" records={domainFamilies} primary="label" secondary="version_count" />
              <RecordList title="source roots" records={Object.entries(portfolio.source_roots ?? {}).map(([label, path]) => ({ label, path, status: portfolio.source_present?.[label] ? 'present' : 'missing' }))} primary="label" secondary="status" />
            </div>
          </div>
        )}
      </div>
    );
  }

  function ProjectOrganizerPanel({ domain, domainFamilies }: { domain: IonProjectPortfolioDomain; domainFamilies: IonProjectPortfolioFamily[] }) {
    if (!portfolio) return null;
    const organizer = portfolio.organizer ?? {};
    const resultSummary = organizerResult?.portfolio_summary as Record<string, unknown> | undefined;
    const latestReceipt = (organizerResult?.latest_receipt as Record<string, unknown> | undefined) ?? organizer.latest_materialization_receipt;
    const resultOk = organizerResult?.ok;
    const domainLaunchable = domainFamilies.reduce((total, family) => total + Number(family.launchable_count ?? 0), 0);
    const domainVersioned = domainFamilies.filter((family) => Number(family.version_count ?? 0) > 1).length;
    return (
      <section className={`ion-project-organizer-panel${resultOk === false ? ' is-blocked' : resultOk ? ' is-ready' : ''}`}>
        <div className="ion-project-organizer-head">
          <div>
            <span>candidate organizer control</span>
            <b>{organizer.materialized_present ? 'professional workspace ready' : 'organizer pending'}</b>
            <p>{organizer.layout ?? 'domains/<domain>/<project>/source/current plus lineage, notes, screenshots, and docs'}</p>
          </div>
          <button disabled={organizerBusy} onClick={materializePortfolioOrganizer} type="button">
            {organizerBusy ? 'Synchronizing' : 'Reconcile Now'}
          </button>
        </div>
        <div className="ion-project-organizer-metrics">
          <Metric label="domain projects" value={String(domainFamilies.length)} tone="ready" />
          <Metric label="versioned" value={String(domainVersioned)} tone="watch" />
          <Metric label="launchable" value={String(domainLaunchable)} tone="ready" />
          <Metric label="all roots" value={String(resultSummary?.project_root_count ?? portfolio.summary?.project_root_count ?? 0)} tone="active" />
          <Metric label="families" value={String(resultSummary?.family_count ?? portfolio.summary?.family_count ?? 0)} tone="ready" />
        </div>
        <div className="ion-project-detail-grid">
          <PathRow label="materialized root" value={organizer.materialized_root} />
          <PathRow label="domain workspace" value={`${organizer.materialized_root ?? ''}/domains/${domain.folder ?? domain.domain_id}`} />
          <PathRow label="latest receipt" value={String(latestReceipt?.relpath ?? latestReceipt?.path ?? '')} />
        </div>
        {latestReceipt && (
          <div className="ion-project-organizer-proof">
            <span>latest materialization proof</span>
            <b>{String(latestReceipt.created_at ?? 'receipt ready')}</b>
            <p>{String(latestReceipt.copy_count ?? 0)} family workspaces reconciled under {String(latestReceipt.target ?? organizer.materialized_root ?? 'organizer root')}</p>
          </div>
        )}
        <div className="ion-vnext-packet-meta">
          <small>originals untouched</small>
          <small>candidate only</small>
          <small>no accepted state</small>
          <small>no production authority</small>
        </div>
      </section>
    );
  }

  function SelectedFamilyHeader({ family = selectedPortfolioFamily, domain = selectedPortfolioDomain }: { family?: IonProjectPortfolioFamily; domain?: IonProjectPortfolioDomain } = {}) {
    if (!family) return <div className="ion-vnext-empty-inline">NO PROJECT SELECTED</div>;
    return (
      <div className="ion-project-family-head">
        <div>
          <span>{family.domain_label ?? domain?.label ?? 'project domain'}</span>
          <b>{family.label ?? family.family_id}</b>
          <p>{family.materialization_plan ?? 'Current source, version lineage, and candidate organizer state.'}</p>
        </div>
        <button className={favoriteFamilies.includes(family.family_id) ? 'is-active' : undefined} onClick={() => toggleFavoriteFamily(family.family_id)} type="button">
          {favoriteFamilies.includes(family.family_id) ? 'Favorited' : 'Favorite'}
        </button>
      </div>
    );
  }

  function ProjectAnnotationPanel() {
    if (!selectedPortfolioFamily) return <div className="ion-vnext-empty-inline">NO PROJECT SELECTED</div>;
    const familyId = selectedPortfolioFamily.family_id;
    const versionId = selectedPortfolioVersion ? versionKey(selectedPortfolioVersion) : '';
    const projectNoteKey = `project:${familyId}`;
    const legacyProjectNoteKey = familyId;
    const versionNoteKey = versionId ? `version:${familyId}:${versionId}` : projectNoteKey;
    const projectScreenshotKey = `project:${familyId}`;
    const versionScreenshotKey = versionId ? `version:${familyId}:${versionId}` : projectScreenshotKey;
    const projectScreenshots = familyScreenshots[projectScreenshotKey] ?? familyScreenshots[familyId] ?? [];
    const versionScreenshots = familyScreenshots[versionScreenshotKey] ?? [];
    return (
      <div className="ion-project-annotation-fields">
        <div className="ion-project-notes-panel">
          <div className="ion-runtime-card-head"><span>project notes</span><b>{selectedPortfolioFamily.label ?? familyId}</b></div>
          <textarea
            value={familyNotes[projectNoteKey] ?? familyNotes[legacyProjectNoteKey] ?? ''}
            onChange={(event) => setFamilyNotes((current) => ({ ...current, [projectNoteKey]: event.target.value }))}
            placeholder="Notes for this project"
          />
          <div className="ion-runtime-card-head"><span>loaded version notes</span><b>{selectedPortfolioVersion?.sequence_label ?? 'version'}</b></div>
          <textarea
            value={familyNotes[versionNoteKey] ?? ''}
            onChange={(event) => setFamilyNotes((current) => ({ ...current, [versionNoteKey]: event.target.value }))}
            placeholder="Notes for the loaded version"
          />
        </div>
        <div className="ion-project-screens-panel">
          <div className="ion-runtime-card-head"><span>project screenshots</span><b>{projectScreenshots.length}</b></div>
          <label className="ion-project-file-attach">
            <input accept="image/*" onChange={(event) => attachFamilyScreenshot(projectScreenshotKey, event.target.files)} type="file" />
            Attach screenshot
          </label>
          <div className="ion-project-shot-grid">
            {projectScreenshots.map((image, index) => (
              <img alt={`${selectedPortfolioFamily.label ?? 'project'} screenshot ${index + 1}`} key={`${image.slice(0, 36)}-${index}`} src={image} />
            ))}
          </div>
          <div className="ion-runtime-card-head"><span>version screenshots</span><b>{versionScreenshots.length}</b></div>
          <label className="ion-project-file-attach">
            <input accept="image/*" onChange={(event) => attachFamilyScreenshot(versionScreenshotKey, event.target.files)} type="file" />
            Attach screenshot
          </label>
          <div className="ion-project-shot-grid">
            {versionScreenshots.map((image, index) => (
              <img alt={`${selectedPortfolioVersion?.display_label ?? selectedPortfolioFamily.label ?? 'version'} screenshot ${index + 1}`} key={`${image.slice(0, 36)}-${index}`} src={image} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  function ProjectOpsPanel({
    domain,
    family,
    version,
    domainFamilies,
  }: {
    domain: IonProjectPortfolioDomain;
    family?: IonProjectPortfolioFamily;
    version?: IonProjectPortfolioVersion;
    domainFamilies: IonProjectPortfolioFamily[];
  }) {
    const domainOps = domain.operating_system ?? {};
    const familyOps = family?.operating_system ?? {};
    const record = launchRecordForVersion(version);
    return (
      <div className="ion-project-ops-layout">
        <section className={`ion-project-ops-hero is-${statusClass(domainOps.posture)}`}>
          <div>
            <span>project operating system</span>
            <b>{domain.label ?? domain.domain_id}</b>
            <p>Human workflow, Codex/GPT action sync, managed local launch, diagnostics, screenshots, edit lanes, rollback posture, docs, and version lineage in one domain-attached system.</p>
          </div>
          <Metric label="domain score" value={String(domainOps.average_readiness_score ?? 0)} tone="active" />
          <Metric label="ready" value={String(domainOps.ready_count ?? 0)} tone="ready" />
          <Metric label="watch" value={String(domainOps.watch_count ?? 0)} tone="watch" />
          <Metric label="blocked" value={String(domainOps.blocked_count ?? 0)} tone="blocked" />
        </section>
        <div className="ion-project-ops-grid">
          <section className="ion-project-ops-panel is-board">
            <div className="ion-runtime-card-head"><span>domain command board</span><b>{domainFamilies.length}</b></div>
            <div className="ion-project-ops-board">
              {(domainOps.board_columns ?? []).map((column) => (
                <div className="ion-project-ops-column" key={column.column_id ?? column.label}>
                  <div className="ion-runtime-card-head"><span>{column.label ?? 'lane'}</span><b>{column.count ?? 0}</b></div>
                  {(column.families ?? []).slice(0, 6).map((item) => (
                    <button className="ion-project-ops-family-chip" key={`${column.column_id}-${item.family_id}`} onClick={() => item.family_id && selectPortfolioFamily(item.family_id, 'ops')} type="button">
                      <b>{item.label ?? item.family_id}</b>
                      <small>{typeof item.score === 'number' ? `${item.score}%` : `${item.count ?? 0}`}</small>
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </section>
          <section className="ion-project-ops-panel">
            <div className="ion-runtime-card-head"><span>selected project system</span><b>{familyOps.readiness_score ?? 0}%</b></div>
            <div className="ion-project-ops-score">
              <span>{familyOps.posture ?? 'unknown'}</span>
              <b>{family?.label ?? family?.family_id ?? 'project'}</b>
            </div>
            <OpsLifecycle lifecycle={familyOps.lifecycle ?? []} />
          </section>
          <section className="ion-project-ops-panel">
            <div className="ion-runtime-card-head"><span>ai sync / action plane</span><b>{record?.running ? 'live' : 'idle'}</b></div>
            <AiSyncPlane version={version} record={record} />
          </section>
          <section className="ion-project-ops-panel">
            <div className="ion-runtime-card-head"><span>maintenance lanes</span><b>{familyOps.maintenance_lanes?.length ?? 0}</b></div>
            <OpsLaneList lanes={familyOps.maintenance_lanes ?? []} />
          </section>
          <section className="ion-project-ops-panel">
            <div className="ion-runtime-card-head"><span>quality gates</span><b>{familyOps.quality_gates?.length ?? 0}</b></div>
            <OpsGateList gates={familyOps.quality_gates ?? []} />
          </section>
          <section className="ion-project-ops-panel">
            <div className="ion-runtime-card-head"><span>risk register</span><b>{familyOps.risk_register?.length ?? 0}</b></div>
            <OpsRiskList risks={familyOps.risk_register ?? []} />
          </section>
          <section className="ion-project-ops-panel is-wide">
            <div className="ion-runtime-card-head"><span>human engineering workflow</span><b>{familyOps.human_workflows?.length ?? 0}</b></div>
            <OpsWorkflowList workflows={familyOps.human_workflows ?? []} />
          </section>
        </div>
      </div>
    );
  }

  function AiSyncPlane({ version, record }: { version?: IonProjectPortfolioVersion; record?: IonProjectLauncherRecord }) {
    const diagnostics = record?.launch_id ? launchDiagnostics[record.launch_id] : undefined;
    const screenshot = diagnostics?.screenshot as Record<string, unknown> | undefined;
    const launchable = Boolean(version?.launch?.launchable ?? version?.launchable);
    return (
      <div className="ion-project-ai-sync-plane">
        <div className="ion-project-ai-sync-flow">
          <div className={`ion-project-ai-sync-node is-${launchable ? 'ready' : 'watch'}`}><span>01</span><b>Launch</b></div>
          <div className={`ion-project-ai-sync-node is-${record?.running ? 'ready' : 'watch'}`}><span>02</span><b>Preview</b></div>
          <div className={`ion-project-ai-sync-node is-${screenshot?.ok ? 'ready' : 'watch'}`}><span>03</span><b>Screenshot</b></div>
          <div className="ion-project-ai-sync-node is-watch"><span>04</span><b>Edit</b></div>
          <div className="ion-project-ai-sync-node is-watch"><span>05</span><b>Rollback</b></div>
        </div>
        <div className="ion-project-ai-sync-actions">
          <button disabled={!launchable || Boolean(record?.running)} onClick={() => startProjectVersion(version, selectedPortfolioFamily)} type="button">Launch</button>
          <button disabled={!record?.running || launchBusyKey === `diagnostics:${record?.launch_id}`} onClick={() => captureProjectLaunchDiagnostics(record)} type="button">Capture</button>
          {record?.open_href && <a href={record.open_href} target="_blank" rel="noreferrer">Preview</a>}
        </div>
        <PathRow label="codex/gpt shared target" value={record?.url ?? version?.path} />
        <PathRow label="screenshot proof" value={screenshot?.screenshot_path} />
        <PathRow label="edit/rollback lane" value="bounded patch preview and rollback surfaces are projected through project workbench lanes" />
      </div>
    );
  }

  function OpsLifecycle({ lifecycle }: { lifecycle: NonNullable<IonProjectOperatingSystem['lifecycle']> }) {
    return (
      <div className="ion-project-ops-lifecycle">
        {lifecycle.map((stage) => (
          <div className={`ion-project-ops-stage is-${statusClass(stage.status)}`} key={stage.stage_id ?? stage.label}>
            <span>{stage.status ?? 'watch'}</span>
            <b>{stage.label ?? 'stage'}</b>
            <p>{stage.objective ?? ''}</p>
          </div>
        ))}
      </div>
    );
  }

  function OpsLaneList({ lanes }: { lanes: NonNullable<IonProjectOperatingSystem['maintenance_lanes']> }) {
    return (
      <div className="ion-project-ops-list">
        {lanes.map((lane) => (
          <div className={`ion-project-ops-row is-${statusClass(lane.status)}`} key={lane.lane_id ?? lane.label}>
            <span>{lane.status ?? 'watch'}</span>
            <b>{lane.label ?? 'lane'}</b>
            <p>{lane.objective ?? ''}</p>
            <code>{lane.next_action ?? ''}</code>
          </div>
        ))}
      </div>
    );
  }

  function OpsGateList({ gates }: { gates: NonNullable<IonProjectOperatingSystem['quality_gates']> }) {
    return (
      <div className="ion-project-ops-list">
        {gates.map((gate) => (
          <div className={`ion-project-ops-row is-${gate.status === 'pass' ? 'ready' : 'watch'}`} key={gate.gate_id ?? gate.label}>
            <span>{gate.status ?? 'gate'}</span>
            <b>{gate.label ?? 'gate'}</b>
            <code>{gate.evidence ?? ''}</code>
          </div>
        ))}
      </div>
    );
  }

  function OpsRiskList({ risks }: { risks: NonNullable<IonProjectOperatingSystem['risk_register']> }) {
    if (!risks.length) return <div className="ion-vnext-empty-inline">NO PROJECT RISKS PROJECTED</div>;
    return (
      <div className="ion-project-ops-list">
        {risks.map((risk) => (
          <div className={`ion-project-ops-row is-${risk.severity === 'high' ? 'blocked' : 'watch'}`} key={risk.risk_id ?? risk.title}>
            <span>{risk.severity ?? 'risk'}</span>
            <b>{risk.title ?? 'risk'}</b>
            <p>{risk.mitigation ?? ''}</p>
          </div>
        ))}
      </div>
    );
  }

  function OpsWorkflowList({ workflows }: { workflows: NonNullable<IonProjectOperatingSystem['human_workflows']> }) {
    return (
      <div className="ion-project-ops-workflow-grid">
        {workflows.map((workflow) => (
          <div className="ion-project-ops-row" key={workflow.workflow_id ?? workflow.label}>
            <span>{workflow.cadence ?? 'workflow'}</span>
            <b>{workflow.label ?? 'workflow'}</b>
            <p>{workflow.trigger ?? ''}</p>
            <code>{workflow.output ?? ''}</code>
          </div>
        ))}
      </div>
    );
  }

  function ProjectDocsPanel({
    domain,
    family,
    version,
    domainFamilies,
  }: {
    domain: IonProjectPortfolioDomain;
    family?: IonProjectPortfolioFamily;
    version?: IonProjectPortfolioVersion;
    domainFamilies: IonProjectPortfolioFamily[];
  }) {
    const domainDocs = domain.docs ?? {};
    const familyDocs = family?.docs ?? {};
    const versionDocs = version?.docs ?? {};
    const primaryDocs = compactDocRows(familyDocs.primary_docs ?? familyDocs.docs ?? []);
    const versionDocRows = compactDocRows(versionDocs.docs ?? []);
    const domainTopDocs = compactDocRows(domainDocs.top_docs ?? []);
    const references = compactReferences([...(familyDocs.references ?? []), ...(versionDocs.references ?? []), ...(domainDocs.references ?? [])]);
    const targetDocs = [...(familyDocs.target_docs ?? []), ...(domainDocs.target_docs ?? [])].slice(0, 12);
    const recommendedSections = domainDocs.recommended_sections ?? [
      'Project Overview',
      'Architecture',
      'Runbook',
      'Version Notes',
      'Diff Evolution',
      'Source Authority',
      'References',
      'Screenshots',
      'Operator Review Notes',
    ];
    return (
      <div className="ion-project-docs-layout">
        <section className="ion-project-docs-hero">
          <div>
            <span>domain documentation system</span>
            <b>{domain.label ?? domain.domain_id}</b>
            <p>Docs, references, sources, version notes, and organized-folder targets stay attached to the selected domain, project, and version.</p>
          </div>
          <Metric label="domain docs" value={String(domain.doc_count ?? domainDocs.doc_count ?? 0)} tone="active" />
          <Metric label="references" value={String(domain.reference_count ?? domainDocs.reference_count ?? 0)} tone="watch" />
          <Metric label="documented" value={String(domain.documented_family_count ?? domainDocs.documented_family_count ?? 0)} tone="ready" />
          <Metric label="projects" value={String(domainFamilies.length)} tone="ready" />
        </section>
        <div className="ion-project-docs-grid">
          <section className="ion-project-docs-panel is-primary">
            <div className="ion-runtime-card-head"><span>selected project docs</span><b>{family?.label ?? family?.family_id ?? 'project'}</b></div>
            <div className="ion-project-doc-health-row">
              <DocHealthPill label="readme" value={familyDocs.coverage?.has_readme} />
              <DocHealthPill label="architecture" value={familyDocs.coverage?.has_architecture} />
              <DocHealthPill label="runbook" value={familyDocs.coverage?.has_runbook} />
              <DocHealthPill label="references" value={familyDocs.coverage?.has_references ?? familyDocs.coverage?.has_reference} />
            </div>
            <DocRowList docs={primaryDocs} emptyLabel="NO PROJECT DOCS FOUND" />
          </section>
          <section className="ion-project-docs-panel">
            <div className="ion-runtime-card-head"><span>loaded version docs</span><b>{version?.sequence_label ?? version?.version_token ?? 'version'}</b></div>
            <PathRow label="version source" value={version?.path} />
            <PathRow label="version manifest" value={version?.load?.organized_version_manifest} />
            <DocRowList docs={versionDocRows.slice(0, 10)} emptyLabel="NO VERSION DOCS FOUND" />
          </section>
          <section className="ion-project-docs-panel">
            <div className="ion-runtime-card-head"><span>references / sources</span><b>{references.length}</b></div>
            <ReferenceList references={references} />
          </section>
          <section className="ion-project-docs-panel">
            <div className="ion-runtime-card-head"><span>organized docs targets</span><b>{targetDocs.length}</b></div>
            {targetDocs.map((target, index) => (
              <div className="ion-project-doc-target" key={`${target.path ?? target.label}-${index}`}>
                <span>{target.status ?? 'target'}</span>
                <b>{target.label ?? 'Documentation target'}</b>
                <code>{target.path ?? 'path pending'}</code>
              </div>
            ))}
            {targetDocs.length === 0 && <div className="ion-vnext-empty-inline">NO ORGANIZED DOC TARGETS PROJECTED</div>}
          </section>
          <section className="ion-project-docs-panel is-wide">
            <div className="ion-runtime-card-head"><span>domain doc canon</span><b>{recommendedSections.length}</b></div>
            <div className="ion-project-doc-canon-grid">
              {recommendedSections.map((section) => (
                <div className="ion-project-doc-canon-card" key={section}>
                  <span>required section</span>
                  <b>{section}</b>
                </div>
              ))}
            </div>
          </section>
          <section className="ion-project-docs-panel is-wide">
            <div className="ion-runtime-card-head"><span>domain top docs</span><b>{domainTopDocs.length}</b></div>
            <DocRowList docs={domainTopDocs} emptyLabel="NO DOMAIN DOCS PROJECTED" />
          </section>
        </div>
      </div>
    );
  }

  function ProjectLaunchPanel({ version, family }: { version?: IonProjectPortfolioVersion; family?: IonProjectPortfolioFamily }) {
    if (!version) return <div className="ion-vnext-empty-inline">NO VERSION LOADED</div>;
    const launch = version.launch ?? {};
    const record = launchRecordForVersion(version);
    const running = Boolean(record?.running);
    const launchable = Boolean(launch.launchable ?? version.launchable);
    const busy = launchBusyKey === launchKeyForVersion(version) || (record?.launch_id ? launchBusyKey === record.launch_id : false);
    const diagnosticsBusy = record?.launch_id ? launchBusyKey === `diagnostics:${record.launch_id}` : false;
    const diagnostics = record?.launch_id ? launchDiagnostics[record.launch_id] : undefined;
    const screenshot = diagnostics?.screenshot as Record<string, unknown> | undefined;
    const framework = launch.framework ?? version.stack ?? record?.framework ?? 'project';
    const state = record?.state ?? launch.status ?? (launchable ? 'ready' : 'not launchable');
    const openHref = record?.open_href ?? record?.url;
    return (
      <div className={`ion-project-launch-panel is-${running ? 'running' : launchable ? 'ready' : 'blocked'}`}>
        <div className="ion-runtime-card-head">
          <span>local project launch</span>
          <b>{running ? 'running' : state}</b>
        </div>
        <div className="ion-vnext-packet-meta">
          <small>{framework}</small>
          <small>{launch.install_repair_on_launch ? 'dependency repair' : 'direct start'}</small>
          <small>{launch.managed_window_stops_server ? 'close stops server' : 'manual stop'}</small>
          {record?.port && <small>port {record.port}</small>}
        </div>
        <PathRow label="launch path" value={launch.project_path ?? version.path} />
        {record?.url && <PathRow label="active url" value={record.url} />}
        {record?.message && <p>{record.message}</p>}
        <div className="ion-project-launch-actions">
          <button disabled={!launchable || busy} onClick={() => startProjectVersion(version, family)} type="button">
            {busy ? 'Starting' : running ? 'Open Managed' : launch.install_repair_on_launch ? 'Repair & Launch' : 'Launch'}
          </button>
          {openHref && (
            <a href={openHref} target="_blank" rel="noreferrer">
              Open
            </a>
          )}
          {running && (
            <button disabled={busy} onClick={() => stopProjectLaunch(record)} type="button">
              Stop Server
            </button>
          )}
          {running && (
            <button disabled={diagnosticsBusy} onClick={() => captureProjectLaunchDiagnostics(record)} type="button">
              {diagnosticsBusy ? 'Capturing' : 'Diagnostics'}
            </button>
          )}
        </div>
        {!launchable && <div className="ion-vnext-empty-inline">NO DEV OR STATIC LAUNCHER DETECTED</div>}
        {diagnostics && (
          <div className="ion-project-launch-diagnostics">
            <div className="ion-runtime-card-head"><span>ai/codex diagnostics</span><b>{String(diagnostics.ok ? 'captured' : diagnostics.finding ?? 'pending')}</b></div>
            {screenshot?.screenshot_href && <img alt="Captured app diagnostic" src={String(screenshot.screenshot_href)} />}
            <PathRow label="screenshot" value={screenshot?.screenshot_path} />
          </div>
        )}
        {record?.log_tail && <pre className="ion-project-launch-log">{record.log_tail}</pre>}
      </div>
    );
  }

  function renderVNextPane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand />
        <div className="ion-vnext-map-grid">
          <section className="ion-vnext-map-band">
            <SectionHead icon={<GraphIcon />} label="Mission Orchestration" />
            <div className="ion-vnext-mission-grid">
              {missions.map((mission) => <MissionCard mission={mission} key={mission.mission_id} />)}
            </div>
            <SectionHead icon={<StreamIcon />} label="Project Evolution" />
            <div className="ion-vnext-timeline-stack">
              {timelineEvents.slice(0, 8).map((event) => <TimelineCard event={event} key={event.event_id} />)}
            </div>
          </section>
          <section className="ion-vnext-side-stack">
            <SectionHead icon={<ReceiptIcon />} label="Issues" />
            <div className="ion-vnext-blocker-grid is-compact">
              {openBlockers.slice(0, 6).map((blocker) => <BlockerCard blocker={blocker} key={blocker.blocker_id} compact />)}
            </div>
            <SectionHead icon={<RouteIcon />} label="Next Route" />
            <RouteCard />
          </section>
        </div>
      </div>
    );
  }

  function renderMissionsPane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand compact />
        <SectionHead icon={<GraphIcon />} label="Mission Families" />
        <div className="ion-vnext-mission-grid">
          {missions.map((mission) => <MissionCard mission={mission} key={mission.mission_id} />)}
        </div>
        <SectionHead icon={<StreamIcon />} label="Long Horizon Epochs" />
        <div className="ion-vnext-epoch-stack">
          {epochs.map((epoch) => <EpochCard epoch={epoch} key={epoch.epoch_id ?? `${epoch.row_start}-${epoch.row_end}`} />)}
        </div>
      </div>
    );
  }

  function renderBlockersPane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand compact />
        {actionMessage && <div className={`ion-vnext-action-banner${actionMessage.includes('failed') || actionMessage.includes('required') ? ' is-blocked' : ''}`}>{actionMessage}</div>}
        <SectionHead icon={<ReceiptIcon />} label="Open Blockers" />
        <div className="ion-vnext-blocker-grid">
          {openBlockers.map((blocker) => <BlockerCard blocker={blocker} key={blocker.blocker_id} />)}
          {openBlockers.length === 0 && <div className="ion-vnext-empty-inline">NO OPEN BLOCKERS</div>}
        </div>
        <SectionHead icon={<RouteIcon />} label="Managed Blocker Intake" />
        <BlockerCreateForm />
        {managedBlockers.length > 0 && (
          <>
            <SectionHead icon={<LensIcon />} label="Managed Blocker Actions" />
            <div className="ion-vnext-form-grid">
              {managedBlockers.map((blocker) => <BlockerActionForm blocker={blocker} key={blocker.blocker_id} />)}
            </div>
          </>
        )}
      </div>
    );
  }

  function renderQuestionsPane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand compact />
        {actionMessage && <div className={`ion-vnext-action-banner${actionMessage.includes('failed') || actionMessage.includes('required') ? ' is-blocked' : ''}`}>{actionMessage}</div>}
        <SectionHead icon={<LensIcon />} label="Open Questions" />
        <div className="ion-vnext-question-grid">
          {openQuestions.map((question) => <QuestionCard question={question} key={question.question_id} />)}
          {openQuestions.length === 0 && <div className="ion-vnext-empty-inline">NO OPEN QUESTIONS</div>}
        </div>
        <SectionHead icon={<RouteIcon />} label="Question Intake" />
        <QuestionCreateForm />
        {questions.length > 0 && (
          <>
            <SectionHead icon={<ReceiptIcon />} label="Question Actions" />
            <div className="ion-vnext-form-grid">
              {questions.map((question) => <QuestionActionForm question={question} key={question.question_id} />)}
            </div>
          </>
        )}
      </div>
    );
  }

  function renderTimelinePane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand compact />
        <SectionHead icon={<StreamIcon />} label="Project Evolution Timeline" />
        <div className="ion-vnext-timeline-stack">
          {timelineEvents.map((event) => <TimelineCard event={event} key={event.event_id} />)}
          {timelineEvents.length === 0 && <div className="ion-vnext-empty-inline">NO TIMELINE EVENTS</div>}
        </div>
      </div>
    );
  }

  function renderProtocolsPane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <div className="ion-vnext-protocol-summary">
          <Metric label="protocol docs" value={String(vnext?.protocol_index?.protocol_count ?? 0)} tone="active" />
          <Metric label="groups" value={String(protocolGroups.length)} tone="neutral" />
          <Metric label="authority docs" value={String(protocolGroups.reduce((total, group) => total + (group.authority_count ?? 0), 0))} tone="neutral" />
          <Metric label="doc files" value={String(vnext?.documentation_surfaces?.file_count ?? 0)} tone="neutral" />
        </div>
        <SectionHead icon={<LensIcon />} label="Protocol Groups" />
        <div className="ion-vnext-family-grid">
          {protocolGroups.map((group) => (
            <article className="ion-vnext-family-card" key={group.family_id}>
              <span>{group.protocol_count ?? 0} protocols</span>
              <b>{group.label ?? group.family_id}</b>
              <p>{group.authority_count ?? 0} authority-marked documents</p>
              <div className="ion-vnext-chip-row">
                {(group.sample_paths ?? []).map((path) => <small key={path}>{path}</small>)}
              </div>
            </article>
          ))}
        </div>
        <SectionHead icon={<ReceiptIcon />} label="Protocol Inventory" />
        <div className="ion-vnext-protocol-table">
          {protocolRows.map((row) => <ProtocolRow row={row} key={row.path} />)}
        </div>
      </div>
    );
  }

  function renderContextPane() {
    return (
      <div className="ion-vnext-scroll-pane">
        <CommandBand compact />
        <SectionHead icon={<ReceiptIcon />} label="Context Packages" />
        <div className="ion-vnext-context-grid">
          {contextPackages.map((item, index) => (
            <ContextPackageCard item={item} key={item.package_id ?? item.context_type ?? `context-${index}`} />
          ))}
        </div>
        <SectionHead icon={<WorkSurfaceIcon />} label="Source Truth" />
        <div className="ion-vnext-source-grid">
          {sourceRows.map(([key, present]) => <SourceRow itemKey={key} present={Boolean(present)} path={vnext?.source_paths?.[key] ?? projectCockpit?.source_paths?.[key]} key={key} />)}
        </div>
        <SectionHead icon={<LensIcon />} label="Documentation Surfaces" />
        <div className="ion-vnext-doc-grid">
          {docSurfaces.map((surface) => <DocumentationSurfaceCard surface={surface} key={surface.surface_id} />)}
        </div>
      </div>
    );
  }

  function renderLeftDrawer(id: LeftDrawerId): ReactNode {
    if (id === 'missions') {
      return <div className="ion-vnext-drawer-stack">{missions.map((mission) => <MissionCard mission={mission} key={mission.mission_id} compact />)}</div>;
    }
    if (id === 'sources') {
      return (
        <div className="ion-vnext-source-stack">
          {sourceRows.map(([key, present]) => <SourceRow itemKey={key} present={Boolean(present)} path={vnext?.source_paths?.[key] ?? projectCockpit?.source_paths?.[key]} key={key} />)}
        </div>
      );
    }
    if (id === 'horizon') {
      return <div className="ion-vnext-drawer-stack">{latestEpochs.map((epoch) => <EpochCard epoch={epoch} key={epoch.epoch_id ?? epoch.row_start} compact />)}</div>;
    }
    if (portfolio) {
      return (
        <div className="ion-project-domain-drawer-stack">
          <div className="ion-project-domain-drawer-head">
            <span>project domains</span>
            <b>{portfolioGroups.length}</b>
            <p>Choose a domain to open its project page.</p>
          </div>
          <div className="ion-project-domain-drawer-list">
            {portfolioGroups.map((group) => {
              const groupId = (group as IonProjectPortfolioDomain).domain_id ?? group.group_id ?? 'all';
              return (
                <button className={selectedPortfolioDomain?.domain_id === groupId || activePortfolioGroup === groupId ? 'is-active' : undefined} key={groupId} onClick={() => selectPortfolioDomain(groupId)} type="button">
                  <span>{group.label ?? groupId}</span>
                  <b>{group.family_count ?? 0}</b>
                  <small>{group.project_count ?? 0} roots / {group.launchable_count ?? 0} launch</small>
                </button>
              );
            })}
          </div>
        </div>
      );
    }
    return <div className="ion-vnext-drawer-stack">{projects.map((project) => <ProjectCard project={project} key={project.project_id} compact />)}</div>;
  }

  function renderRightDrawer(id: RightDrawerId): ReactNode {
    if (id === 'questions') {
      return <div className="ion-vnext-question-grid is-compact">{questions.slice(0, 12).map((question) => <QuestionCard question={question} key={question.question_id} compact />)}</div>;
    }
    if (id === 'receipts') {
      return (
        <div className="ion-vnext-drawer-stack">
          {latestReceipts.map((receipt, index) => <ReceiptCard receipt={receipt} key={String(receipt.receipt_id ?? receipt.path ?? index)} />)}
          {latestReceipts.length === 0 && <div className="ion-vnext-empty-inline">NO PROJECT RECEIPTS</div>}
        </div>
      );
    }
    if (id === 'authority') {
      return (
        <div className="ion-vnext-drawer-stack">
          <div className="ion-vnext-authority-grid">
            <AuthorityFlag label="candidate writes" value={projectCockpit?.authority?.candidate_state_write_authority} />
            <AuthorityFlag label="accepted" value={projectCockpit?.authority?.accepted_state_authority} />
            <AuthorityFlag label="production" value={projectCockpit?.authority?.production_authority} />
            <AuthorityFlag label="live exec" value={projectCockpit?.authority?.live_execution_authority} />
            <AuthorityFlag label="supabase" value={projectCockpit?.authority?.supabase_mutation_authority} />
            <AuthorityFlag label="codex dispatch" value={projectCockpit?.authority?.codex_queue_dispatch_authority} />
          </div>
          <div className="ion-vnext-nonclaim-stack">
            {(projectCockpit?.non_claims ?? []).map((claim) => <span key={claim}>{claim}</span>)}
          </div>
        </div>
      );
    }
    return <div className="ion-vnext-blocker-grid is-compact">{blockers.slice(0, 12).map((blocker) => <BlockerCard blocker={blocker} key={blocker.blocker_id} compact />)}</div>;
  }

  function CommandBand({ compact = false, projectHub = false }: { compact?: boolean; projectHub?: boolean }) {
    const title = projectHub ? 'ION Project Hub' : selectedProject?.label ?? 'ION vNext';
    const kicker = projectHub ? 'PROJECTS / OPERATING HUB' : 'PROJECTS / VNEXT DETAIL';
    return (
      <header className={`ion-vnext-command-band${compact ? ' is-compact' : ''}`}>
        <div className="ion-vnext-command-copy">
          <div className="ion-vnext-kicker"><RouteIcon /> {kicker}</div>
          <h2>{title}</h2>
          <div className="ion-vnext-proof-row">
            <span>{projectCockpit?.status ?? 'projected'}</span>
            <span>{projectHub ? `${projects.length} projects` : selectedProject?.status ?? vnext?.status ?? 'status unknown'}</span>
            <span>{projectHub ? 'vNext isolated' : selectedProject?.current_packet ?? vnext?.current_packet?.token ?? 'no current packet'}</span>
          </div>
        </div>
        <div className="ion-vnext-kpis">
          <Metric label="projects" value={String(projectSummary.project_count ?? projects.length)} tone="active" />
          <Metric label="missions" value={String(projectSummary.mission_count ?? missions.length)} tone="neutral" />
          <Metric label="blockers" value={String(projectSummary.open_blocker_count ?? openBlockers.length)} tone={openBlockers.length > 0 ? 'watch' : 'active'} />
          <Metric label="questions" value={String(projectSummary.open_question_count ?? openQuestions.length)} tone={openQuestions.length > 0 ? 'watch' : 'active'} />
        </div>
      </header>
    );
  }

  function RouteCard() {
    return (
      <div className="ion-vnext-route-card">
        <span>{vnext?.next_safe_route?.automatic ? 'automatic' : 'not automatic'}</span>
        <b>{vnext?.next_safe_route?.route ?? 'NO_ROUTE'}</b>
        <p>{vnext?.next_safe_route?.condition ?? 'No route condition projected.'}</p>
      </div>
    );
  }

  function BlockerCreateForm() {
    return (
      <form className="ion-vnext-form-card" onSubmit={(event) => submitProjectAction('blocker', 'create', event)}>
        <div className="ion-vnext-form-head"><span>new blocker</span><b>{isSubmitting ? 'recording' : 'candidate'}</b></div>
        <label><span>title</span><input name="title" required /></label>
        <label><span>detail</span><textarea name="detail" rows={3} /></label>
        <div className="ion-vnext-form-row">
          <label><span>severity</span><select name="severity" defaultValue="medium"><option>critical</option><option>high</option><option>medium</option><option>low</option></select></label>
          <label><span>owner route</span><input name="owner_route" defaultValue="codex_cli" /></label>
        </div>
        <label><span>unlock condition</span><textarea name="unlock_condition" rows={2} /></label>
        <label><span>next action</span><textarea name="required_next_action" rows={2} /></label>
        <label><span>evidence refs</span><input name="evidence_refs" /></label>
        <button disabled={isSubmitting} type="submit">Record Blocker</button>
      </form>
    );
  }

  function BlockerActionForm({ blocker }: { blocker: IonProjectCockpitBlocker }) {
    return (
      <form className="ion-vnext-form-card is-compact" onSubmit={(event) => submitProjectAction('blocker', 'update', event)}>
        <div className="ion-vnext-form-head"><span>{blocker.status ?? 'open'}</span><b>{blocker.title ?? blocker.blocker_id}</b></div>
        <input name="blocker_id" type="hidden" value={blocker.blocker_id} />
        <label><span>status</span><select name="status" defaultValue={blocker.status ?? 'open'}><option>open</option><option>in_progress</option><option>watch</option><option>blocked</option><option>resolved</option></select></label>
        <label><span>next action</span><textarea name="required_next_action" rows={2} defaultValue={blocker.required_next_action ?? ''} /></label>
        <label><span>evidence refs</span><input name="evidence_refs" defaultValue={(blocker.evidence_refs ?? []).join(', ')} /></label>
        <div className="ion-vnext-action-row">
          <button disabled={isSubmitting} type="submit">Update</button>
          <button disabled={isSubmitting || !isOpenStatus(blocker.status)} onClick={(event) => resolveRecord('blocker', blocker.blocker_id, event)} type="button">Resolve</button>
        </div>
      </form>
    );
  }

  function QuestionCreateForm() {
    return (
      <form className="ion-vnext-form-card" onSubmit={(event) => submitProjectAction('question', 'create', event)}>
        <div className="ion-vnext-form-head"><span>new question</span><b>{isSubmitting ? 'recording' : 'candidate'}</b></div>
        <label><span>question</span><textarea name="question_text" required rows={3} /></label>
        <div className="ion-vnext-form-row">
          <label><span>needed from</span><input name="needed_from" defaultValue="ION_OPERATOR_OR_STEWARD" /></label>
          <label><span>priority</span><select name="priority" defaultValue="P2_NORMAL"><option>P0_BLOCKING</option><option>P1_HIGH</option><option>P2_NORMAL</option><option>P3_LOW</option></select></label>
        </div>
        <label><span>context</span><textarea name="context" rows={2} /></label>
        <label><span>blocking</span><input name="blocking" /></label>
        <label><span>evidence refs</span><input name="evidence_refs" /></label>
        <button disabled={isSubmitting} type="submit">Record Question</button>
      </form>
    );
  }

  function QuestionActionForm({ question }: { question: IonProjectCockpitQuestion }) {
    return (
      <form className="ion-vnext-form-card is-compact" onSubmit={(event) => submitProjectAction('question', 'update', event)}>
        <div className="ion-vnext-form-head"><span>{question.priority ?? 'P2_NORMAL'}</span><b>{question.question_text ?? question.question_id}</b></div>
        <input name="question_id" type="hidden" value={question.question_id} />
        <label><span>status</span><select name="status" defaultValue={question.status ?? 'open'}><option>open</option><option>in_progress</option><option>watch</option><option>blocked</option><option>resolved</option></select></label>
        <label><span>context</span><textarea name="context" rows={2} defaultValue={question.context ?? ''} /></label>
        <label><span>evidence refs</span><input name="evidence_refs" defaultValue={(question.evidence_refs ?? []).join(', ')} /></label>
        <div className="ion-vnext-action-row">
          <button disabled={isSubmitting} type="submit">Update</button>
          <button disabled={isSubmitting || !isOpenStatus(question.status)} onClick={(event) => resolveRecord('question', question.question_id, event)} type="button">Resolve</button>
        </div>
      </form>
    );
  }

  async function resolveRecord(recordType: 'blocker' | 'question', recordId: string, event: MouseEvent<HTMLButtonElement>) {
    const form = event.currentTarget.form;
    if (!form) return;
    const payload = Object.fromEntries(Array.from(new FormData(form).entries()).map(([key, value]) => [key, String(value)]));
    payload.record_id = recordId;
    payload.status = 'resolved';
    payload.resolution = payload.resolution || 'Resolved from Project Mission Control.';
    payload.confirmation = writeConfirmation;
    payload.actor = payload.actor || 'project_cockpit_ui';
    setIsSubmitting(true);
    setActionMessage('');
    try {
      const response = await fetch(`/cockpit/projects/${recordType}/resolve`, {
        method: 'POST',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        setActionMessage(String(result.finding ?? result.error ?? 'project action failed'));
        return;
      }
      setActionMessage(`${recordType} resolve recorded`);
      onRuntimeRefresh?.();
    } catch (error) {
      setActionMessage(error instanceof Error ? error.message : 'project action failed');
    } finally {
      setIsSubmitting(false);
    }
  }
}

export function VNextMissionControlPanel(props: { runtime: IonCockpitViewModel; onRuntimeRefresh?: () => void }) {
  return <ProjectMissionControlPanel {...props} />;
}

function DrawerIconBar<T extends string>({
  items,
  active,
  onSelect,
}: {
  items: Array<{ id: T; icon: ReactNode; title: string }>;
  active?: T;
  onSelect: (id: T) => void;
}) {
  return (
    <div className="ion-vnext-iconbar">
      {items.map((item) => (
        <button className={active === item.id ? 'is-active' : undefined} key={item.id} onClick={() => onSelect(item.id)} title={item.title} type="button">
          <span className="ion-rail-icon" aria-hidden="true">{item.icon}</span>
        </button>
      ))}
    </div>
  );
}

function drawerTitle<T extends string>(items: Array<{ id: T; title: string }>, active: T) {
  return items.find((item) => item.id === active)?.title ?? String(active);
}

function SectionHead({ icon, label }: { icon: ReactNode; label: string }) {
  return (
    <div className="ion-vnext-section-head">
      {icon}
      <span>{label}</span>
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className={`ion-vnext-metric is-${tone}`}>
      <span>{label}</span>
      <b>{value}</b>
    </div>
  );
}

function AuthorityFlag({ label, value }: { label: string; value?: boolean }) {
  const enabled = value === true;
  return (
    <div className={`ion-vnext-authority-flag is-${enabled ? 'true' : 'false'}`}>
      <span>{label}</span>
      <b>{enabled ? 'true' : 'false'}</b>
    </div>
  );
}

function ProjectFamilyCard({
  family,
  favorite,
  selected,
  onSelect,
  onToggleFavorite,
}: {
  family: IonProjectPortfolioFamily;
  favorite: boolean;
  selected: boolean;
  onSelect: () => void;
  onToggleFavorite: () => void;
}) {
  return (
    <article className={`ion-project-family-card${selected ? ' is-selected' : ''}${favorite ? ' is-favorite' : ''}`}>
      <button className="ion-project-family-main" onClick={onSelect} type="button">
        <span>{family.domain_label ?? family.domain_id ?? 'project domain'}</span>
        <b>{family.label ?? family.family_id}</b>
        <div className="ion-vnext-packet-meta">
          <small>{family.project_count ?? 0} roots</small>
          <small>{family.version_count ?? 0} versions</small>
          <small>{family.launchable_count ?? 0} launchers</small>
        </div>
        <code>{family.current_path ?? family.family_id}</code>
      </button>
      <button className="ion-project-favorite-button" aria-pressed={favorite} onClick={onToggleFavorite} title="Favorite project" type="button">
        {favorite ? 'Saved' : 'Save'}
      </button>
    </article>
  );
}

function ProjectCommandFamilyRow({
  family,
  favorite,
  selected,
  detailHref,
  onSelect,
  onToggleFavorite,
}: {
  family: IonProjectPortfolioFamily;
  favorite: boolean;
  selected: boolean;
  detailHref: string;
  onSelect: () => void;
  onToggleFavorite: () => void;
}) {
  return (
    <article className={`ion-project-command-family-row${selected ? ' is-selected' : ''}${favorite ? ' is-favorite' : ''}`}>
      <button className="ion-project-command-family-main" onClick={onSelect} type="button">
        <span>{family.domain_label ?? family.domain_id ?? 'project domain'}</span>
        <b>{family.label ?? family.family_id}</b>
        <div className="ion-vnext-packet-meta">
          <small>{family.project_count ?? 0} roots</small>
          <small>{family.version_count ?? 0} versions</small>
          <small>{family.diff_count ?? 0} diffs</small>
          <small>{family.launchable_count ?? 0} launch</small>
          <small>{family.doc_count ?? 0} docs</small>
        </div>
        <code>{family.current_path ?? family.organized_path ?? family.family_id}</code>
      </button>
      <div className="ion-project-command-family-actions">
        <a href={detailHref} target="_blank" rel="noreferrer">Open</a>
        <button aria-pressed={favorite} onClick={onToggleFavorite} type="button">
          {favorite ? 'Saved' : 'Save'}
        </button>
      </div>
    </article>
  );
}

function ProjectDomainProjectCard({
  family,
  selected,
  onSelect,
}: {
  family: IonProjectPortfolioFamily;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button className={`ion-project-domain-project-card${selected ? ' is-selected' : ''}`} onClick={onSelect} type="button">
      <span>{family.domain_label ?? family.domain_id ?? 'domain'}</span>
      <b>{family.label ?? family.family_id}</b>
      <div className="ion-vnext-packet-meta">
        <small>{family.version_count ?? 0} versions</small>
        <small>{family.branch_count ?? 0} branches</small>
        <small>{family.diff_count ?? 0} diffs</small>
        <small>{family.doc_count ?? 0} docs</small>
      </div>
      <code>{family.current_path ?? family.family_id}</code>
    </button>
  );
}

function ProjectDomainCard({
  domain,
  selected,
  onSelect,
  expandedContent,
}: {
  domain: IonProjectPortfolioDomain;
  selected: boolean;
  onSelect: () => void;
  expandedContent?: ReactNode;
}) {
  return (
    <article className={`ion-project-domain-card${selected ? ' is-selected is-expanded' : ''}`}>
      <button className="ion-project-domain-card-main" onClick={onSelect} type="button">
        <span>{String(domain.sort_order ?? '').padStart(2, '0')}</span>
        <b>{domain.label ?? domain.domain_id}</b>
        <p>{domain.summary ?? 'Project domain'}</p>
        <div className="ion-vnext-packet-meta">
          <small>{domain.family_count ?? 0} projects</small>
          <small>{domain.version_count ?? 0} versions</small>
          <small>{domain.branch_count ?? 0} branches</small>
          <small>{domain.diff_count ?? 0} diffs</small>
          <small>{domain.doc_count ?? 0} docs</small>
        </div>
      </button>
      {expandedContent}
    </article>
  );
}

function BranchStrip({ family }: { family?: IonProjectPortfolioFamily }) {
  const branches = family?.branches ?? [];
  if (!branches.length) return <div className="ion-vnext-empty-inline">NO BRANCHES PROJECTED</div>;
  return (
    <div className="ion-project-branch-strip">
      {branches.map((branch) => (
        <div className="ion-project-branch-pill" key={branch.branch_id ?? branch.label}>
          <span>{branch.label ?? branch.branch_id ?? 'branch'}</span>
          <b>{branch.version_count ?? 0}</b>
          <small>{branch.launchable_count ?? 0} launchers</small>
        </div>
      ))}
    </div>
  );
}

function ProjectVersionRow({
  version,
  index = 0,
  selected = false,
  onSelect,
}: {
  version: IonProjectPortfolioVersion;
  index?: number;
  selected?: boolean;
  onSelect?: () => void;
}) {
  return (
    <button className={`ion-project-version-row${selected ? ' is-selected' : ''}`} onClick={onSelect} type="button">
      <span>{version.sequence_label ?? `v${String(index + 1).padStart(3, '0')}`}</span>
      <b>{version.display_label ?? version.label ?? version.project_id ?? 'project version'}</b>
      <div className="ion-vnext-packet-meta">
        <small>{version.version_token || version.milestone_token || version.date_token || 'snapshot'}</small>
        <small>{version.branch_label ?? 'main'}</small>
        <small>{version.stack ?? 'stack unknown'}</small>
        <small>{version.is_current ? 'loaded current' : version.launchable ? 'launchable' : 'source ref'}</small>
      </div>
      <code>{version.path ?? 'no path projected'}</code>
    </button>
  );
}

function LoadedVersionPanel({ version, diff }: { version?: IonProjectPortfolioVersion; diff?: IonProjectPortfolioDiff }) {
  if (!version) return <div className="ion-vnext-empty-inline">NO VERSION LOADED</div>;
  const load = version.load ?? {};
  return (
    <div className="ion-project-loaded-version">
      <div className="ion-runtime-card-head"><span>loaded version</span><b>{version.sequence_label ?? version.version_token ?? version.milestone_token ?? 'snapshot'}</b></div>
      <b>{version.display_label ?? version.label ?? version.project_id ?? 'version'}</b>
      <div className="ion-vnext-packet-meta">
        <small>{version.branch_label ?? 'main'}</small>
        <small>{version.version_token ?? 'snapshot'}</small>
        <small>{version.stack ?? 'stack'}</small>
        <small>{version.launchable ? 'launchable' : 'source'}</small>
        <small>{version.is_current ? 'current copy' : 'historical ref'}</small>
      </div>
      <PathRow label="source path" value={load.path ?? version.path} />
      <PathRow label="version manifest" value={load.organized_version_manifest} />
      {load.organized_current_source && <PathRow label="current organized source" value={load.organized_current_source} />}
      {diff && <DiffMiniSummary diff={diff} />}
    </div>
  );
}

function ProjectDiffRow({ diff, selected, onSelect }: { diff: IonProjectPortfolioDiff; selected: boolean; onSelect: () => void }) {
  const fileDiff = diff.file_diff ?? {};
  return (
    <button className={`ion-project-diff-row${selected ? ' is-selected' : ''}`} onClick={onSelect} type="button">
      <span>{diff.status ?? 'diff'}</span>
      <b>{diff.from_label ?? diff.from_version ?? 'snapshot'} {'->'} {diff.to_label ?? diff.to_version ?? 'snapshot'}</b>
      <div className="ion-vnext-packet-meta">
        <small>+{fileDiff.added_count ?? 0}</small>
        <small>-{fileDiff.removed_count ?? 0}</small>
        <small>~{fileDiff.changed_count ?? 0}</small>
        <small>{diff.to_branch ?? 'main'}</small>
      </div>
      <code>{diff.diff_id ?? 'diff unit'}</code>
    </button>
  );
}

function DiffDetailPanel({ diff, version }: { diff?: IonProjectPortfolioDiff; version?: IonProjectPortfolioVersion }) {
  if (!diff) return <div className="ion-project-family-detail"><div className="ion-vnext-empty-inline">NO DIFF LOADED</div></div>;
  const fileDiff = diff.file_diff ?? {};
  return (
    <div className="ion-project-diff-detail">
      <div className="ion-runtime-card-head"><span>loaded diff</span><b>{fileDiff.status ?? diff.status ?? 'diff'}</b></div>
      <b>{diff.from_label ?? diff.from_version ?? 'snapshot'} {'->'} {diff.to_label ?? diff.to_version ?? version?.display_label ?? 'snapshot'}</b>
      <p>{diff.copy_policy ?? 'Historical roots remain referenced while changes are represented as bounded diff units.'}</p>
      <div className="ion-project-change-metrics">
        <Metric label="added" value={String(fileDiff.added_count ?? 0)} tone="ready" />
        <Metric label="removed" value={String(fileDiff.removed_count ?? 0)} tone="blocked" />
        <Metric label="changed" value={String(fileDiff.changed_count ?? 0)} tone="watch" />
      </div>
      <div className="ion-vnext-packet-meta">
        <small>{diff.from_branch ?? 'main'}</small>
        <small>{diff.to_branch ?? 'main'}</small>
      </div>
      <PathRow label="from" value={diff.from_path} />
      <PathRow label="to" value={diff.to_path} />
      <PathRow label="manifest" value={diff.manifest_path} />
      <FileChangeList title="added files" values={fileDiff.added_sample ?? []} />
      <FileChangeList title="changed files" values={fileDiff.changed_sample ?? []} />
      <FileChangeList title="removed files" values={fileDiff.removed_sample ?? []} />
    </div>
  );
}

function DiffMiniSummary({ diff }: { diff: IonProjectPortfolioDiff }) {
  const fileDiff = diff.file_diff ?? {};
  return (
    <div className="ion-project-diff-mini">
      <span>related diff</span>
      <b>{diff.from_label ?? diff.from_version ?? 'snapshot'} {'->'} {diff.to_label ?? diff.to_version ?? 'snapshot'}</b>
      <div className="ion-vnext-packet-meta">
        <small>+{fileDiff.added_count ?? 0}</small>
        <small>-{fileDiff.removed_count ?? 0}</small>
        <small>~{fileDiff.changed_count ?? 0}</small>
      </div>
    </div>
  );
}

function DenseDiffPanel({ diff, version }: { diff?: IonProjectPortfolioDiff; version?: IonProjectPortfolioVersion }) {
  if (!diff) return <div className="ion-project-dense-diff-panel"><div className="ion-vnext-empty-inline">NO DIFF LOADED</div></div>;
  const fileDiff = diff.file_diff ?? {};
  return (
    <div className="ion-project-dense-diff-panel">
      <div className="ion-runtime-card-head"><span>diff</span><b>{fileDiff.status ?? diff.status ?? 'ready'}</b></div>
      <b>{diff.from_label ?? diff.from_version ?? 'snapshot'} {'->'} {diff.to_label ?? diff.to_version ?? version?.display_label ?? 'snapshot'}</b>
      <div className="ion-project-dense-diff-counts">
        <Metric label="added" value={String(fileDiff.added_count ?? 0)} tone="ready" />
        <Metric label="removed" value={String(fileDiff.removed_count ?? 0)} tone="blocked" />
        <Metric label="changed" value={String(fileDiff.changed_count ?? 0)} tone="watch" />
      </div>
      <PathRow label="manifest" value={diff.manifest_path} />
      <PathRow label="from" value={diff.from_path} />
      <PathRow label="to" value={diff.to_path} />
    </div>
  );
}

function FileChangeList({ title, values }: { title: string; values: string[] }) {
  return (
    <div className="ion-project-change-list">
      <div className="ion-runtime-card-head"><span>{title}</span><b>{values.length}</b></div>
      {values.slice(0, 12).map((value) => <code key={value}>{value}</code>)}
      {values.length === 0 && <span>none</span>}
    </div>
  );
}

function DocHealthPill({ label, value }: { label: string; value?: boolean }) {
  return (
    <div className={`ion-project-doc-health-pill is-${value ? 'ready' : 'missing'}`}>
      <span>{label}</span>
      <b>{value ? 'yes' : 'missing'}</b>
    </div>
  );
}

function DocRowList({ docs, emptyLabel }: { docs: IonProjectDocRow[]; emptyLabel: string }) {
  if (!docs.length) return <div className="ion-vnext-empty-inline">{emptyLabel}</div>;
  return (
    <div className="ion-project-doc-list">
      {docs.map((doc, index) => (
        <article className={`ion-project-doc-row is-${statusClass(doc.kind)}`} key={`${doc.path ?? doc.rel_path ?? doc.title}-${index}`}>
          <div>
            <span>{doc.kind ?? 'doc'}{doc.primary ? ' / primary' : ''}</span>
            <b>{doc.title ?? doc.rel_path ?? 'Documentation'}</b>
          </div>
          {doc.excerpt && <p>{doc.excerpt}</p>}
          <code>{doc.path ?? doc.rel_path ?? 'path pending'}</code>
        </article>
      ))}
    </div>
  );
}

function ReferenceList({ references }: { references: IonProjectDocReference[] }) {
  if (!references.length) return <div className="ion-vnext-empty-inline">NO REFERENCES PROJECTED</div>;
  return (
    <div className="ion-project-reference-list">
      {references.slice(0, 18).map((reference, index) => (
        <div className="ion-project-reference-row" key={`${reference.target ?? reference.label}-${index}`}>
          <span>{reference.type ?? 'reference'}</span>
          <b>{reference.label ?? reference.type ?? 'Reference'}</b>
          {reference.detail && <p>{reference.detail}</p>}
          <code>{reference.target ?? 'target pending'}</code>
        </div>
      ))}
    </div>
  );
}

function SpecialistLaneList({ lanes, packetStatus }: { lanes: ProjectSpecialistLane[]; packetStatus: string }) {
  return (
    <div className="ion-project-specialist-list">
      {lanes.map((lane) => (
        <article className="ion-project-specialist-row" key={lane.laneId}>
          <div>
            <span>{lane.role}</span>
            <b>{lane.label}</b>
          </div>
          <p>{lane.objective}</p>
          <code>{lane.laneId} / {packetStatus}</code>
        </article>
      ))}
    </div>
  );
}

function PathRow({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="ion-project-path-row">
      <span>{label}</span>
      <code>{text(value, '')}</code>
    </div>
  );
}

function RecordList({ title, records = [], primary = 'name', secondary = 'status' }: { title: string; records?: Array<Record<string, unknown> | object>; primary?: string; secondary?: string }) {
  return (
    <div className="ion-project-record-list">
      <div className="ion-runtime-card-head"><span>{title}</span><b>{records.length}</b></div>
      {records.map((item, index) => {
        const record = item as Record<string, unknown>;
        return (
          <div className="ion-codex-record" key={`${title}-${String(record.path ?? record[primary] ?? index)}`}>
            <b>{text(record[primary], `item-${index + 1}`)}</b>
            <span>{text(record[secondary] ?? record.version_token ?? record.source_id, '')}</span>
            <code>{text(record.path ?? record.rel_path ?? '', '')}</code>
          </div>
        );
      })}
      {records.length === 0 && <div className="ion-vnext-empty-inline">NONE FOUND</div>}
    </div>
  );
}

function ProjectCard({ project, compact = false, onOpenVNext }: { project: IonProjectCockpitProject; compact?: boolean; onOpenVNext?: () => void }) {
  const primaryHref = project.route_href && !project.route_href.startsWith('#') ? project.route_href : undefined;
  return (
    <article className={`ion-vnext-project-card is-${statusClass(project.status)}${compact ? ' is-compact' : ''}`}>
      <span>{project.kind ?? project.status ?? 'projected'}</span>
      <b>{project.label ?? project.project_id}</b>
      {!compact && <p>{project.summary ?? 'No project summary projected.'}</p>}
      <div className="ion-vnext-packet-meta">
        <small>{project.status ?? 'projected'}</small>
        {typeof project.package_root_count === 'number' && <small>{project.package_root_count} packages</small>}
        {typeof project.launchable_count === 'number' && <small>{project.launchable_count} launchers</small>}
        {typeof project.family_count === 'number' && <small>{project.family_count} families</small>}
      </div>
      <code>{project.current_packet ?? project.path ?? project.source ?? 'no current packet'}</code>
      {!compact && (
        <div className="ion-vnext-project-actions">
          {project.project_id === 'ion_vnext' && <button type="button" onClick={onOpenVNext}>Open vNext</button>}
          {primaryHref && <a href={primaryHref}>{project.project_id === 'application_dev' ? 'Bridge' : 'Open'}</a>}
          {project.launcher_url && <a href={project.launcher_url} target="_blank" rel="noreferrer">Launcher</a>}
          {project.preview_href && <a href={project.preview_href}>Preview</a>}
          {project.app_catalog_url && <a href={project.app_catalog_url}>Catalog</a>}
        </div>
      )}
    </article>
  );
}

function organizedProjectPath(family: IonProjectPortfolioFamily | undefined, domain: IonProjectPortfolioDomain | undefined, root: string | undefined) {
  if (!family || !root) return '';
  const domainFolder = domain?.folder ?? slugText(family.domain_id ?? family.group_id ?? 'project-domain');
  return `${root}/domains/${domainFolder}/${slugText(family.label ?? family.family_id)}`;
}

function projectFamilyHref(family: IonProjectPortfolioFamily | undefined) {
  if (!family?.family_id) return '/projects';
  return `/projects/family/${encodeURIComponent(family.family_id)}`;
}

function mergeLaunchRecords(...sets: IonProjectLauncherRecord[][]) {
  const byId = new Map<string, IonProjectLauncherRecord>();
  sets.flat().forEach((record) => {
    const key = record.launch_id ?? `${record.path ?? ''}:${record.port ?? ''}`;
    if (!key.trim()) return;
    byId.set(key, record);
  });
  return Array.from(byId.values()).sort((left, right) => {
    const leftRunning = left.running ? 0 : 1;
    const rightRunning = right.running ? 0 : 1;
    if (leftRunning !== rightRunning) return leftRunning - rightRunning;
    return String(right.updated_at ?? '').localeCompare(String(left.updated_at ?? ''));
  });
}

function compactDocRows(rows: IonProjectDocRow[] | undefined) {
  const byPath = new Map<string, IonProjectDocRow>();
  (rows ?? []).forEach((row) => {
    const key = String(row.path ?? row.rel_path ?? row.title ?? '').trim();
    if (!key || byPath.has(key)) return;
    byPath.set(key, row);
  });
  return Array.from(byPath.values());
}

function compactReferences(rows: IonProjectDocReference[]) {
  const byTarget = new Map<string, IonProjectDocReference>();
  rows.forEach((row) => {
    const key = String(row.target ?? row.label ?? '').trim();
    if (!key || byTarget.has(key)) return;
    byTarget.set(key, row);
  });
  return Array.from(byTarget.values());
}

function launchKeyForVersion(version: IonProjectPortfolioVersion | undefined) {
  if (!version) return '';
  return String(version.launch?.project_path ?? version.path ?? version.launch?.version_id ?? version.version_id ?? version.project_id ?? 'launch');
}

function versionKey(version: IonProjectPortfolioVersion | undefined) {
  if (!version) return '';
  return String(version.version_id ?? version.project_id ?? version.path ?? version.version_token ?? 'version');
}

function slugText(value: unknown) {
  return String(value ?? 'project').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'project';
}

function MissionCard({ mission, compact = false }: { mission: IonProjectCockpitMission; compact?: boolean }) {
  return (
    <article className={`ion-vnext-mission-card is-${statusClass(mission.status)}${compact ? ' is-compact' : ''}`}>
      <span>{mission.status ?? mission.mission_type ?? 'mapped'}</span>
      <b>{mission.label ?? mission.mission_id}</b>
      {!compact && <p>{mission.summary ?? 'No mission summary projected.'}</p>}
      <div className="ion-vnext-packet-meta">
        <small>{mission.packet_count ?? 0} packets</small>
        <small>{mission.epoch_count ?? 0} epochs</small>
        <small>{mission.protocol_count ?? 0} protocols</small>
        <small>{mission.context_package_count ?? 0} contexts</small>
      </div>
      {!compact && <ChipRow values={mission.evidence_refs ?? []} />}
    </article>
  );
}

function BlockerCard({ blocker, compact = false }: { blocker: IonProjectCockpitBlocker; compact?: boolean }) {
  return (
    <article className={`ion-vnext-blocker-card is-${statusClass(blocker.status)}${blocker.derived ? ' is-derived' : ''}${compact ? ' is-compact' : ''}`}>
      <span>{blocker.severity ?? blocker.status ?? 'open'}</span>
      <b>{blocker.title ?? blocker.blocker_id}</b>
      {!compact && <p>{blocker.detail ?? blocker.unlock_condition ?? 'No detail projected.'}</p>}
      <div className="ion-vnext-packet-meta">
        <small>{blocker.status ?? 'open'}</small>
        <small>{blocker.derived ? 'derived' : 'managed'}</small>
        <small>{blocker.owner_route ?? 'route unknown'}</small>
      </div>
      {!compact && <p>{blocker.required_next_action ?? blocker.unlock_condition ?? ''}</p>}
      <code>{blocker.latest_packet ?? blocker.blocker_id}</code>
    </article>
  );
}

function QuestionCard({ question, compact = false }: { question: IonProjectCockpitQuestion; compact?: boolean }) {
  return (
    <article className={`ion-vnext-question-card is-${statusClass(question.status)}${compact ? ' is-compact' : ''}`}>
      <span>{question.priority ?? 'P2_NORMAL'}</span>
      <b>{question.question_text ?? question.question_id}</b>
      {!compact && <p>{question.context ?? question.resolution ?? 'No context projected.'}</p>}
      <div className="ion-vnext-packet-meta">
        <small>{question.status ?? 'open'}</small>
        <small>{question.needed_from ?? 'route unknown'}</small>
        <small>{question.blocking?.length ?? 0} blocking refs</small>
      </div>
    </article>
  );
}

function TimelineCard({ event }: { event: IonProjectCockpitTimelineEvent }) {
  return (
    <article className={`ion-vnext-timeline-card is-${statusClass(event.status)}`}>
      <div className="ion-vnext-timeline-head">
        <span>{event.event_type ?? 'event'}</span>
        <b>{event.title ?? event.event_id}</b>
        <small>{event.occurred_at ?? 'no time'}</small>
      </div>
      <p>{event.detail ?? event.source ?? 'No detail projected.'}</p>
      <ChipRow values={event.evidence_refs ?? []} />
    </article>
  );
}

function ReceiptCard({ receipt }: { receipt: Record<string, unknown> }) {
  return (
    <article className="ion-vnext-receipt-card">
      <span>{String(receipt.action ?? 'recorded')}</span>
      <b>{String(receipt.receipt_id ?? receipt.record_id ?? 'receipt')}</b>
      <p>{String(receipt.record_type ?? '')} / {String(receipt.record_id ?? '')}</p>
      <code>{String(receipt.path ?? '')}</code>
    </article>
  );
}

function LaneCard({ lane }: { lane: IonVNextLane }) {
  return (
    <article className={`ion-vnext-lane-card is-${statusClass(lane.status)}`}>
      <span>{lane.status}</span>
      <b>{lane.label}</b>
      <p>{lane.posture ?? 'posture unavailable'}</p>
      <code>{lane.evidence_path ?? 'no evidence path'}</code>
    </article>
  );
}

function EpochCard({ epoch, compact = false }: { epoch: IonVNextLongHorizonEpoch; compact?: boolean }) {
  return (
    <article className={`ion-vnext-epoch-card${compact ? ' is-compact' : ''}`}>
      <span>{epoch.family_id ?? 'mission_family_unknown'}</span>
      <b>{epoch.epoch_id ?? 'epoch'} / {epoch.row_start ?? '?'}-{epoch.row_end ?? '?'}</b>
      <div className="ion-vnext-packet-meta">
        <small>{epoch.date_start ?? 'unknown'} to {epoch.date_end ?? 'unknown'}</small>
        <small>{epoch.row_count ?? 0} rows</small>
      </div>
      {!compact && (
        <div className="ion-vnext-epoch-summary-stack">
          {(epoch.summaries ?? []).map((summary) => (
            <p key={`${summary.id ?? 'summary'}-${summary.summary ?? ''}`}>{summary.id ? `${summary.id}: ` : ''}{summary.summary ?? 'No summary projected.'}</p>
          ))}
        </div>
      )}
    </article>
  );
}

function ProtocolRow({ row }: { row: IonVNextProtocolRow }) {
  return (
    <article className="ion-vnext-protocol-row">
      <span>{row.kind ?? 'doc'}</span>
      <b>{row.title ?? row.name ?? row.path}</b>
      <small>{row.family_id ?? 'family_unknown'} / {row.authority ?? 'no authority tag'} / {row.status ?? 'no status'}</small>
      <code>{row.path}</code>
    </article>
  );
}

function ContextPackageCard({ item }: { item: VNextContextPackage }) {
  return (
    <article className="ion-vnext-context-card">
      <span>{item.context_type ?? 'context'}</span>
      <b>{item.package_id ?? 'package'}</b>
      <p>{item.load_policy ?? 'No load policy projected.'}</p>
      <ChipRow values={(item.path_refs ?? []).slice(0, 6)} />
    </article>
  );
}

function DocumentationSurfaceCard({ surface }: { surface: VNextDocumentationSurface }) {
  return (
    <article className={`ion-vnext-doc-card is-${surface.exists ? 'present' : 'missing'}`}>
      <span>{surface.exists ? 'present' : 'missing'}</span>
      <b>{surface.label ?? surface.surface_id}</b>
      <p>{surface.file_count ?? 0} files</p>
      <code>{surface.root ?? 'no root'}</code>
      <ChipRow values={(surface.sample_paths ?? []).slice(0, 5)} />
    </article>
  );
}

function SourceRow({ itemKey, present, path }: { itemKey: string; present: boolean; path?: string }) {
  return (
    <div className={`ion-vnext-source-row is-${present ? 'present' : 'missing'}`}>
      <span>{itemKey.replace(/_/g, ' ')}</span>
      <b>{present ? 'present' : 'missing'}</b>
      <code>{path ?? itemKey}</code>
    </div>
  );
}

function DriftGuard({ guard }: { guard: IonVNextDriftGuard }) {
  return (
    <article className={`ion-vnext-guard-card is-${statusClass(guard.status)}`}>
      <span>{guard.status}</span>
      <b>{guard.guard_id.replace(/_/g, ' ')}</b>
      <p>{guard.detail ?? 'No guard detail projected.'}</p>
      <ChipRow values={(guard.items ?? []).slice(0, 8)} />
    </article>
  );
}

function ChipRow({ values }: { values: string[] }) {
  if (!values.length) return null;
  return <div className="ion-vnext-chip-row">{values.map((value) => <small key={value}>{value}</small>)}</div>;
}

function isOpenStatus(value?: string) {
  return !['closed', 'resolved', 'complete'].includes(String(value ?? 'open').toLowerCase());
}

function statusClass(value?: string) {
  return String(value ?? 'unknown').toLowerCase().replace(/[^a-z0-9_-]/g, '-');
}

function text(value: unknown, fallback = 'unknown') {
  if (Array.isArray(value)) return value.map((item) => text(item)).join(', ');
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return fallback;
}

function readStoredList(key: string): string[] {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem(key) || '[]');
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === 'string') : [];
  } catch {
    return [];
  }
}

function readStoredTextRecord(key: string): Record<string, string> {
  if (typeof window === 'undefined') return {};
  try {
    const parsed = JSON.parse(window.localStorage.getItem(key) || '{}');
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    return Object.fromEntries(Object.entries(parsed).filter(([, value]) => typeof value === 'string')) as Record<string, string>;
  } catch {
    return {};
  }
}

function readStoredImageRecord(key: string): Record<string, string[]> {
  if (typeof window === 'undefined') return {};
  try {
    const parsed = JSON.parse(window.localStorage.getItem(key) || '{}');
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {};
    return Object.fromEntries(
      Object.entries(parsed).map(([itemKey, value]) => [
        itemKey,
        Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string' && item.startsWith('data:image/')).slice(-6) : [],
      ]),
    ) as Record<string, string[]>;
  } catch {
    return {};
  }
}
