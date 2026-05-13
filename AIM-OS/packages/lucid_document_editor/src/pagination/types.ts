/**
 * LUCID Document Editor - Pagination Types
 */

export interface PaginationSettings {
  pageSize: 'A4' | 'Letter' | 'Legal' | 'Custom';
  customWidth: number; // in mm
  customHeight: number; // in mm
  linesPerPage: number;
  fontSize: number; // in px
  lineHeight: number; // multiplier (e.g., 1.5)
  marginTop: number; // in mm
  marginBottom: number; // in mm
  marginLeft: number; // in mm
  marginRight: number; // in mm
  showPageBreaks: boolean;
}

