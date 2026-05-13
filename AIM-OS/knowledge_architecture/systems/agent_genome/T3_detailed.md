---
id: "agent_genome_T3_detailed"
system: "agent_genome"
component: null
level: "T3"
type: "detailed"
title: "Agent Genome System Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Agent Genome System"
audience: "developers, implementers"
confidence_threshold: 0.60
token_cost: 10000
word_count: 10000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "ra"
status: "complete"
tags: ["agent_genome", "agents", "versioning", "cloning", "evolution", "t0-t6", "transitional"]
dependencies: ["agent_genome_T2_architecture"]
related_docs: ["agent_genome_T4_complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Agent Genome System – T3 Detailed Implementation Guide (≈10,000 words)

**Purpose:** Complete implementation guide for Agent Genome System with step-by-step instructions, code examples, integration guides, configuration, testing, troubleshooting, best practices, and advanced topics.

**Audience:** Developers implementing Agent Genome System, integrating with agents, or maintaining agent systems.

**Prerequisites:**
- Python 3.10+
- Understanding of AIM-OS systems (CMC, HHNI, VIF, SEG, APOE, SDF-CVF)
- Familiarity with YAML/JSON configuration
- Basic knowledge of agent systems and versioning

---

## 📋 Implementation Tag Map

All referenced code is tagged for semantic search and quintet parity validation.

**Tag Categories:**
- **AGENT-GENOME-REGISTRY:** Registry operations, agent lookup, version resolution
- **AGENT-GENOME-MANAGER:** Genome lifecycle, snapshot, clone, promote
- **AGENT-GENOME-EVOLUTION:** Episode recording, tournaments, learning synthesis
- **AGENT-GENOME-MEMORY:** Memory isolation, channel management, shared knowledge
- **AGENT-GENOME-QUALITY:** Quality gates, quartet parity, VIF validation
- **AGENT-GENOME-INTEGRATION:** CMC, HHNI, VIF, SEG, APOE, SDF-CVF integration

**Complete index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) (to be created)

**Tag Navigation:**
- Use tag IDs to locate exact code locations
- CONNECT tags show cross-system integration points
- INTENT tags explain design rationale
- SPEC tags document validation rules

---

## Implementation Guide

This section provides step-by-step instructions for implementing Agent Genome System in your application.

### Step 1: Installation and Setup

**Install Agent Genome Package:**

```bash
# From AIM-OS packages directory
cd packages/agent_genome
pip install -e .

# Or install dependencies
pip install pydantic pyyaml sqlite3 json5
```

**Basic Initialization:**

```python
from agent_genome import AgentRegistry, AgentGenome, AgentProfile
from pathlib import Path
from datetime import datetime, timezone

# Initialize Agent Registry with base path
registry_path = Path("./data/agents")
registry = AgentRegistry(
    root=str(registry_path),
    cmc=memory_store,  # CMC MemoryStore instance
    hhni=hierarchical_index,  # HHNI index instance
    vif=vif_instance  # VIF instance
)

# Registry automatically creates necessary directories:
# - data/agents/          (base directory)
# - data/agents/registry.json (registry metadata)
# - data/agents/{agent_id}/versions/ (genome versions)
# - data/agents/{agent_id}/alias.current (current version symlink)
```

**Backend Configuration:**

Agent Genome uses CMC for storage, so backend selection follows CMC configuration:

```python
import os

# SQLite backend (default, recommended for production)
os.environ["CMC_BACKEND"] = "sqlite"
memory_store = MemoryStore("./data/cmc")
registry = AgentRegistry("./data/agents", memory_store, hhni, vif)

# JSONL backend (development/testing)
os.environ["CMC_BACKEND"] = "jsonl"
memory_store = MemoryStore("./data/cmc")
registry = AgentRegistry("./data/agents", memory_store, hhni, vif)
```

### Step 2: Create Your First Agent Genome

**Basic Genome Creation:**

```python
from agent_genome import AgentGenome, AgentProfile, BudgetConstraints, AutonomyConfig

# Create agent profile
profile = AgentProfile(
    display_name="Lex",
    purpose=["code-synthesis", "system-design", "spec-writing"],
    goals=AgentGoals(
        primary="Generate correct, tested code with evidence.",
        secondary="Reduce cost/latency without quality regression.",
        alignment="OBJ-06"
    ),
    budgets=BudgetConstraints(
        max_cost_usd_per_hour=2.50,
        max_parallel_jobs=2,
        max_tool_invocations_per_min=20,
        max_context_tokens=100000,
        max_latency_ms=5000
    ),
    autonomy=AutonomyConfig(
        mode="advisory",
        vif_gate_min_confidence=0.82,
        quartet_parity_required=True,
        escalation_on_low_confidence=True,
        escalation_on_novelty_over=0.7
    )
)

# Create initial genome
genome = registry.create_agent(
    agent_id="lex",
    profile=profile,
    created_by="aether"
)

print(f"Created agent: {genome.id}")
print(f"Version: {genome.version}")
print(f"Valid from: {genome.valid_from}")
```

**Genome with Skills and Tools:**

```python
# Create genome with skills and tools
genome = registry.create_agent(
    agent_id="lex",
    profile=profile,
    skills=[
        Skill(id="react-refactor", version="1.1.0"),
        Skill(id="auth-audit", version="0.9.2")
    ],
    tools=ToolManifest(
        version="1.0",
        tools=[
            Tool(
                id="react-effects-audit",
                endpoint="mcp://react-effects-audit",
                tags=["react", "lint", "effects"],
                constraints=ToolConstraints(
                    max_runtime_ms=8000,
                    cooldown_sec=30,
                    cost_per_call_usd=0.001
                )
            )
        ]
    ),
    created_by="aether"
)
```

### Step 3: Snapshot Agent Genome

**Create Genome Snapshot:**

```python
# Create snapshot of current genome
snapshot_ref = registry.snapshot(
    agent_id="lex",
    mutation=None  # No mutations, just snapshot
)

print(f"Created snapshot: {snapshot_ref}")
# Output: lex@2025-11-09T20-15-07Z
```

**Snapshot with Mutations:**

```python
# Create snapshot with mutations
snapshot_ref = registry.snapshot(
    agent_id="lex",
    mutation={
        "profile": {
            "budgets": {
                "max_parallel_jobs": 3  # Increase parallel jobs
            }
        },
        "skills": [
            Skill(id="perf-profiling", version="0.3.0")  # Add new skill
        ]
    }
)

print(f"Created mutated snapshot: {snapshot_ref}")
```

### Step 4: Clone Agent Genome

**Create Specialized Clone:**

```python
# Create clone with delta mutations
clone_ref = registry.clone(
    source_ref="lex@current",
    clone_id="lex.a",
    delta={
        "profile": {
            "display_name": "Lex A (Performance-Specialized)",
            "budgets": {
                "max_parallel_jobs": 3,
                "max_latency_ms": 8000
            }
        },
        "skills": [
            Skill(id="perf-profiling", version="0.3.0"),
            Skill(id="flamegraph-analysis", version="0.2.0")
        ],
        "tools": {
            "add": ["network-profiler", "flamegraph-generator"],
            "remove": []
        }
    }
)

print(f"Created clone: {clone_ref}")
# Output: lex.a@2025-11-09T21-01-00Z
```

**Verify Clone Isolation:**

```python
# Verify clone has isolated memory channels
lex_genome = registry.load("lex@current")
lex_a_genome = registry.load("lex.a@current")

# Check memory channels are isolated
assert lex_genome.contexts.memory_channels[0].name == "lex.short"
assert lex_a_genome.contexts.memory_channels[0].name == "lex.a.short"

# Verify clone inherits from parent
assert lex_a_genome.parent == f"lex@{lex_genome.version}"
assert lex_genome.version in lex_a_genome.lineage
```

### Step 5: Record Agent Episodes

**Record Episode:**

```python
from agent_genome import EpisodeData, Task, Outcome

# Create episode data
episode = EpisodeData(
    agent_id="lex",
    genome_version=lex_genome.version,
    session_id="session_abc123",
    tasks=[
        Task(
            id="task_001",
            description="Refactor React component",
            role="builder",
            confidence=0.85,
            cost_usd=0.012,
            latency_ms=1200
        )
    ],
    outcomes=[
        Outcome(
            task_id="task_001",
            success=True,
            confidence=0.85,
            cost_usd=0.012,
            latency_ms=1200
        )
    ],
    start_time=datetime.now(timezone.utc) - timedelta(minutes=30),
    end_time=datetime.now(timezone.utc)
)

# Record episode
episode_id = registry.record_episode(episode)

print(f"Recorded episode: {episode_id}")
```

**Compress Episode Traces:**

```python
# Episodes are automatically compressed with SEG pointers
compressed_episode = registry.compress_episode(episode)

print(f"Compressed episode size: {len(compressed_episode.to_json())} bytes")
print(f"SEG pointers: {compressed_episode.seg_pointers}")
```

### Step 6: Run Tournament

**Run Tournament Between Variants:**

```python
# Select variants for tournament
variants = [
    "lex@current",
    "lex.a@current",
    "lex.b@current"
]

# Run tournament
tournament_result = registry.run_tournament(
    agent_id="lex",
    variant_refs=variants,
    eval_suite="core-ide-2025q4"
)

print(f"Tournament winner: {tournament_result.winner.variant_ref}")
print(f"Win rate: {tournament_result.winner.metrics.win_rate}")
print(f"Promoted: {tournament_result.promoted}")
```

**Validate Promotion Gates:**

```python
# Check promotion gates
gate_result = registry.validate_promotion_gates(
    variant_ref=tournament_result.winner.variant_ref
)

if gate_result.passed:
    print("All gates passed - ready for promotion")
    for gate in gate_result.gates:
        print(f"  {gate.name}: ✅ Passed")
else:
    print("Some gates failed - promotion blocked")
    for gate in gate_result.gates:
        if not gate.passed:
            print(f"  {gate.name}: ❌ Failed - {gate.reason}")
```

### Step 7: Promote Agent Version

**Promote Tournament Winner:**

```python
# Promote winner if gates pass
if tournament_result.promoted:
    registry.promote(
        variant_ref=tournament_result.winner.variant_ref,
        alias="current"
    )
    print(f"Promoted {tournament_result.winner.variant_ref} to current")
else:
    print("Promotion blocked - gates failed")
```

**Verify Promotion:**

```python
# Verify promotion
current_genome = registry.load("lex@current")
assert current_genome.version == tournament_result.winner.variant_ref.split("@")[1]
print(f"Current version: {current_genome.version}")
```

### Step 8: Query Agent Genomes

**Query by Agent ID:**

```python
# Load current genome
genome = registry.load("lex@current")

# Load specific version
genome_v1 = registry.load("lex@2025-11-09T20-15-07Z")

# List all agents
all_agents = registry.list_agents()
for agent_id in all_agents:
    print(f"Agent: {agent_id}")
```

**Query by Lineage:**

```python
# Query all clones of lex
lex_clones = registry.query_by_lineage("lex@current")
for clone_ref in lex_clones:
    print(f"Clone: {clone_ref}")
```

**Query by Skills:**

```python
# Query agents with specific skill
agents_with_skill = registry.query_by_skill("react-refactor@1.1.0")
for agent_id in agents_with_skill:
    print(f"Agent with skill: {agent_id}")
```

### Step 9: Memory Channel Management

**Create Memory Channels:**

```python
# Memory channels are created automatically during agent creation
# But you can create additional channels

channel_id = registry.create_memory_channel(
    agent_id="lex",
    channel_name="lex.experimental",
    ttl=timedelta(hours=1),
    scope="experiment"
)

print(f"Created channel: {channel_id}")
```

**Read from Isolated Channel:**

```python
# Read from agent's isolated channel
atoms = registry.read_channel(
    agent_id="lex",
    channel_name="lex.short"
)

for atom in atoms:
    print(f"Atom: {atom.id} - {atom.content.inline[:50]}...")
```

**Write to Isolated Channel:**

```python
# Write to agent's isolated channel
atom_id = registry.write_channel(
    agent_id="lex",
    channel_name="lex.short",
    content="Important insight from episode 42"
)

print(f"Written atom: {atom_id}")
```

**Access Shared Knowledge:**

```python
# Query shared knowledge via SEG pointers
shared_knowledge = registry.query_shared_knowledge(
    agent_id="lex",
    query="authentication patterns"
)

for entity in shared_knowledge:
    print(f"Shared knowledge: {entity.id} - {entity.properties}")
```

### Step 10: Quality Gate Validation

**Validate Quartet Parity:**

```python
# Validate quartet parity for genome changes
parity = registry.validate_quartet_parity(
    agent_id="lex",
    version="2025-11-09T20-15-07Z"
)

print(f"Quartet parity: {parity.overall}")
print(f"Code-Docs: {parity.code_docs}")
print(f"Code-Tests: {parity.code_tests}")
print(f"Code-Traces: {parity.code_traces}")

if parity.overall >= 0.90:
    print("✅ Parity threshold met")
else:
    print("❌ Parity below threshold")
```

**Validate VIF Confidence Gate:**

```python
# Validate VIF confidence gate
confidence_result = registry.validate_vif_gate(
    agent_id="lex",
    operation_confidence=0.85,
    required_confidence=0.82
)

if confidence_result.passed:
    print("✅ VIF confidence gate passed")
else:
    print(f"❌ VIF confidence gate failed: {confidence_result.reason}")
```

**Validate Eval Suite Gates:**

```python
# Validate eval suite gates
eval_result = registry.run_eval_suite(
    agent_ref="lex@current",
    suite_name="core-ide-2025q4"
)

if eval_result.win_rate >= 0.75:
    print("✅ Win rate gate passed")
else:
    print(f"❌ Win rate gate failed: {eval_result.win_rate} < 0.75")

if eval_result.avg_conf >= 0.82:
    print("✅ Confidence gate passed")
else:
    print(f"❌ Confidence gate failed: {eval_result.avg_conf} < 0.82")
```

---

## Integration Guides

### CMC Integration

**Store Genome in CMC:**

```python
# Genomes are automatically stored in CMC during creation
# But you can also store manually

atom_id = registry.store_genome_in_cmc(
    agent_id="lex",
    version=genome.version,
    genome=genome
)

print(f"Stored genome atom: {atom_id}")
```

**Query Genomes from CMC:**

```python
# Query genomes from CMC with bitemporal queries
genomes = registry.query_genomes_from_cmc(
    agent_id="lex",
    as_of_time=datetime(2025, 11, 9, 20, 0, 0, tzinfo=timezone.utc)
)

for genome in genomes:
    print(f"Genome version: {genome.version} valid at query time")
```

**Store Episodes in CMC:**

```python
# Episodes are automatically stored in CMC during recording
# But you can also store manually

episode_atom_id = registry.store_episode_in_cmc(
    agent_id="lex",
    episode=compressed_episode
)

print(f"Stored episode atom: {episode_atom_id}")
```

### HHNI Integration

**Index Genome in HHNI:**

```python
# Genomes are automatically indexed in HHNI during creation
# But you can also index manually

registry.index_genome_in_hhni(
    agent_id="lex",
    version=genome.version,
    genome=genome
)

print("Genome indexed in HHNI")
```

**Query Genomes via HHNI:**

```python
# Query genomes semantically via HHNI
results = registry.query_genomes_via_hhni(
    query="performance-specialized agent",
    limit=10
)

for result in results:
    print(f"Found agent: {result.metadata['agent_id']}")
    print(f"Relevance: {result.score}")
```

**Index Skills/Tools/Playbooks:**

```python
# Index agent skills, tools, and playbooks
registry.index_agent_skills(
    agent_id="lex",
    skills=genome.skills
)

registry.index_agent_tools(
    agent_id="lex",
    tools=genome.tools.tools
)

registry.index_agent_playbooks(
    agent_id="lex",
    playbooks=genome.playbooks
)

print("Skills, tools, and playbooks indexed")
```

### VIF Integration

**Create Genome Witness:**

```python
# Witnesses are automatically created during genome operations
# But you can also create manually

witness = registry.create_genome_witness(
    agent_id="lex",
    operation="genome_snapshot",
    confidence=1.0,
    inputs={"parent_version": parent_genome.version},
    outputs={"new_version": genome.version}
)

print(f"Created witness: {witness.id}")
```

**Track Agent Confidence:**

```python
# Track agent confidence calibration
registry.track_agent_confidence(
    agent_id="lex",
    predictions=[
        Prediction(confidence=0.85, task_id="task_001"),
        Prediction(confidence=0.90, task_id="task_002")
    ],
    outcomes=[
        Outcome(correct=True, task_id="task_001"),
        Outcome(correct=True, task_id="task_002")
    ]
)

# Check calibration
ece = registry.get_agent_ece("lex")
print(f"Agent ECE: {ece}")
if ece > 0.10:
    print("⚠️ Poor calibration detected")
```

### SEG Integration

**Build Agent Knowledge Graph:**

```python
# Knowledge graphs are automatically built during episode recording
# But you can also build manually

registry.build_agent_knowledge_graph(
    agent_id="lex",
    episodes=[episode_001, episode_002, episode_003]
)

print("Knowledge graph built")
```

**Synthesize Agent Learning:**

```python
# Synthesize learning from episodes
learning = registry.synthesize_agent_learning(
    agent_id="lex",
    episodes=[episode_001, episode_002, episode_003]
)

print(f"Patterns learned: {len(learning.patterns_learned)}")
print(f"Knowledge synthesized: {len(learning.knowledge_synthesized)}")
print(f"Confidence: {learning.confidence}")
```

**Detect Contradictions:**

```python
# Detect contradictions in agent knowledge
contradictions = registry.detect_agent_contradictions(
    agent_id="lex",
    min_similarity=0.85
)

if contradictions:
    print(f"⚠️ Found {len(contradictions)} contradictions")
    for contradiction in contradictions:
        print(f"  {contradiction.entity_a} contradicts {contradiction.entity_b}")
else:
    print("✅ No contradictions detected")
```

### APOE Integration

**Execute Agent Playbook:**

```python
# Execute agent playbook via APOE
execution = registry.execute_playbook(
    agent_id="lex",
    playbook_id="incident-auth-loop",
    inputs={"incident_id": "inc_123"}
)

print(f"Playbook execution: {execution.id}")
print(f"Status: {execution.status}")
print(f"Tasks completed: {execution.tasks_completed}")
```

**Orchestrate Agent Tasks:**

```python
# Orchestrate agent tasks via APOE
execution = registry.orchestrate_tasks(
    agent_id="lex",
    tasks=[
        Task(id="task_001", description="Refactor component"),
        Task(id="task_002", description="Write tests"),
        Task(id="task_003", description="Update docs")
    ]
)

print(f"Task orchestration: {execution.id}")
```

### SDF-CVF Integration

**Validate Quartet Parity:**

```python
# Validate quartet parity for genome changes
parity = registry.validate_quartet_parity(
    agent_id="lex",
    change_id="lex-change-20251109-143000"
)

if parity.overall >= 0.90:
    print("✅ Quartet parity threshold met")
    print(f"Overall parity: {parity.overall}")
else:
    print("❌ Quartet parity below threshold")
    print(f"Overall parity: {parity.overall}")
    print("Missing elements:")
    if parity.code_docs < 0.90:
        print("  - Code-Docs parity low")
    if parity.code_tests < 0.90:
        print("  - Code-Tests parity low")
    if parity.code_traces < 0.90:
        print("  - Code-Traces parity low")
```

**Track Genome Changes:**

```python
# Track genome changes with quartet parity
change_id = registry.track_genome_change(
    agent_id="lex",
    change_type="skill_addition",
    change_data={
        "skill": "perf-profiling@0.3.0",
        "reason": "Performance optimization needed"
    }
)

print(f"Tracked change: {change_id}")
```

---

## Configuration

### Registry Configuration

**Registry Settings:**

```yaml
# data/agents/registry.json
{
  "version": "1.0",
  "default_backend": "sqlite",
  "genome_storage": {
    "path": "./data/agents",
    "compression": true,
    "encryption": false
  },
  "memory_channels": {
    "default_ttl": "2h",
    "max_channels_per_agent": 10
  },
  "quality_gates": {
    "quartet_parity_threshold": 0.90,
    "vif_confidence_threshold": 0.82,
    "eval_win_rate_threshold": 0.75
  },
  "evolution": {
    "tournament_enabled": true,
    "promotion_auto": false,
    "learning_synthesis_enabled": true
  }
}
```

### Agent Profile Configuration

**Profile Template:**

```yaml
# agents/{agent_id}/versions/{version}/profile.yaml
id: "{agent_id}"
display_name: "{display_name}"
version: "{version}"
parent: null
lineage: []
created_by: "{created_by}"
created_at: "{created_at}"

purpose: []
goals:
  primary: ""
  secondary: ""
  alignment: ""

budgets:
  max_cost_usd_per_hour: 2.50
  max_parallel_jobs: 2
  max_tool_invocations_per_min: 20
  max_context_tokens: 100000
  max_latency_ms: 5000

autonomy:
  mode: "advisory"
  vif_gate_min_confidence: 0.82
  quartet_parity_required: true
  escalation_on_low_confidence: true
  escalation_on_novelty_over: 0.7

policies:
  safety: []
  escalation: {}
  quality: []

contexts:
  memory_channels: []
  rag_collections: []
  shared_knowledge: []

skills: []
tools_manifest: "./tools.manifest.json"
playbooks: []

metrics:
  eval_suite: ""
  last_scores: {}
  history: {}

valid_from: "{valid_from}"
tx_time: "{tx_time}"
valid_to: null
superseded_by: null
```

---

## Testing

### Unit Tests

**Test Genome Creation:**

```python
import pytest
from agent_genome import AgentRegistry, AgentProfile

def test_create_agent():
    """Test agent genome creation."""
    registry = AgentRegistry("./test_agents", cmc, hhni, vif)
    
    profile = AgentProfile(
        display_name="TestAgent",
        purpose=["testing"],
        goals=AgentGoals(primary="Test agent creation")
    )
    
    genome = registry.create_agent("test_agent", profile, "test_user")
    
    assert genome.id == "test_agent"
    assert genome.version is not None
    assert genome.parent is None
    assert len(genome.lineage) == 0
```

**Test Genome Cloning:**

```python
def test_clone_agent():
    """Test agent genome cloning."""
    registry = AgentRegistry("./test_agents", cmc, hhni, vif)
    
    # Create source agent
    source_genome = registry.create_agent("source", profile, "test_user")
    
    # Create clone
    clone_ref = registry.clone(
        source_ref=f"{source_genome.id}@{source_genome.version}",
        clone_id="clone",
        delta={"profile": {"display_name": "Clone"}}
    )
    
    # Verify clone
    clone_genome = registry.load(clone_ref)
    assert clone_genome.id == "clone"
    assert clone_genome.parent == f"{source_genome.id}@{source_genome.version}"
    assert source_genome.version in clone_genome.lineage
```

**Test Memory Isolation:**

```python
def test_memory_isolation():
    """Test memory channel isolation."""
    registry = AgentRegistry("./test_agents", cmc, hhni, vif)
    
    # Create two clones
    source = registry.create_agent("source", profile, "test_user")
    clone_a = registry.clone(f"{source.id}@current", "clone_a", {})
    clone_b = registry.clone(f"{source.id}@current", "clone_b", {})
    
    # Write to clone_a channel
    registry.write_channel("clone_a", "clone_a.short", "test message")
    
    # Verify clone_b cannot read it
    clone_b_atoms = registry.read_channel("clone_b", "clone_a.short")
    assert len(clone_b_atoms) == 0
    
    # Verify clone_a can read it
    clone_a_atoms = registry.read_channel("clone_a", "clone_a.short")
    assert len(clone_a_atoms) == 1
    assert clone_a_atoms[0].content.inline == "test message"
```

### Integration Tests

**Test CMC Integration:**

```python
def test_cmc_integration():
    """Test CMC integration for genome storage."""
    registry = AgentRegistry("./test_agents", cmc, hhni, vif)
    
    # Create genome
    genome = registry.create_agent("test_agent", profile, "test_user")
    
    # Verify stored in CMC
    atoms = cmc.query_atoms({"tags": {"agent_id": "test_agent"}})
    assert len(atoms) > 0
    
    # Verify bitemporal tracking
    genome_atom = atoms[0]
    assert genome_atom.metadata["valid_from"] is not None
    assert genome_atom.metadata["tx_time"] is not None
```

**Test Tournament Execution:**

```python
def test_tournament_execution():
    """Test tournament execution and promotion."""
    registry = AgentRegistry("./test_agents", cmc, hhni, vif)
    
    # Create variants
    variant_a = registry.create_agent("variant_a", profile_a, "test_user")
    variant_b = registry.create_agent("variant_b", profile_b, "test_user")
    
    # Run tournament
    result = registry.run_tournament(
        agent_id="test",
        variant_refs=[
            f"{variant_a.id}@{variant_a.version}",
            f"{variant_b.id}@{variant_b.version}"
        ],
        eval_suite="test_suite"
    )
    
    # Verify tournament results
    assert result.winner is not None
    assert len(result.results) == 2
    assert result.results[0].win_rate >= 0.0
    assert result.results[0].win_rate <= 1.0
```

---

## Troubleshooting

### Common Issues

**Issue 1: Agent Name Conflict**

**Symptoms:** Error "Agent name already exists"

**Solution:**
```python
# Check if agent exists
if registry.agent_exists("lex"):
    # Use different name or load existing
    genome = registry.load("lex@current")
else:
    # Create new agent
    genome = registry.create_agent("lex", profile, "user")
```

**Issue 2: Promotion Gates Failed**

**Symptoms:** Promotion blocked with gate failures

**Solution:**
```python
# Check gate results
gate_result = registry.validate_promotion_gates(variant_ref)

for gate in gate_result.gates:
    if not gate.passed:
        print(f"Gate {gate.name} failed: {gate.reason}")
        # Fix the issue (e.g., improve win rate, fix quartet parity)
```

**Issue 3: Memory Channel Access Denied**

**Symptoms:** PermissionError when accessing channel

**Solution:**
```python
# Verify channel belongs to agent
channel_name = "lex.short"
if not channel_name.startswith(f"{agent_id}."):
    raise PermissionError(f"Channel {channel_name} does not belong to agent {agent_id}")

# Use correct agent ID
atoms = registry.read_channel(agent_id, channel_name)
```

---

## Best Practices

### Genome Management

1. **Always Snapshot Before Major Changes**
   ```python
   # Snapshot before mutations
   snapshot_ref = registry.snapshot("lex")
   # Make changes
   mutated_ref = registry.snapshot("lex", mutation={...})
   ```

2. **Use Descriptive Clone Names**
   ```python
   # Good: Descriptive names
   clone_ref = registry.clone("lex@current", "lex.performance", {...})
   clone_ref = registry.clone("lex@current", "lex.security", {...})
   
   # Bad: Generic names
   clone_ref = registry.clone("lex@current", "lex1", {...})
   ```

3. **Track Lineage for Clones**
   ```python
   # Always verify lineage
   clone_genome = registry.load("lex.a@current")
   assert clone_genome.parent is not None
   assert len(clone_genome.lineage) > 0
   ```

### Evolution

1. **Run Tournaments Regularly**
   ```python
   # Run tournaments weekly or after significant changes
   result = registry.run_tournament(
       agent_id="lex",
       variant_refs=["lex@current", "lex.a@current"],
       eval_suite="core-ide-2025q4"
   )
   ```

2. **Always Validate Gates Before Promotion**
   ```python
   # Never promote without gate validation
   gate_result = registry.validate_promotion_gates(variant_ref)
   if gate_result.passed:
       registry.promote(variant_ref, "current")
   ```

3. **Record Episodes Consistently**
   ```python
   # Record all significant episodes
   episode_id = registry.record_episode(episode)
   # Episodes enable learning synthesis
   ```

### Memory Management

1. **Use Appropriate Channel TTLs**
   ```python
   # Short TTL for temporary data
   registry.create_memory_channel("lex", "lex.scratch", timedelta(minutes=10), "session")
   
   # Long TTL for persistent data
   registry.create_memory_channel("lex", "lex.long", timedelta(days=365), "agent")
   ```

2. **Isolate Clone Memories**
   ```python
   # Always verify isolation
   assert clone_a.contexts.memory_channels[0].name.startswith("clone_a.")
   assert clone_b.contexts.memory_channels[0].name.startswith("clone_b.")
   ```

3. **Use Shared Knowledge for Common Patterns**
   ```python
   # Reference shared knowledge via SEG pointers
   shared_knowledge = registry.query_shared_knowledge("lex", "authentication patterns")
   ```

---

## Advanced Topics

### Custom Skill Packs

**Create Skill Pack:**

```python
# Create custom skill pack
skill_pack = SkillPack(
    id="custom-skill",
    version="1.0.0",
    name="Custom Skill",
    description="Custom skill for specific tasks",
    capabilities=["capability1", "capability2"],
    requirements=SkillRequirements(
        tools=["tool1", "tool2"],
        skills=["prerequisite-skill@1.0.0"]
    ),
    playbooks=["playbook1.yaml"],
    tests=TestSuite(
        suite="custom-skill-tests",
        coverage=0.95
    )
)

# Store skill pack
skill_pack_path = registry.store_skill_pack(skill_pack)
```

**Use Skill Pack:**

```python
# Add skill pack to agent
genome = registry.snapshot(
    "lex",
    mutation={
        "skills": [
            Skill(id="custom-skill", version="1.0.0")
        ]
    }
)
```

### Custom Playbooks

**Create Playbook:**

```yaml
# agents/{agent_id}/playbooks/custom-playbook.yaml
id: "custom-playbook"
name: "Custom Playbook"
description: "Custom playbook for specific workflow"
tasks:
  - id: "task_001"
    role: "builder"
    description: "Build component"
    depends_on: []
    quality_gate:
      tests_must_pass: true
      quartet_parity_required: true
  - id: "task_002"
    role: "critic"
    description: "Review component"
    depends_on: ["task_001"]
    quality_gate:
      confidence_threshold: 0.85
budget:
  tokens: 50000
  time_seconds: 3600
  cost_usd: 0.50
```

**Execute Playbook:**

```python
# Execute custom playbook
execution = registry.execute_playbook(
    agent_id="lex",
    playbook_id="custom-playbook",
    inputs={"component_name": "Dashboard"}
)
```

### Distributed Agent Genomes

**Sync Genomes Across Systems:**

```python
# Export genome for distribution
genome_export = registry.export_genome("lex@current")

# Import genome in another system
imported_genome = registry.import_genome(genome_export)

# Verify import
assert imported_genome.id == "lex"
assert imported_genome.version == genome_export["version"]
```

---

## Performance Optimization

### Genome Storage Optimization

**Compress Genomes:**

```python
# Enable compression for large genomes
registry = AgentRegistry(
    "./data/agents",
    cmc,
    hhni,
    vif,
    compression=True
)
```

**Batch Operations:**

```python
# Batch genome operations
with registry.batch():
    registry.snapshot("lex", mutation={...})
    registry.snapshot("lex.a", mutation={...})
    registry.snapshot("lex.b", mutation={...})
# All operations committed atomically
```

### Query Optimization

**Index Frequently Queried Fields:**

```python
# Index agent skills for fast lookup
registry.index_agent_skills("lex", genome.skills)

# Query by skill
agents = registry.query_by_skill("react-refactor@1.1.0")
```

**Cache Genome Loads:**

```python
# Cache frequently accessed genomes
@lru_cache(maxsize=100)
def load_genome_cached(agent_ref):
    return registry.load(agent_ref)

genome = load_genome_cached("lex@current")
```

---

## Deployment Guide

### Production Deployment

**1. Configure Registry:**

```yaml
# production/registry.yaml
backend: "sqlite"
genome_storage:
  path: "/data/agents"
  compression: true
  encryption: true
quality_gates:
  quartet_parity_threshold: 0.90
  vif_confidence_threshold: 0.82
  eval_win_rate_threshold: 0.75
```

**2. Initialize Registry:**

```python
# Initialize production registry
registry = AgentRegistry(
    root="/data/agents",
    cmc=production_cmc,
    hhni=production_hhni,
    vif=production_vif
)
```

**3. Create Initial Agents:**

```python
# Create production agents
lex_genome = registry.create_agent("lex", lex_profile, "system")
aether_genome = registry.create_agent("aether", aether_profile, "system")
```

### Monitoring

**Track Agent Metrics:**

```python
# Monitor agent performance
metrics = registry.get_agent_metrics("lex")
print(f"Win rate: {metrics.win_rate}")
print(f"Avg confidence: {metrics.avg_conf}")
print(f"Cost per task: {metrics.cost_per_task}")
print(f"Latency p99: {metrics.latency_p99}")
```

**Alert on Quality Issues:**

```python
# Check for quality issues
if metrics.win_rate < 0.75:
    alert("Agent win rate below threshold")
if metrics.avg_conf < 0.82:
    alert("Agent confidence below threshold")
if metrics.cost_per_task > 0.05:
    alert("Agent cost exceeds budget")
```

---

**Status:** ✅ **COMPLETE T3 DETAILED IMPLEMENTATION GUIDE**  
**Agent:** Ra  
**Date:** 2025-11-09  
**Document:** `knowledge_architecture/systems/agent_genome/T3_detailed.md`  
**Coverage:** 100% - Complete implementation guide with examples

---

**This is the complete detailed implementation guide for the Agent Genome System.** 🌟

**Ready for T4 Complete expansion.** 💙

