import { useState, useCallback } from 'react'
import { aiService, type AIResponse, type ContextAnalysis, type ModeSuggestion } from '../lib/ai-service'

export function useAI() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResponse, setLastResponse] = useState<AIResponse | null>(null)

  // Context analysis
  const analyzeContext = useCallback((prompt: string): ContextAnalysis => {
    try {
      setError(null)
      return aiService.analyzeContext(prompt)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze context'
      setError(errorMessage)
      throw err
    }
  }, [])

  // Mode suggestion
  const suggestMode = useCallback((prompt: string): ModeSuggestion => {
    try {
      setError(null)
      return aiService.suggestMode(prompt)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to suggest mode'
      setError(errorMessage)
      throw err
    }
  }, [])

  // Tag generation
  const generateTags = useCallback((content: string): string[] => {
    try {
      setError(null)
      return aiService.generateTags(content)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate tags'
      setError(errorMessage)
      throw err
    }
  }, [])

  // Importance calculation
  const calculateImportance = useCallback((content: string, context: ContextAnalysis): number => {
    try {
      setError(null)
      return aiService.calculateImportance(content, context)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to calculate importance'
      setError(errorMessage)
      throw err
    }
  }, [])

  // Generate AI response
  const generateResponse = useCallback(async (prompt: string, context?: any): Promise<AIResponse> => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await aiService.generateResponse(prompt, context)
      setLastResponse(response)
      return response
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate response'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Provider management
  const getProviders = useCallback(() => {
    return aiService.getProviders()
  }, [])

  const setActiveProvider = useCallback((providerId: string) => {
    try {
      setError(null)
      aiService.setActiveProvider(providerId)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to set active provider'
      setError(errorMessage)
      throw err
    }
  }, [])

  const getActiveProvider = useCallback(() => {
    return aiService.getActiveProvider()
  }, [])

  // Clear error
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    // State
    isLoading,
    error,
    lastResponse,
    
    // AI Operations
    analyzeContext,
    suggestMode,
    generateTags,
    calculateImportance,
    generateResponse,
    
    // Provider Management
    getProviders,
    setActiveProvider,
    getActiveProvider,
    
    // Utilities
    clearError
  }
}
