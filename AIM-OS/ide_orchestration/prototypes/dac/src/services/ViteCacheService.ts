/**
 * Vite Cache Service
 * Service for interacting with Command Server to manage Vite cache
 */

const COMMAND_SERVER_URL = 'http://localhost:5001';

export interface CacheInfo {
  buildCache: {
    path: string;
    exists: boolean;
    size: number;
  };
  depsCache: {
    path: string;
    exists: boolean;
    size: number;
  };
  totalSize: number;
  projectPath: string;
}

export interface ClearCacheResult {
  success: boolean;
  cleared?: string[];
  freed?: number;
  restarted?: boolean;
  projectPath?: string;
  error?: string;
}

export class ViteCacheService {
  /**
   * Get cache information
   */
  static async getCacheInfo(projectPath?: string): Promise<CacheInfo | null> {
    try {
      const url = projectPath
        ? `${COMMAND_SERVER_URL}/dev/vite/cache/info?project=${encodeURIComponent(projectPath)}`
        : `${COMMAND_SERVER_URL}/dev/vite/cache/info`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        return data;
      }
      
      console.error('Failed to get cache info:', data.error);
      return null;
    } catch (error: any) {
      console.error('Error getting cache info:', error);
      return null;
    }
  }

  /**
   * Clear Vite cache
   */
  static async clearCache(options: {
    projectPath?: string;
    types?: 'build' | 'deps' | 'all' | string[];
    restart?: boolean;
  }): Promise<ClearCacheResult> {
    try {
      const response = await fetch(`${COMMAND_SERVER_URL}/dev/vite/cache/clear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options),
      });
      
      const data = await response.json();
      return data;
    } catch (error: any) {
      return {
        success: false,
        error: error.message || String(error),
      };
    }
  }

  /**
   * Format bytes to human-readable string
   */
  static formatBytes(bytes: number): string {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  }
}

