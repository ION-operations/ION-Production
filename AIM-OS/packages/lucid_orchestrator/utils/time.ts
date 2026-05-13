/**
 * Cross-environment high resolution timer utility.
 * Falls back to Date.now when performance API is unavailable.
 */

export const now = (): number => {
  if (typeof globalThis !== 'undefined') {
    const perf = (globalThis as any).performance as Performance | undefined
    if (perf && typeof perf.now === 'function') {
      return perf.now()
    }
  }
  return Date.now()
}
