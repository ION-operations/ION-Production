"""
Generate mesh visualization data and HTML.

Usage:
    python mesh_visualizer.py         # Generate visualization
    python mesh_visualizer.py --open  # Generate and open in browser
"""
import sys
import os
import json
import time
import webbrowser
import hashlib

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(WORKSPACE, 'scripts', 'ai_engine'))
sys.path.insert(0, os.path.join(WORKSPACE, 'scripts', 'agent_comms'))

from roundtable import Roundtable
from agent_mesh import (
    AffinityGraph, ComfortZone, CascadeProtocol,
    AGENT_HIERARCHY, get_rank_priority, get_rank_label,
)

# ================================================================
#  AFFINITY CACHE
# ================================================================

CACHE_DIR = os.path.join(WORKSPACE, '.agent', 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'affinity_matrix.json')


def _domain_hash(seats) -> str:
    """Hash of all domain contexts to detect changes."""
    h = hashlib.md5()
    for s in sorted(seats, key=lambda x: x.system_id):
        h.update(s.system_id.encode())
        h.update(str(len(s.domain_context)).encode())
    return h.hexdigest()


def load_cached_graph(seats) -> dict:
    """Load cached affinity data if domain hasn't changed."""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        if cache.get('domain_hash') == _domain_hash(seats):
            return cache
    except Exception:
        pass
    return None


def save_graph_cache(graph, seats):
    """Save affinity data to cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Serialize graph data
    nodes = []
    for agent_id, node in graph.nodes.items():
        hier = AGENT_HIERARCHY.get(agent_id, {'rank': 'worker', 'tier': 5, 'priority': 0.5})
        nodes.append({
            'id': agent_id,
            'name': node.agent_name,
            'vocab_size': node.vocab_size,
            'rank': hier['rank'],
            'tier': hier['tier'],
            'priority': hier['priority'],
        })
    
    edges = []
    seen = set()
    for (a, b), edge in graph.edges.items():
        key = tuple(sorted((a, b)))
        if key not in seen:
            seen.add(key)
            edges.append({
                'source': edge.agent_a,
                'target': edge.agent_b,
                'weight': round(edge.weight, 4),
                'shared_terms': edge.shared_terms,
                'top_shared': edge.top_shared[:5],
            })
    
    cache = {
        'domain_hash': _domain_hash(seats),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'nodes': nodes,
        'edges': edges,
        'stats': graph.stats(),
    }
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    
    return cache


def generate_html(data: dict, output_path: str):
    """Generate premium hierarchical n8n-style visualization."""
    
    nodes_json = json.dumps(data['nodes'])
    edges_json = json.dumps(data['edges'])
    stats_json = json.dumps(data['stats'])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIM-OS Agent Neural Mesh</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  
  body {{
    background: #08090d;
    color: #c8ccd4;
    font-family: 'Inter', -apple-system, sans-serif;
    overflow: hidden;
    height: 100vh;
  }}
  
  /* ── Header ── */
  .header {{
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 200;
    height: 56px;
    display: flex;
    align-items: center;
    padding: 0 28px;
    gap: 14px;
    background: rgba(8,9,13,0.92);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }}
  .header h1 {{
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.4px;
    color: #e2e4e9;
  }}
  .header h1 span {{ 
    background: linear-gradient(135deg, #facc15 0%, #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 4px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: #888;
    letter-spacing: 0.5px;
  }}
  .badge-live {{
    background: rgba(34,197,94,0.1);
    border-color: rgba(34,197,94,0.25);
    color: #22c55e;
  }}
  .controls {{
    margin-left: auto;
    display: flex; gap: 8px; align-items: center;
  }}
  .controls label {{
    font-size: 11px; color: #666;
    display: flex; align-items: center; gap: 6px;
    cursor: pointer;
  }}
  .controls input[type=checkbox] {{
    accent-color: #60a5fa;
  }}
  
  /* ── Tier Labels ── */
  .tier-labels {{
    position: fixed;
    left: 0; top: 56px; bottom: 44px;
    width: 32px;
    z-index: 150;
    display: flex;
    flex-direction: column;
    pointer-events: none;
  }}
  .tier-label {{
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .tier-label span {{
    writing-mode: vertical-rl;
    text-orientation: mixed;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0.25;
  }}
  .tier-label.t1 span {{ color: #facc15; }}
  .tier-label.t2 span {{ color: #a855f7; }}
  .tier-label.t3 span {{ color: #3b82f6; }}
  .tier-label.t4 span {{ color: #22c55e; }}
  
  /* ── Stats Bar ── */
  .stats-bar {{
    position: fixed;
    bottom: 0; left: 0; right: 0;
    z-index: 200;
    height: 44px;
    display: flex;
    align-items: center;
    padding: 0 28px;
    gap: 28px;
    background: rgba(8,9,13,0.92);
    backdrop-filter: blur(16px);
    border-top: 1px solid rgba(255,255,255,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #555;
  }}
  .stat {{ display: flex; align-items: center; gap: 6px; }}
  .stat-val {{ color: #8b9cf7; font-weight: 600; }}
  .stat-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    display: inline-block;
  }}
  
  /* ── Canvas ── */
  .canvas-wrap {{
    position: fixed;
    top: 56px; left: 32px; right: 0; bottom: 44px;
    overflow: hidden;
  }}
  svg {{
    width: 100%;
    height: 100%;
  }}
  
  /* ── Node Cards ── */
  .node-card {{
    cursor: pointer;
    transition: opacity 0.3s ease;
  }}
  .node-card:hover .card-bg {{
    filter: brightness(1.3);
  }}
  .card-bg {{
    rx: 10; ry: 10;
    transition: filter 0.2s ease;
  }}
  
  /* ── Info Panel ── */
  .info-panel {{
    position: fixed;
    top: 72px; right: 16px;
    width: 300px;
    z-index: 180;
    background: rgba(12,13,18,0.95);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 20px;
    display: none;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  }}
  .info-panel.visible {{ display: block; }}
  .info-panel h3 {{
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
  }}
  .info-meta {{
    font-size: 11px;
    color: #666;
    margin-bottom: 12px;
    display: flex; gap: 8px; align-items: center;
  }}
  .rank-pill {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .pill-command    {{ background: rgba(250,204,21,0.15); color: #facc15; border: 1px solid rgba(250,204,21,0.3); }}
  .pill-executive  {{ background: rgba(168,85,247,0.15); color: #a855f7; border: 1px solid rgba(168,85,247,0.3); }}
  .pill-lead       {{ background: rgba(59,130,246,0.15); color: #3b82f6; border: 1px solid rgba(59,130,246,0.3); }}
  .pill-specialist {{ background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }}
  
  .neighbor-list {{
    margin-top: 12px;
  }}
  .neighbor-list h4 {{
    font-size: 10px;
    font-weight: 600;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
  }}
  .nb-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 12px;
  }}
  .nb-row .nb-id {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 11px;
  }}
  .nb-row .nb-score {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
  }}
  .shared-terms {{
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }}
  .term-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    padding: 2px 7px;
    border-radius: 3px;
    background: rgba(96,165,250,0.1);
    border: 1px solid rgba(96,165,250,0.15);
    color: #60a5fa;
  }}
  
  /* ── Grid Lines ── */
  .grid-line {{
    stroke: rgba(255,255,255,0.03);
    stroke-dasharray: 4,8;
  }}
  
  /* ── Edge Labels ── */
  .edge-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    fill: #444;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }}
</style>
</head>
<body>

<div class="header">
  <h1><span>AGENT NEURAL MESH</span></h1>
  <span class="badge">AIM-OS</span>
  <span class="badge badge-live">LIVE</span>
  <div class="controls">
    <label><input type="checkbox" id="showWeak"> Show weak edges</label>
    <label><input type="checkbox" id="showLabels" checked> Edge scores</label>
  </div>
</div>

<div class="tier-labels">
  <div class="tier-label t1"><span>Command</span></div>
  <div class="tier-label t2"><span>Executive</span></div>
  <div class="tier-label t3"><span>Lead</span></div>
  <div class="tier-label t4"><span>Specialist</span></div>
</div>

<div class="info-panel" id="infoPanel">
  <h3 id="panelName"></h3>
  <div class="info-meta">
    <span class="rank-pill" id="panelRank"></span>
    <span id="panelVocab"></span>
  </div>
  <div class="neighbor-list">
    <h4>Affinities</h4>
    <div id="panelNeighbors"></div>
  </div>
  <div class="shared-terms" id="panelTerms"></div>
</div>

<div class="stats-bar" id="statsBar"></div>
<div class="canvas-wrap"><svg id="graph"></svg></div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = {nodes_json};
const edges = {edges_json};
const stats = {stats_json};

// ── Palette ──
const palette = {{
  command:    {{ fill: '#1a1805', stroke: '#facc15', text: '#facc15', glow: 'rgba(250,204,21,0.15)' }},
  executive:  {{ fill: '#150e1e', stroke: '#a855f7', text: '#a855f7', glow: 'rgba(168,85,247,0.12)' }},
  lead:       {{ fill: '#0c1220', stroke: '#3b82f6', text: '#3b82f6', glow: 'rgba(59,130,246,0.10)' }},
  specialist: {{ fill: '#0a1510', stroke: '#22c55e', text: '#22c55e', glow: 'rgba(34,197,94,0.08)' }},
  worker:     {{ fill: '#111', stroke: '#555', text: '#888', glow: 'rgba(128,128,128,0.05)' }},
}};

// ── Hierarchical Layout ──
const CARD_W = 160, CARD_H = 72;
const tiers = {{ command: [], executive: [], lead: [], specialist: [], worker: [] }};
nodes.forEach(n => tiers[n.rank].push(n));

const svgEl = document.querySelector('#graph');
const rect = svgEl.parentElement.getBoundingClientRect();
const W = rect.width, H = rect.height;

// Vertical positions per tier
const tierY = {{
  command:    H * 0.08,
  executive:  H * 0.30,
  lead:       H * 0.54,
  specialist: H * 0.80,
  worker:     H * 0.95,
}};

// Position nodes horizontally centered per tier
Object.keys(tiers).forEach(rank => {{
  const tier = tiers[rank];
  if (tier.length === 0) return;
  const totalW = tier.length * (CARD_W + 24) - 24;
  const startX = (W - totalW) / 2;
  tier.forEach((n, i) => {{
    n.x = startX + i * (CARD_W + 24) + CARD_W / 2;
    n.y = tierY[rank] + CARD_H / 2;
  }});
}});

// Node lookup
const nodeMap = {{}};
nodes.forEach(n => nodeMap[n.id] = n);

// ── Stats Bar ──
document.getElementById('statsBar').innerHTML = `
  <div class="stat"><span class="stat-dot" style="background:#facc15"></span><span class="stat-val">${{stats.agents}}</span> agents</div>
  <div class="stat"><span class="stat-dot" style="background:#60a5fa"></span><span class="stat-val">${{stats.edges}}</span> edges</div>
  <div class="stat"><span class="stat-dot" style="background:#22c55e"></span><span class="stat-val">${{stats.strong_edges}}</span> strong</div>
  <div class="stat"><span class="stat-dot" style="background:#60a5fa"></span><span class="stat-val">${{stats.medium_edges}}</span> medium</div>
  <div class="stat"><span class="stat-dot" style="background:#333"></span><span class="stat-val">${{stats.weak_edges}}</span> weak</div>
  <div class="stat">avg <span class="stat-val">${{stats.avg_affinity.toFixed(3)}}</span></div>
  <div class="stat">max <span class="stat-val">${{stats.max_affinity.toFixed(3)}}</span></div>
`;

// ── D3 Setup ──
const svg = d3.select('#graph')
  .attr('viewBox', `0 0 ${{W}} ${{H}}`);

// Defs
const defs = svg.append('defs');

// Glow filters per rank
Object.entries(palette).forEach(([rank, p]) => {{
  const f = defs.append('filter').attr('id', `glow-${{rank}}`)
    .attr('x','-50%').attr('y','-50%').attr('width','200%').attr('height','200%');
  f.append('feDropShadow')
    .attr('dx', 0).attr('dy', 0)
    .attr('stdDeviation', 8)
    .attr('flood-color', p.glow)
    .attr('flood-opacity', 1);
}});

// Tier separator lines
[0.19, 0.42, 0.67].forEach(pct => {{
  svg.append('line')
    .attr('class', 'grid-line')
    .attr('x1', 40).attr('y1', H * pct)
    .attr('x2', W - 20).attr('y2', H * pct);
}});

// ── Edge Functions ──
function edgeColor(w) {{
  if (w >= 0.3) return '#22c55e';
  if (w >= 0.15) return '#3b82f6';
  return '#2a2a2a';
}}
function edgeOpacity(w) {{
  if (w >= 0.3) return 0.5;
  if (w >= 0.15) return 0.25;
  return 0.12;
}}
function edgeWidth(w) {{
  if (w >= 0.3) return 2;
  if (w >= 0.15) return 1.2;
  return 0.6;
}}

// ── Draw Edges ──
const edgeGroup = svg.append('g').attr('class', 'edges');

const edgePaths = edgeGroup.selectAll('path')
  .data(edges)
  .enter().append('path')
  .attr('d', d => {{
    const s = nodeMap[typeof d.source === 'object' ? d.source.id : d.source];
    const t = nodeMap[typeof d.target === 'object' ? d.target.id : d.target];
    if (!s || !t) return '';
    const midY = (s.y + t.y) / 2;
    return `M${{s.x}},${{s.y}} C${{s.x}},${{midY}} ${{t.x}},${{midY}} ${{t.x}},${{t.y}}`;
  }})
  .attr('fill', 'none')
  .attr('stroke', d => edgeColor(d.weight))
  .attr('stroke-width', d => edgeWidth(d.weight))
  .attr('stroke-opacity', d => edgeOpacity(d.weight))
  .attr('class', d => d.weight < 0.15 ? 'edge-weak' : '');

// Edge score labels
const edgeLabels = edgeGroup.selectAll('text')
  .data(edges.filter(e => e.weight >= 0.15))
  .enter().append('text')
  .attr('class', 'edge-label')
  .attr('x', d => {{
    const s = nodeMap[typeof d.source === 'object' ? d.source.id : d.source];
    const t = nodeMap[typeof d.target === 'object' ? d.target.id : d.target];
    return s && t ? (s.x + t.x) / 2 : 0;
  }})
  .attr('y', d => {{
    const s = nodeMap[typeof d.source === 'object' ? d.source.id : d.source];
    const t = nodeMap[typeof d.target === 'object' ? d.target.id : d.target];
    return s && t ? (s.y + t.y) / 2 : 0;
  }})
  .attr('text-anchor', 'middle')
  .attr('dominant-baseline', 'middle')
  .text(d => d.weight.toFixed(2));

// Hide weak edges initially
document.querySelectorAll('.edge-weak').forEach(e => e.style.display = 'none');

// ── Draw Node Cards ──
const nodeGroup = svg.append('g').attr('class', 'nodes');

const cards = nodeGroup.selectAll('g')
  .data(nodes)
  .enter().append('g')
  .attr('class', 'node-card')
  .attr('transform', d => `translate(${{d.x - CARD_W/2}}, ${{d.y - CARD_H/2}})`);

// Card background
cards.append('rect')
  .attr('class', 'card-bg')
  .attr('width', CARD_W).attr('height', CARD_H)
  .attr('fill', d => palette[d.rank].fill)
  .attr('stroke', d => palette[d.rank].stroke)
  .attr('stroke-width', 1.5)
  .attr('filter', d => `url(#glow-${{d.rank}})`);

// Left accent bar
cards.append('rect')
  .attr('x', 0).attr('y', 0)
  .attr('width', 3).attr('height', CARD_H)
  .attr('rx', 1.5)
  .attr('fill', d => palette[d.rank].stroke)
  .attr('opacity', 0.6);

// Agent ID label
cards.append('text')
  .attr('x', 14).attr('y', 22)
  .attr('fill', d => palette[d.rank].text)
  .attr('font-size', '13px')
  .attr('font-weight', '700')
  .attr('font-family', "'JetBrains Mono', monospace")
  .text(d => d.id.toUpperCase());

// Agent name
cards.append('text')
  .attr('x', 14).attr('y', 38)
  .attr('fill', '#6b7280')
  .attr('font-size', '9px')
  .attr('font-weight', '500')
  .text(d => d.name);

// Rank badge
cards.append('rect')
  .attr('x', 14).attr('y', 48)
  .attr('width', d => d.rank.length * 6.5 + 12)
  .attr('height', 16)
  .attr('rx', 3)
  .attr('fill', d => palette[d.rank].glow)
  .attr('stroke', d => palette[d.rank].stroke)
  .attr('stroke-width', 0.5)
  .attr('stroke-opacity', 0.4);

cards.append('text')
  .attr('x', 20).attr('y', 60)
  .attr('fill', d => palette[d.rank].text)
  .attr('font-size', '8px')
  .attr('font-weight', '600')
  .attr('font-family', "'JetBrains Mono', monospace")
  .attr('letter-spacing', '0.5px')
  .text(d => d.rank.toUpperCase());

// Vocab count (right side)
cards.append('text')
  .attr('x', CARD_W - 10).attr('y', 22)
  .attr('text-anchor', 'end')
  .attr('fill', '#444')
  .attr('font-size', '9px')
  .attr('font-family', "'JetBrains Mono', monospace")
  .text(d => `${{d.vocab_size}}t`);

// ── Interactivity ──
let selectedNode = null;

cards.on('click', function(event, d) {{
  event.stopPropagation();
  selectedNode = d;
  highlightNode(d);
  showInfoPanel(d);
}});

svg.on('click', () => {{
  selectedNode = null;
  resetHighlight();
  document.getElementById('infoPanel').classList.remove('visible');
}});

function highlightNode(d) {{
  const neighbors = new Set([d.id]);
  edges.forEach(e => {{
    const sid = typeof e.source === 'object' ? e.source.id : e.source;
    const tid = typeof e.target === 'object' ? e.target.id : e.target;
    if (sid === d.id) neighbors.add(tid);
    if (tid === d.id) neighbors.add(sid);
  }});
  
  cards.transition().duration(200)
    .style('opacity', n => neighbors.has(n.id) ? 1 : 0.12);
  
  edgePaths.transition().duration(200)
    .attr('stroke-opacity', e => {{
      const sid = typeof e.source === 'object' ? e.source.id : e.source;
      const tid = typeof e.target === 'object' ? e.target.id : e.target;
      return (sid === d.id || tid === d.id) ? 0.8 : 0.03;
    }})
    .attr('stroke-width', e => {{
      const sid = typeof e.source === 'object' ? e.source.id : e.source;
      const tid = typeof e.target === 'object' ? e.target.id : e.target;
      return (sid === d.id || tid === d.id) ? edgeWidth(e.weight) * 2 : 0.3;
    }});
  
  edgeLabels.transition().duration(200)
    .style('opacity', e => {{
      const sid = typeof e.source === 'object' ? e.source.id : e.source;
      const tid = typeof e.target === 'object' ? e.target.id : e.target;
      return (sid === d.id || tid === d.id) ? 1 : 0.08;
    }});
}}

function resetHighlight() {{
  cards.transition().duration(200).style('opacity', 1);
  edgePaths.transition().duration(200)
    .attr('stroke-opacity', d => edgeOpacity(d.weight))
    .attr('stroke-width', d => edgeWidth(d.weight));
  edgeLabels.transition().duration(200).style('opacity', 1);
}}

function showInfoPanel(d) {{
  const panel = document.getElementById('infoPanel');
  panel.classList.add('visible');
  document.getElementById('panelName').innerText = d.id.toUpperCase();
  document.getElementById('panelName').style.color = palette[d.rank].text;
  
  const rankEl = document.getElementById('panelRank');
  rankEl.className = `rank-pill pill-${{d.rank}}`;
  rankEl.innerText = d.rank;
  document.getElementById('panelVocab').innerText = `${{d.vocab_size}} terms`;
  
  // Neighbors
  const nb = edges
    .filter(e => {{
      const sid = typeof e.source === 'object' ? e.source.id : e.source;
      const tid = typeof e.target === 'object' ? e.target.id : e.target;
      return sid === d.id || tid === d.id;
    }})
    .map(e => {{
      const sid = typeof e.source === 'object' ? e.source.id : e.source;
      const tid = typeof e.target === 'object' ? e.target.id : e.target;
      return {{ id: sid === d.id ? tid : sid, w: e.weight, shared: e.top_shared }};
    }})
    .sort((a,b) => b.w - a.w);
  
  let html = '';
  nb.forEach(n => {{
    const color = n.w >= 0.3 ? '#22c55e' : n.w >= 0.15 ? '#3b82f6' : '#444';
    html += `<div class="nb-row"><span class="nb-id">${{n.id.toUpperCase()}}</span><span class="nb-score" style="color:${{color}}">${{n.w.toFixed(3)}}</span></div>`;
  }});
  document.getElementById('panelNeighbors').innerHTML = html;
  
  // Shared terms with top neighbor
  if (nb.length && nb[0].shared) {{
    document.getElementById('panelTerms').innerHTML = 
      nb[0].shared.map(t => `<span class="term-tag">${{t}}</span>`).join('');
  }}
}}

// ── Controls ──
document.getElementById('showWeak').addEventListener('change', e => {{
  document.querySelectorAll('.edge-weak').forEach(el => 
    el.style.display = e.target.checked ? '' : 'none');
}});

document.getElementById('showLabels').addEventListener('change', e => {{
  edgeLabels.style('display', e.target.checked ? '' : 'none');
}});
</script>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


# ================================================================
#  DYNAMIC HIERARCHY
# ================================================================

HIERARCHY_LOG = os.path.join(CACHE_DIR, 'hierarchy_log.json')


def load_hierarchy_log():
    """Load contribution history."""
    if os.path.exists(HIERARCHY_LOG):
        with open(HIERARCHY_LOG, 'r') as f:
            return json.load(f)
    return {'contributions': {}, 'total_discussions': 0}


def record_contribution(agent_id, zone, confidence, question):
    """Record a contribution for dynamic hierarchy tracking."""
    log = load_hierarchy_log()
    
    if agent_id not in log['contributions']:
        log['contributions'][agent_id] = {
            'total': 0, 'core': 0, 'edge': 0, 'outside': 0,
            'avg_confidence': 0.0, 'questions': [],
        }
    
    entry = log['contributions'][agent_id]
    entry['total'] += 1
    entry[zone] += 1
    
    # Running average confidence
    old_avg = entry['avg_confidence']
    entry['avg_confidence'] = old_avg + (confidence - old_avg) / entry['total']
    
    # Keep last 20 questions
    entry['questions'] = (entry['questions'] + [question])[-20:]
    
    log['total_discussions'] += 1
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(HIERARCHY_LOG, 'w') as f:
        json.dump(log, f, indent=2)
    
    return entry


def compute_dynamic_rank(agent_id):
    """Compute dynamic rank adjustment based on contribution history."""
    log = load_hierarchy_log()
    entry = log['contributions'].get(agent_id)
    
    if not entry or entry['total'] < 3:
        return 0.0  # Not enough data
    
    # Promotion signal: high core ratio + high confidence
    core_ratio = entry['core'] / max(entry['total'], 1)
    confidence = entry['avg_confidence']
    
    # Score: -0.1 to +0.1 adjustment
    score = (core_ratio * 0.6 + confidence * 0.4) - 0.5
    return max(-0.1, min(0.1, score * 0.2))


def get_hierarchy_report():
    """Generate a hierarchy report with dynamic adjustments."""
    log = load_hierarchy_log()
    report = []
    
    for agent_id, entry in sorted(
        log['contributions'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    ):
        base = get_rank_priority(agent_id)
        dynamic = compute_dynamic_rank(agent_id)
        adjusted = base + dynamic
        
        report.append({
            'agent_id': agent_id,
            'rank': get_rank_label(agent_id),
            'base_priority': base,
            'dynamic_adjustment': round(dynamic, 3),
            'adjusted_priority': round(adjusted, 3),
            'contributions': entry['total'],
            'core_ratio': round(entry['core'] / max(entry['total'], 1), 2),
            'avg_confidence': round(entry['avg_confidence'], 3),
        })
    
    return report


# ================================================================
#  CLI
# ================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AIM-OS Mesh Visualizer")
    parser.add_argument("command", choices=["visualize", "cache", "hierarchy"],
                       help="Command to run")
    parser.add_argument("--open", action="store_true",
                       help="Open visualization in browser")
    parser.add_argument("--output", default=None,
                       help="Output path for visualization")
    args = parser.parse_args()
    
    if args.command == "visualize":
        print("  Convening roundtable...")
        rt = Roundtable()
        rt.convene("Neural Mesh Visualization")
        
        print("  Building affinity graph...")
        graph = AffinityGraph.from_seats(rt.seats)
        
        print("  Saving cache...")
        data = save_graph_cache(graph, rt.seats)
        
        output = args.output or os.path.join(WORKSPACE, 'mesh_visualization.html')
        print(f"  Generating visualization -> {output}")
        generate_html(data, output)
        
        stats = graph.stats()
        print(f"\n  {stats['agents']} agents, {stats['edges']} edges")
        print(f"  Strong: {stats['strong_edges']}, Medium: {stats['medium_edges']}, "
              f"Weak: {stats['weak_edges']}")
        
        if args.open:
            webbrowser.open(f'file:///{output}')
            print("  Opened in browser.")
    
    elif args.command == "cache":
        print("  Convening roundtable...")
        rt = Roundtable()
        rt.convene("Cache Rebuild")
        
        print("  Building affinity graph...")
        graph = AffinityGraph.from_seats(rt.seats)
        
        data = save_graph_cache(graph, rt.seats)
        print(f"  Cached to {CACHE_FILE}")
        print(f"  Hash: {data['domain_hash']}")
        print(f"  Timestamp: {data['timestamp']}")
    
    elif args.command == "hierarchy":
        report = get_hierarchy_report()
        if not report:
            print("  No contribution history yet. Run mesh discussions first.")
            return
        
        print(f"\n  {'Agent':12s} {'Rank':12s} {'Base':>6s} {'Adj':>6s} {'Final':>6s} "
              f"{'Core%':>6s} {'AvgConf':>7s} {'Total':>5s}")
        print("  " + "-" * 70)
        for r in report:
            print(f"  {r['agent_id']:12s} {r['rank']:12s} "
                  f"{r['base_priority']:>5.2f}  {r['dynamic_adjustment']:>+5.3f} "
                  f"{r['adjusted_priority']:>5.3f} "
                  f"{r['core_ratio']:>5.0%}  {r['avg_confidence']:>6.3f}  "
                  f"{r['contributions']:>5d}")


if __name__ == "__main__":
    main()
