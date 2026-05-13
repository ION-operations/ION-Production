/**
 * Script Management API Endpoints
 * 
 * REST API endpoints for script management
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import { Router, Request, Response } from 'express';
import { promises as fs } from 'fs';
import { join } from 'path';
import { AutomationScript } from '../types/automation';
import {
  SaveScriptRequest,
  SaveScriptResponse,
  ListScriptsResponse,
  GetScriptResponse
} from '../types/api';

export function resolveScriptsPath(scriptsPath?: string): string {
  return scriptsPath || join(process.cwd(), 'browser-automation-scripts');
}

export async function loadScriptById(scriptId: string, scriptsPath?: string): Promise<AutomationScript | undefined> {
  const storagePath = resolveScriptsPath(scriptsPath);
  const scriptPath = join(storagePath, `${scriptId}.json`);

  try {
    const data = await fs.readFile(scriptPath, 'utf8');
    return JSON.parse(data) as AutomationScript;
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      return undefined;
    }
    throw error;
  }
}

export function createScriptsRouter(scriptsPath?: string): Router {
  const router = Router();
  const storagePath = resolveScriptsPath(scriptsPath);

  // Ensure scripts directory exists
  fs.mkdir(storagePath, { recursive: true }).catch(() => {
    // Directory might already exist, ignore error
  });

  /**
   * POST /api/scripts/save
   * Save a script
   */
  router.post('/save', async (req: Request<{}, SaveScriptResponse, SaveScriptRequest>, res: Response<SaveScriptResponse>) => {
    try {
      const { name, description, provider, script } = req.body;

      if (!name || !script) {
        return res.status(400).json({
          success: false,
          error: 'name and script are required'
        });
      }

      const scriptId = `script-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      const scriptPath = join(storagePath, `${scriptId}.json`);

      const scriptToSave: AutomationScript = {
        ...script,
        name,
        description: description || script.description || '',
        provider: provider || script.provider || 'custom'
      };

      await fs.writeFile(scriptPath, JSON.stringify(scriptToSave, null, 2), 'utf8');

      res.json({
        success: true,
        scriptId
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/scripts/list
   * List all scripts
   */
  router.get('/list', async (req: Request, res: Response<ListScriptsResponse>) => {
    try {
      const { provider } = req.query;

      const files = await fs.readdir(storagePath);
      const scriptFiles = files.filter(f => f.endsWith('.json'));

      const scripts = [];

      for (const file of scriptFiles) {
        try {
          const filePath = join(storagePath, file);
          const data = await fs.readFile(filePath, 'utf8');
          const script: AutomationScript = JSON.parse(data);

          // Filter by provider if specified
          if (provider && script.provider !== provider) {
            continue;
          }

          const scriptId = file.replace('.json', '');
          scripts.push({
            id: scriptId,
            name: script.name,
            provider: script.provider,
            createdAt: new Date(parseInt(scriptId.split('-')[1])).toISOString()
          });
        } catch (error) {
          // Skip invalid script files
          continue;
        }
      }

      res.json({
        success: true,
        scripts
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/scripts/:id
   * Get a specific script
   */
  router.get('/:id', async (req: Request, res: Response<GetScriptResponse>) => {
    try {
      const { id } = req.params;
      const scriptPath = join(storagePath, `${id}.json`);

      try {
        const data = await fs.readFile(scriptPath, 'utf8');
        const script: AutomationScript = JSON.parse(data);

        res.json({
          success: true,
          script
        });
      } catch (error: any) {
        if (error.code === 'ENOENT') {
          return res.status(404).json({
            success: false,
            error: 'Script not found'
          });
        }
        throw error;
      }
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * DELETE /api/scripts/:id
   * Delete a script
   */
  router.delete('/:id', async (req: Request, res: Response) => {
    try {
      const { id } = req.params;
      const scriptPath = join(storagePath, `${id}.json`);

      try {
        await fs.unlink(scriptPath);
        res.json({
          success: true
        });
      } catch (error: any) {
        if (error.code === 'ENOENT') {
          return res.status(404).json({
            success: false,
            error: 'Script not found'
          });
        }
        throw error;
      }
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  return router;
}

