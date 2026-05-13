#!/usr/bin/env python3
"""
Generate D3.js Interactive Visualization
Creates beautiful, zoomable, interactive graph of complete AIM-OS organism
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Color schemes by layer
LAYER_COLORS = {
    1: '#e74c3c',  # Red - Foundation
    2: '#3498db',  # Blue - Core Intelligence
    3: '#2ecc71',  # Green - Executive
    4: '#f39c12',  # Gold - Meta-Cognition
    5: '#9b59b6',  # Purple - Infrastructure
    6: '#1abc9c',  # Teal - Applications
}

# Node type colors
NODE_COLORS = {
    'system': '#2c3e50',
    'doc': '#f1c40f',
    'code': '#27ae60',
    'test': '#3498db',
    'index': '#e67e22',
    'concept': '#95a5a6',
    'nl_tag': '#9b59b6',
    'package': '#16a085',
    'quintet': '#e74c3c',
}

def generate_html():
    """Generate complete HTML with embedded D3.js visualization"""
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIM-OS Complete Organism Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0e27;
            color: #ffffff;
            overflow: hidden;
        }
        
        #container {
            width: 100vw;
            height: 100vh;
            position: relative;
        }
        
        #graph {
            width: 100%;
            height: 100%;
        }
        
        /* UI Controls */
        #controls {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 300px;
        }
        
        #controls h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #3498db;
        }
        
        .control-group {
            margin-bottom: 15px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 12px;
            color: #95a5a6;
        }
        
        input[type="range"] {
            width: 100%;
        }
        
        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .checkbox-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
        }
        
        button {
            width: 100%;
            padding: 10px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
        }
        
        button:hover {
            background: #2980b9;
        }
        
        /* Stats Panel */
        #stats {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            min-width: 200px;
        }
        
        #stats h3 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #3498db;
        }
        
        #stats .stat {
            font-size: 12px;
            margin: 5px 0;
            color: #ecf0f1;
        }
        
        #stats .stat strong {
            color: #3498db;
        }
        
        /* Legend */
        #legend {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        #legend h3 {
            font-size: 14px;
            margin-bottom: 10px;
            color: #3498db;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 5px 0;
            font-size: 11px;
        }
        
        .legend-color {
            width: 15px;
            height: 15px;
            border-radius: 3px;
        }
        
        /* Details Panel */
        #details {
            position: absolute;
            top: 20px;
            right: 250px;
            background: rgba(0, 0, 0, 0.9);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 400px;
            max-height: 80vh;
            overflow-y: auto;
            display: none;
        }
        
        #details.visible {
            display: block;
        }
        
        #details h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #3498db;
        }
        
        #details .detail-section {
            margin: 15px 0;
        }
        
        #details .detail-label {
            font-size: 11px;
            color: #95a5a6;
            margin-bottom: 3px;
        }
        
        #details .detail-value {
            font-size: 13px;
            color: #ecf0f1;
        }
        
        /* Nodes */
        .node {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .node:hover {
            stroke-width: 3px;
            filter: brightness(1.3);
        }
        
        .node.selected {
            stroke: #ffffff;
            stroke-width: 4px;
        }
        
        /* Links */
        .link {
            stroke-opacity: 0.6;
            transition: all 0.3s ease;
        }
        
        .link:hover {
            stroke-opacity: 1;
            stroke-width: 3px;
        }
        
        /* Labels */
        text {
            pointer-events: none;
            font-family: 'Segoe UI', sans-serif;
            font-size: 10px;
            fill: #ffffff;
            text-shadow: 0 0 3px #000000, 0 0 3px #000000;
        }
        
        /* Search */
        #search-container {
            margin-bottom: 15px;
        }
        
        #search-input {
            width: 100%;
            padding: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-radius: 5px;
            font-size: 12px;
        }
        
        #search-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div id="container">
        <svg id="graph"></svg>
        
        <div id="controls">
            <h2>🎛️ Controls</h2>
            
            <div id="search-container">
                <input type="text" id="search-input" placeholder="Search nodes..." />
            </div>
            
            <div class="control-group">
                <label for="zoom-slider">Zoom Level: <span id="zoom-value">0%</span></label>
                <input type="range" id="zoom-slider" min="0" max="100" value="0" />
            </div>
            
            <div class="control-group">
                <label>Show Layers:</label>
                <div class="checkbox-group">
                    <label><input type="checkbox" class="layer-filter" value="1" checked /> Layer 1 (Foundation)</label>
                    <label><input type="checkbox" class="layer-filter" value="2" checked /> Layer 2 (Intelligence)</label>
                    <label><input type="checkbox" class="layer-filter" value="3" checked /> Layer 3 (Executive)</label>
                    <label><input type="checkbox" class="layer-filter" value="4" checked /> Layer 4 (Meta-Cognition)</label>
                    <label><input type="checkbox" class="layer-filter" value="5" checked /> Layer 5 (Infrastructure)</label>
                    <label><input type="checkbox" class="layer-filter" value="6" checked /> Layer 6 (Applications)</label>
                </div>
            </div>
            
            <div class="control-group">
                <label>Show Types:</label>
                <div class="checkbox-group">
                    <label><input type="checkbox" class="type-filter" value="system" checked /> Systems</label>
                    <label><input type="checkbox" class="type-filter" value="doc" checked /> Docs</label>
                    <label><input type="checkbox" class="type-filter" value="code" /> Code</label>
                    <label><input type="checkbox" class="type-filter" value="test" /> Tests</label>
                    <label><input type="checkbox" class="type-filter" value="index" checked /> Indexes</label>
                    <label><input type="checkbox" class="type-filter" value="concept" /> Concepts</label>
                    <label><input type="checkbox" class="type-filter" value="nl_tag" /> NL Tags</label>
                </div>
            </div>
            
            <button id="reset-btn">Reset View</button>
            <button id="export-btn">Export PNG</button>
        </div>
        
        <div id="stats">
            <h3>📊 Statistics</h3>
            <div class="stat"><strong>Nodes:</strong> <span id="stat-nodes">0</span></div>
            <div class="stat"><strong>Edges:</strong> <span id="stat-edges">0</span></div>
            <div class="stat"><strong>Zoom:</strong> <span id="stat-zoom">0%</span></div>
            <div class="stat"><strong>Ratio:</strong> <span id="stat-ratio">16.03</span></div>
        </div>
        
        <div id="legend">
            <h3>🎨 Legend</h3>
            <div class="legend-item">
                <div class="legend-color" style="background: ''' + LAYER_COLORS[1] + '''"></div>
                <span>Layer 1: Foundation</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: ''' + LAYER_COLORS[2] + '''"></div>
                <span>Layer 2: Intelligence</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: ''' + LAYER_COLORS[3] + '''"></div>
                <span>Layer 3: Executive</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: ''' + LAYER_COLORS[4] + '''"></div>
                <span>Layer 4: Meta-Cognition</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: ''' + LAYER_COLORS[5] + '''"></div>
                <span>Layer 5: Infrastructure</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: ''' + LAYER_COLORS[6] + '''"></div>
                <span>Layer 6: Applications</span>
            </div>
        </div>
        
        <div id="details">
            <h2 id="details-title">Node Details</h2>
            <div id="details-content"></div>
        </div>
    </div>
    
    <script>
        // Load relationship data
        const data = ''' + '{PLACEHOLDER}' + ''';
        
        // Set up SVG
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select('#graph')
            .attr('width', width)
            .attr('height', height);
        
        const g = svg.append('g');
        
        // Set up zoom
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
                updateZoomLevel(event.transform.k);
            });
        
        svg.call(zoom);
        
        // Filter nodes by zoom level and filters
        let currentZoom = 0;
        let layerFilters = new Set([1, 2, 3, 4, 5, 6]);
        let typeFilters = new Set(['system', 'doc', 'index']);
        
        function filterNodes() {
            return data.nodes.filter(n => {
                // Check zoom level
                if (!n.zoom_levels || !n.zoom_levels.includes(Math.floor(currentZoom / 20))) {
                    return false;
                }
                
                // Check layer filter
                if (n.layer && !layerFilters.has(n.layer)) {
                    return false;
                }
                
                // Check type filter
                if (!typeFilters.has(n.type)) {
                    return false;
                }
                
                return true;
            });
        }
        
        function filterEdges(nodes) {
            const nodeIds = new Set(nodes.map(n => n.id));
            return data.edges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));
        }
        
        // Color function
        function getNodeColor(node) {
            if (node.layer) {
                return ''' + str(LAYER_COLORS) + '''[node.layer];
            }
            return ''' + str(NODE_COLORS) + '''[node.type] || '#95a5a6';
        }
        
        // Size function
        function getNodeSize(node) {
            if (node.type === 'system') return 20;
            if (node.type === 'package') return 12;
            if (node.type === 'doc') return 8;
            if (node.type === 'code') return 6;
            if (node.type === 'test') return 6;
            if (node.type === 'index') return 15;
            if (node.type === 'concept') return 4;
            if (node.type === 'nl_tag') return 3;
            return 5;
        }
        
        // Create force simulation
        const simulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => getNodeSize(d) + 5));
        
        // Render function
        function render() {
            const nodes = filterNodes();
            const edges = filterEdges(nodes);
            
            // Update stats
            document.getElementById('stat-nodes').textContent = nodes.length;
            document.getElementById('stat-edges').textContent = edges.length;
            
            // Clear
            g.selectAll('*').remove();
            
            // Draw links
            const link = g.append('g')
                .selectAll('line')
                .data(edges)
                .join('line')
                .attr('class', 'link')
                .attr('stroke', d => {
                    if (d.type === 'depends_on') return '#e74c3c';
                    if (d.type === 'provides_to') return '#3498db';
                    if (d.type === 'expands_to') return '#f1c40f';
                    if (d.type === 'imports_from') return '#27ae60';
                    if (d.type === 'tests') return '#3498db';
                    if (d.type === 'indexes') return '#e67e22';
                    return '#95a5a6';
                })
                .attr('stroke-width', d => {
                    if (d.strength === 'critical') return 3;
                    if (d.strength === 'strong') return 2;
                    return 1;
                })
                .attr('stroke-dasharray', d => {
                    if (d.type === 'indexes' || d.type === 'monitors') return '5,5';
                    return null;
                });
            
            // Draw nodes
            const node = g.append('g')
                .selectAll('circle')
                .data(nodes)
                .join('circle')
                .attr('class', 'node')
                .attr('r', getNodeSize)
                .attr('fill', getNodeColor)
                .attr('stroke', '#ffffff')
                .attr('stroke-width', 1.5)
                .on('click', (event, d) => showDetails(d))
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            // Draw labels (only for larger nodes)
            const label = g.append('g')
                .selectAll('text')
                .data(nodes.filter(n => n.type === 'system' || n.type === 'package' || n.type === 'index'))
                .join('text')
                .text(d => d.name || d.id.split(':')[1])
                .attr('font-size', d => d.type === 'system' ? '12px' : '10px')
                .attr('text-anchor', 'middle')
                .attr('dy', d => getNodeSize(d) + 15);
            
            // Update simulation
            simulation.nodes(nodes);
            simulation.force('link').links(edges);
            simulation.alpha(0.3).restart();
            
            // Tick function
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });
        }
        
        // Drag functions
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragged(event) {
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }
        
        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }
        
        // Update zoom level
        function updateZoomLevel(scale) {
            currentZoom = Math.min(100, Math.max(0, (scale - 0.1) / 9.9 * 100));
            document.getElementById('zoom-value').textContent = Math.round(currentZoom) + '%';
            document.getElementById('stat-zoom').textContent = Math.round(currentZoom) + '%';
            render();
        }
        
        // Show node details
        function showDetails(node) {
            const panel = document.getElementById('details');
            const content = document.getElementById('details-content');
            
            let html = '';
            html += `<div class="detail-section">`;
            html += `<div class="detail-label">Type</div>`;
            html += `<div class="detail-value">${node.type}</div>`;
            html += `</div>`;
            
            if (node.system) {
                html += `<div class="detail-section">`;
                html += `<div class="detail-label">System</div>`;
                html += `<div class="detail-value">${node.system}</div>`;
                html += `</div>`;
            }
            
            if (node.path) {
                html += `<div class="detail-section">`;
                html += `<div class="detail-label">Path</div>`;
                html += `<div class="detail-value" style="font-size: 10px; word-break: break-all;">${node.path}</div>`;
                html += `</div>`;
            }
            
            if (node.loc) {
                html += `<div class="detail-section">`;
                html += `<div class="detail-label">Lines of Code</div>`;
                html += `<div class="detail-value">${node.loc.toLocaleString()}</div>`;
                html += `</div>`;
            }
            
            if (node.words) {
                html += `<div class="detail-section">`;
                html += `<div class="detail-label">Word Count</div>`;
                html += `<div class="detail-value">${node.words.toLocaleString()}</div>`;
                html += `</div>`;
            }
            
            if (node.test_count) {
                html += `<div class="detail-section">`;
                html += `<div class="detail-label">Tests</div>`;
                html += `<div class="detail-value">${node.test_count}</div>`;
                html += `</div>`;
            }
            
            content.innerHTML = html;
            panel.classList.add('visible');
            
            document.getElementById('details-title').textContent = node.name || node.id;
        }
        
        // Event listeners
        document.getElementById('zoom-slider').addEventListener('input', (e) => {
            const zoomPercent = parseInt(e.target.value);
            currentZoom = zoomPercent;
            document.getElementById('zoom-value').textContent = zoomPercent + '%';
            render();
        });
        
        document.querySelectorAll('.layer-filter').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const layer = parseInt(e.target.value);
                if (e.target.checked) {
                    layerFilters.add(layer);
                } else {
                    layerFilters.delete(layer);
                }
                render();
            });
        });
        
        document.querySelectorAll('.type-filter').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const type = e.target.value;
                if (e.target.checked) {
                    typeFilters.add(type);
                } else {
                    typeFilters.delete(type);
                }
                render();
            });
        });
        
        document.getElementById('reset-btn').addEventListener('click', () => {
            currentZoom = 0;
            document.getElementById('zoom-slider').value = 0;
            svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
            render();
        });
        
        document.getElementById('search-input').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (!query) return;
            
            const found = data.nodes.find(n => 
                (n.name && n.name.toLowerCase().includes(query)) ||
                n.id.toLowerCase().includes(query)
            );
            
            if (found) {
                showDetails(found);
                // Highlight node
                d3.selectAll('.node').classed('selected', d => d.id === found.id);
            }
        });
        
        // Initial render
        render();
    </script>
</body>
</html>'''
    
    return html


def main():
    print("=" * 80)
    print("D3.JS VISUALIZATION GENERATOR")
    print("=" * 80)
    print()
    
    # Load relationship data
    rel_path = PROJECT_ROOT / 'COMPLETE_RELATIONSHIPS.json'
    
    if not rel_path.exists():
        print(f"[ERROR] {rel_path} not found!")
        print("Run: python scripts/extract_complete_relationships.py first")
        return
    
    print(f"Loading relationships from {rel_path}...")
    with open(rel_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"  Loaded {len(data['nodes'])} nodes, {len(data['edges'])} edges")
    
    # Generate HTML
    print("Generating HTML visualization...")
    html = generate_html()
    
    # Embed data
    data_json = json.dumps(data, indent=None)
    html = html.replace('{PLACEHOLDER}', data_json)
    
    # Save
    output_path = PROJECT_ROOT / 'complete_organism_map.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[SAVED] Interactive visualization: {output_path}")
    print()
    print("=" * 80)
    print("COMPLETE!")
    print("=" * 80)
    print(f"\nOpen in browser: {output_path}")
    print("\nFeatures:")
    print("  - Zoom slider (0-100%)")
    print("  - Layer filters (show/hide layers)")
    print("  - Type filters (show/hide node types)")
    print("  - Search (find any node)")
    print("  - Click nodes for details")
    print("  - Drag nodes to rearrange")
    print("  - Scroll to zoom")
    print()
    print("Shows:")
    print(f"  - {len(data['nodes'])} total nodes")
    print(f"  - {len(data['edges'])} total relationships")
    print("  - Complete AIM-OS organism")
    print("  - All 70+ systems")
    print("  - All documentation hierarchy")
    print("  - All code relationships")
    print()
    print("Visual proof of singularity property! 🌟")
    print("=" * 80)


if __name__ == '__main__':
    main()

