import * as vscode from 'vscode';
import { AIMOSLogger } from './utils/logger';

/**
 * AIMOS Chat Participant
 * 
 * Creates a chat participant (@aimos) that users can invoke in Cursor chat.
 * Routes requests to Command Server which integrates with MCP tools.
 * 
 * Usage: User types "@aimos help me refactor this code" in Cursor chat
 */
export class AIMOSChatParticipant {
    private static participant: vscode.ChatParticipant | null = null;
    private static commandServerUrl: string = 'http://localhost:5001';

    /**
     * Register the AIMOS chat participant
     */
    public static register(context: vscode.ExtensionContext): void {
        try {
            // Check if Chat API is available
            if (!vscode.chat || typeof vscode.chat.createChatParticipant !== 'function') {
                AIMOSLogger.warn('CHAT_PARTICIPANT', 'Chat API not available in this VS Code version');
                vscode.window.showWarningMessage('Chat API not available. Chat participant not registered.');
                return;
            }

            AIMOSLogger.log('CHAT_PARTICIPANT', 'Registering AIMOS chat participant...');

            // Create chat participant
            this.participant = vscode.chat.createChatParticipant('aimos.assistant', async (
                request: vscode.ChatRequest,
                context: vscode.ChatContext,
                stream: vscode.ChatResponseStream,
                token: vscode.CancellationToken
            ) => {
                return this.handleChatRequest(request, context, stream, token);
            });

            // Set description and icon
            this.participant.name = 'AIMOS';
            this.participant.description = 'AIMOS: Multi-agent AI orchestration and consciousness system. Commands: search-memory, store-memory, create-plan, track-confidence, memory-stats';
            
            // Try to add command provider if available (may not exist in all VS Code versions)
            try {
                if ('commandProvider' in this.participant) {
                    (this.participant as any).commandProvider = {
                        provideCommands: async (token: vscode.CancellationToken) => {
                            return [
                                {
                                    name: 'search-memory',
                                    description: 'Search AIMOS memory for information',
                                },
                                {
                                    name: 'store-memory',
                                    description: 'Store information in AIMOS memory',
                                },
                                {
                                    name: 'create-plan',
                                    description: 'Create an execution plan',
                                },
                                {
                                    name: 'track-confidence',
                                    description: 'Track confidence for a task',
                                },
                                {
                                    name: 'memory-stats',
                                    description: 'Show memory statistics',
                                },
                                {
                                    name: 'synthesize-knowledge',
                                    description: 'Synthesize knowledge from multiple sources',
                                },
                            ];
                        }
                    };
                    AIMOSLogger.success('CHAT_PARTICIPANT', 'Command provider registered');
                }
            } catch (error) {
                AIMOSLogger.warn('CHAT_PARTICIPANT', 'Command provider not available in this VS Code version', error);
            }
            
            // Add follow-up provider for better UX
            this.participant.followupProvider = {
                provideFollowups: async (result: vscode.ChatResponseFragment[], context: vscode.ChatContext) => {
                    return [
                        {
                            message: 'Store this in memory',
                            prompt: 'Store this information in AIMOS memory',
                            label: '💾 Store in Memory'
                        },
                        {
                            message: 'Create a plan',
                            prompt: 'Create an execution plan for this task',
                            label: '📋 Create Plan'
                        },
                        {
                            message: 'Search memory',
                            prompt: 'Search AIMOS memory for related information',
                            label: '🔍 Search Memory'
                        }
                    ];
                }
            };

            context.subscriptions.push(this.participant);
            AIMOSLogger.success('CHAT_PARTICIPANT', 'AIMOS chat participant registered successfully');
            vscode.window.showInformationMessage('✅ AIMOS chat participant registered! Use @aimos in chat.');

        } catch (error: any) {
            AIMOSLogger.error('CHAT_PARTICIPANT', 'Failed to register chat participant', error);
            vscode.window.showErrorMessage(`Failed to register AIMOS chat participant: ${error.message}`);
        }
    }

    /**
     * Handle incoming chat requests
     */
    private static async handleChatRequest(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        try {
            AIMOSLogger.log('CHAT_PARTICIPANT', `Handling chat request: ${request.prompt.substring(0, 50)}...`);

            // Show progress
            stream.progress('Processing with AIMOS...');

            // Prepare request payload
            const payload = {
                prompt: request.prompt,
                references: request.references?.map(ref => ({
                    name: ref.name,
                    uri: ref.uri.toString()
                })) || [],
                command: request.command,
                variables: request.variables || {}
            };

            // Check if prompt contains command patterns and route accordingly
            const promptLower = request.prompt.toLowerCase();
            if (promptLower.includes('search') && promptLower.includes('memory')) {
                payload.command = 'mcp:mcp_lucid-mcp_retrieve_memory';
            } else if (promptLower.includes('store') && promptLower.includes('memory')) {
                payload.command = 'mcp:mcp_lucid-mcp_store_memory';
            } else if (promptLower.includes('create') && promptLower.includes('plan')) {
                payload.command = 'mcp:mcp_lucid-mcp_create_plan';
            } else if (promptLower.includes('track') && promptLower.includes('confidence')) {
                payload.command = 'mcp:mcp_lucid-mcp_track_confidence';
            } else if (promptLower.includes('memory') && promptLower.includes('stat')) {
                payload.command = 'mcp:mcp_lucid-mcp_get_memory_stats';
            }

            // Send request to Command Server
            const response = await fetch(`${this.commandServerUrl}/aimos/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
                signal: token ? AbortSignal.timeout(300000) : undefined // 5 minute timeout
            });

            if (!response.ok) {
                throw new Error(`Command Server error: ${response.status} ${response.statusText}`);
            }

            // Check if response is streaming
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/event-stream')) {
                // Stream response
                const reader = response.body?.getReader();
                const decoder = new TextDecoder();

                if (reader) {
                    while (true) {
                        if (token.isCancellationRequested) {
                            reader.cancel();
                            break;
                        }

                        const { done, value } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value, { stream: true });
                        stream.markdown(chunk);
                    }
                }
            } else {
                // Non-streaming response
                const data = await response.json();
                
                if (data.error) {
                    stream.markdown(`❌ **Error:** ${data.error}`);
                    AIMOSLogger.error('CHAT_PARTICIPANT', 'Command Server returned error', data.error);
                } else if (data.response) {
                    stream.markdown(data.response);
                } else if (data.message) {
                    stream.markdown(data.message);
                } else {
                    stream.markdown(JSON.stringify(data, null, 2));
                }
            }

            AIMOSLogger.success('CHAT_PARTICIPANT', 'Chat request processed successfully');

        } catch (error: any) {
            AIMOSLogger.error('CHAT_PARTICIPANT', 'Failed to handle chat request', error);
            
            if (error.name === 'AbortError' || token.isCancellationRequested) {
                stream.markdown('⚠️ Request cancelled.');
            } else {
                stream.markdown(`❌ **Error:** ${error.message}\n\nPlease check that the Command Server is running on port 5001.`);
            }
        }
    }

    /**
     * Set Command Server URL (for testing)
     */
    public static setCommandServerUrl(url: string): void {
        this.commandServerUrl = url;
    }
}

