/**
 * LUCID Document Editor - Pagination Constants
 */

import { PaginationSettings } from './types';

export const DEFAULT_PAGINATION: PaginationSettings = {
  pageSize: 'A4',
  customWidth: 210, // A4 width in mm
  customHeight: 297, // A4 height in mm
  linesPerPage: 50,
  fontSize: 12,
  lineHeight: 1.5,
  marginTop: 20,
  marginBottom: 20,
  marginLeft: 20,
  marginRight: 20,
  showPageBreaks: true,
};

export const PAGE_SIZES = {
  A4: { width: 210, height: 297 }, // mm
  Letter: { width: 216, height: 279 }, // mm
  Legal: { width: 216, height: 356 }, // mm
};

