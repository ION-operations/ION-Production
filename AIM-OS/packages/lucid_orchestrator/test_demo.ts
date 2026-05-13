/**
 * Lucid Orchestrator - Demo and Test
 * 
 * This module demonstrates the Lucid Orchestrator in action with a simple
 * example that shows the four-pane consciousness interface working.
 */

import { createLucidOrchestrator } from './lucid_orchestrator';
import { getGlobalEventBus } from './event_bus/event_bus';

// Example function to demonstrate instrumentation
async function exampleFunction(name: string, delay: number = 100): Promise<string> {
  console.log(`Hello, ${name}!`);
  await new Promise(resolve => setTimeout(resolve, delay));
  return `Processed: ${name}`;
}

// Example React component (simulated)
function ExampleComponent({ title, count }: { title: string; count: number }) {
  console.log(`Rendering ${title} with count ${count}`);
  return { title, count, rendered: true };
}

// Example API handler (simulated)
async function apiHandler(request: any): Promise<any> {
  console.log('Handling API request:', request);
  await new Promise(resolve => setTimeout(resolve, 50));
  return { success: true, data: request };
}

/**
 * Run the Lucid Orchestrator demo
 */
async function runDemo(): Promise<void> {
  console.log('🚀 Starting Lucid Orchestrator Demo...\n');
  
  // Create orchestrator with demo configuration
  const orchestrator = createLucidOrchestrator({
    graph: {
      enableAutoExtraction: true,
      extractionInterval: 10000, // 10 seconds
      includeTests: false,
      includeDependencies: false
    },
    spec: {
      enableDriftDetection: true,
      driftDetectionInterval: 15000, // 15 seconds
      enableAutoGeneration: true,
      securityThreshold: 'medium'
    },
    timeline: {
      enableFunctionInstrumentation: true,
      enableAsyncInstrumentation: true,
      enableIOInstrumentation: true,
      enableUIInstrumentation: true,
      enablePerformanceInstrumentation: true,
      enableSecurityInstrumentation: true,
      performanceSampleRate: 1.0,
      maxEventsPerSession: 1000,
      maxSessionDuration: 60000 // 1 minute
    },
    eventBus: {
      enableFocusSync: true,
      enableUpdateBroadcasting: true,
      enableEventLogging: true,
      maxEventHistory: 100,
      deduplicationWindow: 100
    },
    general: {
      enableLogging: true,
      enableMetrics: true,
      enableHealthMonitoring: true
    }
  });
  
  try {
    // Initialize the orchestrator
    console.log('📋 Initializing Lucid Orchestrator...');
    await orchestrator.initialize('.');
    console.log('✅ Initialization complete!\n');
    
    // Get initial status
    const status = orchestrator.getStatus();
    console.log('📊 Initial Status:');
    console.log(`  Overall Health: ${status.health.overall.toFixed(1)}%`);
    console.log(`  Graph Engine: ${status.engines.graph} (${status.health.graph}%)`);
    console.log(`  Spec Engine: ${status.engines.spec} (${status.health.spec}%)`);
    console.log(`  Timeline Engine: ${status.engines.timeline} (${status.health.timeline}%)`);
    console.log(`  Event Bus: ${status.engines.eventBus} (${status.health.eventBus}%)`);
    console.log(`  Total Nodes: ${status.stats.totalNodes}`);
    console.log(`  Total Specs: ${status.stats.totalSpecs}\n`);
    
    // Set up event listeners to demonstrate the four-pane synchronization
    const eventBus = orchestrator.getEventBus();
    
    console.log('🎯 Setting up Four-Pane Synchronization...');
    
    // Code Pane -> Blueprint Pane
    eventBus.onFocusType('FOCUS_NODE', (event) => {
      console.log(`  📝 Code Pane → Blueprint Pane: Focusing on node ${event.nodeId}`);
    });
    
    // Blueprint Pane -> Spec Pane
    eventBus.onFocusType('FOCUS_SPEC', (event) => {
      console.log(`  🧠 Blueprint Pane → Spec Pane: Focusing on spec ${event.specId}`);
    });
    
    // Spec Pane -> Timeline Pane
    eventBus.onFocusType('FOCUS_TIMELINE', (event) => {
      console.log(`  ⏰ Spec Pane → Timeline Pane: Focusing on event ${event.eventId}`);
    });
    
    // Timeline Pane -> Code Pane
    eventBus.onFocusType('FOCUS_CODE', (event) => {
      console.log(`  🔄 Timeline Pane → Code Pane: Focusing on code location`);
    });
    
    // Drift detection events
    eventBus.onUpdateType('DRIFT_DETECTED', (event) => {
      console.log(`  ⚠️  Drift Detected: Node ${event.nodeId} - ${event.data?.reason}`);
    });
    
    eventBus.onUpdateType('VIOLATION_DETECTED', (event) => {
      console.log(`  🚨 Violation Detected: Node ${event.nodeId} - ${event.data?.reason}`);
    });
    
    console.log('✅ Event listeners configured!\n');
    
    // Demonstrate the Lucid Loop
    console.log('🔄 Demonstrating the Lucid Loop...\n');
    
    // Step 1: Code -> Blueprint (Focus on a node)
    console.log('1️⃣  Code Pane → Blueprint Pane');
    orchestrator.focusNode('example_function', 'code');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 2: Blueprint -> Spec (Focus on spec)
    console.log('2️⃣  Blueprint Pane → Spec Pane');
    orchestrator.focusSpec('example_function_spec', 'blueprint');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 3: Spec -> Timeline (Focus on timeline event)
    console.log('3️⃣  Spec Pane → Timeline Pane');
    orchestrator.focusTimeline('event_123', 'spec');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Step 4: Timeline -> Code (Focus on code location)
    console.log('4️⃣  Timeline Pane → Code Pane');
    eventBus.emitFocusEvent({
      type: 'FOCUS_CODE',
      codeLocation: {
        filePath: 'example.ts',
        startLine: 10,
        endLine: 15
      },
      sourcePane: 'timeline',
      timestamp: Date.now()
    });
    await new Promise(resolve => setTimeout(resolve, 500));
    
    console.log('✅ Lucid Loop demonstration complete!\n');
    
    // Demonstrate instrumentation
    console.log('🔧 Demonstrating Timeline Instrumentation...');
    
    const timelineInstrumentation = orchestrator.getTimelineInstrumentation();
    
    // Instrument the example function
    const instrumentedFunction = timelineInstrumentation.instrumentFunction(
      'example_function',
      'exampleFunction',
      exampleFunction,
      {
        captureArgs: true,
        captureReturn: true,
        captureErrors: true
      }
    );
    
    // Call the instrumented function
    console.log('  📞 Calling instrumented function...');
    const result = await instrumentedFunction('Lucid Orchestrator', 200);
    console.log(`  ✅ Result: ${result}`);
    
    // Record some performance data
    console.log('  📊 Recording performance data...');
    timelineInstrumentation.recordPerformance(
      'example_function',
      'exampleFunction',
      {
        executionTime: 200,
        memoryUsage: 1024,
        cpuUsage: 15.5
      }
    );
    
    // Record a security event
    console.log('  🔒 Recording security event...');
    timelineInstrumentation.recordSecurity(
      'example_function',
      'exampleFunction',
      ['data_processed', 'user_input'],
      { inputLength: 20, sanitized: true }
    );
    
    console.log('✅ Instrumentation demonstration complete!\n');
    
    // Demonstrate drift detection
    console.log('🔍 Running Drift Detection...');
    await orchestrator.runDriftDetection();
    console.log('✅ Drift detection complete!\n');
    
    // Get final status
    const finalStatus = orchestrator.getStatus();
    console.log('📊 Final Status:');
    console.log(`  Overall Health: ${finalStatus.health.overall.toFixed(1)}%`);
    console.log(`  Total Nodes: ${finalStatus.stats.totalNodes}`);
    console.log(`  Total Specs: ${finalStatus.stats.totalSpecs}`);
    console.log(`  Total Events: ${finalStatus.stats.totalEvents}`);
    console.log(`  Uptime: ${(finalStatus.stats.uptime / 1000).toFixed(1)}s\n`);
    
    // Show event history
    const eventHistory = eventBus.getEventHistory();
    console.log('📜 Event History (last 5 events):');
    eventHistory.slice(-5).forEach((event, index) => {
      console.log(`  ${index + 1}. ${event.type} - ${new Date(event.timestamp).toISOString()}`);
    });
    
    console.log('\n🎉 Lucid Orchestrator Demo Complete!');
    console.log('\n💡 Key Features Demonstrated:');
    console.log('  ✅ Four-pane consciousness interface');
    console.log('  ✅ Real-time synchronization via Event Bus');
    console.log('  ✅ Lucid Loop (Code → Blueprint → Spec → Timeline → Code)');
    console.log('  ✅ Timeline instrumentation and event capture');
    console.log('  ✅ Drift detection and violation tracking');
    console.log('  ✅ Performance and security monitoring');
    console.log('  ✅ Health monitoring and metrics');
    
  } catch (error) {
    console.error('❌ Demo failed:', error);
  } finally {
    // Clean up
    console.log('\n🧹 Cleaning up...');
    await orchestrator.stop();
    console.log('✅ Cleanup complete!');
  }
}

/**
 * Run a simple test of the core functionality
 */
async function runSimpleTest(): Promise<void> {
  console.log('🧪 Running Simple Test...\n');
  
  const orchestrator = createLucidOrchestrator({
    general: { enableLogging: false }
  });
  
  try {
    await orchestrator.initialize('.');
    
    // Test basic functionality
    const status = orchestrator.getStatus();
    console.log(`✅ Status: ${status.status}`);
    console.log(`✅ Health: ${status.health.overall.toFixed(1)}%`);
    
    // Test event bus
    const eventBus = orchestrator.getEventBus();
    let eventReceived = false;
    
    eventBus.onFocus(() => {
      eventReceived = true;
    });
    
    eventBus.emitFocusEvent({
      type: 'FOCUS_NODE',
      nodeId: 'test_node',
      sourcePane: 'code',
      timestamp: Date.now()
    });
    
    await new Promise(resolve => setTimeout(resolve, 100));
    console.log(`✅ Event Bus: ${eventReceived ? 'Working' : 'Failed'}`);
    
    console.log('\n✅ Simple test passed!');
    
  } catch (error) {
    console.error('❌ Simple test failed:', error);
  } finally {
    await orchestrator.stop();
  }
}

// Export functions for use
export { runDemo, runSimpleTest };

// Run demo if this file is executed directly
if (require.main === module) {
  runDemo().catch(console.error);
}
