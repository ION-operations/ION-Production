/**
 * PLIx Comparison Matrix System
 * 
 * Manages comparison matrix for research findings
 */

import { PLIxComparisonEntry } from './models/research';

export class PLIxComparisonMatrix {
  private entries: Map<string, PLIxComparisonEntry> = new Map();

  /**
   * Add or update a comparison entry
   */
  addEntry(entry: PLIxComparisonEntry): void {
    this.entries.set(entry.system, entry);
  }

  /**
   * Get entry by system name
   */
  getEntry(system: string): PLIxComparisonEntry | undefined {
    return this.entries.get(system);
  }

  /**
   * Get all entries
   */
  getAllEntries(): PLIxComparisonEntry[] {
    return Array.from(this.entries.values());
  }

  /**
   * Get entries by family
   */
  getEntriesByFamily(family: PLIxComparisonEntry['family']): PLIxComparisonEntry[] {
    return Array.from(this.entries.values()).filter(e => e.family === family);
  }

  /**
   * Get top entries by score (average of all dimensions)
   */
  getTopEntries(limit: number = 10): PLIxComparisonEntry[] {
    return Array.from(this.entries.values())
      .map(entry => ({
        entry,
        avgScore: (
          entry.intent_contracts +
          entry.recoverable_conditions +
          entry.evidence_provenance +
          entry.policy_gates +
          entry.ide_fit
        ) / 5,
      }))
      .sort((a, b) => b.avgScore - a.avgScore)
      .slice(0, limit)
      .map(item => item.entry);
  }

  /**
   * Export to CSV format
   */
  exportToCSV(): string {
    const headers = [
      'System',
      'Family',
      'Intent Contracts',
      'Recoverable Conditions',
      'Evidence/Provenance',
      'Policy Gates',
      'Interop Targets',
      'IDE Fit',
      'License',
      'Maturity',
      'Notes',
    ];

    const rows = Array.from(this.entries.values()).map(entry => [
      entry.system,
      entry.family,
      entry.intent_contracts.toString(),
      entry.recoverable_conditions.toString(),
      entry.evidence_provenance.toString(),
      entry.policy_gates.toString(),
      entry.interop_targets.join('; '),
      entry.ide_fit.toString(),
      entry.license,
      entry.maturity,
      entry.notes || '',
    ]);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  }

  /**
   * Export to Markdown table
   */
  exportToMarkdown(): string {
    const headers = [
      'System',
      'Family',
      'Intent Contracts',
      'Recoverable Conditions',
      'Evidence/Provenance',
      'Policy Gates',
      'Interop Targets',
      'IDE Fit',
      'License',
      'Maturity',
    ];

    const headerRow = `| ${headers.join(' | ')} |`;
    const separatorRow = `| ${headers.map(() => '---').join(' | ')} |`;

    const rows = Array.from(this.entries.values()).map(entry => {
      return `| ${[
        entry.system,
        entry.family,
        entry.intent_contracts.toString(),
        entry.recoverable_conditions.toString(),
        entry.evidence_provenance.toString(),
        entry.policy_gates.toString(),
        entry.interop_targets.join(', '),
        entry.ide_fit.toString(),
        entry.license,
        entry.maturity,
      ].join(' | ')} |`;
    });

    return [headerRow, separatorRow, ...rows].join('\n');
  }
}

