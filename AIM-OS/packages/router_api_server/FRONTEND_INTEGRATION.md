# Router & Log-Sentinels API Server - Frontend Integration Guide

**Date:** 2025-01-27  
**Status:** ✅ **FRONTEND INTEGRATION READY**

---

## Overview

The Router & Log-Sentinels API Server is ready for integration with the DAC V2 IDE frontend. The frontend hooks (`useRouter.ts` and `useLogSentinels.ts`) are already configured and will automatically connect to the API server when it's running.

---

## Frontend Hooks Status

### ✅ Router Hook (`useRouter.ts`)

**Status:** Ready  
**Location:** `ide_orchestration/prototypes/dac/src/hooks/useRouter.ts`

**Endpoints Used:**
- `GET /api/router/tools` - Fetch tool proposals
- `GET /api/router/telemetry` - Fetch telemetry
- `POST /api/router/execute` - Execute tool

**Features:**
- Automatic refresh every 5 seconds
- Error handling
- Loading states
- TypeScript types

### ✅ Log-Sentinels Hook (`useLogSentinels.ts`)

**Status:** Ready  
**Location:** `ide_orchestration/prototypes/dac/src/hooks/useLogSentinels.ts`

**Endpoints Used:**
- `GET /api/log-sentinels/scouts` - Fetch Scout reports
- `GET /api/log-sentinels/forensics` - Fetch Forensics reports
- `GET /api/log-sentinels/telemetry` - Fetch telemetry
- `GET /api/log-sentinels/stream` - SSE streaming
- `POST /api/log-sentinels/run-tool` - Run suggested tool

**Features:**
- SSE streaming for real-time updates
- Mock data fallback for development
- Automatic refresh every 10 seconds
- Error handling with graceful degradation

---

## API Server Configuration

### Development Setup

**Option 1: Same Origin (Recommended)**
Configure Vite proxy to forward API requests:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Option 2: Environment Variable**
Update hooks to use environment variable:

```typescript
// .env.local
VITE_API_BASE_URL=http://localhost:8000

// useRouter.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const response = await fetch(`${API_BASE_URL}/api/router/tools`)
```

**Option 3: CORS (Production)**
API server already configured with CORS for:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Next.js dev server)

---

## Integration Steps

### 1. Start API Server

```bash
cd packages/router_api_server
uvicorn router_api_server.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Configure Frontend Proxy (if needed)

Add proxy configuration to `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
```

### 3. Verify Connection

Open browser console and check for:
- Successful API calls (200 status)
- No CORS errors
- Data loading in panels

---

## Frontend Panels Integration

### Router Panel

**Component:** `RouterPanel.tsx`  
**Hook:** `useRouter()`  
**Features:**
- Tool proposals display
- Tool execution
- Telemetry display

**Status:** ✅ Ready - Will connect automatically when API server is running

### Log-Sentinels Panels

**Components:**
- `LogSentinelsSummaries.tsx` - Scout reports
- `LogSentinelsAnomalies.tsx` - Forensics reports
- `LogAnalysisDashboard.tsx` - Telemetry dashboard

**Hook:** `useLogSentinels()`  
**Features:**
- Real-time SSE updates
- Scout/Forensics reports
- Tool suggestions
- Telemetry display

**Status:** ✅ Ready - Will connect automatically when API server is running

---

## Mock Data Fallback

The Log-Sentinels hook includes mock data fallback for development:

```typescript
// Mock data used when API is unavailable
const MOCK_SCOUTS: ScoutReport[] = [...]
const MOCK_FORENSICS: ForensicsReport[] = [...]
const MOCK_TELEMETRY: LogSentinelsTelemetry = {...}
```

**Behavior:**
- If API call fails → Use mock data
- Console warning logged
- UI continues to work
- Real data loads when API becomes available

---

## Testing Integration

### Manual Testing

1. **Start API Server:**
   ```bash
   cd packages/router_api_server
   uvicorn router_api_server.main:app --reload
   ```

2. **Start Frontend:**
   ```bash
   cd ide_orchestration/prototypes/dac
   npm run dev
   ```

3. **Verify:**
   - Open Router panel → Should show tool proposals
   - Open Log-Sentinels panels → Should show reports
   - Check browser console → No errors
   - Check Network tab → API calls successful

### Automated Testing

Frontend tests should mock API responses:

```typescript
// Mock API responses
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ tools: [], suggestions: [] })
  })
)
```

---

## Troubleshooting

### CORS Errors

**Symptom:** CORS errors in browser console  
**Solution:** API server CORS already configured, but verify:
- Frontend origin matches CORS allowed origins
- Or use Vite proxy (recommended)

### API Not Found

**Symptom:** 404 errors for API endpoints  
**Solution:**
- Verify API server is running on port 8000
- Check proxy configuration
- Verify endpoint paths match

### SSE Connection Failed

**Symptom:** SSE stream not connecting  
**Solution:**
- Check API server `/api/log-sentinels/stream` endpoint
- Verify SSE headers are set correctly
- Check browser console for errors

### Mock Data Always Showing

**Symptom:** Always seeing mock data  
**Solution:**
- Verify API server is running
- Check network tab for failed requests
- Verify API endpoints are correct

---

## Production Deployment

### Frontend Build

```bash
cd ide_orchestration/prototypes/dac
npm run build
```

### API Server Deployment

See `DEPLOYMENT.md` for production deployment guide.

### Environment Configuration

Set environment variables:

```bash
# Frontend
VITE_API_BASE_URL=https://api.example.com

# API Server
COMMAND_SERVER_URL=http://command-server:5001
```

---

## Next Steps

1. **Test Integration:** Start both servers and verify connection
2. **Configure Proxy:** Add Vite proxy configuration if needed
3. **Monitor:** Check browser console and network tab
4. **Deploy:** Follow deployment guides for production

---

**Status:** ✅ **READY FOR INTEGRATION**  
**Frontend Hooks:** ✅ Configured  
**API Server:** ✅ Running  
**Integration:** ✅ Ready

