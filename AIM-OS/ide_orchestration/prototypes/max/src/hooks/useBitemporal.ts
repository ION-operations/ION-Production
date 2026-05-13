// Bitemporal Hook - Max V2
// React hook for managing bitemporal state and queries

import { useState, useMemo, useCallback } from 'react';
import {
  BitemporalMetadata,
  BitemporalEntity,
  isCurrentlyValid,
  wasValidAt,
  getValidAt,
  getCurrentValid,
  createBitemporalMetadata,
  supersedeBitemporalEntity,
} from '../../utils/bitemporal';

export interface UseBitemporalOptions<T> {
  entities: BitemporalEntity<T>[];
  defaultViewTime?: string; // ISO timestamp for time-travel queries
}

export interface UseBitemporalReturn<T> {
  // Current state
  currentEntities: BitemporalEntity<T>[];
  viewTime: string | null;
  
  // Time-travel
  setViewTime: (timestamp: string | null) => void;
  getEntitiesAtTime: (timestamp: string) => BitemporalEntity<T>[];
  
  // Entity management
  createEntity: (data: T, validFrom?: string) => BitemporalEntity<T>;
  supersedeEntity: (entity: BitemporalEntity<T>, supersededAt?: string) => BitemporalEntity<T>;
  
  // Utilities
  isCurrent: (entity: BitemporalEntity<T>) => boolean;
  isValidAt: (entity: BitemporalEntity<T>, timestamp: string) => boolean;
}

export const useBitemporal = <T>(
  options: UseBitemporalOptions<T>
): UseBitemporalReturn<T> => {
  const { entities, defaultViewTime } = options;
  const [viewTime, setViewTime] = useState<string | null>(defaultViewTime || null);

  // Get current valid entities
  const currentEntities = useMemo(() => {
    if (viewTime) {
      return getValidAt(entities, viewTime);
    }
    return getCurrentValid(entities);
  }, [entities, viewTime]);

  // Get entities at specific time
  const getEntitiesAtTime = useCallback(
    (timestamp: string) => {
      return getValidAt(entities, timestamp);
    },
    [entities]
  );

  // Create new entity with bitemporal metadata
  const createEntity = useCallback(
    (data: T, validFrom?: string): BitemporalEntity<T> => {
      return {
        data,
        bitemporal: createBitemporalMetadata(validFrom),
      };
    },
    []
  );

  // Supersede entity
  const supersedeEntity = useCallback(
    (entity: BitemporalEntity<T>, supersededAt?: string): BitemporalEntity<T> => {
      return supersedeBitemporalEntity(entity, supersededAt);
    },
    []
  );

  // Check if entity is current
  const isCurrent = useCallback((entity: BitemporalEntity<T>): boolean => {
    return isCurrentlyValid(entity);
  }, []);

  // Check if entity is valid at timestamp
  const isValidAt = useCallback(
    (entity: BitemporalEntity<T>, timestamp: string): boolean => {
      return wasValidAt(entity, timestamp);
    },
    []
  );

  return {
    currentEntities,
    viewTime,
    setViewTime,
    getEntitiesAtTime,
    createEntity,
    supersedeEntity,
    isCurrent,
    isValidAt,
  };
};

