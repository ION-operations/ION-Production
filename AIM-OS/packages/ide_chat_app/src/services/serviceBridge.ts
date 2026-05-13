/**
 * Service Bridge - Unified API for Electron App
 * Routes requests to MCP (via Extension) or direct HTTP (via Daemon)
 * 
 * Priority: MCP via Extension > Direct HTTP > Fallback
 */

import { getMCPAPI } from './mcpApi'
import AIMOSService from './AIMOSService'

class ServiceBridge {
    private mcpApi = getMCPAPI()
    private aimosService = new AIMOSService()
    private useMCP: boolean = false

    /**
     * Initialize and check which service is available
     */
    async initialize(): Promise<void> {
        // Check if extension (MCP) is available
        this.useMCP = await this.mcpApi.checkExtension()
        
        if (this.useMCP) {
            console.log('[ServiceBridge] Using MCP via Extension')
        } else {
            console.log('[ServiceBridge] Using direct HTTP (daemon)')
        }
    }

    /**
     * Store memory - Uses MCP if available, otherwise HTTP
     */
    async storeMemory(content: string, tags: string[]): Promise<boolean> {
        try {
            if (this.useMCP) {
                const result = await this.mcpApi.storeMemory(content, tags)
                return result.success
            } else {
                await this.aimosService.storeMemory(content, tags)
                return true
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to store memory:', error)
            return false
        }
    }

    /**
     * Retrieve memory - Uses MCP if available, otherwise HTTP
     */
    async retrieveMemory(query: string, limit: number = 10): Promise<any[]> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.retrieveMemory(query, limit)
            } else {
                return await this.aimosService.retrieveMemory(query, limit)
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to retrieve memory:', error)
            return []
        }
    }

    /**
     * Get memory stats - Uses MCP if available, otherwise HTTP
     */
    async getMemoryStats(): Promise<any> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.getMemoryStats()
            } else {
                return await this.aimosService.getMemoryStats()
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to get memory stats:', error)
            return {}
        }
    }

    /**
     * Track confidence - Uses MCP if available, otherwise HTTP
     */
    async trackConfidence(task: string, confidence: number, reasoning?: string): Promise<boolean> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.trackConfidence(task, confidence, reasoning)
            } else {
                await this.aimosService.trackConfidence(task, confidence, reasoning)
                return true
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to track confidence:', error)
            return false
        }
    }

    /**
     * Create plan - Uses MCP if available, otherwise HTTP
     */
    async createPlan(goal: string, priority: string = 'medium'): Promise<any> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.createPlan(goal, priority)
            } else {
                return await this.aimosService.createPlan(goal, priority)
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to create plan:', error)
            return {}
        }
    }

    /**
     * Send AI message - Uses MCP (Extension only)
     */
    async sendAIMessage(toAI: string, content: string, messageType: string = 'discussion', priority: string = 'medium', threadId?: string): Promise<any> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.sendAIMessage(toAI, content, messageType, priority, threadId)
            } else {
                // Try HTTP fallback
                try {
                    return await this.aimosService.sendAIMessage(toAI, content, messageType as any, priority as any, threadId, false)
                } catch (httpError) {
                    console.warn('[ServiceBridge] HTTP fallback failed:', httpError)
                    return {}
                }
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to send AI message:', error)
            return {}
        }
    }

    /**
     * Get AI messages - Uses MCP (Extension only)
     */
    async getAIMessages(fromAI?: string, toAI?: string, threadId?: string, limit?: number): Promise<any[]> {
        try {
            console.log('[ServiceBridge] getAIMessages called:', { fromAI, toAI, threadId, limit, useMCP: this.useMCP });
            if (this.useMCP) {
                const result = await this.mcpApi.getAIMessages(fromAI, toAI, threadId, limit);
                console.log('[ServiceBridge] getAIMessages MCP result:', result?.length || 0, 'messages');
                return result;
            } else {
                // Try HTTP fallback
                try {
                    const result = await this.aimosService.getAIMessages(fromAI, toAI, threadId, limit);
                    console.log('[ServiceBridge] getAIMessages HTTP result:', result?.length || 0, 'messages');
                    return result;
                } catch (httpError) {
                    console.warn('[ServiceBridge] HTTP fallback failed:', httpError)
                    return []
                }
            }
        } catch (error) {
            console.error('[ServiceBridge] Failed to get AI messages:', error)
            return []
        }
    }

    /**
     * Get service status
     */
    getStatus(): { mcp: boolean; http: boolean } {
        return {
            mcp: this.useMCP,
            http: !this.useMCP // If MCP not available, HTTP is fallback
        }
    }

    // =============================================================================
    // Prompt Chain Methods (Phase 2 Implementation)
    // =============================================================================

    /**
     * Create prompt chain - Uses MCP if available
     */
    async createPromptChain(chain: {
        name: string
        description?: string
        nodes: any[]
        edges: any[]
        executionType?: string
        entryPoint?: string
        metadata?: any
    }, createdBy: string = 'user'): Promise<{ success: boolean; chain_id?: string; chain?: any; error?: string }> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.createPromptChain(chain)
            } else {
                // HTTP fallback not implemented yet
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to create prompt chain:', error)
            return { success: false, error: error.message || 'Failed to create prompt chain' }
        }
    }

    /**
     * Update prompt chain - Uses MCP if available
     */
    async updatePromptChain(
        chainId: string,
        updates: any,
        reason?: string,
        updatedBy?: string
    ): Promise<{ success: boolean; chain_id?: string; chain?: any; version?: number; error?: string }> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.updatePromptChain(chainId, updates, reason, updatedBy)
            } else {
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to update prompt chain:', error)
            return { success: false, error: error.message || 'Failed to update prompt chain' }
        }
    }

    /**
     * Get prompt chain - Uses MCP if available
     */
    async getPromptChain(chainId: string, version?: number): Promise<{ success: boolean; chain?: any; version?: number; error?: string }> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.getPromptChain(chainId, version)
            } else {
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to get prompt chain:', error)
            return { success: false, error: error.message || 'Failed to get prompt chain' }
        }
    }

    /**
     * List prompt chains - Uses MCP if available
     */
    async listPromptChains(filters?: {
        tags?: string[]
        category?: string
        isTemplate?: boolean
        createdBy?: string
    }, limit?: number): Promise<{ success: boolean; chains?: any[]; total?: number; error?: string }> {
        try {
            console.log('[ServiceBridge] listPromptChains called:', { filters, limit, useMCP: this.useMCP })
            if (this.useMCP) {
                const result = await this.mcpApi.listPromptChains(filters, limit)
                console.log('[ServiceBridge] listPromptChains MCP result:', result)
                return result
            } else {
                console.warn('[ServiceBridge] MCP not available for listPromptChains')
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to list prompt chains:', error)
            return { success: false, error: error.message || 'Failed to list prompt chains' }
        }
    }

    /**
     * Add chain node - Uses MCP if available
     */
    async addChainNode(
        chainId: string,
        node: any,
        connectTo?: string[],
        connectFrom?: string[]
    ): Promise<{ success: boolean; chain_id?: string; node_id?: string; chain?: any; error?: string }> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.addChainNode(chainId, node, connectTo, connectFrom)
            } else {
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to add chain node:', error)
            return { success: false, error: error.message || 'Failed to add chain node' }
        }
    }

    /**
     * Connect chain nodes - Uses MCP if available
     */
    async connectChainNodes(
        chainId: string,
        source: string,
        target: string,
        type?: string,
        condition?: string,
        dataMapping?: any
    ): Promise<{ success: boolean; chain_id?: string; edge_id?: string; chain?: any; error?: string }> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.connectChainNodes(chainId, source, target, type, condition, dataMapping)
            } else {
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to connect chain nodes:', error)
            return { success: false, error: error.message || 'Failed to connect chain nodes' }
        }
    }

    /**
     * Execute prompt chain - Uses MCP if available
     */
    async executePromptChain(
        chainId: string,
        inputs?: any,
        context?: any
    ): Promise<{ success: boolean; execution_id?: string; status?: string; error?: string }> {
        try {
            if (this.useMCP) {
                return await this.mcpApi.executePromptChain(chainId, inputs, context)
            } else {
                return { success: false, error: 'MCP not available' }
            }
        } catch (error: any) {
            console.error('[ServiceBridge] Failed to execute prompt chain:', error)
            return { success: false, error: error.message || 'Failed to execute prompt chain' }
        }
    }
}

// Singleton instance
let serviceBridgeInstance: ServiceBridge | null = null

export function getServiceBridge(): ServiceBridge {
    if (!serviceBridgeInstance) {
        serviceBridgeInstance = new ServiceBridge()
        // Initialize async (don't block)
        serviceBridgeInstance.initialize().catch(console.error)
    }
    return serviceBridgeInstance
}

export default ServiceBridge

