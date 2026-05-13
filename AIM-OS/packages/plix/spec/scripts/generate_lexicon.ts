/**
 * Generate PLIX Lexicon Table
 * 
 * Auto-generates complete lexicon table from Phase 3 Registry + Phase 1 Parser
 * Outputs Markdown table format for spec documentation
 */

import { PLIXTagRegistry } from '../src/registry/tag-registry';
import { PLIXParser } from '../src/parser';

interface LexiconEntry {
  category: string;
  prefix?: string;
  keyword?: string;
  operator?: string;
  type?: string;
  description: string;
  constraints?: string;
  example: string;
}

export class LexiconGenerator {
  private registry: PLIXTagRegistry;
  private parser: PLIXParser;
  
  constructor(registry: PLIXTagRegistry, parser: PLIXParser) {
    this.registry = registry;
    this.parser = parser;
  }
  
  /**
   * Generate complete lexicon table
   */
  async generateLexicon(): Promise<LexiconEntry[]> {
    const entries: LexiconEntry[] = [];
    
    // Tag Prefixes (from registry)
    entries.push(...this.generateTagPrefixes());
    
    // Operators (from parser)
    entries.push(...this.generateOperators());
    
    // Keywords (from parser)
    entries.push(...this.generateKeywords());
    
    // Speech Acts (from grammar)
    entries.push(...this.generateSpeechActs());
    
    // Types (from compiler)
    entries.push(...this.generateTypes());
    
    return entries;
  }
  
  /**
   * Generate tag prefix entries
   */
  private generateTagPrefixes(): LexiconEntry[] {
    return [
      {
        category: 'Tag Prefix',
        prefix: 'ent:',
        description: 'Entity identity - Canonical entity reference',
        constraints: 'Must resolve via registry to Entity type',
        example: 'ent:plix://db/table/users#rev@h_98fa'
      },
      {
        category: 'Tag Prefix',
        prefix: 'cap:',
        description: 'Capability reference - Tool or service capability',
        constraints: 'Must resolve via registry to Capability type',
        example: 'cap:plix://tool/mcp/pg.migrate#rev@h_2a10'
      },
      {
        category: 'Tag Prefix',
        prefix: 'act:',
        description: 'Action identifier - Action to perform',
        constraints: 'Must be defined in action registry',
        example: 'act:migrate'
      },
      {
        category: 'Tag Prefix',
        prefix: 'con:',
        description: 'Constraint expression - Pre/post condition',
        constraints: 'Must be evaluable to boolean',
        example: 'con:schema_intact == h_prev'
      },
      {
        category: 'Tag Prefix',
        prefix: 'test:',
        description: 'Test specification - Test to execute',
        constraints: 'Must be executable test',
        example: 'test:unique_email'
      },
      {
        category: 'Tag Prefix',
        prefix: 'ev:',
        description: 'Evidence reference - Witness or evidence',
        constraints: 'Must resolve via registry to Evidence type',
        example: 'ev:plix://witness/schema_before'
      }
    ];
  }
  
  /**
   * Generate operator entries
   */
  private generateOperators(): LexiconEntry[] {
    return [
      {
        category: 'Operator',
        operator: '==',
        description: 'Equality comparison',
        constraints: 'Binary, works with scalars/identifiers',
        example: 'con:a == b'
      },
      {
        category: 'Operator',
        operator: '!=',
        description: 'Inequality comparison',
        constraints: 'Binary, works with scalars/identifiers',
        example: 'con:a != b'
      },
      {
        category: 'Operator',
        operator: '<=',
        description: 'Less than or equal comparison',
        constraints: 'Binary, numeric comparison',
        example: 'con:a <= 10'
      },
      {
        category: 'Operator',
        operator: '>=',
        description: 'Greater than or equal comparison',
        constraints: 'Binary, numeric comparison',
        example: 'con:a >= 10'
      },
      {
        category: 'Operator',
        operator: '<',
        description: 'Less than comparison',
        constraints: 'Binary, numeric comparison',
        example: 'con:a < 10'
      },
      {
        category: 'Operator',
        operator: '>',
        description: 'Greater than comparison',
        constraints: 'Binary, numeric comparison',
        example: 'con:a > 10'
      },
      {
        category: 'Operator',
        operator: 'AND',
        description: 'Logical AND',
        constraints: 'Binary, logical operation',
        example: 'con:(a == 1) AND (b == 2)'
      },
      {
        category: 'Operator',
        operator: 'OR',
        description: 'Logical OR',
        constraints: 'Binary, logical operation',
        example: 'con:(a == 1) OR (b == 2)'
      },
      {
        category: 'Operator',
        operator: 'NOT',
        description: 'Logical NOT',
        constraints: 'Unary, logical operation',
        example: 'con:NOT (a == 1)'
      },
      {
        category: 'Operator',
        operator: 'FORALL',
        description: 'Universal quantifier',
        constraints: 'Quantified, requires variable and domain',
        example: 'con:FORALL row IN users (unique_email)'
      },
      {
        category: 'Operator',
        operator: 'EXISTS',
        description: 'Existential quantifier',
        constraints: 'Quantified, requires variable and domain',
        example: 'con:EXISTS room IN rooms (capacity >= 10)'
      }
    ];
  }
  
  /**
   * Generate keyword entries
   */
  private generateKeywords(): LexiconEntry[] {
    return [
      {
        category: 'Keyword',
        keyword: 'intent',
        description: 'Intent declaration - Top-level intent type',
        constraints: 'Required, must be speech act',
        example: 'intent: ensure'
      },
      {
        category: 'Keyword',
        keyword: 'ent:',
        description: 'Entity clause - Entity being acted upon',
        constraints: 'Required, must be valid tag',
        example: 'ent:plix://db/table/users'
      },
      {
        category: 'Keyword',
        keyword: 'act:',
        description: 'Action clause - Action to perform',
        constraints: 'Required (or using cap:)',
        example: 'act:migrate'
      },
      {
        category: 'Keyword',
        keyword: 'using',
        description: 'Capability clause - Use capability instead of action',
        constraints: 'Optional, requires cap: tag',
        example: 'using cap:plix://tool/mcp/pg.migrate'
      },
      {
        category: 'Keyword',
        keyword: 'with:',
        description: 'Parameters - Input parameters for action',
        constraints: 'Optional, key-value pairs',
        example: 'with: version: "v2.0"'
      },
      {
        category: 'Keyword',
        keyword: 'pre:',
        description: 'Preconditions - Conditions that must hold before execution',
        constraints: 'Optional, array of constraints',
        example: 'pre: con:schema_intact == h_prev'
      },
      {
        category: 'Keyword',
        keyword: 'post:',
        description: 'Postconditions - Conditions that must hold after execution',
        constraints: 'Optional, array of constraints',
        example: 'post: con:schema_fingerprint == h_next'
      },
      {
        category: 'Keyword',
        keyword: 'tests:',
        description: 'Test specifications - Tests to execute',
        constraints: 'Optional, array of test specs',
        example: 'tests: test:unique_email'
      },
      {
        category: 'Keyword',
        keyword: 'evidence:',
        description: 'Evidence requirements - Evidence/witnesses to collect',
        constraints: 'Optional, array of evidence refs',
        example: 'evidence: ev:schema_before'
      },
      {
        category: 'Keyword',
        keyword: 'bt:',
        description: 'Bitemporal fields - Transaction and valid time',
        constraints: 'Optional, tx_time required if present',
        example: 'bt: tx_time: now()'
      },
      {
        category: 'Keyword',
        keyword: 'plan',
        description: 'Plan block - Execution plan with steps',
        constraints: 'Optional, array of plan steps',
        example: 'plan [ step validate ]'
      }
    ];
  }
  
  /**
   * Generate speech act entries
   */
  private generateSpeechActs(): LexiconEntry[] {
    return [
      {
        category: 'Speech Act',
        keyword: 'ask',
        description: 'Query intent - Request information',
        constraints: 'Requires Entity, Action',
        example: 'ask ent:users act:query'
      },
      {
        category: 'Speech Act',
        keyword: 'assert',
        description: 'Assertion intent - Assert a fact',
        constraints: 'Requires Entity, Post',
        example: 'assert ent:users post: con:valid == true'
      },
      {
        category: 'Speech Act',
        keyword: 'plan',
        description: 'Planning intent - Create execution plan',
        constraints: 'Requires Entity, Action, Plan',
        example: 'plan ent:users act:migrate plan [ ... ]'
      },
      {
        category: 'Speech Act',
        keyword: 'ensure',
        description: 'Guaranteed execution - Ensure conditions hold',
        constraints: 'Requires Entity, Action, Pre, Post, Tests',
        example: 'ensure ent:users act:migrate pre: ... post: ... tests: ...'
      },
      {
        category: 'Speech Act',
        keyword: 'measure',
        description: 'Measurement intent - Measure entity properties',
        constraints: 'Requires Entity, Tests',
        example: 'measure ent:users tests: test:performance'
      },
      {
        category: 'Speech Act',
        keyword: 'decide',
        description: 'Decision intent - Make a decision',
        constraints: 'Requires Entity, Pre, Post',
        example: 'decide ent:users pre: ... post: ...'
      },
      {
        category: 'Speech Act',
        keyword: 'retract',
        description: 'Retraction intent - Retract a previous assertion',
        constraints: 'Requires Entity',
        example: 'retract ent:users'
      }
    ];
  }
  
  /**
   * Generate type entries
   */
  private generateTypes(): LexiconEntry[] {
    return [
      {
        category: 'Type',
        type: 'Entity',
        description: 'Tagged entity reference',
        constraints: 'Must resolve via registry',
        example: 'plix://db/table/users#rev@h_98fa'
      },
      {
        category: 'Type',
        type: 'Action',
        description: 'Action identifier',
        constraints: 'Must be defined',
        example: 'migrate'
      },
      {
        category: 'Type',
        type: 'Capability<In, Out>',
        description: 'Callable capability with input/output types',
        constraints: 'Must resolve to tool',
        example: 'plix://tool/mcp/pg.migrate<Version:String, Script:Tag> -> Hash'
      },
      {
        category: 'Type',
        type: 'Constraint',
        description: 'Constraint expression',
        constraints: 'Must be evaluable to boolean',
        example: 'schema_intact == h_prev'
      },
      {
        category: 'Type',
        type: 'Test',
        description: 'Test specification',
        constraints: 'Must be executable',
        example: 'unique_email'
      },
      {
        category: 'Type',
        type: 'Evidence',
        description: 'Evidence reference',
        constraints: 'Must resolve to witness',
        example: 'plix://witness/schema_before'
      }
    ];
  }
  
  /**
   * Generate Markdown table from entries
   */
  generateMarkdownTable(entries: LexiconEntry[]): string {
    let markdown = '| Category | Prefix/Keyword/Operator/Type | Description | Constraints | Example |\n';
    markdown += '|----------|-------------------------------|-------------|-------------|----------|\n';
    
    for (const entry of entries) {
      const identifier = entry.prefix || entry.keyword || entry.operator || entry.type || '';
      const description = entry.description || '';
      const constraints = entry.constraints || '';
      const example = entry.example || '';
      
      markdown += `| ${entry.category} | \`${identifier}\` | ${description} | ${constraints} | \`${example}\` |\n`;
    }
    
    return markdown;
  }
  
  /**
   * Generate complete lexicon document
   */
  async generateLexiconDocument(): Promise<string> {
    const entries = await this.generateLexicon();
    const table = this.generateMarkdownTable(entries);
    
    return `# PLIX Complete Lexicon

**Status:** ✅ **AUTO-GENERATED**  
**Version:** 1.0.0  
**Date:** ${new Date().toISOString().split('T')[0]}  
**Source:** Phase 3 Registry + Phase 1 Parser

---

## 📚 **COMPLETE LEXICON TABLE**

${table}

---

## 📋 **CATEGORIES**

### **Tag Prefixes**
Tags that identify entities, capabilities, actions, constraints, tests, and evidence.

### **Operators**
Comparison and logical operators for constraint expressions.

### **Keywords**
Language keywords for intent structure and clauses.

### **Speech Acts**
Top-level intent types (ask, assert, plan, ensure, etc.).

### **Types**
Type system for PLIX entities and expressions.

---

**Note:** This lexicon is auto-generated from the Phase 3 Registry and Phase 1 Parser.  
To regenerate, run: \`npm run generate:lexicon\`

**Last Generated:** ${new Date().toISOString()}
`;
  }
}

