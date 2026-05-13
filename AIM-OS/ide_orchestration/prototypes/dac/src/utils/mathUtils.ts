// Math Utilities for Vector Operations
// Helper functions for cosine similarity and vector operations

/**
 * Compute cosine similarity between two vectors
 * @param a - First vector
 * @param b - Second vector
 * @returns Similarity score [0, 1]
 */
export function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) {
    throw new Error(`Vectors must have same dimension: ${a.length} vs ${b.length}`)
  }
  
  let dotProduct = 0
  let normA = 0
  let normB = 0
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i]
    normA += a[i] * a[i]
    normB += b[i] * b[i]
  }
  
  const denominator = Math.sqrt(normA) * Math.sqrt(normB)
  if (denominator === 0) return 0
  
  return dotProduct / denominator
}

/**
 * Normalize a vector to unit length
 */
export function normalizeVector(vector: number[]): number[] {
  const norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0))
  if (norm === 0) return vector
  return vector.map(v => v / norm)
}

/**
 * Compute Euclidean distance between two vectors
 */
export function euclideanDistance(a: number[], b: number[]): number {
  if (a.length !== b.length) {
    throw new Error(`Vectors must have same dimension: ${a.length} vs ${b.length}`)
  }
  
  let sum = 0
  for (let i = 0; i < a.length; i++) {
    const diff = a[i] - b[i]
    sum += diff * diff
  }
  
  return Math.sqrt(sum)
}

