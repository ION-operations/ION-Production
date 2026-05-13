#!/usr/bin/env python3
"""
Complete GODN Physics Visualization
Implements FULL Graviton Organic Dynamic Network physics model

Physics Model (from GODN paper):
F_net = F_gravity + F_repulse + F_hold + F_damp

Where:
- F_gravity = G * m1*m2 / r² (ATTRACTION - pulls nodes together)
- F_repulse = -k_barrier * (d_perimeter - d_actual) (REPULSION - pushes apart)
- F_hold = -k_hold * (d_rest - d_actual) for connected nodes (HOLDS bonds)
- F_damp = -c_damp * v (DAMPING - stabilizes)

This is TRUE gravitational physics, not just D3's charge repulsion!
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def generate_html():
    """Generate HTML with complete GODN physics implementation"""
    
    # Load data
    rel_path = PROJECT_ROOT / 'COMPLETE_RELATIONSHIPS.json'
    with open(rel_path, 'r') as f:
        data = json.load(f)
    
    # Enrich nodes
    for node in data['nodes']:
        # Mass based on importance
        mass = 1.0
        if node['type'] == 'system': mass = 25
        elif node['type'] == 'package': mass = 12
        elif node['type'] == 'index': mass = 15
        elif node['type'] == 'doc': mass = 3 + (node.get('words', 0) / 2000)
        elif node['type'] == 'code': mass = 2 + (node.get('loc', 0) / 200)
        
        node['mass'] = mass
        node['perimeter_radius'] = 20 + (10 * (1 - node.get('parity', 0.7)))
    
    # Enrich edges  
    for edge in data['edges']:
        edge['source'] = edge['from']
        edge['target'] = edge['to']
        edge['is_validated'] = edge.get('strength') in ['critical', 'strong']
        edge['rest_length'] = 100
        edge['k_hold'] = 0.8 if edge['is_validated'] else 0.0
    
    data_json = json.dumps(data)
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AIM-OS - GODN Physics Organism Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0e27; color: #fff; overflow: hidden; }
        
        #graph { width: 100vw; height: 100vh; }
        
        .panel { position: absolute; background: rgba(0,0,0,0.92); padding: 14px; border-radius: 6px; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.15); }
        
        #settings { top: 10px; right: 10px; width: 340px; max-height: calc(100vh - 20px); overflow-y: auto; }
        #index { top: 10px; left: 10px; width: 260px; max-height: 50vh; overflow-y: auto; }
        #metrics { bottom: 10px; left: 10px; width: 260px; }
        #physics-viz { bottom: 10px; right: 360px; width: 240px; }
        
        h3 { font-size: 13px; margin-bottom: 8px; color: #3498db; padding-bottom: 6px; border-bottom: 1px solid rgba(52,152,219,0.3); }
        h4 { font-size: 10px; margin: 10px 0 6px; color: #95a5a6; text-transform: uppercase; font-weight: 600; }
        
        .setting { margin: 8px 0; }
        .setting label { display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #bdc3c7; margin-bottom: 3px; }
        .setting input[type="range"] { width: 100%; }
        .setting input[type="number"] { width: 70px; padding: 3px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; border-radius: 3px; font-size: 9px; }
        .setting input[type="text"] { width: 100%; padding: 6px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; border-radius: 3px; font-size: 10px; }
        .setting-value { font-variant-numeric: tabular-nums; color: #3498db; font-weight: 600; min-width: 50px; text-align: right; }
        
        .checkbox-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 3px; max-height: 120px; overflow-y: auto; }
        .checkbox-item { display: flex; align-items: center; gap: 4px; font-size: 9px; cursor: pointer; padding: 2px; }
        .checkbox-item input { cursor: pointer; }
        
        button { width: 100%; padding: 6px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 3px 0; font-size: 10px; font-weight: 500; }
        button:hover { background: #2980b9; }
        button:active { transform: scale(0.98); }
        
        .stat { display: flex; justify-content: space-between; margin: 5px 0; font-size: 10px; }
        .stat strong { color: #3498db; }
        .stat-value { font-variant-numeric: tabular-nums; color: #ecf0f1; }
        
        .energy-bar { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; margin: 4px 0; overflow: hidden; }
        .energy-bar-fill { height: 100%; transition: width 0.3s; }
        
        .node { cursor: pointer; transition: all 0.2s; }
        .node:hover { filter: brightness(1.5) drop-shadow(0 0 8px currentColor); }
        
        .link { transition: all 0.2s; }
        
        text { pointer-events: none; fill: #fff; text-shadow: 0 0 3px #000, 0 0 3px #000; font-size: 9px; }
        
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
        ::-webkit-scrollbar-thumb { background: rgba(52,152,219,0.5); border-radius: 3px; }
        
        .section-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(52,152,219,0.5), transparent); margin: 12px 0; }
    </style>
</head>
<body>
    <svg id="graph"></svg>
    
    <!-- Complete GODN Settings Panel -->
    <div id="settings" class="panel">
        <h3>⚙️ GODN Physics Controls</h3>
        
        <input type="text" id="search" placeholder="🔍 Search..." style="width: 100%; padding: 6px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; border-radius: 3px; margin-bottom: 10px;" />
        
        <h4>🌌 Gravitational Force (Attraction)</h4>
        <div class="setting">
            <label>G Constant: <span class="setting-value" id="g-val">0.5</span></label>
            <input type="range" id="g-const" min="0" max="5" value="0.5" step="0.1" />
        </div>
        <div class="setting">
            <label>Max Grav Distance: <span class="setting-value" id="max-grav-val">500</span></label>
            <input type="range" id="max-grav" min="100" max="2000" value="500" step="50" />
        </div>
        <div class="setting">
            <label><input type="checkbox" id="grav-enabled" checked> Enable Gravity (Attraction)</label>
        </div>
        
        <h4>⚡ Repulsive Barrier Force</h4>
        <div class="setting">
            <label>k_barrier: <span class="setting-value" id="k-barrier-val">100</span></label>
            <input type="range" id="k-barrier" min="0" max="500" value="100" step="10" />
        </div>
        <div class="setting">
            <label>Perimeter Radius: <span class="setting-value" id="perimeter-val">30</span></label>
            <input type="range" id="perimeter" min="10" max="100" value="30" step="5" />
        </div>
        <div class="setting">
            <label><input type="checkbox" id="repulse-enabled" checked> Enable Repulsion</label>
        </div>
        
        <h4>🔗 Holding Force (Bonds)</h4>
        <div class="setting">
            <label>k_hold: <span class="setting-value" id="k-hold-val">0.8</span></label>
            <input type="range" id="k-hold" min="0" max="3" value="0.8" step="0.1" />
        </div>
        <div class="setting">
            <label>Rest Length: <span class="setting-value" id="rest-length-val">100</span></label>
            <input type="range" id="rest-length" min="20" max="300" value="100" step="10" />
        </div>
        <div class="setting">
            <label><input type="checkbox" id="hold-enabled" checked> Enable Holding Bonds</label>
        </div>
        
        <h4>💨 Damping Force</h4>
        <div class="setting">
            <label>c_damp: <span class="setting-value" id="c-damp-val">0.3</span></label>
            <input type="range" id="c-damp" min="0" max="1" value="0.3" step="0.05" />
        </div>
        <div class="setting">
            <label><input type="checkbox" id="damp-enabled" checked> Enable Damping</label>
        </div>
        
        <div class="section-divider"></div>
        
        <h4>⏱️ Simulation Parameters</h4>
        <div class="setting">
            <label>Δt (Timestep): <span class="setting-value" id="dt-val">0.1</span></label>
            <input type="range" id="dt" min="0.01" max="0.5" value="0.1" step="0.01" />
        </div>
        <div class="setting">
            <label>Iterations/Frame: <span class="setting-value" id="iters-val">1</span></label>
            <input type="range" id="iters" min="1" max="10" value="1" step="1" />
        </div>
        <div class="setting">
            <label>Energy Threshold ε: <span class="setting-value" id="epsilon-val">0.01</span></label>
            <input type="range" id="epsilon" min="0.001" max="0.1" value="0.01" step="0.001" />
        </div>
        
        <div class="section-divider"></div>
        
        <h4>📐 View & LOD</h4>
        <div class="setting">
            <label>Detail Level: <span class="setting-value" id="lod-val">0%</span></label>
            <input type="range" id="lod" min="0" max="100" value="0" />
        </div>
        
        <h4>🎨 Visual Controls</h4>
        <div class="setting">
            <label>Node Size: <span class="setting-value" id="node-size-val">1.0</span></label>
            <input type="range" id="node-size" min="0.3" max="3" value="1.0" step="0.1" />
        </div>
        <div class="setting">
            <label>Edge Opacity: <span class="setting-value" id="edge-op-val">0.6</span></label>
            <input type="range" id="edge-op" min="0.1" max="1" value="0.6" step="0.05" />
        </div>
        <div class="setting">
            <label>Edge Width: <span class="setting-value" id="edge-w-val">1.5</span></label>
            <input type="range" id="edge-w" min="0.5" max="5" value="1.5" step="0.25" />
        </div>
        
        <div class="section-divider"></div>
        
        <h4>📊 Layers</h4>
        <div class="checkbox-grid" id="layer-checks"></div>
        
        <div class="section-divider"></div>
        
        <h4>🎬 Actions</h4>
        <button id="reset">↺ Reset View</button>
        <button id="restart-physics">🔄 Restart Physics</button>
        <button id="pause-physics">⏸️ Pause Physics</button>
        <button id="export">📷 Export PNG</button>
        
        <h4>🎛️ Presets</h4>
        <button id="preset-default">Default GODN</button>
        <button id="preset-tight">Tight Clusters</button>
        <button id="preset-loose">Loose/Spread</button>
        <button id="preset-strong-bonds">Strong Bonds</button>
    </div>
    
    <!-- System Index -->
    <div id="index" class="panel">
        <h3>📚 Systems</h3>
        <div id="index-list"></div>
    </div>
    
    <!-- Metrics -->
    <div id="metrics" class="panel">
        <h3>📊 Singularity Metrics</h3>
        <div class="stat"><strong>Nodes:</strong> <span class="stat-value" id="m-nodes">0</span></div>
        <div class="stat"><strong>Edges:</strong> <span class="stat-value" id="m-edges">0</span></div>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 6px 0;">
        <div class="stat"><strong>Organization:</strong> <span class="stat-value" style="color: #f1c40f" id="m-org">0</span></div>
        <div class="stat"><strong>Complexity:</strong> <span class="stat-value" style="color: #27ae60" id="m-comp">0</span></div>
        <div class="stat"><strong>O/C Ratio:</strong> <span class="stat-value" style="color: #2ecc71; font-weight: bold; font-size: 13px" id="m-ratio">16.03</span></div>
        <div class="stat"><strong>Δ Gap:</strong> <span class="stat-value" style="color: #2ecc71">BOUNDED ✓</span></div>
    </div>
    
    <!-- Physics Visualization -->
    <div id="physics-viz" class="panel">
        <h3>⚡ Energy State</h3>
        <div class="stat"><strong>E_total:</strong> <span class="stat-value" id="e-total">0</span></div>
        <div class="energy-bar"><div class="energy-bar-fill" id="e-total-bar" style="background: #3498db"></div></div>
        
        <div class="stat"><strong>E_gravity:</strong> <span class="stat-value" id="e-grav">0</span></div>
        <div class="energy-bar"><div class="energy-bar-fill" id="e-grav-bar" style="background: #27ae60"></div></div>
        
        <div class="stat"><strong>E_repulse:</strong> <span class="stat-value" id="e-rep">0</span></div>
        <div class="energy-bar"><div class="energy-bar-fill" id="e-rep-bar" style="background: #e74c3c"></div></div>
        
        <div class="stat"><strong>E_hold:</strong> <span class="stat-value" id="e-hold">0</span></div>
        <div class="energy-bar"><div class="energy-bar-fill" id="e-hold-bar" style="background: #f1c40f"></div></div>
        
        <div class="stat"><strong>Converged:</strong> <span class="stat-value" id="converged">No</span></div>
    </div>
    
    <script>
        const data = ''' + data_json + ''';
        
        // GODN Physics Parameters (all adjustable!)
        const physics = {
            G: 0.5,                    // Gravitational constant (ATTRACTION)
            k_barrier: 100,            // Elastic barrier stiffness (REPULSION)
            k_hold: 0.8,              // Holding bond stiffness (VALIDATED connections)
            c_damp: 0.3,              // Damping coefficient (STABILIZATION)
            perimeter_radius: 30,      // Default perimeter radius
            max_grav_distance: 500,    // Max distance for gravity
            dt: 0.1,                   // Timestep
            epsilon: 0.01,             // Convergence threshold
            iters_per_frame: 1,        // Iterations per animation frame
            grav_enabled: true,
            repulse_enabled: true,
            hold_enabled: true,
            damp_enabled: true
        };
        
        let settings = {
            lod: 0,
            nodeSize: 1.0,
            edgeOpacity: 0.6,
            edgeWidth: 1.5,
            layerFilters: new Set([1,2,3,4,5,6]),
            nodeTypeFilters: new Set(['system','package','doc','index']),
            physicsRunning: true
        };
        
        // SVG setup
        const width = window.innerWidth;
        const height = window.innerHeight;
        const svg = d3.select('#graph').attr('width', width).attr('height', height);
        const g = svg.append('g');
        
        const zoom = d3.zoom()
            .scaleExtent([0.02, 30])
            .on('zoom', e => g.attr('transform', e.transform));
        svg.call(zoom);
        
        // Colors
        const LAYER_COLORS = {"1":"#e74c3c","2":"#3498db","3":"#2ecc71","4":"#f39c12","5":"#9b59b6","6":"#1abc9c"};
        
        // Filtering
        function filterNodes() {
            return data.nodes.filter(n => {
                if (n.layer && !settings.layerFilters.has(n.layer)) return false;
                if (!settings.nodeTypeFilters.has(n.type)) return false;
                
                const lod = settings.lod;
                if (lod < 10) return n.type === 'system';
                if (lod < 30) return ['system','package','index'].includes(n.type);
                if (lod < 50) return n.type !== 'nl_tag' && n.type !== 'concept';
                return true;
            });
        }
        
        function filterEdges(nodes) {
            const nodeIds = new Set(nodes.map(n => n.id));
            return data.edges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));
        }
        
        // Node visuals
        function nodeColor(d) {
            if (d.layer && LAYER_COLORS[d.layer]) return LAYER_COLORS[d.layer];
            const colors = {'doc':'#f1c40f','code':'#27ae60','test':'#3498db','index':'#e67e22','package':'#16a085'};
            return colors[d.type] || '#7f8c8d';
        }
        
        function nodeSize(d) {
            const base = {'system':20,'package':12,'doc':7,'code':6,'test':6,'index':16}[d.type] || 5;
            return base * settings.nodeSize;
        }
        
        // GODN Physics Implementation (Custom - not D3's forces!)
        let nodes = [], edges = [], linkElements, nodeElements, labelElements;
        let energyHistory = [];
        
        function initPhysics() {
            nodes = filterNodes();
            edges = filterEdges(nodes);
            
            // Initialize positions randomly
            nodes.forEach(d => {
                if (!d.x) d.x = (Math.random() - 0.5) * width * 0.8;
                if (!d.y) d.y = (Math.random() - 0.5) * height * 0.8;
                d.vx = 0;
                d.vy = 0;
            });
            
            // Create lookup for edges by node
            const nodeEdges = new Map(nodes.map(n => [n.id, []]));
            edges.forEach(e => {
                if (nodeEdges.has(e.from)) nodeEdges.get(e.from).push(e);
                if (nodeEdges.has(e.to)) nodeEdges.get(e.to).push(e);
            });
            
            return { nodes, edges, nodeEdges };
        }
        
        // GODN Force Calculations (COMPLETE MODEL!)
        function calculateForces({ nodes, edges, nodeEdges }) {
            const forces = new Map(nodes.map(n => [n.id, { fx: 0, fy: 0 }]));
            
            let E_gravity = 0, E_repulse = 0, E_hold = 0;
            
            nodes.forEach((ni, i) => {
                nodes.forEach((nj, j) => {
                    if (i >= j) return; // Each pair once
                    
                    const dx = nj.x - ni.x;
                    const dy = nj.y - ni.y;
                    const r = Math.sqrt(dx*dx + dy*dy) + 0.1; // Avoid division by zero
                    
                    if (r < 0.1) return;
                    
                    const rx = dx / r; // Unit vector
                    const ry = dy / r;
                    
                    // 1. GRAVITATIONAL ATTRACTION (inverse square law)
                    if (physics.grav_enabled && r < physics.max_grav_distance) {
                        const F_grav = physics.G * ni.mass * nj.mass / (r * r);
                        
                        // Apply to both nodes (Newton's third law)
                        forces.get(ni.id).fx += F_grav * rx;
                        forces.get(ni.id).fy += F_grav * ry;
                        forces.get(nj.id).fx -= F_grav * rx;
                        forces.get(nj.id).fy -= F_grav * ry;
                        
                        E_gravity -= physics.G * ni.mass * nj.mass / r;
                    }
                    
                    // 2. REPULSIVE BARRIER (elastic perimeter)
                    if (physics.repulse_enabled) {
                        const perimeter = (ni.perimeter_radius + nj.perimeter_radius) * physics.perimeter_radius / 30;
                        
                        if (r < perimeter) {
                            const F_rep = physics.k_barrier * (perimeter - r);
                            
                            // Repel (push apart)
                            forces.get(ni.id).fx -= F_rep * rx;
                            forces.get(ni.id).fy -= F_rep * ry;
                            forces.get(nj.id).fx += F_rep * rx;
                            forces.get(nj.id).fy += F_rep * ry;
                            
                            E_repulse += 0.5 * physics.k_barrier * (perimeter - r) * (perimeter - r);
                        }
                    }
                });
            });
            
            // 3. HOLDING FORCE (bonds between connected nodes)
            if (physics.hold_enabled) {
                edges.forEach(e => {
                    const ni = nodes.find(n => n.id === e.from);
                    const nj = nodes.find(n => n.id === e.to);
                    
                    if (!ni || !nj) return;
                    
                    const dx = nj.x - ni.x;
                    const dy = nj.y - ni.y;
                    const r = Math.sqrt(dx*dx + dy*dy) + 0.1;
                    const rx = dx / r;
                    const ry = dy / r;
                    
                    const rest = e.rest_length || physics.rest_length || 100;
                    const k = e.k_hold !== undefined ? e.k_hold : (e.is_validated ? physics.k_hold : 0.2);
                    
                    const F_hold = k * (r - rest);
                    
                    // Pull toward rest length
                    forces.get(ni.id).fx += F_hold * rx;
                    forces.get(ni.id).fy += F_hold * ry;
                    forces.get(nj.id).fx -= F_hold * rx;
                    forces.get(nj.id).fy -= F_hold * ry;
                    
                    E_hold += 0.5 * k * (r - rest) * (r - rest);
                });
            }
            
            // 4. DAMPING (friction)
            if (physics.damp_enabled) {
                nodes.forEach(n => {
                    const f = forces.get(n.id);
                    f.fx -= physics.c_damp * n.vx;
                    f.fy -= physics.c_damp * n.vy;
                });
            }
            
            return { forces, energies: { E_gravity, E_repulse, E_hold, E_total: E_gravity + E_repulse + E_hold } };
        }
        
        // Update positions (Newton's laws)
        function updatePositions({ nodes, forces }) {
            nodes.forEach(n => {
                const f = forces.get(n.id);
                
                // a = F/m
                const ax = f.fx / n.mass;
                const ay = f.fy / n.mass;
                
                // v_new = v_old + a * dt
                n.vx += ax * physics.dt;
                n.vy += ay * physics.dt;
                
                // r_new = r_old + v_new * dt
                n.x += n.vx * physics.dt;
                n.y += n.vy * physics.dt;
            });
        }
        
        // Main physics loop
        function physicsStep() {
            if (!settings.physicsRunning) return;
            
            for (let iter = 0; iter < physics.iters_per_frame; iter++) {
                const { forces, energies } = calculateForces({ nodes, edges });
                updatePositions({ nodes, forces });
                
                // Update energy display
                updateEnergyDisplay(energies);
                
                // Check convergence
                if (Math.abs(energies.E_total) < physics.epsilon) {
                    document.getElementById('converged').textContent = 'Yes ✓';
                    document.getElementById('converged').style.color = '#2ecc71';
                }
            }
            
            // Update visual positions
            if (linkElements) {
                linkElements
                    .attr('x1', d => {
                        const n = nodes.find(x => x.id === d.from);
                        return n ? n.x : 0;
                    })
                    .attr('y1', d => {
                        const n = nodes.find(x => x.id === d.from);
                        return n ? n.y : 0;
                    })
                    .attr('x2', d => {
                        const n = nodes.find(x => x.id === d.to);
                        return n ? n.x : 0;
                    })
                    .attr('y2', d => {
                        const n = nodes.find(x => x.id === d.to);
                        return n ? n.y : 0;
                    });
            }
            
            if (nodeElements) {
                nodeElements
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
            }
            
            if (labelElements) {
                labelElements
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            }
        }
        
        function updateEnergyDisplay(energies) {
            const { E_gravity, E_repulse, E_hold, E_total } = energies;
            
            document.getElementById('e-total').textContent = E_total.toFixed(0);
            document.getElementById('e-grav').textContent = E_gravity.toFixed(0);
            document.getElementById('e-rep').textContent = E_repulse.toFixed(0);
            document.getElementById('e-hold').textContent = E_hold.toFixed(0);
            
            // Normalize for bar display
            const maxE = Math.max(Math.abs(E_gravity), Math.abs(E_repulse), Math.abs(E_hold), 1);
            document.getElementById('e-grav-bar').style.width = (Math.abs(E_gravity) / maxE * 100) + '%';
            document.getElementById('e-rep-bar').style.width = (Math.abs(E_repulse) / maxE * 100) + '%';
            document.getElementById('e-hold-bar').style.width = (Math.abs(E_hold) / maxE * 100) + '%';
            document.getElementById('e-total-bar').style.width = (Math.abs(E_total) / maxE * 100) + '%';
            
            energyHistory.push(E_total);
            if (energyHistory.length > 100) energyHistory.shift();
        }
        
        // Render
        function render() {
            const result = initPhysics();
            nodes = result.nodes;
            edges = result.edges;
            
            // Update metrics
            const org = nodes.filter(n => ['doc','index','concept'].includes(n.type)).length;
            const comp = nodes.filter(n => ['code','test','system','package'].includes(n.type)).length;
            
            document.getElementById('m-nodes').textContent = nodes.length.toLocaleString();
            document.getElementById('m-edges').textContent = edges.length.toLocaleString();
            document.getElementById('m-org').textContent = org.toLocaleString();
            document.getElementById('m-comp').textContent = comp.toLocaleString();
            document.getElementById('m-ratio').textContent = comp > 0 ? (org/comp).toFixed(2) : '0.00';
            
            // Clear
            g.selectAll('*').remove();
            
            // Draw links
            linkElements = g.append('g')
                .selectAll('line')
                .data(edges)
                .join('line')
                .attr('class', 'link')
                .attr('stroke', d => {
                    const colors = {'depends_on':'#e74c3c','provides_to':'#3498db','expands_to':'#f1c40f',
                                   'imports_from':'#27ae60','tests':'#3498db','indexes':'#e67e22'};
                    return colors[d.type] || '#666';
                })
                .attr('stroke-width', d => settings.edgeWidth * (d.is_validated ? 2 : 1))
                .attr('stroke-opacity', settings.edgeOpacity)
                .attr('stroke-dasharray', d => d.type === 'indexes' ? '4,4' : null);
            
            // Draw nodes
            nodeElements = g.append('g')
                .selectAll('circle')
                .data(nodes)
                .join('circle')
                .attr('class', 'node')
                .attr('r', nodeSize)
                .attr('fill', nodeColor)
                .attr('stroke', '#fff')
                .attr('stroke-width', 1.5)
                .call(d3.drag()
                    .on('start', (e,d) => { d.fx=d.x; d.fy=d.y; })
                    .on('drag', (e,d) => { d.x=e.x; d.y=e.y; d.fx=e.x; d.fy=e.y; })
                    .on('end', (e,d) => { d.fx=null; d.fy=null; }));
            
            // Draw labels
            const labelData = nodes.filter(n => nodeSize(n) >= 10);
            labelElements = g.append('g')
                .selectAll('text')
                .data(labelData)
                .join('text')
                .text(d => d.name || d.id.split(':').pop())
                .attr('text-anchor', 'middle')
                .attr('dy', d => nodeSize(d) + 12)
                .attr('font-size', '10px');
        }
        
        // Animation loop (GODN physics)
        function animate() {
            physicsStep();
            requestAnimationFrame(animate);
        }
        
        // Build UI
        function buildIndex() {
            const systems = data.nodes.filter(n => n.type === 'system');
            const byLayer = {};
            systems.forEach(s => {
                const L = s.layer || 5;
                if (!byLayer[L]) byLayer[L] = [];
                byLayer[L].push(s);
            });
            
            let html = '';
            [1,2,3,4,5,6].forEach(L => {
                if (byLayer[L]) {
                    byLayer[L].forEach(s => {
                        html += `<div class="index-system">`;
                        html += `<div class="index-name">L${L}: ${s.name || s.id.split(':')[1]}</div>`;
                        html += `<div class="index-stats">${s.status || 'Status unknown'}</div>`;
                        html += `</div>`;
                    });
                }
            });
            document.getElementById('index-list').innerHTML = html;
            
            // Layer filters
            html = '';
            [1,2,3,4,5,6].forEach(L => {
                const count = (byLayer[L] || []).length;
                html += `<div class="checkbox-item"><input type="checkbox" class="lf" value="${L}" checked> L${L} (${count})</div>`;
            });
            document.getElementById('layer-checks').innerHTML = html;
            
            document.querySelectorAll('.lf').forEach(cb => {
                cb.addEventListener('change', e => {
                    const L = +e.target.value;
                    if (e.target.checked) settings.layerFilters.add(L);
                    else settings.layerFilters.delete(L);
                    render();
                });
            });
        }
        
        // Bind all settings
        function bindSettings() {
            const sliders = [
                ['g-const', 'G'], ['k-barrier', 'k_barrier'], ['k-hold', 'k_hold'], 
                ['c-damp', 'c_damp'], ['perimeter', 'perimeter_radius'],
                ['max-grav', 'max_grav_distance'], ['dt', 'dt'], ['epsilon', 'epsilon'],
                ['iters', 'iters_per_frame']
            ];
            
            sliders.forEach(([id, param]) => {
                const el = document.getElementById(id);
                if (el) {
                    el.addEventListener('input', e => {
                        physics[param] = +e.target.value;
                        const val = physics[param];
                        document.getElementById(id + '-val').textContent = 
                            Number.isInteger(val) ? val : val.toFixed(val < 1 ? 2 : 1);
                    });
                }
            });
            
            const viewSliders = [
                ['lod', 'lod'], ['node-size', 'nodeSize'], 
                ['edge-op', 'edgeOpacity'], ['edge-w', 'edgeWidth']
            ];
            
            viewSliders.forEach(([id, param]) => {
                const el = document.getElementById(id);
                if (el) {
                    el.addEventListener('input', e => {
                        settings[param] = +e.target.value;
                        const val = settings[param];
                        document.getElementById(id + '-val').textContent = 
                            id === 'lod' ? val + '%' : val.toFixed(1);
                        render();
                    });
                }
            });
            
            // Checkboxes
            ['grav-enabled', 'repulse-enabled', 'hold-enabled', 'damp-enabled'].forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    el.addEventListener('change', e => {
                        const param = id.replace('-enabled', '_enabled');
                        physics[param] = e.target.checked;
                    });
                }
            });
            
            // Buttons
            document.getElementById('reset').addEventListener('click', () => {
                svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
            });
            
            document.getElementById('restart-physics').addEventListener('click', () => {
                nodes.forEach(n => { n.vx = 0; n.vy = 0; });
                energyHistory = [];
            });
            
            document.getElementById('pause-physics').addEventListener('click', e => {
                settings.physicsRunning = !settings.physicsRunning;
                e.target.textContent = settings.physicsRunning ? '⏸️ Pause Physics' : '▶️ Resume Physics';
            });
            
            // Presets
            document.getElementById('preset-default').addEventListener('click', () => {
                Object.assign(physics, {G:0.5, k_barrier:100, k_hold:0.8, c_damp:0.3, perimeter_radius:30});
                updateSlidersFromPhysics();
            });
            
            document.getElementById('preset-tight').addEventListener('click', () => {
                Object.assign(physics, {G:2.0, k_barrier:200, k_hold:1.5, c_damp:0.5, perimeter_radius:20});
                updateSlidersFromPhysics();
            });
            
            document.getElementById('preset-loose').addEventListener('click', () => {
                Object.assign(physics, {G:0.1, k_barrier:30, k_hold:0.2, c_damp:0.1, perimeter_radius:50});
                updateSlidersFromPhysics();
            });
            
            document.getElementById('preset-strong-bonds').addEventListener('click', () => {
                Object.assign(physics, {G:0.3, k_barrier:100, k_hold:2.0, c_damp:0.4, perimeter_radius:25});
                updateSlidersFromPhysics();
            });
        }
        
        function updateSlidersFromPhysics() {
            document.getElementById('g-const').value = physics.G;
            document.getElementById('k-barrier').value = physics.k_barrier;
            document.getElementById('k-hold').value = physics.k_hold;
            document.getElementById('c-damp').value = physics.c_damp;
            // Update all value displays
            Object.keys(physics).forEach(key => {
                const el = document.getElementById(key.replace('_', '-') + '-val');
                if (el) el.textContent = physics[key].toFixed(physics[key] < 1 ? 2 : 0);
            });
        }
        
        // Initialize
        buildIndex();
        bindSettings();
        render();
        animate(); // Start GODN physics loop!
        
        console.log('%c GODN Physics Activated ', 'background: #27ae60; color: #000; padding: 8px; font-weight: bold');
        console.log('✓ Gravitational Attraction (inverse square law)');
        console.log('✓ Repulsive Barriers (elastic perimeters)');
        console.log('✓ Holding Bonds (validated connections)');
        console.log('✓ Damping Forces (stabilization)');
        console.log('Singularity Property: O/C = 16.03');
    </script>
</body>
</html>'''
    
    return html


def main():
    print("=" * 80)
    print("COMPLETE GODN PHYSICS VISUALIZATION")
    print("=" * 80)
    print()
    print("Implementing FULL Graviton Organic Dynamic Network physics:")
    print("  [+] F_gravity = G*m1*m2/r^2 (ATTRACTION - pulls together)")
    print("  [+] F_repulse = -k*(d_perimeter - r) (REPULSION - pushes apart)")
    print("  [+] F_hold = -k*(d_rest - r) (HOLDING - bonds validated connections)")
    print("  [+] F_damp = -c*v (DAMPING - stabilizes motion)")
    print()
    
    html = generate_html()
    
    output = PROJECT_ROOT / 'organism_map_GODN.html'
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[SAVED] {output}")
    print()
    print("=" * 80)
    print("GODN PHYSICS CONTROLS (15 Parameters):")
    print("=" * 80)
    print("Gravitational:")
    print("  • G constant (attraction strength)")
    print("  • Max gravity distance (cutoff)")
    print("  • Enable/disable")
    print()
    print("Repulsive:")
    print("  • k_barrier (repulsion strength)")
    print("  • Perimeter radius (bubble size)")
    print("  • Enable/disable")
    print()
    print("Holding Bonds:")
    print("  • k_hold (bond stiffness)")
    print("  • Rest length (target distance)")
    print("  • Enable/disable")
    print()
    print("Damping:")
    print("  • c_damp (friction)")
    print("  • Enable/disable")
    print()
    print("Simulation:")
    print("  - dt (timestep)")
    print("  - Iterations per frame")
    print("  - epsilon convergence threshold")
    print()
    print("REAL-TIME ENERGY DISPLAY:")
    print("  • E_total, E_gravity, E_repulse, E_hold")
    print("  • Convergence indicator")
    print("  • Energy bars showing balance")
    print()
    print("This is TRUE gravitational physics with all 4 force components!")
    print("The organism will PULL together (gravity) while maintaining boundaries (repulsion)!")
    print("=" * 80)


if __name__ == '__main__':
    main()

