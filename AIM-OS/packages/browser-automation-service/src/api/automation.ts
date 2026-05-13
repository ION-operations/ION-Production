/**
 * Automation API Endpoints
 * 
 * REST API endpoints for automation script execution
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import { Router, Request, Response } from 'express';
import { ScriptEngine } from '../services/scriptEngine';
import { loadScriptById } from './scripts';
import {
  ExecuteScriptRequest,
  ExecuteScriptResponse,
  ExecutionStatusResponse,
  PauseExecutionRequest,
  ResumeExecutionRequest,
  StopExecutionRequest,
  ExecutionControlResponse,
  MetricsResponse
} from '../types/api';

export function createAutomationRouter(scriptEngine: ScriptEngine, scriptsPath?: string): Router {
  const router = Router();

  /**
   * POST /api/automation/execute
   * Execute an automation script
   */
  router.post('/execute', async (req: Request<{}, ExecuteScriptResponse, ExecuteScriptRequest>, res: Response<ExecuteScriptResponse>) => {
    try {
      const { browserId, scriptId, script, variables } = req.body;

      if (!browserId) {
        return res.status(400).json({
          success: false,
          error: 'browserId is required'
        });
      }

      if (!script && !scriptId) {
        return res.status(400).json({
          success: false,
          error: 'Either script or scriptId is required'
        });
      }

      let executableScript = script;
      if (!executableScript && scriptId) {
        executableScript = await loadScriptById(scriptId, scriptsPath);
        if (!executableScript) {
          return res.status(404).json({
            success: false,
            error: `Script not found: ${scriptId}`
          });
        }
      }

      if (!executableScript) {
        return res.status(400).json({
          success: false,
          error: 'script is required'
        });
      }

      const executionId = scriptEngine.startExecution(browserId, executableScript, variables);

      res.json({
        success: true,
        executionId
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/automation/status
   * Get execution status
   */
  router.get('/status', async (req: Request, res: Response<ExecutionStatusResponse>) => {
    try {
      const { executionId } = req.query;

      if (!executionId || typeof executionId !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'executionId query parameter is required'
        });
      }

      const status = scriptEngine.getExecutionStatus(executionId);

      if (!status) {
        return res.status(404).json({
          success: false,
          error: 'Execution not found'
        });
      }

      res.json({
        success: true,
        status
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/automation/pause
   * Pause execution
   */
  router.post('/pause', async (req: Request<{}, ExecutionControlResponse, PauseExecutionRequest>, res: Response<ExecutionControlResponse>) => {
    try {
      const { executionId } = req.body;

      if (!executionId) {
        return res.status(400).json({
          success: false,
          error: 'executionId is required'
        });
      }

      scriptEngine.pauseExecution(executionId);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/automation/resume
   * Resume execution
   */
  router.post('/resume', async (req: Request<{}, ExecutionControlResponse, ResumeExecutionRequest>, res: Response<ExecutionControlResponse>) => {
    try {
      const { executionId } = req.body;

      if (!executionId) {
        return res.status(400).json({
          success: false,
          error: 'executionId is required'
        });
      }

      scriptEngine.resumeExecution(executionId);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/automation/stop
   * Stop execution
   */
  router.post('/stop', async (req: Request<{}, ExecutionControlResponse, StopExecutionRequest>, res: Response<ExecutionControlResponse>) => {
    try {
      const { executionId } = req.body;

      if (!executionId) {
        return res.status(400).json({
          success: false,
          error: 'executionId is required'
        });
      }

      scriptEngine.stopExecution(executionId);

      res.json({
        success: true
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/automation/metrics
   * Get aggregated execution metrics
   */
  router.get('/metrics', async (req: Request, res: Response<MetricsResponse>) => {
    try {
      const metrics = scriptEngine.getMetrics();

      res.json({
        success: true,
        metrics
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  return router;
}

