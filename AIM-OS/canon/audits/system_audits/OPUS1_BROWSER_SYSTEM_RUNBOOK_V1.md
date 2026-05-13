# OPUS1 Browser System Operator Runbook V1

**Agent:** Opus1 (Antigravity IDE)  
**Date:** 2026-03-02

---

## Quick Reference

| Action | Command |
|--------|---------|
| Install deps | `cd packages/browser-automation-service && npm install` |
| Build | `npm run build` |
| Start server | `npm start` (port 5002) |
| Run tests | `npm test` |
| Health check | `curl http://localhost:5002/health` |

---

## 1. Starting the Service

```bash
cd packages/browser-automation-service
npm install     # first time only
npm run build   # compile TypeScript
npm start       # starts on http://localhost:5002
```

Environment variables:
- `PORT` — server port (default: `5002`)
- `BROWSER_AUTOMATION_ENCRYPTION_KEY` — encryption key for stored credentials (default: built-in dev key)

---

## 2. API Quick Test

```bash
# Launch browser
curl -X POST http://localhost:5002/api/browser/launch \
  -H "Content-Type: application/json" \
  -d '{"headless":false,"viewport":{"width":1280,"height":720}}'

# Save the browserId from the response, then:
# Navigate
curl -X POST http://localhost:5002/api/browser/navigate \
  -H "Content-Type: application/json" \
  -d '{"browserId":"BROWSER_ID","url":"https://chat.openai.com"}'

# Get viewport (live view)
curl "http://localhost:5002/api/browser/viewport?browserId=BROWSER_ID"

# Detect elements
curl -X POST http://localhost:5002/api/browser/detect-elements \
  -H "Content-Type: application/json" \
  -d '{"browserId":"BROWSER_ID"}'

# Get metrics
curl http://localhost:5002/api/automation/metrics

# Screenshot
curl "http://localhost:5002/api/browser/screenshot?browserId=BROWSER_ID" --output screenshot.png

# Close browser
curl -X POST http://localhost:5002/api/browser/close \
  -H "Content-Type: application/json" \
  -d '{"browserId":"BROWSER_ID"}'
```

---

## 3. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ECONNREFUSED :5002` | Server not running | `npm start` |
| `Browser instance not found` | Browser was closed or timed out | Launch a new browser |
| Viewport returns `null` | CDP WebSocket not available | Use screenshot fallback (panel does this automatically) |
| `Failed to launch browser` | Puppeteer/Chrome not installed | `npx puppeteer install` |
| Stale browsers accumulate | Cleanup interval not running | Restart server (auto-starts cleanup) |
| Tests fail with `supertest` error | Dependencies not installed | `npm install` |

---

## 4. Architecture Notes

- **Browser instances** are tracked in-memory in `BrowserService.instances` Map
- **Stale cleanup** runs every 5 minutes, removes instances inactive for 30+ minutes
- **Dead instance detection** checks `browser.isConnected()` each cleanup cycle
- **Graceful shutdown** on SIGINT/SIGTERM: stops cleanup interval, closes all browsers
- **Session data** (cookies, credentials) stored encrypted in `browser-automation-accounts.json`
- **Credentials** encrypted with AES-256-GCM via `ConnectionManager`

---

## 5. Panel Integration

The DAC panel (`BrowserAutomationPanel.tsx`) connects to `http://localhost:5002/api`. All 14 API calls are wired to real backend endpoints. Ensure the backend is running before loading the panel.

Key panel features:
- **Live View:** Attempts viewport URL first, falls back to direct iframe/screenshot
- **Metrics:** Loaded from `GET /api/automation/metrics` on mount
- **Element Inspector:** Calls `POST /api/browser/detect-elements` for real page analysis
- **Error Reporting:** All errors logged to panel log pane

---

*Browser Automation Service — Part of AIM-OS Project* 💙✨
