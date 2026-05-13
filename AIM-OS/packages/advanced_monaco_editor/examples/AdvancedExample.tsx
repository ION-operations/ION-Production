/**
 * Advanced Example - Advanced Monaco Editor
 * 
 * Demonstrates advanced usage with full configuration,
 * theme system, and all features enabled
 */

import React, { useState } from 'react';
import { AdvancedMonacoEditor } from '../src/components/AdvancedMonacoEditor';

export const AdvancedExample: React.FC = () => {
  const [code, setCode] = useState(`// Advanced Example with TypeScript
interface User {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
}

class UserService {
  private users: User[] = [];
  
  constructor() {
    this.loadUsers();
  }
  
  private async loadUsers(): Promise<void> {
    try {
      const response = await fetch('/api/users');
      this.users = await response.json();
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  }
  
  public getUserById(id: number): User | undefined {
    return this.users.find(user => user.id === id);
  }
  
  public createUser(userData: Omit<User, 'id'>): User {
    const newUser: User = {
      id: Date.now(),
      ...userData
    };
    this.users.push(newUser);
    return newUser;
  }
  
  public getActiveUsers(): User[] {
    return this.users.filter(user => user.isActive);
  }
}

const userService = new UserService();
const activeUsers = userService.getActiveUsers();
console.log('Active users:', activeUsers);
`);

  const [theme, setTheme] = useState('default-dark');

  const handleChange = (newCode: string) => {
    setCode(newCode);
  };

  const handleMount = (editor: any) => {
    console.log('Advanced editor mounted:', editor);
  };

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme);
    console.log('Theme changed to:', newTheme);
  };

  const config = {
    dropdowns: {
      enabled: true,
      maxItems: 15,
      showDescriptions: true,
      showExamples: true,
      showRelatedSymbols: true
    },
    contextMenus: {
      enabled: true,
      maxItems: 20,
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
      cacheSize: 2000,
      cacheTimeout: 600000
    },
    aimos: {
      enabled: true,
      services: ['cmc', 'hhni', 'vif', 'seg', 'apoe', 'iis'],
      retryAttempts: 5,
      retryDelay: 2000
    },
    performance: {
      enableMetrics: true,
      enableProfiling: true,
      enableLazyLoading: true,
      maxMemoryUsage: 200 * 1024 * 1024,
      maxAnalysisTime: 200
    },
    security: {
      enableValidation: true,
      enableAccessControl: true,
      enableAuditLogging: true,
      enableEncryption: false,
      enableSandboxing: true
    }
  };

  return (
    <div style={{ height: '600px', border: '1px solid #ccc', borderRadius: '4px' }}>
      <AdvancedMonacoEditor
        value={code}
        language="typescript"
        onChange={handleChange}
        onMount={handleMount}
        theme={theme}
        onThemeChange={handleThemeChange}
        showThemeSelector={true}
        enableDropdowns={true}
        enableContextMenus={true}
        enableTooltips={true}
        config={config}
      />
    </div>
  );
};

export default AdvancedExample;
