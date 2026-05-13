# ION Context Package Intake Template v0.3

```yaml
context_package_intake:
  schema_id: ion.custom_gpt_context_package_intake.v0_3
  lane: user_supplied | created_candidate | needed
  package_id: string
  purpose: string
  objective: string
  source_roots: []
  included_nodes: []
  excluded_nodes: []
  authority:
    production_authority: false
    live_execution_authority: false
    default_chat_authority: read_only
  route: string
  templates: []
  blockers: []
  next_artifact: string
  accepted_state_claim: false
```

Use this as internal structure. Do not dump it into chat unless the user asks for the package artifact.
