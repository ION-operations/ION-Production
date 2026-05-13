# Claim-Evidence Lock

- Generated UTC: 2026-02-19T04:54:16.012366+00:00
- Repo root: `C:\Users\bombe\OneDrive\Desktop\AIM-OS`
- Controlled env: `PYTHONPATH=.;packages`

## Claims

| ID | Statement | Status | Observed | Evidence Command |
|---|---|---|---|---|
| CLM-001 | MCP tools/list surface matches tools/call surface. | supported | listed=103 callable=103 parity_ok=True | `mcp_parity` |
| CLM-002 | Coverage policy excludes tagged mirror files from coverage parsing scope. | supported | policy_ok=True tagged_count=115 parse_failures=18 | `tagged_policy` |
| CLM-003 | APOE package test suite passes in controlled environment. | supported | passed=381 failed=0 skipped=10 errors=0 | `apoe_tests` |
| CLM-004 | HHNI package test suite passes in controlled environment. | supported | passed=119 failed=0 skipped=1 errors=0 | `hhni_tests` |
| CLM-005 | SEG package test suite passes in controlled environment. | supported | passed=104 failed=0 errors=0 | `seg_tests` |
| CLM-006 | SDF-CVF package test suite passes in controlled environment. | supported | passed=154 failed=0 warnings=0 | `sdfcvf_tests` |
| CLM-007 | MCP parity pytest guardrails are passing. | supported | passed=2 failed=0 errors=0 | `mcp_parity_tests` |
| CLM-008 | Source-of-truth dry-run reports parity and current inventory metrics. | supported | mcp_listed=103 mcp_callable=103 systems=64 docs=3407 tests=316 | `source_of_truth` |

## Command Evidence

### mcp_parity
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe scripts/check_mcp_tool_parity.py`
- Return code: `0`
- Duration seconds: `0.122`
- Parsed summary: `{"callable_count": 103, "listed_count": 103, "parity_ok": true}`
- Stdout tail:
```text
{
  "listed_count": 103,
  "callable_count": 103,
  "parity_ok": true,
  "listed_not_callable": [],
  "callable_not_listed": []
}
```

### source_of_truth
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe scripts/detect_source_of_truth.py --dry-run --check-mcp-parity`
- Return code: `0`
- Duration seconds: `96.453`
- Parsed summary: `{"documentation_files": 3407, "mcp_callable": 103, "mcp_listed": 103, "mcp_parity_ok": true, "systems": 64, "test_files": 316}`
- Stdout tail:
```text
DRY RUN - Detecting source of truth...

Source of Truth Preview:
   MCP Tools (listed): 103
   MCP Tools (callable): 103
   MCP Parity OK: True
   Cursor Commands: 16
   Systems: 64
   Documentation Files: 3407
   Test Files: 316
[OK] MCP tool parity check passed.
```

### tagged_policy
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe scripts/check_tagged_coverage_policy.py`
- Return code: `0`
- Duration seconds: `1.4`
- Parsed summary: `{"parse_clean": false, "parse_failure_count": 18, "policy_ok": true, "tagged_file_count": 115}`
- Stdout tail:
```text
        "error_type": "SyntaxError",
        "error": "'(' was never closed (calibration_TAGGED.py, line 325)"
      },
      {
        "path": "packages\\vif\\cmc_integration_TAGGED.py",
        "error_type": "SyntaxError",
        "error": "'(' was never closed (cmc_integration_TAGGED.py, line 252)"
      },
      {
        "path": "packages\\vif\\confidence_extraction_TAGGED.py",
        "error_type": "SyntaxError",
        "error": "'(' was never closed (confidence_extraction_TAGGED.py, line 293)"
      }
    ]
  },
  "status": {
    "policy_ok": true,
    "parse_clean": false
  }
}
```

### mcp_parity_tests
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe -m pytest tests/test_mcp_tool_surface_parity.py -q -o addopts=''`
- Return code: `0`
- Duration seconds: `1.176`
- Parsed summary: `{"errors": 0, "failed": 0, "passed": 2, "skipped": 0, "warnings": 0, "xfailed": 0, "xpassed": 0}`
- Stdout tail:
```text
..                                                                       [100%]
2 passed in 0.12s
```

### apoe_tests
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe -m pytest packages/apoe/tests -q -o addopts=''`
- Return code: `0`
- Duration seconds: `19.036`
- Parsed summary: `{"errors": 0, "failed": 0, "passed": 381, "skipped": 10, "warnings": 0, "xfailed": 0, "xpassed": 0}`
- Stdout tail:
```text
.................................................ss.ssssssss............ [ 18%]
........................................................................ [ 36%]
........................................................................ [ 55%]
........................................................................ [ 73%]
........................................................................ [ 92%]
...............................                                          [100%]
381 passed, 10 skipped in 17.21s
```

### hhni_tests
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe -m pytest packages/hhni/tests -q -o addopts=''`
- Return code: `0`
- Duration seconds: `23.723`
- Parsed summary: `{"errors": 0, "failed": 0, "passed": 119, "skipped": 1, "warnings": 0, "xfailed": 0, "xpassed": 0}`
- Stdout tail:
```text
..................................................s..................... [ 60%]
................................................                         [100%]
119 passed, 1 skipped in 21.55s
```

### seg_tests
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe -m pytest packages/seg/tests -q -o addopts=''`
- Return code: `0`
- Duration seconds: `10.758`
- Parsed summary: `{"errors": 0, "failed": 0, "passed": 104, "skipped": 0, "warnings": 0, "xfailed": 0, "xpassed": 0}`
- Stdout tail:
```text
........................................................................ [ 69%]
................................                                         [100%]
104 passed in 9.08s
```

### sdfcvf_tests
- Command: `C:\Users\bombe\AppData\Local\Programs\Python\Python312\python.exe -m pytest packages/sdfcvf/tests -q -o addopts=''`
- Return code: `0`
- Duration seconds: `651.26`
- Parsed summary: `{"errors": 0, "failed": 0, "passed": 154, "skipped": 0, "warnings": 0, "xfailed": 0, "xpassed": 0}`
- Stdout tail:
```text
........................................................................ [ 46%]
........................................................................ [ 93%]
..........                                                               [100%]
154 passed in 648.26s (0:10:48)
```
