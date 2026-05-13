/**
 * PLIx Observability: Metrics
 * 
 * Provides metrics collection and reporting (Prometheus-compatible)
 */

export interface Metric {
  name: string;
  type: 'counter' | 'gauge' | 'histogram' | 'summary';
  help: string;
  value: number | number[];
  labels?: Record<string, string>;
  timestamp: number;
}

/**
 * Metrics Registry
 */
export class MetricsRegistry {
  private metrics: Map<string, Metric>;
  
  constructor() {
    this.metrics = new Map();
  }
  
  /**
   * Increment counter
   */
  incrementCounter(name: string, labels?: Record<string, string>, value: number = 1): void {
    const key = this.getKey(name, labels);
    const metric = this.metrics.get(key);
    
    if (metric) {
      metric.value = (metric.value as number) + value;
      metric.timestamp = Date.now();
    } else {
      this.metrics.set(key, {
        name,
        type: 'counter',
        help: `Counter for ${name}`,
        value,
        labels,
        timestamp: Date.now()
      });
    }
  }
  
  /**
   * Set gauge value
   */
  setGauge(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.getKey(name, labels);
    this.metrics.set(key, {
      name,
      type: 'gauge',
      help: `Gauge for ${name}`,
      value,
      labels,
      timestamp: Date.now()
    });
  }
  
  /**
   * Observe histogram value
   */
  observeHistogram(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.getKey(name, labels);
    const metric = this.metrics.get(key);
    
    if (metric && Array.isArray(metric.value)) {
      metric.value.push(value);
      metric.timestamp = Date.now();
    } else {
      this.metrics.set(key, {
        name,
        type: 'histogram',
        help: `Histogram for ${name}`,
        value: [value],
        labels,
        timestamp: Date.now()
      });
    }
  }
  
  /**
   * Get all metrics
   */
  getMetrics(): Metric[] {
    return Array.from(this.metrics.values());
  }
  
  /**
   * Export metrics in Prometheus format
   */
  exportPrometheus(): string {
    const lines: string[] = [];
    
    for (const metric of this.metrics.values()) {
      // HELP line
      lines.push(`# HELP ${metric.name} ${metric.help}`);
      
      // TYPE line
      lines.push(`# TYPE ${metric.name} ${metric.type}`);
      
      // Metric line
      const labels = metric.labels ? this.formatLabels(metric.labels) : '';
      
      if (metric.type === 'histogram' && Array.isArray(metric.value)) {
        const values = metric.value as number[];
        lines.push(`${metric.name}_count${labels} ${values.length}`);
        lines.push(`${metric.name}_sum${labels} ${values.reduce((a, b) => a + b, 0)}`);
      } else {
        lines.push(`${metric.name}${labels} ${metric.value}`);
      }
      
      lines.push('');
    }
    
    return lines.join('\n');
  }
  
  private getKey(name: string, labels?: Record<string, string>): string {
    const labelStr = labels ? JSON.stringify(labels) : '';
    return `${name}:${labelStr}`;
  }
  
  private formatLabels(labels: Record<string, string>): string {
    const pairs = Object.entries(labels).map(([k, v]) => `${k}="${v}"`);
    return `{${pairs.join(',')}}`;
  }
}

// Global registry
export const metrics = new MetricsRegistry();

// Standard metrics
export const PLIxMetrics = {
  parseCount: (status: 'success' | 'failure') => 
    metrics.incrementCounter('plix_parse_total', { status }),
  
  parseLatency: (durationMs: number) => 
    metrics.observeHistogram('plix_parse_duration_ms', durationMs),
  
  compileCount: (status: 'success' | 'failure') => 
    metrics.incrementCounter('plix_compile_total', { status }),
  
  compileLatency: (durationMs: number) => 
    metrics.observeHistogram('plix_compile_duration_ms', durationMs),
  
  intentCount: (speechAct: string) => 
    metrics.incrementCounter('plix_intent_total', { speech_act: speechAct }),
  
  stepCount: (count: number) => 
    metrics.setGauge('plix_plan_steps', count),
  
  confidence: (value: number) => 
    metrics.observeHistogram('plix_confidence', value),
  
  testPass: () => 
    metrics.incrementCounter('plix_test_passed'),
  
  testFail: () => 
    metrics.incrementCounter('plix_test_failed')
};

