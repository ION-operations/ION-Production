---
id: "lucid-ide-frontend-L1-overview"
system: "lucid-ide-frontend-system"
component: null
level: "L1"
type: "overview"
title: "Lucid IDE Frontend System - Overview"
description: "500-word overview of Lucid IDE Frontend System"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "frontend", "nextjs", "react"]
dependencies: ["lucid-ide-frontend-L0-executive"]
related_docs: ["lucid-ide-frontend-L2-architecture", "system.map.lucid.json5"]
version: "v1.0.0"
---

# Lucid IDE Frontend System – L1 Overview (≈500 words)

## Purpose & Scope

Lucid IDE Frontend System provides comprehensive Next.js 15 + React 19 interface enabling 7 operational modes (development, teams, backend, backend-v2, documentation, templates, cortex) with resizable panels, 50+ Radix UI components, and advanced visualization capabilities. The system transforms backend API capabilities into intuitive, powerful IDE interface enabling developers to build, visualize, and manage complex systems through unified multi-mode interface.

**System Boundaries:**
- Frontend System owns: UI rendering, state management, user interactions, theme management, keyboard shortcuts
- Frontend System does NOT own: Business logic (delegates to backend), data persistence (uses backend APIs), AI operations (uses backend APIs)

## Users & Integrations

**Backend API System:** Frontend calls backend API routes via REST/WebSocket for all data operations, AI services, and real-time updates. Backend provides 42 API routes covering AI services, architecture generation, context preview, and tracing.

**AI Studio System:** Frontend integrates AI Studio panels (15+ panels) via React props for agent management, knowledge maps, models, providers, and performance monitoring. AI Studio provides unified AI resource management interface.

**Reactor Systems:** Frontend integrates 2D/3D reactor visualizations via React props for system architecture visualization, node relationships, and activity monitoring. Reactor systems provide interactive visual representations.

**System Cortex:** Frontend integrates System Cortex for system analysis, code browsing, version history, and architecture visualization. System Cortex provides comprehensive system understanding interface.

## Core Concepts

**Multi-Mode Architecture:** Seven operational modes (development, teams, backend, backend-v2, documentation, templates, cortex) each providing specialized interface for different workflows. Mode switching preserves state and provides seamless transitions.

**Resizable Panels:** Four-panel layout (left drawer, right drawer, bottom drawer, top bar) with drag handles and state persistence. Panels can be resized, collapsed, and restored with state preservation.

**Component Library:** 50+ Radix UI components providing accessible UI primitives including forms, overlays, navigation, feedback, data display, and layout components. All components follow accessibility standards and provide consistent design system.

**State Management:** React Context API and useState hooks manage application state. No external state management libraries (Zustand, Redux) currently used, though large components (4700+ lines) suggest need for state management refactoring.

**Theme System:** Four themes (space, cyberpunk, matrix, aurora) with OKLCH color space support. Theme preferences persisted and applied globally across all components.

## High-Level Data Flow

**User Interaction Flow:**
```
User Action → React Component → State Update → 
API Call (if needed) → Backend API → Response → 
State Update → UI Re-render
```

**Mode Switching Flow:**
```
Mode Selection → State Preservation → Component Unmount → 
New Mode Component Mount → State Restoration → UI Update
```

**Real-Time Updates Flow:**
```
Backend Event → WebSocket → Frontend Handler → 
State Update → UI Re-render
```

## Non-Goals

Frontend System is NOT:
- **Backend logic:** All business logic delegated to backend API
- **Data persistence:** Uses backend APIs for all data operations
- **AI operations:** Delegates all AI operations to backend
- **File system access:** Uses backend APIs for file operations
- **Database operations:** All database operations via backend APIs

## References

- System map: `systems/lucid-ide/frontend-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/frontend-system/system.index.lucid.json5`
- L0 Executive: `systems/lucid-ide/frontend-system/L0_executive.md`
- L2 Architecture: `systems/lucid-ide/frontend-system/L2_architecture.md`

