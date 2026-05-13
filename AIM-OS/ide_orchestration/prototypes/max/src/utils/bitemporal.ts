// Bitemporal Utilities - Max V2
// Shared utilities for bitemporal support across all panels

export interface BitemporalMetadata {
  valid_from: string; // ISO timestamp when this became valid
  valid_to: string | null; // ISO timestamp when this was superseded (null = current)
}

export interface BitemporalEntity<T> {
  data: T;
  bitemporal: BitemporalMetadata;
}

/**
 * Check if a bitemporal entity is currently valid
 */
export const isCurrentlyValid = <T>(entity: BitemporalEntity<T>): boolean => {
  return entity.bitemporal.valid_to === null;
};

/**
 * Check if a bitemporal entity was valid at a specific time
 */
export const wasValidAt = <T>(
  entity: BitemporalEntity<T>,
  timestamp: string
): boolean => {
  const validFrom = new Date(entity.bitemporal.valid_from);
  const validTo = entity.bitemporal.valid_to
    ? new Date(entity.bitemporal.valid_to)
    : null;
  const checkTime = new Date(timestamp);

  return (
    checkTime >= validFrom &&
    (validTo === null || checkTime < validTo)
  );
};

/**
 * Get all entities valid at a specific time
 */
export const getValidAt = <T>(
  entities: BitemporalEntity<T>[],
  timestamp: string
): BitemporalEntity<T>[] => {
  return entities.filter((entity) => wasValidAt(entity, timestamp));
};

/**
 * Get current valid entities
 */
export const getCurrentValid = <T>(
  entities: BitemporalEntity<T>[]
): BitemporalEntity<T>[] => {
  return entities.filter(isCurrentlyValid);
};

/**
 * Create bitemporal metadata for a new entity
 */
export const createBitemporalMetadata = (
  validFrom?: string
): BitemporalMetadata => {
  return {
    valid_from: validFrom || new Date().toISOString(),
    valid_to: null,
  };
};

/**
 * Supersede a bitemporal entity (mark as superseded)
 */
export const supersedeBitemporalEntity = <T>(
  entity: BitemporalEntity<T>,
  supersededAt?: string
): BitemporalEntity<T> => {
  return {
    ...entity,
    bitemporal: {
      ...entity.bitemporal,
      valid_to: supersededAt || new Date().toISOString(),
    },
  };
};

/**
 * Format bitemporal metadata for display
 */
export const formatBitemporalRange = (
  bitemporal: BitemporalMetadata
): string => {
  const from = new Date(bitemporal.valid_from).toLocaleString();
  const to = bitemporal.valid_to
    ? new Date(bitemporal.valid_to).toLocaleString()
    : 'Current';
  return `${from} → ${to}`;
};

/**
 * Get duration of validity
 */
export const getValidityDuration = (
  bitemporal: BitemporalMetadata
): string | null => {
  const from = new Date(bitemporal.valid_from);
  const to = bitemporal.valid_to
    ? new Date(bitemporal.valid_to)
    : new Date();

  const diffMs = to.getTime() - from.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 0) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''}`;
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''}`;
  } else if (diffMinutes > 0) {
    return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''}`;
  } else {
    return `${diffSeconds} second${diffSeconds > 1 ? 's' : ''}`;
  }
};

