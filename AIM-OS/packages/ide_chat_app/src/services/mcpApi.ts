/**
 * MCP API Client for Electron App
 * Communicates with Extension via HTTP API to execute MCP tools
 */

export interface MCPToolRequest {
    tool: string;
    arguments?: any;
}

export interface MCPToolResponse {
    success: boolean;
    tool?: string;
    result?: any;
    error?: string;
}

export interface MCPTool {
    name: string;
    description?: string;
    inputSchema?: any;
}

export class MCPAPI {
    private baseUrl: string;
    private extensionAvailable: boolean = false;

    constructor(baseUrl: string = 'http://localhost:5001') {
        this.baseUrl = baseUrl;
    }

    /**
     * Check if extension command server is available
     */
    async checkExtension(): Promise<boolean> {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(1000)
            });
            this.extensionAvailable = response.ok;
            return this.extensionAvailable;
        } catch (error) {
            this.extensionAvailable = false;
            return false;
        }
    }

    /**
     * Execute an MCP tool via the extension
     */
    async executeTool(tool: string, args: any = {}): Promise<MCPToolResponse> {
        if (!this.extensionAvailable) {
            const available = await this.checkExtension();
            if (!available) {
                return {
                    success: false,
                    error: 'Extension command server not available. Is Cursor open with extension activated?'
                };
            }
        }

        try {
            const response = await fetch(`${this.baseUrl}/mcp/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tool,
                    arguments: args
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result: MCPToolResponse = await response.json();
            return result;
        } catch (error: any) {
            return {
                success: false,
                error: error.message || 'Failed to execute MCP tool'
            };
        }
    }

    /**
     * List available MCP tools
     */
    async listTools(): Promise<MCPTool[]> {
        if (!this.extensionAvailable) {
            const available = await this.checkExtension();
            if (!available) {
                return [];
            }
        }

        try {
            const response = await fetch(`${this.baseUrl}/mcp/list`, {
                method: 'GET',
                signal: AbortSignal.timeout(2000)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result.tools || [];
        } catch (error: any) {
            console.error('[MCPAPI] Failed to list tools:', error);
            return [];
        }
    }

    // ========================================
    // Convenience Methods for Common MCP Tools
    // ========================================

    /**
     * Store memory in CMC
     */
    async storeMemory(content: string, tags: string[]): Promise<MCPToolResponse> {
        return this.executeTool('store_memory', {
            content,
            tags: tags.reduce((acc, tag, index) => {
                acc[tag] = 0.5 + (index * 0.1);
                return acc;
            }, {} as Record<string, number>)
        });
    }

    /**
     * Retrieve memory from HHNI
     */
    async retrieveMemory(query: string, limit: number = 10): Promise<any[]> {
        const response = await this.executeTool('retrieve_memory', {
            query,
            limit
        });
        return response.success ? (response.result?.result || []) : [];
    }

    /**
     * Get memory statistics
     */
    async getMemoryStats(): Promise<any> {
        const response = await this.executeTool('get_memory_stats', {});
        return response.success ? (response.result?.result || {}) : {};
    }

    /**
     * Create execution plan via APOE
     */
    async createPlan(goal: string, priority: string = 'medium'): Promise<any> {
        const response = await this.executeTool('create_plan', {
            goal,
            priority
        });
        return response.success ? (response.result?.result || {}) : {};
    }

    /**
     * Track confidence via VIF
     */
    async trackConfidence(task: string, confidence: number, reasoning?: string): Promise<boolean> {
        const response = await this.executeTool('track_confidence', {
            task,
            confidence,
            reasoning
        });
        return response.success;
    }

    /**
     * Synthesize knowledge via SEG
     */
    async synthesizeKnowledge(topics: string[]): Promise<any> {
        const response = await this.executeTool('synthesize_knowledge', {
            topics
        });
        return response.success ? (response.result?.result || {}) : {};
    }

    /**
     * Send message to another AI
     */
    async sendAIMessage(toAI: string, content: string, messageType: string = 'discussion', priority: string = 'medium', threadId?: string): Promise<any> {
        const args: any = {
            from_ai: 'electron-app',
            to_ai: toAI,
            content,
            message_type: messageType,
            priority
        };
        if (threadId) args.thread_id = threadId;
        
        const response = await this.executeTool('send_ai_message', args);
        
        // MCP client now parses JSON from content[0].text, so response.result IS the tool result
        // Command server wraps it: {success: true, tool: 'send_ai_message', result: {success: true, message_id: ...}}
        if (response.success && response.result) {
            // response.result is the actual tool result (from MCP server)
            return response.result;
        }
        
        return {};
    }

    /**
     * Get AI messages
     */
    async getAIMessages(fromAI?: string, toAI?: string, threadId?: string, limit?: number): Promise<any[]> {
        const args: any = {};
        if (fromAI) args.from_ai = fromAI;
        if (toAI) args.to_ai = toAI;
        if (threadId) args.thread_id = threadId;
        if (limit) args.limit = limit;
        
        console.log('[MCPAPI] getAIMessages called with args:', { fromAI, toAI, threadId, limit, args });
        
        const response = await this.executeTool('get_ai_messages', args);
        
        console.log('[MCPAPI] getAIMessages response:', response);
        
        // MCP server returns: {success: true, messages: [...], count: ...}
        // Command server wraps it: {success: true, tool: 'get_ai_messages', result: {success: true, messages: [...], count: ...}}
        if (response.success && response.result) {
            // Check if result has messages directly (MCP server format)
            if (response.result.messages && Array.isArray(response.result.messages)) {
                console.log('[MCPAPI] getAIMessages returning', response.result.messages.length, 'messages from result.messages');
                return response.result.messages;
            }
            // Check if result has result.messages (nested format)
            if (response.result.result && response.result.result.messages && Array.isArray(response.result.result.messages)) {
                console.log('[MCPAPI] getAIMessages returning', response.result.result.messages.length, 'messages from result.result.messages');
                return response.result.result.messages;
            }
            // Fallback: if result is an array, return it
            if (Array.isArray(response.result)) {
                console.log('[MCPAPI] getAIMessages returning', response.result.length, 'messages from result array');
                return response.result;
            }
        }
        
        console.warn('[MCPAPI] getAIMessages: Unexpected response format', response);
        return [];
    }

    /**
     * Start AI discussion thread
     */
    async startAIDiscussion(toAI: string, topic: string, initialMessage: string): Promise<any> {
        const response = await this.executeTool('start_ai_discussion', {
            from_ai: 'electron-app',
            to_ai: toAI,
            topic,
            initial_message: initialMessage
        });
        return response.success ? (response.result?.result || {}) : {};
    }

    /**
     * Get AI collaboration summary
     */
    async getAICollaborationSummary(): Promise<any> {
        const response = await this.executeTool('get_ai_collaboration_summary', {});
        return response.success ? (response.result?.result || {}) : {};
    }

    // =============================================================================
    // Prompt Chain Methods (Phase 2 Implementation)
    // =============================================================================

    /**
     * Create prompt chain
     */
    async createPromptChain(chain: {
        name: string
        description?: string
        nodes: any[]
        edges: any[]
        executionType?: string
        entryPoint?: string
        metadata?: any
    }): Promise<{ success: boolean; chain_id?: string; chain?: any; error?: string }> {
        const result = await this.executeTool('create_prompt_chain', {
            name: chain.name,
            description: chain.description,
            nodes: chain.nodes,
            edges: chain.edges,
            executionType: chain.executionType || 'sequential',
            entryPoint: chain.entryPoint,
            metadata: chain.metadata,
            created_by: 'user' // Could be 'ai' if created by AI
        });

        if (result.success && result.result) {
            return {
                success: result.result.success || false,
                chain_id: result.result.chain_id,
                chain: result.result.chain,
                error: result.result.error
            };
        }
        return { success: false, error: result.error || 'Failed to create prompt chain' };
    }

    /**
     * Update prompt chain
     */
    async updatePromptChain(
        chainId: string,
        updates: any,
        reason?: string,
        updatedBy?: string
    ): Promise<{ success: boolean; chain_id?: string; chain?: any; version?: number; error?: string }> {
        const result = await this.executeTool('update_prompt_chain', {
            chain_id: chainId,
            updates,
            reason: reason || 'Chain updated',
            updated_by: updatedBy || 'user'
        });

        if (result.success && result.result) {
            return {
                success: result.result.success || false,
                chain_id: result.result.chain_id,
                chain: result.result.chain,
                version: result.result.version,
                error: result.result.error
            };
        }
        return { success: false, error: result.error || 'Failed to update prompt chain' };
    }

    /**
     * Get prompt chain
     */
    async getPromptChain(chainId: string, version?: number): Promise<{ success: boolean; chain?: any; version?: number; error?: string }> {
        const result = await this.executeTool('get_prompt_chain', {
            chain_id: chainId,
            version
        });

        if (result.success && result.result) {
            return {
                success: result.result.success || false,
                chain: result.result.chain,
                version: result.result.version,
                error: result.result.error
            };
        }
        return { success: false, error: result.error || 'Failed to get prompt chain' };
    }

    /**
     * List prompt chains
     */
    async listPromptChains(filters?: {
        tags?: string[]
        category?: string
        isTemplate?: boolean
        createdBy?: string
    }, limit?: number): Promise<{ success: boolean; chains?: any[]; total?: number; error?: string }> {
        console.log('[MCPAPI] listPromptChains called:', { filters, limit })
        const result = await this.executeTool('list_prompt_chains', {
            filters: filters || {},
            limit: limit || 50
        });
        console.log('[MCPAPI] listPromptChains executeTool result:', result)

        if (result.success && result.result) {
            // Extension wraps MCP response: {success: true, tool: 'list_prompt_chains', result: {success: true, chains: [...], total: ...}}
            // result.result is already the parsed tool result from JSON-RPC content[0].text
            let parsedResult = result.result;
            
            // Handle case where result might be a JSON string
            if (typeof parsedResult === 'string') {
                try {
                    parsedResult = JSON.parse(parsedResult);
                } catch (e) {
                    console.error('[MCPAPI] Failed to parse result as JSON:', e);
                    return { success: false, error: 'Invalid JSON response from MCP server' };
                }
            }
            
            // Handle nested result structure (if Extension wraps it again)
            if (parsedResult.result && typeof parsedResult.result === 'object') {
                parsedResult = parsedResult.result;
            }
            
            console.log('[MCPAPI] listPromptChains parsed result:', parsedResult)
            
            return {
                success: parsedResult.success !== false, // Default to true if not explicitly false
                chains: parsedResult.chains || [],
                total: parsedResult.total || (parsedResult.chains ? parsedResult.chains.length : 0),
                error: parsedResult.error
            };
        }
        console.error('[MCPAPI] listPromptChains failed:', result.error)
        return { success: false, error: result.error || 'Failed to list prompt chains' };
    }

    /**
     * Add chain node
     */
    async addChainNode(
        chainId: string,
        node: any,
        connectTo?: string[],
        connectFrom?: string[]
    ): Promise<{ success: boolean; chain_id?: string; node_id?: string; chain?: any; error?: string }> {
        const result = await this.executeTool('add_chain_node', {
            chain_id: chainId,
            node,
            connectTo: connectTo || [],
            connectFrom: connectFrom || []
        });

        if (result.success && result.result) {
            return {
                success: result.result.success || false,
                chain_id: result.result.chain_id,
                node_id: result.result.node_id,
                chain: result.result.chain,
                error: result.result.error
            };
        }
        return { success: false, error: result.error || 'Failed to add chain node' };
    }

    /**
     * Connect chain nodes
     */
    async connectChainNodes(
        chainId: string,
        source: string,
        target: string,
        type?: string,
        condition?: string,
        dataMapping?: any
    ): Promise<{ success: boolean; chain_id?: string; edge_id?: string; chain?: any; error?: string }> {
        const result = await this.executeTool('connect_chain_nodes', {
            chain_id: chainId,
            source,
            target,
            type: type || 'sequential',
            condition,
            dataMapping
        });

        if (result.success && result.result) {
            return {
                success: result.result.success || false,
                chain_id: result.result.chain_id,
                edge_id: result.result.edge_id,
                chain: result.result.chain,
                error: result.result.error
            };
        }
        return { success: false, error: result.error || 'Failed to connect chain nodes' };
    }

    /**
     * Execute prompt chain
     */
    async executePromptChain(
        chainId: string,
        inputs?: any,
        context?: any
    ): Promise<{ success: boolean; execution_id?: string; status?: string; error?: string }> {
        const result = await this.executeTool('execute_prompt_chain', {
            chain_id: chainId,
            inputs: inputs || {},
            context: context || {}
        });

        if (result.success && result.result) {
            return {
                success: result.result.success || false,
                execution_id: result.result.execution_id,
                status: result.result.status,
                error: result.result.error
            };
        }
        return { success: false, error: result.error || 'Failed to execute prompt chain' };
    }
}

// Singleton instance
let mcpApiInstance: MCPAPI | null = null;

export function getMCPAPI(): MCPAPI {
    if (!mcpApiInstance) {
        mcpApiInstance = new MCPAPI();
    }
    return mcpApiInstance;
}

