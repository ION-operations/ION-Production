/**
 * Token Counter - Estimate token counts for text
 * 
 * Uses character-based estimation (1 token ≈ 4 characters)
 * More accurate than actual tokenizers would require tiktoken dependency
 */

export class TokenCounter {
  /**
   * Estimate token count for text
   * 
   * Uses heuristic: 1 token ≈ 4 characters (English text average)
   * Accuracy: ±20% typically
   * 
   * @param text Text to count tokens for
   * @returns Estimated token count
   */
  static estimate(text: string): number {
    if (!text || text.length === 0) return 0
    
    // Character-based estimation
    // 1 token ≈ 4 characters for English text
    return Math.ceil(text.length / 4)
  }

  /**
   * Estimate tokens for chat messages
   */
  static estimateMessages(messages: Array<{ role: string; content: string }>): number {
    let total = 0
    
    for (const message of messages) {
      // Count content
      total += this.estimate(message.content)
      
      // Add overhead for role and formatting (~4 tokens per message)
      total += 4
    }
    
    return total
  }

  /**
   * Estimate tokens for API request
   */
  static estimateRequest(data: any): { input: number; estimated_output: number } {
    let inputTokens = 0
    let estimatedOutput = 100 // Default estimate
    
    // Count messages
    if (data.messages && Array.isArray(data.messages)) {
      inputTokens = this.estimateMessages(data.messages)
    }
    
    // Count system prompt
    if (data.system) {
      inputTokens += this.estimate(data.system)
    }
    
    // Estimate output from max_tokens
    if (data.max_tokens && typeof data.max_tokens === 'number') {
      estimatedOutput = data.max_tokens
    }
    
    return {
      input: inputTokens,
      estimated_output: estimatedOutput,
    }
  }

  /**
   * Calculate actual tokens from response
   */
  static countResponse(content: string): number {
    return this.estimate(content)
  }
}

