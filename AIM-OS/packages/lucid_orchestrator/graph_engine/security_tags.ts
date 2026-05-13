/**
 * Security Tags for Lucid Orchestrator
 * 
 * This module provides security tagging and analysis for IR nodes,
 * helping identify security-sensitive code and potential vulnerabilities.
 */

import { IRNode, NodeKind } from './ir_model';

export type SecurityLevel = 'low' | 'medium' | 'high' | 'critical';
export type SecurityTag = 
  | 'authentication'
  | 'authorization'
  | 'input_validation'
  | 'output_encoding'
  | 'cryptography'
  | 'session_management'
  | 'file_operations'
  | 'network_operations'
  | 'database_operations'
  | 'api_security'
  | 'xss_vulnerable'
  | 'sql_injection_vulnerable'
  | 'csrf_vulnerable'
  | 'insecure_direct_object_reference'
  | 'security_misconfiguration'
  | 'sensitive_data_exposure'
  | 'insecure_deserialization'
  | 'known_vulnerabilities'
  | 'insufficient_logging'
  | 'business_logic_vulnerability';

export interface SecurityAnalysis {
  level: SecurityLevel;
  tags: SecurityTag[];
  vulnerabilities: SecurityVulnerability[];
  recommendations: string[];
  riskScore: number; // 0-100
}

export interface SecurityVulnerability {
  type: string;
  severity: SecurityLevel;
  description: string;
  line?: number;
  column?: number;
  cwe?: string; // Common Weakness Enumeration
  owasp?: string; // OWASP Top 10 category
  remediation: string;
}

export class SecurityTagger {
  private securityPatterns: Map<SecurityTag, RegExp[]> = new Map();
  private vulnerabilityPatterns: Map<string, SecurityVulnerability> = new Map();

  constructor() {
    this.initializeSecurityPatterns();
    this.initializeVulnerabilityPatterns();
  }

  /**
   * Analyze security characteristics of a node
   */
  analyzeSecurity(node: IRNode): SecurityAnalysis {
    const tags = this.extractSecurityTags(node);
    const vulnerabilities = this.detectVulnerabilities(node);
    const level = this.calculateSecurityLevel(tags, vulnerabilities);
    const recommendations = this.generateRecommendations(tags, vulnerabilities);
    const riskScore = this.calculateRiskScore(tags, vulnerabilities);

    return {
      level,
      tags,
      vulnerabilities,
      recommendations,
      riskScore
    };
  }

  /**
   * Extract security tags from a node
   */
  private extractSecurityTags(node: IRNode): SecurityTag[] {
    const tags: SecurityTag[] = [];
    
    // Analyze based on node kind
    tags.push(...this.getTagsByNodeKind(node.kind));
    
    // Analyze based on node name
    tags.push(...this.getTagsByNodeName(node.name));
    
    // Analyze based on inputs/outputs
    tags.push(...this.getTagsByInputsOutputs(node.inputs, node.outputs));
    
    // Analyze based on side effects
    tags.push(...this.getTagsBySideEffects(node.sideEffects));
    
    // Analyze based on metadata
    if (node.metadata) {
      tags.push(...this.getTagsByMetadata(node.metadata));
    }
    
    // Remove duplicates
    return [...new Set(tags)];
  }

  /**
   * Get security tags based on node kind
   */
  private getTagsByNodeKind(kind: NodeKind): SecurityTag[] {
    const kindTags: Record<NodeKind, SecurityTag[]> = {
      'function': [],
      'reactComponent': ['xss_vulnerable'],
      'component': ['xss_vulnerable'],
      'test': [],
      'apiHandler': ['api_security', 'input_validation', 'output_encoding'],
      'store': ['sensitive_data_exposure'],
      'reducer': ['business_logic_vulnerability'],
      'hook': ['xss_vulnerable'],
      'service': ['api_security'],
      'job': ['business_logic_vulnerability'],
      'queue': ['business_logic_vulnerability'],
      'dbModel': ['database_operations', 'sql_injection_vulnerable'],
      'cssBlock': [],
      'type': [],
      'interface': [],
      'enum': [],
      'constant': [],
      'variable': []
    };
    
    return kindTags[kind] || [];
  }

  /**
   * Get security tags based on node name
   */
  private getTagsByNodeName(name: string): SecurityTag[] {
    const tags: SecurityTag[] = [];
    const nameLower = name.toLowerCase();
    
    // Authentication related
    if (nameLower.includes('auth') || nameLower.includes('login') || nameLower.includes('signin')) {
      tags.push('authentication');
    }
    
    // Authorization related
    if (nameLower.includes('authz') || nameLower.includes('permission') || nameLower.includes('role')) {
      tags.push('authorization');
    }
    
    // Input validation
    if (nameLower.includes('validate') || nameLower.includes('sanitize') || nameLower.includes('filter')) {
      tags.push('input_validation');
    }
    
    // Output encoding
    if (nameLower.includes('encode') || nameLower.includes('escape') || nameLower.includes('sanitize')) {
      tags.push('output_encoding');
    }
    
    // Cryptography
    if (nameLower.includes('crypt') || nameLower.includes('hash') || nameLower.includes('encrypt') || nameLower.includes('decrypt')) {
      tags.push('cryptography');
    }
    
    // Session management
    if (nameLower.includes('session') || nameLower.includes('token') || nameLower.includes('cookie')) {
      tags.push('session_management');
    }
    
    // File operations
    if (nameLower.includes('file') || nameLower.includes('upload') || nameLower.includes('download')) {
      tags.push('file_operations');
    }
    
    // Network operations
    if (nameLower.includes('http') || nameLower.includes('fetch') || nameLower.includes('request') || nameLower.includes('api')) {
      tags.push('network_operations');
    }
    
    // Database operations
    if (nameLower.includes('db') || nameLower.includes('query') || nameLower.includes('sql') || nameLower.includes('database')) {
      tags.push('database_operations');
    }
    
    return tags;
  }

  /**
   * Get security tags based on inputs and outputs
   */
  private getTagsByInputsOutputs(inputs: string[], outputs: string[]): SecurityTag[] {
    const tags: SecurityTag[] = [];
    
    // Check for sensitive data in inputs
    const sensitiveInputs = inputs.filter(input => 
      this.isSensitiveData(input)
    );
    if (sensitiveInputs.length > 0) {
      tags.push('sensitive_data_exposure');
    }
    
    // Check for sensitive data in outputs
    const sensitiveOutputs = outputs.filter(output => 
      this.isSensitiveData(output)
    );
    if (sensitiveOutputs.length > 0) {
      tags.push('sensitive_data_exposure');
    }
    
    return tags;
  }

  /**
   * Get security tags based on side effects
   */
  private getTagsBySideEffects(sideEffects: string[]): SecurityTag[] {
    const tags: SecurityTag[] = [];
    
    for (const effect of sideEffects) {
      const effectLower = effect.toLowerCase();
      
      if (effectLower.includes('file') || effectLower.includes('write') || effectLower.includes('read')) {
        tags.push('file_operations');
      }
      
      if (effectLower.includes('network') || effectLower.includes('http') || effectLower.includes('api')) {
        tags.push('network_operations');
      }
      
      if (effectLower.includes('database') || effectLower.includes('db') || effectLower.includes('query')) {
        tags.push('database_operations');
      }
      
      if (effectLower.includes('log') || effectLower.includes('audit')) {
        tags.push('insufficient_logging');
      }
    }
    
    return tags;
  }

  /**
   * Get security tags based on metadata
   */
  private getTagsByMetadata(metadata: any): SecurityTag[] {
    const tags: SecurityTag[] = [];
    
    // Check for security-related metadata
    if (metadata.securityLevel) {
      if (metadata.securityLevel === 'high' || metadata.securityLevel === 'critical') {
        tags.push('sensitive_data_exposure');
      }
    }
    
    // Check for authentication metadata
    if (metadata.requiresAuth || metadata.authenticated) {
      tags.push('authentication');
    }
    
    // Check for authorization metadata
    if (metadata.requiresPermission || metadata.authorized) {
      tags.push('authorization');
    }
    
    return tags;
  }

  /**
   * Detect security vulnerabilities in a node
   */
  private detectVulnerabilities(node: IRNode): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];
    
    // Check for XSS vulnerabilities
    if (this.hasXSSVulnerability(node)) {
      vulnerabilities.push({
        type: 'Cross-Site Scripting (XSS)',
        severity: 'high',
        description: 'Potential XSS vulnerability detected',
        cwe: 'CWE-79',
        owasp: 'A03:2021 – Injection',
        remediation: 'Implement proper output encoding and input validation'
      });
    }
    
    // Check for SQL injection vulnerabilities
    if (this.hasSQLInjectionVulnerability(node)) {
      vulnerabilities.push({
        type: 'SQL Injection',
        severity: 'critical',
        description: 'Potential SQL injection vulnerability detected',
        cwe: 'CWE-89',
        owasp: 'A03:2021 – Injection',
        remediation: 'Use parameterized queries and input validation'
      });
    }
    
    // Check for CSRF vulnerabilities
    if (this.hasCSRFVulnerability(node)) {
      vulnerabilities.push({
        type: 'Cross-Site Request Forgery (CSRF)',
        severity: 'medium',
        description: 'Potential CSRF vulnerability detected',
        cwe: 'CWE-352',
        owasp: 'A01:2021 – Broken Access Control',
        remediation: 'Implement CSRF tokens and same-site cookies'
      });
    }
    
    // Check for insecure direct object references
    if (this.hasInsecureDirectObjectReference(node)) {
      vulnerabilities.push({
        type: 'Insecure Direct Object Reference',
        severity: 'medium',
        description: 'Potential insecure direct object reference detected',
        cwe: 'CWE-639',
        owasp: 'A01:2021 – Broken Access Control',
        remediation: 'Implement proper authorization checks'
      });
    }
    
    return vulnerabilities;
  }

  /**
   * Check for XSS vulnerability
   */
  private hasXSSVulnerability(node: IRNode): boolean {
    // Check if node handles user input without proper encoding
    const hasUserInput = node.inputs.some(input => 
      input.toLowerCase().includes('user') || 
      input.toLowerCase().includes('input') ||
      input.toLowerCase().includes('form')
    );
    
    const hasHTMLOutput = node.outputs.some(output => 
      output.toLowerCase().includes('html') || 
      output.toLowerCase().includes('dom') ||
      output.toLowerCase().includes('render')
    );
    
    const hasEncoding = node.name.toLowerCase().includes('encode') || 
                       node.name.toLowerCase().includes('escape') ||
                       node.name.toLowerCase().includes('sanitize');
    
    return hasUserInput && hasHTMLOutput && !hasEncoding;
  }

  /**
   * Check for SQL injection vulnerability
   */
  private hasSQLInjectionVulnerability(node: IRNode): boolean {
    const hasDatabaseOperation = node.kind === 'dbModel' || 
                                node.name.toLowerCase().includes('sql') ||
                                node.name.toLowerCase().includes('query') ||
                                node.name.toLowerCase().includes('database');
    
    const hasUserInput = node.inputs.some(input => 
      input.toLowerCase().includes('user') || 
      input.toLowerCase().includes('input') ||
      input.toLowerCase().includes('param')
    );
    
    const hasParameterizedQueries = node.name.toLowerCase().includes('parameterized') ||
                                   node.name.toLowerCase().includes('prepared') ||
                                   node.name.toLowerCase().includes('bind');
    
    return hasDatabaseOperation && hasUserInput && !hasParameterizedQueries;
  }

  /**
   * Check for CSRF vulnerability
   */
  private hasCSRFVulnerability(node: IRNode): boolean {
    const hasStateChange = node.sideEffects.some(effect => 
      effect.toLowerCase().includes('create') ||
      effect.toLowerCase().includes('update') ||
      effect.toLowerCase().includes('delete')
    );
    
    const hasCSRFProtection = node.name.toLowerCase().includes('csrf') ||
                             node.name.toLowerCase().includes('token') ||
                             node.name.toLowerCase().includes('same-site');
    
    return hasStateChange && !hasCSRFProtection;
  }

  /**
   * Check for insecure direct object reference
   */
  private hasInsecureDirectObjectReference(node: IRNode): boolean {
    const hasObjectReference = node.inputs.some(input => 
      input.toLowerCase().includes('id') ||
      input.toLowerCase().includes('key') ||
      input.toLowerCase().includes('reference')
    );
    
    const hasAuthorization = node.name.toLowerCase().includes('auth') ||
                            node.name.toLowerCase().includes('permission') ||
                            node.name.toLowerCase().includes('authorize');
    
    return hasObjectReference && !hasAuthorization;
  }

  /**
   * Calculate security level based on tags and vulnerabilities
   */
  private calculateSecurityLevel(tags: SecurityTag[], vulnerabilities: SecurityVulnerability[]): SecurityLevel {
    let score = 0;
    
    // Base score from tags
    for (const tag of tags) {
      score += this.getTagScore(tag);
    }
    
    // Add vulnerability scores
    for (const vuln of vulnerabilities) {
      score += this.getVulnerabilityScore(vuln.severity);
    }
    
    // Determine level
    if (score >= 80) return 'critical';
    if (score >= 60) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  }

  /**
   * Get score for a security tag
   */
  private getTagScore(tag: SecurityTag): number {
    const tagScores: Record<SecurityTag, number> = {
      'authentication': 20,
      'authorization': 20,
      'input_validation': 15,
      'output_encoding': 15,
      'cryptography': 25,
      'session_management': 20,
      'file_operations': 15,
      'network_operations': 10,
      'database_operations': 15,
      'api_security': 15,
      'xss_vulnerable': 30,
      'sql_injection_vulnerable': 40,
      'csrf_vulnerable': 25,
      'insecure_direct_object_reference': 20,
      'security_misconfiguration': 15,
      'sensitive_data_exposure': 35,
      'insecure_deserialization': 30,
      'known_vulnerabilities': 40,
      'insufficient_logging': 10,
      'business_logic_vulnerability': 25
    };
    
    return tagScores[tag] || 0;
  }

  /**
   * Get score for a vulnerability severity
   */
  private getVulnerabilityScore(severity: SecurityLevel): number {
    const severityScores = { 'low': 10, 'medium': 20, 'high': 40, 'critical': 60 };
    return severityScores[severity] || 0;
  }

  /**
   * Calculate risk score (0-100)
   */
  private calculateRiskScore(tags: SecurityTag[], vulnerabilities: SecurityVulnerability[]): number {
    let score = 0;
    
    // Add tag scores
    for (const tag of tags) {
      score += this.getTagScore(tag);
    }
    
    // Add vulnerability scores
    for (const vuln of vulnerabilities) {
      score += this.getVulnerabilityScore(vuln.severity);
    }
    
    // Cap at 100
    return Math.min(score, 100);
  }

  /**
   * Generate security recommendations
   */
  private generateRecommendations(tags: SecurityTag[], vulnerabilities: SecurityVulnerability[]): string[] {
    const recommendations: string[] = [];
    
    // Generate recommendations based on tags
    if (tags.includes('xss_vulnerable')) {
      recommendations.push('Implement proper output encoding for all user-generated content');
    }
    
    if (tags.includes('sql_injection_vulnerable')) {
      recommendations.push('Use parameterized queries for all database operations');
    }
    
    if (tags.includes('csrf_vulnerable')) {
      recommendations.push('Implement CSRF tokens for state-changing operations');
    }
    
    if (tags.includes('sensitive_data_exposure')) {
      recommendations.push('Encrypt sensitive data at rest and in transit');
    }
    
    if (tags.includes('insufficient_logging')) {
      recommendations.push('Implement comprehensive security logging and monitoring');
    }
    
    // Generate recommendations based on vulnerabilities
    for (const vuln of vulnerabilities) {
      recommendations.push(vuln.remediation);
    }
    
    return [...new Set(recommendations)]; // Remove duplicates
  }

  /**
   * Check if data is sensitive
   */
  private isSensitiveData(data: string): boolean {
    const sensitivePatterns = [
      'password', 'passwd', 'pwd',
      'secret', 'key', 'token',
      'ssn', 'social', 'credit',
      'card', 'cvv', 'cvc',
      'email', 'phone', 'address',
      'private', 'confidential'
    ];
    
    const dataLower = data.toLowerCase();
    return sensitivePatterns.some(pattern => dataLower.includes(pattern));
  }

  /**
   * Initialize security patterns
   */
  private initializeSecurityPatterns(): void {
    // This would contain regex patterns for detecting security-related code
    // For now, it's a placeholder
  }

  /**
   * Initialize vulnerability patterns
   */
  private initializeVulnerabilityPatterns(): void {
    // This would contain patterns for detecting specific vulnerabilities
    // For now, it's a placeholder
  }
}
