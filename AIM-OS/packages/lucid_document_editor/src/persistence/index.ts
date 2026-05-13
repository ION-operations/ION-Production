/**
 * LUCID Document Editor - Document Persistence
 * 
 * Save/load functionality for documents
 */

import { DocumentModel, SaveOptions, LoadOptions } from './models';

export class DocumentPersistence {
  /**
   * Save document to JSON format
   */
  static saveToJSON(document: DocumentModel, options: SaveOptions = { format: 'json', includeMetadata: true, includeHistory: false, compress: false }): string {
    const data: any = {
      id: document.id,
      title: document.title,
      description: document.description,
      sections: document.sections,
      tags: document.tags,
      version: document.version,
      createdAt: document.createdAt,
      updatedAt: document.updatedAt,
      createdBy: document.createdBy,
      collaborators: document.collaborators,
    };

    if (options.includeMetadata) {
      data.metadata = document.metadata;
    }

    const json = JSON.stringify(data, null, 2);

    if (options.compress) {
      // TODO: Implement compression (gzip/lz4)
      return json;
    }

    return json;
  }

  /**
   * Load document from JSON format
   */
  static loadFromJSON(json: string, options: LoadOptions = { format: 'json', merge: false, preserveHistory: false }): DocumentModel {
    const data = JSON.parse(json);

    const document: DocumentModel = {
      id: data.id || `doc-${Date.now()}`,
      title: data.title || 'Untitled Document',
      description: data.description,
      sections: data.sections || [],
      tags: data.tags || [],
      metadata: data.metadata || {
        totalWords: 0,
        totalSections: data.sections?.length || 0,
        totalMathBlocks: 0,
        totalCodeBlocks: 0,
        estimatedReadingTime: 0,
        language: 'en',
        aiManaged: false,
      },
      version: data.version || 1,
      createdAt: data.createdAt || new Date().toISOString(),
      updatedAt: data.updatedAt || new Date().toISOString(),
      createdBy: data.createdBy || 'user',
      collaborators: data.collaborators,
    };

    return document;
  }

  /**
   * Save document to localStorage
   */
  static saveToLocalStorage(document: DocumentModel, key: string = 'lucid-document'): void {
    const json = this.saveToJSON(document);
    localStorage.setItem(key, json);
  }

  /**
   * Load document from localStorage
   */
  static loadFromLocalStorage(key: string = 'lucid-document'): DocumentModel | null {
    const json = localStorage.getItem(key);
    if (!json) return null;
    return this.loadFromJSON(json);
  }

  /**
   * Export document to Markdown format
   */
  static exportToMarkdown(document: DocumentModel): string {
    let markdown = `# ${document.title}\n\n`;
    
    if (document.description) {
      markdown += `${document.description}\n\n`;
    }

    for (const section of document.sections) {
      markdown += `## ${section.title}\n\n`;
      markdown += `${section.content}\n\n`;
    }

    return markdown;
  }

  /**
   * Import document from Markdown format
   */
  static importFromMarkdown(markdown: string): DocumentModel {
    const lines = markdown.split('\n');
    const sections: DocumentModel['sections'] = [];
    let currentSection: { title: string; content: string[] } | null = null;
    let title = 'Untitled Document';
    let hasSections = false;

    // Extract title from first H1
    if (lines[0]?.startsWith('# ')) {
      title = lines[0].substring(2).trim();
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      if (line.startsWith('## ')) {
        hasSections = true;
        // Save previous section
        if (currentSection) {
          sections.push({
            id: `section-${sections.length}`,
            title: currentSection.title,
            content: currentSection.content.join('\n').trim(),
            type: 'text',
            tags: [],
            metadata: {},
            version: 1,
            locked: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          });
        }
        
        // Start new section
        currentSection = {
          title: line.substring(3).trim() || 'Untitled Section',
          content: [],
        };
      } else if (line.startsWith('# ')) {
        // Skip main title (already extracted)
        continue;
      } else if (currentSection) {
        currentSection.content.push(line);
      } else {
        // Content before any sections - create initial section
        if (!hasSections && line.trim()) {
          if (!currentSection) {
            currentSection = {
              title: 'Content',
              content: [],
            };
          }
          currentSection.content.push(line);
        }
      }
    }

    // Save last section
    if (currentSection) {
      sections.push({
        id: `section-${sections.length}`,
        title: currentSection.title,
        content: currentSection.content.join('\n').trim(),
        type: 'text',
        tags: [],
        metadata: {},
        version: 1,
        locked: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }

    // If no sections created, create one with all content
    if (sections.length === 0) {
      sections.push({
        id: 'section-0',
        title: 'Content',
        content: markdown.trim(),
        type: 'text',
        tags: [],
        metadata: {},
        version: 1,
        locked: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      });
    }

    const wordCount = markdown.split(/\s+/).filter(w => w.length > 0).length;

    return {
      id: `doc-${Date.now()}`,
      title,
      sections,
      tags: [],
      metadata: {
        totalWords: wordCount,
        totalSections: sections.length,
        totalMathBlocks: (markdown.match(/\$\$[\s\S]*?\$\$/g) || []).length,
        totalCodeBlocks: (markdown.match(/```[\s\S]*?```/g) || []).length,
        estimatedReadingTime: Math.ceil(wordCount / 200),
        language: 'en',
        aiManaged: false,
      },
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy: 'user',
    };
  }
}

