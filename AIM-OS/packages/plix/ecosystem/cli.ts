/**
 * PLIx CLI Tool
 * 
 * Command-line interface for PLIx operations
 */

import { PLIXParser, Pipeline } from '../src';
import * as fs from 'fs';
import * as path from 'path';

/**
 * CLI Commands
 */
export class PLIxCLI {
  /**
   * Parse command: plix parse <file>
   */
  async parse(filePath: string): Promise<void> {
    const text = fs.readFileSync(filePath, 'utf-8');
    const parser = new PLIXParser();
    const result = parser.parse(text);
    
    if (result.errors.length > 0) {
      console.error('Parse errors:');
      for (const error of result.errors) {
        console.error(`  Line ${error.line}: ${error.message}`);
      }
      process.exit(1);
    }
    
    console.log('✅ Parse successful');
    console.log(JSON.stringify(result.intent, null, 2));
  }
  
  /**
   * Compile command: plix compile <file> [--target tla|alloy|opa|irplan]
   */
  async compile(filePath: string, target: string = 'irplan'): Promise<void> {
    const text = fs.readFileSync(filePath, 'utf-8');
    const result = await Pipeline.parseAndCompile(text);
    
    if (result.errors.length > 0) {
      console.error('Compilation errors:');
      for (const error of result.errors) {
        console.error(`  ${error}`);
      }
      process.exit(1);
    }
    
    console.log(`✅ Compiled to ${target}`);
    
    // Output based on target
    const outputPath = filePath.replace(/\.plix$/, `.${target}`);
    fs.writeFileSync(outputPath, JSON.stringify(result.aipGraph, null, 2));
    
    console.log(`Output written to ${outputPath}`);
  }
  
  /**
   * Validate command: plix validate <file>
   */
  async validate(filePath: string): Promise<void> {
    const text = fs.readFileSync(filePath, 'utf-8');
    const result = await Pipeline.validate(text);
    
    if (!result.valid) {
      console.error('Validation errors:');
      for (const error of result.errors) {
        console.error(`  ${error}`);
      }
      process.exit(1);
    }
    
    if (result.warnings.length > 0) {
      console.warn('Warnings:');
      for (const warning of result.warnings) {
        console.warn(`  ${warning}`);
      }
    }
    
    console.log('✅ Validation passed');
  }
  
  /**
   * Execute command: plix execute <file>
   */
  async execute(filePath: string): Promise<void> {
    const text = fs.readFileSync(filePath, 'utf-8');
    const result = await Pipeline.executeFullPipeline(text);
    
    if (!result.success) {
      console.error('Execution failed:');
      for (const error of result.errors) {
        console.error(`  ${error}`);
      }
      process.exit(1);
    }
    
    console.log('✅ Execution successful');
    console.log(`Duration: ${result.metadata.durationMs}ms`);
    console.log(`Stages: ${result.metadata.stages.join(' → ')}`);
  }
  
  /**
   * Init command: plix init
   */
  init(): void {
    const template = `# Example PLIx Intent

ask ent:plix://example/entity
  act:example_action
  requires
    con:precondition == true
  ensures
    con:postcondition == true
  plan [
    task step1 := api.action()
  ]
`;
    
    fs.writeFileSync('example.plix', template);
    console.log('✅ Created example.plix');
  }
}

/**
 * Main CLI entry point
 */
export function main(args: string[]): void {
  const cli = new PLIxCLI();
  const command = args[2];
  const filePath = args[3];
  const options = args.slice(4);
  
  switch (command) {
    case 'parse':
      cli.parse(filePath);
      break;
    case 'compile':
      const target = options.find(o => o.startsWith('--target='))?.split('=')[1] || 'irplan';
      cli.compile(filePath, target);
      break;
    case 'validate':
      cli.validate(filePath);
      break;
    case 'execute':
      cli.execute(filePath);
      break;
    case 'init':
      cli.init();
      break;
    default:
      console.log('Usage: plix <command> [options]');
      console.log('Commands:');
      console.log('  parse <file>      Parse PLIx file');
      console.log('  compile <file>    Compile PLIx to target');
      console.log('  validate <file>   Validate PLIx intent');
      console.log('  execute <file>    Execute PLIx intent');
      console.log('  init              Create example PLIx file');
  }
}

