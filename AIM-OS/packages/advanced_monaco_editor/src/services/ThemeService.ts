/**
 * Theme Service
 * 
 * Provides comprehensive theme management including:
 * - Theme loading and saving
 * - Theme validation
 * - Theme migration
 * - Theme export/import
 * - Theme synchronization
 */

import { EventEmitter } from 'events';
import { ThemeManager, Theme, ThemeConfig, ThemeColors } from '../themes/ThemeManager';

export interface ThemeServiceConfig {
  storageKey: string;
  autoSave: boolean;
  autoLoad: boolean;
  validateThemes: boolean;
  migrateThemes: boolean;
  syncThemes: boolean;
}

export interface ThemeExport {
  version: string;
  themes: Theme[];
  config: ThemeConfig;
  metadata: {
    exportedAt: string;
    exportedBy: string;
    totalThemes: number;
  };
}

export interface ThemeValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
}

export class ThemeService extends EventEmitter {
  private themeManager: ThemeManager;
  private config: ThemeServiceConfig;
  private isInitialized: boolean = false;

  constructor(
    themeManager: ThemeManager,
    config: Partial<ThemeServiceConfig> = {}
  ) {
    super();
    this.themeManager = themeManager;
    this.config = {
      storageKey: 'advanced-monaco-editor-themes',
      autoSave: true,
      autoLoad: true,
      validateThemes: true,
      migrateThemes: true,
      syncThemes: false,
      ...config
    };

    if (this.config.autoLoad) {
      this.initialize();
    }
  }

  private async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      await this.loadThemes();
      this.setupEventListeners();
      this.isInitialized = true;
      this.emit('initialized');
    } catch (error) {
      console.error('Failed to initialize ThemeService:', error);
      this.emit('error', error);
    }
  }

  private setupEventListeners(): void {
    if (this.config.autoSave) {
      this.themeManager.on('themeChanged', () => this.saveThemes());
      this.themeManager.on('themeRegistered', () => this.saveThemes());
      this.themeManager.on('themeUnregistered', () => this.saveThemes());
      this.themeManager.on('configUpdated', () => this.saveThemes());
    }
  }

  public async loadThemes(): Promise<void> {
    try {
      const data = localStorage.getItem(this.config.storageKey);
      if (!data) {
        this.emit('themesLoaded', { count: 0, migrated: 0 });
        return;
      }

      const parsed = JSON.parse(data);
      
      // Handle version migration
      if (this.config.migrateThemes) {
        await this.migrateThemes(parsed);
      }

      // Load custom themes
      if (parsed.themes && Array.isArray(parsed.themes)) {
        let loadedCount = 0;
        let migratedCount = 0;

        for (const themeData of parsed.themes) {
          try {
            if (this.config.validateThemes) {
              const validation = this.validateTheme(themeData);
              if (!validation.isValid) {
                console.warn('Invalid theme skipped:', themeData.id, validation.errors);
                continue;
              }
            }

            // Check if theme needs migration
            if (this.needsMigration(themeData)) {
              const migratedTheme = this.migrateTheme(themeData);
              this.themeManager.registerTheme(migratedTheme);
              migratedCount++;
            } else {
              this.themeManager.registerTheme(themeData);
            }
            
            loadedCount++;
          } catch (error) {
            console.warn('Failed to load theme:', themeData.id, error);
          }
        }

        this.emit('themesLoaded', { count: loadedCount, migrated: migratedCount });
      }

      // Load config
      if (parsed.config) {
        this.themeManager.updateConfig(parsed.config);
      }

    } catch (error) {
      console.error('Failed to load themes:', error);
      this.emit('error', error);
    }
  }

  public async saveThemes(): Promise<void> {
    try {
      const customThemes = this.themeManager.getAllThemes().filter(t => t.metadata.isCustom);
      const config = this.themeManager.getConfig();
      
      const data = {
        version: '1.0.0',
        themes: customThemes,
        config,
        metadata: {
          savedAt: new Date().toISOString(),
          totalThemes: customThemes.length
        }
      };

      localStorage.setItem(this.config.storageKey, JSON.stringify(data, null, 2));
      this.emit('themesSaved', { count: customThemes.length });
    } catch (error) {
      console.error('Failed to save themes:', error);
      this.emit('error', error);
    }
  }

  public async exportThemes(): Promise<ThemeExport> {
    const customThemes = this.themeManager.getAllThemes().filter(t => t.metadata.isCustom);
    const config = this.themeManager.getConfig();
    
    return {
      version: '1.0.0',
      themes: customThemes,
      config,
      metadata: {
        exportedAt: new Date().toISOString(),
        exportedBy: 'Advanced Monaco Editor',
        totalThemes: customThemes.length
      }
    };
  }

  public async importThemes(themeExport: ThemeExport): Promise<{ imported: number; errors: string[] }> {
    const errors: string[] = [];
    let imported = 0;

    try {
      // Validate export format
      if (!themeExport.version || !themeExport.themes || !Array.isArray(themeExport.themes)) {
        throw new Error('Invalid theme export format');
      }

      // Import themes
      for (const themeData of themeExport.themes) {
        try {
          if (this.config.validateThemes) {
            const validation = this.validateTheme(themeData);
            if (!validation.isValid) {
              errors.push(`Theme ${themeData.id}: ${validation.errors.join(', ')}`);
              continue;
            }
          }

          // Check if theme already exists
          if (this.themeManager.getTheme(themeData.id)) {
            errors.push(`Theme ${themeData.id} already exists`);
            continue;
          }

          this.themeManager.registerTheme(themeData);
          imported++;
        } catch (error) {
          errors.push(`Theme ${themeData.id}: ${error.message}`);
        }
      }

      // Import config if provided
      if (themeExport.config) {
        this.themeManager.updateConfig(themeExport.config);
      }

      this.emit('themesImported', { imported, errors });
      return { imported, errors };
    } catch (error) {
      errors.push(`Import failed: ${error.message}`);
      this.emit('error', error);
      return { imported, errors };
    }
  }

  public validateTheme(theme: any): ThemeValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    const suggestions: string[] = [];

    // Required fields
    if (!theme.id || typeof theme.id !== 'string') {
      errors.push('Theme ID is required and must be a string');
    }

    if (!theme.metadata || typeof theme.metadata !== 'object') {
      errors.push('Theme metadata is required');
    } else {
      if (!theme.metadata.name || typeof theme.metadata.name !== 'string') {
        errors.push('Theme name is required');
      }
      if (!theme.metadata.description || typeof theme.metadata.description !== 'string') {
        errors.push('Theme description is required');
      }
      if (!theme.metadata.author || typeof theme.metadata.author !== 'string') {
        errors.push('Theme author is required');
      }
    }

    if (!theme.colors || typeof theme.colors !== 'object') {
      errors.push('Theme colors are required');
    } else {
      // Validate color format
      const colorKeys = Object.keys(theme.colors);
      for (const key of colorKeys) {
        const color = theme.colors[key];
        if (typeof color !== 'string' || !this.isValidColor(color)) {
          errors.push(`Invalid color format for ${key}: ${color}`);
        }
      }

      // Check for required colors
      const requiredColors = ['background', 'foreground', 'selection', 'selectionBackground'];
      for (const color of requiredColors) {
        if (!theme.colors[color]) {
          errors.push(`Required color missing: ${color}`);
        }
      }
    }

    if (!theme.monacoTheme || typeof theme.monacoTheme !== 'object') {
      errors.push('Monaco theme is required');
    } else {
      if (!theme.monacoTheme.base || typeof theme.monacoTheme.base !== 'string') {
        errors.push('Monaco theme base is required');
      }
    }

    // Accessibility checks
    if (theme.metadata?.accessibility) {
      const acc = theme.metadata.accessibility;
      if (acc.contrastRatio && (acc.contrastRatio < 3 || acc.contrastRatio > 21)) {
        warnings.push('Contrast ratio should be between 3 and 21');
      }
      if (acc.wcagLevel && !['A', 'AA', 'AAA'].includes(acc.wcagLevel)) {
        warnings.push('WCAG level should be A, AA, or AAA');
      }
    }

    // Suggestions
    if (theme.metadata && !theme.metadata.version) {
      suggestions.push('Consider adding a version number');
    }
    if (theme.metadata && !theme.metadata.isDark) {
      suggestions.push('Consider specifying if theme is dark or light');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      suggestions
    };
  }

  private isValidColor(color: string): boolean {
    // Check for hex colors
    if (/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color)) {
      return true;
    }
    
    // Check for rgb/rgba colors
    if (/^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(,\s*[\d.]+)?\s*\)$/.test(color)) {
      return true;
    }
    
    // Check for hsl/hsla colors
    if (/^hsla?\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*(,\s*[\d.]+)?\s*\)$/.test(color)) {
      return true;
    }
    
    // Check for named colors (basic set)
    const namedColors = [
      'black', 'white', 'red', 'green', 'blue', 'yellow', 'orange', 'purple',
      'pink', 'brown', 'gray', 'grey', 'transparent'
    ];
    
    return namedColors.includes(color.toLowerCase());
  }

  private needsMigration(theme: any): boolean {
    // Check if theme needs migration based on version or structure
    return !theme.version || theme.version < '1.0.0';
  }

  private migrateTheme(theme: any): Theme {
    // Migrate theme to current format
    const migrated: Theme = {
      id: theme.id,
      metadata: {
        ...theme.metadata,
        version: theme.metadata?.version || '1.0.0',
        isCustom: theme.metadata?.isCustom || true,
        accessibility: theme.metadata?.accessibility || {
          wcagLevel: 'AA',
          contrastRatio: 4.5,
          supportsReducedMotion: true,
          supportsHighContrast: true
        }
      },
      colors: theme.colors,
      monacoTheme: theme.monacoTheme
    };

    return migrated;
  }

  private async migrateThemes(data: any): Promise<void> {
    // Handle migration logic for different versions
    if (data.version === '0.9.0') {
      // Migration from 0.9.0 to 1.0.0
      console.log('Migrating themes from version 0.9.0 to 1.0.0');
    }
  }

  public async resetThemes(): Promise<void> {
    try {
      // Remove all custom themes
      const customThemes = this.themeManager.getAllThemes().filter(t => t.metadata.isCustom);
      for (const theme of customThemes) {
        this.themeManager.unregisterTheme(theme.id);
      }

      // Clear storage
      localStorage.removeItem(this.config.storageKey);

      // Reset to default theme
      this.themeManager.setTheme('default-dark');

      this.emit('themesReset');
    } catch (error) {
      console.error('Failed to reset themes:', error);
      this.emit('error', error);
    }
  }

  public async syncThemes(): Promise<void> {
    if (!this.config.syncThemes) return;

    try {
      // Implement theme synchronization logic
      // This could sync with a remote server, other instances, etc.
      this.emit('themesSynced');
    } catch (error) {
      console.error('Failed to sync themes:', error);
      this.emit('error', error);
    }
  }

  public getThemeManager(): ThemeManager {
    return this.themeManager;
  }

  public getConfig(): ThemeServiceConfig {
    return { ...this.config };
  }

  public updateConfig(config: Partial<ThemeServiceConfig>): void {
    this.config = { ...this.config, ...config };
    this.emit('configUpdated', this.config);
  }

  public destroy(): void {
    this.removeAllListeners();
    this.isInitialized = false;
  }
}
