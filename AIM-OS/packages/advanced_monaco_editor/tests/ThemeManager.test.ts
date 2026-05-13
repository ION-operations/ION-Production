/**
 * Theme Manager Tests
 * 
 * Comprehensive unit tests for the ThemeManager class
 */

import { ThemeManager, Theme, ThemeConfig } from '../src/themes/ThemeManager';

describe('ThemeManager', () => {
  let themeManager: ThemeManager;

  beforeEach(() => {
    themeManager = new ThemeManager();
  });

  afterEach(() => {
    themeManager.destroy();
  });

  describe('Initialization', () => {
    it('should initialize with default configuration', () => {
      expect(themeManager).toBeDefined();
      expect(themeManager.getConfig()).toEqual({
        defaultTheme: 'default-dark',
        autoDetect: true,
        persistTheme: true,
        accessibility: {
          highContrast: false,
          reducedMotion: false,
          fontSize: 'medium'
        },
        customThemes: []
      });
    });

    it('should initialize with custom configuration', () => {
      const customConfig: Partial<ThemeConfig> = {
        defaultTheme: 'custom-theme',
        autoDetect: false,
        persistTheme: false
      };

      const customThemeManager = new ThemeManager(customConfig);
      expect(customThemeManager.getConfig().defaultTheme).toBe('custom-theme');
      expect(customThemeManager.getConfig().autoDetect).toBe(false);
      expect(customThemeManager.getConfig().persistTheme).toBe(false);
      customThemeManager.destroy();
    });

    it('should register built-in themes', () => {
      const themes = themeManager.getAllThemes();
      expect(themes.length).toBeGreaterThan(0);
      
      const themeIds = themes.map(t => t.id);
      expect(themeIds).toContain('default-dark');
      expect(themeIds).toContain('default-light');
      expect(themeIds).toContain('high-contrast-dark');
      expect(themeIds).toContain('aimos-theme');
    });
  });

  describe('Theme Management', () => {
    it('should register a custom theme', () => {
      const customTheme: Theme = {
        id: 'test-theme',
        metadata: {
          id: 'test-theme',
          name: 'Test Theme',
          description: 'A test theme',
          author: 'Test Author',
          version: '1.0.0',
          isDark: true,
          isHighContrast: false,
          isCustom: true,
          accessibility: {
            wcagLevel: 'AA',
            contrastRatio: 4.5,
            supportsReducedMotion: true,
            supportsHighContrast: true
          }
        },
        colors: {
          background: '#000000',
          foreground: '#ffffff',
          selection: '#333333',
          selectionBackground: '#333333',
          cursor: '#ffffff',
          cursorForeground: '#000000',
          keyword: '#ff0000',
          string: '#00ff00',
          comment: '#0000ff',
          number: '#ffff00',
          function: '#ff00ff',
          variable: '#00ffff',
          type: '#ffffff',
          operator: '#ffffff',
          punctuation: '#ffffff',
          dropdownBackground: '#111111',
          dropdownForeground: '#ffffff',
          dropdownBorder: '#333333',
          dropdownHover: '#222222',
          dropdownSelected: '#444444',
          contextMenuBackground: '#111111',
          contextMenuForeground: '#ffffff',
          contextMenuBorder: '#333333',
          contextMenuHover: '#222222',
          contextMenuSeparator: '#333333',
          contextMenuGroupHeader: '#ff0000',
          tooltipBackground: '#111111',
          tooltipForeground: '#ffffff',
          tooltipBorder: '#333333',
          tooltipShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
          foldBackground: '#111111',
          foldForeground: '#ffffff',
          foldBorder: '#333333',
          foldHover: '#222222',
          foldExpanded: '#00ff00',
          foldCollapsed: '#ff0000',
          gutterIcon: '#666666',
          gutterIconHover: '#ffffff',
          gutterIconActive: '#00ff00',
          statusSuccess: '#00ff00',
          statusWarning: '#ffff00',
          statusError: '#ff0000',
          statusInfo: '#0000ff',
          aimosPrimary: '#00ff00',
          aimosSecondary: '#0000ff',
          aimosAccent: '#ffff00',
          aimosBackground: '#000000',
          aimosForeground: '#ffffff',
          focusRing: '#007acc',
          highContrast: '#ffffff',
          reducedMotion: '#ffffff'
        },
        monacoTheme: {
          base: 'vs-dark',
          inherit: true,
          rules: [],
          colors: {
            'editor.background': '#000000',
            'editor.foreground': '#ffffff',
            'editor.selectionBackground': '#333333',
            'editorCursor.foreground': '#ffffff'
          }
        }
      };

      themeManager.registerTheme(customTheme);
      expect(themeManager.getTheme('test-theme')).toEqual(customTheme);
    });

    it('should unregister a custom theme', () => {
      const customTheme: Theme = {
        id: 'test-theme-2',
        metadata: {
          id: 'test-theme-2',
          name: 'Test Theme 2',
          description: 'Another test theme',
          author: 'Test Author',
          version: '1.0.0',
          isDark: true,
          isHighContrast: false,
          isCustom: true,
          accessibility: {
            wcagLevel: 'AA',
            contrastRatio: 4.5,
            supportsReducedMotion: true,
            supportsHighContrast: true
          }
        },
        colors: {} as any,
        monacoTheme: {} as any
      };

      themeManager.registerTheme(customTheme);
      expect(themeManager.getTheme('test-theme-2')).toBeDefined();

      const unregistered = themeManager.unregisterTheme('test-theme-2');
      expect(unregistered).toBe(true);
      expect(themeManager.getTheme('test-theme-2')).toBeUndefined();
    });

    it('should not unregister built-in themes', () => {
      const unregistered = themeManager.unregisterTheme('default-dark');
      expect(unregistered).toBe(false);
      expect(themeManager.getTheme('default-dark')).toBeDefined();
    });

    it('should set current theme', () => {
      const success = themeManager.setTheme('default-light');
      expect(success).toBe(true);
      expect(themeManager.getCurrentTheme()?.id).toBe('default-light');
    });

    it('should not set non-existent theme', () => {
      const success = themeManager.setTheme('non-existent-theme');
      expect(success).toBe(false);
    });
  });

  describe('Theme Creation', () => {
    it('should create custom theme from base theme', () => {
      const customTheme = themeManager.createCustomTheme(
        'my-custom-theme',
        'My Custom Theme',
        'A custom theme based on default dark',
        'Test Author',
        'default-dark',
        {
          background: '#1a1a1a',
          foreground: '#e0e0e0'
        }
      );

      expect(customTheme.id).toBe('my-custom-theme');
      expect(customTheme.metadata.name).toBe('My Custom Theme');
      expect(customTheme.metadata.author).toBe('Test Author');
      expect(customTheme.metadata.isCustom).toBe(true);
      expect(customTheme.colors.background).toBe('#1a1a1a');
      expect(customTheme.colors.foreground).toBe('#e0e0e0');
    });

    it('should throw error for non-existent base theme', () => {
      expect(() => {
        themeManager.createCustomTheme(
          'invalid-theme',
          'Invalid Theme',
          'A theme with invalid base',
          'Test Author',
          'non-existent-base',
          {}
        );
      }).toThrow('Base theme not found: non-existent-base');
    });
  });

  describe('Configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        defaultTheme: 'default-light',
        autoDetect: false
      };

      themeManager.updateConfig(newConfig);
      const config = themeManager.getConfig();
      expect(config.defaultTheme).toBe('default-light');
      expect(config.autoDetect).toBe(false);
    });

    it('should merge configuration properly', () => {
      const newConfig = {
        accessibility: {
          highContrast: true,
          fontSize: 'large' as const
        }
      };

      themeManager.updateConfig(newConfig);
      const config = themeManager.getConfig();
      expect(config.accessibility.highContrast).toBe(true);
      expect(config.accessibility.fontSize).toBe('large');
      expect(config.accessibility.reducedMotion).toBe(false); // Should preserve existing value
    });
  });

  describe('Monaco Editor Integration', () => {
    it('should set Monaco editor', () => {
      const mockEditor = {
        defineTheme: jest.fn(),
        setTheme: jest.fn()
      } as any;

      themeManager.setMonacoEditor(mockEditor);
      expect(mockEditor.defineTheme).toHaveBeenCalled();
      expect(mockEditor.setTheme).toHaveBeenCalled();
    });
  });

  describe('Event Handling', () => {
    it('should emit theme changed event', (done) => {
      themeManager.on('themeChanged', (event) => {
        expect(event.previous).toBe('default-dark');
        expect(event.current).toBe('default-light');
        expect(event.theme).toBeDefined();
        done();
      });

      themeManager.setTheme('default-light');
    });

    it('should emit theme registered event', (done) => {
      const customTheme: Theme = {
        id: 'event-test-theme',
        metadata: {
          id: 'event-test-theme',
          name: 'Event Test Theme',
          description: 'A theme for testing events',
          author: 'Test Author',
          version: '1.0.0',
          isDark: true,
          isHighContrast: false,
          isCustom: true,
          accessibility: {
            wcagLevel: 'AA',
            contrastRatio: 4.5,
            supportsReducedMotion: true,
            supportsHighContrast: true
          }
        },
        colors: {} as any,
        monacoTheme: {} as any
      };

      themeManager.on('themeRegistered', (theme) => {
        expect(theme.id).toBe('event-test-theme');
        done();
      });

      themeManager.registerTheme(customTheme);
    });

    it('should emit theme unregistered event', (done) => {
      const customTheme: Theme = {
        id: 'unregister-test-theme',
        metadata: {
          id: 'unregister-test-theme',
          name: 'Unregister Test Theme',
          description: 'A theme for testing unregistration',
          author: 'Test Author',
          version: '1.0.0',
          isDark: true,
          isHighContrast: false,
          isCustom: true,
          accessibility: {
            wcagLevel: 'AA',
            contrastRatio: 4.5,
            supportsReducedMotion: true,
            supportsHighContrast: true
          }
        },
        colors: {} as any,
        monacoTheme: {} as any
      };

      themeManager.registerTheme(customTheme);

      themeManager.on('themeUnregistered', (themeId) => {
        expect(themeId).toBe('unregister-test-theme');
        done();
      });

      themeManager.unregisterTheme('unregister-test-theme');
    });
  });

  describe('Accessibility', () => {
    it('should apply accessibility settings', () => {
      const mockEditor = {
        defineTheme: jest.fn(),
        setTheme: jest.fn()
      } as any;

      themeManager.setMonacoEditor(mockEditor);
      themeManager.updateConfig({
        accessibility: {
          highContrast: true,
          reducedMotion: true,
          fontSize: 'large'
        }
      });

      // Check if CSS classes are applied (this would be tested in integration tests)
      expect(document.documentElement.classList.contains('high-contrast')).toBe(true);
      expect(document.documentElement.classList.contains('reduced-motion')).toBe(true);
      expect(document.documentElement.classList.contains('font-large')).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid theme data gracefully', () => {
      const invalidTheme = {
        id: 'invalid-theme',
        metadata: {
          id: 'invalid-theme',
          name: 'Invalid Theme',
          description: 'A theme with invalid data',
          author: 'Test Author',
          version: '1.0.0',
          isDark: true,
          isHighContrast: false,
          isCustom: true,
          accessibility: {
            wcagLevel: 'AA',
            contrastRatio: 4.5,
            supportsReducedMotion: true,
            supportsHighContrast: true
          }
        },
        colors: null as any,
        monacoTheme: null as any
      };

      // Should not throw error
      expect(() => {
        themeManager.registerTheme(invalidTheme as any);
      }).not.toThrow();
    });
  });

  describe('Cleanup', () => {
    it('should destroy theme manager', () => {
      const customTheme: Theme = {
        id: 'cleanup-test-theme',
        metadata: {
          id: 'cleanup-test-theme',
          name: 'Cleanup Test Theme',
          description: 'A theme for testing cleanup',
          author: 'Test Author',
          version: '1.0.0',
          isDark: true,
          isHighContrast: false,
          isCustom: true,
          accessibility: {
            wcagLevel: 'AA',
            contrastRatio: 4.5,
            supportsReducedMotion: true,
            supportsHighContrast: true
          }
        },
        colors: {} as any,
        monacoTheme: {} as any
      };

      themeManager.registerTheme(customTheme);
      expect(themeManager.getAllThemes().length).toBeGreaterThan(0);

      themeManager.destroy();
      expect(themeManager.getAllThemes().length).toBe(0);
    });
  });
});
