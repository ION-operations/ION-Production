/**
 * PLIX Phase 2 Integration Examples
 * 
 * Examples of compiling PLIX to AIP graph and APOE execution plans
 */

import { PLIXParser } from '../parser';
import { PLIXToAIPCompiler } from '../compiler/aip-compiler';
import type { PLIxIntent } from '../models/schema';

/**
 * Example 1: Basic PLIX → AIP Graph Compilation
 */
export async function example1_BasicCompilation() {
  const plixText = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:schema_intact == h_prev
    con:rowcount_stable <= 0
  post:
    con:schema_fingerprint == h_next
  evidence:
    w:pg.schema_fingerprint_before
    w:pg.schema_fingerprint_after
`;

  // Parse PLIX
  const parser = new PLIXParser();
  const parseResult = parser.parse(plixText);
  
  if (!parseResult.intent) {
    throw new Error('Parse failed');
  }
  
  // Compile to AIP graph
  const compiler = new PLIXToAIPCompiler();
  const aipGraph = await compiler.compileToAIPGraph(parseResult.intent);
  
  console.log('AIP Graph Nodes:', aipGraph.nodes.length);
  console.log('AIP Graph Edges:', aipGraph.edges.length);
  
  return aipGraph;
}

/**
 * Example 2: PLIX → APOE Execution Plan Compilation
 */
export async function example2_APOECompilation() {
  const plixText = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
  post:
    con:schema_fingerprint == h_next
  plan [
    step validate_preconditions
      on_error: constraint.violated -> fail
    step reserve_room
      retry 3 backoff exponential(100ms, 2s) jitter
      on_error: net.timeout -> retry with retry(3, 100ms, 2s)
      on_error: policy.denied -> escalate(admin)
      compensate release_room
  ]
`;

  // Parse PLIX
  const parser = new PLIXParser();
  const parseResult = parser.parse(plixText);
  
  if (!parseResult.intent) {
    throw new Error('Parse failed');
  }
  
  // Compile to APOE
  const compiler = new PLIXToAIPCompiler();
  const apoeResult = await compiler.compileToAPOE(parseResult.intent);
  
  console.log('APOE Plan:', apoeResult.plan.name);
  console.log('Steps:', apoeResult.plan.steps.length);
  console.log('Witness Requirements:', apoeResult.witnessRequirements.length);
  
  return apoeResult;
}

/**
 * Example 3: Tag Resolution via HHNI/SEG
 */
export async function example3_TagResolution() {
  const compiler = new PLIXToAIPCompiler({
    // In production, these would be actual client instances
    // hhniClient: new HHNIClient(),
    // segClient: new SEGClient(),
    // cmcClient: new CMCClient()
  });
  
  const tags = [
    'plix://db/table/users#rev@h_98fa',
    'plix://tool/mcp/pg.migrate#rev@h_2a10',
    'plix://witness/schema_before',
    'plix://witness/schema_after'
  ];
  
  const resolutions = await Promise.all(
    tags.map(tag => compiler.resolveTag(tag))
  );
  
  console.log('Tag Resolutions:');
  resolutions.forEach((result, i) => {
    console.log(`  ${tags[i]}: ${result.source} (confidence: ${result.confidence})`);
  });
  
  return resolutions;
}

/**
 * Example 4: VIF Witness Requirements Generation
 */
export async function example4_WitnessRequirements() {
  const plixText = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:schema_intact == h_prev
  post:
    con:schema_fingerprint == h_next
  evidence:
    w:pg.schema_fingerprint_before
    w:pg.schema_fingerprint_after
  plan [
    step validate_preconditions
      confidence_threshold: 0.90
      evidence_required: [schema_before]
    step migrate_schema
      depends_on: [validate_preconditions]
      confidence_threshold: 0.85
      evidence_required: [schema_after]
  ]
`;

  // Parse PLIX
  const parser = new PLIXParser();
  const parseResult = parser.parse(plixText);
  
  if (!parseResult.intent) {
    throw new Error('Parse failed');
  }
  
  // Generate witness requirements
  const compiler = new PLIXToAIPCompiler();
  const requirements = compiler.generateWitnessRequirements(parseResult.intent);
  
  console.log('Witness Requirements:');
  requirements.forEach(req => {
    console.log(`  ${req.operation}:`);
    console.log(`    Confidence: ${req.requiredConfidence}`);
    console.log(`    Evidence: ${req.evidenceTypes.join(', ')}`);
  });
  
  return requirements;
}

/**
 * Example 5: Full Pipeline (PLIX → AIP → APOE → VIF)
 */
export async function example5_FullPipeline() {
  const plixText = `
ensure ent:plix://db/table/users#rev@h_98fa
  act:migrate using cap:plix://tool/mcp/pg.migrate#rev@h_2a10
  pre:
    con:(schema_intact == h_prev) AND (rowcount_stable <= 0)
    con:forall_rows unique_email
  post:
    con:schema_fingerprint == h_next
    con:eventually_true(room_reserved, within_ms=5000)
  evidence:
    w:pg.schema_fingerprint_before
    w:pg.schema_fingerprint_after
  plan [
    step validate_preconditions
      on_error: constraint.violated -> fail
      confidence_threshold: 0.90
    step migrate_schema
      depends_on: [validate_preconditions]
      retry 3 backoff exponential(100ms, 2s) jitter
      on_error: net.timeout -> retry with retry(3, 100ms, 2s)
      on_error: policy.denied -> escalate(admin)
      compensate rollback_migration
      confidence_threshold: 0.85
  ]
`;

  // Step 1: Parse PLIX
  const parser = new PLIXParser();
  const parseResult = parser.parse(plixText);
  
  if (!parseResult.intent) {
    throw new Error(`Parse failed: ${parseResult.errors.map(e => e.message).join(', ')}`);
  }
  
  // Step 2: Compile to AIP graph
  const compiler = new PLIXToAIPCompiler();
  const aipGraph = await compiler.compileToAIPGraph(parseResult.intent);
  
  // Step 3: Compile to APOE execution plan
  const apoeResult = await compiler.compileToAPOE(parseResult.intent);
  
  // Step 4: Generate VIF witness requirements
  const witnessRequirements = compiler.generateWitnessRequirements(parseResult.intent);
  
  return {
    parsedIntent: parseResult.intent,
    aipGraph,
    apoePlan: apoeResult.plan,
    witnessRequirements,
    resolvedTags: apoeResult.resolvedTags,
    errors: parseResult.errors,
    warnings: parseResult.warnings
  };
}

