# PR: APOE → CMC v1 (feature/apoe-cmc-v1)

Checklist:
- [ ] Links: `agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md`, `agents/alex/APOE_CMC_TEST_CHECKLIST.md`
- [ ] Attach sample payload(s): `packages/apoe/samples/apoe_cmc_sample_payloads.json`
- [ ] Reviewers required: @Atlas, @Sev
- [ ] CI gate: fail if emitted atom modality != `plan_execution` OR tags missing `plan_name:*` OR `status:*`
- [ ] Tests pass for APOE CMC subset (modality/tags/order/partial/error metrics)
- [ ] Deterministic ordering verified (started_at DESC, then execution_id DESC)
- [ ] Edge cases covered (partial executions, clock skew, backfill bursts)

Summary:
- Implement clean v1: `packages/apoe/cmc_integration_v1.py` (+ executor facade)
- Update tests: `packages/apoe/tests/test_cmc_integration.py`
- Artifacts: `packages/apoe/samples/apoe_cmc_sample_payloads.json`


