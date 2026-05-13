/**
 * JOC AI Connectivity Test
 * 
 * Tests live connectivity to AI providers from the development environment.
 * Run: node --experimental-fetch scripts/test-connectivity.mjs
 */

import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── Load Environment ───

function loadEnv() {
    try {
        const envPath = join(__dirname, '../../../.env');
        const envContent = readFileSync(envPath, 'utf-8');
        const vars = {};
        envContent.split('\n').forEach(line => {
            const match = line.match(/^([^#=]+)=(.*)$/);
            if (match) vars[match[1].trim()] = match[2].trim();
        });
        return vars;
    } catch {
        return {};
    }
}

const env = loadEnv();

// ─── Test Results ───

const results = [];
const timestamp = new Date().toISOString();

function log(provider, status, message, data = null) {
    const icon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⚠️';
    console.log(`  ${icon} [${provider}] ${message}`);
    results.push({ provider, status, message, data, timestamp });
}

// ─── Test 1: Gemini API (REST) ───

async function testGeminiAPI() {
    const apiKey = env.GEMINI_API_KEY;
    if (!apiKey) {
        log('Gemini API', 'SKIP', 'No GEMINI_API_KEY found in .env');
        return;
    }

    console.log('\n  Testing Gemini API...');

    try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
        const body = {
            contents: [{
                parts: [{
                    text: 'JOC connectivity test from Claude Opus 4.6 via AIM-OS MCP bridge. Reply with ONLY this JSON: {"status":"connected","provider":"Gemini","model":"<your-model>","message":"<one-line greeting>"}'
                }]
            }],
            generationConfig: {
                maxOutputTokens: 100,
                temperature: 0.1,
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.text();
            log('Gemini API', 'FAIL', `HTTP ${response.status}: ${error.slice(0, 200)}`);
            return;
        }

        const data = await response.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
        log('Gemini API', 'PASS', `Response received`, { response: text.trim() });
    } catch (err) {
        log('Gemini API', 'FAIL', `Error: ${err.message}`);
    }
}

// ─── Test 2: Gemini CLI ───

async function testGeminiCLI() {
    console.log('\n  Testing Gemini CLI...');

    try {
        // Check if gemini CLI exists
        const version = execSync('gemini --version 2>&1', { encoding: 'utf-8', timeout: 10000 }).trim();
        log('Gemini CLI', 'PASS', `CLI found: ${version}`);
    } catch (err) {
        log('Gemini CLI', 'FAIL', `CLI not available: ${err.message.slice(0, 100)}`);
    }
}

// ─── Test 3: MCP Connectivity ───

async function testMCPBridge() {
    console.log('\n  Testing MCP bridge...');

    try {
        // Check if MCP server is running on port 5001
        const response = await fetch('http://localhost:5001/health', {
            signal: AbortSignal.timeout(3000)
        });
        if (response.ok) {
            log('MCP Bridge', 'PASS', 'Lucid MCP server responding on port 5001');
        } else {
            log('MCP Bridge', 'WARN', `MCP server returned ${response.status}`);
        }
    } catch {
        // Try alternative port
        try {
            const response = await fetch('http://localhost:5001/', {
                signal: AbortSignal.timeout(3000)
            });
            log('MCP Bridge', 'PASS', 'MCP server responding');
        } catch {
            log('MCP Bridge', 'WARN', 'MCP server not reachable on port 5001 (may be running via stdio)');
        }
    }
}

// ─── Test 4: JOC Dev Server ───

async function testJOCServer() {
    console.log('\n  Testing JOC dev server...');

    try {
        const response = await fetch('http://localhost:5011/', {
            signal: AbortSignal.timeout(3000)
        });
        if (response.ok) {
            log('JOC Server', 'PASS', 'Dev server running on port 5011');
        } else {
            log('JOC Server', 'FAIL', `Server returned ${response.status}`);
        }
    } catch {
        log('JOC Server', 'FAIL', 'Dev server not running on port 5011');
    }
}

// ─── Run All Tests ───

console.log('╔══════════════════════════════════════════════════╗');
console.log('║  JOC — AI Connectivity Test Suite                ║');
console.log('║  Testing from: Claude Opus 4.6 IDE session       ║');
console.log('╚══════════════════════════════════════════════════╝');

await testGeminiAPI();
await testGeminiCLI();
await testMCPBridge();
await testJOCServer();

console.log('\n─── Summary ───');
const passed = results.filter(r => r.status === 'PASS').length;
const failed = results.filter(r => r.status === 'FAIL').length;
const warned = results.filter(r => r.status === 'WARN').length;
console.log(`  ${passed} passed, ${failed} failed, ${warned} warnings`);
console.log('');
