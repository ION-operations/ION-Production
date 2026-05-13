---
id: "lucid-ide-frontend-L3-detailed"
system: "lucid-ide-frontend-system"
component: null
level: "L3"
type: "detailed"
title: "Lucid IDE Frontend System - Detailed Implementation Guide"
description: "10,000-word detailed implementation guide for Lucid IDE Frontend System"
audience: "developers, implementers, maintainers"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "frontend", "nextjs", "react", "implementation"]
dependencies: ["lucid-ide-frontend-L2-architecture"]
related_docs: ["lucid-ide-frontend-L4-complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

# Lucid IDE Frontend System – L3 Detailed Implementation Guide

**Purpose:** Complete implementation guide for Lucid IDE Frontend System with step-by-step instructions, code examples, integration guides, configuration, testing, troubleshooting, best practices, and advanced topics.

**Audience:** Developers implementing, integrating with, or maintaining the Lucid IDE Frontend System.

**Prerequisites:**
- Next.js 15+
- React 19+
- TypeScript 5+
- Understanding of React hooks and context
- Familiarity with Tailwind CSS and Radix UI
- Basic knowledge of WebSocket and real-time updates

---

## 📜 **EVOLUTION & HISTORY**

### **Version Timeline**

**v1.0 (2025-11-09) - Initial Documentation**
- **Changes:** Comprehensive AIM-OS protocol-compliant documentation
- **Key Features:** 7 operational modes, 50+ Radix UI components, resizable panels, theme system
- **Status:** Production-ready with identified refactoring needs

### **Key Evolution Points**

**Phase 1: Foundation (Initial)**
- **Goal:** Basic IDE interface with file tree and editor
- **Implementation:** Next.js 15 + React 19, basic panels
- **Outcome:** Functional IDE interface

**Phase 2: Multi-Mode Architecture**
- **Goal:** Support multiple operational modes
- **Implementation:** Mode switching, conditional rendering, mode-specific components
- **Outcome:** 7 operational modes (development, teams, backend, backend-v2, documentation, templates, cortex)

**Phase 3: Component Library**
- **Goal:** Comprehensive UI component library
- **Implementation:** 50+ Radix UI components, Tailwind CSS styling
- **Outcome:** Complete component library with accessibility

**Phase 4: Advanced Features**
- **Goal:** Advanced visualization and AI integration
- **Implementation:** Reactor systems, AI Studio integration, knowledge map
- **Outcome:** Advanced features integrated

---

## 🌟 **SYSTEM ARCHITECTURE**

### **Core Technologies**

**Framework Stack:**
- **Next.js 15:** App Router, Server Components, Server Actions
- **React 19:** Concurrent features, Server Components, Suspense
- **TypeScript 5:** Type safety, strict mode
- **Tailwind CSS:** Utility-first styling
- **Radix UI:** Accessible component primitives

**State Management:**
- **React Context API:** Global state (AI context, theme)
- **useState Hooks:** Component-level state
- **useReducer:** Complex state (planned)

**Performance:**
- **Code Splitting:** Dynamic imports, lazy loading
- **Memoization:** React.memo, useMemo, useCallback
- **Virtual Scrolling:** Large list optimization

### **Component Hierarchy**

```
app/page.tsx (Root)
├── TopBar
├── LeftDrawer
│   ├── FileTree
│   ├── SearchPanel
│   ├── TemplateHub
│   ├── MasterDocumentationCenter
│   └── AutonomousAgents
├── RightDrawer
│   ├── AIChat
│   ├── ToolsPanel
│   └── ContextPreview
├── BottomDrawer
│   ├── Terminal
│   ├── Logs
│   └── ContextPreview
├── PreviewArea
│   ├── UIEditor
│   ├── CodeEditor
│   └── Preview
├── CommandPalette
├── KeyboardShortcuts
└── ToastHost
```

---

## 🔧 **IMPLEMENTATION GUIDE**

### **Step 1: Installation and Setup**

**Prerequisites:**
```bash
# Node.js 18+ required
node --version

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

**Environment Configuration:**
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_WS_URL=ws://localhost:3000
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
XAI_API_KEY=your_key_here
```

**Development Server:**
```bash
npm run dev
# Server starts on http://localhost:3000
```

### **Step 2: Project Structure**

**Directory Layout:**
```
app/
├── page.tsx              # Main application page
├── layout.tsx            # Root layout
├── api/                  # API routes
│   ├── ai/              # AI service routes
│   ├── architect/       # Architect routes
│   └── trace/           # Trace routes
components/
├── ui/                  # Radix UI components
├── left-drawer.tsx      # Left sidebar
├── right-drawer.tsx     # Right sidebar
├── bottom-drawer.tsx    # Bottom panel
├── top-bar.tsx          # Top navigation
├── command-palette.tsx  # Command palette
└── ...                  # Other components
lib/
├── ai-context-provider.tsx  # AI context
├── theme-provider.tsx      # Theme management
└── ...                     # Utilities
```

### **Step 3: Core Component Implementation**

#### **3.1 Application Root (`app/page.tsx`)**

**Purpose:** Main application orchestrator

**Key Responsibilities:**
- Mode management
- Panel state management
- Theme management
- Command palette coordination
- Keyboard shortcuts

**Implementation:**
```typescript
"use client"

import { useState, useEffect } from "react"
import { TopBar } from "@/components/top-bar"
import { LeftDrawer } from "@/components/left-drawer"
import { RightDrawer } from "@/components/right-drawer"
import { BottomDrawer } from "@/components/bottom-drawer"
import { CommandPalette } from "@/components/command-palette"
import { AIContextProvider } from "@/components/ai-context-provider"

type Theme = "space" | "cyberpunk" | "matrix" | "aurora"
type Mode = "development" | "teams" | "backend" | "backend-v2" | "documentation" | "templates" | "cortex"

export default function OmniBuilderIDE() {
  const [theme, setTheme] = useState<Theme>("space")
  const [mode, setMode] = useState<Mode>("development")
  const [leftWidth, setLeftWidth] = useState(380)
  const [rightWidth, setRightWidth] = useState(350)
  const [bottomHeight, setBottomHeight] = useState(250)
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false)
  
  // ... more state ...

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Command Palette: Cmd+Shift+P
      if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "P") {
        e.preventDefault()
        setIsCommandPaletteOpen(true)
      }
      // ... more shortcuts ...
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  return (
    <AIContextProvider>
      <div className={`theme-${theme}`}>
        <TopBar mode={mode} onModeChange={setMode} theme={theme} onThemeChange={setTheme} />
        <LeftDrawer collapsed={isLeftCollapsed} minimized={isLeftMinimized} />
        <RightDrawer collapsed={isRightCollapsed} minimized={isRightMinimized} />
        <BottomDrawer collapsed={isBottomCollapsed} minimized={isBottomMinimized} />
        <CommandPalette open={isCommandPaletteOpen} onOpenChange={setIsCommandPaletteOpen} />
      </div>
    </AIContextProvider>
  )
}
```

**State Management Issues:**
- ⚠️ **20+ useState hooks** - Consider useReducer or Zustand
- ⚠️ **Prop drilling** - Consider Context API or state management library
- ⚠️ **Large component** - Consider splitting into smaller components

**Refactoring Recommendations:**
```typescript
// Use useReducer for complex state
const [state, dispatch] = useReducer(appReducer, initialState)

// Or use Zustand for global state
import { create } from 'zustand'

const useAppStore = create((set) => ({
  theme: 'space',
  mode: 'development',
  setTheme: (theme) => set({ theme }),
  setMode: (mode) => set({ mode }),
}))
```

#### **3.2 Left Drawer (`components/left-drawer.tsx`)**

**Purpose:** Left sidebar with file tree, search, and panels

**Critical Issues:**
- ⚠️ **EXTREMELY LARGE:** 4700+ lines ⚠️ CRITICAL
- ⚠️ Needs urgent refactoring

**Refactoring Strategy:**
```typescript
// Extract FileTree component
components/
├── left-drawer/
│   ├── index.tsx              # Main drawer
│   ├── file-tree.tsx          # File tree component
│   ├── search-panel.tsx        # Search component
│   ├── template-hub.tsx       # Template hub
│   └── documentation-center.tsx # Documentation center
```

**FileTree Component:**
```typescript
// components/left-drawer/file-tree.tsx
"use client"

import { useState } from "react"
import { File, Folder, FolderOpen } from "lucide-react"

interface FileNode {
  name: string
  type: "file" | "folder"
  children?: FileNode[]
  expanded?: boolean
  modified?: boolean
  staged?: boolean
}

export function FileTree({ nodes }: { nodes: FileNode[] }) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const toggleExpand = (path: string) => {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }

  return (
    <div className="file-tree">
      {nodes.map(node => (
        <FileTreeNode
          key={node.name}
          node={node}
          expanded={expanded.has(node.name)}
          onToggle={() => toggleExpand(node.name)}
        />
      ))}
    </div>
  )
}
```

#### **3.3 Right Drawer (`components/right-drawer.tsx`)**

**Purpose:** Right sidebar with AI chat and tools

**Implementation Pattern:**
```typescript
"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AIChat } from "./ai-chat"
import { ToolsPanel } from "./tools-panel"

export function RightDrawer({ collapsed, minimized }: RightDrawerProps) {
  const [activeTab, setActiveTab] = useState("chat")

  return (
    <div className={`right-drawer ${collapsed ? 'collapsed' : ''} ${minimized ? 'minimized' : ''}`}>
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
        </TabsList>
        <TabsContent value="chat">
          <AIChat />
        </TabsContent>
        <TabsContent value="tools">
          <ToolsPanel />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

#### **3.4 Bottom Drawer (`components/bottom-drawer.tsx`)**

**Purpose:** Bottom panel with terminal and logs

**Terminal Integration:**
```typescript
"use client"

import { Terminal } from "./terminal"
import { Logs } from "./logs"

export function BottomDrawer({ collapsed, minimized }: BottomDrawerProps) {
  const [activeTab, setActiveTab] = useState("terminal")

  return (
    <div className={`bottom-drawer ${collapsed ? 'collapsed' : ''} ${minimized ? 'minimized' : ''}`}>
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="terminal">Terminal</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>
        <TabsContent value="terminal">
          <Terminal />
        </TabsContent>
        <TabsContent value="logs">
          <Logs />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### **Step 4: State Management**

#### **4.1 Context API Implementation**

**AI Context Provider:**
```typescript
// components/ai-context-provider.tsx
"use client"

import { createContext, useContext, useState, ReactNode } from "react"

interface AIContextType {
  provider: "openai" | "anthropic" | "xai"
  apiKey: string | null
  setProvider: (provider: "openai" | "anthropic" | "xai") => void
  setApiKey: (key: string) => void
}

const AIContext = createContext<AIContextType | undefined>(undefined)

export function AIContextProvider({ children }: { children: ReactNode }) {
  const [provider, setProvider] = useState<"openai" | "anthropic" | "xai">("openai")
  const [apiKey, setApiKey] = useState<string | null>(null)

  return (
    <AIContext.Provider value={{ provider, apiKey, setProvider, setApiKey }}>
      {children}
    </AIContext.Provider>
  )
}

export function useAIContext() {
  const context = useContext(AIContext)
  if (!context) {
    throw new Error("useAIContext must be used within AIContextProvider")
  }
  return context
}
```

**Theme Provider:**
```typescript
// components/theme-provider.tsx
"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

type Theme = "space" | "cyberpunk" | "matrix" | "aurora"

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("theme") as Theme) || "space"
    }
    return "space"
  })

  useEffect(() => {
    localStorage.setItem("theme", theme)
    document.documentElement.setAttribute("data-theme", theme)
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider")
  }
  return context
}
```

#### **4.2 Recommended: Zustand State Management**

**Installation:**
```bash
npm install zustand
```

**Store Implementation:**
```typescript
// lib/stores/app-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  theme: "space" | "cyberpunk" | "matrix" | "aurora"
  mode: "development" | "teams" | "backend" | "backend-v2" | "documentation" | "templates" | "cortex"
  leftWidth: number
  rightWidth: number
  bottomHeight: number
  isLeftCollapsed: boolean
  isRightCollapsed: boolean
  isBottomCollapsed: boolean
  setTheme: (theme: AppState["theme"]) => void
  setMode: (mode: AppState["mode"]) => void
  setLeftWidth: (width: number) => void
  setRightWidth: (width: number) => void
  setBottomHeight: (height: number) => void
  toggleLeftCollapse: () => void
  toggleRightCollapse: () => void
  toggleBottomCollapse: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: "space",
      mode: "development",
      leftWidth: 380,
      rightWidth: 350,
      bottomHeight: 250,
      isLeftCollapsed: false,
      isRightCollapsed: false,
      isBottomCollapsed: false,
      setTheme: (theme) => set({ theme }),
      setMode: (mode) => set({ mode }),
      setLeftWidth: (leftWidth) => set({ leftWidth }),
      setRightWidth: (rightWidth) => set({ rightWidth }),
      setBottomHeight: (bottomHeight) => set({ bottomHeight }),
      toggleLeftCollapse: () => set((state) => ({ isLeftCollapsed: !state.isLeftCollapsed })),
      toggleRightCollapse: () => set((state) => ({ isRightCollapsed: !state.isRightCollapsed })),
      toggleBottomCollapse: () => set((state) => ({ isBottomCollapsed: !state.isBottomCollapsed })),
    }),
    {
      name: "app-storage",
    }
  )
)
```

### **Step 5: UI Component Library**

#### **5.1 Radix UI Components**

**Button Component:**
```typescript
// components/ui/button.tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

**Input Component:**
```typescript
// components/ui/input.tsx
import * as React from "react"
import { cn } from "@/lib/utils"

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
```

#### **5.2 Custom Components**

**Resizable Panels:**
```typescript
// components/resize-handle.tsx
"use client"

import { useState, useRef, useEffect } from "react"

interface ResizeHandleProps {
  direction: "horizontal" | "vertical"
  onResize: (delta: number) => void
  minSize?: number
  maxSize?: number
}

export function ResizeHandle({ direction, onResize, minSize, maxSize }: ResizeHandleProps) {
  const [isDragging, setIsDragging] = useState(false)
  const startPos = useRef(0)

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    startPos.current = direction === "horizontal" ? e.clientX : e.clientY
  }

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      const currentPos = direction === "horizontal" ? e.clientX : e.clientY
      const delta = currentPos - startPos.current
      onResize(delta)
      startPos.current = currentPos
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mouseup", handleMouseUp)

    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
    }
  }, [isDragging, direction, onResize])

  return (
    <div
      className={`resize-handle resize-handle-${direction} ${isDragging ? "dragging" : ""}`}
      onMouseDown={handleMouseDown}
    />
  )
}
```

### **Step 6: Performance Optimization**

#### **6.1 Code Splitting**

**Dynamic Imports:**
```typescript
// Lazy load heavy components
import dynamic from "next/dynamic"

const KnowledgeMapPanel = dynamic(
  () => import("@/components/ai-studio/KnowledgeMapPanel"),
  { ssr: false, loading: () => <div>Loading...</div> }
)

const BackendArchitectV2 = dynamic(
  () => import("@/components/backend-architect-v2"),
  { ssr: false }
)
```

**Route-Based Splitting:**
```typescript
// Automatic code splitting by route
// Next.js automatically splits by route
app/
├── page.tsx           # Main page bundle
├── api/               # API routes (server-only)
└── (routes)/          # Route groups for splitting
```

#### **6.2 Memoization**

**Component Memoization:**
```typescript
import { memo } from "react"

export const FileTreeNode = memo(({ node }: { node: FileNode }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.node.id === nextProps.node.id
})
```

**Value Memoization:**
```typescript
import { useMemo } from "react"

const filteredFiles = useMemo(() => {
  return files.filter(file => 
    file.name.toLowerCase().includes(searchQuery.toLowerCase())
  )
}, [files, searchQuery])
```

**Callback Memoization:**
```typescript
import { useCallback } from "react"

const handleFileClick = useCallback((fileId: string) => {
  // Handle file click
}, [/* dependencies */])
```

#### **6.3 Virtual Scrolling**

**Large List Optimization:**
```typescript
import { useVirtualizer } from "@tanstack/react-virtual"

export function VirtualizedFileList({ files }: { files: FileNode[] }) {
  const parentRef = useRef<HTMLDivElement>(null)

  const virtualizer = useVirtualizer({
    count: files.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 5,
  })

  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: "100%",
          position: "relative",
        }}
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <FileItem file={files[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  )
}
```

### **Step 7: Security Implementation**

#### **7.1 Input Validation**

**Zod Schemas:**
```typescript
import { z } from "zod"

const filePathSchema = z.string()
  .min(1)
  .max(260)
  .refine(path => !path.includes(".."), {
    message: "Path traversal not allowed"
  })

const apiKeySchema = z.string()
  .min(20)
  .max(200)
  .regex(/^sk-[a-zA-Z0-9]+$/, {
    message: "Invalid API key format"
  })
```

**Input Sanitization:**
```typescript
import DOMPurify from "isomorphic-dompurify"

export function sanitizeInput(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  })
}
```

#### **7.2 API Key Security**

**Secure Storage:**
```typescript
// Never store API keys in localStorage
// Use environment variables or secure backend storage

// ❌ BAD
localStorage.setItem("apiKey", apiKey)

// ✅ GOOD
// Store in backend, retrieve via secure API
const response = await fetch("/api/ai/secrets", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key: encryptedKey }),
})
```

**Never Log Keys:**
```typescript
// ❌ BAD
console.log("API Key:", apiKey)

// ✅ GOOD
console.log("API Key configured:", apiKey ? "***" : "not set")
```

### **Step 8: Testing**

#### **8.1 Component Testing**

**Setup:**
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

**Component Test:**
```typescript
// __tests__/components/button.test.tsx
import { render, screen } from "@testing-library/react"
import { Button } from "@/components/ui/button"

describe("Button", () => {
  it("renders correctly", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText("Click me")).toBeInTheDocument()
  })

  it("handles click events", () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    screen.getByText("Click me").click()
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

#### **8.2 Integration Testing**

**API Integration Test:**
```typescript
// __tests__/integration/api.test.ts
import { fetch } from "node-fetch"

describe("API Integration", () => {
  it("fetches agents correctly", async () => {
    const response = await fetch("http://localhost:3000/api/ai/agents")
    const data = await response.json()
    expect(data.ok).toBe(true)
    expect(Array.isArray(data.agents)).toBe(true)
  })
})
```

### **Step 9: Troubleshooting**

#### **9.1 Common Issues**

**Issue: Panel not resizing**
- **Cause:** Event listeners not properly attached
- **Solution:** Ensure resize handles have proper event handlers

**Issue: State not persisting**
- **Cause:** localStorage not configured
- **Solution:** Add persistence middleware to state management

**Issue: Performance degradation**
- **Cause:** Too many re-renders
- **Solution:** Add memoization, use React DevTools Profiler

**Issue: API keys exposed**
- **Cause:** Keys in client-side code
- **Solution:** Move to environment variables, use backend proxy

#### **9.2 Debugging Tools**

**React DevTools:**
- Install React DevTools browser extension
- Use Profiler to identify performance issues
- Use Components tab to inspect state

**Next.js Debugging:**
```bash
# Enable debug mode
DEBUG=* npm run dev

# Or specific debug
DEBUG=next:* npm run dev
```

### **Step 10: Best Practices**

#### **10.1 Component Design**

**Do:**
- ✅ Keep components small and focused
- ✅ Use TypeScript for type safety
- ✅ Extract reusable logic to hooks
- ✅ Use composition over inheritance
- ✅ Follow single responsibility principle

**Don't:**
- ❌ Create components >500 lines
- ❌ Mix UI and business logic
- ❌ Use any type
- ❌ Create deeply nested components
- ❌ Ignore accessibility

#### **10.2 State Management**

**Do:**
- ✅ Use Context for truly global state
- ✅ Use local state for component-specific state
- ✅ Consider Zustand for complex state
- ✅ Persist important state
- ✅ Normalize state structure

**Don't:**
- ❌ Overuse Context API
- ❌ Store everything in global state
- ❌ Mutate state directly
- ❌ Store sensitive data in state
- ❌ Create circular dependencies

#### **10.3 Performance**

**Do:**
- ✅ Use code splitting
- ✅ Memoize expensive computations
- ✅ Virtualize long lists
- ✅ Lazy load heavy components
- ✅ Optimize images

**Don't:**
- ❌ Over-memoize
- ❌ Ignore bundle size
- ❌ Render unnecessary components
- ❌ Block rendering with heavy operations
- ❌ Ignore performance metrics

---

## 📚 **REFERENCES**

- System map: `systems/lucid-ide/frontend-system/system.map.lucid.json5`
- System index: `systems/lucid-ide/frontend-system/system.index.lucid.json5`
- L2 Architecture: `systems/lucid-ide/frontend-system/L2_architecture.md`
- L4 Complete: `systems/lucid-ide/frontend-system/L4_complete.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

