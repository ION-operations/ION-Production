import { useJOCStore } from '../../store/jocStore';
import { NAV_GROUPS, getGroupForPage, type NavGroup } from './TopBar';

/**
 * PageSubBar — replaces the old PageTabs.
 * Shows sub-page tabs for whichever group the current page belongs to.
 * Clicking a sub-tab navigates to that page within the group.
 */
export function PageSubBar() {
    const { addTab, activeTab, tabs } = useJOCStore();

    // Find the current page and its group
    const activeTabData = tabs.find(t => t.id === activeTab);
    const currentPage = activeTabData?.type || 'dashboard';
    const activeGroup: NavGroup | undefined = getGroupForPage(currentPage);

    if (!activeGroup) return null;

    const handleSubTabClick = (type: string, label: string) => {
        addTab({
            id: type,
            type: type as any,
            label,
            closable: type !== 'dashboard',
        });
    };

    return (
        <div className="page-sub-bar">
            {activeGroup.pages.map(page => (
                <button
                    key={page.type}
                    className={`sub-bar-tab ${currentPage === page.type ? 'active' : ''}`}
                    onClick={() => handleSubTabClick(page.type, page.label)}
                >
                    {page.label}
                </button>
            ))}
        </div>
    );
}
