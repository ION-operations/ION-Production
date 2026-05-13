// Bitemporal Time Travel Component - Max V2
// UI component for time-travel queries and state restoration

import React, { useState } from 'react';
import { Clock, RotateCcw, Calendar } from 'lucide-react';
import './BitemporalTimeTravel.css';

export interface BitemporalTimeTravelProps {
  currentTime: string | null;
  onTimeChange: (timestamp: string | null) => void;
  onRestore?: (timestamp: string) => void;
  className?: string;
}

export const BitemporalTimeTravel: React.FC<BitemporalTimeTravelProps> = ({
  currentTime,
  onTimeChange,
  onRestore,
  className = '',
}) => {
  const [timeInput, setTimeInput] = useState('');
  const [showTimePicker, setShowTimePicker] = useState(false);

  const handleSetTime = () => {
    if (timeInput) {
      const timestamp = new Date(timeInput).toISOString();
      if (!isNaN(new Date(timeInput).getTime())) {
        onTimeChange(timestamp);
        setTimeInput('');
        setShowTimePicker(false);
      }
    }
  };

  const handleReset = () => {
    onTimeChange(null);
    setTimeInput('');
    setShowTimePicker(false);
  };

  const handleRestore = () => {
    if (currentTime && onRestore) {
      onRestore(currentTime);
    }
  };

  return (
    <div className={`bitemporal-time-travel ${className}`} role="group" aria-label="Bitemporal time travel">
      <div className="time-travel-header">
        <Clock className="time-travel-icon" />
        <span className="time-travel-label">Time Travel</span>
        {currentTime && (
          <span className="time-travel-active">
            Viewing: {new Date(currentTime).toLocaleString()}
          </span>
        )}
      </div>
      
      <div className="time-travel-controls">
        <button
          onClick={() => setShowTimePicker(!showTimePicker)}
          className="time-travel-button"
          aria-label="Toggle time picker"
        >
          <Calendar className="time-travel-button-icon" />
          <span>Set Time</span>
        </button>
        
        {currentTime && (
          <>
            <button
              onClick={handleReset}
              className="time-travel-button"
              aria-label="Reset to current time"
            >
              <RotateCcw className="time-travel-button-icon" />
              <span>Reset</span>
            </button>
            {onRestore && (
              <button
                onClick={handleRestore}
                className="time-travel-button time-travel-button-restore"
                aria-label="Restore state to selected time"
              >
                <RotateCcw className="time-travel-button-icon" />
                <span>Restore</span>
              </button>
            )}
          </>
        )}
      </div>

      {showTimePicker && (
        <div className="time-picker">
          <input
            type="datetime-local"
            value={timeInput}
            onChange={(e) => setTimeInput(e.target.value)}
            className="time-picker-input"
            aria-label="Select time"
          />
          <div className="time-picker-buttons">
            <button
              onClick={handleSetTime}
              className="time-picker-button"
              disabled={!timeInput}
            >
              Set Time
            </button>
            <button
              onClick={() => {
                setShowTimePicker(false);
                setTimeInput('');
              }}
              className="time-picker-button time-picker-button-cancel"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

