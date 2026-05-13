# BAS Auth Gates 7-8 Proof Runbook (2026-03-04)

## Purpose

Execute and capture evidence for authenticated BAS gates:

- Gate 7: Prompt Injection (`/api/bridge/send-prompt`)
- Gate 8: Response Extraction (`/api/bridge/extract-response`)

This runbook is for a human/operator with an active ChatGPT session in the launched browser.

## Policy Guardrail

- If ChatGPT is not authenticated in the target browser, status is **`PENDING_AUTH`**.
- Do not claim Gate 7/8 success from transport-only responses when login is missing.
- Baseline no-auth gates may still pass while authenticated gates remain pending.
- Do not execute Gate 7/8 unless operator explicitly issues **`AUTH_READY`**.

## Preconditions

1. BAS is running on `http://127.0.0.1:5002`.
2. No-auth smoke gates 1-6 already pass.
3. You can interact with the launched browser window.
4. You are logged in to ChatGPT in that browser session.

## Step 1: Run No-Auth Smoke and Capture `browserId`

```powershell
cd C:\Users\bombe\OneDrive\Desktop\AIM-OS
node packages/joc/scripts/bas-e2e-smoke.mjs
```

Record the `browserId` printed by Gate 2.

## Step 2: Gate 7 Prompt Injection

```powershell
curl -X POST http://localhost:5002/api/bridge/send-prompt ^
  -H "Content-Type: application/json" ^
  -d "{\"browserId\":\"<BROWSER_ID>\",\"prompt\":\"Say hello in 5 words\",\"provider\":\"chatgpt\",\"waitForResponse\":true}"
```

Expected:

- HTTP success
- Non-error JSON payload
- Provider path confirms prompt dispatch

Save full response payload to evidence.

## Step 3: Gate 8 Response Extraction

```powershell
curl -X POST http://localhost:5002/api/bridge/extract-response ^
  -H "Content-Type: application/json" ^
  -d "{\"browserId\":\"<BROWSER_ID>\",\"provider\":\"chatgpt\"}"
```

Expected:

- HTTP success
- Extracted response content present (non-empty text)

Save full response payload to evidence.

## Step 4: Close Browser Session

```powershell
curl -X POST http://localhost:5002/api/browser/close ^
  -H "Content-Type: application/json" ^
  -d "{\"browserId\":\"<BROWSER_ID>\"}"
```

## Evidence Checklist

- [ ] Timestamp of run
- [ ] Operator identity
- [ ] `browserId`
- [ ] Gate 7 raw request + response payload
- [ ] Gate 8 raw request + response payload
- [ ] Any failure category (auth expired / selector miss / timeout / provider mismatch)
- [ ] Close-session confirmation payload

## Failure Classification

1. `AUTH_REQUIRED`: ChatGPT session missing/expired
2. `SELECTOR_MISMATCH`: provider DOM selectors outdated
3. `TIMEOUT_RESPONSE`: response not detected in wait window
4. `EXTRACTION_EMPTY`: extraction succeeded but content empty
5. `TRANSPORT_ERROR`: non-2xx HTTP/network issue

## Rollback / Recovery

- Re-run no-auth smoke (gates 1-6) to confirm baseline.
- Re-authenticate ChatGPT in same browser session.
- Re-run Gate 7 then Gate 8.
- If repeated selector failures occur, route to BAS selector maintenance lane.
