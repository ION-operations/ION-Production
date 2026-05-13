/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Template Library
   Drawer with premade elements, buttons, menus, pages, layouts etc.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState } from 'react';
import { useEditorStore } from '../store/editorStore';
import {
    IconTemplates, IconTplButton, IconTplCard, IconTplNav, IconTplHero,
    IconTplForm, IconTplLayout, IconTplGrid, IconTplFooter, IconTplModal,
    IconSearch, IconPlus, IconStar, IconChevron,
} from '../icons/Icons';

// ─── Template data ──────────────────────────────────────────────────────────
type TemplateCategory = 'buttons' | 'cards' | 'navigation' | 'heroes' | 'forms' | 'layouts' | 'grids' | 'footers' | 'modals';

interface TemplateItem {
    id: string;
    name: string;
    description: string;
    category: TemplateCategory;
    tags: string[];
    favorite?: boolean;
    preview: React.ReactNode;
}

const CATEGORIES: { key: TemplateCategory; label: string; Icon: React.FC<{ size?: number }> }[] = [
    { key: 'buttons', label: 'Buttons', Icon: IconTplButton },
    { key: 'cards', label: 'Cards', Icon: IconTplCard },
    { key: 'navigation', label: 'Navigation', Icon: IconTplNav },
    { key: 'heroes', label: 'Heroes', Icon: IconTplHero },
    { key: 'forms', label: 'Forms', Icon: IconTplForm },
    { key: 'layouts', label: 'Layouts', Icon: IconTplLayout },
    { key: 'grids', label: 'Grids', Icon: IconTplGrid },
    { key: 'footers', label: 'Footers', Icon: IconTplFooter },
    { key: 'modals', label: 'Modals', Icon: IconTplModal },
];

// ─── Mini preview components ────────────────────────────────────────────────
const MiniButton = ({ variant, label }: { variant: 'primary' | 'secondary' | 'ghost' | 'danger' | 'gradient'; label: string }) => {
    const styles: Record<string, React.CSSProperties> = {
        primary: { background: 'var(--ob-accent)', color: '#fff', border: 'none' },
        secondary: { background: 'transparent', color: 'var(--ob-text-primary)', border: '1px solid var(--ob-border)' },
        ghost: { background: 'transparent', color: 'var(--ob-accent)', border: '1px solid transparent' },
        danger: { background: 'hsla(0,80%,55%,0.15)', color: 'hsl(0,80%,65%)', border: '1px solid hsla(0,80%,55%,0.3)' },
        gradient: { background: 'linear-gradient(135deg, var(--ob-accent), var(--ob-purple))', color: '#fff', border: 'none' },
    };
    return (
        <div style={{
            ...styles[variant], padding: '4px 10px', borderRadius: '6px',
            fontSize: '9px', fontWeight: 600, textAlign: 'center', cursor: 'default',
        }}>{label}</div>
    );
};

const MiniCard = ({ variant }: { variant: 'basic' | 'media' | 'pricing' | 'testimonial' }) => (
    <div style={{
        background: 'var(--ob-bg-elevated)', border: '1px solid var(--ob-border)',
        borderRadius: '6px', padding: '6px', width: '100%',
    }}>
        {variant === 'media' && (
            <div style={{
                height: 28, borderRadius: '4px', marginBottom: 4,
                background: 'linear-gradient(135deg, hsla(215,60%,40%,0.3), hsla(265,50%,40%,0.3))',
            }} />
        )}
        {variant === 'pricing' && (
            <div style={{ textAlign: 'center', fontSize: '12px', fontWeight: 700, color: 'var(--ob-accent)', marginBottom: 2 }}>$29</div>
        )}
        {variant === 'testimonial' && (
            <div style={{ fontSize: '7px', color: 'var(--ob-text-tertiary)', fontStyle: 'italic', marginBottom: 2 }}>"Amazing product..."</div>
        )}
        <div style={{ height: 3, width: '70%', background: 'var(--ob-border)', borderRadius: 2, marginBottom: 3 }} />
        <div style={{ height: 2, width: '50%', background: 'var(--ob-border-subtle)', borderRadius: 2 }} />
    </div>
);

const MiniNav = ({ variant }: { variant: 'horizontal' | 'sidebar' | 'burger' }) => (
    <div style={{
        background: 'var(--ob-bg-elevated)', border: '1px solid var(--ob-border)',
        borderRadius: '4px', padding: '4px 6px', display: 'flex', alignItems: 'center', gap: 6,
        width: '100%',
    }}>
        <div style={{ width: 10, height: 10, borderRadius: '50%', background: 'var(--ob-accent)', flexShrink: 0 }} />
        {variant === 'horizontal' && (
            <div style={{ display: 'flex', gap: 4, flex: 1 }}>
                {[0.6, 0.5, 0.4].map((op, i) => <div key={i} style={{ height: 2, width: 16, background: 'var(--ob-text-primary)', opacity: op, borderRadius: 1 }} />)}
            </div>
        )}
        {variant === 'sidebar' && <div style={{ height: 2, width: '50%', background: 'var(--ob-border)', borderRadius: 1 }} />}
        {variant === 'burger' && (
            <div style={{ marginLeft: 'auto', display: 'flex', flexDirection: 'column', gap: 2 }}>
                {[0, 1, 2].map((i) => <div key={i} style={{ height: 1.5, width: 10, background: 'var(--ob-text-primary)', borderRadius: 1 }} />)}
            </div>
        )}
    </div>
);

const MiniHero = ({ variant }: { variant: 'centered' | 'split' | 'gradient' }) => (
    <div style={{
        background: variant === 'gradient'
            ? 'linear-gradient(135deg, hsla(215,60%,20%,0.6), hsla(265,50%,20%,0.6))'
            : 'var(--ob-bg-elevated)',
        border: '1px solid var(--ob-border)', borderRadius: '4px', padding: '8px',
        textAlign: variant === 'split' ? 'left' : 'center', width: '100%',
    }}>
        <div style={{ height: 4, width: variant === 'split' ? '50%' : '60%', background: 'var(--ob-text-primary)', borderRadius: 2, marginBottom: 3, ...(variant !== 'split' ? { margin: '0 auto 3px' } : {}) }} />
        <div style={{ height: 2, width: variant === 'split' ? '40%' : '40%', background: 'var(--ob-text-tertiary)', borderRadius: 2, marginBottom: 4, ...(variant !== 'split' ? { margin: '0 auto 4px' } : {}) }} />
        <div style={{
            height: 8, width: 24, borderRadius: 4,
            background: 'var(--ob-accent)',
            ...(variant !== 'split' ? { margin: '0 auto' } : {}),
        }} />
    </div>
);

const MiniForm = () => (
    <div style={{ background: 'var(--ob-bg-elevated)', border: '1px solid var(--ob-border)', borderRadius: '4px', padding: '6px', width: '100%' }}>
        {[0, 1].map((i) => (
            <div key={i} style={{ marginBottom: 4 }}>
                <div style={{ height: 2, width: '30%', background: 'var(--ob-text-tertiary)', borderRadius: 1, marginBottom: 2 }} />
                <div style={{ height: 10, border: '1px solid var(--ob-border)', borderRadius: 3, background: 'var(--ob-bg-base)' }} />
            </div>
        ))}
        <div style={{ height: 10, borderRadius: 4, background: 'var(--ob-accent)', marginTop: 2 }} />
    </div>
);

const MiniLayout = ({ variant }: { variant: 'sidebar' | 'dashboard' | 'magazine' }) => (
    <div style={{
        background: 'var(--ob-bg-elevated)', border: '1px solid var(--ob-border)',
        borderRadius: '4px', display: 'flex', gap: 2, padding: '3px', height: 50, width: '100%',
    }}>
        {variant === 'sidebar' && <>
            <div style={{ width: 14, borderRadius: 2, background: 'var(--ob-bg-panel)' }} />
            <div style={{ flex: 1, borderRadius: 2, background: 'var(--ob-bg-base)' }} />
        </>}
        {variant === 'dashboard' && <>
            <div style={{ width: 14, borderRadius: 2, background: 'var(--ob-bg-panel)' }} />
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <div style={{ height: '40%', display: 'flex', gap: 2 }}>
                    <div style={{ flex: 1, borderRadius: 2, background: 'var(--ob-bg-base)' }} />
                    <div style={{ flex: 1, borderRadius: 2, background: 'var(--ob-bg-base)' }} />
                </div>
                <div style={{ flex: 1, borderRadius: 2, background: 'var(--ob-bg-base)' }} />
            </div>
        </>}
        {variant === 'magazine' && <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 2 }}>
            <div style={{ gridRow: '1/3', borderRadius: 2, background: 'var(--ob-bg-base)' }} />
            <div style={{ borderRadius: 2, background: 'var(--ob-bg-base)' }} />
            <div style={{ borderRadius: 2, background: 'var(--ob-bg-base)' }} />
        </div>}
    </div>
);

// ─── Build templates ────────────────────────────────────────────────────────
const TEMPLATES: TemplateItem[] = [
    // Buttons
    { id: 'btn-primary', name: 'Primary Button', description: 'Solid filled CTA button', category: 'buttons', tags: ['cta', 'solid'], preview: <MiniButton variant="primary" label="Get Started" /> },
    { id: 'btn-secondary', name: 'Secondary Button', description: 'Outlined subtle action', category: 'buttons', tags: ['outline', 'subtle'], preview: <MiniButton variant="secondary" label="Learn More" /> },
    { id: 'btn-ghost', name: 'Ghost Button', description: 'Transparent text-only', category: 'buttons', tags: ['minimal', 'text'], preview: <MiniButton variant="ghost" label="Cancel" /> },
    { id: 'btn-danger', name: 'Danger Button', description: 'Destructive action warning', category: 'buttons', tags: ['destructive', 'caution'], preview: <MiniButton variant="danger" label="Delete" /> },
    { id: 'btn-gradient', name: 'Gradient Button', description: 'Premium gradient accent', category: 'buttons', tags: ['gradient', 'premium'], preview: <MiniButton variant="gradient" label="Upgrade →" />, favorite: true },
    // Cards
    { id: 'card-basic', name: 'Basic Card', description: 'Simple content container', category: 'cards', tags: ['container', 'simple'], preview: <MiniCard variant="basic" /> },
    { id: 'card-media', name: 'Media Card', description: 'Image header with content', category: 'cards', tags: ['image', 'preview'], preview: <MiniCard variant="media" />, favorite: true },
    { id: 'card-pricing', name: 'Pricing Card', description: 'Plan comparison element', category: 'cards', tags: ['pricing', 'plan'], preview: <MiniCard variant="pricing" /> },
    { id: 'card-testimonial', name: 'Testimonial Card', description: 'Quote with attribution', category: 'cards', tags: ['quote', 'social'], preview: <MiniCard variant="testimonial" /> },
    // Navigation
    { id: 'nav-horizontal', name: 'Horizontal Nav', description: 'Classic top navigation bar', category: 'navigation', tags: ['topbar', 'classic'], preview: <MiniNav variant="horizontal" />, favorite: true },
    { id: 'nav-sidebar', name: 'Sidebar Nav', description: 'Collapsible side navigation', category: 'navigation', tags: ['sidebar', 'collapsible'], preview: <MiniNav variant="sidebar" /> },
    { id: 'nav-burger', name: 'Burger Menu', description: 'Mobile hamburger menu', category: 'navigation', tags: ['mobile', 'responsive'], preview: <MiniNav variant="burger" /> },
    // Heroes
    { id: 'hero-centered', name: 'Centered Hero', description: 'Full-width centered headline', category: 'heroes', tags: ['centered', 'headline'], preview: <MiniHero variant="centered" />, favorite: true },
    { id: 'hero-split', name: 'Split Hero', description: 'Text left, media right', category: 'heroes', tags: ['split', 'asymmetric'], preview: <MiniHero variant="split" /> },
    { id: 'hero-gradient', name: 'Gradient Hero', description: 'Gradient background hero', category: 'heroes', tags: ['gradient', 'dramatic'], preview: <MiniHero variant="gradient" /> },
    // Forms
    { id: 'form-login', name: 'Login Form', description: 'Email + password fields', category: 'forms', tags: ['auth', 'login'], preview: <MiniForm /> },
    { id: 'form-contact', name: 'Contact Form', description: 'Name, email, message', category: 'forms', tags: ['contact', 'message'], preview: <MiniForm />, favorite: true },
    // Layouts
    { id: 'layout-sidebar', name: 'Sidebar Layout', description: 'Left nav + content area', category: 'layouts', tags: ['sidebar', 'app'], preview: <MiniLayout variant="sidebar" /> },
    { id: 'layout-dashboard', name: 'Dashboard Layout', description: 'Cards + charts grid', category: 'layouts', tags: ['dashboard', 'data'], preview: <MiniLayout variant="dashboard" />, favorite: true },
    { id: 'layout-magazine', name: 'Magazine Layout', description: 'Asymmetric editorial grid', category: 'layouts', tags: ['editorial', 'asymmetric'], preview: <MiniLayout variant="magazine" /> },
    // Grids
    { id: 'grid-features', name: 'Feature Grid', description: '3-column feature showcase', category: 'grids', tags: ['features', '3-col'], preview: <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 3 }}>{[0, 1, 2].map(i => <div key={i} style={{ height: 28, borderRadius: 3, background: 'var(--ob-bg-elevated)', border: '1px solid var(--ob-border)' }} />)}</div> },
    { id: 'grid-gallery', name: 'Photo Gallery', description: 'Masonry-style photo grid', category: 'grids', tags: ['gallery', 'masonry'], preview: <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>{[24, 32, 32, 24].map((h, i) => <div key={i} style={{ height: h, borderRadius: 3, background: 'linear-gradient(135deg, hsla(215,50%,30%,0.3), hsla(265,40%,30%,0.3))' }} />)}</div>, favorite: true },
    // Footers
    { id: 'footer-columns', name: 'Column Footer', description: 'Multi-column link footer', category: 'footers', tags: ['links', 'columns'], preview: <div style={{ display: 'flex', gap: 6, padding: '4px', background: 'var(--ob-bg-elevated)', borderRadius: 3, border: '1px solid var(--ob-border)' }}>{[0, 1, 2].map(i => <div key={i} style={{ flex: 1 }}>{[0, 1].map(j => <div key={j} style={{ height: 2, width: `${60 + j * 10}%`, background: 'var(--ob-text-tertiary)', borderRadius: 1, marginBottom: 3, opacity: 1 - j * 0.3 }} />)}</div>)}</div>, favorite: true },
    // Modals
    { id: 'modal-confirm', name: 'Confirm Dialog', description: 'Yes/No confirmation modal', category: 'modals', tags: ['confirm', 'dialog'], preview: <div style={{ background: 'var(--ob-bg-elevated)', border: '1px solid var(--ob-border)', borderRadius: 6, padding: 6, textAlign: 'center' }}><div style={{ height: 3, width: '50%', margin: '0 auto 4px', background: 'var(--ob-text-primary)', borderRadius: 1 }} /><div style={{ height: 2, width: '70%', margin: '0 auto 6px', background: 'var(--ob-text-tertiary)', borderRadius: 1 }} /><div style={{ display: 'flex', gap: 3 }}><div style={{ flex: 1, height: 10, borderRadius: 4, border: '1px solid var(--ob-border)' }} /><div style={{ flex: 1, height: 10, borderRadius: 4, background: 'var(--ob-accent)' }} /></div></div> },
];

// ─── Component ──────────────────────────────────────────────────────────────
export default function TemplateLibrary() {
    const [searchQuery, setSearchQuery] = useState('');
    const [activeCategory, setActiveCategory] = useState<TemplateCategory | 'all'>('all');
    const [showFavorites, setShowFavorites] = useState(false);
    const [expandedCats, setExpandedCats] = useState<Set<TemplateCategory>>(new Set(['buttons', 'cards', 'navigation']));

    const toggleCat = (cat: TemplateCategory) => {
        setExpandedCats((prev) => {
            const n = new Set(prev);
            n.has(cat) ? n.delete(cat) : n.add(cat);
            return n;
        });
    };

    const filtered = TEMPLATES.filter((t) => {
        if (showFavorites && !t.favorite) return false;
        if (activeCategory !== 'all' && t.category !== activeCategory) return false;
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            return t.name.toLowerCase().includes(q) || t.description.toLowerCase().includes(q) || t.tags.some(tag => tag.includes(q));
        }
        return true;
    });

    const groupedByCategory = CATEGORIES.reduce((acc, cat) => {
        acc[cat.key] = filtered.filter((t) => t.category === cat.key);
        return acc;
    }, {} as Record<TemplateCategory, TemplateItem[]>);

    return (
        <div className="ob-template-library">
            {/* Header */}
            <div className="ob-panel-header">
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <IconTemplates size={12} />
                    Templates
                </span>
                <span style={{ fontSize: '9px', color: 'var(--ob-text-tertiary)' }}>
                    {filtered.length}
                </span>
            </div>

            {/* Search */}
            <div className="ob-tpl-search">
                <IconSearch size={12} style={{ opacity: 0.4, flexShrink: 0 }} />
                <input
                    className="ob-tpl-search-input"
                    placeholder="Search templates..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </div>

            {/* Filter bar */}
            <div className="ob-tpl-filters">
                <button
                    className={`ob-tpl-filter-btn${activeCategory === 'all' ? ' active' : ''}`}
                    onClick={() => setActiveCategory('all')}
                >All</button>
                <button
                    className={`ob-tpl-filter-btn fav${showFavorites ? ' active' : ''}`}
                    onClick={() => setShowFavorites(!showFavorites)}
                ><IconStar size={10} /></button>
                {CATEGORIES.map(({ key, label, Icon }) => (
                    <button
                        key={key}
                        className={`ob-tpl-filter-btn${activeCategory === key ? ' active' : ''}`}
                        onClick={() => setActiveCategory(activeCategory === key ? 'all' : key)}
                        title={label}
                    >
                        <Icon size={10} />
                    </button>
                ))}
            </div>

            {/* Template list */}
            <div className="ob-tpl-list">
                {CATEGORIES.map(({ key, label, Icon }) => {
                    const items = groupedByCategory[key];
                    if (items.length === 0) return null;
                    const isExpanded = expandedCats.has(key);
                    return (
                        <div key={key} className="ob-tpl-category">
                            <div className="ob-tpl-category-header" onClick={() => toggleCat(key)}>
                                <span style={{
                                    display: 'inline-flex', transform: isExpanded ? 'rotate(90deg)' : undefined,
                                    transition: 'transform 0.15s ease',
                                }}>
                                    <IconChevron size={8} />
                                </span>
                                <Icon size={11} />
                                <span>{label}</span>
                                <span className="ob-tpl-category-count">{items.length}</span>
                            </div>
                            {isExpanded && (
                                <div className="ob-tpl-items">
                                    {items.map((tpl) => (
                                        <div key={tpl.id} className="ob-tpl-item" draggable title={tpl.description}>
                                            <div className="ob-tpl-preview">
                                                {tpl.preview}
                                            </div>
                                            <div className="ob-tpl-meta">
                                                <span className="ob-tpl-name">{tpl.name}</span>
                                                <span className="ob-tpl-desc">{tpl.description}</span>
                                            </div>
                                            {tpl.favorite && <span className="ob-tpl-fav-star"><IconStar size={8} /></span>}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
