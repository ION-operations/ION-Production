# AIM-OS MCP Relay Server

## What This Is

A **WebSocket relay server** that allows ChatGPT (and other remote AI agents) to connect to a local MCP (Model Context Protocol) server running on a developer's machine. This replaces ngrok — providing a **permanent, self-hosted tunnel** with a stable URL.

## Architecture

```
ChatGPT ──HTTP/SSE──► THIS SERVER (cloud) ◄──WebSocket──► Local Bridge (dev machine)
                                                              │
                                                              ▼
                                                        localhost:8000
                                                        (MCP SSE Server)
```

**Two sides:**
1. **ChatGPT side** — connects via standard MCP SSE protocol (`GET /sse` for stream, `POST /messages` for tool calls)
2. **Bridge side** — a Python script on the developer's machine connects via WebSocket to `/ws/bridge` and proxies all traffic to the local MCP server

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Health check / status JSON |
| `GET` | `/health` | Simple health check |
| `GET` | `/sse` | MCP SSE endpoint — ChatGPT connects here |
| `POST` | `/messages?session_id=X` | MCP message endpoint — ChatGPT sends tool calls here |
| `WS` | `/ws/bridge?secret=X` | WebSocket — local bridge connects here |

## How It Works

1. The local bridge script connects to this server via WebSocket at `/ws/bridge?secret=aimos-relay-secret-2026`
2. When ChatGPT connects to `GET /sse`, this server creates an SSE session and sends back an `endpoint` event with the messages URL
3. When ChatGPT sends a `POST /messages`, this server forwards the JSON body to the bridge via WebSocket
4. The bridge forwards it to `localhost:8000/messages` on the dev machine
5. The response comes back through the WebSocket and this server returns it to ChatGPT

## Tech Stack

- **Node.js** (>=18)
- **Express** — HTTP/SSE handling
- **ws** — WebSocket server for bridge connection
- **uuid** — Session ID generation

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | `3001` | Server port |
| `BRIDGE_SECRET` | `aimos-relay-secret-2026` | Auth secret for bridge WebSocket |

## Security

- Bridge WebSocket requires a shared secret query parameter
- Only one bridge connection allowed at a time (new connection replaces old)
- Request timeout: 120 seconds
- Stale request cleanup every 30 seconds

## Deployment

This server should be deployed to **any Node.js hosting platform** — Lovable, Bolt, Render, Railway, Vercel, etc. The only requirement is:
1. Node.js runtime
2. WebSocket support
3. A persistent process (not serverless/edge functions)

After deployment, the URL (e.g., `https://your-app.lovable.app/sse`) is pasted into ChatGPT's MCP App configuration as the MCP Server URL. **This URL never changes.**

## Local Development

```bash
npm install
npm start
```

Server starts on port 3001. Visit `http://localhost:3001/` to see status.
