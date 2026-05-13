/**
 * LUCID Document Editor - Pagination Calculator
 */

import { PaginationSettings } from './types';
import { PAGE_SIZES } from './constants';

export class PaginationCalculator {
  /**
   * Calculate how many lines fit on a page
   */
  static calculateLinesPerPage(settings: PaginationSettings): number {
    const pageHeight = settings.pageSize === 'Custom' 
      ? settings.customHeight 
      : PAGE_SIZES[settings.pageSize].height;
    
    // Convert mm to pixels (assuming 96 DPI = 3.779527559 pixels per mm)
    const mmToPx = 3.779527559;
    const pageHeightPx = pageHeight * mmToPx;
    
    // Calculate usable height (page height minus margins)
    const marginTopPx = settings.marginTop * mmToPx;
    const marginBottomPx = settings.marginBottom * mmToPx;
    const usableHeight = pageHeightPx - marginTopPx - marginBottomPx;
    
    // Calculate line height in pixels
    const lineHeightPx = settings.fontSize * settings.lineHeight;
    
    // Calculate lines per page
    const linesPerPage = Math.floor(usableHeight / lineHeightPx);
    
    return Math.max(1, linesPerPage);
  }

  /**
   * Split content into pages based on pagination settings
   */
  static splitIntoPages(
    content: string,
    settings: PaginationSettings
  ): Array<{ pageNumber: number; content: string; lineStart: number; lineEnd: number }> {
    const lines = content.split('\n');
    const linesPerPage = settings.linesPerPage || this.calculateLinesPerPage(settings);
    const pages: Array<{ pageNumber: number; content: string; lineStart: number; lineEnd: number }> = [];
    
    for (let i = 0; i < lines.length; i += linesPerPage) {
      const pageLines = lines.slice(i, i + linesPerPage);
      pages.push({
        pageNumber: Math.floor(i / linesPerPage) + 1,
        content: pageLines.join('\n'),
        lineStart: i + 1,
        lineEnd: Math.min(i + linesPerPage, lines.length),
      });
    }
    
    return pages;
  }

  /**
   * Get page size dimensions in pixels
   */
  static getPageSizePx(settings: PaginationSettings): { width: number; height: number } {
    const mmToPx = 3.779527559;
    const width = settings.pageSize === 'Custom' 
      ? settings.customWidth 
      : PAGE_SIZES[settings.pageSize].width;
    const height = settings.pageSize === 'Custom' 
      ? settings.customHeight 
      : PAGE_SIZES[settings.pageSize].height;
    
    return {
      width: width * mmToPx,
      height: height * mmToPx,
    };
  }
}

