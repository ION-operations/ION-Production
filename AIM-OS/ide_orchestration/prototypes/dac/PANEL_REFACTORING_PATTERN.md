# Panel Refactoring Pattern Guide
## V2 Foundation Enhancement - Standardizing Panel Architecture

**Created:** 2025-11-08  
**Purpose:** Guide for refactoring existing panels to use BasePanel component  
**Status:** Active

---

## 🎯 **REFACTORING GOALS**

1. **Consistency** - All panels use the same structure and patterns
2. **Maintainability** - Shared functionality in one place (BasePanel)
3. **AIM-OS Integration** - Standardized confidence, contradiction, and status indicators
4. **Error Handling** - Consistent loading and error states
5. **Code Reduction** - Remove duplicate header/footer code

---

## 📋 **REFACTORING STEPS**

### **Step 1: Update Imports**

**Before:**
```typescript
import React, { useState, useEffect } from 'react'
import { useCMC } from '../hooks/useAIMOS'
import { Brain } from 'lucide-react'
```

**After:**
```typescript
import React, { useState, useEffect } from 'react'
import { useCMC } from '../hooks/useAIMOS'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import { Brain } from 'lucide-react'
```

---

### **Step 2: Add State Management**

**Add loading and error states:**
```typescript
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)

useEffect(() => {
  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      // Load data...
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }
  loadData()
}, [])
```

---

### **Step 3: Calculate AIM-OS Metrics**

**Calculate confidence, contradictions, atom count:**
```typescript
// Calculate overall confidence
const overallConfidence = data ? calculateConfidence(data) : undefined

// Determine confidence band
const confidenceBand = overallConfidence 
  ? (overallConfidence >= 0.90 ? 'A' 
     : overallConfidence >= 0.70 ? 'B' 
     : 'C')
  : undefined

// Count contradictions
const contradictionCount = contradictions?.length || 0

// Count atoms/data items
const atomCount = data?.length || 0
```

---

### **Step 4: Wrap Content with BasePanel**

**Before:**
```typescript
return (
  <div className="h-full flex flex-col bg-gray-900">
    {/* Header */}
    <div className="p-3 border-b border-gray-700">
      <h3>Panel Title</h3>
    </div>
    
    {/* Content */}
    <div className="flex-1 overflow-auto">
      {/* Panel content */}
    </div>
    
    {/* Footer */}
    <div className="p-2 border-t border-gray-700">
      Status
    </div>
  </div>
)
```

**After:**
```typescript
return (
  <BasePanel
    id="panel-unique-id"
    title="Panel Title"
    icon={PanelIcon}
    description="Panel description"
    loading={loading}
    error={error}
    empty={!loading && !error && !data}
    emptyMessage="No data available"
    confidence={overallConfidence}
    confidenceBand={confidenceBand}
    contradictionCount={contradictionCount}
    atomCount={atomCount}
    footerContent={
      // Custom footer content if needed
      <div>Custom Status</div>
    }
  >
    {/* Panel content - no header/footer needed */}
    <div className="p-3">
      {/* Panel-specific content */}
    </div>
  </BasePanel>
)
```

---

### **Step 5: Remove Duplicate Code**

**Remove:**
- Custom header divs (BasePanel provides this)
- Custom footer divs (BasePanel provides this, or use footerContent)
- Loading spinners (BasePanel handles this)
- Error displays (BasePanel handles this)
- Empty states (BasePanel handles this)

**Keep:**
- Panel-specific content
- Panel-specific logic
- Panel-specific styling (if needed)

---

## 📝 **EXAMPLE: SystemStatus Refactoring**

**Before:** 350+ lines with custom header/footer/loading/error handling

**After:** ~200 lines, using BasePanel for shared functionality

**Key Changes:**
1. ✅ Added loading/error state management
2. ✅ Wrapped content with BasePanel
3. ✅ Removed duplicate header/footer code
4. ✅ Added confidence and contradiction indicators
5. ✅ Custom footerContent for system status

---

## 🎨 **BASE PANEL PROPS REFERENCE**

```typescript
interface BasePanelProps {
  // Identity
  id: string                    // Unique panel ID
  title: string                 // Panel title
  icon?: React.ElementType      // Panel icon component
  description?: string           // Panel description
  
  // Content
  children: ReactNode           // Panel content
  
  // States
  loading?: boolean             // Show loading state
  error?: string | null         // Show error state
  empty?: boolean               // Show empty state
  emptyMessage?: string         // Empty state message
  
  // AIM-OS Integration
  confidence?: number           // Confidence score (0-1)
  confidenceBand?: 'A' | 'B' | 'C' | 'green' | 'yellow' | 'red'
  contradictionCount?: number   // Number of contradictions
  atomCount?: number            // Number of atoms/data items
  
  // Actions
  onClose?: () => void         // Close panel handler
  onSettings?: () => void       // Settings handler
  actions?: ReactNode          // Custom action buttons
  
  // Customization
  className?: string            // Additional CSS classes
  headerClassName?: string      // Header CSS classes
  contentClassName?: string     // Content CSS classes
  footerClassName?: string      // Footer CSS classes
  
  // Footer
  showFooter?: boolean          // Show/hide footer (default: true)
  footerContent?: ReactNode     // Custom footer content
}
```

---

## ✅ **REFACTORING CHECKLIST**

- [ ] Updated imports (BasePanel, shared components)
- [ ] Added loading state management
- [ ] Added error state management
- [ ] Calculated AIM-OS metrics (confidence, contradictions, atom count)
- [ ] Wrapped content with BasePanel
- [ ] Removed duplicate header code
- [ ] Removed duplicate footer code (or moved to footerContent)
- [ ] Removed duplicate loading/error/empty state code
- [ ] Tested panel functionality
- [ ] Verified AIM-OS integration (confidence badges, contradiction alerts)

---

## 🚀 **NEXT PANELS TO REFACTOR**

**Priority Order:**
1. ✅ SystemStatus (COMPLETE)
2. MemoryBrowser (next)
3. FileTree
4. ContextWeb
5. TimelineView
6. OutlinePanel
7. ProblemsPanel
8. TerminalPanel
9. CodeEditor
10. EvolutionExplorer
11. ConsciousnessVisualization
12. AIMOSOrchestration

---

**Status:** Refactoring pattern established, SystemStatus complete, ready for next panels

