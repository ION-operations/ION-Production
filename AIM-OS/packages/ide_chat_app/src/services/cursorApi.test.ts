/**
 * Test file for Cursor API client
 * Tests connection to extension command server
 */

import { CursorAPI, getCursorAPI } from './cursorApi';

async function testCursorAPI() {
    console.log('🧪 Testing Cursor API connection...');
    
    const api = getCursorAPI();
    
    // Test 1: Check availability
    console.log('\n1. Checking command server availability...');
    const available = await api.checkAvailability();
    console.log(`   Available: ${available ? '✅' : '❌'}`);
    
    if (!available) {
        console.log('\n⚠️  Command server not available.');
        console.log('   Make sure:');
        console.log('   1. Cursor extension is installed and activated');
        console.log('   2. Extension command server is running on port 5001');
        console.log('   3. No firewall blocking localhost:5001');
        return;
    }
    
    // Test 2: Execute simple command
    console.log('\n2. Testing command execution...');
    const result = await api.executeCommand('aimos.showDashboard');
    console.log(`   Result: ${result.success ? '✅' : '❌'}`);
    if (!result.success) {
        console.log(`   Error: ${result.error}`);
    }
    
    // Test 3: Test convenience methods
    console.log('\n3. Testing convenience methods...');
    
    try {
        await api.showDashboard();
        console.log('   showDashboard(): ✅');
    } catch (error: any) {
        console.log(`   showDashboard(): ❌ ${error.message}`);
    }
    
    console.log('\n✅ Cursor API tests complete!');
}

// Run tests if executed directly
if (typeof window !== 'undefined') {
    // Browser context
    (window as any).testCursorAPI = testCursorAPI;
} else {
    // Node context
    testCursorAPI().catch(console.error);
}

