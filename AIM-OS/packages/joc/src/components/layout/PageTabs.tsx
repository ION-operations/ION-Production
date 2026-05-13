import { useJOCStore } from '../../store/jocStore';
import { RadarIcon, CloseIcon, PlusIcon } from '../icons';

const PAGE_ICONS: Record<string, React.ComponentType<{ size?: number }>> = {
    dashboard: RadarIcon,
};

export function PageTabs() {
    const { tabs, activeTab, setActiveTab, closeTab } = useJOCStore();

    return (
        <div className="page-tabs">
            {tabs.map(tab => {
                const Icon = PAGE_ICONS[tab.type] || RadarIcon;
                return (
                    <div
                        key={tab.id}
                        className={`page-tab ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <Icon size={14} />
                        <span>{tab.label}</span>
                        {tab.closable && (
                            <button
                                className="page-tab-close"
                                onClick={(e) => { e.stopPropagation(); closeTab(tab.id); }}
                            >
                                <CloseIcon size={10} />
                            </button>
                        )}
                    </div>
                );
            })}

            <button className="page-tab-add" title="New Tab">
                <PlusIcon size={14} />
            </button>
        </div>
    );
}
