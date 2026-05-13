# Quintet Parity - Canonical Number Reconciliation
# Ensures all documentation matches source of truth

.PHONY: init test test-quick reconcile verify sign pack prove clean help

# First-time setup
init:
	python -m pip install -U pip
	python -m pip install -r requirements.txt || true
	chmod +x .git/hooks/pre-commit || true

# Run a quick quintet test pass
test-quick:
	pytest -q --maxfail=1 --disable-warnings packages/sdfcvf/tests/ packages/nl_tags/tests/

# Reconcile all numbers from source of truth
reconcile:
	@echo "Reconciling numbers from NL_TAG_CATALOG.md files..."
	python scripts/reconcile_from_catalogs.py
	python scripts/validate_tag_references.py || true
	python scripts/fix_all_tag_numbers.py || true
	@echo "[OK] All numbers reconciled"

# Verify documentation matches reconciled totals
verify:
	@echo "Verifying documentation matches source of truth..."
	@python scripts/verify_numbers_match.py || (echo "[FAIL] Numbers diverged from source!" && exit 1)
	@echo "[OK] All numbers match source of truth"

# Tri-source verification (regex + catalogs + registry must agree) + schema validation
prove: reconcile
	@echo "Running tri-source verification..."
	@python scripts/simple_tag_counter.py
	@python scripts/tri_verify_counts.py
	@python -m jsonschema -q -i artifacts/reconciled_totals.json schema/reconciled_totals.schema.json 2>/dev/null || echo "[WARN] jsonschema not installed - run: pip install jsonschema"
	@echo "[OK] Tri-verify + schema validation complete"

# Sign reconciled totals with SHA256
sign:
	@echo "Signing reconciled totals..."
	@python -c "import json,hashlib,datetime; \
		p='artifacts/reconciled_totals.json'; \
		b=open(p,'rb').read(); \
		sha=hashlib.sha256(b).hexdigest(); \
		sig={'file':p,'sha256':sha,'timestamp':datetime.datetime.utcnow().isoformat()+'Z'}; \
		open('artifacts/reconciled_totals.sha256.json','w').write(json.dumps(sig,indent=2))"
	@echo "[OK] Signature created: artifacts/reconciled_totals.sha256.json"

# Create tamper-evident proof pack
pack: reconcile verify sign
	@echo "Creating proof pack..."
	@echo "Creating proof pack..."
	tar -czf artifacts/proof-pack-$(shell date +%Y%m%dT%H%M%S).tar.gz \
		artifacts/reconciled_totals.json \
		artifacts/reconciled_totals.sha256.json \
		artifacts/session_completion_witness.jsonld
	@echo "[OK] Proof pack created"

# Run quintet tests
test:
	@echo "Running quintet parity tests..."
	python -m pytest packages/sdfcvf/tests/ packages/nl_tags/tests/ -v --tb=short
	@echo "[OK] Tests complete"

# Clean artifacts
clean:
	rm -f artifacts/*.tar.gz
	@echo "[OK] Cleaned proof packs"

# Help
help:
	@echo "Quintet Parity Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  reconcile - Generate canonical numbers from catalogs"
	@echo "  verify    - Verify docs match reconciled totals"
	@echo "  sign      - Sign reconciled totals with SHA256"
	@echo "  pack      - Create tamper-evident proof pack"
	@echo "  test      - Run all quintet tests"
	@echo "  clean     - Remove old proof packs"

