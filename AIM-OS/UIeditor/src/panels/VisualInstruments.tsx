/* ═══════════════════════════════════════════════════════════════════════════
   OmniBuilder — Visual Instruments Panel
   Dynamically selects which visual editors to show based on the selected
   node's property stack. This IS the OPUS Canon in action.
   "NEVER BUILD GENERIC SLIDER/INPUT SETTINGS PANELS."
   ═══════════════════════════════════════════════════════════════════════════ */
import { useState } from 'react';
import { useEditorStore } from '../store/editorStore';
import BoxModelInstrument from '../editors/BoxModelInstrument';
import RadiusEditor from '../editors/RadiusEditor';
import GradientStripEditor from '../editors/GradientStripEditor';
import ShadowSculptor from '../editors/ShadowSculptor';
import TypographyScale from '../editors/TypographyScale';
import ColorRelationshipEditor from '../editors/ColorRelationshipEditor';
import BreakpointEditor from '../editors/BreakpointEditor';

// ─── Default instrument values (derived from property stacks) ────────────────
function parseBoxModel(props: { property: string; computedValue: string }[]) {
    const padding = props.find((p) => p.property === 'padding');
    if (!padding) return null;
    // Parse "10px 24px" or "28px" format
    const parts = padding.computedValue.replace(/px/g, '').trim().split(/\s+/).map(Number);
    const [pt, pr, pb, pl] = parts.length === 1
        ? [parts[0], parts[0], parts[0], parts[0]]
        : parts.length === 2
            ? [parts[0], parts[1], parts[0], parts[1]]
            : [parts[0], parts[1], parts[2] ?? parts[0], parts[3] ?? parts[1]];
    return {
        margin: { top: 0, right: 0, bottom: 0, left: 0 },
        padding: { top: pt, right: pr, bottom: pb, left: pl },
        width: 0, height: 0,
    };
}

function parseRadius(props: { property: string; computedValue: string }[]) {
    const r = props.find((p) => p.property === 'border-radius');
    if (!r) return null;
    const val = parseInt(r.computedValue) || 0;
    return { topLeft: val, topRight: val, bottomRight: val, bottomLeft: val };
}

function parseGradient(props: { property: string; computedValue: string }[]) {
    const bg = props.find((p) => p.property === 'background');
    if (!bg || !bg.computedValue.includes('gradient')) return null;
    // Simplified parsing — extract color stops
    const match = bg.computedValue.match(/linear-gradient\((\d+)deg,\s*(.+)\)/);
    if (!match) return {
        stops: [
            { position: 0, color: '#4a8af4' },
            { position: 1, color: '#5c6bc0' },
        ],
        angle: 135,
        type: 'linear' as 'linear' | 'radial',
    };
    const angle = parseInt(match[1]) || 135;
    const colorPart = match[2];
    const stops = colorPart.split(',').map((s, i, arr) => ({
        position: i / (arr.length - 1),
        color: s.trim().split(' ')[0],
    }));
    return { stops, angle, type: 'linear' as 'linear' | 'radial' };
}

function parseShadow(props: { property: string; computedValue: string }[]) {
    const s = props.find((p) => p.property === 'box-shadow');
    if (!s) return null;
    // Parse "0 4px 16px rgba(74,138,244,0.3)"
    const parts = s.computedValue.match(/(-?\d+)\w*\s+(-?\d+)\w*\s+(-?\d+)\w*\s*(.*)/);
    if (!parts) return {
        offsetX: 0, offsetY: 4, blur: 16, spread: 0,
        color: 'rgba(74,138,244,0.3)', inset: false,
    };
    return {
        offsetX: parseInt(parts[1]) || 0,
        offsetY: parseInt(parts[2]) || 0,
        blur: parseInt(parts[3]) || 0,
        spread: 0,
        color: parts[4]?.trim() || 'rgba(0,0,0,0.3)',
        inset: s.computedValue.includes('inset'),
    };
}

function parseTypography(props: { property: string; computedValue: string }[]) {
    const fs = props.find((p) => p.property === 'font-size');
    const fw = props.find((p) => p.property === 'font-weight');
    const col = props.find((p) => p.property === 'color');
    if (!fs && !fw) return null;
    return {
        fontSize: parseInt(fs?.computedValue || '16') || 16,
        fontWeight: parseInt(fw?.computedValue || '400') || 400,
        lineHeight: 1.5,
        letterSpacing: 0,
        color: col?.computedValue || '#e8ebf0',
    };
}

export default function VisualInstruments() {
    const selectedIds = useEditorStore((s) => s.selectedNodeIds);
    const propertyStacks = useEditorStore((s) => s.propertyStacks);
    const nodes = useEditorStore((s) => s.nodes);

    const selId = selectedIds[0];
    const node = selId ? nodes[selId] : null;
    const props = selId ? propertyStacks[selId] : null;

    // Parse what editors to show
    const [boxModel, setBoxModel] = useState(() => props ? parseBoxModel(props) : null);
    const [radius, setRadius] = useState(() => props ? parseRadius(props) : null);
    const [gradient, setGradient] = useState(() => props ? parseGradient(props) : null);
    const [shadow, setShadow] = useState(() => props ? parseShadow(props) : null);
    const [typo, setTypo] = useState(() => props ? parseTypography(props) : null);

    // Re-derive values when selection changes (basic reactivity)
    const currentBoxModel = props ? parseBoxModel(props) : null;
    const currentRadius = props ? parseRadius(props) : null;
    const currentGradient = props ? parseGradient(props) : null;
    const currentShadow = props ? parseShadow(props) : null;
    const currentTypo = props ? parseTypography(props) : null;

    const hasAnyEditor = currentBoxModel || currentRadius || currentGradient || currentShadow || currentTypo;

    if (!node) {
        return (
            <div className="ob-visual-instruments-empty">
                <div className="ob-vi-empty-icon">⬡</div>
                <div className="ob-vi-empty-text">Select a node to see visual instruments</div>
            </div>
        );
    }

    if (!hasAnyEditor) {
        return (
            <div className="ob-visual-instruments-empty">
                <div className="ob-vi-empty-icon">◇</div>
                <div className="ob-vi-empty-text">No visual editors available for {node.componentName || `<${node.tag}>`}</div>
                <div className="ob-vi-empty-hint">Add properties to this node to unlock editors</div>
            </div>
        );
    }

    return (
        <div className="ob-visual-instruments">
            <div className="ob-vi-header">
                <span className="ob-vi-node-name">{node.componentName || `<${node.tag}>`}</span>
                <span className="ob-vi-node-label">{node.label}</span>
            </div>

            <div className="ob-vi-editors">
                {currentBoxModel && (
                    <BoxModelInstrument
                        value={boxModel ?? currentBoxModel}
                        onChange={setBoxModel}
                        label="Box Model"
                    />
                )}

                {currentRadius && (
                    <RadiusEditor
                        value={radius ?? currentRadius}
                        onChange={setRadius}
                        label="Border Radius"
                    />
                )}

                {currentGradient && (
                    <GradientStripEditor
                        value={gradient ?? currentGradient}
                        onChange={setGradient}
                        label="Background Gradient"
                    />
                )}

                {currentShadow && (
                    <ShadowSculptor
                        value={shadow ?? currentShadow}
                        onChange={setShadow}
                        label="Box Shadow"
                    />
                )}

                {currentTypo && (
                    <TypographyScale
                        value={typo ?? currentTypo}
                        onChange={setTypo}
                        label="Typography"
                        sampleText={node.label || 'Aa'}
                    />
                )}

                {/* Always show Color Relationship & Breakpoint editors */}
                <ColorRelationshipEditor />
                <BreakpointEditor />
            </div>
        </div>
    );
}
