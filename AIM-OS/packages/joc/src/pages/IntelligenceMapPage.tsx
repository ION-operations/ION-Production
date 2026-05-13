import React, { useState, useEffect } from 'react';
import { HexLatticeIcon, RadarIcon, SignalPulseIcon, LaunchVectorIcon } from '../components/icons';
import '../styles/intelligence-map.css';

export function IntelligenceMapPage() {
    const [query, setQuery] = useState('AetherEngine');
    const [isSearching, setIsSearching] = useState(false);
    const [contextData, setContextData] = useState<string>('');
    const [errorMsg, setErrorMsg] = useState('');
    const [streamLogs, setStreamLogs] = useState<string[]>([]);
    const [isConnected, setIsConnected] = useState(true);

    useEffect(() => {
        // Mock reactive stream for visual demo purposes while integrating
        const demoStream = setInterval(() => {
            setStreamLogs(prev => {
                const msgs = [
                    "OS Watcher: File `victus/ion/query_v2.py` modified",
                    "AST Daemon: Re-indexed `HybridQueryEngine` (+4 lines)",
                    "Graph Engine: Updated 2 dependencies for `query_v2.py`",
                    "Aether: Context threshold 0ms nominal",
                    "System: Waiting for telemetry flush"
                ];
                const newMsg = `[${new Date().toISOString().split('T')[1].slice(0, 8)}] ${msgs[Math.floor(Math.random() * msgs.length)]}`;
                return [newMsg, ...prev].slice(0, 50);
            });
        }, 3000);
        return () => clearInterval(demoStream);
    }, []);

    const handleSearch = async () => {
        setIsSearching(true);
        setErrorMsg('');
        try {
            const res = await fetch("http://127.0.0.1:5001/mcp/execute", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    tool: "ion_query",
                    arguments: { intent: query }
                })
            });
            const data = await res.json();
            const content = data?.result?.content?.[0] as { type: string; text: string };
            if (content && content.type === 'text') {
                setContextData(content.text);
            } else {
                setContextData("No context returned.");
            }
            setIsConnected(true);
        } catch (e: any) {
            setErrorMsg(e.message || "Failed to query OS Mind.");
            setIsConnected(false);
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="intel-map-root">
            {/* Top Toolbar */}
            <div className="intel-map-toolbar">
                <div className="intel-search-box">
                    <RadarIcon size={16} className="search-icon" />
                    <input 
                        className="intel-search-input"
                        placeholder="Query V3 OS Mind (AST, Classes, Functions)..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    />
                    <button className="intel-search-btn" onClick={handleSearch} disabled={isSearching || !isConnected}>
                        {isSearching ? 'ROUTING...' : 'QUERY (0ms)'}
                    </button>
                </div>
                <div className="intel-connection-status">
                    <div className={`status-indicator ${isConnected ? 'active' : 'offline'}`} />
                    <span>LUCID-MCP {isConnected ? 'ONLINE' : 'OFFLINE'}</span>
                </div>
            </div>

            {errorMsg && <div className="intel-error-banner">{errorMsg}</div>}

            {/* Main Layout Grid */}
            <div className="intel-map-grid">
                
                {/* Left Panel: AST Topology Viewer */}
                <div className="intel-panel ast-panel">
                    <div className="panel-header">
                        <HexLatticeIcon size={16} />
                        <span>Global Inverted Index</span>
                        <div className="lucid-badge">V3 Engine</div>
                    </div>
                    <div className="panel-content ast-content">
                        {contextData ? (
                            <pre className="ast-raw-output">{contextData}</pre>
                        ) : (
                            <div className="empty-state">
                                <HexLatticeIcon size={48} />
                                <p>Search the OS memory to visualize the cognitive AST map.</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Panel: Reactive Stream */}
                <div className="intel-panel stream-panel">
                    <div className="panel-header">
                        <SignalPulseIcon size={16} />
                        <span>Reactive OS Stream</span>
                    </div>
                    <div className="panel-content stream-content">
                        {streamLogs.map((log, i) => (
                            <div key={i} className="stream-line">
                                <span className="stream-time">{log.split('] ')[0]}]</span>
                                <span className="stream-msg">{log.split('] ')[1]}</span>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}
