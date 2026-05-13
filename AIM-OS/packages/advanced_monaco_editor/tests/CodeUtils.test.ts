/**
 * Advanced Monaco Editor - Code Utils Tests
 * 
 * This file contains tests for the CodeUtils utility class.
 */

import { CodeUtils } from '../src/utils/CodeUtils';
import { SymbolType, SymbolKind } from '../src/types/MonacoTypes';

describe('CodeUtils', () => {
  describe('extractSymbols', () => {
    it('should extract symbols from TypeScript code', () => {
      const code = `
        function hello() { return "world"; }
        class TestClass { }
        interface TestInterface { }
        const testVar = "hello";
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should extract symbols from JavaScript code', () => {
      const code = `
        function hello() { return "world"; }
        class TestClass { }
        const testVar = "hello";
      `;
      const language = 'javascript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should extract symbols from Python code', () => {
      const code = `
        def hello():
            return "world"
        
        class TestClass:
            pass
      `;
      const language = 'python';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle empty code', () => {
      const code = '';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBe(0);
    });

    it('should handle code with comments', () => {
      const code = `
        // This is a comment
        function hello() { return "world"; }
        /* Another comment */
        class TestClass { }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with multiple functions', () => {
      const code = `
        function hello() { return "world"; }
        function goodbye() { return "bye"; }
        function greet(name) { return \`Hello \${name}\`; }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBe(3);
    });

    it('should handle code with classes', () => {
      const code = `
        class User {
          constructor(name) {
            this.name = name;
          }
          getName() {
            return this.name;
          }
        }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with interfaces', () => {
      const code = `
        interface User {
          name: string;
          email: string;
        }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with variables', () => {
      const code = `
        const testVar = "hello";
        let anotherVar = 42;
        var oldVar = true;
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with constants', () => {
      const code = `
        const TEST_CONST = "hello";
        const ANOTHER_CONST = 42;
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with enums', () => {
      const code = `
        enum TestEnum {
          A,
          B,
          C
        }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with modules', () => {
      const code = `
        module TestModule {
          export function hello() { return "world"; }
        }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with namespaces', () => {
      const code = `
        namespace TestNamespace {
          export function hello() { return "world"; }
        }
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });

    it('should handle code with types', () => {
      const code = `
        type TestType = string;
        type AnotherType = { name: string; age: number; };
      `;
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);

      expect(symbols).toBeDefined();
      expect(Array.isArray(symbols)).toBe(true);
      expect(symbols.length).toBeGreaterThan(0);
    });
  });

  describe('formatCode', () => {
    it('should format TypeScript code', () => {
      const code = 'function hello(){return "world";}';
      const language = 'typescript';

      const formatted = CodeUtils.formatCode(code, language);

      expect(formatted).toBeDefined();
      expect(typeof formatted).toBe('string');
    });

    it('should format JavaScript code', () => {
      const code = 'function hello(){return "world";}';
      const language = 'javascript';

      const formatted = CodeUtils.formatCode(code, language);

      expect(formatted).toBeDefined();
      expect(typeof formatted).toBe('string');
    });

    it('should format Python code', () => {
      const code = 'def hello():return "world"';
      const language = 'python';

      const formatted = CodeUtils.formatCode(code, language);

      expect(formatted).toBeDefined();
      expect(typeof formatted).toBe('string');
    });

    it('should handle empty code', () => {
      const code = '';
      const language = 'typescript';

      const formatted = CodeUtils.formatCode(code, language);

      expect(formatted).toBeDefined();
      expect(formatted).toBe('');
    });

    it('should handle invalid language', () => {
      const code = 'function hello() { return "world"; }';
      const language = 'invalid-language';

      const formatted = CodeUtils.formatCode(code, language);

      expect(formatted).toBeDefined();
      expect(typeof formatted).toBe('string');
    });
  });

  describe('validateCode', () => {
    it('should validate TypeScript code', () => {
      const code = 'function hello() { return "world"; }';
      const language = 'typescript';

      const result = CodeUtils.validateCode(code, language);

      expect(result).toBeDefined();
      expect(result.valid).toBeDefined();
      expect(typeof result.valid).toBe('boolean');
      expect(result.errors).toBeDefined();
      expect(Array.isArray(result.errors)).toBe(true);
    });

    it('should validate JavaScript code', () => {
      const code = 'function hello() { return "world"; }';
      const language = 'javascript';

      const result = CodeUtils.validateCode(code, language);

      expect(result).toBeDefined();
      expect(result.valid).toBeDefined();
      expect(typeof result.valid).toBe('boolean');
      expect(result.errors).toBeDefined();
      expect(Array.isArray(result.errors)).toBe(true);
    });

    it('should validate Python code', () => {
      const code = 'def hello():\n    return "world"';
      const language = 'python';

      const result = CodeUtils.validateCode(code, language);

      expect(result).toBeDefined();
      expect(result.valid).toBeDefined();
      expect(typeof result.valid).toBe('boolean');
      expect(result.errors).toBeDefined();
      expect(Array.isArray(result.errors)).toBe(true);
    });

    it('should handle empty code', () => {
      const code = '';
      const language = 'typescript';

      const result = CodeUtils.validateCode(code, language);

      expect(result).toBeDefined();
      expect(result.valid).toBeDefined();
      expect(typeof result.valid).toBe('boolean');
      expect(result.errors).toBeDefined();
      expect(Array.isArray(result.errors)).toBe(true);
    });

    it('should handle invalid language', () => {
      const code = 'function hello() { return "world"; }';
      const language = 'invalid-language';

      const result = CodeUtils.validateCode(code, language);

      expect(result).toBeDefined();
      expect(result.valid).toBeDefined();
      expect(typeof result.valid).toBe('boolean');
      expect(result.errors).toBeDefined();
      expect(Array.isArray(result.errors)).toBe(true);
    });
  });

  describe('getLanguageConfig', () => {
    it('should return TypeScript configuration', () => {
      const config = CodeUtils.getLanguageConfig('typescript');

      expect(config).toBeDefined();
      expect(config.tabSize).toBe(2);
      expect(config.insertSpaces).toBe(true);
      expect(config.detectIndentation).toBe(true);
    });

    it('should return JavaScript configuration', () => {
      const config = CodeUtils.getLanguageConfig('javascript');

      expect(config).toBeDefined();
      expect(config.tabSize).toBe(2);
      expect(config.insertSpaces).toBe(true);
      expect(config.detectIndentation).toBe(true);
    });

    it('should return Python configuration', () => {
      const config = CodeUtils.getLanguageConfig('python');

      expect(config).toBeDefined();
      expect(config.tabSize).toBe(4);
      expect(config.insertSpaces).toBe(true);
      expect(config.detectIndentation).toBe(true);
    });

    it('should return Java configuration', () => {
      const config = CodeUtils.getLanguageConfig('java');

      expect(config).toBeDefined();
      expect(config.tabSize).toBe(4);
      expect(config.insertSpaces).toBe(true);
      expect(config.detectIndentation).toBe(true);
    });

    it('should return C# configuration', () => {
      const config = CodeUtils.getLanguageConfig('csharp');

      expect(config).toBeDefined();
      expect(config.tabSize).toBe(4);
      expect(config.insertSpaces).toBe(true);
      expect(config.detectIndentation).toBe(true);
    });

    it('should return default configuration for unknown language', () => {
      const config = CodeUtils.getLanguageConfig('unknown-language');

      expect(config).toBeDefined();
      expect(config.tabSize).toBe(2);
      expect(config.insertSpaces).toBe(true);
      expect(config.detectIndentation).toBe(true);
    });
  });

  describe('symbol extraction methods', () => {
    it('should extract function symbols correctly', () => {
      const code = 'function hello() { return "world"; }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbols = symbols.filter(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbols.length).toBeGreaterThan(0);
      expect(functionSymbols[0].name).toBe('hello');
      expect(functionSymbols[0].type).toBe(SymbolType.FUNCTION);
      expect(functionSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract class symbols correctly', () => {
      const code = 'class TestClass { }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const classSymbols = symbols.filter(s => s.type === SymbolType.CLASS);

      expect(classSymbols.length).toBeGreaterThan(0);
      expect(classSymbols[0].name).toBe('TestClass');
      expect(classSymbols[0].type).toBe(SymbolType.CLASS);
      expect(classSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract interface symbols correctly', () => {
      const code = 'interface TestInterface { }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const interfaceSymbols = symbols.filter(s => s.type === SymbolType.INTERFACE);

      expect(interfaceSymbols.length).toBeGreaterThan(0);
      expect(interfaceSymbols[0].name).toBe('TestInterface');
      expect(interfaceSymbols[0].type).toBe(SymbolType.INTERFACE);
      expect(interfaceSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract variable symbols correctly', () => {
      const code = 'const testVar = "hello";';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const variableSymbols = symbols.filter(s => s.type === SymbolType.VARIABLE);

      expect(variableSymbols.length).toBeGreaterThan(0);
      expect(variableSymbols[0].name).toBe('testVar');
      expect(variableSymbols[0].type).toBe(SymbolType.VARIABLE);
      expect(variableSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract constant symbols correctly', () => {
      const code = 'const TEST_CONST = "hello";';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const constantSymbols = symbols.filter(s => s.type === SymbolType.CONSTANT);

      expect(constantSymbols.length).toBeGreaterThan(0);
      expect(constantSymbols[0].name).toBe('TEST_CONST');
      expect(constantSymbols[0].type).toBe(SymbolType.CONSTANT);
      expect(constantSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract enum symbols correctly', () => {
      const code = 'enum TestEnum { A, B, C }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const enumSymbols = symbols.filter(s => s.type === SymbolType.ENUM);

      expect(enumSymbols.length).toBeGreaterThan(0);
      expect(enumSymbols[0].name).toBe('TestEnum');
      expect(enumSymbols[0].type).toBe(SymbolType.ENUM);
      expect(enumSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract module symbols correctly', () => {
      const code = 'module TestModule { }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const moduleSymbols = symbols.filter(s => s.type === SymbolType.MODULE);

      expect(moduleSymbols.length).toBeGreaterThan(0);
      expect(moduleSymbols[0].name).toBe('TestModule');
      expect(moduleSymbols[0].type).toBe(SymbolType.MODULE);
      expect(moduleSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract namespace symbols correctly', () => {
      const code = 'namespace TestNamespace { }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const namespaceSymbols = symbols.filter(s => s.type === SymbolType.NAMESPACE);

      expect(namespaceSymbols.length).toBeGreaterThan(0);
      expect(namespaceSymbols[0].name).toBe('TestNamespace');
      expect(namespaceSymbols[0].type).toBe(SymbolType.NAMESPACE);
      expect(namespaceSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });

    it('should extract type symbols correctly', () => {
      const code = 'type TestType = string;';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const typeSymbols = symbols.filter(s => s.type === SymbolType.TYPE);

      expect(typeSymbols.length).toBeGreaterThan(0);
      expect(typeSymbols[0].name).toBe('TestType');
      expect(typeSymbols[0].type).toBe(SymbolType.TYPE);
      expect(typeSymbols[0].kind).toBe(SymbolKind.DEFINITION);
    });
  });

  describe('symbol metadata extraction', () => {
    it('should extract function parameters', () => {
      const code = 'function test(param1: string, param2?: number) { return "hello"; }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbol = symbols.find(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbol).toBeDefined();
      expect(functionSymbol?.metadata.parameters).toBeDefined();
      expect(Array.isArray(functionSymbol?.metadata.parameters)).toBe(true);
    });

    it('should extract return type', () => {
      const code = 'function test(): string { return "hello"; }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbol = symbols.find(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbol).toBeDefined();
      expect(functionSymbol?.metadata.returnType).toBeDefined();
    });

    it('should extract modifiers', () => {
      const code = 'export async function test() { return "hello"; }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbol = symbols.find(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbol).toBeDefined();
      expect(functionSymbol?.metadata.modifiers).toBeDefined();
      expect(Array.isArray(functionSymbol?.metadata.modifiers)).toBe(true);
    });

    it('should extract annotations', () => {
      const code = '@deprecated function test() { return "hello"; }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbol = symbols.find(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbol).toBeDefined();
      expect(functionSymbol?.metadata.annotations).toBeDefined();
      expect(Array.isArray(functionSymbol?.metadata.annotations)).toBe(true);
    });

    it('should calculate complexity', () => {
      const code = 'function test() { if (true) { return "hello"; } }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbol = symbols.find(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbol).toBeDefined();
      expect(functionSymbol?.metadata.complexity).toBeDefined();
      expect(typeof functionSymbol?.metadata.complexity).toBe('number');
    });

    it('should extract dependencies', () => {
      const code = 'import { Component } from "react"; function test() { return "hello"; }';
      const language = 'typescript';

      const symbols = CodeUtils.extractSymbols(code, language);
      const functionSymbol = symbols.find(s => s.type === SymbolType.FUNCTION);

      expect(functionSymbol).toBeDefined();
      expect(functionSymbol?.metadata.dependencies).toBeDefined();
      expect(Array.isArray(functionSymbol?.metadata.dependencies)).toBe(true);
    });
  });
});
