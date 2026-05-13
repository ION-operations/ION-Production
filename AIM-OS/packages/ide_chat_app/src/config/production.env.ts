/**
 * Production Environment Configuration
 * Centralized environment variables for production deployment
 */

export const productionEnv = {
  // Environment
  NODE_ENV: 'production' as const,
  
  // API Configuration
  API_BASE_URL: 'https://api.aimos.dev',
  API_TIMEOUT: 30000,
  
  // AIM-OS Configuration
  AIMOS_ENABLED: true,
  AIMOS_FALLBACK: false,
  AIMOS_TIMEOUT: 10000,
  
  // Error Handling
  ERROR_REPORTING: true,
  ERROR_RECOVERY: true,
  
  // Performance
  LAZY_LOADING: true,
  CODE_SPLITTING: true,
  CACHING: true,
  
  // Monitoring
  METRICS_ENABLED: true,
  LOGGING_ENABLED: true,
  LOG_LEVEL: 'warn' as const,
  
  // Security
  CSP_ENABLED: true,
  HTTPS_ENABLED: true,
  CORS_ENABLED: true,
  
  // Build Configuration
  BUILD_OPTIMIZE: true,
  BUILD_MINIFY: true,
  BUILD_SOURCEMAP: false,
}

export default productionEnv
