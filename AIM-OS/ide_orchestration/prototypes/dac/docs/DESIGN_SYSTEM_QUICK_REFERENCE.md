# AIM-OS Design System Quick Reference

**Quick reference guide for using the AIM-OS design system**

---

## 🚀 Getting Started

### 1. Import Design Tokens

```typescript
// CSS tokens are automatically imported via index.css
// TypeScript tokens available via:
import { designTokens, getSystemColor, iconSizes } from '@/styles/design-tokens';
```

### 2. Use Tailwind Classes

```tsx
// Colors
<div className="bg-aimos-bg-primary text-aimos-text-primary">
  Content
</div>

// System Colors
<Brain className="w-5 h-5 text-aimos-cmc" />      // CMC
<Network className="w-5 h-5 text-aimos-hhni" />  // HHNI
<Target className="w-5 h-5 text-aimos-vif" />    // VIF

// Spacing
<div className="p-aimos-4 m-aimos-2">
  Content
</div>

// Typography
<h1 className="font-aimos text-aimos-2xl font-aimos-bold">
  Heading
</h1>
```

### 3. Use CSS Variables

```css
.my-component {
  background: var(--aimos-bg-primary);
  color: var(--aimos-text-primary);
  padding: var(--aimos-space-4);
  border-radius: var(--aimos-radius-md);
  box-shadow: var(--aimos-depth-2);
}
```

---

## 🎨 Color Quick Reference

### Backgrounds
- `bg-aimos-bg-primary` - Main background
- `bg-aimos-bg-secondary` - Secondary background
- `bg-aimos-bg-tertiary` - Tertiary background
- `bg-aimos-bg-elevated` - Elevated surfaces

### Text
- `text-aimos-text-primary` - Primary text
- `text-aimos-text-secondary` - Secondary text
- `text-aimos-text-tertiary` - Tertiary text

### Semantic Colors
- `text-aimos-success` / `bg-aimos-success` - Success
- `text-aimos-warning` / `bg-aimos-warning` - Warning
- `text-aimos-error` / `bg-aimos-error` - Error
- `text-aimos-info` / `bg-aimos-info` - Info

### AIM-OS System Colors
- `text-aimos-cmc` / `bg-aimos-cmc` - CMC (green)
- `text-aimos-hhni` / `bg-aimos-hhni` - HHNI (blue)
- `text-aimos-vif` / `bg-aimos-vif` - VIF (orange)
- `text-aimos-apoe` / `bg-aimos-apoe` - APOE (purple)
- `text-aimos-seg` / `bg-aimos-seg` - SEG (red)
- `text-aimos-cas` / `bg-aimos-cas` - CAS (teal)
- `text-aimos-tcs` / `bg-aimos-tcs` - TCS (cyan)
- `text-aimos-scor` / `bg-aimos-scor` - SCOR (red)

### Interactive Colors
- `bg-aimos-primary` - Primary button
- `bg-aimos-secondary` - Secondary button
- `bg-aimos-accent` - Accent button

---

## 📝 Typography Quick Reference

### Font Families
- `font-aimos` - Inter (UI text)
- `font-aimos-mono` - JetBrains Mono (code)
- `font-aimos-display` - Inter (headings)

### Font Sizes
- `text-aimos-xs` - 12px
- `text-aimos-sm` - 14px
- `text-aimos-base` - 16px (default)
- `text-aimos-lg` - 18px
- `text-aimos-xl` - 20px
- `text-aimos-2xl` - 24px
- `text-aimos-3xl` - 30px
- `text-aimos-4xl` - 36px

### Font Weights
- `font-aimos-light` - 300
- `font-aimos-normal` - 400
- `font-aimos-medium` - 500
- `font-aimos-semibold` - 600
- `font-aimos-bold` - 700

---

## 📏 Spacing Quick Reference

### Spacing Scale (8px base)
- `p-aimos-1` / `m-aimos-1` - 4px
- `p-aimos-2` / `m-aimos-2` - 8px
- `p-aimos-3` / `m-aimos-3` - 12px
- `p-aimos-4` / `m-aimos-4` - 16px
- `p-aimos-6` / `m-aimos-6` - 24px
- `p-aimos-8` / `m-aimos-8` - 32px

---

## 🎯 Icon Quick Reference

### Icon Sizes
```tsx
import { Brain } from 'lucide-react';

// Standard sizes
<Brain className="w-3 h-3" />  // xs - 12px
<Brain className="w-4 h-4" />  // sm - 16px
<Brain className="w-5 h-5" />  // md - 20px (default)
<Brain className="w-6 h-6" />  // lg - 24px
<Brain className="w-8 h-8" />  // xl - 32px
<Brain className="w-12 h-12" /> // 2xl - 48px
```

### System Icons
```tsx
import { Brain, Network, Target, GitBranch, Layers, Shield, Activity, Timeline } from 'lucide-react';

<Brain className="w-5 h-5 text-aimos-cmc" />      // CMC
<Network className="w-5 h-5 text-aimos-hhni" />  // HHNI
<Target className="w-5 h-5 text-aimos-vif" />    // VIF
<GitBranch className="w-5 h-5 text-aimos-apoe" /> // APOE
<Layers className="w-5 h-5 text-aimos-seg" />      // SEG
<Shield className="w-5 h-5 text-aimos-scor" />     // SCOR
<Activity className="w-5 h-5 text-aimos-cas" />    // CAS
<Timeline className="w-5 h-5 text-aimos-tcs" />     // TCS
```

---

## 🧩 Component Quick Reference

### Panel Structure
```tsx
import { PanelHeader, PanelFooter } from '@/components/shared';

<div className="aimos-panel">
  <PanelHeader title="Panel Title" icon={Brain} />
  <div className="aimos-panel-content">
    {/* Content */}
  </div>
  <PanelFooter confidence={0.85} />
</div>
```

### Button
```tsx
<button className="px-aimos-4 py-aimos-2 bg-aimos-primary hover:bg-aimos-primary-hover rounded-aimos-md text-aimos-text-primary font-aimos-medium">
  Button
</button>
```

### Card
```tsx
<div className="bg-aimos-bg-secondary border border-aimos-border-primary rounded-aimos-lg p-aimos-4 shadow-aimos-md">
  <h3 className="text-aimos-xl font-aimos-semibold text-aimos-text-primary mb-aimos-2">
    Card Title
  </h3>
  <p className="text-aimos-base text-aimos-text-secondary">
    Card content
  </p>
</div>
```

---

## ✅ Validation

### Validate Design System Compliance

```typescript
import { validateDesignSystem, generateValidationReport } from '@/utils/designSystemValidator';

// Validate entire page
const validation = validateDesignSystem(document.body);

// Generate report
const report = generateValidationReport(validation);
console.log(report);
```

### Validation Checklist
- [ ] All colors use AIM-OS tokens
- [ ] Typography uses Inter/JetBrains Mono
- [ ] Icons use lucide-react
- [ ] Spacing uses 8px base scale
- [ ] Components use shared components
- [ ] Accessibility (WCAG AA)
- [ ] Performance (< 16ms interactions)

---

## 📚 Full Documentation

See `AIMOS_DESIGN_SYSTEM_PROTOCOL.md` for complete documentation.

---

**Quick Reference v1.0.0**  
**Last Updated:** 2025-01-27

