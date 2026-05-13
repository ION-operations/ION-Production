/**
 * Spec Pane Data Service
 * 
 * Handles specification management, compliance checking,
 * and quality monitoring for the Spec Pane of the Lucid Orchestrator.
 */

import {
  SpecPaneData,
  SpecificationCollection,
  Specification,
  DocumentationMapping,
  ComplianceStatus,
  QualityMetrics,
  Violation,
  Warning,
  Recommendation,
  MappingEntry
} from '../data_models/core_interfaces';
import { CodePaneData } from '../data_models/core_interfaces';
import * as fs from 'fs';
import * as path from 'path';

export class SpecPaneService {
  private specifications: Map<string, Specification> = new Map();
  private complianceCache: Map<string, ComplianceStatus> = new Map();
  private qualityCache: Map<string, QualityMetrics> = new Map();

  constructor() {
    this.initializeDefaultSpecifications();
  }

  /**
   * Load specifications for a system
   */
  async loadSpecifications(systemId: string): Promise<SpecificationCollection> {
    const specs: SpecificationCollection = {
      requirements: [],
      constraints: [],
      standards: [],
      guidelines: []
    };

    // Load from system-specific spec files
    const specPath = path.join('knowledge_architecture', 'systems', systemId, 'specs');
    if (fs.existsSync(specPath)) {
      await this.loadSpecsFromDirectory(specPath, specs);
    }

    // Add default specifications
    this.addDefaultSpecifications(systemId, specs);

    return specs;
  }

  /**
   * Load specifications from directory
   */
  private async loadSpecsFromDirectory(
    specPath: string, 
    specs: SpecificationCollection
  ): Promise<void> {
    const files = fs.readdirSync(specPath);
    
    for (const file of files) {
      if (file.endsWith('.md') || file.endsWith('.yaml') || file.endsWith('.json')) {
        const filePath = path.join(specPath, file);
        const content = fs.readFileSync(filePath, 'utf-8');
        const spec = this.parseSpecificationFile(content, file);
        
        if (spec) {
          this.specifications.set(spec.id, spec);
          this.categorizeSpecification(spec, specs);
        }
      }
    }
  }

  /**
   * Parse specification file
   */
  private parseSpecificationFile(content: string, filename: string): Specification | null {
    try {
      // Try to parse as JSON first
      if (filename.endsWith('.json')) {
        const data = JSON.parse(content);
        return this.createSpecificationFromData(data);
      }
      
      // Try to parse as YAML
      if (filename.endsWith('.yaml') || filename.endsWith('.yml')) {
        // Simple YAML parsing (would use a proper YAML library in production)
        return this.parseYAMLSpecification(content, filename);
      }
      
      // Parse as Markdown
      if (filename.endsWith('.md')) {
        return this.parseMarkdownSpecification(content, filename);
      }
      
      return null;
    } catch (error) {
      console.error(`Error parsing specification file ${filename}:`, error);
      return null;
    }
  }

  /**
   * Parse YAML specification
   */
  private parseYAMLSpecification(content: string, filename: string): Specification | null {
    // Simple YAML parsing (would use yaml library in production)
    const lines = content.split('\n');
    const spec: any = {
      id: `spec_${filename.replace(/\.(yaml|yml)$/, '')}`,
      title: filename.replace(/\.(yaml|yml)$/, ''),
      description: '',
      type: 'requirement',
      priority: 'medium',
      content: {
        must: [],
        mustNot: [],
        should: [],
        could: []
      },
      status: 'active',
      violations: [],
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      author: 'system',
      version: '1.0.0'
    };

    let currentSection = '';
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('title:')) {
        spec.title = trimmed.substring(6).trim();
      } else if (trimmed.startsWith('description:')) {
        spec.description = trimmed.substring(12).trim();
      } else if (trimmed.startsWith('type:')) {
        spec.type = trimmed.substring(5).trim();
      } else if (trimmed.startsWith('priority:')) {
        spec.priority = trimmed.substring(9).trim();
      } else if (trimmed.startsWith('must:')) {
        currentSection = 'must';
      } else if (trimmed.startsWith('mustNot:')) {
        currentSection = 'mustNot';
      } else if (trimmed.startsWith('should:')) {
        currentSection = 'should';
      } else if (trimmed.startsWith('could:')) {
        currentSection = 'could';
      } else if (trimmed.startsWith('- ') && currentSection) {
        spec.content[currentSection].push(trimmed.substring(2));
      }
    }

    return this.createSpecificationFromData(spec);
  }

  /**
   * Parse Markdown specification
   */
  private parseMarkdownSpecification(content: string, filename: string): Specification | null {
    const lines = content.split('\n');
    const spec: any = {
      id: `spec_${filename.replace(/\.md$/, '')}`,
      title: filename.replace(/\.md$/, ''),
      description: '',
      type: 'requirement',
      priority: 'medium',
      content: {
        must: [],
        mustNot: [],
        should: [],
        could: []
      },
      status: 'active',
      violations: [],
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      author: 'system',
      version: '1.0.0'
    };

    let currentSection = '';
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('# ')) {
        spec.title = trimmed.substring(2);
      } else if (trimmed.startsWith('## Description')) {
        currentSection = 'description';
      } else if (trimmed.startsWith('## Must')) {
        currentSection = 'must';
      } else if (trimmed.startsWith('## Must Not')) {
        currentSection = 'mustNot';
      } else if (trimmed.startsWith('## Should')) {
        currentSection = 'should';
      } else if (trimmed.startsWith('## Could')) {
        currentSection = 'could';
      } else if (trimmed.startsWith('- ') && currentSection) {
        if (currentSection === 'description') {
          spec.description += trimmed.substring(2) + ' ';
        } else {
          spec.content[currentSection].push(trimmed.substring(2));
        }
      }
    }

    spec.description = spec.description.trim();
    return this.createSpecificationFromData(spec);
  }

  /**
   * Create specification from data object
   */
  private createSpecificationFromData(data: any): Specification {
    return {
      id: data.id || `spec_${Date.now()}`,
      nodeId: data.nodeId,
      title: data.title || 'Untitled Specification',
      description: data.description || '',
      type: data.type || 'requirement',
      priority: data.priority || 'medium',
      content: {
        must: data.content?.must || [],
        mustNot: data.content?.mustNot || [],
        should: data.content?.should || [],
        could: data.content?.could || [],
        examples: data.content?.examples || [],
        references: data.content?.references || []
      },
      status: data.status || 'active',
      violations: data.violations || [],
      created: data.created || new Date().toISOString(),
      updated: data.updated || new Date().toISOString(),
      author: data.author || 'system',
      version: data.version || '1.0.0'
    };
  }

  /**
   * Categorize specification by type
   */
  private categorizeSpecification(spec: Specification, specs: SpecificationCollection): void {
    switch (spec.type) {
      case 'requirement':
        specs.requirements.push(spec);
        break;
      case 'constraint':
        specs.constraints.push(spec);
        break;
      case 'standard':
        specs.standards.push(spec);
        break;
      case 'guideline':
        specs.guidelines.push(spec);
        break;
    }
  }

  /**
   * Add default specifications for a system
   */
  private addDefaultSpecifications(systemId: string, specs: SpecificationCollection): void {
    // Add default requirements
    const defaultRequirements = [
      {
        id: `${systemId}_data_integrity`,
        title: 'Data Integrity Requirements',
        description: 'System must maintain data integrity across all operations',
        type: 'requirement',
        priority: 'critical',
        content: {
          must: [
            'All data operations must be atomic',
            'Data corruption must be detected and prevented',
            'Backup and recovery mechanisms must be in place'
          ],
          mustNot: [
            'Data must never be lost due to system failures',
            'Concurrent access must not cause data corruption'
          ],
          should: [
            'Implement checksums for data validation',
            'Use transactions for complex operations'
          ]
        }
      },
      {
        id: `${systemId}_performance_requirements`,
        title: 'Performance Requirements',
        description: 'System must meet specific performance benchmarks',
        type: 'requirement',
        priority: 'high',
        content: {
          must: [
            'Response time must be under 100ms for 95% of requests',
            'System must handle 1000 concurrent users',
            'Memory usage must not exceed 1GB per session'
          ],
          should: [
            'Implement caching for frequently accessed data',
            'Use connection pooling for database operations'
          ]
        }
      },
      {
        id: `${systemId}_security_requirements`,
        title: 'Security Requirements',
        description: 'System must implement appropriate security measures',
        type: 'requirement',
        priority: 'critical',
        content: {
          must: [
            'All user input must be validated and sanitized',
            'Sensitive data must be encrypted at rest and in transit',
            'Authentication and authorization must be implemented'
          ],
          mustNot: [
            'Sensitive data must never be logged in plain text',
            'Default credentials must not be used in production'
          ]
        }
      }
    ];

    defaultRequirements.forEach(req => {
      const spec = this.createSpecificationFromData(req);
      this.specifications.set(spec.id, spec);
      specs.requirements.push(spec);
    });
  }

  /**
   * Initialize default specifications
   */
  private initializeDefaultSpecifications(): void {
    // This would load system-wide default specifications
    // For now, we'll add them when needed per system
  }

  /**
   * Check compliance for a specification
   */
  async checkCompliance(specId: string, codeData?: CodePaneData): Promise<ComplianceStatus> {
    const spec = this.specifications.get(specId);
    if (!spec) {
      throw new Error(`Specification not found: ${specId}`);
    }

    // Check cache first
    const cacheKey = `${specId}_${codeData ? 'with_code' : 'without_code'}`;
    if (this.complianceCache.has(cacheKey)) {
      return this.complianceCache.get(cacheKey)!;
    }

    const violations: Violation[] = [];
    const warnings: Warning[] = [];
    const recommendations: Recommendation[] = [];

    // Check must requirements
    for (const requirement of spec.content.must) {
      const violation = await this.checkRequirement(requirement, codeData);
      if (violation) {
        violations.push(violation);
      }
    }

    // Check must not requirements
    for (const prohibition of spec.content.mustNot) {
      const violation = await this.checkProhibition(prohibition, codeData);
      if (violation) {
        violations.push(violation);
      }
    }

    // Check should requirements (warnings)
    for (const recommendation of spec.content.should) {
      const warning = await this.checkRecommendation(recommendation, codeData);
      if (warning) {
        warnings.push(warning);
      }
    }

    // Generate recommendations
    recommendations.push(...this.generateRecommendations(spec, violations, warnings));

    const compliance: ComplianceStatus = {
      violations,
      warnings,
      recommendations,
      overallScore: this.calculateComplianceScore(violations, warnings)
    };

    // Cache the result
    this.complianceCache.set(cacheKey, compliance);
    return compliance;
  }

  /**
   * Check a single requirement
   */
  private async checkRequirement(requirement: string, codeData?: CodePaneData): Promise<Violation | null> {
    // This is a simplified implementation
    // In a real system, this would use static analysis, runtime monitoring, etc.
    
    if (!codeData) {
      return null; // Can't check without code data
    }

    // Check for common patterns
    const lowerReq = requirement.toLowerCase();
    
    if (lowerReq.includes('atomic') && !this.hasAtomicOperations(codeData)) {
      return {
        id: `violation_${Date.now()}`,
        message: 'Atomic operations not detected',
        severity: 'error',
        suggestion: 'Implement database transactions or atomic operations',
        created: new Date().toISOString()
      };
    }

    if (lowerReq.includes('validation') && !this.hasInputValidation(codeData)) {
      return {
        id: `violation_${Date.now()}`,
        message: 'Input validation not detected',
        severity: 'error',
        suggestion: 'Add input validation for all user inputs',
        created: new Date().toISOString()
      };
    }

    if (lowerReq.includes('encryption') && !this.hasEncryption(codeData)) {
      return {
        id: `violation_${Date.now()}`,
        message: 'Encryption not detected',
        severity: 'error',
        suggestion: 'Implement encryption for sensitive data',
        created: new Date().toISOString()
      };
    }

    return null;
  }

  /**
   * Check a prohibition
   */
  private async checkProhibition(prohibition: string, codeData?: CodePaneData): Promise<Violation | null> {
    if (!codeData) {
      return null;
    }

    const lowerProhibition = prohibition.toLowerCase();
    
    if (lowerProhibition.includes('plain text') && this.hasPlainTextLogging(codeData)) {
      return {
        id: `violation_${Date.now()}`,
        message: 'Plain text logging detected',
        severity: 'error',
        suggestion: 'Remove or encrypt sensitive data in logs',
        created: new Date().toISOString()
      };
    }

    if (lowerProhibition.includes('default') && this.hasDefaultCredentials(codeData)) {
      return {
        id: `violation_${Date.now()}`,
        message: 'Default credentials detected',
        severity: 'error',
        suggestion: 'Change default credentials and use environment variables',
        created: new Date().toISOString()
      };
    }

    return null;
  }

  /**
   * Check a recommendation
   */
  private async checkRecommendation(recommendation: string, codeData?: CodePaneData): Promise<Warning | null> {
    if (!codeData) {
      return null;
    }

    const lowerRec = recommendation.toLowerCase();
    
    if (lowerRec.includes('caching') && !this.hasCaching(codeData)) {
      return {
        id: `warning_${Date.now()}`,
        specId: 'performance_requirements',
        message: 'Caching not implemented',
        severity: 'medium',
        recommendation: 'Implement caching for better performance'
      };
    }

    if (lowerRec.includes('connection pooling') && !this.hasConnectionPooling(codeData)) {
      return {
        id: `warning_${Date.now()}`,
        specId: 'performance_requirements',
        message: 'Connection pooling not implemented',
        severity: 'low',
        recommendation: 'Implement connection pooling for database operations'
      };
    }

    return null;
  }

  /**
   * Generate recommendations based on violations and warnings
   */
  private generateRecommendations(
    spec: Specification, 
    violations: Violation[], 
    warnings: Warning[]
  ): Recommendation[] {
    const recommendations: Recommendation[] = [];

    if (violations.length > 0) {
      recommendations.push({
        id: `rec_${Date.now()}`,
        specId: spec.id,
        message: 'Address critical violations to improve compliance',
        priority: 'high',
        effort: 'high'
      });
    }

    if (warnings.length > 0) {
      recommendations.push({
        id: `rec_${Date.now() + 1}`,
        specId: spec.id,
        message: 'Address warnings to improve quality',
        priority: 'medium',
        effort: 'medium'
      });
    }

    return recommendations;
  }

  /**
   * Calculate compliance score
   */
  private calculateComplianceScore(violations: Violation[], warnings: Warning[]): number {
    const totalIssues = violations.length + warnings.length;
    if (totalIssues === 0) return 1.0;

    const violationWeight = 0.7;
    const warningWeight = 0.3;
    const score = 1.0 - (violations.length * violationWeight + warnings.length * warningWeight) / 10;
    
    return Math.max(0, Math.min(1, score));
  }

  /**
   * Check if code has atomic operations
   */
  private hasAtomicOperations(codeData: CodePaneData): boolean {
    // Simplified check for atomic operations
    const atomicKeywords = ['transaction', 'atomic', 'commit', 'rollback'];
    return this.hasKeywordsInCode(codeData, atomicKeywords);
  }

  /**
   * Check if code has input validation
   */
  private hasInputValidation(codeData: CodePaneData): boolean {
    const validationKeywords = ['validate', 'sanitize', 'check', 'verify'];
    return this.hasKeywordsInCode(codeData, validationKeywords);
  }

  /**
   * Check if code has encryption
   */
  private hasEncryption(codeData: CodePaneData): boolean {
    const encryptionKeywords = ['encrypt', 'decrypt', 'cipher', 'hash', 'bcrypt'];
    return this.hasKeywordsInCode(codeData, encryptionKeywords);
  }

  /**
   * Check if code has plain text logging
   */
  private hasPlainTextLogging(codeData: CodePaneData): boolean {
    const logKeywords = ['console.log', 'print', 'logger.info'];
    return this.hasKeywordsInCode(codeData, logKeywords);
  }

  /**
   * Check if code has default credentials
   */
  private hasDefaultCredentials(codeData: CodePaneData): boolean {
    const defaultKeywords = ['admin', 'password', '123456', 'default'];
    return this.hasKeywordsInCode(codeData, defaultKeywords);
  }

  /**
   * Check if code has caching
   */
  private hasCaching(codeData: CodePaneData): boolean {
    const cacheKeywords = ['cache', 'redis', 'memcached', 'lru'];
    return this.hasKeywordsInCode(codeData, cacheKeywords);
  }

  /**
   * Check if code has connection pooling
   */
  private hasConnectionPooling(codeData: CodePaneData): boolean {
    const poolKeywords = ['pool', 'connection', 'pooling'];
    return this.hasKeywordsInCode(codeData, poolKeywords);
  }

  /**
   * Check if code contains specific keywords
   */
  private hasKeywordsInCode(codeData: CodePaneData, keywords: string[]): boolean {
    for (const file of codeData.files.source) {
      // This would need to read actual file content in a real implementation
      // For now, we'll do a simple check based on file names and metadata
      const fileName = file.name.toLowerCase();
      for (const keyword of keywords) {
        if (fileName.includes(keyword.toLowerCase())) {
          return true;
        }
      }
    }
    return false;
  }

  /**
   * Build documentation mapping
   */
  async buildDocumentationMapping(codeData: CodePaneData): Promise<DocumentationMapping> {
    const mapping: DocumentationMapping = {
      L0: [],
      L1: [],
      L2: [],
      L3: [],
      L4: []
    };

    // Map specifications to documentation levels
    for (const spec of this.specifications.values()) {
      const docLevel = this.mapSpecToDocumentationLevel(spec);
      if (docLevel) {
        mapping[docLevel].push({
          specId: spec.id,
          docId: `doc_${spec.id}`,
          mapping: `Specification ${spec.title} maps to ${docLevel} documentation`,
          alignment: 0.8
        });
      }
    }

    return mapping;
  }

  /**
   * Map specification to documentation level
   */
  private mapSpecToDocumentationLevel(spec: Specification): 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | null {
    // Simple mapping based on priority and type
    if (spec.priority === 'critical' && spec.type === 'requirement') {
      return 'L0';
    } else if (spec.priority === 'high' && spec.type === 'requirement') {
      return 'L1';
    } else if (spec.type === 'requirement') {
      return 'L2';
    } else if (spec.type === 'constraint') {
      return 'L3';
    } else if (spec.type === 'guideline') {
      return 'L4';
    }
    return null;
  }

  /**
   * Calculate quality metrics
   */
  async calculateQualityMetrics(specs: SpecificationCollection): Promise<QualityMetrics> {
    const totalSpecs = specs.requirements.length + specs.constraints.length + 
                      specs.standards.length + specs.guidelines.length;
    
    const specCompleteness = totalSpecs > 0 ? 1.0 : 0.0;
    const docAlignment = 0.8; // Would calculate based on actual mapping
    const complianceRate = 0.9; // Would calculate based on actual compliance checks
    
    const overallHealth = (specCompleteness + docAlignment + complianceRate) / 3;

    return {
      specCompleteness,
      docAlignment,
      complianceRate,
      overallHealth,
      lastChecked: new Date().toISOString()
    };
  }

  /**
   * Update specification
   */
  async updateSpecification(specId: string, updates: Partial<Specification>): Promise<void> {
    const spec = this.specifications.get(specId);
    if (!spec) {
      throw new Error(`Specification not found: ${specId}`);
    }

    const updatedSpec = {
      ...spec,
      ...updates,
      updated: new Date().toISOString()
    };

    this.specifications.set(specId, updatedSpec);
    
    // Clear related caches
    this.complianceCache.clear();
    this.qualityCache.clear();
  }

  /**
   * Get specification by ID
   */
  getSpecification(specId: string): Specification | null {
    return this.specifications.get(specId) || null;
  }

  /**
   * Get all specifications
   */
  getAllSpecifications(): Specification[] {
    return Array.from(this.specifications.values());
  }

  /**
   * Clear caches
   */
  clearCaches(): void {
    this.complianceCache.clear();
    this.qualityCache.clear();
  }
}
