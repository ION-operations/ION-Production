/**
 * Advanced Monaco Editor - Basic Example
 * 
 * This example demonstrates the basic usage of the Advanced Monaco Editor.
 */

import React, { useState } from 'react';
import { AdvancedMonacoEditor, AdvancedMonacoConfiguration } from '../src';

const BasicExample: React.FC = () => {
  const [code, setCode] = useState(`/**
 * Advanced Monaco Editor Example
 * 
 * This example demonstrates the basic usage of the Advanced Monaco Editor
 * with AI-driven intelligence and natural language descriptions.
 */

interface User {
  id: number;
  name: string;
  email: string;
  createdAt: Date;
}

class UserService {
  private users: User[] = [];

  /**
   * Creates a new user
   * @param userData - The user data to create
   * @returns The created user
   */
  async createUser(userData: Omit<User, 'id' | 'createdAt'>): Promise<User> {
    const user: User = {
      id: this.users.length + 1,
      ...userData,
      createdAt: new Date()
    };
    
    this.users.push(user);
    return user;
  }

  /**
   * Retrieves a user by ID
   * @param id - The user ID
   * @returns The user or undefined if not found
   */
  getUserById(id: number): User | undefined {
    return this.users.find(user => user.id === id);
  }

  /**
   * Retrieves all users
   * @returns Array of all users
   */
  getAllUsers(): User[] {
    return [...this.users];
  }

  /**
   * Updates a user
   * @param id - The user ID
   * @param updates - The updates to apply
   * @returns The updated user or undefined if not found
   */
  updateUser(id: number, updates: Partial<User>): User | undefined {
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) return undefined;

    this.users[userIndex] = { ...this.users[userIndex], ...updates };
    return this.users[userIndex];
  }

  /**
   * Deletes a user
   * @param id - The user ID
   * @returns True if deleted, false if not found
   */
  deleteUser(id: number): boolean {
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) return false;

    this.users.splice(userIndex, 1);
    return true;
  }
}

export default UserService;`);

  const [language, setLanguage] = useState('typescript');

  const configuration: AdvancedMonacoConfiguration = {
    dropdowns: {
      enabled: true,
      position: 'below',
      maxWidth: 400,
      maxHeight: 300,
      animation: true,
      delay: 500,
      timeout: 5000,
      autoHide: true,
      closeOnClickOutside: true,
      closeOnEscape: true
    },
    contextMenus: {
      enabled: true,
      position: 'mouse',
      maxItems: 10,
      grouping: true,
      icons: true,
      shortcuts: true,
      autoHide: true,
      closeOnClickOutside: true,
      closeOnEscape: true
    },
    tooltips: {
      enabled: true,
      position: 'mouse',
      delay: 1000,
      timeout: 3000,
      maxWidth: 300,
      animation: true,
      autoHide: true,
      closeOnClickOutside: true,
      closeOnEscape: true
    },
    intelligence: {
      enabled: true,
      analysisDepth: 'medium',
      cacheEnabled: true,
      cacheSize: 100,
      cacheTimeout: 300000,
      aimosIntegration: true,
      naturalLanguage: true,
      suggestions: true,
      actions: true,
      realTimeAnalysis: true,
      backgroundAnalysis: true
    },
    aimos: {
      enabled: true,
      endpoints: {
        cmc: 'http://localhost:8000/cmc',
        hhni: 'http://localhost:8000/hhni',
        vif: 'http://localhost:8000/vif',
        seg: 'http://localhost:8000/seg',
        apoe: 'http://localhost:8000/apoe',
        iis: 'http://localhost:8000/iis'
      },
      timeout: 5000,
      retries: 3,
      cache: true
    },
    performance: {
      maxAnalysisTime: 5000,
      maxMemoryUsage: 100 * 1024 * 1024, // 100MB
      enableProfiling: false,
      enableMetrics: true,
      enableOptimizations: true,
      enableLazyLoading: true,
      enableProgressiveLoading: true,
      workerThreads: 2,
      batchSize: 10
    },
    security: {
      enableSandboxing: true,
      maxCodeSize: 1024 * 1024, // 1MB
      enableValidation: true,
      enableEncryption: false,
      enableAccessControl: true,
      allowedDomains: ['localhost'],
      blockedDomains: [],
      enableDataProtection: true,
      enableAuditLogging: false,
      enablePrivacyMode: false
    },
    theme: {
      name: 'advanced-monaco',
      base: 'vs-dark',
      colors: {},
      tokenColors: []
    },
    editor: {
      theme: 'vs-dark',
      fontSize: 14,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      lineNumbers: 'on',
      wordWrap: 'on',
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 2,
      insertSpaces: true,
      detectIndentation: true,
      renderWhitespace: 'selection',
      renderControlCharacters: false,
      renderIndentGuides: true,
      highlightActiveIndentGuide: true,
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true
      }
    }
  };

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    console.log('Code changed:', newCode);
  };

  const handleSymbolDetected = (symbol: any) => {
    console.log('Symbol detected:', symbol);
  };

  const handleAnalysisComplete = (analysis: any) => {
    console.log('Analysis complete:', analysis);
  };

  const handleError = (error: Error) => {
    console.error('Error:', error);
  };

  const handleLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(event.target.value);
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px', borderBottom: '1px solid #333', backgroundColor: '#2d2d30' }}>
        <h1 style={{ margin: 0, color: '#fff', fontSize: '24px' }}>
          Advanced Monaco Editor Example
        </h1>
        <div style={{ marginTop: '8px', display: 'flex', gap: '16px', alignItems: 'center' }}>
          <label style={{ color: '#ccc', fontSize: '14px' }}>
            Language:
            <select
              value={language}
              onChange={handleLanguageChange}
              style={{
                marginLeft: '8px',
                padding: '4px 8px',
                backgroundColor: '#3e3e42',
                color: '#fff',
                border: '1px solid #4e4e52',
                borderRadius: '4px'
              }}
            >
              <option value="typescript">TypeScript</option>
              <option value="javascript">JavaScript</option>
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="csharp">C#</option>
            </select>
          </label>
          <div style={{ color: '#888', fontSize: '12px' }}>
            Features: Symbol Detection • Code Analysis • AIM-OS Integration • Natural Language Descriptions
          </div>
        </div>
      </div>
      
      <div style={{ flex: 1, position: 'relative' }}>
        <AdvancedMonacoEditor
          code={code}
          language={language}
          configuration={configuration}
          onCodeChange={handleCodeChange}
          onSymbolDetected={handleSymbolDetected}
          onAnalysisComplete={handleAnalysisComplete}
          onError={handleError}
          style={{ height: '100%', width: '100%' }}
        />
      </div>
    </div>
  );
};

export default BasicExample;
