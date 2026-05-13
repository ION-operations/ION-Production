---
id: "lucid-ide-frontend-L2-architecture"
system: "lucid-ide-frontend-system"
component: null
level: "L2"
type: "architecture"
title: "Lucid IDE Frontend System - Architecture"
description: "2,000-word architecture document for Lucid IDE Frontend System"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "frontend", "nextjs", "react", "architecture"]
dependencies: ["lucid-ide-frontend-L1-overview"]
related_docs: ["lucid-ide-frontend-L3-detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Frontend System – L2 Architecture (≈2000 words)

## System Overview

Lucid IDE Frontend System implements comprehensive Next.js 15 + React 19 interface enabling 7 operational modes with resizable panels, 50+ Radix UI components, and advanced visualization capabilities. The system transforms backend API capabilities into intuitive, powerful IDE interface through unified multi-mode architecture.

**Core Architectural Principles:**
1. **Component Composition:** Modular component architecture with clear separation of concerns
2. **State Management:** React Context API and useState hooks for application state
3. **Performance Optimization:** Code splitting, lazy loading, memoization for optimal performance
4. **Accessibility First:** Radix UI components ensure WCAG compliance
5. **Theme System:** Four themes (space, cyberpunk, matrix, aurora) with OKLCH color space

## Component Architecture

### 1. Application Root (`app/page.tsx`)

**Purpose:** Main application orchestrator managing all modes, panels, and application state

**Responsibilities:**
- Mode switching (development, teams, backend, backend-v2, documentation, templates, cortex)
- Panel state management (left, right, bottom, top)
- Theme management
- Command palette coordination
- Keyboard shortcuts handling

**Key State:**
- `mode`: Current operational mode
- `theme`: Current theme (space, cyberpunk, matrix, aurora)
- `leftWidth`, `rightWidth`, `bottomHeight`: Panel dimensions
- `isLeftCollapsed`, `isRightCollapsed`, `isBottomCollapsed`: Panel collapse states
- `isCommandPaletteOpen`: Command palette visibility
- `activePreviewTab`, `leftActiveTab`, `rightActiveTab`, `bottomActiveTab`: Tab states

**Performance Considerations:**
- Component large (413 lines) but manageable
- Heavy useState usage (20+ hooks) suggests need for useReducer or Zustand
- Mode switching preserves state to prevent data loss

**Critical Issues:**
- ⚠️ Heavy useState usage could lead to prop drilling
- ⚠️ No global state management library (consider Zustand/Jotai)
- ⚠️ Mode switching logic complex, consider state machine

### 2. Left Drawer (`components/left-drawer.tsx`)

**Purpose:** Left sidebar providing file tree, search, navigation tabs, and various panels

**Responsibilities:**
- File tree rendering and navigation
- Search functionality
- Tab management (files, search, templates, documentation, agents, etc.)
- Panel content rendering based on active tab

**Key Features:**
- File tree with expand/collapse
- Git status indicators (modified, staged)
- Search with filtering
- Multiple tab panels
- Resizable width

**Critical Issues:**
- ⚠️ **EXTREMELY LARGE:** 4700+ lines ⚠️ CRITICAL - needs urgent refactoring
- ⚠️ Uses mock data (mockFileTree) - needs real file system API
- ⚠️ Too many responsibilities - should be split into smaller components

**Refactoring Recommendations:**
1. Extract FileTree component (separate file)
2. Extract SearchPanel component (separate file)
3. Extract TabPanels into separate components
4. Replace mock data with real file system API
5. Use useReducer for complex state management

### 3. Right Drawer (`components/right-drawer.tsx`)

**Purpose:** Right sidebar providing AI chat, tools, and context panels

**Responsibilities:**
- AI chat interface
- Tool panels
- Context preview panels
- Tab management

**Key Features:**
- AI chat with history
- Tool integration
- Context preview
- Resizable width

**State Management:**
- Chat history state
- Tool state
- Context preview state

### 4. Bottom Drawer (`components/bottom-drawer.tsx`)

**Purpose:** Bottom panel providing terminal, logs, and context preview

**Responsibilities:**
- Terminal interface
- Log display
- Context preview
- Tab management

**Key Features:**
- Terminal emulation
- Log streaming
- Context preview
- Resizable height

**Security Considerations:**
- ⚠️ Terminal execution needs security validation
- ⚠️ Command injection prevention required
- ⚠️ Log sanitization needed

### 5. Top Bar (`components/top-bar.tsx`)

**Purpose:** Top navigation bar with mode switching, theme controls, and command palette

**Responsibilities:**
- Mode switching UI
- Theme selection
- Command palette trigger
- Navigation controls

**Key Features:**
- Mode selector
- Theme switcher
- Command palette button
- Navigation breadcrumbs

### 6. Command Palette (`components/command-palette.tsx`)

**Purpose:** Keyboard-driven command interface for rapid navigation and actions

**Responsibilities:**
- Command registration
- Command search and filtering
- Command execution
- Keyboard navigation

**Key Features:**
- Fuzzy search
- Categorized commands
- Keyboard shortcuts
- Command history

**Command Categories:**
- Navigation commands
- File operations
- Mode switching
- Theme switching
- AI operations
- System operations

**Critical Issues:**
- ⚠️ Some commands are placeholders (console.log)
- ⚠️ Need to implement all command actions
- ⚠️ Consider dynamic plugin system for commands

### 7. UI Component Library (`components/ui/`)

**Purpose:** 50+ Radix UI components providing accessible UI primitives

**Component Categories:**
- **Forms:** button, input, textarea, select, checkbox, radio-group, switch
- **Overlays:** dialog, drawer, sheet, popover, tooltip, hover-card
- **Navigation:** tabs, accordion, breadcrumb, navigation-menu, menubar
- **Feedback:** toast, alert, alert-dialog, progress
- **Data Display:** table, card, badge, avatar, separator
- **Layout:** resizable, scroll-area, sidebar
- **Charts:** chart (recharts wrapper)

**Architecture:**
- Built on Radix UI primitives
- Tailwind CSS styling
- TypeScript type safety
- Forward ref support
- Accessibility built-in

**Design System:**
- Consistent spacing (Tailwind scale)
- Color system (OKLCH color space)
- Typography scale
- Component variants (class-variance-authority)

### 8. AI Context Provider (`components/ai-context-provider.tsx`)

**Purpose:** React Context providing AI service integration and state

**Responsibilities:**
- AI service configuration
- Provider switching
- API key management
- Connection state management

**Key Features:**
- Multiple provider support (OpenAI, Anthropic, XAI)
- Provider switching
- Error handling
- Loading states

**Security Considerations:**
- ⚠️ API keys stored in context (needs secure storage)
- ⚠️ Never expose API keys in logs or errors
- ⚠️ Consider environment variable storage

### 9. Theme Provider (`components/theme-provider.tsx`)

**Purpose:** Theme management with 4 themes and OKLCH color space

**Responsibilities:**
- Theme state management
- Theme switching
- Color system application
- Theme persistence

**Key Features:**
- Four themes (space, cyberpunk, matrix, aurora)
- OKLCH color space support
- Theme persistence (localStorage)
- Smooth theme transitions

**Color System:**
- OKLCH color space for perceptual uniformity
- CSS custom properties for theming
- Dark/light mode support
- Accessibility contrast ratios

### 10. Resizable Panels (`components/resize-handle.tsx`)

**Purpose:** Resizable panel system with drag handles and state persistence

**Responsibilities:**
- Panel resizing logic
- Drag handle rendering
- State persistence
- Layout management

**Key Features:**
- Drag-and-drop resizing
- State persistence (localStorage)
- Minimum/maximum size constraints
- Smooth resizing animations

**Implementation:**
- Uses react-resizable-panels library
- Custom resize handles
- State synchronization
- Layout restoration

## Data Flow Architecture

### User Interaction Flow

```
User Action → React Component → 
Event Handler → State Update → 
Conditional API Call → Backend API → 
Response Processing → State Update → 
UI Re-render → User Feedback
```

### Mode Switching Flow

```
Mode Selection → Current Mode State Save → 
Component Unmount → New Mode Component Mount → 
State Restoration → UI Update → 
Mode-Specific Initialization
```

### Real-Time Updates Flow

```
Backend Event → WebSocket Connection → 
Event Handler → State Update → 
UI Re-render → User Notification
```

### API Request Flow

```
Component → API Client → 
Request Preparation → Backend API Route → 
Response Processing → State Update → 
Error Handling → UI Update
```

## State Management Architecture

### Current Approach

**React Context API:**
- AI Context Provider for AI services
- Theme Provider for theme management
- No global state management library

**useState Hooks:**
- Component-level state management
- 20+ useState hooks in main page component
- Prop drilling for shared state

### Recommended Improvements

**Global State Management:**
- Consider Zustand for global state
- Consider Jotai for atomic state
- Reduce prop drilling
- Improve performance

**State Organization:**
- Group related state (useReducer)
- Extract state logic to custom hooks
- Separate UI state from business state

## Performance Architecture

### Code Splitting

**Route-Based Splitting:**
- Next.js automatic code splitting
- Dynamic imports for large components
- Lazy loading for modes

**Component Splitting:**
- Lazy load large components (left-drawer, knowledge-map-panel)
- Code splitting for visualization components
- Dynamic imports for Three.js

### Optimization Strategies

**Memoization:**
- React.memo for expensive components
- useMemo for computed values
- useCallback for event handlers

**Rendering Optimization:**
- Virtual scrolling for large lists
- Debouncing for search inputs
- Throttling for resize handlers

**Bundle Optimization:**
- Tree shaking
- Minification
- Compression

### Performance Targets

- **Render Time:** < 100ms for main page
- **API Latency:** < 200ms for simple routes
- **Bundle Size:** < 2MB initial load
- **Time to Interactive:** < 3 seconds

## Security Architecture

### Authentication

**Current State:**
- ⚠️ No authentication implemented
- ⚠️ Session-based auth planned
- ⚠️ API keys in context (needs secure storage)

**Recommendations:**
- Implement authentication middleware
- Secure API key storage (environment variables)
- Session management
- Token refresh mechanism

### Input Validation

**Current State:**
- ⚠️ Limited input validation
- ⚠️ No sanitization on frontend
- ⚠️ Relies on backend validation

**Recommendations:**
- Client-side validation (Zod schemas)
- Input sanitization
- XSS prevention
- CSRF protection

### Data Protection

**API Keys:**
- Never expose in logs
- Never expose in errors
- Secure storage (environment variables)
- Rotation support

**Sensitive Data:**
- Never log sensitive data
- Sanitize error messages
- Secure WebSocket connections
- HTTPS only

## Integration Architecture

### Backend API Integration

**REST API:**
- Fetch API for HTTP requests
- Error handling middleware
- Request/response interceptors
- Retry logic

**WebSocket:**
- WebSocket client for real-time updates
- Connection management
- Reconnection logic
- Message queuing

### AI Studio Integration

**React Props:**
- Panel state via props
- Event callbacks
- Resource configurations
- Real-time updates

### Reactor Systems Integration

**React Props:**
- Reactor data via props
- Visualization state
- Interaction events
- Performance metrics

## Error Handling Architecture

### Error Boundaries

**Component-Level:**
- Error boundaries for major sections
- Fallback UI for errors
- Error logging
- User-friendly error messages

### API Error Handling

**Error Types:**
- Network errors
- API errors (4xx, 5xx)
- Timeout errors
- Validation errors

**Error Recovery:**
- Retry logic
- Fallback strategies
- User notification
- Error logging

## Testing Architecture

### Current State

**⚠️ CRITICAL:** Zero test coverage identified

**Recommendations:**
- Unit tests for components (Jest + React Testing Library)
- Integration tests for workflows
- E2E tests for critical paths
- Visual regression tests

### Test Strategy

**Component Tests:**
- Render tests
- Interaction tests
- State tests
- Prop tests

**Integration Tests:**
- API integration
- State management
- User workflows
- Mode switching

## Deployment Architecture

### Build Process

**Next.js Build:**
- Static generation (SSG)
- Server-side rendering (SSR)
- Incremental static regeneration (ISR)
- Image optimization

### Environment Configuration

**Environment Variables:**
- API endpoints
- Feature flags
- Theme configuration
- Analytics keys

### Deployment Targets

**Vercel (Recommended):**
- Next.js optimized
- Edge functions
- CDN distribution
- Automatic deployments

## References

- System map: `systems/lucid-ide/frontend-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/frontend-system/system.index.lucid.json5`
- L1 Overview: `systems/lucid-ide/frontend-system/L1_overview.md`
- L3 Detailed: `systems/lucid-ide/frontend-system/L3_detailed.md`

