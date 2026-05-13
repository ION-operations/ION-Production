// Canvas Store - Zustand store for Canvas document management
// Manages Canvas documents, editing, version history, and chat integration

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type {
  CanvasDocument,
  CanvasSection,
  CanvasVersion,
  CanvasBranch,
  CanvasEnhancementRequest,
  AISuggestion,
  Evidence,
  WorkReference,
  EvidenceTrail,
  GoalAlignment
} from '../types/canvasTypes'

interface CanvasStore {
  // State
  canvases: Record<string, CanvasDocument>
  activeCanvas: string | null
  selectedSection: string | null
  editingSection: string | null
  
  // Actions - Canvas Management
  createCanvas: (options: {
    title: string
    fromMessageId?: string
    initialContent?: string
    channel?: string
    aimos?: {
      confidence?: number
      evidence?: Evidence[]
      workReferences?: WorkReference
      evidenceTrail?: EvidenceTrail
      goalAlignment?: GoalAlignment
    }
  }) => string
  
  updateCanvas: (id: string, updates: Partial<CanvasDocument>) => void
  deleteCanvas: (id: string) => void
  setActiveCanvas: (id: string | null) => void
  
  // Actions - Section Management
  addSection: (canvasId: string, section: Omit<CanvasSection, 'id' | 'metadata'>) => string
  updateSection: (canvasId: string, sectionId: string, updates: Partial<CanvasSection>) => void
  deleteSection: (canvasId: string, sectionId: string) => void
  reorderSections: (canvasId: string, sectionIds: string[]) => void
  
  // Actions - Selection
  setSelectedSection: (sectionId: string | null) => void
  setEditingSection: (sectionId: string | null) => void
  
  // Actions - Chat Integration
  addMessageToCanvas: (canvasId: string, messageId: string) => void
  linkCanvasToMessage: (canvasId: string, messageId: string) => void
  createCanvasFromMessage: (messageId: string, options?: {
    title?: string
    channel?: string
  }) => string
  
  // Actions - Version History
  createVersion: (canvasId: string) => void
  getVersionHistory: (canvasId: string) => CanvasVersion[]
  restoreVersion: (canvasId: string, versionId: string) => void
  
  // Actions - Branches
  createBranch: (canvasId: string, branchName: string) => string
  getBranches: (canvasId: string) => CanvasBranch[]
  switchBranch: (canvasId: string, branchId: string) => void
  mergeBranch: (canvasId: string, branchId: string) => void
  
  // Actions - AI Enhancement
  requestEnhancement: (request: CanvasEnhancementRequest) => Promise<AISuggestion[]>
  applySuggestion: (canvasId: string, sectionId: string, suggestionId: string) => void
  dismissSuggestion: (canvasId: string, sectionId: string, suggestionId: string) => void
  
  // Actions - AIM-OS Integration
  updateAIMOSMetadata: (canvasId: string, updates: Partial<CanvasDocument['aimos']>) => void
  
  // Getters
  getCanvas: (id: string) => CanvasDocument | undefined
  getActiveCanvas: () => CanvasDocument | undefined
  getSection: (canvasId: string, sectionId: string) => CanvasSection | undefined
}

// Helper function to generate unique IDs
const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

// Helper function to create initial section
const createInitialSection = (
  content: string,
  createdBy: 'user' | 'ai' | 'chat' = 'user',
  createdFrom?: string
): CanvasSection => ({
  id: generateId(),
  type: 'text',
  content,
  metadata: {
    createdBy,
    createdFrom,
    editedBy: [],
    timestamp: new Date(),
    version: 1
  },
  editable: true,
  chatReferences: createdFrom ? [createdFrom] : []
})

export const useCanvasStore = create<CanvasStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        canvases: {},
        activeCanvas: null,
        selectedSection: null,
        editingSection: null,
        
        // Canvas Management
        createCanvas: (options) => {
          const id = generateId()
          const now = new Date()
          
          const canvas: CanvasDocument = {
            id,
            title: options.title,
            content: options.initialContent
              ? [createInitialSection(options.initialContent, options.fromMessageId ? 'chat' : 'user', options.fromMessageId)]
              : [],
            metadata: {
              createdAt: now,
              updatedAt: now,
              version: 1,
              author: 'user',
              createdFrom: options.fromMessageId,
              relatedMessages: options.fromMessageId ? [options.fromMessageId] : [],
              collaborators: [],
              tags: []
            },
            history: [],
            branches: [],
            aimos: {
              confidence: options.aimos?.confidence || 0.8,
              evidence: options.aimos?.evidence || [],
              memory: [],
              knowledgeGraph: [],
              workReferences: options.aimos?.workReferences,
              evidenceTrail: options.aimos?.evidenceTrail,
              goalAlignment: options.aimos?.goalAlignment
            },
            chatIntegration: {
              relatedChannel: options.channel,
              relatedMessages: options.fromMessageId ? [options.fromMessageId] : [],
              lastSyncedAt: now
            }
          }
          
          set((state) => ({
            canvases: { ...state.canvases, [id]: canvas },
            activeCanvas: id
          }))
          
          return id
        },
        
        updateCanvas: (id, updates) => {
          set((state) => {
            const canvas = state.canvases[id]
            if (!canvas) return state
            
            const updated = {
              ...canvas,
              ...updates,
              metadata: {
                ...canvas.metadata,
                ...updates.metadata,
                updatedAt: new Date(),
                version: canvas.metadata.version + 1
              }
            }
            
            return {
              canvases: { ...state.canvases, [id]: updated }
            }
          })
        },
        
        deleteCanvas: (id) => {
          set((state) => {
            const { [id]: deleted, ...rest } = state.canvases
            return {
              canvases: rest,
              activeCanvas: state.activeCanvas === id ? null : state.activeCanvas
            }
          })
        },
        
        setActiveCanvas: (id) => {
          set({ activeCanvas: id })
        },
        
        // Section Management
        addSection: (canvasId, sectionData) => {
          const sectionId = generateId()
          const section: CanvasSection = {
            id: sectionId,
            ...sectionData,
            metadata: {
              createdBy: sectionData.metadata?.createdBy || 'user',
              createdFrom: sectionData.metadata?.createdFrom,
              editedBy: [],
              timestamp: new Date(),
              version: 1,
              ...sectionData.metadata
            }
          }
          
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  content: [...canvas.content, section],
                  metadata: {
                    ...canvas.metadata,
                    updatedAt: new Date(),
                    version: canvas.metadata.version + 1
                  }
                }
              }
            }
          })
          
          return sectionId
        },
        
        updateSection: (canvasId, sectionId, updates) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const sectionIndex = canvas.content.findIndex(s => s.id === sectionId)
            if (sectionIndex === -1) return state
            
            const section = canvas.content[sectionIndex]
            const updatedSection: CanvasSection = {
              ...section,
              ...updates,
              metadata: {
                ...section.metadata,
                ...updates.metadata,
                editedBy: [...section.metadata.editedBy, 'user'],
                timestamp: new Date(),
                version: section.metadata.version + 1
              }
            }
            
            const updatedContent = [...canvas.content]
            updatedContent[sectionIndex] = updatedSection
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  content: updatedContent,
                  metadata: {
                    ...canvas.metadata,
                    updatedAt: new Date(),
                    version: canvas.metadata.version + 1
                  }
                }
              }
            }
          })
        },
        
        deleteSection: (canvasId, sectionId) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  content: canvas.content.filter(s => s.id !== sectionId),
                  metadata: {
                    ...canvas.metadata,
                    updatedAt: new Date(),
                    version: canvas.metadata.version + 1
                  }
                }
              }
            }
          })
        },
        
        reorderSections: (canvasId, sectionIds) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const sectionMap = new Map(canvas.content.map(s => [s.id, s]))
            const reorderedContent = sectionIds
              .map(id => sectionMap.get(id))
              .filter((s): s is CanvasSection => s !== undefined)
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  content: reorderedContent,
                  metadata: {
                    ...canvas.metadata,
                    updatedAt: new Date(),
                    version: canvas.metadata.version + 1
                  }
                }
              }
            }
          })
        },
        
        // Selection
        setSelectedSection: (sectionId) => {
          set({ selectedSection: sectionId })
        },
        
        setEditingSection: (sectionId) => {
          set({ editingSection: sectionId })
        },
        
        // Chat Integration
        addMessageToCanvas: (canvasId, messageId) => {
          const sectionId = get().addSection(canvasId, {
            type: 'chat-reference',
            content: { messageId },
            metadata: {
              createdBy: 'chat',
              createdFrom: messageId
            },
            editable: true
          })
          
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  metadata: {
                    ...canvas.metadata,
                    relatedMessages: [...(canvas.metadata.relatedMessages || []), messageId]
                  },
                  chatIntegration: {
                    ...canvas.chatIntegration,
                    relatedMessages: [...canvas.chatIntegration.relatedMessages, messageId],
                    lastSyncedAt: new Date()
                  }
                }
              }
            }
          })
          
          return sectionId
        },
        
        linkCanvasToMessage: (canvasId, messageId) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  metadata: {
                    ...canvas.metadata,
                    relatedMessages: [...(canvas.metadata.relatedMessages || []), messageId]
                  },
                  chatIntegration: {
                    ...canvas.chatIntegration,
                    relatedMessages: [...canvas.chatIntegration.relatedMessages, messageId],
                    lastSyncedAt: new Date()
                  }
                }
              }
            }
          })
        },
        
        createCanvasFromMessage: (messageId, options) => {
          // This will be implemented with actual message retrieval
          // For now, create a basic canvas
          return get().createCanvas({
            title: options?.title || 'New Canvas',
            fromMessageId: messageId,
            channel: options?.channel
          })
        },
        
        // Version History
        createVersion: (canvasId) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const version: CanvasVersion = {
              id: generateId(),
              version: canvas.metadata.version,
              timestamp: new Date(),
              author: 'user',
              changes: [], // TODO: Track actual changes
              snapshot: JSON.parse(JSON.stringify(canvas)) // Deep clone
            }
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  history: [...canvas.history, version]
                }
              }
            }
          })
        },
        
        getVersionHistory: (canvasId) => {
          const canvas = get().canvases[canvasId]
          return canvas?.history || []
        },
        
        restoreVersion: (canvasId, versionId) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const version = canvas.history.find(v => v.id === versionId)
            if (!version) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...version.snapshot,
                  metadata: {
                    ...version.snapshot.metadata,
                    updatedAt: new Date(),
                    version: canvas.metadata.version + 1
                  }
                }
              }
            }
          })
        },
        
        // Branches
        createBranch: (canvasId, branchName) => {
          const branchId = generateId()
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const branch: CanvasBranch = {
              id: branchId,
              name: branchName,
              createdAt: new Date(),
              createdBy: 'user',
              baseVersion: canvas.metadata.version,
              sections: JSON.parse(JSON.stringify(canvas.content)) // Deep clone
            }
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  branches: [...canvas.branches, branch]
                }
              }
            }
          })
          
          return branchId
        },
        
        getBranches: (canvasId) => {
          const canvas = get().canvases[canvasId]
          return canvas?.branches || []
        },
        
        switchBranch: (canvasId, branchId) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const branch = canvas.branches.find(b => b.id === branchId)
            if (!branch) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  content: JSON.parse(JSON.stringify(branch.sections)) // Deep clone
                }
              }
            }
          })
        },
        
        mergeBranch: (canvasId, branchId) => {
          // TODO: Implement merge logic
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  branches: canvas.branches.filter(b => b.id !== branchId)
                }
              }
            }
          })
        },
        
        // AI Enhancement
        requestEnhancement: async (request) => {
          // TODO: Implement actual AI enhancement request
          // For now, return mock suggestions
          return []
        },
        
        applySuggestion: (canvasId, sectionId, suggestionId) => {
          // TODO: Implement suggestion application
        },
        
        dismissSuggestion: (canvasId, sectionId, suggestionId) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            const sectionIndex = canvas.content.findIndex(s => s.id === sectionId)
            if (sectionIndex === -1) return state
            
            const section = canvas.content[sectionIndex]
            const updatedSection: CanvasSection = {
              ...section,
              aiSuggestions: section.aiSuggestions?.filter(s => s.id !== suggestionId)
            }
            
            const updatedContent = [...canvas.content]
            updatedContent[sectionIndex] = updatedSection
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  content: updatedContent
                }
              }
            }
          })
        },
        
        // AIM-OS Integration
        updateAIMOSMetadata: (canvasId, updates) => {
          set((state) => {
            const canvas = state.canvases[canvasId]
            if (!canvas) return state
            
            return {
              canvases: {
                ...state.canvases,
                [canvasId]: {
                  ...canvas,
                  aimos: {
                    ...canvas.aimos,
                    ...updates
                  }
                }
              }
            }
          })
        },
        
        // Getters
        getCanvas: (id) => {
          return get().canvases[id]
        },
        
        getActiveCanvas: () => {
          const state = get()
          return state.activeCanvas ? state.canvases[state.activeCanvas] : undefined
        },
        
        getSection: (canvasId, sectionId) => {
          const canvas = get().canvases[canvasId]
          return canvas?.content.find(s => s.id === sectionId)
        }
      }),
      {
        name: 'canvas-store',
        partialize: (state) => ({
          canvases: state.canvases,
          activeCanvas: state.activeCanvas
        })
      }
    ),
    { name: 'CanvasStore' }
  )
)

