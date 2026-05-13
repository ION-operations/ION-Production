/**
 * BAS E2E Smoke Test — Gates 1-4 (no login required)
 * 
 * Tests: Health → Launch → Navigate → Screenshot
 * Gates 5-6 (inject/extract) require manual ChatGPT login.
 * 
 * Usage: node packages/joc/scripts/bas-e2e-smoke.mjs
 */

const BAS = 'http://localhost:5002';

async function gate(name, fn) {
    process.stdout.write(`  ${name}... `);
    try {
        const result = await fn();
        console.log(`✅ PASS ${result || ''}`);
        return result;
    } catch (err) {
        console.log(`❌ FAIL: ${err.message}`);
        return null;
    }
}

async function main() {
    console.log('\n🔬 BAS E2E Smoke Test\n');
    console.log('─'.repeat(50));

    // Gate 1: Health
    const health = await gate('Gate 1: BAS Health', async () => {
        const res = await fetch(`${BAS}/health`);
        const data = await res.json();
        if (data.status !== 'ok') throw new Error(`status: ${data.status}`);
        return `(services: ${Object.keys(data.services).join(', ')})`;
    });
    if (!health) {
        console.log('\n⛔ BAS not running. Start with: cd packages/browser-automation-service && npm start');
        process.exit(1);
    }

    // Gate 2: Browser Launch
    let browserId = null;
    browserId = await gate('Gate 2: Browser Launch', async () => {
        const res = await fetch(`${BAS}/api/browser/launch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ headless: false, viewport: { width: 1280, height: 800 } }),
        });
        const data = await res.json();
        if (!data.success || !data.browserId) throw new Error(JSON.stringify(data));
        return data.browserId;
    });
    if (!browserId) {
        console.log('\n⛔ Browser launch failed. Check Puppeteer/Chromium installation.');
        process.exit(1);
    }

    // Gate 3: Navigation
    await gate('Gate 3: Navigate to chatgpt.com', async () => {
        const res = await fetch(`${BAS}/api/browser/navigate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ browserId, url: 'https://chatgpt.com' }),
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Navigation failed');
        return '';
    });

    // Wait for page load
    await new Promise(r => setTimeout(r, 3000));

    // Gate 4: Screenshot
    await gate('Gate 4: Screenshot Capture', async () => {
        const res = await fetch(`${BAS}/api/browser/screenshot?browserId=${browserId}&type=png`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const buffer = await res.arrayBuffer();
        const size = buffer.byteLength;
        if (size < 1000) throw new Error(`Image too small: ${size} bytes`);
        return `(${Math.round(size / 1024)}KB PNG)`;
    });

    // Gate 5: Status Check
    await gate('Gate 5: Browser Status', async () => {
        const res = await fetch(`${BAS}/api/browser/status?browserId=${browserId}`);
        const data = await res.json();
        if (!data.success) throw new Error(data.error);
        const s = data.status;
        return `(status: ${s?.status}, url: ${s?.url?.substring(0, 40)}...)`;
    });

    // Gate 6: Providers
    await gate('Gate 6: Provider Discovery', async () => {
        const res = await fetch(`${BAS}/api/bridge/providers`);
        const data = await res.json();
        if (!data.success) throw new Error(data.error);
        return `(${data.providers?.length} providers: ${data.providers?.map(p => p.name).join(', ')})`;
    });

    console.log('\n─'.repeat(50));
    console.log('📋 Gates 1-6 complete (no-auth gates).');
    console.log('');
    console.log('⚠️  Gates 7-8 (inject/extract) require manual ChatGPT login.');
    console.log('    Log into ChatGPT in the launched browser, then run:');
    console.log('');
    console.log(`    curl -X POST ${BAS}/api/bridge/send-prompt \\`);
    console.log(`      -H "Content-Type: application/json" \\`);
    console.log(`      -d '{"browserId":"${browserId}","prompt":"Say hello in 5 words","provider":"chatgpt","waitForResponse":true}'`);
    console.log('');

    // Cleanup option
    console.log(`    To close browser: curl -X POST ${BAS}/api/browser/close -H "Content-Type: application/json" -d '{"browserId":"${browserId}"}'`);
    console.log('');
}

main().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
