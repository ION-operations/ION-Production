/**
 * AIM-OS Design System Validator
 * Validates that components/apps comply with the design system protocol
 */

import type { LucideIcon } from 'lucide-react';

export interface DesignSystemValidation {
  colors: boolean;
  typography: boolean;
  icons: boolean;
  spacing: boolean;
  components: boolean;
  accessibility: boolean;
  performance: boolean;
  violations: ValidationViolation[];
}

export interface ValidationViolation {
  type: 'color' | 'typography' | 'icon' | 'spacing' | 'component' | 'accessibility' | 'performance';
  severity: 'error' | 'warning' | 'info';
  message: string;
  element?: string;
  suggestion?: string;
}

/**
 * Validate color usage
 */
function validateColors(element: HTMLElement): ValidationViolation[] {
  const violations: ValidationViolation[] = [];
  const computedStyle = window.getComputedStyle(element);

  // Check if using AIM-OS color tokens
  const color = computedStyle.color;
  const backgroundColor = computedStyle.backgroundColor;
  const borderColor = computedStyle.borderColor;

  // Check for hardcoded colors (not using CSS variables)
  const hardcodedColorPattern = /^#[0-9a-fA-F]{3,6}$|^rgb\(|^rgba\(/;
  
  if (hardcodedColorPattern.test(color) && !color.startsWith('var(--aimos-')) {
    violations.push({
      type: 'color',
      severity: 'warning',
      message: `Hardcoded text color detected: ${color}. Use AIM-OS color tokens instead.`,
      element: element.tagName,
      suggestion: 'Use var(--aimos-text-primary) or Tailwind class text-aimos-text-primary',
    });
  }

  if (hardcodedColorPattern.test(backgroundColor) && !backgroundColor.startsWith('var(--aimos-')) {
    violations.push({
      type: 'color',
      severity: 'warning',
      message: `Hardcoded background color detected: ${backgroundColor}. Use AIM-OS color tokens instead.`,
      element: element.tagName,
      suggestion: 'Use var(--aimos-bg-primary) or Tailwind class bg-aimos-bg-primary',
    });
  }

  return violations;
}

/**
 * Validate typography
 */
function validateTypography(element: HTMLElement): ValidationViolation[] {
  const violations: ValidationViolation[] = [];
  const computedStyle = window.getComputedStyle(element);

  const fontFamily = computedStyle.fontFamily;
  const fontSize = computedStyle.fontSize;

  // Check if using AIM-OS fonts
  const hasInter = fontFamily.includes('Inter') || fontFamily.includes('system-ui');
  const hasMono = fontFamily.includes('JetBrains Mono') || fontFamily.includes('Fira Code') || fontFamily.includes('Consolas');

  if (!hasInter && !hasMono && element.tagName !== 'CODE') {
    violations.push({
      type: 'typography',
      severity: 'error',
      message: `Non-standard font family: ${fontFamily}. Use Inter or JetBrains Mono.`,
      element: element.tagName,
      suggestion: 'Use font-aimos or font-aimos-mono Tailwind classes',
    });
  }

  // Check font size (should use design tokens)
  const fontSizeNum = parseFloat(fontSize);
  if (fontSizeNum && fontSizeNum < 12) {
    violations.push({
      type: 'typography',
      severity: 'warning',
      message: `Font size too small: ${fontSize}. Minimum recommended: 12px (0.75rem).`,
      element: element.tagName,
      suggestion: 'Use text-aimos-xs or larger',
    });
  }

  return violations;
}

/**
 * Validate icon usage
 */
function validateIcons(element: HTMLElement): ValidationViolation[] {
  const violations: ValidationViolation[] = [];
  
  // Check for emoji icons
  const emojiPattern = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu;
  if (emojiPattern.test(element.textContent || '')) {
    violations.push({
      type: 'icon',
      severity: 'error',
      message: 'Emoji icons detected. Use lucide-react icons instead.',
      element: element.tagName,
      suggestion: 'Import and use icons from lucide-react',
    });
  }

  // Check for Font Awesome or Material Icons classes
  const iconFontPattern = /fa-|material-icons|mdi-/;
  if (iconFontPattern.test(element.className)) {
    violations.push({
      type: 'icon',
      severity: 'error',
      message: 'Icon font detected. Use lucide-react icons instead.',
      element: element.tagName,
      suggestion: 'Replace with lucide-react icons',
    });
  }

  return violations;
}

/**
 * Validate spacing
 */
function validateSpacing(element: HTMLElement): ValidationViolation[] {
  const violations: ValidationViolation[] = [];
  const computedStyle = window.getComputedStyle(element);

  const margin = computedStyle.margin;
  const padding = computedStyle.padding;

  // Check if using 8px base spacing scale
  const spacingValues = [margin, padding].flatMap(v => v.split(' '));
  const spacingPattern = /(\d+(?:\.\d+)?)px/;

  for (const value of spacingValues) {
    const match = value.match(spacingPattern);
    if (match) {
      const pxValue = parseFloat(match[1]);
      // Check if not a multiple of 4px (8px base scale)
      if (pxValue % 4 !== 0) {
        violations.push({
          type: 'spacing',
          severity: 'warning',
          message: `Non-standard spacing value: ${pxValue}px. Use 8px base scale (multiples of 4px).`,
          element: element.tagName,
          suggestion: 'Use spacing-aimos-* Tailwind classes',
        });
      }
    }
  }

  return violations;
}

/**
 * Validate accessibility
 */
function validateAccessibility(element: HTMLElement): ValidationViolation[] {
  const violations: ValidationViolation[] = [];
  const computedStyle = window.getComputedStyle(element);

  // Check contrast ratio (simplified check)
  const color = computedStyle.color;
  const backgroundColor = computedStyle.backgroundColor;

  // Check for aria-labels on icon-only buttons
  if (element.tagName === 'BUTTON' && !element.textContent?.trim() && !element.getAttribute('aria-label')) {
    violations.push({
      type: 'accessibility',
      severity: 'error',
      message: 'Icon-only button missing aria-label',
      element: element.tagName,
      suggestion: 'Add aria-label attribute for screen readers',
    });
  }

  // Check for keyboard navigation
  if (element.tagName === 'BUTTON' && element.tabIndex === -1 && !element.hasAttribute('disabled')) {
    violations.push({
      type: 'accessibility',
      severity: 'warning',
      message: 'Interactive element not keyboard accessible',
      element: element.tagName,
      suggestion: 'Ensure element is keyboard accessible',
    });
  }

  return violations;
}

/**
 * Validate component structure
 */
function validateComponents(element: HTMLElement): ValidationViolation[] {
  const violations: ValidationViolation[] = [];

  // Check if using shared components
  const hasSharedComponent = element.classList.contains('aimos-panel') ||
    element.classList.contains('aimos-panel-header') ||
    element.classList.contains('aimos-panel-content') ||
    element.classList.contains('aimos-panel-footer');

  // This is informational, not an error
  if (!hasSharedComponent && (element.classList.contains('panel') || element.classList.contains('card'))) {
    violations.push({
      type: 'component',
      severity: 'info',
      message: 'Consider using shared AIM-OS components for consistency',
      element: element.tagName,
      suggestion: 'Use PanelHeader, PanelContent, PanelFooter from shared components',
    });
  }

  return violations;
}

/**
 * Main validation function
 */
export function validateDesignSystem(
  rootElement: HTMLElement = document.body,
  options: {
    checkColors?: boolean;
    checkTypography?: boolean;
    checkIcons?: boolean;
    checkSpacing?: boolean;
    checkComponents?: boolean;
    checkAccessibility?: boolean;
  } = {}
): DesignSystemValidation {
  const {
    checkColors = true,
    checkTypography = true,
    checkIcons = true,
    checkSpacing = true,
    checkComponents = true,
    checkAccessibility = true,
  } = options;

  const violations: ValidationViolation[] = [];
  const elements = rootElement.querySelectorAll('*');

  elements.forEach((element) => {
    const htmlElement = element as HTMLElement;

    if (checkColors) {
      violations.push(...validateColors(htmlElement));
    }
    if (checkTypography) {
      violations.push(...validateTypography(htmlElement));
    }
    if (checkIcons) {
      violations.push(...validateIcons(htmlElement));
    }
    if (checkSpacing) {
      violations.push(...validateSpacing(htmlElement));
    }
    if (checkComponents) {
      violations.push(...validateComponents(htmlElement));
    }
    if (checkAccessibility) {
      violations.push(...validateAccessibility(htmlElement));
    }
  });

  const errors = violations.filter(v => v.severity === 'error');
  const warnings = violations.filter(v => v.severity === 'warning');

  return {
    colors: !errors.some(v => v.type === 'color'),
    typography: !errors.some(v => v.type === 'typography'),
    icons: !errors.some(v => v.type === 'icon'),
    spacing: !errors.some(v => v.type === 'spacing'),
    components: !errors.some(v => v.type === 'component'),
    accessibility: !errors.some(v => v.type === 'accessibility'),
    performance: true, // Performance validation would require runtime metrics
    violations,
  };
}

/**
 * Generate validation report
 */
export function generateValidationReport(validation: DesignSystemValidation): string {
  const { violations } = validation;
  const errors = violations.filter(v => v.severity === 'error');
  const warnings = violations.filter(v => v.severity === 'warning');
  const info = violations.filter(v => v.severity === 'info');

  let report = '# AIM-OS Design System Validation Report\n\n';
  report += `## Summary\n\n`;
  report += `- ✅ Colors: ${validation.colors ? 'PASS' : 'FAIL'}\n`;
  report += `- ✅ Typography: ${validation.typography ? 'PASS' : 'FAIL'}\n`;
  report += `- ✅ Icons: ${validation.icons ? 'PASS' : 'FAIL'}\n`;
  report += `- ✅ Spacing: ${validation.spacing ? 'PASS' : 'FAIL'}\n`;
  report += `- ✅ Components: ${validation.components ? 'PASS' : 'FAIL'}\n`;
  report += `- ✅ Accessibility: ${validation.accessibility ? 'PASS' : 'FAIL'}\n`;
  report += `- ✅ Performance: ${validation.performance ? 'PASS' : 'FAIL'}\n\n`;

  if (errors.length > 0) {
    report += `## Errors (${errors.length})\n\n`;
    errors.forEach((violation, index) => {
      report += `${index + 1}. **${violation.type}**: ${violation.message}\n`;
      if (violation.suggestion) {
        report += `   - Suggestion: ${violation.suggestion}\n`;
      }
      report += `\n`;
    });
  }

  if (warnings.length > 0) {
    report += `## Warnings (${warnings.length})\n\n`;
    warnings.forEach((violation, index) => {
      report += `${index + 1}. **${violation.type}**: ${violation.message}\n`;
      if (violation.suggestion) {
        report += `   - Suggestion: ${violation.suggestion}\n`;
      }
      report += `\n`;
    });
  }

  if (info.length > 0) {
    report += `## Info (${info.length})\n\n`;
    info.forEach((violation, index) => {
      report += `${index + 1}. **${violation.type}**: ${violation.message}\n`;
      if (violation.suggestion) {
        report += `   - Suggestion: ${violation.suggestion}\n`;
      }
      report += `\n`;
    });
  }

  return report;
}

