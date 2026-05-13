/**
 * Security Service Tests
 * 
 * Comprehensive unit tests for the SecurityService class
 */

import { SecurityService, SecurityConfig, ValidationResult, ThreatDetectionResult } from '../src/services/SecurityService';

describe('SecurityService', () => {
  let securityService: SecurityService;

  beforeEach(() => {
    securityService = new SecurityService({
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
      blockedDomains: ['malicious.com'],
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
      auditLogLevel: 'medium'
    });
  });

  afterEach(() => {
    securityService.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      const defaultService = new SecurityService();
      expect(defaultService).toBeDefined();
      expect(defaultService.getConfig().enableInputValidation).toBe(true);
      expect(defaultService.getConfig().enableXSSProtection).toBe(true);
      defaultService.destroy();
    });

    it('should initialize with custom configuration', () => {
      const customConfig: Partial<SecurityConfig> = {
        enableInputValidation: false,
        enableXSSProtection: false,
        maxCodeSize: 2 * 1024 * 1024
      };

      const customService = new SecurityService(customConfig);
      expect(customService.getConfig().enableInputValidation).toBe(false);
      expect(customService.getConfig().enableXSSProtection).toBe(false);
      expect(customService.getConfig().maxCodeSize).toBe(2 * 1024 * 1024);
      customService.destroy();
    });
  });

  describe('Input Validation', () => {
    it('should validate valid input', () => {
      const result = securityService.validateInput('valid input', 'general');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.warnings).toHaveLength(0);
      expect(result.riskLevel).toBe('low');
    });

    it('should validate input size', () => {
      const largeInput = 'a'.repeat(2 * 1024 * 1024); // 2MB
      const result = securityService.validateInput(largeInput, 'general');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toContain('exceeds maximum size limit');
      expect(result.riskLevel).toBe('high');
    });

    it('should detect XSS threats', () => {
      const xssInput = '<script>alert("xss")</script>';
      const result = securityService.validateInput(xssInput, 'general');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toContain('XSS threat detected');
      expect(result.riskLevel).toBe('critical');
    });

    it('should sanitize XSS input', () => {
      const xssInput = '<script>alert("xss")</script>';
      const result = securityService.validateInput(xssInput, 'general');
      expect(result.sanitizedInput).not.toContain('<script>');
      expect(result.sanitizedInput).toContain('&lt;script&gt;');
    });

    it('should validate code context', () => {
      const codeInput = 'function test() { console.log("hello"); }';
      const result = securityService.validateInput(codeInput, 'code');
      expect(result.isValid).toBe(true);
      expect(result.warnings).toHaveLength(0);
    });

    it('should validate URL context', () => {
      const validUrl = 'https://example.com';
      const result = securityService.validateInput(validUrl, 'url');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject invalid URL', () => {
      const invalidUrl = 'not-a-url';
      const result = securityService.validateInput(invalidUrl, 'url');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toContain('Invalid URL format');
    });

    it('should reject blocked domain', () => {
      const blockedUrl = 'https://malicious.com';
      const result = securityService.validateInput(blockedUrl, 'url');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toContain('Blocked domain');
      expect(result.riskLevel).toBe('critical');
    });

    it('should reject non-allowed domain', () => {
      const nonAllowedUrl = 'https://external.com';
      const result = securityService.validateInput(nonAllowedUrl, 'url');
      expect(result.isValid).toBe(false);
      expect(result.errors).toHaveLength(1);
      expect(result.errors[0].message).toContain('Domain not in allowed list');
      expect(result.riskLevel).toBe('high');
    });

    it('should accept allowed domain', () => {
      const allowedUrl = 'https://localhost';
      const result = securityService.validateInput(allowedUrl, 'url');
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });
  });

  describe('Threat Detection', () => {
    it('should detect XSS threats', () => {
      const xssInput = '<script>alert("xss")</script>';
      const threats = securityService.detectThreats(xssInput);
      expect(threats).toHaveLength(1);
      expect(threats[0].isThreat).toBe(true);
      expect(threats[0].threatType).toBe('xss');
      expect(threats[0].confidence).toBeGreaterThan(0.8);
    });

    it('should detect injection threats', () => {
      const injectionInput = "SELECT * FROM users WHERE id = '1' OR '1'='1'";
      const threats = securityService.detectThreats(injectionInput);
      expect(threats).toHaveLength(1);
      expect(threats[0].isThreat).toBe(true);
      expect(threats[0].threatType).toBe('injection');
      expect(threats[0].confidence).toBeGreaterThan(0.7);
    });

    it('should detect malware threats', () => {
      const malwareInput = 'eval("malicious code")';
      const threats = securityService.detectThreats(malwareInput);
      expect(threats).toHaveLength(1);
      expect(threats[0].isThreat).toBe(true);
      expect(threats[0].threatType).toBe('malware');
      expect(threats[0].confidence).toBeGreaterThan(0.6);
    });

    it('should detect phishing threats', () => {
      const phishingInput = 'password=123456&username=admin';
      const threats = securityService.detectThreats(phishingInput);
      expect(threats).toHaveLength(1);
      expect(threats[0].isThreat).toBe(true);
      expect(threats[0].threatType).toBe('phishing');
      expect(threats[0].confidence).toBeGreaterThan(0.5);
    });

    it('should detect suspicious activity', () => {
      const suspiciousInput = 'base64encodedstring';
      const threats = securityService.detectThreats(suspiciousInput);
      expect(threats).toHaveLength(1);
      expect(threats[0].isThreat).toBe(true);
      expect(threats[0].threatType).toBe('suspicious');
      expect(threats[0].confidence).toBeGreaterThan(0.4);
    });

    it('should not detect threats in clean input', () => {
      const cleanInput = 'This is a normal text input';
      const threats = securityService.detectThreats(cleanInput);
      expect(threats).toHaveLength(0);
    });
  });

  describe('Rate Limiting', () => {
    it('should allow requests within rate limit', () => {
      const identifier = 'test-user';
      const allowed = securityService.checkRateLimit(identifier);
      expect(allowed).toBe(true);
    });

    it('should block requests exceeding rate limit', () => {
      const identifier = 'test-user';
      const config = securityService.getConfig();
      
      // Make requests up to the limit
      for (let i = 0; i < config.rateLimitMaxRequests; i++) {
        const allowed = securityService.checkRateLimit(identifier);
        expect(allowed).toBe(true);
      }
      
      // Next request should be blocked
      const blocked = securityService.checkRateLimit(identifier);
      expect(blocked).toBe(false);
    });

    it('should reset rate limit after window', (done) => {
      const identifier = 'test-user';
      const config = securityService.getConfig();
      
      // Make requests up to the limit
      for (let i = 0; i < config.rateLimitMaxRequests; i++) {
        securityService.checkRateLimit(identifier);
      }
      
      // Should be blocked
      expect(securityService.checkRateLimit(identifier)).toBe(false);
      
      // Wait for rate limit window to reset
      setTimeout(() => {
        const allowed = securityService.checkRateLimit(identifier);
        expect(allowed).toBe(true);
        done();
      }, config.rateLimitWindow + 100);
    });
  });

  describe('Access Control', () => {
    it('should allow access to allowed resource', () => {
      const allowed = securityService.checkAccess('localhost', 'read', 'test-user');
      expect(allowed).toBe(true);
    });

    it('should deny access to blocked resource', () => {
      const allowed = securityService.checkAccess('malicious.com', 'read', 'test-user');
      expect(allowed).toBe(false);
    });

    it('should deny access to non-allowed resource', () => {
      const allowed = securityService.checkAccess('external.com', 'read', 'test-user');
      expect(allowed).toBe(false);
    });
  });

  describe('Data Encryption', () => {
    it('should encrypt data when enabled', () => {
      const service = new SecurityService({ enableDataEncryption: true });
      const data = 'sensitive data';
      const encrypted = service.encryptData(data);
      expect(encrypted).not.toBe(data);
      expect(encrypted).toBeDefined();
      service.destroy();
    });

    it('should decrypt data when enabled', () => {
      const service = new SecurityService({ enableDataEncryption: true });
      const data = 'sensitive data';
      const encrypted = service.encryptData(data);
      const decrypted = service.decryptData(encrypted);
      expect(decrypted).toBe(data);
      service.destroy();
    });

    it('should not encrypt data when disabled', () => {
      const data = 'sensitive data';
      const encrypted = securityService.encryptData(data);
      expect(encrypted).toBe(data);
    });

    it('should not decrypt data when disabled', () => {
      const data = 'sensitive data';
      const decrypted = securityService.decryptData(data);
      expect(decrypted).toBe(data);
    });
  });

  describe('Audit Logging', () => {
    it('should log security events', (done) => {
      securityService.on('securityEvent', (event) => {
        expect(event).toBeDefined();
        expect(event.id).toBeDefined();
        expect(event.timestamp).toBeDefined();
        expect(event.type).toBeDefined();
        expect(event.level).toBeDefined();
        expect(event.message).toBeDefined();
        expect(event.details).toBeDefined();
        expect(event.source).toBe('AdvancedMonacoEditor');
        done();
      });

      // Trigger a security event
      securityService.validateInput('<script>alert("xss")</script>', 'general');
    });

    it('should get security events', () => {
      // Trigger some security events
      securityService.validateInput('<script>alert("xss")</script>', 'general');
      securityService.validateInput('https://malicious.com', 'url');
      
      const events = securityService.getSecurityEvents();
      expect(events.length).toBeGreaterThan(0);
    });

    it('should get security report', () => {
      // Trigger some security events
      securityService.validateInput('<script>alert("xss")</script>', 'general');
      securityService.validateInput('https://malicious.com', 'url');
      
      const report = securityService.getSecurityReport();
      expect(report).toBeDefined();
      expect(report.totalEvents).toBeGreaterThan(0);
      expect(report.eventsByType).toBeDefined();
      expect(report.eventsByLevel).toBeDefined();
      expect(report.recentThreats).toBeDefined();
      expect(report.recommendations).toBeDefined();
    });
  });

  describe('Configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        enableInputValidation: false,
        maxCodeSize: 2 * 1024 * 1024
      };

      securityService.updateConfig(newConfig);
      const config = securityService.getConfig();
      expect(config.enableInputValidation).toBe(false);
      expect(config.maxCodeSize).toBe(2 * 1024 * 1024);
    });

    it('should merge configuration properly', () => {
      const newConfig = {
        alertThresholds: {
          memory: 90,
          cpu: 80
        }
      };

      securityService.updateConfig(newConfig);
      const config = securityService.getConfig();
      expect(config.alertThresholds.memory).toBe(90);
      expect(config.alertThresholds.cpu).toBe(80);
      expect(config.alertThresholds.render).toBe(20); // Should preserve existing value
    });
  });

  describe('Error Handling', () => {
    it('should handle validation errors gracefully', () => {
      // Mock validator to throw error
      const originalValidateInput = securityService.validateInput;
      securityService.validateInput = jest.fn().mockImplementation(() => {
        throw new Error('Validation error');
      });

      // Should not throw error
      expect(() => {
        securityService.validateInput('test input', 'general');
      }).not.toThrow();

      // Restore original method
      securityService.validateInput = originalValidateInput;
    });

    it('should handle encryption errors gracefully', () => {
      const service = new SecurityService({ enableDataEncryption: true });
      
      // Mock crypto to throw error
      const originalGetRandomValues = crypto.getRandomValues;
      crypto.getRandomValues = jest.fn().mockImplementation(() => {
        throw new Error('Crypto error');
      });

      // Should not throw error
      expect(() => {
        service.encryptData('test data');
      }).not.toThrow();

      // Restore original method
      crypto.getRandomValues = originalGetRandomValues;
      service.destroy();
    });
  });

  describe('Cleanup', () => {
    it('should destroy service', () => {
      // Trigger some events
      securityService.validateInput('<script>alert("xss")</script>', 'general');
      securityService.checkRateLimit('test-user');
      
      const events = securityService.getSecurityEvents();
      expect(events.length).toBeGreaterThan(0);
      
      securityService.destroy();
      
      const eventsAfterDestroy = securityService.getSecurityEvents();
      expect(eventsAfterDestroy.length).toBe(0);
    });
  });
});
