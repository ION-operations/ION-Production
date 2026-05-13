/**
 * Browser Control API Endpoints
 * 
 * REST API endpoints for browser control operations
 * Based on: BROWSER_AUTOMATION_PANEL_SPECIFICATION_T3.md
 */

import { Router, Request, Response } from 'express';
import { BrowserService } from '../services/browserService';
import {
  LaunchBrowserRequest,
  LaunchBrowserResponse,
  NavigateRequest,
  NavigateResponse,
  BrowserStatusResponse,
  ViewportResponse,
  DetectElementsRequest,
  DetectElementsResponse
} from '../types/api';

export function createBrowserRouter(browserService: BrowserService): Router {
  const router = Router();

  /**
   * POST /api/browser/launch
   * Launch a new browser instance
   */
  router.post('/launch', async (req: Request<{}, LaunchBrowserResponse, LaunchBrowserRequest>, res: Response<LaunchBrowserResponse>) => {
    try {
      const { headless, viewport, userAgent, args } = req.body;

      if (!viewport || !viewport.width || !viewport.height) {
        return res.status(400).json({
          success: false,
          error: 'Viewport width and height are required'
        });
      }

      const browserId = await browserService.launchBrowser({
        // Default to visible browser for manual sign-in workflows.
        headless: headless ?? false,
        viewport,
        userAgent,
        args
      });

      res.json({
        success: true,
        browserId
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/browser/navigate
   * Navigate to a URL
   */
  router.post('/navigate', async (req: Request<{}, NavigateResponse, NavigateRequest>, res: Response<NavigateResponse>) => {
    try {
      const { browserId, url } = req.body;

      if (!browserId || !url) {
        return res.status(400).json({
          success: false,
          error: 'browserId and url are required'
        });
      }

      await browserService.navigateTo(browserId, url);

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
   * GET /api/browser/screenshot
   * Capture screenshot
   */
  router.get('/screenshot', async (req: Request, res: Response) => {
    try {
      const { browserId, fullPage, type, quality } = req.query;

      if (!browserId || typeof browserId !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'browserId query parameter is required'
        });
      }

      const screenshot = await browserService.screenshot(browserId, {
        type: (type as 'png' | 'jpeg') || 'png',
        fullPage: fullPage === 'true',
        quality: quality ? parseInt(quality as string) : undefined
      });

      res.setHeader('Content-Type', type === 'jpeg' ? 'image/jpeg' : 'image/png');
      res.send(screenshot);
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * GET /api/browser/status
   * Get browser status
   */
  router.get('/status', async (req: Request, res: Response<BrowserStatusResponse>) => {
    try {
      const { browserId } = req.query;

      if (!browserId || typeof browserId !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'browserId query parameter is required'
        });
      }

      const status = await browserService.getBrowserStatus(browserId);

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
   * POST /api/browser/close
   * Close browser instance
   */
  router.post('/close', async (req: Request, res: Response) => {
    try {
      const { browserId } = req.body;

      if (!browserId) {
        return res.status(400).json({
          success: false,
          error: 'browserId is required'
        });
      }

      await browserService.closeBrowser(browserId);

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
   * GET /api/browser/viewport
   * Get viewport URL for live browser view
   */
  router.get('/viewport', async (req: Request, res: Response<ViewportResponse>) => {
    try {
      const { browserId } = req.query;

      if (!browserId || typeof browserId !== 'string') {
        return res.status(400).json({
          success: false,
          error: 'browserId query parameter is required'
        });
      }

      const viewportUrl = await browserService.getViewportUrl(browserId);

      res.json({
        success: true,
        viewportUrl
      });
    } catch (error) {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  /**
   * POST /api/browser/detect-elements
   * Detect interactive elements on the current page
   */
  router.post('/detect-elements', async (req: Request<{}, DetectElementsResponse, DetectElementsRequest>, res: Response<DetectElementsResponse>) => {
    try {
      const { browserId, selector } = req.body;

      if (!browserId) {
        return res.status(400).json({
          success: false,
          error: 'browserId is required'
        });
      }

      const elements = await browserService.detectElements(browserId, selector);

      res.json({
        success: true,
        elements
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

