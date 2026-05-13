# Advanced Monaco Editor

A sophisticated Monaco Editor wrapper with advanced features including AI-powered code intelligence, natural language descriptions, interactive code exploration, and comprehensive theming.

## Features

### 🧠 AI-Powered Intelligence
- **Symbol Detection**: Automatic detection of code symbols with enhanced information
- **Code Analysis**: Real-time analysis with SpecBlocks, BlueprintSlices, and TimelineSummaries
- **AIM-OS Integration**: Full integration with all 6 core AIM-OS services
- **Natural Language Descriptions**: Rich, context-aware descriptions for code elements

### 🎨 Advanced UI Components
- **Smart Dropdowns**: Context-aware dropdowns with natural language descriptions
- **Rich Context Menus**: Grouped, intelligent context menus with filtering
- **Enhanced Tooltips**: Detailed tooltips with metadata and examples
- **Interactive Widgets**: Custom widgets for code exploration and editing

### 🎭 Comprehensive Theming
- **Theme Manager**: Flexible theme management with persistence
- **Theme Selector**: Interactive theme selection with preview
- **Accessibility**: High contrast, reduced motion, and font size options
- **Custom Themes**: Support for custom theme definitions

### ⚡ Performance Optimization
- **Performance Monitoring**: Real-time performance metrics and alerts
- **Lazy Loading**: On-demand loading of resources and features
- **Resource Optimization**: Image, font, CSS, JS, and network optimizations
- **Caching**: Intelligent caching with configurable strategies

### 🔒 Security Features
- **Input Validation**: Comprehensive input validation with custom rules
- **Threat Detection**: XSS, injection, malware, and phishing detection
- **Access Control**: Domain and resource-based access control
- **Audit Logging**: Detailed security event logging and reporting

## Installation

```bash
npm install @aimos/advanced-monaco-editor
```

## Quick Start

```tsx
import React from 'react';
import { AdvancedMonacoEditor } from '@aimos/advanced-monaco-editor';

function App() {
  const [value, setValue] = React.useState('console.log("Hello, World!");');

  return (
    <AdvancedMonacoEditor
      value={value}
      language="javascript"
      onChange={setValue}
      enableDropdowns={true}
      enableContextMenus={true}
      enableTooltips={true}
      showThemeSelector={true}
    />
  );
}
```

## Configuration

### Basic Configuration

```tsx
<AdvancedMonacoEditor
  value={code}
  language="typescript"
  onChange={handleChange}
  onMount={handleMount}
  enableDropdowns={true}
  enableContextMenus={true}
  enableTooltips={true}
  showThemeSelector={true}
  onThemeChange={handleThemeChange}
/>
```

### Advanced Configuration

```tsx
<AdvancedMonacoEditor
  value={code}
  language="typescript"
  onChange={handleChange}
  onMount={handleMount}
  config={{
    dropdowns: {
      enabled: true,
      maxItems: 10,
      showDescriptions: true,
      showExamples: true,
      showRelatedSymbols: true
    },
    contextMenus: {
      enabled: true,
      maxItems: 15,
      groupActions: true,
      showCategories: true,
      filterActions: true
    },
    tooltips: {
      enabled: true,
      showMetadata: true,
      showExamples: true,
      showRelatedSymbols: true,
      showNaturalLanguage: true
    },
    intelligence: {
      enabled: true,
      realTimeAnalysis: true,
      cacheEnabled: true,
      cacheSize: 1000,
      cacheTimeout: 300000
    },
    aimos: {
      enabled: true,
      services: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'iis'],
      retryAttempts: 3,
      retryDelay: 1000
    },
    performance: {
      enableMetrics: true,
      enableProfiling: false,
      enableLazyLoading: true,
      maxMemoryUsage: 100 * 1024 * 1024,
      maxAnalysisTime: 100
    },
    security: {
      enableValidation: true,
      enableAccessControl: true,
      enableAuditLogging: false,
      enableEncryption: false,
      enableSandboxing: true
    }
  }}
/>
```

## API Reference

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `string` | `''` | The editor value |
| `language` | `string` | `'javascript'` | The editor language |
| `onChange` | `(value: string) => void` | - | Change handler |
| `onMount` | `(editor: monaco.editor.IStandaloneCodeEditor) => void` | - | Mount handler |
| `enableDropdowns` | `boolean` | `true` | Enable smart dropdowns |
| `enableContextMenus` | `boolean` | `true` | Enable context menus |
| `enableTooltips` | `boolean` | `true` | Enable enhanced tooltips |
| `showThemeSelector` | `boolean` | `false` | Show theme selector |
| `onThemeChange` | `(theme: string) => void` | - | Theme change handler |
| `config` | `AdvancedMonacoEditorConfig` | `{}` | Advanced configuration |

### Configuration Options

#### Dropdowns
- `enabled`: Enable/disable dropdowns
- `maxItems`: Maximum items to show
- `showDescriptions`: Show natural language descriptions
- `showExamples`: Show code examples
- `showRelatedSymbols`: Show related symbols

#### Context Menus
- `enabled`: Enable/disable context menus
- `maxItems`: Maximum items to show
- `groupActions`: Group actions by category
- `showCategories`: Show category headers
- `filterActions`: Filter actions based on context

#### Tooltips
- `enabled`: Enable/disable tooltips
- `showMetadata`: Show symbol metadata
- `showExamples`: Show code examples
- `showRelatedSymbols`: Show related symbols
- `showNaturalLanguage`: Show natural language descriptions

#### Intelligence
- `enabled`: Enable/disable AI intelligence
- `realTimeAnalysis`: Enable real-time analysis
- `cacheEnabled`: Enable caching
- `cacheSize`: Cache size limit
- `cacheTimeout`: Cache timeout

#### AIM-OS
- `enabled`: Enable/disable AIM-OS integration
- `services`: Array of AIM-OS services to use
- `retryAttempts`: Number of retry attempts
- `retryDelay`: Delay between retries

#### Performance
- `enableMetrics`: Enable performance metrics
- `enableProfiling`: Enable performance profiling
- `enableLazyLoading`: Enable lazy loading
- `maxMemoryUsage`: Maximum memory usage
- `maxAnalysisTime`: Maximum analysis time

#### Security
- `enableValidation`: Enable input validation
- `enableAccessControl`: Enable access control
- `enableAuditLogging`: Enable audit logging
- `enableEncryption`: Enable data encryption
- `enableSandboxing`: Enable sandboxing

## Examples

### Basic Usage

```tsx
import React from 'react';
import { AdvancedMonacoEditor } from '@aimos/advanced-monaco-editor';

function BasicExample() {
  const [code, setCode] = React.useState('console.log("Hello, World!");');

  return (
    <div style={{ height: '400px' }}>
      <AdvancedMonacoEditor
        value={code}
        language="javascript"
        onChange={setCode}
      />
    </div>
  );
}
```

### With Theme Selector

```tsx
import React from 'react';
import { AdvancedMonacoEditor } from '@aimos/advanced-monaco-editor';

function ThemedExample() {
  const [code, setCode] = React.useState('console.log("Hello, World!");');
  const [theme, setTheme] = React.useState('default-dark');

  return (
    <div style={{ height: '400px' }}>
      <AdvancedMonacoEditor
        value={code}
        language="javascript"
        onChange={setCode}
        showThemeSelector={true}
        onThemeChange={setTheme}
      />
    </div>
  );
}
```

### With Full Configuration

```tsx
import React from 'react';
import { AdvancedMonacoEditor } from '@aimos/advanced-monaco-editor';

function FullExample() {
  const [code, setCode] = React.useState('console.log("Hello, World!");');
  const [theme, setTheme] = React.useState('default-dark');

  const config = {
    dropdowns: {
      enabled: true,
      maxItems: 10,
      showDescriptions: true,
      showExamples: true,
      showRelatedSymbols: true
    },
    contextMenus: {
      enabled: true,
      maxItems: 15,
      groupActions: true,
      showCategories: true,
      filterActions: true
    },
    tooltips: {
      enabled: true,
      showMetadata: true,
      showExamples: true,
      showRelatedSymbols: true,
      showNaturalLanguage: true
    },
    intelligence: {
      enabled: true,
      realTimeAnalysis: true,
      cacheEnabled: true,
      cacheSize: 1000,
      cacheTimeout: 300000
    },
    aimos: {
      enabled: true,
      services: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'iis'],
      retryAttempts: 3,
      retryDelay: 1000
    },
    performance: {
      enableMetrics: true,
      enableProfiling: false,
      enableLazyLoading: true,
      maxMemoryUsage: 100 * 1024 * 1024,
      maxAnalysisTime: 100
    },
    security: {
      enableValidation: true,
      enableAccessControl: true,
      enableAuditLogging: false,
      enableEncryption: false,
      enableSandboxing: true
    }
  };

  return (
    <div style={{ height: '400px' }}>
      <AdvancedMonacoEditor
        value={code}
        language="javascript"
        onChange={setCode}
        showThemeSelector={true}
        onThemeChange={setTheme}
        config={config}
      />
    </div>
  );
}
```

## Development

### Prerequisites
- Node.js 18+
- npm 9+

### Setup
```bash
npm install
npm run build
npm test
```

### Scripts
- `npm run build`: Build the package
- `npm test`: Run tests
- `npm run lint`: Run linter
- `npm run type-check`: Run type checking

## License

MIT License - see LICENSE file for details.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## Support

For support, please open an issue on GitHub or contact the development team.