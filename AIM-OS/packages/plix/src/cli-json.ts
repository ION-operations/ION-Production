/**
 * PLIx CLI - JSON Output Mode
 * 
 * Provides machine-readable JSON output for integration with Python APOE
 */

import { PLIXParser } from './parser';
import * as fs from 'fs';

export interface CLIResult {
  success: boolean;
  intent?: any;
  errors?: Array<{
    line: number;
    column: number;
    message: string;
    code: string;
  }>;
  warnings?: Array<{
    line: number;
    column: number;
    message: string;
  }>;
  metadata?: {
    parse_time_ms: number;
    source_hash: string;
  };
}

export async function parseJSON(input: string): Promise<CLIResult> {
  const parser = new PLIXParser();
  const startTime = Date.now();
  
  try {
    const result = parser.parse(input);
    const parseTime = Date.now() - startTime;
    
    if (result.errors.length > 0) {
      return {
        success: false,
        errors: result.errors.map(e => ({
          line: e.line,
          column: e.column || 0,
          message: e.message,
          code: e.type || 'PARSE_ERROR'
        })),
        warnings: result.warnings?.map(w => ({
          line: w.line,
          column: w.column || 0,
          message: w.message
        })),
        metadata: {
          parse_time_ms: parseTime,
          source_hash: hashString(input)
        }
      };
    }
    
    return {
      success: true,
      intent: result.intent,
      warnings: result.warnings?.map(w => ({
        line: w.line,
        column: w.column || 0,
        message: w.message
      })),
      metadata: {
        parse_time_ms: parseTime,
        source_hash: hashString(input)
      }
    };
  } catch (error: any) {
    return {
      success: false,
      errors: [{
        line: 0,
        column: 0,
        message: error.message || 'Unknown error',
        code: 'INTERNAL_ERROR'
      }],
      metadata: {
        parse_time_ms: Date.now() - startTime,
        source_hash: hashString(input)
      }
    };
  }
}

function hashString(input: string): string {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(input).digest('hex');
}

// CLI entry point for JSON mode
export async function main() {
  const args = process.argv.slice(2);
  
  if (!args.includes('--json')) {
    console.error('Usage: plix-json --json < input.plix');
    process.exit(1);
  }
  
  // Read from stdin or file
  let input = '';
  
  if (args.includes('-')) {
    // Read from stdin
    input = fs.readFileSync(0, 'utf-8');
  } else {
    // Read from file
    const filename = args.find(a => !a.startsWith('--'));
    if (!filename) {
      console.error('No input file specified');
      process.exit(1);
    }
    input = fs.readFileSync(filename, 'utf-8');
  }
  
  const result = await parseJSON(input);
  console.log(JSON.stringify(result, null, 2));
  
  process.exit(result.success ? 0 : 1);
}

// Run if executed directly
if (require.main === module) {
  main().catch(error => {
    console.error(JSON.stringify({
      success: false,
      errors: [{
        line: 0,
        column: 0,
        message: error.message,
        code: 'FATAL_ERROR'
      }]
    }));
    process.exit(1);
  });
}

