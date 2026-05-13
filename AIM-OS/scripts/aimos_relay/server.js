/**
 * ═══════════════════════════════════════════════════════════════════
 * AIM-OS MCP Relay Server
 * ═══════════════════════════════════════════════════════════════════
 *
 * Self-hosted ngrok replacement. Deploy to ANY platform that runs
 * Node.js (Lovable, Bolt, Render, Railway, Glitch, etc.)
 *
 * Architecture:
 *   ChatGPT ──HTTP/SSE──► Relay (cloud) ◄──WebSocket──► Bridge (local)
 *                                                          │
 *                                                          ▼
 *                                                   localhost:8000
 *                                                   (SSE MCP Server)
 *
 * Protocol:
 *   1. Local bridge connects via WS to /ws/bridge?secret=XXX
 *   2. ChatGPT connects to GET /sse — relay returns session endpoint
 *   3. ChatGPT POSTs to /messages — relay forwards to bridge via WS
 *   4. Bridge calls local SSE server, gets response, sends back via WS
 *   5. Relay returns response to ChatGPT
 */

const express = require('express');
const http = require('http');
const { WebSocketServer, WebSocket } = require('ws');
const { v4: uuidv4 } = require('uuid');

const app = express();
const server = http.createServer(app);

// ─── Config ───
const PORT = process.env.PORT || 3001;
const BRIDGE_SECRET = process.env.BRIDGE_SECRET || 'aimos-relay-secret-2026';

// ─── State ───
let bridgeSocket = null;                      // Single bridge WS connection
const pendingRequests = new Map();            // requestId → { res, sseWriter }
const sseSessions = new Map();                // sessionId → SSE response writer

// ─── Middleware ───
app.use(express.json({ limit: '10mb' }));
app.use(express.text({ type: 'text/*', limit: '10mb' }));

// CORS for ChatGPT
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') return res.sendStatus(200);
    next();
});

// ─── Health ───
app.get('/', (req, res) => {
    res.json({
        service: 'AIM-OS MCP Relay',
        version: '1.0.0',
        bridge_connected: bridgeSocket?.readyState === WebSocket.OPEN,
        active_sessions: sseSessions.size,
        uptime: process.uptime(),
    });
});

app.get('/health', (req, res) => {
    res.json({ ok: bridgeSocket?.readyState === WebSocket.OPEN });
});

// ─── MCP SSE Endpoint (ChatGPT connects here) ───
app.get('/sse', (req, res) => {
    if (!bridgeSocket || bridgeSocket.readyState !== WebSocket.OPEN) {
        return res.status(503).json({ error: 'Bridge not connected — local AIM-OS is offline' });
    }

    const sessionId = uuidv4();

    // SSE headers
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
    });

    // Store the SSE writer
    sseSessions.set(sessionId, res);

    // Send endpoint event (MCP SSE protocol requirement)
    const messagesUrl = `/messages?session_id=${sessionId}`;
    res.write(`event: endpoint\ndata: ${messagesUrl}\n\n`);

    console.log(`[SSE] Session ${sessionId} opened`);

    // Notify bridge of new session
    bridgeSend({ type: 'session_open', sessionId });

    // Cleanup on disconnect
    req.on('close', () => {
        sseSessions.delete(sessionId);
        bridgeSend({ type: 'session_close', sessionId });
        console.log(`[SSE] Session ${sessionId} closed`);
    });
});

// ─── MCP Messages Endpoint (ChatGPT sends tool calls here) ───
app.post('/messages', (req, res) => {
    const sessionId = req.query.session_id;

    if (!sessionId || !sseSessions.has(sessionId)) {
        return res.status(400).json({ error: 'Invalid or expired session_id' });
    }

    if (!bridgeSocket || bridgeSocket.readyState !== WebSocket.OPEN) {
        return res.status(503).json({ error: 'Bridge not connected' });
    }

    const requestId = uuidv4();

    // Store pending request so we can respond when bridge replies
    pendingRequests.set(requestId, {
        res,
        sessionId,
        timestamp: Date.now(),
    });

    // Forward to bridge
    bridgeSend({
        type: 'mcp_request',
        requestId,
        sessionId,
        method: req.method,
        body: req.body,
        contentType: req.headers['content-type'],
    });

    // Timeout after 120s
    setTimeout(() => {
        if (pendingRequests.has(requestId)) {
            pendingRequests.delete(requestId);
            if (!res.headersSent) {
                res.status(504).json({ error: 'Bridge timeout' });
            }
        }
    }, 120000);
});

// ─── WebSocket Server (Bridge connects here) ───
const wss = new WebSocketServer({ server, path: '/ws/bridge' });

wss.on('connection', (ws, req) => {
    // Auth check
    const url = new URL(req.url, `http://${req.headers.host}`);
    const secret = url.searchParams.get('secret');

    if (secret !== BRIDGE_SECRET) {
        console.log('[WS] Bridge rejected — bad secret');
        ws.close(4001, 'Invalid secret');
        return;
    }

    // Only one bridge at a time
    if (bridgeSocket && bridgeSocket.readyState === WebSocket.OPEN) {
        console.log('[WS] Replacing existing bridge connection');
        bridgeSocket.close(4002, 'Replaced by new connection');
    }

    bridgeSocket = ws;
    console.log('[WS] Bridge connected!');

    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data.toString());
            handleBridgeMessage(msg);
        } catch (e) {
            console.error('[WS] Bad message from bridge:', e.message);
        }
    });

    ws.on('close', () => {
        console.log('[WS] Bridge disconnected');
        if (bridgeSocket === ws) bridgeSocket = null;
    });

    ws.on('error', (err) => {
        console.error('[WS] Bridge error:', err.message);
    });
});

// ─── Handle messages from bridge ───
function handleBridgeMessage(msg) {
    switch (msg.type) {
        case 'mcp_response': {
            // Response to a pending request
            const pending = pendingRequests.get(msg.requestId);
            if (pending && !pending.res.headersSent) {
                pending.res.status(msg.status || 200);
                if (msg.contentType) {
                    pending.res.setHeader('Content-Type', msg.contentType);
                }
                pending.res.send(msg.body);
            }
            pendingRequests.delete(msg.requestId);
            break;
        }

        case 'sse_event': {
            // Forward SSE event to the right session
            const sseRes = sseSessions.get(msg.sessionId);
            if (sseRes) {
                if (msg.event) {
                    sseRes.write(`event: ${msg.event}\ndata: ${msg.data}\n\n`);
                } else {
                    sseRes.write(`data: ${msg.data}\n\n`);
                }
            }
            break;
        }

        case 'bridge_status': {
            console.log(`[Bridge] Status: ${msg.message}`);
            break;
        }

        default:
            console.log(`[Bridge] Unknown message type: ${msg.type}`);
    }
}

// ─── Helper ───
function bridgeSend(msg) {
    if (bridgeSocket && bridgeSocket.readyState === WebSocket.OPEN) {
        bridgeSocket.send(JSON.stringify(msg));
    }
}

// ─── Cleanup stale requests every 30s ───
setInterval(() => {
    const now = Date.now();
    for (const [id, req] of pendingRequests) {
        if (now - req.timestamp > 120000) {
            pendingRequests.delete(id);
        }
    }
}, 30000);

// ─── Start ───
server.listen(PORT, () => {
    console.log('═══════════════════════════════════════════════════');
    console.log('  AIM-OS MCP Relay Server');
    console.log(`  Port: ${PORT}`);
    console.log(`  SSE Endpoint: /sse`);
    console.log(`  Bridge WS: /ws/bridge?secret=${BRIDGE_SECRET}`);
    console.log('═══════════════════════════════════════════════════');
    console.log('Waiting for bridge connection from local AIM-OS...');
});
