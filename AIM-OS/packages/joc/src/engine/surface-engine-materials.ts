// surface-engine-materials.ts
// ═══════════════════════════════════════════════════════════════════
// Canonical Material Presets — The 6 tactile families.
//
// Each preset encodes how a surface responds to light:
//   - base gradient (top → bottom curvature)
//   - specular intensity and size
//   - shadow multipliers (cavity depth, cast intensity)
//   - glow color (for active state LED bleed)
//   - surface noise (grain density)
// ═══════════════════════════════════════════════════════════════════

export interface MaterialPreset {
    name: string;
    /** Top color of the volume gradient */
    gradientTop: string;
    /** Bottom color of the volume gradient */
    gradientBottom: string;
    /** Specular highlight opacity (0–1) */
    specularIntensity: number;
    /** Specular radius as % of surface (10–100) */
    specularRadius: number;
    /** Rim highlight opacity (0–1) */
    rimHighlight: number;
    /** Cavity shadow multiplier (0.5–2) */
    cavityDepth: number;
    /** Cast shadow multiplier (0.5–2) */
    castIntensity: number;
    /** Active state glow color (LED bleed) */
    glowColor: string;
    /** Surface noise grain density (0=smooth, 1=heavy) */
    grain: number;
    /** Border radius scale: 0=sharp, 1=full round */
    roundness: number;
    /** CSS filter for the material (blur, saturate, etc.) */
    surfaceFilter?: string;
}

// ─── Canonical Presets ───────────────────────────────────────────

export const MATERIAL_PRESETS: Record<string, MaterialPreset> = {
    /**
     * polymer.soft — Rubber/silicone-like surfaces.
     * Low specular, deep cavity shadows, slight grain.
     * Use: button grips, rail backgrounds, separator zones.
     */
    'polymer.soft': {
        name: 'Soft Polymer',
        gradientTop: '#1e2230',
        gradientBottom: '#0e1218',
        specularIntensity: 0.06,
        specularRadius: 60,
        rimHighlight: 0.05,
        cavityDepth: 1.4,
        castIntensity: 0.8,
        glowColor: 'rgba(98, 178, 255, 0.15)',
        grain: 0.5,
        roundness: 0.6,
    },

    /**
     * ceramic.gloss — Smooth, reflective, camera-body-grade.
     * High specular, tight highlight, low grain.
     * Use: primary panels, card bodies, elevated surfaces.
     */
    'ceramic.gloss': {
        name: 'Gloss Ceramic',
        gradientTop: '#2a3040',
        gradientBottom: '#14181f',
        specularIntensity: 0.18,
        specularRadius: 28,
        rimHighlight: 0.12,
        cavityDepth: 1.0,
        castIntensity: 1.2,
        glowColor: 'rgba(122, 204, 255, 0.18)',
        grain: 0.08,
        roundness: 0.5,
    },

    /**
     * metal.anodized — Brushed aluminum aerospace feel.
     * Linear brush texture, directional specular, sharp edges.
     * Use: bezels, frames, structural dividers, fascias.
     */
    'metal.anodized': {
        name: 'Anodized Metal',
        gradientTop: '#3a3f4a',
        gradientBottom: '#1a1e26',
        specularIntensity: 0.22,
        specularRadius: 40,
        rimHighlight: 0.15,
        cavityDepth: 0.7,
        castIntensity: 1.5,
        glowColor: 'rgba(160, 200, 240, 0.12)',
        grain: 0.3,
        roundness: 0.25,
        surfaceFilter: 'contrast(1.05)',
    },

    /**
     * glass.acrylic.soft — Frosted glass, translucent layers.
     * Very high specular, soft bloom, no grain.
     * Use: overlays, status displays, glass knobs.
     */
    'glass.acrylic.soft': {
        name: 'Soft Acrylic Glass',
        gradientTop: 'rgba(255,255,255,0.08)',
        gradientBottom: 'rgba(0,0,0,0.12)',
        specularIntensity: 0.30,
        specularRadius: 50,
        rimHighlight: 0.18,
        cavityDepth: 0.5,
        castIntensity: 0.6,
        glowColor: 'rgba(150, 220, 255, 0.22)',
        grain: 0,
        roundness: 0.7,
        surfaceFilter: 'blur(0.5px) saturate(1.2)',
    },

    /**
     * rubber.tactile — Textured grip surface with stipple.
     * Very low specular, heavy grain, deep cavity.
     * Use: button pads, knob grips, touch zone indicators.
     */
    'rubber.tactile': {
        name: 'Tactile Rubber',
        gradientTop: '#1a1c22',
        gradientBottom: '#0d0f14',
        specularIntensity: 0.03,
        specularRadius: 80,
        rimHighlight: 0.03,
        cavityDepth: 1.8,
        castIntensity: 0.6,
        glowColor: 'rgba(80, 160, 240, 0.10)',
        grain: 0.85,
        roundness: 0.4,
    },

    /**
     * gel.capsule — Soft, translucent, pill-shaped gel.
     * Medium specular with subsurface scatter hint.
     * Use: status pills, chips, badges, toggle tracks.
     */
    'gel.capsule': {
        name: 'Gel Capsule',
        gradientTop: '#222838',
        gradientBottom: '#141820',
        specularIntensity: 0.14,
        specularRadius: 45,
        rimHighlight: 0.10,
        cavityDepth: 0.9,
        castIntensity: 0.9,
        glowColor: 'rgba(110, 190, 255, 0.20)',
        grain: 0.02,
        roundness: 1.0,
        surfaceFilter: 'saturate(1.1)',
    },
};

// ─── Material Compiler ───────────────────────────────────────────

/**
 * Compile a MaterialPreset into CSS properties for a surface.
 * Enforces all 5 Laws automatically.
 */
export function compileMaterialSurface(
    preset: MaterialPreset,
    opts: {
        hovered?: boolean;
        pressed?: boolean;
        active?: boolean;
        hotspotX?: number;
        hotspotY?: number;
    } = {}
): React.CSSProperties {
    const { hovered, pressed, active, hotspotX = 0.3, hotspotY = 0.2 } = opts;
    const hpX = `${(hotspotX * 100).toFixed(1)}%`;
    const hpY = `${(hotspotY * 100).toFixed(1)}%`;

    const lift = hovered ? 2 : 0;
    const depress = pressed ? 1.5 : 0;

    // LAW 2: Volume gradient
    const background = [
        // Specular hotspot
        `radial-gradient(${preset.specularRadius}% ${preset.specularRadius}% at ${hpX} ${hpY}, rgba(255,255,255,${preset.specularIntensity}) 0%, transparent 60%)`,
        // Active glow
        active ? `radial-gradient(80% 60% at 50% 50%, ${preset.glowColor} 0%, transparent 70%)` : '',
        // Volume curvature
        `linear-gradient(180deg, ${preset.gradientTop} 0%, ${preset.gradientBottom} 100%)`,
    ].filter(Boolean).join(', ');

    // LAW 3: 3-Tier Cast Shadow
    const boxShadow = [
        // LAW 4: Top micro-bevel
        `inset 0 1px 0 rgba(255,255,255,${preset.rimHighlight})`,
        // Bottom compression
        `inset 0 -2px 4px rgba(0,0,0,${0.3 * preset.cavityDepth})`,
        // Tier 1: Contact shadow
        `0 ${(1 + lift - depress).toFixed(1)}px ${(2 + lift).toFixed(1)}px rgba(0,0,0,${(0.3 * preset.castIntensity).toFixed(2)})`,
        // Tier 2: Cast shadow with negative spread (LAW 5)
        `0 ${(6 + lift * 2 - depress * 2).toFixed(1)}px ${(14 + lift * 3).toFixed(1)}px -4px rgba(0,0,0,${(0.25 * preset.castIntensity).toFixed(2)})`,
        // Tier 3: Ambient penumbra
        `0 ${(14 + lift * 3).toFixed(1)}px ${(32 + lift * 4).toFixed(1)}px -10px rgba(0,0,0,${(0.15 * preset.castIntensity).toFixed(2)})`,
    ].join(', ');

    return {
        background,
        boxShadow,
        transform: `translateY(${(-lift + depress).toFixed(1)}px)`,
        transition: 'all 120ms cubic-bezier(0.22, 1, 0.36, 1)',
        filter: preset.surfaceFilter,
    };
}

/**
 * Quick access to preset by key name.
 */
export function getMaterial(key: string): MaterialPreset {
    return MATERIAL_PRESETS[key] ?? MATERIAL_PRESETS['ceramic.gloss'];
}
