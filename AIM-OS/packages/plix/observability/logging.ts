/**
 * PLIx Observability: Structured Logging
 * 
 * Provides structured logging with context and tracing
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  FATAL = 4
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  component: string;
  context?: Record<string, any>;
  traceId?: string;
  spanId?: string;
  error?: Error;
}

export interface LoggerConfig {
  level: LogLevel;
  output: 'console' | 'file' | 'both';
  filePath?: string;
  pretty?: boolean;
  includeStackTrace?: boolean;
}

/**
 * Structured Logger
 */
export class Logger {
  private config: LoggerConfig;
  private component: string;
  
  constructor(component: string, config: Partial<LoggerConfig> = {}) {
    this.component = component;
    this.config = {
      level: config.level || LogLevel.INFO,
      output: config.output || 'console',
      pretty: config.pretty !== false,
      includeStackTrace: config.includeStackTrace || false,
      ...config
    };
  }
  
  debug(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context);
  }
  
  info(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context);
  }
  
  warn(message: string, context?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context);
  }
  
  error(message: string, error?: Error, context?: Record<string, any>): void {
    this.log(LogLevel.ERROR, message, { ...context, error });
  }
  
  fatal(message: string, error?: Error, context?: Record<string, any>): void {
    this.log(LogLevel.FATAL, message, { ...context, error });
  }
  
  private log(level: LogLevel, message: string, context?: Record<string, any>): void {
    if (level < this.config.level) return;
    
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      component: this.component,
      context,
      traceId: (context as any)?.traceId,
      spanId: (context as any)?.spanId,
      error: (context as any)?.error
    };
    
    this.output(entry);
  }
  
  private output(entry: LogEntry): void {
    const formatted = this.config.pretty ? this.formatPretty(entry) : JSON.stringify(entry);
    
    if (this.config.output === 'console' || this.config.output === 'both') {
      console.log(formatted);
    }
    
    // File output would go here
  }
  
  private formatPretty(entry: LogEntry): string {
    const levelName = LogLevel[entry.level];
    const context = entry.context ? ` ${JSON.stringify(entry.context)}` : '';
    return `[${entry.timestamp}] ${levelName} [${entry.component}] ${entry.message}${context}`;
  }
}

/**
 * Global logger factory
 */
export const createLogger = (component: string, config?: Partial<LoggerConfig>): Logger => {
  return new Logger(component, config);
};

