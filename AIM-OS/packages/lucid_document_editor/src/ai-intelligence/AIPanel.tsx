/**
 * LUCID Document Editor - AI Intelligence UI Components
 * 
 * React components for AI intelligence features
 */

import React, { useState, useEffect } from 'react';
import { useDocumentStore } from '../store';
import { AIIntelligenceService, TagSuggestion, ContentSuggestion, CitationSuggestion } from './ai-intelligence-service';
import { Sparkles, Tag, Lightbulb, BookOpen } from 'lucide-react';

export interface AIPanelProps {
  documentId: string;
  hhniEndpoint?: string;
  apiKey?: string;
}

export const AIPanel: React.FC<AIPanelProps> = ({ documentId, hhniEndpoint, apiKey }) => {
  const { document } = useDocumentStore();
  const [aiService] = useState(() => new AIIntelligenceService({ hhniEndpoint, apiKey }));
  const [activeTab, setActiveTab] = useState<'tags' | 'suggestions' | 'citations'>('tags');
  const [tagSuggestions, setTagSuggestions] = useState<TagSuggestion[]>([]);
  const [contentSuggestions, setContentSuggestions] = useState<ContentSuggestion[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSuggestions();
  }, [document]);

  const loadSuggestions = async () => {
    setLoading(true);
    try {
      const tags = await aiService.suggestTags(document, 0.7);
      setTagSuggestions(tags);

      const analysis = await aiService.analyzeDocument(document);
      setContentSuggestions(analysis.suggestions);
    } catch (error) {
      console.error('Failed to load AI suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyTag = async (tag: TagSuggestion) => {
    // TODO: Apply tag to document
    console.log('Applying tag:', tag);
  };

  return (
    <div style={{ width: '300px', borderLeft: '1px solid #ccc', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{ padding: '8px', borderBottom: '1px solid #ccc', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Sparkles size={16} />
        <span style={{ fontWeight: 'bold' }}>AI Intelligence</span>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #ccc' }}>
        <button
          onClick={() => setActiveTab('tags')}
          style={{
            flex: 1,
            padding: '8px',
            border: 'none',
            backgroundColor: activeTab === 'tags' ? '#e0e0e0' : 'transparent',
            cursor: 'pointer',
          }}
        >
          <Tag size={14} /> Tags
        </button>
        <button
          onClick={() => setActiveTab('suggestions')}
          style={{
            flex: 1,
            padding: '8px',
            border: 'none',
            backgroundColor: activeTab === 'suggestions' ? '#e0e0e0' : 'transparent',
            cursor: 'pointer',
          }}
        >
          <Lightbulb size={14} /> Suggestions
        </button>
        <button
          onClick={() => setActiveTab('citations')}
          style={{
            flex: 1,
            padding: '8px',
            border: 'none',
            backgroundColor: activeTab === 'citations' ? '#e0e0e0' : 'transparent',
            cursor: 'pointer',
          }}
        >
          <BookOpen size={14} /> Citations
        </button>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '16px', color: '#666' }}>Loading...</div>
        ) : (
          <>
            {activeTab === 'tags' && (
              <div>
                <h4 style={{ marginBottom: '8px' }}>Suggested Tags</h4>
                {tagSuggestions.map((tag, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '8px',
                      marginBottom: '4px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '4px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{tag.name}</div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        {tag.category} • {Math.round(tag.confidence * 100)}% confidence
                      </div>
                    </div>
                    <button
                      onClick={() => handleApplyTag(tag)}
                      style={{
                        padding: '4px 8px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                      }}
                    >
                      Apply
                    </button>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'suggestions' && (
              <div>
                <h4 style={{ marginBottom: '8px' }}>Content Suggestions</h4>
                {contentSuggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '8px',
                      marginBottom: '4px',
                      backgroundColor: '#f5f5f5',
                      borderRadius: '4px',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                      {suggestion.type.replace('-', ' ')}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                      {suggestion.reason}
                    </div>
                    <div style={{ fontSize: '11px', color: '#999' }}>
                      {Math.round(suggestion.confidence * 100)}% confidence
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'citations' && (
              <div>
                <h4 style={{ marginBottom: '8px' }}>Citation Search</h4>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  Citation search coming soon...
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

