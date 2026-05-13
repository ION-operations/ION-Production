/**
 * Code Validation Service
 * Provides code validation and quality checks
 * Integrates with ICIP and VIF for quality gates
 */

import { mcpService } from './MCPService'
import { CodeValidationResult } from './ICIPService'

export interface ValidationRequest {
  code: string
  language: string
  validationTypes?: ValidationType[]
}

export type ValidationType = 'syntax' | 'quality' | 'security' | 'style' | 'performance'

export interface SecurityIssue {
  type: 'dangerous_pattern' | 'vulnerability' | 'injection_risk' | 'resource_exhaustion' | 'other'
  severity: 'low' | 'medium' | 'high' | 'critical'
  message: string
  location?: {
    line: number
    column: number
  }
  suggestion?: string
}

export interface QualityIssue {
  type: 'complexity' | 'maintainability' | 'readability' | 'test_coverage' | 'documentation' | 'other'
  severity: 'low' | 'medium' | 'high'
  message: string
  location?: {
    line: number
    column: number
  }
  suggestion?: string
}

export interface ValidationResult extends CodeValidationResult {
  securityIssues: SecurityIssue[]
  qualityIssues: QualityIssue[]
  passed: boolean  // All validation types passed
}

/**
 * Code Validation Service
 * Validates code syntax, quality, security, and style
 */
export class CodeValidationService {
  /**
   * Validate code with multiple validation types
   */
  async validate(
    request: ValidationRequest
  ): Promise<{ success: boolean; result?: ValidationResult; error?: string }> {
    try {
      const validationTypes = request.validationTypes || ['syntax', 'quality', 'security']
      
      const results: Partial<ValidationResult> = {
        valid: true,
        errors: [],
        warnings: [],
        quality_metrics: {},
        confidence: 1.0,
        securityIssues: [],
        qualityIssues: []
      }

      // Run all validation types
      for (const type of validationTypes) {
        const typeResult = await this.validateByType(request.code, request.language, type)
        
        if (!typeResult.valid) {
          results.valid = false
        }

        // Merge errors and warnings
        if (typeResult.errors) {
          results.errors = [...(results.errors || []), ...typeResult.errors]
        }
        if (typeResult.warnings) {
          results.warnings = [...(results.warnings || []), ...typeResult.warnings]
        }

        // Merge security issues
        if (typeResult.securityIssues) {
          results.securityIssues = [...(results.securityIssues || []), ...typeResult.securityIssues]
        }

        // Merge quality issues
        if (typeResult.qualityIssues) {
          results.qualityIssues = [...(results.qualityIssues || []), ...typeResult.qualityIssues]
        }

        // Merge quality metrics
        if (typeResult.quality_metrics) {
          results.quality_metrics = {
            ...results.quality_metrics,
            ...typeResult.quality_metrics
          }
        }

        // Update confidence (lowest confidence from all validations)
        if (typeResult.confidence !== undefined) {
          results.confidence = Math.min(results.confidence || 1.0, typeResult.confidence)
        }
      }

      const finalResult: ValidationResult = {
        ...results as CodeValidationResult,
        securityIssues: results.securityIssues || [],
        qualityIssues: results.qualityIssues || [],
        passed: results.valid && (results.errors?.length || 0) === 0
      }

      return {
        success: true,
        result: finalResult
      }
    } catch (error) {
      console.error('Code validation error:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Validate code by specific type
   */
  async validateByType(
    code: string,
    language: string,
    type: ValidationType
  ): Promise<Partial<ValidationResult>> {
    switch (type) {
      case 'syntax':
        return this.validateSyntax(code, language)
      case 'quality':
        return this.validateQuality(code, language)
      case 'security':
        return this.validateSecurity(code, language)
      case 'style':
        return this.validateStyle(code, language)
      case 'performance':
        return this.validatePerformance(code, language)
      default:
        return { valid: true, confidence: 1.0 }
    }
  }

  /**
   * Validate syntax
   */
  private async validateSyntax(
    code: string,
    language: string
  ): Promise<Partial<ValidationResult>> {
    try {
      // Basic syntax validation
      // TODO: Integrate with language-specific syntax checkers
      
      // For now, basic checks
      const errors: Array<{
        type: 'syntax' | 'quality' | 'security' | 'other'
        message: string
        severity: 'low' | 'medium' | 'high' | 'critical'
      }> = []

      // Check for basic syntax issues
      if (language === 'typescript' || language === 'javascript') {
        // Check for unclosed brackets
        const openBrackets = (code.match(/\{/g) || []).length
        const closeBrackets = (code.match(/\}/g) || []).length
        if (openBrackets !== closeBrackets) {
          errors.push({
            type: 'syntax',
            message: `Unclosed brackets: ${openBrackets} open, ${closeBrackets} close`,
            severity: 'critical'
          })
        }

        // Check for unclosed parentheses
        const openParens = (code.match(/\(/g) || []).length
        const closeParens = (code.match(/\)/g) || []).length
        if (openParens !== closeParens) {
          errors.push({
            type: 'syntax',
            message: `Unclosed parentheses: ${openParens} open, ${closeParens} close`,
            severity: 'critical'
          })
        }
      }

      return {
        valid: errors.length === 0,
        errors: errors,
        warnings: [],
        confidence: errors.length === 0 ? 0.95 : 0.5
      }
    } catch (error) {
      return {
        valid: false,
        errors: [{
          type: 'syntax',
          message: error instanceof Error ? error.message : 'Syntax validation error',
          severity: 'critical'
        }],
        confidence: 0.3
      }
    }
  }

  /**
   * Validate quality
   */
  private async validateQuality(
    code: string,
    language: string
  ): Promise<Partial<ValidationResult>> {
    try {
      const qualityIssues: QualityIssue[] = []
      const qualityMetrics: {
        complexity?: number
        maintainability?: number
        test_coverage?: number
      } = {}

      // Calculate code complexity (basic)
      const lines = code.split('\n').length
      const complexity = Math.min(1.0, lines / 100) // Simple line-based complexity
      qualityMetrics.complexity = complexity

      // Check for high complexity
      if (lines > 200) {
        qualityIssues.push({
          type: 'complexity',
          severity: 'medium',
          message: `Code is long (${lines} lines). Consider breaking into smaller functions.`,
          suggestion: 'Split into smaller, focused functions'
        })
      }

      // Check for comments (basic maintainability check)
      const commentLines = (code.match(/\/\//g) || []).length + (code.match(/\/\*/g) || []).length
      const commentRatio = commentLines / Math.max(1, lines)
      
      if (commentRatio < 0.1) {
        qualityIssues.push({
          type: 'documentation',
          severity: 'low',
          message: 'Low comment ratio. Consider adding more documentation.',
          suggestion: 'Add inline comments and documentation'
        })
      }

      qualityMetrics.maintainability = Math.min(1.0, 0.7 + commentRatio * 0.3)

      return {
        valid: true,
        qualityIssues,
        quality_metrics: qualityMetrics,
        confidence: 0.85
      }
    } catch (error) {
      return {
        valid: true,
        qualityIssues: [],
        quality_metrics: {},
        confidence: 0.7
      }
    }
  }

  /**
   * Validate security
   */
  private async validateSecurity(
    code: string,
    language: string
  ): Promise<Partial<ValidationResult>> {
    try {
      const securityIssues: SecurityIssue[] = []

      // Dangerous patterns (comprehensive)
      const dangerousPatterns: Array<{
        pattern: RegExp
        type: SecurityIssue['type']
        severity: SecurityIssue['severity']
        message: string
        suggestion: string
      }> = [
        {
          pattern: /eval\s*\(/,
          type: 'dangerous_pattern',
          severity: 'critical',
          message: 'Use of eval() detected - high security risk',
          suggestion: 'Avoid eval(). Use safer alternatives like JSON.parse() or structured data.'
        },
        {
          pattern: /Function\s*\(/,
          type: 'dangerous_pattern',
          severity: 'critical',
          message: 'Use of Function() constructor detected - security risk',
          suggestion: 'Avoid Function() constructor. Use standard functions instead.'
        },
        {
          pattern: /require\s*\(['"]fs['"]/,
          type: 'vulnerability',
          severity: 'high',
          message: 'File system access detected',
          suggestion: 'File system access should be restricted in sandboxed code.'
        },
        {
          pattern: /import\s+.*fs|from\s+['"]fs['"]/,
          type: 'vulnerability',
          severity: 'high',
          message: 'File system module import detected',
          suggestion: 'File system access should be restricted in sandboxed code.'
        },
        {
          pattern: /process\.exit/,
          type: 'dangerous_pattern',
          severity: 'medium',
          message: 'process.exit() detected',
          suggestion: 'Avoid process.exit() in application code.'
        },
        {
          pattern: /child_process/,
          type: 'vulnerability',
          severity: 'critical',
          message: 'Child process execution detected - critical security risk',
          suggestion: 'Child process execution is not allowed in sandboxed code.'
        },
        {
          pattern: /exec\s*\(|spawn\s*\(/,
          type: 'vulnerability',
          severity: 'critical',
          message: 'Command execution detected - critical security risk',
          suggestion: 'Command execution is not allowed in sandboxed code.'
        },
        {
          pattern: /innerHTML\s*=/,
          type: 'injection_risk',
          severity: 'high',
          message: 'innerHTML assignment detected - XSS risk',
          suggestion: 'Use textContent or proper sanitization instead of innerHTML.'
        },
        {
          pattern: /dangerouslySetInnerHTML/,
          type: 'injection_risk',
          severity: 'high',
          message: 'dangerouslySetInnerHTML detected - XSS risk',
          suggestion: 'Avoid dangerouslySetInnerHTML. Use safe React patterns instead.'
        },
        {
          pattern: /while\s*\(true\)|for\s*\(\s*;\s*;\s*\)/,
          type: 'resource_exhaustion',
          severity: 'medium',
          message: 'Infinite loop pattern detected',
          suggestion: 'Add loop termination conditions to prevent resource exhaustion.'
        }
      ]

      // Check for dangerous patterns
      const lines = code.split('\n')
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        for (const check of dangerousPatterns) {
          if (check.pattern.test(line)) {
            securityIssues.push({
              type: check.type,
              severity: check.severity,
              message: check.message,
              location: {
                line: i + 1,
                column: 0
              },
              suggestion: check.suggestion
            })
          }
        }
      }

      const hasCritical = securityIssues.some(issue => issue.severity === 'critical')
      const hasHigh = securityIssues.some(issue => issue.severity === 'high')

      return {
        valid: securityIssues.length === 0,
        errors: hasCritical || hasHigh ? securityIssues.map(issue => ({
          type: 'security' as const,
          message: issue.message,
          location: issue.location,
          severity: issue.severity
        })) : [],
        warnings: securityIssues.filter(issue => issue.severity === 'low' || issue.severity === 'medium').map(issue => ({
          type: issue.type,
          message: issue.message,
          location: issue.location
        })),
        securityIssues,
        confidence: securityIssues.length === 0 ? 0.95 : hasCritical ? 0.3 : hasHigh ? 0.5 : 0.7
      }
    } catch (error) {
      return {
        valid: false,
        securityIssues: [],
        confidence: 0.5
      }
    }
  }

  /**
   * Validate style
   */
  private async validateStyle(
    code: string,
    language: string
  ): Promise<Partial<ValidationResult>> {
    try {
      const warnings: Array<{
        type: string
        message: string
        location?: { line: number; column: number }
      }> = []

      // Basic style checks
      const lines = code.split('\n')
      
      // Check for consistent indentation
      let indentationType: 'space' | 'tab' | 'mixed' | null = null
      for (const line of lines) {
        if (line.trim().length > 0) {
          const indent = line.match(/^(\s+)/)?.[1] || ''
          if (indent.length > 0) {
            const isTab = indent.includes('\t')
            const isSpace = indent.includes(' ')
            
            if (indentationType === null) {
              indentationType = isTab ? 'tab' : 'space'
            } else if ((isTab && indentationType === 'space') || (isSpace && indentationType === 'tab')) {
              indentationType = 'mixed'
              break
            }
          }
        }
      }

      if (indentationType === 'mixed') {
        warnings.push({
          type: 'style',
          message: 'Mixed indentation detected (tabs and spaces). Use consistent indentation.'
        })
      }

      return {
        valid: true,
        warnings,
        confidence: 0.9
      }
    } catch (error) {
      return {
        valid: true,
        warnings: [],
        confidence: 0.8
      }
    }
  }

  /**
   * Validate performance
   */
  private async validatePerformance(
    code: string,
    language: string
  ): Promise<Partial<ValidationResult>> {
    try {
      const warnings: Array<{
        type: string
        message: string
        location?: { line: number; column: number }
      }> = []

      // Basic performance checks
      // Check for nested loops (O(n²) complexity)
      const nestedLoopPattern = /for\s*\([^)]*\)\s*\{[^}]*for\s*\([^)]*\)/s
      if (nestedLoopPattern.test(code)) {
        warnings.push({
          type: 'performance',
          message: 'Nested loops detected - potential performance issue for large datasets'
        })
      }

      return {
        valid: true,
        warnings,
        quality_metrics: {
          complexity: 0.7
        },
        confidence: 0.85
      }
    } catch (error) {
      return {
        valid: true,
        warnings: [],
        confidence: 0.8
      }
    }
  }

  /**
   * Track validation confidence via VIF
   */
  async trackValidationConfidence(
    result: ValidationResult
  ): Promise<{ witness_id?: string }> {
    try {
      const vifResult = await mcpService.executeTool('mcp_lucid-mcp_track_confidence', {
        confidence_score: result.confidence,
        task_type: 'code_validation',
        context: {
          passed: result.passed,
          errors_count: result.errors?.length || 0,
          warnings_count: result.warnings?.length || 0,
          security_issues_count: result.securityIssues?.length || 0
        }
      })

      return { witness_id: vifResult.result?.witness_id }
    } catch (error) {
      console.error('VIF tracking error:', error)
      return {}
    }
  }
}

// Singleton instance
export const codeValidationService = new CodeValidationService()

