// Demo script for Lucid Core Console
// This demonstrates the basic functionality without requiring VS Code

import { DaemonClient } from './src/daemonClient';
import { TimelineLogger } from './src/timelineLogger';
import { VoiceInterface } from './src/voiceInterface';
import { PhoneRemote } from './src/phoneRemote';

async function runDemo() {
    console.log('🚀 Lucid Core Console Demo');
    console.log('========================\n');

    // Initialize components
    const timelineLogger = new TimelineLogger();
    const daemonClient = new DaemonClient(timelineLogger);
    const voiceInterface = new VoiceInterface(daemonClient, timelineLogger);
    const phoneRemote = new PhoneRemote(daemonClient, timelineLogger);

    console.log('✅ Components initialized');

    // Test timeline logging
    console.log('\n📊 Testing Timeline Logging...');
    timelineLogger.log('demo_started', {
        message: 'Lucid Core Console demo started',
        timestamp: Date.now()
    });

    // Test voice interface
    console.log('\n🎤 Testing Voice Interface...');
    try {
        const config = voiceInterface.getConfig();
        console.log(`Voice config: ${JSON.stringify(config, null, 2)}`);
        
        // Simulate voice input processing
        const transcript = await voiceInterface.processAudio('test audio data');
        console.log(`Voice transcript: "${transcript}"`);
    } catch (error) {
        console.log(`Voice interface error (expected in demo): ${error.message}`);
    }

    // Test phone remote
    console.log('\n📱 Testing Phone Remote...');
    try {
        const qrCode = await phoneRemote.startPairing();
        console.log(`QR Code generated: ${qrCode.substring(0, 20)}...`);
        
        const sessions = phoneRemote.getActiveSessions();
        console.log(`Active sessions: ${sessions.length}`);
    } catch (error) {
        console.log(`Phone remote error: ${error.message}`);
    }

    // Test daemon client (will fail without daemon)
    console.log('\n🔌 Testing Daemon Client...');
    console.log(`Daemon connected: ${daemonClient.isConnected}`);
    
    try {
        await daemonClient.processInput('Hello, Aether!');
        console.log('✅ Daemon communication successful');
    } catch (error) {
        console.log(`Daemon communication error (expected without daemon): ${error.message}`);
    }

    // Test timeline stats
    console.log('\n📈 Timeline Statistics...');
    const stats = timelineLogger.getStats();
    console.log(`Total entries: ${stats.totalEntries}`);
    console.log(`Session entries: ${stats.sessionEntries}`);
    console.log(`Entry types: ${JSON.stringify(stats.types, null, 2)}`);

    // Cleanup
    console.log('\n🧹 Cleaning up...');
    daemonClient.dispose();
    voiceInterface.dispose();
    phoneRemote.dispose();

    console.log('\n✅ Demo completed successfully!');
    console.log('\nTo use the full extension:');
    console.log('1. Install in VS Code/Cursor');
    console.log('2. Start Aether\'s daemon on localhost:8080');
    console.log('3. Open the Lucid Core Console panel');
    console.log('4. Start interacting with Aether!');
}

// Run the demo
runDemo().catch(console.error);
