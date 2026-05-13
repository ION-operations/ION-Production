/**
 * Lucid Orchestrator Data Services Demo
 * 
 * Demonstrates how to use the data services to load and manage
 * system data across all four panes.
 */

import { LucidOrchestratorService } from '../data_services/lucid_orchestrator_service';
import { Event, EventType } from '../data_models/core_interfaces';

async function runDemo() {
  console.log('🚀 Starting Lucid Orchestrator Data Services Demo\n');

  // Initialize the orchestrator service
  const orchestrator = new LucidOrchestratorService('knowledge_architecture/systems');

  try {
    // Load a system (using CMC as an example)
    console.log('📁 Loading CMC system...');
    const systemData = await orchestrator.loadSystem('cmc');
    
    console.log('✅ System loaded successfully!');
    console.log(`   - System: ${systemData.metadata.name}`);
    console.log(`   - Status: ${systemData.metadata.status}`);
    console.log(`   - Files: ${systemData.code.files.source.length} source, ${systemData.code.files.documentation.length} docs`);
    console.log(`   - Architecture Nodes: ${systemData.blueprint.architecture.nodes.length}`);
    console.log(`   - Specifications: ${systemData.spec.specs.requirements.length} requirements`);
    console.log(`   - Timeline Events: ${systemData.timeline.events.documentation.length} doc events\n`);

    // Display code metrics
    console.log('📊 Code Metrics:');
    console.log(`   - Total Lines: ${systemData.code.metrics.totalLines}`);
    console.log(`   - Test Coverage: ${(systemData.code.metrics.testCoverage * 100).toFixed(1)}%`);
    console.log(`   - Documentation Coverage: ${(systemData.code.metrics.documentationCoverage * 100).toFixed(1)}%`);
    console.log(`   - Complexity: ${systemData.code.metrics.complexity.toFixed(2)}`);
    console.log(`   - Code Quality: ${(systemData.code.metrics.codeQuality * 100).toFixed(1)}%\n`);

    // Display architecture info
    console.log('🏗️ Architecture:');
    console.log(`   - Total Nodes: ${systemData.blueprint.architecture.nodes.length}`);
    console.log(`   - Total Edges: ${systemData.blueprint.architecture.edges.length}`);
    console.log(`   - Layout Algorithm: ${systemData.blueprint.layout.algorithm}\n`);

    // Display specifications
    console.log('📋 Specifications:');
    console.log(`   - Requirements: ${systemData.spec.specs.requirements.length}`);
    console.log(`   - Constraints: ${systemData.spec.specs.constraints.length}`);
    console.log(`   - Standards: ${systemData.spec.specs.standards.length}`);
    console.log(`   - Guidelines: ${systemData.spec.specs.guidelines.length}`);
    console.log(`   - Compliance Score: ${(systemData.spec.compliance.overallScore * 100).toFixed(1)}%\n`);

    // Display timeline info
    console.log('⏰ Timeline:');
    console.log(`   - Documentation Events: ${systemData.timeline.events.documentation.length}`);
    console.log(`   - Code Events: ${systemData.timeline.events.code.length}`);
    console.log(`   - Spec Events: ${systemData.timeline.events.spec.length}`);
    console.log(`   - System Events: ${systemData.timeline.events.system.length}\n`);

    // Subscribe to changes
    console.log('🔄 Setting up change notifications...');
    const unsubscribe = orchestrator.subscribeToChanges((data) => {
      console.log('📢 System data updated!');
      console.log(`   - Last updated: ${data.metadata.updatedAt}`);
    });

    // Simulate some changes
    console.log('🎭 Simulating changes...');
    
    // Add a timeline event
    const timelineService = orchestrator.getServices().timeline;
    const newEvent = timelineService.createEvent(
      'documentation_updated' as EventType,
      'cmc_system',
      'demo_session',
      {
        action: 'updated',
        details: {
          file: 'knowledge_architecture/systems/cmc/L1_overview.md',
          changes: ['Added new section', 'Updated metrics']
        },
        result: 'success'
      },
      {
        user: 'demo_user',
        system: 'cmc',
        environment: 'development',
        version: '1.0.0'
      }
    );

    await timelineService.addEvent(newEvent);
    console.log('✅ Added timeline event');

    // Update a node position in blueprint
    const blueprintService = orchestrator.getServices().blueprint;
    await blueprintService.updateNodePosition('cmc_system', { x: 500, y: 300 });
    console.log('✅ Updated node position');

    // Export system data
    console.log('\n📤 Exporting system data...');
    const jsonExport = await orchestrator.exportSystem('cmc', 'json');
    console.log(`✅ Exported to JSON (${jsonExport.length} characters)`);

    const graphmlExport = await orchestrator.exportSystem('cmc', 'graphml');
    console.log(`✅ Exported to GraphML (${graphmlExport.length} characters)`);

    const dotExport = await orchestrator.exportSystem('cmc', 'dot');
    console.log(`✅ Exported to DOT (${dotExport.length} characters)`);

    // Display final status
    console.log('\n🎉 Demo completed successfully!');
    console.log(`   - Loaded systems: ${orchestrator.listLoadedSystems().join(', ')}`);
    console.log(`   - Cache size: ${orchestrator.listLoadedSystems().length} systems`);

    // Cleanup
    unsubscribe();
    orchestrator.cleanup();
    console.log('🧹 Cleanup completed');

  } catch (error) {
    console.error('❌ Demo failed:', error);
  }
}

// Run the demo if this file is executed directly
if (require.main === module) {
  runDemo().catch(console.error);
}

export { runDemo };
