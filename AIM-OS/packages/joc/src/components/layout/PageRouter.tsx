import { useJOCStore } from '../../store/jocStore';
import { DashboardPage } from '../../pages/DashboardPage';
import { SessionPage } from '../../pages/SessionPage';
import { ComputePage } from '../../pages/ComputePage';
import { DispatchPage } from '../../pages/DispatchPage';
import { SynthesizerPage } from '../../pages/SynthesizerPage';
import { AgentCommsPage } from '../../pages/AgentCommsPage';
import { SessionHealthPage } from '../../pages/SessionHealthPage';
import { AutoContextPage } from '../../pages/AutoContextPage';
import { CredentialVaultPage } from '../../pages/CredentialVaultPage';
import { CliTerminalPage } from '../../pages/CliTerminalPage';
import { SettingsPage } from '../../pages/SettingsPage';
import { MissionBuilderPage } from '../../pages/MissionBuilderPage';
import { WelcomePage } from '../../pages/WelcomePage';
import { CodeEditor } from '../CodeEditor';
import { SystemAtlas } from '../SystemAtlas';
import { ContextGraphPage } from '../../pages/ContextGraphPage';
import { CalendarPage } from '../../pages/CalendarPage';
import { OraclePage } from '../../pages/OraclePage';
import AgentBuilderPage from '../../pages/AgentBuilderPage';
import { SurfaceEngineDemo } from '../../pages/SurfaceEngineDemo';
import { ContextLabPage } from '../../pages/ContextLabPage';
import { InfraConsolePage } from '../../pages/InfraConsolePage';
import { AgentWorkforcePage } from '../../pages/AgentWorkforcePage';
import { IntelligenceMapPage } from '../../pages/IntelligenceMapPage';

export function PageRouter() {
    const { activeTab, tabs } = useJOCStore();
    const activeTabData = tabs.find(t => t.id === activeTab);

    if (!activeTabData) {
        return <DashboardPage />;
    }

    switch (activeTabData.type) {
        case 'dashboard':
            return <DashboardPage />;
        case 'session':
            return <SessionPage sessionId={activeTabData.data?.sessionId as string || 'chatgpt-session'} />;
        case 'mission':
        case 'dispatch':
            return <DispatchPage />;
        case 'compute':
            return <ComputePage />;
        case 'synthesizer':
            return <SynthesizerPage />;
        case 'comms':
            return <AgentCommsPage />;
        case 'health':
            return <SessionHealthPage />;
        case 'context':
            return <AutoContextPage />;
        case 'vault':
            return <CredentialVaultPage />;
        case 'cli':
            return <CliTerminalPage />;
        case 'settings':
            return <SettingsPage />;
        case 'mission-builder':
            return <MissionBuilderPage />;
        case 'welcome':
            return <WelcomePage />;
        case 'editor':
            return <CodeEditor />;
        case 'atlas':
            return <SystemAtlas />;
        case 'context-graph':
            return <ContextGraphPage />;
        case 'calendar':
            return <CalendarPage />;
        case 'oracle':
            return <OraclePage />;
        case 'agent-builder':
            return <AgentBuilderPage />;
        case 'surface-demo':
            return <SurfaceEngineDemo />;
        case 'context-lab':
            return <ContextLabPage />;
        case 'infra':
            return <InfraConsolePage />;
        case 'agent-workforce':
            return <AgentWorkforcePage />;
        case 'intelligence-map':
            return <IntelligenceMapPage />;
        default:
            return <DashboardPage />;
    }
}
