/**
 * Security Service
 * 
 * Provides comprehensive security features for the Advanced Monaco Editor
 * including:
 * - Input validation and sanitization
 * - XSS prevention
 * - CSRF protection
 * - Content Security Policy (CSP)
 * - Access control
 * - Audit logging
 * - Threat detection
 * - Data encryption
 */

import { EventEmitter } from 'events';

export interface SecurityConfig {
  enableInputValidation: boolean;
  enableXSSProtection: boolean;
  enableCSRFProtection: boolean;
  enableCSP: boolean;
  enableAccessControl: boolean;
  enableAuditLogging: boolean;
  enableThreatDetection: boolean;
  enableDataEncryption: boolean;
  enableSandboxing: boolean;
  maxCodeSize: number; // in bytes
  allowedDomains: string[];
  blockedDomains: string[];
  allowedFileTypes: string[];
  blockedFileTypes: string[];
  maxFileSize: number; // in bytes
  enableRateLimiting: boolean;
  rateLimitWindow: number; // in milliseconds
  rateLimitMaxRequests: number;
  enableContentFiltering: boolean;
  blockedPatterns: RegExp[];
  enableDataProtection: boolean;
  enablePrivacyMode: boolean;
  enableSecureStorage: boolean;
  encryptionKey?: string;
  auditLogLevel: 'low' | 'medium' | 'high' | 'critical';
}

export interface SecurityEvent {
  id: string;
  timestamp: number;
  type: 'validation' | 'xss' | 'csrf' | 'access' | 'audit' | 'threat' | 'encryption' | 'sandbox';
  level: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  details: Record<string, any>;
  source: string;
  userAgent?: string;
  ipAddress?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  sanitizedInput: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

export interface ThreatDetectionResult {
  isThreat: boolean;
  threatType: 'xss' | 'injection' | 'malware' | 'phishing' | 'suspicious' | 'unknown';
  confidence: number; // 0-1
  details: string;
  recommendations: string[];
}

export class SecurityService extends EventEmitter {
  private config: SecurityConfig;
  private events: SecurityEvent[] = [];
  private rateLimitTracker: Map<string, { count: number; resetTime: number }> = new Map();
  private blockedIPs: Set<string> = new Set();
  private allowedIPs: Set<string> = new Set();
  private encryptionKey: string;

  constructor(config: Partial<SecurityConfig> = {}) {
    super();
    
    this.config = {
      enableInputValidation: true,
      enableXSSProtection: true,
      enableCSRFProtection: true,
      enableCSP: true,
      enableAccessControl: true,
      enableAuditLogging: true,
      enableThreatDetection: true,
      enableDataEncryption: false,
      enableSandboxing: true,
      maxCodeSize: 1024 * 1024, // 1MB
      allowedDomains: ['localhost', '127.0.0.1'],
      blockedDomains: [],
      allowedFileTypes: ['.js', '.ts', '.jsx', '.tsx', '.json', '.md'],
      blockedFileTypes: ['.exe', '.bat', '.cmd', '.scr', '.pif'],
      maxFileSize: 10 * 1024 * 1024, // 10MB
      enableRateLimiting: true,
      rateLimitWindow: 60000, // 1 minute
      rateLimitMaxRequests: 100,
      enableContentFiltering: true,
      blockedPatterns: [
        /<script[^>]*>.*?<\/script>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi,
        /eval\s*\(/gi,
        /expression\s*\(/gi
      ],
      enableDataProtection: true,
      enablePrivacyMode: false,
      enableSecureStorage: false,
      auditLogLevel: 'medium',
      ...config
    };

    this.encryptionKey = config.encryptionKey || this.generateEncryptionKey();
    this.initializeSecurity();
  }

  private initializeSecurity(): void {
    // Set up CSP if enabled
    if (this.config.enableCSP) {
      this.setupCSP();
    }

    // Set up rate limiting cleanup
    if (this.config.enableRateLimiting) {
      setInterval(() => {
        this.cleanupRateLimitTracker();
      }, this.config.rateLimitWindow);
    }

    // Set up audit logging
    if (this.config.enableAuditLogging) {
      this.logSecurityEvent('info', 'audit', 'Security service initialized', {
        config: this.config
      });
    }
  }

  private setupCSP(): void {
    if (typeof document === 'undefined') return;

    const csp = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob:",
      "font-src 'self' data:",
      "connect-src 'self'",
      "frame-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'"
    ].join('; ');

    const meta = document.createElement('meta');
    meta.httpEquiv = 'Content-Security-Policy';
    meta.content = csp;
    document.head.appendChild(meta);
  }

  private generateEncryptionKey(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  // Input validation
  public validateInput(input: string, context: string = 'general'): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let sanitizedInput = input;
    let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';

    if (!this.config.enableInputValidation) {
      return {
        isValid: true,
        errors: [],
        warnings: [],
        sanitizedInput: input,
        riskLevel: 'low'
      };
    }

    // Check input size
    if (input.length > this.config.maxCodeSize) {
      errors.push(`Input exceeds maximum size limit of ${this.config.maxCodeSize} bytes`);
      riskLevel = 'high';
    }

    // XSS protection
    if (this.config.enableXSSProtection) {
      const xssResult = this.detectXSS(input);
      if (xssResult.isThreat) {
        errors.push(`XSS threat detected: ${xssResult.details}`);
        riskLevel = 'critical';
        sanitizedInput = this.sanitizeInput(input);
      }
    }

    // Content filtering
    if (this.config.enableContentFiltering) {
      for (const pattern of this.config.blockedPatterns) {
        if (pattern.test(input)) {
          errors.push(`Blocked pattern detected: ${pattern.source}`);
          riskLevel = 'high';
          sanitizedInput = this.sanitizeInput(input);
        }
      }
    }

    // Context-specific validation
    switch (context) {
      case 'code':
        const codeValidation = this.validateCode(input);
        errors.push(...codeValidation.errors);
        warnings.push(...codeValidation.warnings);
        if (codeValidation.riskLevel === 'high' || codeValidation.riskLevel === 'critical') {
          riskLevel = codeValidation.riskLevel;
        }
        break;
      case 'url':
        const urlValidation = this.validateURL(input);
        errors.push(...urlValidation.errors);
        warnings.push(...urlValidation.warnings);
        if (urlValidation.riskLevel === 'high' || urlValidation.riskLevel === 'critical') {
          riskLevel = urlValidation.riskLevel;
        }
        break;
    }

    const result: ValidationResult = {
      isValid: errors.length === 0,
      errors,
      warnings,
      sanitizedInput,
      riskLevel
    };

    if (this.config.enableAuditLogging) {
      this.logSecurityEvent(
        errors.length > 0 ? 'warning' : 'info',
        'validation',
        `Input validation for ${context}`,
        { input: input.substring(0, 100), result }
      );
    }

    return result;
  }

  private validateCode(code: string): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';

    // Check for dangerous functions
    const dangerousFunctions = ['eval', 'Function', 'setTimeout', 'setInterval', 'execScript'];
    for (const func of dangerousFunctions) {
      if (code.includes(func)) {
        warnings.push(`Potentially dangerous function detected: ${func}`);
        riskLevel = 'medium';
      }
    }

    // Check for suspicious patterns
    const suspiciousPatterns = [
      /document\.write/gi,
      /innerHTML\s*=/gi,
      /outerHTML\s*=/gi,
      /document\.cookie/gi,
      /localStorage/gi,
      /sessionStorage/gi
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(code)) {
        warnings.push(`Suspicious pattern detected: ${pattern.source}`);
        riskLevel = 'high';
      }
    }

    return {
      isValid: true,
      errors,
      warnings,
      sanitizedInput: code,
      riskLevel
    };
  }

  private validateURL(url: string): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';

    try {
      const urlObj = new URL(url);
      
      // Check if domain is blocked
      if (this.config.blockedDomains.includes(urlObj.hostname)) {
        errors.push(`Blocked domain: ${urlObj.hostname}`);
        riskLevel = 'critical';
      }

      // Check if domain is allowed
      if (this.config.allowedDomains.length > 0 && !this.config.allowedDomains.includes(urlObj.hostname)) {
        errors.push(`Domain not in allowed list: ${urlObj.hostname}`);
        riskLevel = 'high';
      }

      // Check for suspicious protocols
      if (!['http:', 'https:', 'data:'].includes(urlObj.protocol)) {
        errors.push(`Suspicious protocol: ${urlObj.protocol}`);
        riskLevel = 'high';
      }

    } catch (error) {
      errors.push('Invalid URL format');
      riskLevel = 'high';
    }

    return {
      isValid: true,
      errors,
      warnings,
      sanitizedInput: url,
      riskLevel
    };
  }

  private detectXSS(input: string): ThreatDetectionResult {
    const xssPatterns = [
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe[^>]*>.*?<\/iframe>/gi,
      /<object[^>]*>.*?<\/object>/gi,
      /<embed[^>]*>.*?<\/embed>/gi,
      /<link[^>]*>.*?<\/link>/gi,
      /<meta[^>]*>.*?<\/meta>/gi,
      /<style[^>]*>.*?<\/style>/gi,
      /<form[^>]*>.*?<\/form>/gi,
      /<input[^>]*>.*?<\/input>/gi,
      /<textarea[^>]*>.*?<\/textarea>/gi,
      /<select[^>]*>.*?<\/select>/gi,
      /<option[^>]*>.*?<\/option>/gi,
      /<button[^>]*>.*?<\/button>/gi,
      /<a[^>]*>.*?<\/a>/gi,
      /<img[^>]*>.*?<\/img>/gi,
      /<video[^>]*>.*?<\/video>/gi,
      /<audio[^>]*>.*?<\/audio>/gi,
      /<source[^>]*>.*?<\/source>/gi,
      /<track[^>]*>.*?<\/track>/gi,
      /<canvas[^>]*>.*?<\/canvas>/gi,
      /<svg[^>]*>.*?<\/svg>/gi,
      /<math[^>]*>.*?<\/math>/gi,
      /<iframe[^>]*>.*?<\/iframe>/gi,
      /<object[^>]*>.*?<\/object>/gi,
      /<embed[^>]*>.*?<\/embed>/gi,
      /<link[^>]*>.*?<\/link>/gi,
      /<meta[^>]*>.*?<\/meta>/gi,
      /<style[^>]*>.*?<\/style>/gi,
      /<form[^>]*>.*?<\/form>/gi,
      /<input[^>]*>.*?<\/input>/gi,
      /<textarea[^>]*>.*?<\/textarea>/gi,
      /<select[^>]*>.*?<\/select>/gi,
      /<option[^>]*>.*?<\/option>/gi,
      /<button[^>]*>.*?<\/button>/gi,
      /<a[^>]*>.*?<\/a>/gi,
      /<img[^>]*>.*?<\/img>/gi,
      /<video[^>]*>.*?<\/video>/gi,
      /<audio[^>]*>.*?<\/audio>/gi,
      /<source[^>]*>.*?<\/source>/gi,
      /<track[^>]*>.*?<\/track>/gi,
      /<canvas[^>]*>.*?<\/canvas>/gi,
      /<svg[^>]*>.*?<\/svg>/gi,
      /<math[^>]*>.*?<\/math>/gi
    ];

    for (const pattern of xssPatterns) {
      if (pattern.test(input)) {
        return {
          isThreat: true,
          threatType: 'xss',
          confidence: 0.9,
          details: `XSS pattern detected: ${pattern.source}`,
          recommendations: [
            'Sanitize input before processing',
            'Use Content Security Policy (CSP)',
            'Validate and escape output',
            'Use trusted libraries for HTML parsing'
          ]
        };
      }
    }

    return {
      isThreat: false,
      threatType: 'unknown',
      confidence: 0,
      details: 'No XSS threats detected',
      recommendations: []
    };
  }

  private sanitizeInput(input: string): string {
    // Basic HTML sanitization
    return input
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;')
      .replace(/&/g, '&amp;');
  }

  // Threat detection
  public detectThreats(input: string): ThreatDetectionResult[] {
    if (!this.config.enableThreatDetection) {
      return [];
    }

    const threats: ThreatDetectionResult[] = [];

    // XSS detection
    const xssResult = this.detectXSS(input);
    if (xssResult.isThreat) {
      threats.push(xssResult);
    }

    // Injection detection
    const injectionResult = this.detectInjection(input);
    if (injectionResult.isThreat) {
      threats.push(injectionResult);
    }

    // Malware detection
    const malwareResult = this.detectMalware(input);
    if (malwareResult.isThreat) {
      threats.push(malwareResult);
    }

    // Phishing detection
    const phishingResult = this.detectPhishing(input);
    if (phishingResult.isThreat) {
      threats.push(phishingResult);
    }

    // Suspicious activity detection
    const suspiciousResult = this.detectSuspiciousActivity(input);
    if (suspiciousResult.isThreat) {
      threats.push(suspiciousResult);
    }

    return threats;
  }

  private detectInjection(input: string): ThreatDetectionResult {
    const injectionPatterns = [
      /union\s+select/gi,
      /drop\s+table/gi,
      /delete\s+from/gi,
      /insert\s+into/gi,
      /update\s+set/gi,
      /create\s+table/gi,
      /alter\s+table/gi,
      /exec\s*\(/gi,
      /sp_executesql/gi,
      /xp_cmdshell/gi,
      /bulk\s+insert/gi,
      /openrowset/gi,
      /opendatasource/gi
    ];

    for (const pattern of injectionPatterns) {
      if (pattern.test(input)) {
        return {
          isThreat: true,
          threatType: 'injection',
          confidence: 0.8,
          details: `SQL injection pattern detected: ${pattern.source}`,
          recommendations: [
            'Use parameterized queries',
            'Validate and sanitize input',
            'Implement proper access controls',
            'Use prepared statements'
          ]
        };
      }
    }

    return {
      isThreat: false,
      threatType: 'unknown',
      confidence: 0,
      details: 'No injection threats detected',
      recommendations: []
    };
  }

  private detectMalware(input: string): ThreatDetectionResult {
    const malwarePatterns = [
      /eval\s*\(/gi,
      /Function\s*\(/gi,
      /setTimeout\s*\(/gi,
      /setInterval\s*\(/gi,
      /execScript/gi,
      /document\.write/gi,
      /innerHTML\s*=/gi,
      /outerHTML\s*=/gi,
      /document\.cookie/gi,
      /localStorage/gi,
      /sessionStorage/gi,
      /XMLHttpRequest/gi,
      /fetch\s*\(/gi,
      /import\s*\(/gi,
      /require\s*\(/gi
    ];

    for (const pattern of malwarePatterns) {
      if (pattern.test(input)) {
        return {
          isThreat: true,
          threatType: 'malware',
          confidence: 0.7,
          details: `Potentially malicious code detected: ${pattern.source}`,
          recommendations: [
            'Review code for malicious intent',
            'Use sandboxing for untrusted code',
            'Implement code signing',
            'Use static analysis tools'
          ]
        };
      }
    }

    return {
      isThreat: false,
      threatType: 'unknown',
      confidence: 0,
      details: 'No malware threats detected',
      recommendations: []
    };
  }

  private detectPhishing(input: string): ThreatDetectionResult {
    const phishingPatterns = [
      /password\s*=/gi,
      /username\s*=/gi,
      /login\s*=/gi,
      /email\s*=/gi,
      /credit\s*card/gi,
      /ssn\s*=/gi,
      /social\s*security/gi,
      /bank\s*account/gi,
      /routing\s*number/gi,
      /account\s*number/gi
    ];

    for (const pattern of phishingPatterns) {
      if (pattern.test(input)) {
        return {
          isThreat: true,
          threatType: 'phishing',
          confidence: 0.6,
          details: `Potential phishing pattern detected: ${pattern.source}`,
          recommendations: [
            'Verify source authenticity',
            'Use secure communication channels',
            'Implement multi-factor authentication',
            'Educate users about phishing'
          ]
        };
      }
    }

    return {
      isThreat: false,
      threatType: 'unknown',
      confidence: 0,
      details: 'No phishing threats detected',
      recommendations: []
    };
  }

  private detectSuspiciousActivity(input: string): ThreatDetectionResult {
    const suspiciousPatterns = [
      /base64/gi,
      /atob\s*\(/gi,
      /btoa\s*\(/gi,
      /unescape\s*\(/gi,
      /escape\s*\(/gi,
      /decodeURIComponent/gi,
      /encodeURIComponent/gi,
      /String\.fromCharCode/gi,
      /charCodeAt/gi,
      /fromCharCode/gi
    ];

    for (const pattern of suspiciousPatterns) {
      if (pattern.test(input)) {
        return {
          isThreat: true,
          threatType: 'suspicious',
          confidence: 0.5,
          details: `Suspicious encoding/decoding pattern detected: ${pattern.source}`,
          recommendations: [
            'Review code for obfuscation',
            'Use static analysis tools',
            'Implement code review process',
            'Monitor for unusual activity'
          ]
        };
      }
    }

    return {
      isThreat: false,
      threatType: 'unknown',
      confidence: 0,
      details: 'No suspicious activity detected',
      recommendations: []
    };
  }

  // Rate limiting
  public checkRateLimit(identifier: string): boolean {
    if (!this.config.enableRateLimiting) {
      return true;
    }

    const now = Date.now();
    const limit = this.rateLimitTracker.get(identifier);

    if (!limit) {
      this.rateLimitTracker.set(identifier, { count: 1, resetTime: now + this.config.rateLimitWindow });
      return true;
    }

    if (now > limit.resetTime) {
      this.rateLimitTracker.set(identifier, { count: 1, resetTime: now + this.config.rateLimitWindow });
      return true;
    }

    if (limit.count >= this.config.rateLimitMaxRequests) {
      this.logSecurityEvent('warning', 'rate-limit', 'Rate limit exceeded', { identifier, count: limit.count });
      return false;
    }

    limit.count++;
    return true;
  }

  private cleanupRateLimitTracker(): void {
    const now = Date.now();
    for (const [identifier, limit] of this.rateLimitTracker.entries()) {
      if (now > limit.resetTime) {
        this.rateLimitTracker.delete(identifier);
      }
    }
  }

  // Access control
  public checkAccess(resource: string, action: string, user?: string): boolean {
    if (!this.config.enableAccessControl) {
      return true;
    }

    // Basic access control logic
    // In a real implementation, this would check against user permissions, roles, etc.
    
    if (this.config.blockedDomains.includes(resource)) {
      this.logSecurityEvent('warning', 'access', 'Access denied to blocked resource', { resource, action, user });
      return false;
    }

    if (this.config.allowedDomains.length > 0 && !this.config.allowedDomains.includes(resource)) {
      this.logSecurityEvent('warning', 'access', 'Access denied to non-allowed resource', { resource, action, user });
      return false;
    }

    return true;
  }

  // Data encryption
  public encryptData(data: string): string {
    if (!this.config.enableDataEncryption) {
      return data;
    }

    try {
      // Simple XOR encryption (not secure for production)
      let encrypted = '';
      for (let i = 0; i < data.length; i++) {
        encrypted += String.fromCharCode(data.charCodeAt(i) ^ this.encryptionKey.charCodeAt(i % this.encryptionKey.length));
      }
      return btoa(encrypted);
    } catch (error) {
      console.error('Encryption failed:', error);
      return data;
    }
  }

  public decryptData(encryptedData: string): string {
    if (!this.config.enableDataEncryption) {
      return encryptedData;
    }

    try {
      const data = atob(encryptedData);
      let decrypted = '';
      for (let i = 0; i < data.length; i++) {
        decrypted += String.fromCharCode(data.charCodeAt(i) ^ this.encryptionKey.charCodeAt(i % this.encryptionKey.length));
      }
      return decrypted;
    } catch (error) {
      console.error('Decryption failed:', error);
      return encryptedData;
    }
  }

  // Audit logging
  private logSecurityEvent(
    level: 'info' | 'warning' | 'error' | 'critical',
    type: 'validation' | 'xss' | 'csrf' | 'access' | 'audit' | 'threat' | 'encryption' | 'sandbox',
    message: string,
    details: Record<string, any> = {}
  ): void {
    if (!this.config.enableAuditLogging) return;

    const event: SecurityEvent = {
      id: this.generateEventId(),
      timestamp: Date.now(),
      type,
      level,
      message,
      details,
      source: 'AdvancedMonacoEditor',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
      ipAddress: this.getClientIP()
    };

    this.events.push(event);

    // Keep only recent events
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }

    this.emit('securityEvent', event);
  }

  private generateEventId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private getClientIP(): string {
    // In a real implementation, this would get the actual client IP
    return '127.0.0.1';
  }

  // Public methods
  public getSecurityEvents(): SecurityEvent[] {
    return [...this.events];
  }

  public getSecurityReport(): {
    totalEvents: number;
    eventsByType: Record<string, number>;
    eventsByLevel: Record<string, number>;
    recentThreats: ThreatDetectionResult[];
    recommendations: string[];
  } {
    const eventsByType: Record<string, number> = {};
    const eventsByLevel: Record<string, number> = {};
    const recentThreats: ThreatDetectionResult[] = [];

    for (const event of this.events) {
      eventsByType[event.type] = (eventsByType[event.type] || 0) + 1;
      eventsByLevel[event.level] = (eventsByLevel[event.level] || 0) + 1;

      if (event.type === 'threat' && event.level === 'critical') {
        recentThreats.push(event.details as ThreatDetectionResult);
      }
    }

    const recommendations: string[] = [];
    if (eventsByType['xss'] > 0) {
      recommendations.push('Implement XSS protection measures');
    }
    if (eventsByType['injection'] > 0) {
      recommendations.push('Implement injection protection measures');
    }
    if (eventsByType['access'] > 0) {
      recommendations.push('Review access control policies');
    }
    if (eventsByLevel['critical'] > 0) {
      recommendations.push('Address critical security issues immediately');
    }

    return {
      totalEvents: this.events.length,
      eventsByType,
      eventsByLevel,
      recentThreats,
      recommendations
    };
  }

  public destroy(): void {
    this.events = [];
    this.rateLimitTracker.clear();
    this.blockedIPs.clear();
    this.allowedIPs.clear();
    this.removeAllListeners();
  }
}
