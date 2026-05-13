/**
 * LUCID Document Editor - Document Model
 * 
 * Core data structures for representing documents with sections, math, tags, and metadata
 */

export interface DocumentSection {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'math' | 'code' | 'mixed';
  tags: string[];
  metadata: SectionMetadata;
  version: number;
  locked: boolean;
  lockedBy?: string;
  createdAt: string;
  updatedAt: string;
}

export interface SectionMetadata {
  wordCount?: number;
  mathBlockCount?: number;
  codeBlockCount?: number;
  readingTime?: number;
  complexity?: number;
  aiTags?: string[];
  citations?: Citation[];
}

export interface Citation {
  id: string;
  type: 'url' | 'doi' | 'arxiv' | 'book' | 'paper';
  reference: string;
  title?: string;
  authors?: string[];
  year?: number;
  position: { sectionId: string; offset: number };
}

export interface DocumentTag {
  id: string;
  name: string;
  category: 'topic' | 'concept' | 'method' | 'reference' | 'custom';
  color?: string;
  description?: string;
  aiGenerated: boolean;
  confidence?: number;
}

export interface DocumentChange {
  id: string;
  sectionId: string;
  type: 'insert' | 'delete' | 'replace' | 'format';
  before?: string;
  after?: string;
  timestamp: string;
  author: string;
  metadata?: Record<string, unknown>;
}

export interface DocumentModel {
  id: string;
  title: string;
  description?: string;
  sections: DocumentSection[];
  tags: DocumentTag[];
  metadata: DocumentMetadata;
  version: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  collaborators?: string[];
}

export interface DocumentMetadata {
  totalWords: number;
  totalSections: number;
  totalMathBlocks: number;
  totalCodeBlocks: number;
  estimatedReadingTime: number;
  language: string;
  template?: string;
  aiManaged: boolean;
  lastAiUpdate?: string;
}

export interface DocumentState {
  document: DocumentModel;
  activeSectionId?: string;
  selection?: {
    sectionId: string;
    start: number;
    end: number;
  };
  changes: DocumentChange[];
  unsavedChanges: boolean;
}

export interface MathBlock {
  id: string;
  content: string;
  format: 'latex' | 'mathml' | 'asciimath';
  display: 'inline' | 'block';
  sectionId: string;
  position: number;
}

export interface SaveOptions {
  format: 'json' | 'markdown' | 'latex' | 'html';
  includeMetadata: boolean;
  includeHistory: boolean;
  compress: boolean;
}

export interface LoadOptions {
  format: 'json' | 'markdown' | 'latex' | 'html';
  merge: boolean;
  preserveHistory: boolean;
}

