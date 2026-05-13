// Enhanced Main Chat Panel - Max V2
// AIM-OS integration: CMC-backed messages, HHNI semantic search, VIF confidence tracking

import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Search, Shield, Database, Network } from 'lucide-react';
import { useAIMOS } from '../../hooks/useAIMOS';
import { ConfidenceIndicator } from '../ConfidenceIndicator/ConfidenceIndicator';
import { PanelLoading } from '../Loading/Loading';
import { mockChatMessages } from '../../mockData/mockData';
import './MainChatPanel.css';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  codeBlocks?: string[];
  
  // AIM-OS Integration
  cmcAtomId?: string;
  hhniResults?: any[];
  vifConfidence?: number;
  witnessId?: string;
  evidenceTrail?: any[];
}

export const MainChatPanel: React.FC = () => {
  const { cmc, hhni, vif, loading, errors } = useAIMOS();
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages);
  const [inputValue, setInputValue] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}_user`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    // Store user message in CMC
    try {
      const atomResult = await cmc.storeAtom({
        modality: 'text',
        content: {
          inline: inputValue,
          media_type: 'text/plain',
        },
        metadata: {
          message_id: userMessage.id,
          role: 'user',
          agent: 'max',
        },
        tags: { chat_message: 1, user: 1 },
      });
      userMessage.cmcAtomId = atomResult.id;
    } catch (error) {
      console.error('[MAX] Failed to store user message in CMC:', error);
    }

    // Search HHNI for relevant context
    setIsSearching(true);
    try {
      const hhniResults = await hhni.search(inputValue, 'paragraph');
      userMessage.hhniResults = hhniResults.slice(0, 3); // Top 3 results
    } catch (error) {
      console.error('[MAX] Failed to search HHNI:', error);
    }
    setIsSearching(false);

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    // Simulate assistant response (in real implementation, this would call AI)
    setTimeout(async () => {
      const assistantMessage: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: `I understand you're asking about: "${inputValue}". Based on the codebase context, here's what I found...`,
        timestamp: new Date().toISOString(),
      };

      // Store assistant message in CMC
      try {
        const atomResult = await cmc.storeAtom({
          modality: 'text',
          content: {
            inline: assistantMessage.content,
            media_type: 'text/plain',
          },
          metadata: {
            message_id: assistantMessage.id,
            role: 'assistant',
            agent: 'max',
            in_reply_to: userMessage.id,
          },
          tags: { chat_message: 1, assistant: 1 },
        });
        assistantMessage.cmcAtomId = atomResult.id;

        // Track confidence with VIF
        const confidence = 0.85; // Mock confidence
        const witnessResult = await vif.trackConfidence({
          model_id: 'max-v2',
          prompt_hash: userMessage.cmcAtomId || '',
          confidence_score: confidence,
          confidence_band: confidence >= 0.90 ? 'A' : confidence >= 0.80 ? 'B' : 'C',
        });
        assistantMessage.vifConfidence = confidence;
        assistantMessage.witnessId = witnessResult.id;
      } catch (error) {
        console.error('[MAX] Failed to store assistant message:', error);
      }

      setMessages((prev) => [...prev, assistantMessage]);
    }, 500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) {
    return <PanelLoading message="Loading chat..." />;
  }

  if (errors.length > 0) {
    return (
      <div className="chat-panel error">
        <div className="error-message">
          <p>Error loading chat:</p>
          <ul>
            {errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span className="chat-title">Main Chat</span>
        <span className="chat-subtitle">AI Assistant</span>
        {isSearching && (
          <span className="chat-search-indicator">
            <Search size={12} /> Searching context...
          </span>
        )}
      </div>
      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.role === 'user' ? 'user' : 'assistant'}`}
          >
            <div className="chat-message-avatar">
              {message.role === 'user' ? (
                <User size={16} />
              ) : (
                <Bot size={16} />
              )}
            </div>
            <div className="chat-message-content">
              <div className="chat-message-text">{message.content}</div>
              {message.codeBlocks && message.codeBlocks.length > 0 && (
                <div className="chat-message-code">
                  <pre>
                    <code>{message.codeBlocks[0]}</code>
                  </pre>
                </div>
              )}
              
              {/* AIM-OS Integration Indicators */}
              {message.role === 'assistant' && (
                <div className="chat-message-aimos">
                  {message.vifConfidence !== undefined && (
                    <div className="chat-message-confidence">
                      <ConfidenceIndicator confidence={message.vifConfidence} size="sm" />
                    </div>
                  )}
                  {message.cmcAtomId && (
                    <div className="chat-message-cmc" title={`CMC Atom: ${message.cmcAtomId}`}>
                      <Database size={12} />
                      <span>CMC</span>
                    </div>
                  )}
                  {message.witnessId && (
                    <div className="chat-message-witness" title={`VIF Witness: ${message.witnessId}`}>
                      <Shield size={12} />
                      <span>VIF</span>
                    </div>
                  )}
                  {message.hhniResults && message.hhniResults.length > 0 && (
                    <div className="chat-message-hhni" title={`${message.hhniResults.length} HHNI results`}>
                      <Network size={12} />
                      <span>HHNI ({message.hhniResults.length})</span>
                    </div>
                  )}
                </div>
              )}
              
              <div className="chat-message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-container">
        <textarea
          className="chat-input"
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={1}
          disabled={isSearching}
        />
        <button 
          className="chat-send-button" 
          onClick={handleSend}
          disabled={isSearching || !inputValue.trim()}
        >
          {isSearching ? <Search size={16} /> : <Send size={16} />}
        </button>
      </div>
    </div>
  );
};

