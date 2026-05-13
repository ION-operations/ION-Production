/**
 * Test setup for Advanced Monaco Editor
 */

import '@testing-library/jest-dom';

// Mock Monaco Editor
jest.mock('monaco-editor', () => ({
  editor: {
    create: jest.fn(),
    setModelMarkers: jest.fn(),
    getModel: jest.fn(),
    onDidChangeModelContent: jest.fn(),
    onDidChangeModel: jest.fn(),
    dispose: jest.fn()
  },
  languages: {
    register: jest.fn(),
    setLanguageConfiguration: jest.fn(),
    setMonarchTokensProvider: jest.fn(),
    registerCompletionItemProvider: jest.fn(),
    registerHoverProvider: jest.fn(),
    registerSignatureHelpProvider: jest.fn()
  },
  Range: jest.fn(),
  Position: jest.fn(),
  CancellationToken: jest.fn(),
  Uri: jest.fn()
}));

// Mock @monaco-editor/react
jest.mock('@monaco-editor/react', () => ({
  Editor: ({ onMount, onChange, ...props }: any) => {
    const mockEditor = {
      getModel: () => ({
        getValue: () => props.value || '',
        getLanguageId: () => props.language || 'typescript'
      }),
      onDidChangeModelContent: jest.fn(),
      onDidChangeModel: jest.fn(),
      dispose: jest.fn()
    };

    React.useEffect(() => {
      if (onMount) {
        onMount(mockEditor);
      }
    }, [onMount]);

    return (
      <div data-testid="monaco-editor" onClick={() => onChange && onChange(props.value)}>
        Monaco Editor
      </div>
    );
  }
}));

// Mock console methods to reduce noise in tests
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalConsoleError.call(console, ...args);
  };

  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalConsoleWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalConsoleError;
  console.warn = originalConsoleWarn;
});
