# Ranked Sign-Off Template

```yaml
schema_id: ion.rank_authority.signoff.v0_1
candidate_true_name: "<worker true name>"
candidate_rank: "R0_WITNESS | R1_LOCAL_WORKER | R2_DOMAIN_WORKER | R3_BRANCH_INTEGRATOR | R4_SETTLEMENT_STEWARD | R5_ROOT_GOVERNOR | R6_HUMAN_AUTHORITY"
signer_true_name: "<signer true name>"
signer_rank: "R4_SETTLEMENT_STEWARD"
output_class: "branch_reconciliation_promotion"
proof:
  candidate_output_ref: "<path or receipt>"
  evidence_refs:
    - "<path>"
  validation_refs:
    - "<path or command>"
  human_approval_ref: null
requested_authority:
  accepted_state_authority: false
  production_authority: false
  live_execution_authority: false
  secrets_authority: false
  deploy_authority: false
validation:
  decision: "ACCEPT | REJECT"
  rejections: []
authority:
  accepted_state_authority: false
  production_authority: false
  live_execution_authority: false
  secrets_authority: false
  deploy_authority: false
```
