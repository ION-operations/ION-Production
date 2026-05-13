import { useState, useCallback } from 'react'
import { 
  validateChatMessage, 
  validateMemoryEntry, 
  validateUserInput, 
  validateTheme, 
  validateMode,
  validateField,
  type ValidationResult,
  type ValidationRule
} from '../lib/validation'

export function useValidation() {
  const [validationHistory, setValidationHistory] = useState<ValidationResult[]>([])

  // Chat message validation
  const validateMessage = useCallback((message: string): ValidationResult => {
    const result = validateChatMessage(message)
    setValidationHistory(prev => [...prev.slice(-9), result]) // Keep last 10 results
    return result
  }, [])

  // Memory entry validation
  const validateMemory = useCallback((entry: {
    title: string
    content: string
    category: string
    tags: string[]
  }): ValidationResult => {
    const result = validateMemoryEntry(entry)
    setValidationHistory(prev => [...prev.slice(-9), result])
    return result
  }, [])

  // User input validation
  const validateInput = useCallback((input: string, type: 'search' | 'command' | 'general'): ValidationResult => {
    const result = validateUserInput(input, type)
    setValidationHistory(prev => [...prev.slice(-9), result])
    return result
  }, [])

  // Theme validation
  const validateThemeInput = useCallback((theme: string): ValidationResult => {
    const result = validateTheme(theme)
    setValidationHistory(prev => [...prev.slice(-9), result])
    return result
  }, [])

  // Mode validation
  const validateModeInput = useCallback((mode: string): ValidationResult => {
    const result = validateMode(mode)
    setValidationHistory(prev => [...prev.slice(-9), result])
    return result
  }, [])

  // Generic field validation
  const validateGenericField = useCallback((value: any, rules: ValidationRule, fieldName: string): ValidationResult => {
    const result = validateField(value, rules, fieldName)
    setValidationHistory(prev => [...prev.slice(-9), result])
    return result
  }, [])

  // Clear validation history
  const clearHistory = useCallback(() => {
    setValidationHistory([])
  }, [])

  // Get validation statistics
  const getValidationStats = useCallback(() => {
    const total = validationHistory.length
    const passed = validationHistory.filter(r => r.isValid).length
    const failed = total - passed
    const withWarnings = validationHistory.filter(r => r.warnings.length > 0).length

    return {
      total,
      passed,
      failed,
      withWarnings,
      successRate: total > 0 ? (passed / total) * 100 : 0
    }
  }, [validationHistory])

  return {
    // Validation functions
    validateMessage,
    validateMemory,
    validateInput,
    validateThemeInput,
    validateModeInput,
    validateGenericField,
    
    // History and stats
    validationHistory,
    clearHistory,
    getValidationStats
  }
}
