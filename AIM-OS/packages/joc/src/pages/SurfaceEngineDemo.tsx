// SurfaceEngineDemo.tsx
// ═══════════════════════════════════════════════════════════════════
// Demo page for the Surface Engine — showcasing the SkeuShaderToggle
// and material system. Accessible via the JOC page router.
// ═══════════════════════════════════════════════════════════════════

import React, { useState } from 'react';
import { SkeuShaderToggle } from '../components/surface/SkeuShaderToggle';

export function SurfaceEngineDemo() {
    const [toggles, setToggles] = useState({
        mcp: true,
        fleet: false,
        oracle: true,
        recording: false,
    });

    const toggle = (key: keyof typeof toggles) => {
        setToggles(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div style={{
            width: '100%',
            height: '100%',
            background: '#0a0c12',
            padding: '48px',
            display: 'flex',
            flexDirection: 'column',
            gap: '48px',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            overflow: 'auto',
        }}>
            {/* Title */}
            <div style={{ textAlign: 'center' }}>
                <h1 style={{
                    fontSize: 28,
                    fontWeight: 700,
                    color: 'rgba(255,255,255,0.92)',
                    letterSpacing: '-0.02em',
                    margin: 0,
                }}>
                    Surface Engine — Material System
                </h1>
                <p style={{
                    fontSize: 14,
                    color: 'rgba(255,255,255,0.4)',
                    marginTop: 8,
                    letterSpacing: '0.02em',
                }}>
                    2.5D physically-rendered UI controls • CSS backend with WebGPU hero path
                </p>
            </div>

            {/* Toggle Showcase */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '40px',
                maxWidth: 700,
            }}>
                {([
                    { key: 'mcp' as const, label: 'MCP SERVER', subtitle: 'Core Communication' },
                    { key: 'fleet' as const, label: 'AI FLEET', subtitle: 'Agent Fleet Status' },
                    { key: 'oracle' as const, label: 'ORACLE', subtitle: 'Autonomous Mode' },
                    { key: 'recording' as const, label: 'RECORDING', subtitle: 'Session Capture' },
                ]).map(({ key, label, subtitle }) => (
                    <div key={key} style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: 16,
                    }}>
                        <SkeuShaderToggle
                            checked={toggles[key]}
                            onChange={() => toggle(key)}
                            theme="dark"
                            width={200}
                            height={88}
                            label={label}
                        />
                        <div style={{ textAlign: 'center' }}>
                            <div style={{
                                fontSize: 11,
                                fontWeight: 700,
                                color: toggles[key] ? 'rgba(122, 204, 255, 0.9)' : 'rgba(255,255,255,0.35)',
                                letterSpacing: '0.12em',
                                textTransform: 'uppercase' as const,
                                transition: 'color 300ms ease',
                            }}>
                                {label}
                            </div>
                            <div style={{
                                fontSize: 10,
                                color: 'rgba(255,255,255,0.25)',
                                marginTop: 2,
                                letterSpacing: '0.04em',
                            }}>
                                {subtitle} • {toggles[key] ? 'ACTIVE' : 'STANDBY'}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Engine Info */}
            <div style={{
                display: 'flex',
                gap: '24px',
                fontSize: 10,
                color: 'rgba(255,255,255,0.2)',
                letterSpacing: '0.06em',
                textTransform: 'uppercase' as const,
            }}>
                <span>Backend: CSS</span>
                <span>•</span>
                <span>Physics: Hooke's Law Springs</span>
                <span>•</span>
                <span>Laws: 5/5 Skeuomorphic</span>
                <span>•</span>
                <span>Material: glass.acrylic.soft</span>
            </div>
        </div>
    );
}

export default SurfaceEngineDemo;
