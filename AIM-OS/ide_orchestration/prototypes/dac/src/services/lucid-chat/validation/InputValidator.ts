/**
 * Input Validator
 * 
 * Comprehensive input validation utilities for all services
 */

export interface ValidationError {
  field: string
  value: any
  error: string
  expected: string
}

export class ValidationError extends Error {
  constructor(
    public field: string,
    public value: any,
    public expected: string,
    message?: string
  ) {
    super(message || `Validation failed for field "${field}": expected ${expected}, got ${typeof value}`)
    this.name = 'ValidationError'
  }
}

export class InputValidator {
  /**
   * Validate string input
   */
  static validateString(
    value: any,
    field: string = 'value',
    options: {
      minLength?: number
      maxLength?: number
      required?: boolean
      trim?: boolean
    } = {}
  ): string {
    const { minLength, maxLength, required = true, trim = true } = options

    if (value === undefined || value === null) {
      if (required) {
        throw new ValidationError(field, value, 'non-null string', `Field "${field}" is required`)
      }
      return ''
    }

    if (typeof value !== 'string') {
      throw new ValidationError(field, value, 'string', `Field "${field}" must be a string`)
    }

    let validated = trim ? value.trim() : value

    if (minLength !== undefined && validated.length < minLength) {
      throw new ValidationError(
        field,
        value,
        `string with length >= ${minLength}`,
        `Field "${field}" must be at least ${minLength} characters`
      )
    }

    if (maxLength !== undefined && validated.length > maxLength) {
      throw new ValidationError(
        field,
        value,
        `string with length <= ${maxLength}`,
        `Field "${field}" must be at most ${maxLength} characters`
      )
    }

    return validated
  }

  /**
   * Validate number input
   */
  static validateNumber(
    value: any,
    field: string = 'value',
    options: {
      min?: number
      max?: number
      required?: boolean
      integer?: boolean
    } = {}
  ): number {
    const { min, max, required = true, integer = false } = options

    if (value === undefined || value === null) {
      if (required) {
        throw new ValidationError(field, value, 'non-null number', `Field "${field}" is required`)
      }
      return 0
    }

    const num = typeof value === 'number' ? value : Number(value)

    if (isNaN(num)) {
      throw new ValidationError(field, value, 'number', `Field "${field}" must be a valid number`)
    }

    if (integer && !Number.isInteger(num)) {
      throw new ValidationError(field, value, 'integer', `Field "${field}" must be an integer`)
    }

    if (min !== undefined && num < min) {
      throw new ValidationError(
        field,
        value,
        `number >= ${min}`,
        `Field "${field}" must be at least ${min}`
      )
    }

    if (max !== undefined && num > max) {
      throw new ValidationError(
        field,
        value,
        `number <= ${max}`,
        `Field "${field}" must be at most ${max}`
      )
    }

    return num
  }

  /**
   * Validate array input
   */
  static validateArray<T>(
    value: any,
    field: string = 'value',
    options: {
      minItems?: number
      maxItems?: number
      required?: boolean
      itemValidator?: (item: any, index: number) => T
    } = {}
  ): T[] {
    const { minItems, maxItems, required = true, itemValidator } = options

    if (value === undefined || value === null) {
      if (required) {
        throw new ValidationError(field, value, 'non-null array', `Field "${field}" is required`)
      }
      return []
    }

    if (!Array.isArray(value)) {
      throw new ValidationError(field, value, 'array', `Field "${field}" must be an array`)
    }

    if (minItems !== undefined && value.length < minItems) {
      throw new ValidationError(
        field,
        value,
        `array with length >= ${minItems}`,
        `Field "${field}" must have at least ${minItems} items`
      )
    }

    if (maxItems !== undefined && value.length > maxItems) {
      throw new ValidationError(
        field,
        value,
        `array with length <= ${maxItems}`,
        `Field "${field}" must have at most ${maxItems} items`
      )
    }

    if (itemValidator) {
      return value.map((item, index) => {
        try {
          return itemValidator(item, index)
        } catch (error) {
          throw new ValidationError(
            `${field}[${index}]`,
            item,
            'valid item',
            `Invalid item at index ${index}: ${error instanceof Error ? error.message : String(error)}`
          )
        }
      })
    }

    return value as T[]
  }

  /**
   * Validate object input
   */
  static validateObject(
    value: any,
    field: string = 'value',
    options: {
      required?: boolean
      schema?: Record<string, (v: any) => any>
    } = {}
  ): Record<string, any> {
    const { required = true, schema } = options

    if (value === undefined || value === null) {
      if (required) {
        throw new ValidationError(field, value, 'non-null object', `Field "${field}" is required`)
      }
      return {}
    }

    if (typeof value !== 'object' || Array.isArray(value)) {
      throw new ValidationError(field, value, 'object', `Field "${field}" must be an object`)
    }

    if (schema) {
      const validated: Record<string, any> = {}
      for (const [key, validator] of Object.entries(schema)) {
        try {
          validated[key] = validator(value[key])
        } catch (error) {
          throw new ValidationError(
            `${field}.${key}`,
            value[key],
            'valid value',
            `Invalid field "${key}": ${error instanceof Error ? error.message : String(error)}`
          )
        }
      }
      return validated
    }

    return value
  }

  /**
   * Validate enum value
   */
  static validateEnum<T extends string>(
    value: any,
    allowed: T[],
    field: string = 'value',
    required: boolean = true
  ): T {
    if (value === undefined || value === null) {
      if (required) {
        throw new ValidationError(
          field,
          value,
          `one of: ${allowed.join(', ')}`,
          `Field "${field}" is required and must be one of: ${allowed.join(', ')}`
        )
      }
      return allowed[0] // Default to first value
    }

    if (!allowed.includes(value)) {
      throw new ValidationError(
        field,
        value,
        `one of: ${allowed.join(', ')}`,
        `Field "${field}" must be one of: ${allowed.join(', ')}, got "${value}"`
      )
    }

    return value as T
  }

  /**
   * Validate optional value
   */
  static validateOptional<T>(
    value: any,
    validator: (v: any) => T,
    field: string = 'value'
  ): T | undefined {
    if (value === undefined || value === null) {
      return undefined
    }

    try {
      return validator(value)
    } catch (error) {
      throw new ValidationError(
        field,
        value,
        'valid value or undefined',
        `Invalid optional field "${field}": ${error instanceof Error ? error.message : String(error)}`
      )
    }
  }

  /**
   * Validate boolean
   */
  static validateBoolean(
    value: any,
    field: string = 'value',
    required: boolean = true
  ): boolean {
    if (value === undefined || value === null) {
      if (required) {
        throw new ValidationError(field, value, 'boolean', `Field "${field}" is required`)
      }
      return false
    }

    if (typeof value === 'boolean') {
      return value
    }

    if (typeof value === 'string') {
      const lower = value.toLowerCase()
      if (lower === 'true' || lower === '1' || lower === 'yes') {
        return true
      }
      if (lower === 'false' || lower === '0' || lower === 'no') {
        return false
      }
    }

    if (typeof value === 'number') {
      return value !== 0
    }

    throw new ValidationError(field, value, 'boolean', `Field "${field}" must be a boolean`)
  }
}

