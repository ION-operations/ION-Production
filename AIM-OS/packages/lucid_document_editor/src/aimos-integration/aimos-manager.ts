/**
 * LUCID Document Editor - AIM-OS Integration Manager
 * 
 * Unified interface for all AIM-OS system integrations
 */

import { DocumentModel } from '../models';
import { CMCIntegration, CMCConfig } from './cmc-integration';
import { VIFIntegration, VIFConfig } from './vif-integration';
import { SEGIntegration, SEGConfig } from './seg-integration';
import { HHNIIntegration, HHNIConfig } from './hhni-integration';
import { APOEIntegration, APOEConfig } from './apoe-integration';
import { DocumentExporter } from './export-import';

export interface AIMOSConfig {
  cmc?: CMCConfig;
  vif?: VIFConfig;
  seg?: SEGConfig;
  hhni?: HHNIConfig;
  apoe?: APOEConfig;
}

export class AIMOSIntegrationManager {
  private cmc: CMCIntegration;
  private vif: VIFIntegration;
  private seg: SEGIntegration;
  private hhni: HHNIIntegration;
  private apoe: APOEIntegration;

  constructor(config: AIMOSConfig = {}) {
    this.cmc = new CMCIntegration(config.cmc || {});
    this.vif = new VIFIntegration(config.vif || {});
    this.seg = new SEGIntegration(config.seg || {});
    this.hhni = new HHNIIntegration(config.hhni || {});
    this.apoe = new APOEIntegration(config.apoe || {});
  }

  /**
   * Save document with full AIM-OS integration
   */
  async saveDocument(document: DocumentModel): Promise<{
    atomId: string;
    witnessId: string;
    entityId: string;
  }> {
    // Store in CMC
    const atomId = await this.cmc.storeDocument(document);

    // Create VIF witness
    const witness = await this.vif.createWitness({
      operation: 'document_save',
      inputs: { documentId: document.id },
      outputs: { atomId },
      confidence: 0.95,
    });

    // Link to SEG
    const entityId = await this.seg.linkDocument(document);

    // Index in HHNI
    await this.hhni.indexDocument(document);

    return { atomId, witnessId: witness.id, entityId };
  }

  /**
   * Load document with full AIM-OS integration
   */
  async loadDocument(atomId: string): Promise<DocumentModel | null> {
    return await this.cmc.loadDocument(atomId);
  }

  /**
   * Export document
   */
  async exportDocument(
    document: DocumentModel,
    format: 'json' | 'markdown' | 'latex' | 'html' | 'pdf',
    options?: Partial<{
      includeMetadata: boolean;
      includeHistory: boolean;
      includeComments: boolean;
      compress: boolean;
    }>
  ): Promise<string | Blob> {
    return DocumentExporter.exportDocument(document, {
      format,
      includeMetadata: options?.includeMetadata ?? true,
      includeHistory: options?.includeHistory ?? false,
      includeComments: options?.includeComments ?? false,
      compress: options?.compress ?? false,
    });
  }

  /**
   * Import document
   */
  async importDocument(
    content: string,
    format: 'json' | 'markdown' | 'latex' | 'html',
    options?: Partial<{
      merge: boolean;
      preserveHistory: boolean;
    }>
  ): Promise<DocumentModel> {
    return DocumentExporter.importDocument(content, {
      format,
      merge: options?.merge ?? false,
      preserveHistory: options?.preserveHistory ?? false,
    });
  }

  /**
   * Semantic search
   */
  async semanticSearch(query: string, limit: number = 10): Promise<any[]> {
    return await this.hhni.search({ query, limit });
  }

  /**
   * Get related documents
   */
  async getRelatedDocuments(documentId: string, limit: number = 10): Promise<string[]> {
    return await this.seg.findRelatedDocuments(documentId, limit);
  }

  /**
   * Create execution plan
   */
  async createPlan(goal: string, priority: 'low' | 'medium' | 'high' | 'critical' = 'medium'): Promise<any> {
    return await this.apoe.createPlan({ goal, priority });
  }
}

