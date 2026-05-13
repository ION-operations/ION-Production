/**
 * Sandbox Backend API Design
 * API specification for Docker container sandbox management
 * For integration with Command Server (port 5001)
 */

/**
 * Sandbox API Endpoints
 * All endpoints are under /sandbox prefix
 * Base URL: http://localhost:5001/sandbox
 */

// ===== ENDPOINT SPECIFICATIONS =====

/**
 * POST /sandbox/create
 * Create a new sandbox container
 * 
 * Request:
 * {
 *   language: string,        // 'python', 'javascript', 'typescript', etc.
 *   code: string,            // Code to execute
 *   timeout?: number,        // Timeout in ms (default: 30000)
 *   memory?: number,         // Memory limit in MB (default: 512)
 *   cpu?: number,            // CPU limit as fraction (default: 0.5)
 *   network?: 'none' | 'localhost',  // Network mode (default: 'none')
 *   workspace?: string       // Workspace path (optional)
 * }
 * 
 * Response:
 * {
 *   success: boolean,
 *   containerId?: string,
 *   error?: string
 * }
 */

/**
 * POST /sandbox/execute
 * Execute code in existing container
 * 
 * Request:
 * {
 *   containerId: string,
 *   code: string,
 *   input?: string           // stdin input (optional)
 * }
 * 
 * Response:
 * {
 *   success: boolean,
 *   result?: {
 *     stdout: string,
 *     stderr: string,
 *     exitCode: number,
 *     executionTime: number,  // milliseconds
 *     resourceUsage: {
 *       cpu: number,          // percentage
 *       memory: number,       // MB
 *       time: number          // milliseconds
 *     }
 *   },
 *   error?: string
 * }
 */

/**
 * POST /sandbox/destroy
 * Destroy a sandbox container
 * 
 * Request:
 * {
 *   containerId: string
 * }
 * 
 * Response:
 * {
 *   success: boolean,
 *   error?: string
 * }
 */

/**
 * GET /sandbox/status/:containerId
 * Get container status
 * 
 * Response:
 * {
 *   success: boolean,
 *   status?: {
 *     containerId: string,
 *     status: 'created' | 'running' | 'completed' | 'failed' | 'destroyed',
 *     createdAt?: string,
 *     completedAt?: string
 *   },
 *   error?: string
 * }
 */

/**
 * POST /sandbox/execute-code
 * Convenience endpoint: Create, execute, and destroy in one call
 * 
 * Request:
 * {
 *   language: string,
 *   code: string,
 *   timeout?: number,
 *   memory?: number,
 *   cpu?: number,
 *   network?: 'none' | 'localhost',
 *   input?: string
 * }
 * 
 * Response:
 * {
 *   success: boolean,
 *   result?: {
 *     stdout: string,
 *     stderr: string,
 *     exitCode: number,
 *     executionTime: number,
 *     resourceUsage: {
 *       cpu: number,
 *       memory: number,
 *       time: number
 *     }
 *   },
 *   error?: string
 * }
 */

// ===== IMPLEMENTATION NOTES =====

/**
 * Command Server Integration
 * 
 * To add sandbox endpoints to Command Server:
 * 
 * 1. Add route handlers in commandServer.ts handleRequest method:
 * 
 *    if (pathname === '/sandbox/create') {
 *      const result = await this.handleSandboxCreate(req);
 *      this.sendSuccess(res, result);
 *      return;
 *    }
 * 
 *    if (pathname === '/sandbox/execute') {
 *      const result = await this.handleSandboxExecute(req);
 *      this.sendSuccess(res, result);
 *      return;
 *    }
 * 
 *    // ... etc
 * 
 * 2. Implement handler methods:
 * 
 *    private async handleSandboxCreate(req: http.IncomingMessage): Promise<any> {
 *      const body = await this.readRequestBody(req);
 *      const { language, code, timeout, memory, cpu, network, workspace } = JSON.parse(body);
 *      
 *      // Use Docker API or dockerode library to create container
 *      // Return { success: true, containerId: '...' }
 *    }
 * 
 * 3. Docker Integration:
 *    - Use dockerode library (npm install dockerode)
 *    - Or use Docker API directly (http://localhost:2375)
 *    - Or spawn docker CLI commands
 * 
 * 4. Security:
 *    - Validate all inputs
 *    - Enforce resource limits
 *    - Isolate containers completely
 *    - Clean up containers after execution
 */

/**
 * Alternative: MCP Tool Approach
 * 
 * Instead of direct Command Server endpoints, could create MCP tools:
 * 
 * - mcp_lucid-mcp_create_sandbox
 * - mcp_lucid-mcp_execute_in_sandbox
 * - mcp_lucid-mcp_destroy_sandbox
 * 
 * Then Nova's SandboxService would use MCPService.executeTool() instead of direct HTTP calls.
 * 
 * This approach:
 * - ✅ Consistent with other AIM-OS integrations
 * - ✅ Uses existing MCPService infrastructure
 * - ✅ Easier to implement (add to Python MCP server)
 * - ✅ Better error handling via MCPService
 */

