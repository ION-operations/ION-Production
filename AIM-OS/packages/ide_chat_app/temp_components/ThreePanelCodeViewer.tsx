/**
 * Three-Panel Code Viewer Component
 * Revolutionary three-panel system:
 * 1. Code Editor (Left)
 * 2. Syntax & Architecture Layer (Middle) - NEW!
 * 3. Documentation (Right)
 * 
 * This creates a complete development experience where:
 * - Code is on the left
 * - Syntax explanations and architectural context are in the middle
 * - Full documentation and plans are on the right
 */

import React, { useState, useEffect, useRef } from 'react'
import { MonacoEditor } from './MonacoEditor'
import { ArchitecturalDocumentation } from './ArchitecturalDocumentation'
import { SyntaxArchitectureLayer } from './SyntaxArchitectureLayer'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { 
  Code, 
  BookOpen, 
  Settings, 
  Zap
} from 'lucide-react'
import { aimosClient } from '../lib/aimos-client'

interface ThreePanelCodeViewerProps {
  filePath?: string
  initialCode?: string
  documentation?: string
  onCodeChange?: (code: string) => void
  onDocumentationChange?: (docs: string) => void
  className?: string
}

export const ThreePanelCodeViewer: React.FC<ThreePanelCodeViewerProps> = ({
  filePath = 'src/example.tsx',
  initialCode = `// Welcome to the Three-Panel IDE! 🚀
import React, { useState, useEffect, useRef } from 'react'
import { Button } from './Button'

interface UserProfileProps {
  userId: string
  onUpdate: (user: User) => void
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchUser(userId)
  }, [userId])

  const fetchUser = async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(\`/api/users/\${id}\`)
      if (!response.ok) throw new Error('Failed to fetch user')
      const userData = await response.json()
      setUser(userData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = (updatedUser: User) => {
    setUser(updatedUser)
    onUpdate(updatedUser)
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!user) return <div>User not found</div>

  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <Button onClick={() => handleUpdate(user)}>
        Update Profile
      </Button>
    </div>
  )
}`,
  documentation = `# UserProfile Component

## Overview
The \`UserProfile\` component is a React functional component that displays and manages user profile information. It's designed to be reusable across the application and provides a clean interface for user data management.

## Architecture

### Component Structure
- **Type**: Functional Component with TypeScript
- **Pattern**: Props Interface + State Management
- **Dependencies**: React hooks, custom Button component

### Design Decisions
1. **TypeScript Interface**: Uses \`UserProfileProps\` for type safety
2. **State Management**: Uses \`useState\` for local state
3. **Side Effects**: Uses \`useEffect\` for data fetching
4. **Error Handling**: Implements try-catch for robust error management
5. **Loading States**: Provides user feedback during async operations

## Props

### UserProfileProps
\`\`\`typescript
interface UserProfileProps {
  userId: string        // Required: Unique identifier for the user
  onUpdate: (user: User) => void  // Callback when user data is updated
}
\`\`\`

## State Management

### Local State
- \`user: User | null\` - Current user data
- \`loading: boolean\` - Loading state for async operations
- \`error: string | null\` - Error message if operation fails

### State Flow
1. Component mounts with \`userId\`
2. \`useEffect\` triggers \`fetchUser\`
3. Loading state is set to \`true\`
4. API call is made
5. On success: user data is set, loading becomes \`false\`
6. On error: error message is set, loading becomes \`false\`

## API Integration

### fetchUser Function
- **Method**: GET
- **Endpoint**: \`/api/users/{userId}\`
- **Error Handling**: Throws error for non-200 responses
- **Type Safety**: Returns typed \`User\` object

### Error Scenarios
- Network failures
- Invalid user ID
- Server errors (4xx, 5xx)
- Malformed response data

## Usage Examples

### Basic Usage
\`\`\`tsx
<UserProfile 
  userId="123" 
  onUpdate={(user) => console.log('User updated:', user)} 
/>
\`\`\`

### With Error Boundary
\`\`\`tsx
<ErrorBoundary>
  <UserProfile 
    userId={currentUserId} 
    onUpdate={handleUserUpdate} 
  />
</ErrorBoundary>
\`\`\`

## Testing Strategy

### Unit Tests
- Component renders with valid props
- Loading state displays correctly
- Error state displays correctly
- User data displays correctly
- onUpdate callback is called

### Integration Tests
- API integration works correctly
- Error handling works for various scenarios
- State updates work correctly

## Performance Considerations

### Optimizations
- \`useEffect\` dependency array prevents unnecessary re-fetches
- Error state is reset on new fetch attempts
- Loading state provides immediate user feedback

### Potential Improvements
- Add \`useMemo\` for expensive computations
- Add \`useCallback\` for event handlers
- Consider implementing retry logic for failed requests

## Related Components
- \`Button\` - Used for update actions
- \`User\` - Type definition for user data
- \`ErrorBoundary\` - For error handling

## Future Enhancements
- Add user avatar display
- Add form validation for updates
- Add optimistic updates
- Add offline support
- Add accessibility improvements`,
  onCodeChange,
  onDocumentationChange,
  className
}) => {
  const [code, setCode] = useState(initialCode)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [lastAnalysis, setLastAnalysis] = useState<Date | null>(null)

  const analysisIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    // Store initial state in AIM-OS
    aimosClient.storeMemory(
      `Three-panel code viewer initialized for ${filePath}`,
      { 'three_panel_viewer': 1.0, 'code_analysis': 0.8, [`file_${filePath}`]: 0.7 }
    )

    return () => {
      if (analysisIntervalRef.current) {
        clearInterval(analysisIntervalRef.current)
      }
    }
  }, [filePath])

  const handleCodeChange = (newCode: string | undefined) => {
    if (newCode !== undefined) {
      setCode(newCode)
      onCodeChange?.(newCode)
      
      // Trigger analysis with debouncing
      debouncedAnalysis()
    }
  }

  const debouncedAnalysis = (() => {
    let timeoutId: NodeJS.Timeout
    return () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        simulateAnalysis()
      }, 1000) // 1 second debounce
    }
  })()

  const simulateAnalysis = () => {
    setIsAnalyzing(true)
    setAnalysisProgress(0)
    
    // Simulate analysis progress
    analysisIntervalRef.current = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          setIsAnalyzing(false)
          setLastAnalysis(new Date())
          if (analysisIntervalRef.current) {
            clearInterval(analysisIntervalRef.current)
          }
          return 100
        }
        return prev + 10
      })
    }, 100)

    // Store analysis in AIM-OS
    aimosClient.addTimelineEntry(
      'three_panel_analysis',
      `Code analysis started for ${filePath}`,
      { filePath, codeLength: code.length }
    )
  }


  const handleDocumentationLinkClick = (link: string) => {
    console.log('Documentation link clicked:', link)
    // Store interaction in AIM-OS
    aimosClient.storeMemory(
      `User clicked documentation link: ${link}`,
      { 'user_interaction': 1.0, 'documentation': 0.8, [`link_${link}`]: 0.7 }
    )
  }

  const handleArchitectureLinkClick = (component: string) => {
    console.log('Architecture link clicked:', component)
    // Store interaction in AIM-OS
    aimosClient.storeMemory(
      `User clicked architecture link: ${component}`,
      { 'user_interaction': 1.0, 'architecture': 0.8, [`component_${component}`]: 0.7 }
    )
  }

  return (
    <div className={`h-full bg-gray-900 text-gray-100 ${className}`}>
      {/* Header */}
      <div className="h-12 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Code className="w-5 h-5 text-blue-400" />
            <span className="font-semibold">Three-Panel IDE</span>
          </div>
          <div className="text-sm text-gray-400">
            {filePath}
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {isAnalyzing && (
            <div className="flex items-center gap-2 text-sm text-yellow-400">
              <Zap className="w-4 h-4 animate-pulse" />
              <span>Analyzing... {analysisProgress}%</span>
            </div>
          )}
          {lastAnalysis && !isAnalyzing && (
            <div className="text-xs text-gray-500">
              Last analysis: {lastAnalysis.toLocaleTimeString()}
            </div>
          )}
          <button className="p-1 hover:bg-gray-700 rounded">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Three-Panel Layout */}
      <PanelGroup direction="horizontal" className="h-[calc(100%-3rem)]">
        {/* Left Panel: Code Editor */}
        <Panel defaultSize={40} minSize={25} maxSize={60}>
          <div className="h-full border-r border-gray-700 bg-gray-900">
            <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-center px-3">
              <Code className="w-4 h-4 mr-2 text-blue-400" />
              <span className="text-sm font-medium">Code Editor</span>
            </div>
            <div className="h-[calc(100%-2rem)]">
                    <MonacoEditor
                      language="typescript"
                      value={code}
                      onChange={handleCodeChange}
                      theme="vs-dark"
                    />
            </div>
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600 transition-colors" />

        {/* Middle Panel: Syntax & Architecture Layer */}
        <Panel defaultSize={35} minSize={25} maxSize={50}>
          <div className="h-full border-r border-gray-700 bg-gray-900">
            <SyntaxArchitectureLayer
              code={code}
              filePath={filePath}
              onDocumentationLinkClick={handleDocumentationLinkClick}
              onArchitectureLinkClick={handleArchitectureLinkClick}
            />
          </div>
        </Panel>

        <PanelResizeHandle className="w-1 bg-gray-700 hover:bg-gray-600 transition-colors" />

        {/* Right Panel: Documentation */}
        <Panel defaultSize={25} minSize={20} maxSize={50}>
          <div className="h-full bg-gray-900">
            <div className="h-8 bg-gray-800 border-b border-gray-700 flex items-center px-3">
              <BookOpen className="w-4 h-4 mr-2 text-green-400" />
              <span className="text-sm font-medium">Documentation</span>
            </div>
            <div className="h-[calc(100%-2rem)] overflow-y-auto custom-scrollbar">
              <ArchitecturalDocumentation
                componentName={filePath.split('/').pop()?.replace(/\.(tsx?|jsx?)$/, '') || 'Unknown'}
                filePath={filePath}
                onPatternClick={(pattern) => console.log('Pattern clicked:', pattern)}
                onDecisionClick={(decision) => console.log('Decision clicked:', decision)}
                onPlanClick={(plan) => console.log('Plan clicked:', plan)}
              />
            </div>
          </div>
        </Panel>
      </PanelGroup>

      {/* Status Bar */}
      <div className="h-6 bg-gray-800 border-t border-gray-700 flex items-center justify-between px-4 text-xs text-gray-400">
        <div className="flex items-center gap-4">
          <span>Lines: {code.split('\n').length}</span>
          <span>Characters: {code.length}</span>
          <span>File: {filePath}</span>
        </div>
        <div className="flex items-center gap-4">
          <span>TypeScript</span>
          <span>UTF-8</span>
          <span>LF</span>
        </div>
      </div>
    </div>
  )
}
