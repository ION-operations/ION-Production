# AIM-OS Design System Protocol
**Comprehensive Design System & App Integration Protocol**

**Version:** 1.0.0  
**Status:** PRODUCTION  
**Last Updated:** 2025-01-27  
**Purpose:** Unified design system and integration protocol for all AIM-OS applications

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [App Integration Protocol](#app-integration-protocol)
3. [Design System](#design-system)
   - [Color Palette](#color-palette)
   - [Typography](#typography)
   - [Spacing & Layout](#spacing--layout)
   - [Shadows & Depth](#shadows--depth)
   - [Animations & Transitions](#animations--transitions)
4. [Icon System](#icon-system)
5. [Component Library Standards](#component-library-standards)
6. [Layout Principles](#layout-principles)
7. [Professional Aesthetic Guidelines](#professional-aesthetic-guidelines)
8. [Implementation Guide](#implementation-guide)
9. [Validation & Compliance](#validation--compliance)

---

## 🎯 Overview

The AIM-OS Design System Protocol ensures that all applications integrated with AIM-OS and the IDE maintain a consistent, professional, and cohesive aesthetic. This protocol defines:

- **Integration patterns** for apps connecting to IDE and AIM-OS
- **Design tokens** (colors, typography, spacing, shadows, animations)
- **Icon standards** (professional, consistent, non-cartoon)
- **Component patterns** (reusable, accessible, professional)
- **Layout principles** (clean, organized, efficient)
- **Aesthetic guidelines** (professional, modern, polished)

**Core Principle:** Every app integrated with AIM-OS must evolve into the correct aesthetic automatically, ensuring a unified experience across all applications.

---

## 🔌 App Integration Protocol

### Integration Architecture

Apps can integrate with AIM-OS and the IDE through multiple patterns:

#### **1. MCP-Based Integration** (Recommended)
```
App → MCP Client → lucid_mcp_server.py (stdio) → Core AIM-OS Systems
```

**Benefits:**
- Standardized protocol (JSON-RPC 2.0)
- Access to 84+ MCP tools
- Type-safe integration
- Automatic error handling

**Implementation:**
```typescript
import { MCPClient } from '@aimos/mcp-client';

const mcpClient = new MCPClient();
await mcpClient.initialize();

// Use MCP tools
const result = await mcpClient.callTool('store_memory', {
  content: 'App data',
  tags: ['app-integration']
});
```

#### **2. HTTP API Integration**
```
App → HTTP API → Extension Command Server → MCP Client → AIM-OS
```

**Benefits:**
- RESTful interface
- Works from any environment
- Persistent connections
- WebSocket support (optional)

**Implementation:**
```typescript
const response = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'store_memory',
    arguments: { content: 'App data', tags: ['app-integration'] }
  })
});
```

#### **3. Direct Integration**
```
App → Direct Python/TypeScript calls → Core AIM-OS Systems
```

**Benefits:**
- Lowest latency
- Full type safety
- Direct access to internals
- No protocol overhead

**Implementation:**
```typescript
import { CMC } from '@aimos/cmc';
import { HHNI } from '@aimos/hhni';

const atom = await CMC.create_atom({ content: 'App data' });
const results = await HHNI.search({ query: 'app data' });
```

#### **4. Hybrid Integration** (Recommended for Complex Apps)
```
App → Service Layer → [MCP Client | HTTP API | Direct Calls] → AIM-OS
```

**Benefits:**
- Flexible integration
- Fallback mechanisms
- Optimized for each use case
- Best of all worlds

### Integration Checklist

Before integrating an app, ensure:

- [ ] **Design System Compliance:** App uses AIM-OS design tokens
- [ ] **Icon System:** App uses lucide-react icons (no custom/cartoon icons)
- [ ] **Typography:** App uses Inter/JetBrains Mono fonts
- [ ] **Color Palette:** App uses AIM-OS color system
- [ ] **Layout:** App follows AIM-OS layout principles
- [ ] **Component Library:** App uses shared components where possible
- [ ] **Accessibility:** App meets WCAG AA standards
- [ ] **Performance:** App meets performance targets (< 16ms interactions)

---

## 🎨 Design System

### Color Palette

The AIM-OS color palette is **diverse, complex, and dynamic**, with various shades for different contexts while maintaining consistency.

#### **Base Colors (Dark Theme - Default)**

```css
/* Backgrounds */
--aimos-bg-primary: #030712;      /* Main background (gray-950) */
--aimos-bg-secondary: #111827;    /* Secondary background (gray-900) */
--aimos-bg-tertiary: #1f2937;     /* Tertiary background (gray-800) */
--aimos-bg-elevated: #374151;     /* Elevated surfaces (gray-700) */
--aimos-bg-hover: #4b5563;        /* Hover states (gray-600) */

/* Text */
--aimos-text-primary: #f3f4f6;    /* Primary text (gray-100) */
--aimos-text-secondary: #9ca3af;  /* Secondary text (gray-400) */
--aimos-text-tertiary: #6b7280;    /* Tertiary text (gray-500) */
--aimos-text-disabled: #4b5563;   /* Disabled text (gray-600) */

/* Borders & Dividers */
--aimos-border-primary: #374151;  /* Primary borders (gray-700) */
--aimos-border-secondary: #4b5563; /* Secondary borders (gray-600) */
--aimos-border-subtle: #1f2937;    /* Subtle borders (gray-800) */
```

#### **Semantic Colors**

```css
/* Status Colors */
--aimos-success: #10b981;         /* Success/Healthy (green-500) */
--aimos-success-dark: #059669;    /* Success dark (green-600) */
--aimos-success-light: #34d399;   /* Success light (green-400) */
--aimos-success-bg: rgba(16, 185, 129, 0.1); /* Success background */

--aimos-warning: #f59e0b;         /* Warning (amber-500) */
--aimos-warning-dark: #d97706;    /* Warning dark (amber-600) */
--aimos-warning-light: #fbbf24;   /* Warning light (amber-400) */
--aimos-warning-bg: rgba(245, 158, 11, 0.1); /* Warning background */

--aimos-error: #ef4444;            /* Error (red-500) */
--aimos-error-dark: #dc2626;       /* Error dark (red-600) */
--aimos-error-light: #f87171;     /* Error light (red-400) */
--aimos-error-bg: rgba(239, 68, 68, 0.1); /* Error background */

--aimos-info: #3b82f6;             /* Info (blue-500) */
--aimos-info-dark: #2563eb;       /* Info dark (blue-600) */
--aimos-info-light: #60a5fa;      /* Info light (blue-400) */
--aimos-info-bg: rgba(59, 130, 246, 0.1); /* Info background */
```

#### **AIM-OS System Colors**

```css
/* Core System Colors */
--aimos-cmc: #7ee787;              /* CMC (green) */
--aimos-hhni: #79c0ff;             /* HHNI (blue) */
--aimos-vif: #ffa657;               /* VIF (orange) */
--aimos-apoe: #d2a8ff;              /* APOE (purple) */
--aimos-seg: #ff7b72;               /* SEG (red) */
--aimos-cas: #4ec9b0;               /* CAS (teal) */
--aimos-tcs: #569cd6;               /* TCS (cyan) */
--aimos-scor: #f44747;              /* SCOR (red) */

/* System Color Variants */
--aimos-cmc-dark: #56d364;
--aimos-cmc-light: #a0e7a0;
--aimos-cmc-bg: rgba(126, 231, 135, 0.1);

--aimos-hhni-dark: #58a6ff;
--aimos-hhni-light: #a5d6ff;
--aimos-hhni-bg: rgba(121, 192, 255, 0.1);

/* ... (similar variants for all systems) */
```

#### **Interactive Colors**

```css
/* Primary Actions */
--aimos-primary: #3b82f6;           /* Primary (blue-500) */
--aimos-primary-hover: #2563eb;    /* Primary hover (blue-600) */
--aimos-primary-active: #1d4ed8;   /* Primary active (blue-700) */
--aimos-primary-disabled: #1e3a8a; /* Primary disabled (blue-800) */

/* Secondary Actions */
--aimos-secondary: #8b5cf6;        /* Secondary (violet-500) */
--aimos-secondary-hover: #7c3aed;  /* Secondary hover (violet-600) */
--aimos-secondary-active: #6d28d9; /* Secondary active (violet-700) */

/* Accent Colors */
--aimos-accent: #ec4899;            /* Accent (pink-500) */
--aimos-accent-hover: #db2777;      /* Accent hover (pink-600) */
--aimos-accent-active: #be185d;     /* Accent active (pink-700) */
```

#### **Light Theme Variants**

```css
[data-theme="light"] {
  --aimos-bg-primary: #ffffff;
  --aimos-bg-secondary: #f9fafb;
  --aimos-bg-tertiary: #f3f4f6;
  --aimos-text-primary: #111827;
  --aimos-text-secondary: #6b7280;
  /* ... (light theme variants) */
}
```

#### **High Contrast Variants**

```css
[data-theme="high-contrast"] {
  --aimos-bg-primary: #000000;
  --aimos-bg-secondary: #1a1a1a;
  --aimos-text-primary: #ffffff;
  --aimos-text-secondary: #cccccc;
  /* ... (high contrast variants) */
}
```

### Typography

#### **Font Families**

```css
/* Primary Font (UI Text) */
--aimos-font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;

/* Monospace Font (Code) */
--aimos-font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace;

/* Display Font (Headings - Optional) */
--aimos-font-display: 'Inter', sans-serif; /* Use primary for consistency */
```

#### **Font Sizes**

```css
/* Text Sizes */
--aimos-text-xs: 0.75rem;      /* 12px - Labels, captions */
--aimos-text-sm: 0.875rem;    /* 14px - Secondary text, small buttons */
--aimos-text-base: 1rem;      /* 16px - Body text (default) */
--aimos-text-lg: 1.125rem;    /* 18px - Emphasized text */
--aimos-text-xl: 1.25rem;     /* 20px - Large text */
--aimos-text-2xl: 1.5rem;     /* 24px - Section headings */
--aimos-text-3xl: 1.875rem;   /* 30px - Page headings */
--aimos-text-4xl: 2.25rem;    /* 36px - Hero headings */

/* Line Heights */
--aimos-leading-tight: 1.25;
--aimos-leading-normal: 1.5;
--aimos-leading-relaxed: 1.75;
```

#### **Font Weights**

```css
--aimos-font-light: 300;
--aimos-font-normal: 400;
--aimos-font-medium: 500;
--aimos-font-semibold: 600;
--aimos-font-bold: 700;
```

#### **Typography Usage**

```css
/* Headings */
h1 {
  font-family: var(--aimos-font-primary);
  font-size: var(--aimos-text-3xl);
  font-weight: var(--aimos-font-bold);
  line-height: var(--aimos-leading-tight);
  color: var(--aimos-text-primary);
}

h2 {
  font-family: var(--aimos-font-primary);
  font-size: var(--aimos-text-2xl);
  font-weight: var(--aimos-font-semibold);
  line-height: var(--aimos-leading-tight);
  color: var(--aimos-text-primary);
}

/* Body Text */
body {
  font-family: var(--aimos-font-primary);
  font-size: var(--aimos-text-base);
  font-weight: var(--aimos-font-normal);
  line-height: var(--aimos-leading-normal);
  color: var(--aimos-text-primary);
}

/* Code Text */
code {
  font-family: var(--aimos-font-mono);
  font-size: var(--aimos-text-sm);
  font-weight: var(--aimos-font-normal);
  line-height: var(--aimos-leading-normal);
}
```

### Spacing & Layout

#### **Spacing Scale**

```css
/* Spacing Units (8px base) */
--aimos-space-0: 0;
--aimos-space-1: 0.25rem;   /* 4px */
--aimos-space-2: 0.5rem;    /* 8px */
--aimos-space-3: 0.75rem;   /* 12px */
--aimos-space-4: 1rem;      /* 16px */
--aimos-space-5: 1.25rem;   /* 20px */
--aimos-space-6: 1.5rem;    /* 24px */
--aimos-space-8: 2rem;      /* 32px */
--aimos-space-10: 2.5rem;   /* 40px */
--aimos-space-12: 3rem;     /* 48px */
--aimos-space-16: 4rem;     /* 64px */
--aimos-space-20: 5rem;     /* 80px */
--aimos-space-24: 6rem;      /* 96px */
```

#### **Layout Principles**

```css
/* Container Widths */
--aimos-container-sm: 640px;
--aimos-container-md: 768px;
--aimos-container-lg: 1024px;
--aimos-container-xl: 1280px;
--aimos-container-2xl: 1536px;

/* Border Radius */
--aimos-radius-sm: 0.25rem;   /* 4px */
--aimos-radius-md: 0.5rem;    /* 8px */
--aimos-radius-lg: 0.75rem;   /* 12px */
--aimos-radius-xl: 1rem;      /* 16px */
--aimos-radius-full: 9999px;  /* Full circle */
```

#### **Grid System**

```css
/* Grid Gaps */
--aimos-grid-gap-sm: var(--aimos-space-2);  /* 8px */
--aimos-grid-gap-md: var(--aimos-space-4);  /* 16px */
--aimos-grid-gap-lg: var(--aimos-space-6);  /* 24px */

/* Panel Spacing */
--aimos-panel-padding: var(--aimos-space-4);  /* 16px */
--aimos-panel-gap: var(--aimos-space-3);      /* 12px */
```

### Shadows & Depth

```css
/* Shadow Levels */
--aimos-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--aimos-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--aimos-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--aimos-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--aimos-shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Depth Levels */
--aimos-depth-0: none;                    /* Flat */
--aimos-depth-1: var(--aimos-shadow-sm);  /* Subtle elevation */
--aimos-depth-2: var(--aimos-shadow-md);  /* Card elevation */
--aimos-depth-3: var(--aimos-shadow-lg);  /* Modal elevation */
--aimos-depth-4: var(--aimos-shadow-xl);  /* Overlay elevation */
--aimos-depth-5: var(--aimos-shadow-2xl); /* Maximum elevation */
```

### Animations & Transitions

```css
/* Transition Durations */
--aimos-transition-fast: 150ms;
--aimos-transition-base: 200ms;
--aimos-transition-slow: 300ms;
--aimos-transition-slower: 500ms;

/* Easing Functions */
--aimos-ease-in: cubic-bezier(0.4, 0, 1, 1);
--aimos-ease-out: cubic-bezier(0, 0, 0.2, 1);
--aimos-ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--aimos-ease-standard: cubic-bezier(0.4, 0, 0.2, 1);

/* Standard Transitions */
--aimos-transition-standard: var(--aimos-transition-base) var(--aimos-ease-standard);
--aimos-transition-hover: var(--aimos-transition-fast) var(--aimos-ease-out);
--aimos-transition-focus: var(--aimos-transition-fast) var(--aimos-ease-out);
```

#### **Animation Patterns**

```css
/* Hover Effects */
.hover-lift {
  transition: transform var(--aimos-transition-hover), box-shadow var(--aimos-transition-hover);
}
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--aimos-shadow-lg);
}

/* Focus Effects */
.focus-ring {
  transition: box-shadow var(--aimos-transition-focus);
}
.focus-ring:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
}

/* Loading States */
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loading-spin {
  animation: spin 1s linear infinite;
}

/* Pulse Animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.loading-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

## 🎯 Icon System

### Icon Library: Lucide React

**Primary Library:** `lucide-react` (v0.263.1+)

**Why Lucide React:**
- Professional, clean, modern icons
- Consistent stroke width and style
- Comprehensive icon set (1000+ icons)
- Tree-shakeable (import only what you need)
- TypeScript support
- Accessible by default

### Icon Standards

#### **Icon Sizes**

```typescript
// Standard Icon Sizes
const iconSizes = {
  xs: 'w-3 h-3',    // 12px - Inline with small text
  sm: 'w-4 h-4',    // 16px - Inline with body text
  md: 'w-5 h-5',    // 20px - Standard size
  lg: 'w-6 h-6',    // 24px - Emphasized
  xl: 'w-8 h-8',    // 32px - Large icons
  '2xl': 'w-12 h-12' // 48px - Hero icons
};
```

#### **Icon Usage**

```typescript
import { 
  Brain, 
  Activity, 
  Database, 
  Shield, 
  Target, 
  Network, 
  Layers, 
  Timeline,
  Zap,
  Settings,
  Search,
  Code,
  FileText,
  GitBranch,
  Globe,
  Eye,
  MessageSquare,
  User,
  LogOut,
  Bell,
  HelpCircle
} from 'lucide-react';

// Example: System Icons
<Brain className="w-5 h-5 text-aimos-cmc" />      // CMC
<Network className="w-5 h-5 text-aimos-hhni" />  // HHNI
<Target className="w-5 h-5 text-aimos-vif" />    // VIF
<GitBranch className="w-5 h-5 text-aimos-apoe" /> // APOE
<Layers className="w-5 h-5 text-aimos-seg" />      // SEG
<Shield className="w-5 h-5 text-aimos-scor" />     // SCOR
```

#### **Icon Guidelines**

1. **Always use lucide-react** - No custom icons, no cartoon icons, no emoji icons
2. **Consistent stroke width** - Use default stroke (2px)
3. **Proper sizing** - Use standard sizes (xs, sm, md, lg, xl, 2xl)
4. **Color consistency** - Use AIM-OS color tokens
5. **Accessibility** - Include `aria-label` for icon-only buttons
6. **Semantic meaning** - Choose icons that clearly represent their function

#### **Forbidden Icon Patterns**

❌ **DO NOT USE:**
- Custom SVG icons (unless absolutely necessary and approved)
- Cartoon-style icons
- Emoji as icons (🔄, ⚙️, etc.)
- Icon fonts (Font Awesome, Material Icons, etc.)
- Inconsistent icon libraries

✅ **DO USE:**
- Lucide React icons exclusively
- Consistent sizing and styling
- Proper semantic meaning
- Accessibility attributes

---

## 🧩 Component Library Standards

### Shared Components

All apps should use shared components from `ide_orchestration/prototypes/dac/src/components/shared/`:

- `LoadingSpinner` - Loading states
- `ErrorDisplay` - Error handling
- `ConfidenceBadge` - Confidence indicators
- `ContradictionAlert` - Contradiction warnings
- `StatusIndicator` - Status displays
- `EmptyState` - Empty states
- `PanelHeader` - Panel headers
- `PanelFooter` - Panel footers

### Component Patterns

#### **Button Component**

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: LucideIcon;
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
}

// Usage
<Button variant="primary" size="md" icon={Save}>
  Save Changes
</Button>
```

#### **Input Component**

```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number';
  placeholder?: string;
  icon?: LucideIcon;
  error?: string;
  disabled?: boolean;
}

// Usage
<Input 
  type="text" 
  placeholder="Search..." 
  icon={Search}
  error={errors.search}
/>
```

#### **Card Component**

```typescript
interface CardProps {
  title?: string;
  description?: string;
  icon?: LucideIcon;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

// Usage
<Card 
  title="Memory Browser" 
  description="Browse AIM-OS memory"
  icon={Database}
  actions={<Button>Refresh</Button>}
>
  {/* Card content */}
</Card>
```

### Component Guidelines

1. **Consistent Styling** - Use AIM-OS design tokens
2. **Accessibility** - WCAG AA compliant
3. **Type Safety** - Full TypeScript support
4. **Documentation** - JSDoc comments for all props
5. **Testing** - Unit tests for all components
6. **Performance** - Optimized rendering (< 16ms)

---

## 📐 Layout Principles

### Layout Structure

```typescript
// Standard Layout Structure
<IDELayout>
  <TopBar />
  <MainContent>
    <LeftSidebar />
    <CenterPanel />
    <RightSidebar />
  </MainContent>
  <BottomPanel />
</IDELayout>
```

### Layout Guidelines

1. **Consistent Spacing** - Use spacing scale (8px base)
2. **Clear Hierarchy** - Visual hierarchy through size, color, spacing
3. **Responsive Design** - Works on all screen sizes
4. **Panel Management** - Resizable, collapsible panels
5. **Grid System** - Use CSS Grid for complex layouts
6. **Flexbox** - Use Flexbox for simple layouts

### Panel Standards

```css
/* Panel Styling */
.panel {
  background: var(--aimos-bg-secondary);
  border: 1px solid var(--aimos-border-primary);
  border-radius: var(--aimos-radius-md);
  padding: var(--aimos-panel-padding);
  box-shadow: var(--aimos-depth-1);
}

/* Panel Header */
.panel-header {
  padding: var(--aimos-space-4);
  border-bottom: 1px solid var(--aimos-border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Panel Content */
.panel-content {
  padding: var(--aimos-space-4);
  overflow-y: auto;
}

/* Panel Footer */
.panel-footer {
  padding: var(--aimos-space-3);
  border-top: 1px solid var(--aimos-border-primary);
  background: var(--aimos-bg-tertiary);
}
```

---

## ✨ Professional Aesthetic Guidelines

### Core Principles

1. **Professional & Neat**
   - Clean, organized layouts
   - Consistent spacing and alignment
   - No clutter or unnecessary elements
   - Clear visual hierarchy

2. **Modern & Polished**
   - Contemporary design patterns
   - Smooth animations and transitions
   - Professional color palette
   - High-quality icons and typography

3. **Consistent & Cohesive**
   - Same design tokens across all apps
   - Unified icon system
   - Consistent component patterns
   - Cohesive visual language

4. **Accessible & Inclusive**
   - WCAG AA compliance
   - Keyboard navigation
   - Screen reader support
   - High contrast support

### Visual Quality Standards

#### **Color Usage**
- Use semantic colors for status (success, warning, error, info)
- Use system colors for AIM-OS system indicators
- Maintain sufficient contrast ratios (4.5:1 minimum)
- Avoid color-only information (use icons + text)

#### **Typography**
- Use Inter for UI text (professional, readable)
- Use JetBrains Mono for code (clear, consistent)
- Maintain consistent font sizes and weights
- Ensure readable line heights (1.5 minimum)

#### **Icons**
- Use lucide-react exclusively
- Consistent sizing and styling
- Proper semantic meaning
- Accessible (aria-labels)

#### **Spacing**
- Use 8px base spacing scale
- Consistent padding and margins
- Clear visual separation
- No arbitrary spacing values

#### **Shadows & Depth**
- Subtle shadows for elevation
- Consistent depth levels
- No excessive shadows
- Professional depth hierarchy

---

## 🚀 Implementation Guide

### Step 1: Install Dependencies

```bash
npm install lucide-react
npm install @aimos/design-tokens  # (if available)
```

### Step 2: Import Design Tokens

```typescript
// In your CSS or Tailwind config
import '@aimos/design-tokens/css/tokens.css';

// Or use CSS variables directly
:root {
  /* Copy AIM-OS design tokens */
}
```

### Step 3: Use Shared Components

```typescript
import { 
  LoadingSpinner, 
  ErrorDisplay, 
  PanelHeader 
} from '@aimos/shared-components';
```

### Step 4: Follow Icon Standards

```typescript
import { Brain, Activity, Database } from 'lucide-react';

<Brain className="w-5 h-5 text-aimos-cmc" />
```

### Step 5: Apply Layout Principles

```typescript
// Use standard layout structure
<IDELayout>
  <YourApp />
</IDELayout>
```

### Step 6: Validate Compliance

```bash
npm run validate-design-system
```

---

## ✅ Validation & Compliance

### Design System Validator

```typescript
// Design System Validator
interface DesignSystemValidation {
  colors: boolean;        // Uses AIM-OS color tokens
  typography: boolean;    // Uses Inter/JetBrains Mono
  icons: boolean;         // Uses lucide-react
  spacing: boolean;       // Uses 8px base scale
  components: boolean;    // Uses shared components
  accessibility: boolean; // WCAG AA compliant
  performance: boolean;   // < 16ms interactions
}

function validateApp(app: App): DesignSystemValidation {
  // Validation logic
}
```

### Compliance Checklist

Before deploying an app:

- [ ] **Colors:** All colors use AIM-OS design tokens
- [ ] **Typography:** Uses Inter/JetBrains Mono fonts
- [ ] **Icons:** Uses lucide-react exclusively
- [ ] **Spacing:** Uses 8px base spacing scale
- [ ] **Components:** Uses shared components where possible
- [ ] **Layout:** Follows AIM-OS layout principles
- [ ] **Accessibility:** WCAG AA compliant
- [ ] **Performance:** < 16ms interaction latency
- [ ] **Design Review:** Passed design system review

### Automated Validation

```bash
# Run design system validation
npm run validate-design-system

# Check for design system violations
npm run lint-design-system

# Generate design system report
npm run design-system-report
```

---

## 📚 References

### External Resources
- **Lucide React:** https://lucide.dev/
- **Inter Font:** https://rsms.me/inter/
- **JetBrains Mono:** https://www.jetbrains.com/lp/mono/
- **WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/

### AIM-OS Design System Files
- **Design Tokens (CSS):** `src/styles/design-tokens.css`
- **Design Tokens (TypeScript):** `src/styles/design-tokens.ts`
- **Tailwind Config:** `tailwind.config.js`
- **Design System Validator:** `src/utils/designSystemValidator.ts`
- **Quick Reference:** `docs/DESIGN_SYSTEM_QUICK_REFERENCE.md`
- **AIM-OS Integration Docs:** `ide_orchestration/prototypes/dac/docs/`

---

## 🎯 Summary

The AIM-OS Design System Protocol ensures that all applications integrated with AIM-OS maintain a **professional, consistent, and cohesive aesthetic**. By following this protocol, apps automatically evolve into the correct aesthetic, creating a unified experience across all AIM-OS applications.

**Key Takeaways:**
- Use AIM-OS design tokens (colors, typography, spacing)
- Use lucide-react icons exclusively (no custom/cartoon icons)
- Follow layout principles (clean, organized, professional)
- Use shared components where possible
- Maintain accessibility and performance standards
- Validate compliance before deployment

**Remember:** The goal is a **unified, professional aesthetic** across all AIM-OS applications. Every app should feel like part of the same system, not a separate application.

---

**Version:** 1.0.0  
**Status:** PRODUCTION  
**Last Updated:** 2025-01-27  
**Maintained By:** AIM-OS Design Team

