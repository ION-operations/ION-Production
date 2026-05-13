# Component Architecture Guide
## V2 Component Architecture Patterns

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Guide for component architecture in V2  
**Status:** Architecture Guide Complete

---

## 🏗️ **COMPONENT ARCHITECTURE PATTERNS**

### **1. Panel Components**

#### **Structure:**
```typescript
// Panel component pattern
import React from 'react'
import { useAIMOS } from '@/hooks'
import type { PanelProps } from '@/types'

export const MyPanel: React.FC<PanelProps> = () => {
  const { cmc, hhni } = useAIMOS()
  
  // Panel logic here
  
  return (
    <div className="h-full flex flex-col">
      {/* Panel content */}
    </div>
  )
}
```

#### **Best Practices:**
- Use `useAIMOS` hook for AIM-OS integration
- Consistent styling with Tailwind classes
- Loading states for async operations
- Error handling with user-friendly messages
- Accessibility (ARIA labels, keyboard navigation)

---

### **2. Layout Components**

#### **Structure:**
```typescript
// Layout component pattern
import React from 'react'
import { PanelGroup, Panel } from 'react-resizable-panels'
import { usePanelStore } from '@/stores'

export const MyLayout: React.FC = () => {
  const { panels, getPanelsByZone } = usePanelStore()
  
  // Layout logic here
  
  return (
    <PanelGroup direction="horizontal">
      {/* Panels */}
    </PanelGroup>
  )
}
```

#### **Best Practices:**
- Use `usePanelStore` for panel state
- Responsive design with react-resizable-panels
- Panel persistence via Zustand
- Layout presets support

---

### **3. Hook Usage Pattern**

#### **Unified Hook:**
```typescript
// Use unified hook for all systems
const { cmc, hhni, vif } = useAIMOS()

// Or use individual hooks
const cmc = useCMC()
const hhni = useHHNI()
```

#### **Best Practices:**
- Use unified hook (`useAIMOS`) for multiple systems
- Use individual hooks for single-system components
- Handle loading states
- Handle errors gracefully
- Show connection status

---

### **4. State Management Pattern**

#### **Zustand Stores:**
```typescript
// Use Zustand stores for global state
import { usePanelStore } from '@/stores'

const { panels, addPanel, movePanel } = usePanelStore()
```

#### **Local State:**
```typescript
// Use React hooks for local state
const [expanded, setExpanded] = useState(false)
```

#### **Best Practices:**
- Zustand for global state (panels, layout, settings)
- React hooks for component-local state
- Avoid prop drilling
- Use selectors for performance

---

### **5. Type Safety**

#### **TypeScript Types:**
```typescript
// Import types from hooks
import type { Memory, CMCInterface } from '@/hooks'

// Use types consistently
const memory: Memory = { ... }
```

#### **Best Practices:**
- Import types from centralized locations
- Use type inference where possible
- Define component prop types
- Use type guards for runtime checks

---

### **6. Error Boundaries**

#### **Error Boundary Pattern:**
```typescript
import React, { ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<Props, State> {
  // Error boundary implementation
}
```

#### **Best Practices:**
- Wrap panels in error boundaries
- Show user-friendly error messages
- Log errors for debugging
- Provide recovery options

---

### **7. Performance Optimization**

#### **Memoization:**
```typescript
import { useMemo, useCallback } from 'react'

const expensiveValue = useMemo(() => {
  // Expensive computation
}, [dependencies])

const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies])
```

#### **Best Practices:**
- Memoize expensive computations
- Use `useCallback` for event handlers
- Use `React.memo` for expensive components
- Virtualize long lists

---

### **8. Accessibility**

#### **ARIA Labels:**
```typescript
<button
  aria-label="Close panel"
  aria-expanded={isExpanded}
  onClick={handleToggle}
>
  Close
</button>
```

#### **Keyboard Navigation:**
```typescript
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    handleClose()
  }
}
```

#### **Best Practices:**
- Add ARIA labels to interactive elements
- Support keyboard navigation
- Ensure color contrast (WCAG AA)
- Test with screen readers

---

## 📋 **COMPONENT ORGANIZATION**

### **File Structure:**
```
src/
  components/
    panels/          # Panel components
      MyPanel.tsx
    layouts/         # Layout components
      MyLayout.tsx
    shared/          # Shared components
      Button.tsx
      Loading.tsx
  hooks/             # Custom hooks
    useAIMOS.ts
    index.ts
  stores/            # Zustand stores
    panelStore.ts
    index.ts
  types/             # TypeScript types
    index.ts
```

---

## 🎯 **INTEGRATION CHECKLIST**

When creating new components:

- [ ] Use `useAIMOS` hook for AIM-OS integration
- [ ] Use `usePanelStore` for panel state
- [ ] Add TypeScript types
- [ ] Handle loading states
- [ ] Handle errors gracefully
- [ ] Add accessibility features
- [ ] Optimize performance
- [ ] Add error boundaries
- [ ] Follow naming conventions
- [ ] Document component purpose

---

**Status:** Architecture Guide Complete  
**Next:** Apply patterns to existing components 💙

