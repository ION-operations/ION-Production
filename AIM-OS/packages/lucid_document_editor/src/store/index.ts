/**
 * LUCID Document Editor - Document Store
 * 
 * Zustand store for managing document state
 */

import { create } from 'zustand';
import { DocumentModel, DocumentState, DocumentSection, DocumentChange } from './models';
import { SectionLockManager } from '../locking/section-locking';
import { SectionVersionManager } from '../versioning/section-versioning';
import { ChangeTracker } from '../change-tracking/change-tracker';

interface DocumentStore extends DocumentState {
  // Managers
  lockManager: SectionLockManager;
  versionManager: SectionVersionManager;
  changeTracker: ChangeTracker;
  
  // Actions
  setDocument: (document: DocumentModel) => void;
  updateSection: (sectionId: string, updates: Partial<DocumentSection>) => void;
  addSection: (section: DocumentSection, position?: number) => void;
  deleteSection: (sectionId: string) => void;
  reorderSections: (sectionIds: string[]) => void;
  setActiveSection: (sectionId: string | undefined) => void;
  setSelection: (selection: DocumentState['selection']) => void;
  addChange: (change: DocumentChange) => void;
  clearChanges: () => void;
  setUnsavedChanges: (unsaved: boolean) => void;
  // Computed
  getSection: (sectionId: string) => DocumentSection | undefined;
  getActiveSection: () => DocumentSection | undefined;
  getChangesForSection: (sectionId: string) => DocumentChange[];
}

export const useDocumentStore = create<DocumentStore>((set, get) => ({
  document: {
    id: '',
    title: 'Untitled Document',
    sections: [],
    tags: [],
    metadata: {
      totalWords: 0,
      totalSections: 0,
      totalMathBlocks: 0,
      totalCodeBlocks: 0,
      estimatedReadingTime: 0,
      language: 'en',
      aiManaged: false,
    },
    version: 1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    createdBy: 'user',
  },
  changes: [],
  unsavedChanges: false,

  // Initialize managers
  lockManager: new SectionLockManager(),
  versionManager: new SectionVersionManager(),
  changeTracker: new ChangeTracker(),

  setDocument: (document) => set({ document, unsavedChanges: false }),

  updateSection: (sectionId, updates) => {
    const state = get();
    const section = state.document.sections.find(s => s.id === sectionId);
    if (!section) return;

    const oldContent = section.content;
    const sections = state.document.sections.map((s) =>
      s.id === sectionId
        ? { ...s, ...updates, updatedAt: new Date().toISOString(), version: s.version + 1 }
        : s
    );
    
    const newSection = sections.find(s => s.id === sectionId)!;
    
    // Track change
    state.changeTracker.trackChange(
      sectionId,
      'replace',
      oldContent,
      newSection.content,
      'user'
    );

    // Create version
    state.versionManager.createVersion(
      newSection,
      'user',
      'Section updated'
    );

    set({
      document: {
        ...state.document,
        sections,
        updatedAt: new Date().toISOString(),
        version: state.document.version + 1,
      },
      unsavedChanges: true,
    });
  },

  addSection: (section, position) =>
    set((state) => {
      const sections = [...state.document.sections];
      if (position !== undefined && position >= 0 && position < sections.length) {
        sections.splice(position, 0, section);
      } else {
        sections.push(section);
      }
      return {
        document: {
          ...state.document,
          sections,
          updatedAt: new Date().toISOString(),
          version: state.document.version + 1,
          metadata: {
            ...state.document.metadata,
            totalSections: sections.length,
          },
        },
        unsavedChanges: true,
      };
    }),

  deleteSection: (sectionId) =>
    set((state) => {
      const sections = state.document.sections.filter((s) => s.id !== sectionId);
      return {
        document: {
          ...state.document,
          sections,
          updatedAt: new Date().toISOString(),
          version: state.document.version + 1,
          metadata: {
            ...state.document.metadata,
            totalSections: sections.length,
          },
        },
        unsavedChanges: true,
      };
    }),

  reorderSections: (sectionIds) =>
    set((state) => {
      const sectionMap = new Map(state.document.sections.map((s) => [s.id, s]));
      const sections = sectionIds.map((id) => sectionMap.get(id)).filter(Boolean) as DocumentSection[];
      return {
        document: {
          ...state.document,
          sections,
          updatedAt: new Date().toISOString(),
          version: state.document.version + 1,
        },
        unsavedChanges: true,
      };
    }),

  setActiveSection: (sectionId) => set({ activeSectionId: sectionId }),

  setSelection: (selection) => set({ selection }),

  addChange: (change) =>
    set((state) => ({
      changes: [...state.changes, change],
      unsavedChanges: true,
    })),

  clearChanges: () => set({ changes: [] }),

  setUnsavedChanges: (unsaved) => set({ unsavedChanges: unsaved }),

  getSection: (sectionId) => {
    const state = get();
    return state.document.sections.find((s) => s.id === sectionId);
  },

  getActiveSection: () => {
    const state = get();
    if (!state.activeSectionId) return undefined;
    return state.document.sections.find((s) => s.id === state.activeSectionId);
  },

  getChangesForSection: (sectionId) => {
    const state = get();
    return state.changes.filter((c) => c.sectionId === sectionId);
  },
}));

