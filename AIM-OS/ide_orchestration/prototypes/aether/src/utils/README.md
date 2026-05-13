# Utilities Documentation
## Helper Functions for AIM-OS Integration

**Created:** 2025-11-08  
**Agent:** Aether  
**Purpose:** Utility functions for common operations  
**Status:** Production Ready ✅

---

## 🎯 **UTILITIES OVERVIEW**

Utility functions for:
- Formatting (confidence, timestamps, file sizes)
- Colors (confidence colors, status colors)
- Text manipulation (truncate, format)
- Async operations (debounce, throttle, retry)
- Data manipulation (deep clone, nested values)
- Type utilities (isEmpty, safe JSON)

---

## 📚 **UTILITIES REFERENCE**

### **Formatting**

#### **formatConfidence(confidence: number): string**
Format confidence as percentage (e.g., "85%")

#### **formatTimestamp(timestamp: string): string**
Format timestamp for display (e.g., "11/8/2025, 10:00:00 AM")

#### **formatRelativeTime(timestamp: string): string**
Format relative time (e.g., "2 minutes ago")

#### **formatFileSize(bytes: number): string**
Format file size (e.g., "1.5 MB")

#### **formatValidationResult(result: ValidationResult): string**
Format validation result for display

---

### **Colors**

#### **getConfidenceColor(confidence: number): string**
Get Tailwind color class for confidence level

#### **getConfidenceBgColor(confidence: number): string**
Get Tailwind background color class for confidence level

#### **getStatusColor(status: string): string**
Get Tailwind color class for status

#### **getStatusBgColor(status: string): string**
Get Tailwind background color class for status

---

### **Text Manipulation**

#### **truncateText(text: string, maxLength: number): string**
Truncate text with ellipsis

#### **formatMemory(memory: Memory): string**
Format memory for display

#### **formatSearchResult(result: SearchResult): string**
Format search result for display

---

### **Async Operations**

#### **debounce<T>(func: T, wait: number): T**
Debounce function calls

#### **throttle<T>(func: T, limit: number): T**
Throttle function calls

#### **retry<T>(fn: () => Promise<T>, maxRetries?: number, delay?: number): Promise<T>**
Retry async operation with exponential backoff

#### **sleep(ms: number): Promise<void>**
Sleep utility for async operations

---

### **Data Manipulation**

#### **deepClone<T>(obj: T): T**
Deep clone object

#### **getNestedValue(obj: any, path: string): any**
Get nested value from object

#### **setNestedValue(obj: any, path: string, value: any): void**
Set nested value in object

#### **groupBy<T>(items: T[], key: keyof T): Record<string, T[]>**
Group items by key

#### **sortByConfidence<T>(items: T[]): T[]**
Sort by confidence (highest first)

#### **sortByTimestamp<T>(items: T[]): T[]**
Sort by timestamp (newest first)

#### **filterByConfidence<T>(items: T[], threshold?: number): T[]**
Filter by confidence threshold

---

### **Type Utilities**

#### **isEmpty(value: any): boolean**
Check if value is empty

#### **generateId(prefix?: string): string**
Generate unique ID

#### **cn(...classes: (string | boolean | undefined | null)[]): string**
Class name utility (like clsx)

#### **safeJsonParse<T>(json: string, defaultValue: T): T**
Safe JSON parse with default

#### **safeJsonStringify(obj: any, defaultValue?: string): string**
Safe JSON stringify with default

---

## 💡 **USAGE EXAMPLES**

### **Formatting:**
```typescript
import { formatConfidence, formatTimestamp, formatRelativeTime } from '@/utils'

const confidence = formatConfidence(0.85) // "85%"
const timestamp = formatTimestamp('2025-11-08T10:00:00Z') // "11/8/2025, 10:00:00 AM"
const relative = formatRelativeTime('2025-11-08T10:00:00Z') // "2 minutes ago"
```

### **Colors:**
```typescript
import { getConfidenceColor, getStatusColor } from '@/utils'

const color = getConfidenceColor(0.85) // "text-yellow-400"
const statusColor = getStatusColor('connected') // "text-green-400"
```

### **Debounce/Throttle:**
```typescript
import { debounce, throttle } from '@/utils'

const debouncedSearch = debounce((query: string) => {
  // Search logic
}, 300)

const throttledScroll = throttle(() => {
  // Scroll logic
}, 100)
```

### **Data Manipulation:**
```typescript
import { sortByConfidence, filterByConfidence, groupBy } from '@/utils'

const sorted = sortByConfidence(memories)
const filtered = filterByConfidence(memories, 0.7)
const grouped = groupBy(memories, 'tag')
```

---

## 🎯 **BEST PRACTICES**

1. **Use Formatting:** Always format values for display
2. **Use Colors:** Use color utilities for consistent styling
3. **Debounce/Throttle:** Use for expensive operations
4. **Safe Operations:** Use safe JSON functions for error handling
5. **Type Safety:** Use TypeScript types with utilities

---

**Status:** Production Ready ✅  
**Version:** 1.0.0  
**Last Updated:** 2025-11-08

