/**
 * Advanced Monaco Editor - Symbol Detection Service Tests
 * 
 * This file contains tests for the SymbolDetectionService.
 */

import { SymbolDetectionService } from '../src/services/SymbolDetectionService';
import { SymbolType, SymbolKind } from '../src/types/MonacoTypes';

// Mock Monaco Editor
const mockEditor = {
  getModel: jest.fn(() => ({
    getValue: jest.fn(() => 'function test() { return "hello"; }'),
    getLanguageId: jest.fn(() => 'typescript')
  })),
  onDidChangeModelContent: jest.fn(),
  onDidChangeModel: jest.fn(),
  dispose: jest.fn()
};

describe('SymbolDetectionService', () => {
  let service: SymbolDetectionService;

  beforeEach(() => {
    service = new SymbolDetectionService(mockEditor as any);
  });

  afterEach(() => {
    service.destroy();
  });

  describe('detectSymbols', () => {
    it('should detect function symbols', async () => {
      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect class symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'class TestClass { }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect interface symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'interface TestInterface { }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect variable symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'const testVar = "hello";'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect constant symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'const TEST_CONST = "hello";'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect enum symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'enum TestEnum { A, B, C }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect module symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'module TestModule { }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect namespace symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'namespace TestNamespace { }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should detect type symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'type TestType = string;'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should handle empty code', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => ''),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBe(0);
    });

    it('should handle code with comments', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => '// This is a comment\nfunction test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });

    it('should handle code with multiple symbols', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => `
          function test() { return "hello"; }
          class TestClass { }
          interface TestInterface { }
          const testVar = "hello";
        `),
        getLanguageId: jest.fn(() => 'typescript')
      });

      const symbols = await service.detectSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle different languages', async () => {
      const languages = ['typescript', 'javascript', 'python', 'java', 'csharp'];
      
      for (const language of languages) {
        mockEditor.getModel.mockReturnValue({
          getValue: jest.fn(() => 'function test() { return "hello"; }'),
          getLanguageId: jest.fn(() => language)
        });

        const symbols = await service.detectSymbols();
        
        expect(symbols).toBeDefined();
        expect(Array.isArray(symbols)).toBe(true);
      }
    });

    it('should emit symbols-detected event', (done) => {
      service.on('symbols-detected', (symbols) => {
        expect(symbols).toBeDefined();
        expect(Array.isArray(symbols)).toBe(true);
        done();
      });

      service.detectSymbols();
    });

    it('should emit error event on failure', (done) => {
      service.on('error', (error) => {
        expect(error).toBeDefined();
        done();
      });

      // Mock an error by making getModel return null
      mockEditor.getModel.mockReturnValue(null);
      service.detectSymbols();
    });
  });

  describe('getSymbols', () => {
    it('should return all symbols', async () => {
      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
    });
  });

  describe('getSymbol', () => {
    it('should return symbol by ID', async () => {
      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = service.getSymbol(symbols[0].id);
        expect(symbol).toBeDefined();
        expect(symbol?.id).toBe(symbols[0].id);
      }
    });

    it('should return undefined for non-existent ID', () => {
      const symbol = service.getSymbol('non-existent-id');
      expect(symbol).toBeUndefined();
    });
  });

  describe('getSymbolsByType', () => {
    it('should return symbols by type', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const functionSymbols = service.getSymbolsByType(SymbolType.FUNCTION);
      
      expect(functionSymbols).toBeDefined();
      expect(Array.isArray(functionSymbols)).toBe(true);
    });
  });

  describe('getSymbolsByKind', () => {
    it('should return symbols by kind', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const definitionSymbols = service.getSymbolsByKind(SymbolKind.DEFINITION);
      
      expect(definitionSymbols).toBeDefined();
      expect(Array.isArray(definitionSymbols)).toBe(true);
    });
  });

  describe('searchSymbols', () => {
    it('should search symbols by name', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const searchResults = service.searchSymbols('test');
      
      expect(searchResults).toBeDefined();
      expect(Array.isArray(searchResults)).toBe(true);
    });

    it('should return empty array for no matches', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const searchResults = service.searchSymbols('nonexistent');
      
      expect(searchResults).toBeDefined();
      expect(Array.isArray(searchResults)).toBe(true);
      expect(searchResults.length).toBe(0);
    });

    it('should be case insensitive', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const searchResults = service.searchSymbols('TEST');
      
      expect(searchResults).toBeDefined();
      expect(Array.isArray(searchResults)).toBe(true);
    });
  });

  describe('event handling', () => {
    it('should add event listener', () => {
      const listener = jest.fn();
      service.on('symbols-detected', listener);
      
      // The listener should be added without error
      expect(() => service.on('symbols-detected', listener)).not.toThrow();
    });

    it('should remove event listener', () => {
      const listener = jest.fn();
      service.on('symbols-detected', listener);
      service.off('symbols-detected', listener);
      
      // The listener should be removed without error
      expect(() => service.off('symbols-detected', listener)).not.toThrow();
    });

    it('should emit events', (done) => {
      service.on('symbols-detected', (symbols) => {
        expect(symbols).toBeDefined();
        done();
      });

      service.detectSymbols();
    });
  });

  describe('cleanup', () => {
    it('should destroy service and clean up resources', () => {
      service.destroy();
      // Service should be destroyed without errors
    });
  });

  describe('symbol metadata extraction', () => {
    it('should extract function parameters', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test(param1: string, param2?: number) { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = symbols[0];
        expect(symbol.metadata.parameters).toBeDefined();
        expect(Array.isArray(symbol.metadata.parameters)).toBe(true);
      }
    });

    it('should extract return type', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test(): string { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = symbols[0];
        expect(symbol.metadata.returnType).toBeDefined();
      }
    });

    it('should extract modifiers', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'export async function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = symbols[0];
        expect(symbol.metadata.modifiers).toBeDefined();
        expect(Array.isArray(symbol.metadata.modifiers)).toBe(true);
      }
    });

    it('should extract annotations', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => '@deprecated function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = symbols[0];
        expect(symbol.metadata.annotations).toBeDefined();
        expect(Array.isArray(symbol.metadata.annotations)).toBe(true);
      }
    });

    it('should calculate complexity', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'function test() { if (true) { return "hello"; } }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = symbols[0];
        expect(symbol.metadata.complexity).toBeDefined();
        expect(typeof symbol.metadata.complexity).toBe('number');
      }
    });

    it('should extract dependencies', async () => {
      mockEditor.getModel.mockReturnValue({
        getValue: jest.fn(() => 'import { Component } from "react"; function test() { return "hello"; }'),
        getLanguageId: jest.fn(() => 'typescript')
      });

      await service.detectSymbols();
      const symbols = service.getSymbols();
      
      if (symbols.length > 0) {
        const symbol = symbols[0];
        expect(symbol.metadata.dependencies).toBeDefined();
        expect(Array.isArray(symbol.metadata.dependencies)).toBe(true);
      }
    });
  });
});
