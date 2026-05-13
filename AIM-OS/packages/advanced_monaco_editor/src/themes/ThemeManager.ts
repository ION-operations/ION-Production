/**
 * Theme Manager for Advanced Monaco Editor
 * 
 * Provides comprehensive theme management including:
 * - Built-in themes (Light, Dark, High Contrast, etc.)
 * - Custom theme creation and management
 * - Dynamic theme switching
 * - Theme persistence
 * - Accessibility support
 * - Monaco Editor theme integration
 */

import { editor } from 'monaco-editor';
import { EventEmitter } from 'events';

export interface ThemeColors {
  // Core editor colors
  background: string;
  foreground: string;
  selection: string;
  selectionBackground: string;
  cursor: string;
  cursorForeground: string;
  
  // Syntax highlighting
  keyword: string;
  string: string;
  comment: string;
  number: string;
  function: string;
  variable: string;
  type: string;
  operator: string;
  punctuation: string;
  
  // UI elements
  dropdownBackground: string;
  dropdownForeground: string;
  dropdownBorder: string;
  dropdownHover: string;
  dropdownSelected: string;
  
  // Context menu
  contextMenuBackground: string;
  contextMenuForeground: string;
  contextMenuBorder: string;
  contextMenuHover: string;
  contextMenuSeparator: string;
  contextMenuGroupHeader: string;
  
  // Tooltips
  tooltipBackground: string;
  tooltipForeground: string;
  tooltipBorder: string;
  tooltipShadow: string;
  
  // Inline folds
  foldBackground: string;
  foldForeground: string;
  foldBorder: string;
  foldHover: string;
  foldExpanded: string;
  foldCollapsed: string;
  
  // Gutter icons
  gutterIcon: string;
  gutterIconHover: string;
  gutterIconActive: string;
  
  // Status indicators
  statusSuccess: string;
  statusWarning: string;
  statusError: string;
  statusInfo: string;
  
  // AIM-OS specific
  aimosPrimary: string;
  aimosSecondary: string;
  aimosAccent: string;
  aimosBackground: string;
  aimosForeground: string;
  
  // Accessibility
  focusRing: string;
  highContrast: string;
  reducedMotion: string;
}

export interface ThemeMetadata {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  baseTheme?: string;
  isDark: boolean;
  isHighContrast: boolean;
  isCustom: boolean;
  accessibility: {
    wcagLevel: 'A' | 'AA' | 'AAA';
    contrastRatio: number;
    supportsReducedMotion: boolean;
    supportsHighContrast: boolean;
  };
}

export interface Theme {
  id: string;
  metadata: ThemeMetadata;
  colors: ThemeColors;
  monacoTheme: editor.IStandaloneThemeData;
}

export interface ThemeConfig {
  defaultTheme: string;
  autoDetect: boolean;
  persistTheme: boolean;
  accessibility: {
    highContrast: boolean;
    reducedMotion: boolean;
    fontSize: 'small' | 'medium' | 'large';
  };
  customThemes: Theme[];
}

export class ThemeManager extends EventEmitter {
  private themes: Map<string, Theme> = new Map();
  private currentTheme: string = 'default-dark';
  private config: ThemeConfig;
  private monacoEditor: editor.IStandaloneCodeEditor | null = null;

  constructor(config: Partial<ThemeConfig> = {}) {
    super();
    this.config = {
      defaultTheme: 'default-dark',
      autoDetect: true,
      persistTheme: true,
      accessibility: {
        highContrast: false,
        reducedMotion: false,
        fontSize: 'medium'
      },
      customThemes: []
    };
    
    this.mergeConfig(config);
    this.initializeBuiltInThemes();
    this.loadCustomThemes();
    this.loadPersistedTheme();
  }

  private mergeConfig(config: Partial<ThemeConfig>): void {
    this.config = { ...this.config, ...config };
    if (config.accessibility) {
      this.config.accessibility = { ...this.config.accessibility, ...config.accessibility };
    }
  }

  private initializeBuiltInThemes(): void {
    // Default Dark Theme
    this.registerTheme({
      id: 'default-dark',
      metadata: {
        id: 'default-dark',
        name: 'Default Dark',
        description: 'The default dark theme for Advanced Monaco Editor',
        author: 'AIM-OS',
        version: '1.0.0',
        isDark: true,
        isHighContrast: false,
        isCustom: false,
        accessibility: {
          wcagLevel: 'AA',
          contrastRatio: 4.5,
          supportsReducedMotion: true,
          supportsHighContrast: true
        }
      },
      colors: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        selection: '#264f78',
        selectionBackground: '#264f78',
        cursor: '#aeafad',
        cursorForeground: '#000000',
        keyword: '#569cd6',
        string: '#ce9178',
        comment: '#6a9955',
        number: '#b5cea8',
        function: '#dcdcaa',
        variable: '#9cdcfe',
        type: '#4ec9b0',
        operator: '#d4d4d4',
        punctuation: '#d4d4d4',
        dropdownBackground: '#252526',
        dropdownForeground: '#cccccc',
        dropdownBorder: '#454545',
        dropdownHover: '#2a2d2e',
        dropdownSelected: '#094771',
        contextMenuBackground: '#252526',
        contextMenuForeground: '#cccccc',
        contextMenuBorder: '#454545',
        contextMenuHover: '#2a2d2e',
        contextMenuSeparator: '#454545',
        contextMenuGroupHeader: '#569cd6',
        tooltipBackground: '#252526',
        tooltipForeground: '#cccccc',
        tooltipBorder: '#454545',
        tooltipShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        foldBackground: '#2d2d30',
        foldForeground: '#cccccc',
        foldBorder: '#3e3e42',
        foldHover: '#37373a',
        foldExpanded: '#4ec9b0',
        foldCollapsed: '#569cd6',
        gutterIcon: '#858585',
        gutterIconHover: '#cccccc',
        gutterIconActive: '#4ec9b0',
        statusSuccess: '#4ec9b0',
        statusWarning: '#dcdcaa',
        statusError: '#f44747',
        statusInfo: '#569cd6',
        aimosPrimary: '#4ec9b0',
        aimosSecondary: '#569cd6',
        aimosAccent: '#dcdcaa',
        aimosBackground: '#1e1e1e',
        aimosForeground: '#d4d4d4',
        focusRing: '#007acc',
        highContrast: '#ffffff',
        reducedMotion: '#d4d4d4'
      },
      monacoTheme: {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'keyword', foreground: '569cd6', fontStyle: 'bold' },
          { token: 'string', foreground: 'ce9178' },
          { token: 'comment', foreground: '6a9955', fontStyle: 'italic' },
          { token: 'number', foreground: 'b5cea8' },
          { token: 'function', foreground: 'dcdcaa' },
          { token: 'variable', foreground: '9cdcfe' },
          { token: 'type', foreground: '4ec9b0' },
          { token: 'operator', foreground: 'd4d4d4' },
          { token: 'punctuation', foreground: 'd4d4d4' }
        ],
        colors: {
          'editor.background': '#1e1e1e',
          'editor.foreground': '#d4d4d4',
          'editor.selectionBackground': '#264f78',
          'editorCursor.foreground': '#aeafad',
          'editor.lineHighlightBackground': '#2d2d30',
          'editorLineNumber.foreground': '#858585',
          'editorLineNumber.activeForeground': '#d4d4d4'
        }
      }
    });

    // Default Light Theme
    this.registerTheme({
      id: 'default-light',
      metadata: {
        id: 'default-light',
        name: 'Default Light',
        description: 'The default light theme for Advanced Monaco Editor',
        author: 'AIM-OS',
        version: '1.0.0',
        isDark: false,
        isHighContrast: false,
        isCustom: false,
        accessibility: {
          wcagLevel: 'AA',
          contrastRatio: 4.5,
          supportsReducedMotion: true,
          supportsHighContrast: true
        }
      },
      colors: {
        background: '#ffffff',
        foreground: '#333333',
        selection: '#add6ff',
        selectionBackground: '#add6ff',
        cursor: '#000000',
        cursorForeground: '#ffffff',
        keyword: '#0000ff',
        string: '#a31515',
        comment: '#008000',
        number: '#098658',
        function: '#795e26',
        variable: '#001080',
        type: '#267f99',
        operator: '#000000',
        punctuation: '#000000',
        dropdownBackground: '#ffffff',
        dropdownForeground: '#333333',
        dropdownBorder: '#cccccc',
        dropdownHover: '#f0f0f0',
        dropdownSelected: '#0078d4',
        contextMenuBackground: '#ffffff',
        contextMenuForeground: '#333333',
        contextMenuBorder: '#cccccc',
        contextMenuHover: '#f0f0f0',
        contextMenuSeparator: '#cccccc',
        contextMenuGroupHeader: '#0000ff',
        tooltipBackground: '#ffffff',
        tooltipForeground: '#333333',
        tooltipBorder: '#cccccc',
        tooltipShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        foldBackground: '#f8f8f8',
        foldForeground: '#333333',
        foldBorder: '#e1e1e1',
        foldHover: '#f0f0f0',
        foldExpanded: '#267f99',
        foldCollapsed: '#0000ff',
        gutterIcon: '#666666',
        gutterIconHover: '#333333',
        gutterIconActive: '#267f99',
        statusSuccess: '#267f99',
        statusWarning: '#795e26',
        statusError: '#a31515',
        statusInfo: '#0000ff',
        aimosPrimary: '#267f99',
        aimosSecondary: '#0000ff',
        aimosAccent: '#795e26',
        aimosBackground: '#ffffff',
        aimosForeground: '#333333',
        focusRing: '#0078d4',
        highContrast: '#000000',
        reducedMotion: '#333333'
      },
      monacoTheme: {
        base: 'vs',
        inherit: true,
        rules: [
          { token: 'keyword', foreground: '0000ff', fontStyle: 'bold' },
          { token: 'string', foreground: 'a31515' },
          { token: 'comment', foreground: '008000', fontStyle: 'italic' },
          { token: 'number', foreground: '098658' },
          { token: 'function', foreground: '795e26' },
          { token: 'variable', foreground: '001080' },
          { token: 'type', foreground: '267f99' },
          { token: 'operator', foreground: '000000' },
          { token: 'punctuation', foreground: '000000' }
        ],
        colors: {
          'editor.background': '#ffffff',
          'editor.foreground': '#333333',
          'editor.selectionBackground': '#add6ff',
          'editorCursor.foreground': '#000000',
          'editor.lineHighlightBackground': '#f8f8f8',
          'editorLineNumber.foreground': '#666666',
          'editorLineNumber.activeForeground': '#333333'
        }
      }
    });

    // High Contrast Dark Theme
    this.registerTheme({
      id: 'high-contrast-dark',
      metadata: {
        id: 'high-contrast-dark',
        name: 'High Contrast Dark',
        description: 'High contrast dark theme for accessibility',
        author: 'AIM-OS',
        version: '1.0.0',
        isDark: true,
        isHighContrast: true,
        isCustom: false,
        accessibility: {
          wcagLevel: 'AAA',
          contrastRatio: 7.0,
          supportsReducedMotion: true,
          supportsHighContrast: true
        }
      },
      colors: {
        background: '#000000',
        foreground: '#ffffff',
        selection: '#ffff00',
        selectionBackground: '#ffff00',
        cursor: '#ffffff',
        cursorForeground: '#000000',
        keyword: '#00ffff',
        string: '#ffff00',
        comment: '#00ff00',
        number: '#ff00ff',
        function: '#ffff00',
        variable: '#00ffff',
        type: '#00ff00',
        operator: '#ffffff',
        punctuation: '#ffffff',
        dropdownBackground: '#000000',
        dropdownForeground: '#ffffff',
        dropdownBorder: '#ffffff',
        dropdownHover: '#333333',
        dropdownSelected: '#ffff00',
        contextMenuBackground: '#000000',
        contextMenuForeground: '#ffffff',
        contextMenuBorder: '#ffffff',
        contextMenuHover: '#333333',
        contextMenuSeparator: '#ffffff',
        contextMenuGroupHeader: '#00ffff',
        tooltipBackground: '#000000',
        tooltipForeground: '#ffffff',
        tooltipBorder: '#ffffff',
        tooltipShadow: '0 2px 8px rgba(255, 255, 255, 0.3)',
        foldBackground: '#1a1a1a',
        foldForeground: '#ffffff',
        foldBorder: '#ffffff',
        foldHover: '#333333',
        foldExpanded: '#00ff00',
        foldCollapsed: '#00ffff',
        gutterIcon: '#ffffff',
        gutterIconHover: '#ffff00',
        gutterIconActive: '#00ff00',
        statusSuccess: '#00ff00',
        statusWarning: '#ffff00',
        statusError: '#ff0000',
        statusInfo: '#00ffff',
        aimosPrimary: '#00ff00',
        aimosSecondary: '#00ffff',
        aimosAccent: '#ffff00',
        aimosBackground: '#000000',
        aimosForeground: '#ffffff',
        focusRing: '#ffff00',
        highContrast: '#ffffff',
        reducedMotion: '#ffffff'
      },
      monacoTheme: {
        base: 'hc-black',
        inherit: true,
        rules: [
          { token: 'keyword', foreground: '00ffff', fontStyle: 'bold' },
          { token: 'string', foreground: 'ffff00' },
          { token: 'comment', foreground: '00ff00', fontStyle: 'italic' },
          { token: 'number', foreground: 'ff00ff' },
          { token: 'function', foreground: 'ffff00' },
          { token: 'variable', foreground: '00ffff' },
          { token: 'type', foreground: '00ff00' },
          { token: 'operator', foreground: 'ffffff' },
          { token: 'punctuation', foreground: 'ffffff' }
        ],
        colors: {
          'editor.background': '#000000',
          'editor.foreground': '#ffffff',
          'editor.selectionBackground': '#ffff00',
          'editorCursor.foreground': '#ffffff',
          'editor.lineHighlightBackground': '#1a1a1a',
          'editorLineNumber.foreground': '#ffffff',
          'editorLineNumber.activeForeground': '#ffffff'
        }
      }
    });

    // AIM-OS Theme
    this.registerTheme({
      id: 'aimos-theme',
      metadata: {
        id: 'aimos-theme',
        name: 'AIM-OS Theme',
        description: 'Custom theme designed for AIM-OS development',
        author: 'AIM-OS',
        version: '1.0.0',
        isDark: true,
        isHighContrast: false,
        isCustom: false,
        accessibility: {
          wcagLevel: 'AA',
          contrastRatio: 4.5,
          supportsReducedMotion: true,
          supportsHighContrast: true
        }
      },
      colors: {
        background: '#0d1117',
        foreground: '#e6edf3',
        selection: '#264f78',
        selectionBackground: '#264f78',
        cursor: '#f0f6fc',
        cursorForeground: '#0d1117',
        keyword: '#ff7b72',
        string: '#a5d6ff',
        comment: '#7ee787',
        number: '#79c0ff',
        function: '#d2a8ff',
        variable: '#ffa657',
        type: '#7ee787',
        operator: '#f0f6fc',
        punctuation: '#f0f6fc',
        dropdownBackground: '#161b22',
        dropdownForeground: '#e6edf3',
        dropdownBorder: '#30363d',
        dropdownHover: '#21262d',
        dropdownSelected: '#1f6feb',
        contextMenuBackground: '#161b22',
        contextMenuForeground: '#e6edf3',
        contextMenuBorder: '#30363d',
        contextMenuHover: '#21262d',
        contextMenuSeparator: '#30363d',
        contextMenuGroupHeader: '#ff7b72',
        tooltipBackground: '#161b22',
        tooltipForeground: '#e6edf3',
        tooltipBorder: '#30363d',
        tooltipShadow: '0 2px 8px rgba(0, 0, 0, 0.4)',
        foldBackground: '#21262d',
        foldForeground: '#e6edf3',
        foldBorder: '#30363d',
        foldHover: '#262c36',
        foldExpanded: '#7ee787',
        foldCollapsed: '#ff7b72',
        gutterIcon: '#7d8590',
        gutterIconHover: '#e6edf3',
        gutterIconActive: '#7ee787',
        statusSuccess: '#7ee787',
        statusWarning: '#d2a8ff',
        statusError: '#ff7b72',
        statusInfo: '#79c0ff',
        aimosPrimary: '#7ee787',
        aimosSecondary: '#79c0ff',
        aimosAccent: '#d2a8ff',
        aimosBackground: '#0d1117',
        aimosForeground: '#e6edf3',
        focusRing: '#1f6feb',
        highContrast: '#ffffff',
        reducedMotion: '#e6edf3'
      },
      monacoTheme: {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'keyword', foreground: 'ff7b72', fontStyle: 'bold' },
          { token: 'string', foreground: 'a5d6ff' },
          { token: 'comment', foreground: '7ee787', fontStyle: 'italic' },
          { token: 'number', foreground: '79c0ff' },
          { token: 'function', foreground: 'd2a8ff' },
          { token: 'variable', foreground: 'ffa657' },
          { token: 'type', foreground: '7ee787' },
          { token: 'operator', foreground: 'f0f6fc' },
          { token: 'punctuation', foreground: 'f0f6fc' }
        ],
        colors: {
          'editor.background': '#0d1117',
          'editor.foreground': '#e6edf3',
          'editor.selectionBackground': '#264f78',
          'editorCursor.foreground': '#f0f6fc',
          'editor.lineHighlightBackground': '#21262d',
          'editorLineNumber.foreground': '#7d8590',
          'editorLineNumber.activeForeground': '#e6edf3'
        }
      }
    });
  }

  private loadCustomThemes(): void {
    this.config.customThemes.forEach(theme => {
      this.registerTheme(theme);
    });
  }

  private loadPersistedTheme(): void {
    if (this.config.persistTheme) {
      try {
        const savedTheme = localStorage.getItem('advanced-monaco-editor-theme');
        if (savedTheme && this.themes.has(savedTheme)) {
          this.currentTheme = savedTheme;
        }
      } catch (error) {
        console.warn('Failed to load persisted theme:', error);
      }
    }
  }

  private saveTheme(): void {
    if (this.config.persistTheme) {
      try {
        localStorage.setItem('advanced-monaco-editor-theme', this.currentTheme);
      } catch (error) {
        console.warn('Failed to save theme:', error);
      }
    }
  }

  public registerTheme(theme: Theme): void {
    this.themes.set(theme.id, theme);
    this.emit('themeRegistered', theme);
  }

  public unregisterTheme(themeId: string): boolean {
    const theme = this.themes.get(themeId);
    if (theme && !theme.metadata.isCustom) {
      console.warn('Cannot unregister built-in theme:', themeId);
      return false;
    }
    
    const removed = this.themes.delete(themeId);
    if (removed) {
      this.emit('themeUnregistered', themeId);
    }
    return removed;
  }

  public getTheme(themeId: string): Theme | undefined {
    return this.themes.get(themeId);
  }

  public getAllThemes(): Theme[] {
    return Array.from(this.themes.values());
  }

  public getCurrentTheme(): Theme | undefined {
    return this.themes.get(this.currentTheme);
  }

  public setTheme(themeId: string): boolean {
    const theme = this.themes.get(themeId);
    if (!theme) {
      console.warn('Theme not found:', themeId);
      return false;
    }

    const previousTheme = this.currentTheme;
    this.currentTheme = themeId;
    
    this.applyTheme(theme);
    this.saveTheme();
    
    this.emit('themeChanged', { previous: previousTheme, current: themeId, theme });
    return true;
  }

  private applyTheme(theme: Theme): void {
    // Apply Monaco Editor theme
    if (this.monacoEditor) {
      editor.setTheme(theme.id);
    }

    // Apply CSS custom properties
    this.applyCSSVariables(theme.colors);
    
    // Apply accessibility settings
    this.applyAccessibilitySettings(theme);
  }

  private applyCSSVariables(colors: ThemeColors): void {
    const root = document.documentElement;
    
    Object.entries(colors).forEach(([key, value]) => {
      const cssVar = `--monaco-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
      root.style.setProperty(cssVar, value);
    });
  }

  private applyAccessibilitySettings(theme: Theme): void {
    const root = document.documentElement;
    
    // High contrast
    if (this.config.accessibility.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    
    // Reduced motion
    if (this.config.accessibility.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }
    
    // Font size
    root.classList.remove('font-small', 'font-medium', 'font-large');
    root.classList.add(`font-${this.config.accessibility.fontSize}`);
  }

  public setMonacoEditor(editor: editor.IStandaloneCodeEditor): void {
    this.monacoEditor = editor;
    
    // Register theme with Monaco
    const currentTheme = this.getCurrentTheme();
    if (currentTheme) {
      editor.defineTheme(currentTheme.id, currentTheme.monacoTheme);
      editor.setTheme(currentTheme.id);
    }
  }

  public createCustomTheme(
    id: string,
    name: string,
    description: string,
    author: string,
    baseTheme: string,
    colors: Partial<ThemeColors>
  ): Theme {
    const baseThemeData = this.themes.get(baseTheme);
    if (!baseThemeData) {
      throw new Error(`Base theme not found: ${baseTheme}`);
    }

    const mergedColors = { ...baseThemeData.colors, ...colors };
    
    const theme: Theme = {
      id,
      metadata: {
        id,
        name,
        description,
        author,
        version: '1.0.0',
        baseTheme,
        isDark: baseThemeData.metadata.isDark,
        isHighContrast: baseThemeData.metadata.isHighContrast,
        isCustom: true,
        accessibility: {
          wcagLevel: 'AA',
          contrastRatio: 4.5,
          supportsReducedMotion: true,
          supportsHighContrast: true
        }
      },
      colors: mergedColors,
      monacoTheme: {
        ...baseThemeData.monacoTheme,
        colors: {
          ...baseThemeData.monacoTheme.colors,
          'editor.background': mergedColors.background,
          'editor.foreground': mergedColors.foreground,
          'editor.selectionBackground': mergedColors.selectionBackground,
          'editorCursor.foreground': mergedColors.cursor
        }
      }
    };

    this.registerTheme(theme);
    return theme;
  }

  public updateConfig(config: Partial<ThemeConfig>): void {
    this.mergeConfig(config);
    this.emit('configUpdated', this.config);
  }

  public getConfig(): ThemeConfig {
    return { ...this.config };
  }

  public destroy(): void {
    this.removeAllListeners();
    this.themes.clear();
    this.monacoEditor = null;
  }
}
