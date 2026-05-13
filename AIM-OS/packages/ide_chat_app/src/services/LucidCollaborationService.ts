/**
 * Lucid Collaboration Service
 * Enables real-time collaboration on code intelligence
 */

export interface CollaborationUser {
  id: string
  name: string
  color: string
  cursor?: {
    line: number
    column: number
  }
  selection?: {
    startLine: number
    endLine: number
    startColumn: number
    endColumn: number
  }
}

export interface CollaborationEvent {
  type: 'focus' | 'spec_view' | 'blueprint_view' | 'timeline_view' | 'change_proposal'
  nodeId: string
  userId: string
  timestamp: number
  data?: any
}

export interface LucidSession {
  id: string
  users: Map<string, CollaborationUser>
  focusedNode?: string
  activeFolds: Set<string>
  events: CollaborationEvent[]
}

class LucidCollaborationService {
  private session: LucidSession | null = null
  private eventListeners: Map<string, Function[]> = new Map()
  private isHost: boolean = false
  private userId: string = this.generateUserId()

  constructor() {
    this.initializeSession()
  }

  private generateUserId(): string {
    return `user_${Math.random().toString(36).substr(2, 9)}`
  }

  private generateSessionId(): string {
    return `session_${Math.random().toString(36).substr(2, 9)}`
  }

  private initializeSession() {
    this.session = {
      id: this.generateSessionId(),
      users: new Map(),
      activeFolds: new Set(),
      events: []
    }
    
    // Add current user
    this.addUser({
      id: this.userId,
      name: 'Current User',
      color: this.generateUserColor()
    })
  }

  private generateUserColor(): string {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
      '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
    ]
    return colors[Math.floor(Math.random() * colors.length)]
  }

  // Event system
  on(event: string, callback: Function) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event)!.push(callback)
  }

  off(event: string, callback: Function) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: any) {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach(callback => callback(data))
    }
  }

  // User management
  addUser(user: CollaborationUser) {
    if (!this.session) return
    
    this.session.users.set(user.id, user)
    this.emit('user_joined', user)
  }

  removeUser(userId: string) {
    if (!this.session) return
    
    this.session.users.delete(userId)
    this.emit('user_left', userId)
  }

  updateUserCursor(userId: string, cursor: { line: number; column: number }) {
    if (!this.session) return
    
    const user = this.session.users.get(userId)
    if (user) {
      user.cursor = cursor
      this.emit('cursor_updated', { userId, cursor })
    }
  }

  updateUserSelection(userId: string, selection: {
    startLine: number
    endLine: number
    startColumn: number
    endColumn: number
  }) {
    if (!this.session) return
    
    const user = this.session.users.get(userId)
    if (user) {
      user.selection = selection
      this.emit('selection_updated', { userId, selection })
    }
  }

  // Node focus management
  focusNode(nodeId: string) {
    if (!this.session) return
    
    this.session.focusedNode = nodeId
    this.addEvent({
      type: 'focus',
      nodeId,
      userId: this.userId,
      timestamp: Date.now()
    })
    
    this.emit('node_focused', { nodeId, userId: this.userId })
  }

  // Fold management
  toggleFold(nodeId: string, foldType: 'spec' | 'blueprint' | 'timeline') {
    if (!this.session) return
    
    const foldId = `${nodeId}-${foldType}`
    
    if (this.session.activeFolds.has(foldId)) {
      this.session.activeFolds.delete(foldId)
    } else {
      this.session.activeFolds.add(foldId)
    }
    
    this.addEvent({
      type: `${foldType}_view` as any,
      nodeId,
      userId: this.userId,
      timestamp: Date.now(),
      data: { foldType, active: this.session.activeFolds.has(foldId) }
    })
    
    this.emit('fold_toggled', { nodeId, foldType, active: this.session.activeFolds.has(foldId) })
  }

  // Event management
  private addEvent(event: CollaborationEvent) {
    if (!this.session) return
    
    this.session.events.push(event)
    
    // Keep only last 100 events
    if (this.session.events.length > 100) {
      this.session.events = this.session.events.slice(-100)
    }
    
    this.emit('event_added', event)
  }

  // Change proposal collaboration
  proposeChange(nodeId: string, proposal: any) {
    this.addEvent({
      type: 'change_proposal',
      nodeId,
      userId: this.userId,
      timestamp: Date.now(),
      data: proposal
    })
    
    this.emit('change_proposed', { nodeId, proposal, userId: this.userId })
  }

  // Session state
  getSession(): LucidSession | null {
    return this.session
  }

  getUsers(): CollaborationUser[] {
    if (!this.session) return []
    return Array.from(this.session.users.values())
  }

  getFocusedNode(): string | undefined {
    return this.session?.focusedNode
  }

  getActiveFolds(): string[] {
    if (!this.session) return []
    return Array.from(this.session.activeFolds)
  }

  getRecentEvents(limit: number = 10): CollaborationEvent[] {
    if (!this.session) return []
    return this.session.events.slice(-limit)
  }

  // Collaboration indicators
  getCollaborationIndicators() {
    const users = this.getUsers()
    const focusedNode = this.getFocusedNode()
    const activeFolds = this.getActiveFolds()
    
    return {
      userCount: users.length,
      focusedNode,
      activeFolds: activeFolds.length,
      recentActivity: this.getRecentEvents(5)
    }
  }

  // Export/Import session
  exportSession() {
    if (!this.session) return null
    
    return {
      id: this.session.id,
      users: Array.from(this.session.users.entries()),
      focusedNode: this.session.focusedNode,
      activeFolds: Array.from(this.session.activeFolds),
      events: this.session.events
    }
  }

  importSession(sessionData: any) {
    this.session = {
      id: sessionData.id,
      users: new Map(sessionData.users),
      focusedNode: sessionData.focusedNode,
      activeFolds: new Set(sessionData.activeFolds),
      events: sessionData.events
    }
    
    this.emit('session_imported', this.session)
  }
}

// Export singleton instance
export const lucidCollaborationService = new LucidCollaborationService()
export default LucidCollaborationService
