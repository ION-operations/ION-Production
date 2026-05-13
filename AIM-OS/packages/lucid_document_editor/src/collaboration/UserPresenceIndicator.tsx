/**
 * LUCID Document Editor - User Presence Indicator
 * 
 * Component showing active users in collaborative editing
 */

import React from 'react';
import { UserPresence } from './collaboration-engine';
import { Users } from 'lucide-react';

export interface UserPresenceIndicatorProps {
  users: UserPresence[];
  maxVisible?: number;
}

export const UserPresenceIndicator: React.FC<UserPresenceIndicatorProps> = ({
  users,
  maxVisible = 5,
}) => {
  const visibleUsers = users.slice(0, maxVisible);
  const remainingCount = Math.max(0, users.length - maxVisible);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '4px 8px' }}>
      <Users size={16} />
      <div style={{ display: 'flex', gap: '4px' }}>
        {visibleUsers.map((user) => (
          <div
            key={user.userId}
            style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              backgroundColor: user.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '10px',
              fontWeight: 'bold',
              cursor: 'pointer',
              border: '2px solid white',
            }}
            title={user.userName}
          >
            {user.userName.charAt(0).toUpperCase()}
          </div>
        ))}
        {remainingCount > 0 && (
          <div
            style={{
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              backgroundColor: '#ccc',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '10px',
              fontWeight: 'bold',
            }}
            title={`${remainingCount} more user${remainingCount !== 1 ? 's' : ''}`}
          >
            +{remainingCount}
          </div>
        )}
      </div>
      <span style={{ fontSize: '12px', color: '#666' }}>
        {users.length} active
      </span>
    </div>
  );
};

