/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Logo Studio
   Premium SVG logo builder and gallery showcase.
   Build masterpiece logos with radial gradients, geometric overlays,
   spectral effects, and export as pure SVG.
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState, useCallback, useMemo } from 'react';

// ─── Types ───────────────────────────────────────────────────────────────────
interface LogoPetal {
    angle: number;
    color1: string;
    color2: string;
    opacity: number;
    spread: number;
}

interface LogoConfig {
    name: string;
    petals: LogoPetal[];
    centerColor: string;
    centerGlow: number;
    bgColor: string;
    geometricOverlay: boolean;
    vignette: number;
    blur: number;
}

interface GalleryItem {
    id: string;
    name: string;
    description: string;
    config: LogoConfig;
}

// ─── Gallery of masterpiece logos ─────────────────────────────────────────────
const GALLERY: GalleryItem[] = [
    {
        id: 'convergence',
        name: 'The Convergence',
        description: 'OmniBuilder\'s signature — six spectral rays meeting at a nexus of creation.',
        config: {
            name: 'The Convergence',
            petals: [
                { angle: 300, color1: '#c4b5fd', color2: '#4c1d95', opacity: 0.92, spread: 55 },
                { angle: 0, color1: '#fda4af', color2: '#881337', opacity: 0.92, spread: 52 },
                { angle: 60, color1: '#fde68a', color2: '#78350f', opacity: 0.88, spread: 50 },
                { angle: 120, color1: '#bef264', color2: '#365314', opacity: 0.9, spread: 48 },
                { angle: 180, color1: '#67e8f9', color2: '#164e63', opacity: 0.92, spread: 55 },
                { angle: 240, color1: '#93c5fd', color2: '#1e3a5f', opacity: 0.9, spread: 50 },
            ],
            centerColor: '#ffffff', centerGlow: 90, bgColor: '#050508',
            geometricOverlay: true, vignette: 0.7, blur: 8,
        },
    },
    {
        id: 'aurora',
        name: 'Aurora Borealis',
        description: 'Northern lights — ethereal curtains of cyan, green, and violet.',
        config: {
            name: 'Aurora Borealis',
            petals: [
                { angle: 250, color1: '#a78bfa', color2: '#3730a3', opacity: 0.85, spread: 70 },
                { angle: 290, color1: '#67e8f9', color2: '#155e75', opacity: 0.95, spread: 65 },
                { angle: 330, color1: '#5eead4', color2: '#134e4a', opacity: 0.9, spread: 68 },
                { angle: 10, color1: '#86efac', color2: '#14532d', opacity: 0.88, spread: 60 },
                { angle: 50, color1: '#67e8f9', color2: '#0e7490', opacity: 0.8, spread: 55 },
            ],
            centerColor: '#e0f2fe', centerGlow: 70, bgColor: '#020617',
            geometricOverlay: false, vignette: 0.8, blur: 12,
        },
    },
    {
        id: 'ember',
        name: 'Dying Ember',
        description: 'A final burst of warmth — deep amber, crimson, and gold forged in darkness.',
        config: {
            name: 'Dying Ember',
            petals: [
                { angle: 280, color1: '#fbbf24', color2: '#92400e', opacity: 0.95, spread: 50 },
                { angle: 320, color1: '#f87171', color2: '#7f1d1d', opacity: 0.9, spread: 55 },
                { angle: 0, color1: '#fde68a', color2: '#78350f', opacity: 0.92, spread: 52 },
                { angle: 40, color1: '#fb923c', color2: '#7c2d12', opacity: 0.88, spread: 48 },
                { angle: 80, color1: '#ef4444', color2: '#450a0a', opacity: 0.85, spread: 50 },
                { angle: 180, color1: '#1c1917', color2: '#0c0a09', opacity: 0.3, spread: 40 },
                { angle: 220, color1: '#292524', color2: '#0a0908', opacity: 0.25, spread: 35 },
            ],
            centerColor: '#fef3c7', centerGlow: 80, bgColor: '#0a0604',
            geometricOverlay: false, vignette: 0.85, blur: 10,
        },
    },
    {
        id: 'deep-ocean',
        name: 'Deep Ocean',
        description: 'Abyssal depths — bioluminescent blues, teals, and phantom purples.',
        config: {
            name: 'Deep Ocean',
            petals: [
                { angle: 270, color1: '#818cf8', color2: '#312e81', opacity: 0.9, spread: 60 },
                { angle: 310, color1: '#67e8f9', color2: '#155e75', opacity: 0.95, spread: 55 },
                { angle: 350, color1: '#38bdf8', color2: '#0c4a6e', opacity: 0.88, spread: 58 },
                { angle: 30, color1: '#2dd4bf', color2: '#134e4a', opacity: 0.85, spread: 50 },
                { angle: 70, color1: '#818cf8', color2: '#1e1b4b', opacity: 0.8, spread: 52 },
                { angle: 140, color1: '#06b6d4', color2: '#083344', opacity: 0.75, spread: 45 },
                { angle: 200, color1: '#6366f1', color2: '#1e1b4b', opacity: 0.82, spread: 48 },
            ],
            centerColor: '#cffafe', centerGlow: 85, bgColor: '#020618',
            geometricOverlay: true, vignette: 0.75, blur: 10,
        },
    },
    {
        id: 'singularity',
        name: 'Singularity',
        description: 'An event horizon of creation — monochrome power with a single accent.',
        config: {
            name: 'Singularity',
            petals: [
                { angle: 0, color1: '#e2e8f0', color2: '#1e293b', opacity: 0.6, spread: 50 },
                { angle: 60, color1: '#cbd5e1', color2: '#0f172a', opacity: 0.5, spread: 48 },
                { angle: 120, color1: '#94a3b8', color2: '#020617', opacity: 0.55, spread: 52 },
                { angle: 180, color1: '#e2e8f0', color2: '#1e293b', opacity: 0.45, spread: 46 },
                { angle: 240, color1: '#818cf8', color2: '#3730a3', opacity: 0.95, spread: 60 },
                { angle: 300, color1: '#cbd5e1', color2: '#0f172a', opacity: 0.5, spread: 50 },
            ],
            centerColor: '#ffffff', centerGlow: 100, bgColor: '#020206',
            geometricOverlay: true, vignette: 0.9, blur: 7,
        },
    },
    {
        id: 'solar-flare',
        name: 'Solar Flare',
        description: 'Chromospheric eruption — hot pinks, electric yellows, and cosmic violet.',
        config: {
            name: 'Solar Flare',
            petals: [
                { angle: 260, color1: '#c084fc', color2: '#581c87', opacity: 0.9, spread: 55 },
                { angle: 300, color1: '#f472b6', color2: '#831843', opacity: 0.95, spread: 58 },
                { angle: 340, color1: '#fb7185', color2: '#9f1239', opacity: 0.92, spread: 52 },
                { angle: 20, color1: '#fbbf24', color2: '#92400e', opacity: 0.88, spread: 50 },
                { angle: 60, color1: '#facc15', color2: '#713f12', opacity: 0.85, spread: 48 },
                { angle: 120, color1: '#f472b6', color2: '#9d174d', opacity: 0.78, spread: 45 },
                { angle: 180, color1: '#a855f7', color2: '#3b0764', opacity: 0.72, spread: 42 },
            ],
            centerColor: '#fef9c3', centerGlow: 95, bgColor: '#0c0008',
            geometricOverlay: false, vignette: 0.7, blur: 9,
        },
    },
];

// ─── Logo Renderer (inline SVG) ──────────────────────────────────────────────
function LogoPreview({ config, size = 200 }: { config: LogoConfig; size?: number }) {
    const half = size / 2;
    const r = half * 0.88;
    const uid = useMemo(() => Math.random().toString(36).slice(2, 8), []);

    return (
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
            <defs>
                {config.petals.map((p, i) => (
                    <radialGradient key={i} id={`pg-${uid}-${i}`} cx="0.3" cy="0.3" r="0.7">
                        <stop offset="0%" stopColor={p.color1} stopOpacity="0.95" />
                        <stop offset="35%" stopColor={p.color1} stopOpacity="0.7" />
                        <stop offset="70%" stopColor={p.color2} stopOpacity="0.4" />
                        <stop offset="100%" stopColor={p.color2} stopOpacity="0" />
                    </radialGradient>
                ))}
                <radialGradient id={`nx-${uid}`} cx="0.5" cy="0.5" r="0.5">
                    <stop offset="0%" stopColor={config.centerColor} stopOpacity="1" />
                    <stop offset="15%" stopColor={config.centerColor} stopOpacity="0.6" />
                    <stop offset="40%" stopColor={config.centerColor} stopOpacity="0.15" />
                    <stop offset="100%" stopColor="#000" stopOpacity="0" />
                </radialGradient>
                <filter id={`fb-${uid}`} x="-40%" y="-40%" width="180%" height="180%">
                    <feGaussianBlur stdDeviation={config.blur * size / 512} />
                </filter>
                <filter id={`fg-${uid}`} x="-60%" y="-60%" width="220%" height="220%">
                    <feGaussianBlur stdDeviation={config.blur * 2 * size / 512} />
                </filter>
                <filter id={`fs-${uid}`} x="-30%" y="-30%" width="160%" height="160%">
                    <feGaussianBlur stdDeviation={3 * size / 512} />
                </filter>
                <clipPath id={`cc-${uid}`}>
                    <circle cx={half} cy={half} r={r} />
                </clipPath>
            </defs>

            <rect width={size} height={size} fill={config.bgColor} />

            <g clipPath={`url(#cc-${uid})`}>
                <circle cx={half} cy={half} r={r} fill={config.bgColor} />

                {/* Deep atmosphere */}
                <g filter={`url(#fg-${uid})`} opacity="0.4">
                    {config.petals.map((p, i) => {
                        const a1 = (p.angle - p.spread / 2) * Math.PI / 180;
                        const a2 = (p.angle + p.spread / 2) * Math.PI / 180;
                        return (
                            <polygon key={i}
                                points={`${half},${half} ${half + Math.cos(a1) * r * 1.2},${half + Math.sin(a1) * r * 1.2} ${half + Math.cos(a2) * r * 1.2},${half + Math.sin(a2) * r * 1.2}`}
                                fill={p.color1} opacity={p.opacity * 0.5}
                            />
                        );
                    })}
                </g>

                {/* Primary petals */}
                {config.petals.map((p, i) => {
                    const a1 = (p.angle - p.spread / 3) * Math.PI / 180;
                    const a2 = (p.angle + p.spread / 3) * Math.PI / 180;
                    const am = p.angle * Math.PI / 180;
                    return (
                        <g key={i} filter={`url(#fb-${uid})`} opacity={p.opacity}>
                            <polygon
                                points={`${half},${half} ${half + Math.cos(a1) * r * 1.1},${half + Math.sin(a1) * r * 1.1} ${half + Math.cos(am) * r * 1.15},${half + Math.sin(am) * r * 1.15} ${half + Math.cos(a2) * r * 1.1},${half + Math.sin(a2) * r * 1.1}`}
                                fill={`url(#pg-${uid}-${i})`}
                            />
                        </g>
                    );
                })}

                {/* Void seams */}
                <g opacity="0.5">
                    {config.petals.map((p, i) => {
                        const nextAngle = config.petals[(i + 1) % config.petals.length]?.angle ?? p.angle + 60;
                        const seamAngle = ((p.angle + nextAngle) / 2 + (nextAngle < p.angle ? 180 : 0)) * Math.PI / 180;
                        return (
                            <line key={i}
                                x1={half} y1={half}
                                x2={half + Math.cos(seamAngle) * r * 1.1}
                                y2={half + Math.sin(seamAngle) * r * 1.1}
                                stroke={config.bgColor} strokeWidth={Math.max(2, 5 * size / 512)}
                                filter={`url(#fs-${uid})`}
                            />
                        );
                    })}
                </g>
            </g>

            {/* Geometric overlay */}
            {config.geometricOverlay && (
                <g transform={`translate(${half},${half})`} opacity="0.12">
                    {[0, 30, 15].map((rot, i) => {
                        const hr = r * (0.45 - i * 0.1);
                        const pts = Array.from({ length: 6 }, (_, j) => {
                            const a = (j * 60 + rot) * Math.PI / 180;
                            return `${Math.cos(a) * hr},${Math.sin(a) * hr}`;
                        }).join(' ');
                        return <polygon key={i} points={pts} fill="none" stroke="rgba(165,180,252,0.3)" strokeWidth={Math.max(0.3, 0.8 - i * 0.2)} />;
                    })}
                </g>
            )}

            {/* Center nexus */}
            <circle cx={half} cy={half} r={config.centerGlow * size / 512}
                fill={`url(#nx-${uid})`} filter={`url(#fg-${uid})`} opacity="0.9" />
            <circle cx={half} cy={half} r={config.centerGlow * 0.4 * size / 512}
                fill={`url(#nx-${uid})`} opacity="0.7" />
            <circle cx={half} cy={half} r={Math.max(1.5, 5 * size / 512)} fill={config.centerColor} opacity="0.95" />
            <circle cx={half} cy={half} r={Math.max(0.8, 2.5 * size / 512)} fill="#fff" />

            {/* Starburst */}
            <g opacity="0.4" stroke="#fff" strokeWidth={Math.max(0.3, 0.6 * size / 512)} strokeLinecap="round">
                {[0, 45, 90, 135, 180, 225, 270, 315].map((a) => {
                    const inner = 8 * size / 512;
                    const outer = 16 * size / 512;
                    return (
                        <line key={a}
                            x1={half + Math.cos(a * Math.PI / 180) * inner}
                            y1={half + Math.sin(a * Math.PI / 180) * inner}
                            x2={half + Math.cos(a * Math.PI / 180) * outer}
                            y2={half + Math.sin(a * Math.PI / 180) * outer}
                        />
                    );
                })}
            </g>

            {/* Vignette */}
            <circle cx={half} cy={half} r={r + 5} fill="none" stroke={config.bgColor}
                strokeWidth={r * 0.15} opacity={config.vignette * 0.6} />
            <circle cx={half} cy={half} r={r + 12} fill="none" stroke={config.bgColor}
                strokeWidth={r * 0.1} opacity={config.vignette * 0.85} />

            {/* Boundary */}
            <circle cx={half} cy={half} r={r - 1} fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
        </svg>
    );
}

// ─── Logo Studio Component ───────────────────────────────────────────────────
export default function LogoStudio() {
    const [activeGalleryItem, setActiveGalleryItem] = useState<string>('convergence');
    const [viewMode, setViewMode] = useState<'gallery' | 'builder'>('gallery');

    const selectedLogo = GALLERY.find((g) => g.id === activeGalleryItem) ?? GALLERY[0];

    const handleExportSVG = useCallback(() => {
        // Create a temporary SVG download
        const svgEl = document.querySelector('.ob-logo-hero-preview svg');
        if (!svgEl) return;
        const svgData = new XMLSerializer().serializeToString(svgEl);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedLogo.config.name.toLowerCase().replace(/\s+/g, '-')}.svg`;
        a.click();
        URL.revokeObjectURL(url);
    }, [selectedLogo]);

    return (
        <div className="ob-logo-studio">
            {/* Mode toggle */}
            <div className="ob-logo-mode-bar">
                <button
                    className={`ob-logo-mode-btn${viewMode === 'gallery' ? ' active' : ''}`}
                    onClick={() => setViewMode('gallery')}
                >Gallery</button>
                <button
                    className={`ob-logo-mode-btn${viewMode === 'builder' ? ' active' : ''}`}
                    onClick={() => setViewMode('builder')}
                >Builder</button>
            </div>

            {viewMode === 'gallery' ? (
                <>
                    {/* Hero preview */}
                    <div className="ob-logo-hero-preview">
                        <LogoPreview config={selectedLogo.config} size={280} />
                        <div className="ob-logo-hero-info">
                            <h3 className="ob-logo-hero-name">{selectedLogo.name}</h3>
                            <p className="ob-logo-hero-desc">{selectedLogo.description}</p>
                            <div className="ob-logo-hero-actions">
                                <button className="ob-logo-action-btn primary" onClick={handleExportSVG}>
                                    Export SVG
                                </button>
                                <button className="ob-logo-action-btn" onClick={() => setViewMode('builder')}>
                                    Customize
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Gallery grid */}
                    <div className="ob-logo-gallery-label">Masterpiece Collection</div>
                    <div className="ob-logo-gallery">
                        {GALLERY.map((item) => (
                            <button
                                key={item.id}
                                className={`ob-logo-gallery-item${activeGalleryItem === item.id ? ' active' : ''}`}
                                onClick={() => setActiveGalleryItem(item.id)}
                            >
                                <div className="ob-logo-gallery-thumb">
                                    <LogoPreview config={item.config} size={100} />
                                </div>
                                <span className="ob-logo-gallery-name">{item.name}</span>
                            </button>
                        ))}
                    </div>

                    {/* Petal details */}
                    <div className="ob-logo-details">
                        <div className="ob-logo-detail-label">Color Petals</div>
                        <div className="ob-logo-petals">
                            {selectedLogo.config.petals.map((p, i) => (
                                <div key={i} className="ob-logo-petal-info">
                                    <div className="ob-logo-petal-swatch" style={{
                                        background: `linear-gradient(135deg, ${p.color1}, ${p.color2})`
                                    }} />
                                    <span className="ob-logo-petal-angle">{p.angle}°</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            ) : (
                <div className="ob-logo-builder">
                    <div className="ob-logo-builder-preview">
                        <LogoPreview config={selectedLogo.config} size={220} />
                    </div>
                    <div className="ob-logo-builder-hint">
                        <p>Logo Builder coming soon — full petal editor, color picker, angle control, export pipeline.</p>
                        <p>Currently showing: <strong>{selectedLogo.name}</strong></p>
                        <button className="ob-logo-action-btn" onClick={() => setViewMode('gallery')}>
                            ← Back to Gallery
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
