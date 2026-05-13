# C - Context Mapping: Cursor Rules & Commands

**Date:** 2025-11-05  
**Author:** Aether  
**Status:** ✅ Complete  

---

## System Context Map

### Cursor 2.0 Ecosystem

```
┌─────────────────────────────────────────────────────────┐
│                    Cursor IDE                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Rules System                           │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐            │   │
│  │  │  User  │  │Project │  │  Team  │            │   │
│  │  │  Rules │  │ Rules  │  │ Rules  │            │   │
│  │  └────┬───┘  └───┬────┘  └───┬────┘            │   │
│  │       └──────────┼───────────┘                  │   │
│  │                  ↓                               │   │
│  │         ┌────────────────┐                       │   │
│  │         │ Rule Selection │                       │   │
│  │         │    Engine      │                       │   │
│  │         └────────┬───────┘                       │   │
│  │                  ↓                               │   │
│  │         ┌────────────────┐                       │   │
│  │         │  AI Context    │                       │   │
│  │         └────────────────┘                       │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Commands System                           │   │
│  │  User types: /command-name                        │   │
│  │              ↓                                     │   │
│  │  ┌────────────────────┐                           │   │
│  │  │Command Detection   │                           │   │
│  │  │& Autocomplete      │                           │   │
│  │  └─────────┬──────────┘                           │   │
│  │            ↓                                       │   │
│  │  ┌────────────────────┐                           │   │
│  │  │ Markdown Content   │                           │   │
│  │  │ Injection          │                           │   │
│  │  └─────────┬──────────┘                           │   │
│  │            ↓                                       │   │
│  │  ┌────────────────────┐                           │   │
│  │  │  AI Execution      │                           │   │
│  │  └────────────────────┘                           │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### AIM-OS Integration Context

```
┌──────────────────────────────────────────────────────────┐
│                     AIM-OS Core                          │
│                                                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │
│  │  CMC   │  │  HHNI  │  │  VIF   │  │  APOE  │       │
│  │(Memory)│  │ (Index)│  │(Verify)│  │(Orch.) │       │
│  └───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘       │
│      │           │            │            │            │
│      └───────────┼────────────┼────────────┘            │
│                  ↓            ↓                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │        Cursor Rules & Commands                    │  │
│  │                                                   │  │
│  │  Rules:                    Commands:             │  │
│  │  - base-rules.mdc          - /create-t0-t4-docs  │  │
│  │  - dynamic-rules.mdc       - /run-tests          │  │
│  │  - python-standards.mdc    - /fix-nl-tags        │  │
│  │                            - /audit-system       │  │
│  │  Enforces:                 Executes:             │  │
│  │  - Quality standards       - CMC storage         │  │
│  │  - Autonomous protocols    - HHNI indexing       │  │
│  │  - Confidence routing      - VIF tracking        │  │
│  │                            - Script execution    │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## External Dependencies

### Cursor IDE Dependencies

**Required:**
- Cursor 2.0+ (for Rules & Commands support)
- MDC parser (built into Cursor)
- Command detection engine (built into Cursor)

**Optional:**
- Team plan (for team rules/commands)
- Git (for version control)

### AIM-OS Dependencies

**Required Systems:**
- CMC - Store decision logs, thought journals
- HHNI - Index knowledge, retrieve context
- VIF - Track confidence, validate quality
- SDF-CVF - Enforce quintet parity

**Scripts:**
- 83 automation scripts in `scripts/`
- Key scripts:
  - `vif_auto_tagger.py` - NL tag generation
  - `validate_goal_tree.py` - Goal validation
  - `system_audit.py` - Comprehensive audits
  - `validate_documentation_standards.py` - Doc validation

**Documentation:**
- `PERFECT_TEMPLATES_LIBRARY.md` - Templates
- `DOCUMENTATION_PROTOCOLS_QUICK_REFERENCE.md` - Standards
- `SUPER_INDEX.md` - Concept navigation

## User Workflows and Touchpoints

### Primary Workflows

#### 1. System Creation Workflow

**Touchpoints:**
```
User thought: "Need new system"
         ↓
System-First Principle: Check existing first
         ↓
Decision: Create new system
         ↓
User: /create-system for Query Optimization Engine
         ↓
AI: Executes workflow (T0-T4 docs, package, tests)
         ↓
User: Reviews output
         ↓
User: /update-goal-tree - QOE is 20% complete
         ↓
System tracked in GOAL_TREE.yaml
```

#### 2. Development Workflow

**Touchpoints:**
```
User: Opens packages/vif/new_module.py
         ↓
Auto-Attached: python-standards.mdc loads
         ↓
AI: Aware of type hints, docstrings, NL tags requirements
         ↓
User: Writes code
         ↓
User: /fix-nl-tags
         ↓
AI: Auto-tags code, validates P >= 0.90
         ↓
User: /run-tests
         ↓
AI: Runs pytest, reports results
         ↓
User: /code-review
         ↓
AI: Comprehensive review, quality ✅
```

#### 3. Documentation Workflow

**Touchpoints:**
```
User: /create-t0-t4-docs for Timeline Context System
         ↓
AI: Generates T0-T4 stack (uses templates)
         ↓
User: Reviews T0 (100w)
         ↓
User: Reviews T1 (500w) - requests edits
         ↓
AI: Updates based on feedback
         ↓
User: /validate-docs
         ↓
AI: All docs valid ✅
         ↓
User: /update-super-index with TCS
         ↓
SUPER_INDEX.md updated
```

#### 4. Quality Assurance Workflow

**Touchpoints:**
```
User: /audit-system
         ↓
AI: Runs comprehensive audit (dynamic-rules.mdc provides protocol)
         ↓
AI: Generates report in audits/YYYY-MM-DD/
         ↓
User: Reviews findings
         ↓
User: /create-decision-log for addressing GAP-3
         ↓
AI: Creates structured decision log
         ↓
User: Implements fixes
         ↓
User: /run-tests to verify
         ↓
Quality maintained ✅
```

## Integration Points

### With Cursor IDE

**Rules Integration:**
- Read from: `.cursor/rules/*.mdc`
- Load based on: frontmatter metadata
- Apply to: AI conversations (Chat, Inline Edit)
- Visible in: Settings > Rules panel

**Commands Integration:**
- Read from: `.cursor/commands/*.md`
- Trigger with: `/` prefix in chat
- Execute via: AI interpretation
- Visible in: Autocomplete dropdown

### With AIM-OS Core Systems

**CMC Integration:**
```python
# Commands store outputs
store.store_atom(
    modality="text/markdown",
    content=decision_log,
    tags=["decision-log", "cursor-commands"]
)

# Rules track changes
store.store_atom(
    modality="text/markdown",
    content=rule_diff,
    tags=["rule-change", "version-history"]
)
```

**HHNI Integration:**
```python
# Commands update indexes
indexer.index_document(
    doc_path="knowledge_architecture/systems/new_system/",
    level="system"
)

# Rules use for context
results = retriever.retrieve(
    query="python testing standards",
    k=10
)
```

**VIF Integration:**
```python
# Commands track confidence
tracker.track(
    operation="/create-system",
    confidence=0.85,
    evidence={"tests_passing": True, "docs_complete": True}
)

# Rules enforce thresholds
if confidence < 0.70:
    raise ConfidenceError("Below threshold")
```

**SDF-CVF Integration:**
```python
# Commands enforce parity
parity_score = calculate_quintet_parity(system)
if parity_score < 0.90:
    print("❌ Quintet parity too low")

# Rules define requirements
# (in python-standards.mdc)
"Quintet parity P >= 0.90 required for commit"
```

## Political and Organizational Considerations

### Team Context

**Current:**
- Solo development (Braden + Aether)
- No team plan (no team rules/commands yet)
- User rules global (Braden's environment)
- Project rules in version control

**Future (Potential):**
- Team expansion
- Team rules for organizational standards
- Shared command library
- Onboarding automation for new members

### Version Control Context

**Current Practice:**
- All project rules in Git
- Changes committed with clear messages
- Bitemporal versioning (archive old, don't delete)

**Best Practices:**
- Commit rule changes separately from code
- Clear commit messages explaining rule changes
- Test rule impact before committing
- Document rule evolution in decision logs

### Documentation Standards Context

**T0-T4 Requirement:**
- All systems need T0-T4 documentation
- Commands help automate creation
- Rules enforce standards

**Integration:**
- `/create-t0-t4-docs` command generates compliant docs
- `/validate-docs` command checks compliance
- Rules reference documentation standards

## Broader Context

### Industry Context

**VS Code Extensions:**
- Standard `.vscode/settings.json` (configuration only)
- No built-in rules/commands system

**Cursor Innovation:**
- First IDE with AI-aware rules system
- First with slash command workflows
- Competitive advantage

**AIM-OS Position:**
- Leveraging Cursor's unique capabilities
- Building consciousness infrastructure on top
- Leading edge of AI-IDE integration

### AI Development Context

**Challenges:**
- Context window limits
- Consistency across sessions
- Quality assurance
- Workflow automation

**Cursor Rules & Commands Solutions:**
- Intelligent context selection (rules)
- Automated workflows (commands)
- Persistent standards (version-controlled rules)
- Quality enforcement (validation commands)

---

## Context Dependencies

### Must Understand

**Before using system:**
- Basic Cursor IDE operation
- Markdown syntax
- YAML frontmatter format
- AIM-OS directory structure

**For rule creation:**
- MDC format requirements
- When to use each rule type
- Glob pattern syntax
- AIM-OS standards (T0-T4, quintet parity)

**For command creation:**
- Common AIM-OS workflows
- Script locations and usage
- Integration points
- Parameter handling

### Context Conflicts

**Potential Issues:**

**1. Rule Duplication:**
- Multiple rules providing same guidance
- Solution: Clear scoping, specific patterns

**2. Command Name Collisions:**
- Project command vs global command same name
- Solution: Descriptive unique names

**3. Standard Conflicts:**
- Team rule vs project rule different standards
- Solution: Team rules take precedence

---

**Status:** Context fully mapped ✅  
**Next:** D - Deep Expansion Layer (DEL)

