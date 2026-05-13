/**
 * PLIx Integration Bridge
 * 
 * Connects parser → compiler → interpreter → verifier pipeline
 * Provides end-to-end execution and verification
 */

import { PLIXParser, type ParseResult } from '../parser/index';
import { PLIXToAIPCompiler, type AIPGraph, type APOECompilationResult } from '../compiler/aip-compiler';
import { AnnotatedTypeChecker, EffectValidator, type TypeJudgment } from '../semantics/annotated-typing';
import { Plan as PlanSemantics, type Dist } from '../semantics/subdistribution';

/**
 * Pipeline Configuration
 */
export interface PipelineConfig {
  /** Parser options */
  parser?: {
    strict?: boolean;
    allowDelimiters?: boolean;
  };
  
  /** Compiler options */
  compiler?: {
    hhniClient?: any;
    segClient?: any;
    cmcClient?: any;
    tagRegistry?: any;
  };
  
  /** Validation options */
  validation?: {
    enableTypeChecking?: boolean;
    enableEffectChecking?: boolean;
    contextId?: string;
    policyId?: string;
  };
  
  /** Runtime options */
  runtime?: {
    enableInterpreter?: boolean;
    enableVerifier?: boolean;
  };
}

/**
 * Pipeline Result
 */
export interface PipelineResult {
  /** Success flag */
  success: boolean;
  
  /** Parse result */
  parse?: {
    intent: any;
    errors: any[];
    warnings: any[];
  };
  
  /** Type checking result */
  typeCheck?: {
    judgment: TypeJudgment;
    valid: boolean;
    errors: string[];
  };
  
  /** Effect checking result */
  effectCheck?: {
    valid: boolean;
    errors: string[];
    warnings: string[];
  };
  
  /** Compilation result */
  compile?: {
    aipGraph: AIPGraph;
    apoeP: APOECompilationResult;
    errors: string[];
    warnings: string[];
  };
  
  /** Interpretation result */
  interpret?: {
    finalState: any;
    evidenceLog: any[];
    errors: string[];
  };
  
  /** Verification result */
  verify?: {
    passed: boolean;
    errors: string[];
    evidenceValid: boolean;
  };
  
  /** Overall errors */
  errors: string[];
  
  /** Overall warnings */
  warnings: string[];
  
  /** Pipeline metadata */
  metadata: {
    startTime: number;
    endTime: number;
    durationMs: number;
    stages: string[];
  };
}

/**
 * PLIx Integration Bridge
 * 
 * Main entry point for end-to-end pipeline execution
 */
export class PLIxIntegrationBridge {
  private config: PipelineConfig;
  private parser: PLIXParser;
  private compiler: PLIXToAIPCompiler;
  private typeChecker: AnnotatedTypeChecker;
  private effectValidator: EffectValidator;
  
  constructor(config: PipelineConfig = {}) {
    this.config = config;
    this.parser = new PLIXParser(config.parser);
    this.compiler = new PLIXToAIPCompiler(config.compiler);
    this.typeChecker = new AnnotatedTypeChecker();
    this.effectValidator = new EffectValidator();
    
    // Register default context and policy if needed
    if (config.validation?.contextId) {
      this.effectValidator.getEffectChecker().registerContext(
        config.validation.contextId,
        { io: true, net: true, db: true } // Default: allow all
      );
    }
    
    if (config.validation?.policyId) {
      this.effectValidator.getPolicyEngine().registerPolicy(
        config.validation.policyId,
        {
          allowed: ['io', 'net', 'db'],
          prohibited: [],
          requiresApproval: ['compensable']
        }
      );
    }
  }
  
  /**
   * Execute full pipeline: parse → type check → effect check → compile → interpret → verify
   */
  async execute(plixText: string): Promise<PipelineResult> {
    const startTime = Date.now();
    const stages: string[] = [];
    const allErrors: string[] = [];
    const allWarnings: string[] = [];
    
    const result: PipelineResult = {
      success: false,
      errors: [],
      warnings: [],
      metadata: {
        startTime,
        endTime: 0,
        durationMs: 0,
        stages: []
      }
    };
    
    try {
      // Stage 1: Parse
      stages.push('parse');
      const parseResult = this.parser.parse(plixText);
      
      result.parse = {
        intent: parseResult.intent,
        errors: parseResult.errors,
        warnings: parseResult.warnings
      };
      
      if (parseResult.errors.length > 0) {
        allErrors.push(...parseResult.errors.map(e => `Parse error: ${e.message}`));
      }
      
      allWarnings.push(...parseResult.warnings.map(w => `Parse warning: ${w.message}`));
      
      if (!parseResult.intent) {
        result.success = false;
        result.errors = allErrors;
        result.warnings = allWarnings;
        return this.finalizeResult(result, startTime, stages);
      }
      
      // Stage 2: Type Check (if enabled)
      if (this.config.validation?.enableTypeChecking !== false) {
        stages.push('typeCheck');
        
        try {
          const typeJudgment = this.typeChecker.check(
            this.typeChecker['context'] || require('../semantics/annotated-typing').TypingContext.prototype.constructor(),
            parseResult.intent
          );
          
          result.typeCheck = {
            judgment: typeJudgment,
            valid: true,
            errors: []
          };
        } catch (error: any) {
          result.typeCheck = {
            judgment: {} as TypeJudgment,
            valid: false,
            errors: [error.message]
          };
          
          allErrors.push(`Type check error: ${error.message}`);
        }
      }
      
      // Stage 3: Effect Check (if enabled)
      if (this.config.validation?.enableEffectChecking !== false && 
          this.config.validation?.contextId && 
          this.config.validation?.policyId) {
        stages.push('effectCheck');
        
        const effectResult = this.effectValidator.validateIntent(
          parseResult.intent,
          this.config.validation.contextId,
          this.config.validation.policyId
        );
        
        result.effectCheck = effectResult;
        
        if (!effectResult.valid) {
          allErrors.push(...effectResult.errors.map(e => `Effect check error: ${e}`));
        }
        
        allWarnings.push(...effectResult.warnings.map(w => `Effect check warning: ${w}`));
      }
      
      // Stage 4: Compile to AIP/APOE
      stages.push('compile');
      
      const aipGraph = await this.compiler.compileToAIPGraph(parseResult.intent);
      const apoeCompilation = await this.compiler.compileToAPOE(parseResult.intent);
      
      result.compile = {
        aipGraph,
        apoeP: apoeCompilation,
        errors: apoeCompilation.errors,
        warnings: apoeCompilation.warnings
      };
      
      allErrors.push(...apoeCompilation.errors.map(e => `Compile error: ${e}`));
      allWarnings.push(...apoeCompilation.warnings.map(w => `Compile warning: ${w}`));
      
      // Stage 5: Interpret (if enabled)
      if (this.config.runtime?.enableInterpreter) {
        stages.push('interpret');
        
        // Note: Would integrate with ref-interpreter here
        // For now, mark as placeholder
        result.interpret = {
          finalState: { placeholder: true },
          evidenceLog: [],
          errors: ['Interpreter integration pending']
        };
        
        allWarnings.push('Interpreter integration pending');
      }
      
      // Stage 6: Verify (if enabled)
      if (this.config.runtime?.enableVerifier) {
        stages.push('verify');
        
        // Note: Would integrate with verifier here
        // For now, mark as placeholder
        result.verify = {
          passed: false,
          errors: ['Verifier integration pending'],
          evidenceValid: false
        };
        
        allWarnings.push('Verifier integration pending');
      }
      
      // Success if no errors
      result.success = allErrors.length === 0;
      
    } catch (error: any) {
      allErrors.push(`Pipeline error: ${error.message}`);
      result.success = false;
    }
    
    result.errors = allErrors;
    result.warnings = allWarnings;
    
    return this.finalizeResult(result, startTime, stages);
  }
  
  /**
   * Finalize result with metadata
   */
  private finalizeResult(result: PipelineResult, startTime: number, stages: string[]): PipelineResult {
    const endTime = Date.now();
    
    result.metadata = {
      startTime,
      endTime,
      durationMs: endTime - startTime,
      stages
    };
    
    return result;
  }
  
  /**
   * Execute just parse → compile (no runtime)
   */
  async compileOnly(plixText: string): Promise<PipelineResult> {
    const config = {
      ...this.config,
      runtime: {
        enableInterpreter: false,
        enableVerifier: false
      }
    };
    
    const bridge = new PLIxIntegrationBridge(config);
    return bridge.execute(plixText);
  }
  
  /**
   * Execute with validation only (no runtime)
   */
  async validateOnly(plixText: string): Promise<PipelineResult> {
    const config = {
      ...this.config,
      validation: {
        ...this.config.validation,
        enableTypeChecking: true,
        enableEffectChecking: true
      },
      runtime: {
        enableInterpreter: false,
        enableVerifier: false
      }
    };
    
    const bridge = new PLIxIntegrationBridge(config);
    return bridge.execute(plixText);
  }
}

/**
 * Convenience functions for common pipeline operations
 */
export const Pipeline = {
  /**
   * Parse and compile PLIX text to AIP graph
   */
  async parseAndCompile(plixText: string): Promise<{ aipGraph: AIPGraph | null; errors: string[] }> {
    const bridge = new PLIxIntegrationBridge();
    const result = await bridge.compileOnly(plixText);
    
    return {
      aipGraph: result.compile?.aipGraph || null,
      errors: result.errors
    };
  },
  
  /**
   * Validate PLIX text (parse + type check + effect check)
   */
  async validate(plixText: string, contextId: string = 'default', policyId: string = 'default'): Promise<{ valid: boolean; errors: string[]; warnings: string[] }> {
    const bridge = new PLIxIntegrationBridge({
      validation: {
        enableTypeChecking: true,
        enableEffectChecking: true,
        contextId,
        policyId
      }
    });
    
    const result = await bridge.validateOnly(plixText);
    
    return {
      valid: result.success,
      errors: result.errors,
      warnings: result.warnings
    };
  },
  
  /**
   * Execute full pipeline (all stages)
   */
  async executeFullPipeline(plixText: string): Promise<PipelineResult> {
    const bridge = new PLIxIntegrationBridge({
      validation: {
        enableTypeChecking: true,
        enableEffectChecking: true,
        contextId: 'default',
        policyId: 'default'
      },
      runtime: {
        enableInterpreter: true,
        enableVerifier: true
      }
    });
    
    return bridge.execute(plixText);
  }
};

