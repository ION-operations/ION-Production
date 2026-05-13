/**
 * LUCID Document Editor - Comment Panel
 * 
 * UI component for managing comments
 */

import React, { useState } from 'react';
import { CommentManager, CommentThread } from './comment-system';
import { MessageSquare, Check } from 'lucide-react';

export interface CommentPanelProps {
  sectionId: string;
  commentManager: CommentManager;
  currentUserId: string;
  onCommentClick?: (thread: CommentThread) => void;
}

export const CommentPanel: React.FC<CommentPanelProps> = ({
  sectionId,
  commentManager,
  currentUserId,
  onCommentClick,
}) => {
  const [showResolved, setShowResolved] = useState(false);
  const threads = commentManager.getThreadsForSection(sectionId, showResolved);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ padding: '8px', borderBottom: '1px solid #ccc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageSquare size={16} />
          <span style={{ fontWeight: 'bold' }}>Comments</span>
          <span style={{ fontSize: '12px', color: '#666' }}>
            ({threads.length})
          </span>
        </div>
        <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <input
            type="checkbox"
            checked={showResolved}
            onChange={(e) => setShowResolved(e.target.checked)}
          />
          Show resolved
        </label>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '8px' }}>
        {threads.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '16px', color: '#666' }}>
            No comments
          </div>
        ) : (
          threads.map((thread) => (
            <div
              key={thread.id}
              style={{
                padding: '8px',
                marginBottom: '8px',
                backgroundColor: thread.resolved ? '#f0f0f0' : '#f5f5f5',
                borderRadius: '4px',
                opacity: thread.resolved ? 0.6 : 1,
                cursor: 'pointer',
              }}
              onClick={() => onCommentClick?.(thread)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '4px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 'bold', fontSize: '12px', marginBottom: '4px' }}>
                    {thread.comments[0].authorName}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {thread.comments[0].content}
                  </div>
                  {thread.comments.length > 1 && (
                    <div style={{ fontSize: '11px', color: '#999', marginTop: '4px' }}>
                      {thread.comments.length - 1} repl{thread.comments.length - 1 !== 1 ? 'ies' : 'y'}
                    </div>
                  )}
                </div>
                {thread.resolved && (
                  <Check size={14} style={{ color: '#4caf50' }} />
                )}
              </div>
              <div style={{ fontSize: '11px', color: '#999' }}>
                {new Date(thread.createdAt).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

