/**
 * LUCID Document Editor - File Parser System
 * 
 * Comprehensive file parsing for multiple formats including PDF, DOCX, RTF, etc.
 */

import { DocumentModel } from '../models';
import { DocumentPersistence } from '../persistence';

export type SupportedFileType = 
  | 'markdown' 
  | 'text' 
  | 'json' 
  | 'pdf' 
  | 'docx' 
  | 'rtf' 
  | 'html' 
  | 'latex';

export interface FileParseResult {
  document: DocumentModel;
  metadata: {
    fileType: SupportedFileType;
    pageCount?: number;
    wordCount: number;
    characterCount: number;
    language?: string;
  };
}

export class FileParser {
  /**
   * Detect file type from file name or content
   */
  static detectFileType(fileName: string, mimeType?: string): SupportedFileType {
    const extension = fileName.toLowerCase().split('.').pop() || '';
    
    // Check MIME type first if available
    if (mimeType) {
      if (mimeType.includes('pdf')) return 'pdf';
      if (mimeType.includes('word') || mimeType.includes('document')) return 'docx';
      if (mimeType.includes('rtf')) return 'rtf';
      if (mimeType.includes('html')) return 'html';
      if (mimeType.includes('json')) return 'json';
      if (mimeType.includes('markdown') || mimeType.includes('text/markdown')) return 'markdown';
    }
    
    // Fallback to extension
    switch (extension) {
      case 'pdf':
        return 'pdf';
      case 'docx':
      case 'doc':
        return 'docx';
      case 'rtf':
        return 'rtf';
      case 'html':
      case 'htm':
        return 'html';
      case 'json':
        return 'json';
      case 'md':
      case 'markdown':
        return 'markdown';
      case 'tex':
      case 'latex':
        return 'latex';
      default:
        return 'text';
    }
  }

  /**
   * Parse file content based on file type
   */
  static async parseFile(
    file: File,
    content?: string
  ): Promise<FileParseResult> {
    const fileType = this.detectFileType(file.name, file.type);
    const text = content || await file.text();
    
    let document: DocumentModel;
    let metadata: FileParseResult['metadata'];

    switch (fileType) {
      case 'pdf':
        return await this.parsePDF(file);
      
      case 'docx':
        return await this.parseDOCX(file);
      
      case 'rtf':
        return await this.parseRTF(file);
      
      case 'html':
        return await this.parseHTML(text, file.name);
      
      case 'json':
        document = DocumentPersistence.loadFromJSON(text);
        metadata = this.calculateMetadata(document);
        return { document, metadata: { ...metadata, fileType: 'json' } };
      
      case 'latex':
        return await this.parseLaTeX(text, file.name);
      
      case 'markdown':
      case 'text':
      default:
        document = DocumentPersistence.importFromMarkdown(text);
        metadata = this.calculateMetadata(document);
        return { document, metadata: { ...metadata, fileType: fileType === 'markdown' ? 'markdown' : 'text' } };
    }
  }

  /**
   * Parse PDF file
   */
  static async parsePDF(file: File): Promise<FileParseResult> {
    try {
      // Dynamic import of pdf.js
      const pdfjsLib = await import('pdfjs-dist');
      
      // Set worker - use jsdelivr CDN (most reliable)
      if (typeof window !== 'undefined') {
        // Get version from the library
        const version = pdfjsLib.version || '5.4.394';
        
        // Use jsdelivr CDN - reliable and works offline after first load
        // For pdfjs-dist 5.x, the worker is at build/pdf.worker.min.js
        pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdn.jsdelivr.net/npm/pdfjs-dist@${version}/build/pdf.worker.min.js`;
      }
      
      const arrayBuffer = await file.arrayBuffer();
      const loadingTask = pdfjsLib.getDocument({ 
        data: arrayBuffer,
        useSystemFonts: true,
        verbosity: 0, // Reduce console noise
      });
      const pdf = await loadingTask.promise;
      
      const sections: DocumentModel['sections'] = [];
      let fullText = '';
      
      // Extract text from each page
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items
          .map((item: any) => item.str)
          .join(' ')
          .trim();
        
        if (pageText) {
          sections.push({
            id: `section-page-${pageNum}`,
            title: `Page ${pageNum}`,
            content: pageText,
            type: 'text',
            tags: [],
            metadata: {
              pageNumber: pageNum,
              wordCount: pageText.split(/\s+/).filter(w => w.length > 0).length,
            },
            version: 1,
            locked: false,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          });
          
          fullText += pageText + '\n\n';
        }
      }
      
      // If no sections created, create one with all content
      if (sections.length === 0) {
        sections.push({
          id: 'section-0',
          title: 'Content',
          content: fullText.trim() || 'No text content found in PDF',
          type: 'text',
          tags: [],
          metadata: {},
          version: 1,
          locked: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        });
      }
      
      const wordCount = fullText.split(/\s+/).filter(w => w.length > 0).length;
      
      const document: DocumentModel = {
        id: `doc-${Date.now()}`,
        title: file.name.replace(/\.pdf$/i, ''),
        sections,
        tags: [],
        metadata: {
          totalWords: wordCount,
          totalSections: sections.length,
          totalMathBlocks: 0,
          totalCodeBlocks: 0,
          estimatedReadingTime: Math.ceil(wordCount / 200),
          language: 'en',
          aiManaged: false,
        },
        version: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: 'user',
      };
      
      return {
        document,
        metadata: {
          fileType: 'pdf',
          pageCount: pdf.numPages,
          wordCount,
          characterCount: fullText.length,
        },
      };
    } catch (error) {
      console.error('Error parsing PDF:', error);
      throw new Error(`Failed to parse PDF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Parse DOCX file
   */
  static async parseDOCX(file: File): Promise<FileParseResult> {
    try {
      // Dynamic import of mammoth for DOCX parsing
      const mammoth = await import('mammoth');
      
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      
      const text = result.value;
      const document = DocumentPersistence.importFromMarkdown(text);
      document.title = file.name.replace(/\.docx?$/i, '');
      
      const metadata = this.calculateMetadata(document);
      
      return {
        document,
        metadata: {
          ...metadata,
          fileType: 'docx',
        },
      };
    } catch (error) {
      console.error('Error parsing DOCX:', error);
      throw new Error(`Failed to parse DOCX: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Parse RTF file
   */
  static async parseRTF(file: File): Promise<FileParseResult> {
    try {
      // RTF is text-based, extract plain text
      const text = await file.text();
      
      // Simple RTF text extraction (remove RTF control codes)
      const plainText = text
        .replace(/\\[a-z]+\d*\s?/g, '') // Remove RTF commands
        .replace(/\{[^}]*\}/g, '') // Remove RTF groups
        .replace(/\n{3,}/g, '\n\n') // Normalize line breaks
        .trim();
      
      const document = DocumentPersistence.importFromMarkdown(plainText);
      document.title = file.name.replace(/\.rtf$/i, '');
      
      const metadata = this.calculateMetadata(document);
      
      return {
        document,
        metadata: {
          ...metadata,
          fileType: 'rtf',
        },
      };
    } catch (error) {
      console.error('Error parsing RTF:', error);
      throw new Error(`Failed to parse RTF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Parse HTML file
   */
  static parseHTML(html: string, fileName: string): FileParseResult {
    // Create a temporary DOM element to parse HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Extract text content
    const text = doc.body.textContent || doc.body.innerText || '';
    
    // Extract title
    const title = doc.querySelector('title')?.textContent || 
                  doc.querySelector('h1')?.textContent || 
                  fileName.replace(/\.html?$/i, '');
    
    const document = DocumentPersistence.importFromMarkdown(text);
    document.title = title;
    
    const metadata = this.calculateMetadata(document);
    
    return {
      document,
      metadata: {
        ...metadata,
        fileType: 'html',
      },
    };
  }

  /**
   * Parse LaTeX file
   */
  static parseLaTeX(latex: string, fileName: string): FileParseResult {
    // Extract document title from LaTeX
    const titleMatch = latex.match(/\\title\{([^}]+)\}/);
    const title = titleMatch ? titleMatch[1] : fileName.replace(/\.tex$/i, '');
    
    // Convert LaTeX to markdown-like format
    // This is a simplified conversion
    let markdown = latex
      .replace(/\\section\{([^}]+)\}/g, '## $1\n\n')
      .replace(/\\subsection\{([^}]+)\}/g, '### $1\n\n')
      .replace(/\\textbf\{([^}]+)\}/g, '**$1**')
      .replace(/\\textit\{([^}]+)\}/g, '*$1*')
      .replace(/\\emph\{([^}]+)\}/g, '*$1*')
      .replace(/\\begin\{equation\}([\s\S]*?)\\end\{equation\}/g, '$$\n$1\n$$\n')
      .replace(/\\begin\{align\}([\s\S]*?)\\end\{align\}/g, '$$\n$1\n$$\n')
      .replace(/\\begin\{document\}([\s\S]*?)\\end\{document\}/s, '$1')
      .replace(/\\[a-z]+\{([^}]+)\}/g, '$1') // Remove other LaTeX commands
      .replace(/\n{3,}/g, '\n\n')
      .trim();
    
    const document = DocumentPersistence.importFromMarkdown(markdown);
    document.title = title;
    
    const metadata = this.calculateMetadata(document);
    
    return {
      document,
      metadata: {
        ...metadata,
        fileType: 'latex',
      },
    };
  }

  /**
   * Calculate document metadata
   */
  static calculateMetadata(document: DocumentModel): FileParseResult['metadata'] {
    const allText = document.sections.map(s => s.content).join(' ');
    const wordCount = allText.split(/\s+/).filter(w => w.length > 0).length;
    const characterCount = allText.length;
    
    return {
      fileType: 'text',
      wordCount,
      characterCount,
    };
  }
}

