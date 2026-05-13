/**
 * Syntax Architecture Layer Component
 * Middle layer between code and docs that provides:
 * - Syntax explanations in natural language
 * - Architectural context and connections
 * - Real-time code analysis and insights
 * - Links to broader documentation and plans
 */

import React, { useState, useEffect, useRef } from 'react'
import { 
  Code2, 
  Brain, 
  GitBranch, 
  Lightbulb, 
  Link, 
  ArrowRight, 
  ChevronDown, 
  ChevronRight,
  Zap,
  Target,
  Layers,
  BookOpen,
  FileText,
  Search,
  Sparkles
} from 'lucide-react'
import { aimosClient } from '../lib/aimos-client'
import { codeIntelligence, CodeAnalysis } from '../lib/code-intelligence'

interface SyntaxExplanation {
  id: string
  lineNumber: number
  codeSnippet: string
  explanation: string
  complexity: 'simple' | 'moderate' | 'complex'
  concepts: string[]
  relatedPatterns: string[]
  architecturalImpact: string
  documentationLinks: string[]
}

interface ArchitecturalContext {
  componentName: string
  purpose: string
  responsibilities: string[]
  dependencies: string[]
  designPatterns: string[]
  architecturalDecisions: string[]
  relatedComponents: string[]
  documentationSections: string[]
}

interface SyntaxArchitectureLayerProps {
  code: string
  filePath: string
  onDocumentationLinkClick?: (link: string) => void
  onArchitectureLinkClick?: (component: string) => void
}

export const SyntaxArchitectureLayer: React.FC<SyntaxArchitectureLayerProps> = ({
  code,
  filePath,
  onDocumentationLinkClick,
  onArchitectureLinkClick
}) => {
  const [syntaxExplanations, setSyntaxExplanations] = useState<SyntaxExplanation[]>([])
  const [architecturalContext, setArchitecturalContext] = useState<ArchitecturalContext | null>(null)
  const [codeAnalysis, setCodeAnalysis] = useState<CodeAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [selectedExplanation, setSelectedExplanation] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['syntax', 'architecture']))

  const analysisRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    analyzeCode()
  }, [code, filePath])

  const analyzeCode = async () => {
    setIsAnalyzing(true)
    try {
      // Get code analysis
      const analysis = await codeIntelligence.analyzeCode(code, filePath, 'typescript')
      setCodeAnalysis(analysis)

      // Generate syntax explanations
      const explanations = await generateSyntaxExplanations(code, analysis)
      setSyntaxExplanations(explanations)

      // Generate architectural context
      const context = await generateArchitecturalContext(filePath, code, analysis)
      setArchitecturalContext(context)

      // Store analysis in AIM-OS
      await aimosClient.storeMemory(
        `Syntax analysis completed for ${filePath}. Generated ${explanations.length} explanations and architectural context.`,
        { 'syntax_analysis': 1.0, 'architectural_context': 0.9, [`file_${filePath}`]: 0.8 }
      )

      await aimosClient.addTimelineEntry(
        'syntax_analysis_complete',
        `Syntax and architectural analysis completed for ${filePath}`,
        { filePath, explanationsCount: explanations.length, hasContext: !!context }
      )

    } catch (error) {
      console.error('Syntax analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const generateSyntaxExplanations = async (code: string, analysis: CodeAnalysis): Promise<SyntaxExplanation[]> => {
    const lines = code.split('\n')
    const explanations: SyntaxExplanation[] = []

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line || line.startsWith('//') || line.startsWith('/*')) continue

      const explanation = await generateLineExplanation(line, i + 1, analysis)
      if (explanation) {
        explanations.push(explanation)
      }
    }

    return explanations
  }

  const generateLineExplanation = async (line: string, lineNumber: number, analysis: CodeAnalysis): Promise<SyntaxExplanation | null> => {
    // Simulate AI-powered syntax explanation generation
    await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100))

    const concepts: string[] = []
    const patterns: string[] = []
    let complexity: 'simple' | 'moderate' | 'complex' = 'simple'
    let architecturalImpact = ''

    // Analyze line content
    if (line.includes('import')) {
      concepts.push('Module Import', 'Dependency Management')
      patterns.push('ES6 Modules')
      complexity = 'simple'
      architecturalImpact = 'Establishes external dependencies'
    } else if (line.includes('export')) {
      concepts.push('Module Export', 'Public API')
      patterns.push('ES6 Modules', 'API Design')
      complexity = 'simple'
      architecturalImpact = 'Defines public interface'
    } else if (line.includes('function') || line.includes('=>')) {
      concepts.push('Function Definition', 'Behavioral Logic')
      patterns.push('Function Pattern')
      complexity = line.includes('=>') ? 'simple' : 'moderate'
      architecturalImpact = 'Implements business logic'
    } else if (line.includes('class')) {
      concepts.push('Class Definition', 'Object-Oriented Design')
      patterns.push('Class Pattern', 'Encapsulation')
      complexity = 'complex'
      architecturalImpact = 'Defines object structure and behavior'
    } else if (line.includes('useState') || line.includes('useEffect')) {
      concepts.push('React Hooks', 'State Management', 'Lifecycle')
      patterns.push('Hook Pattern', 'React Pattern')
      complexity = 'moderate'
      architecturalImpact = 'Manages component state and side effects'
    } else if (line.includes('interface') || line.includes('type')) {
      concepts.push('Type Definition', 'Type Safety')
      patterns.push('TypeScript Pattern', 'Contract Definition')
      complexity = 'moderate'
      architecturalImpact = 'Defines data contracts and type safety'
    } else if (line.includes('async') || line.includes('await')) {
      concepts.push('Asynchronous Programming', 'Promise Handling')
      patterns.push('Async/Await Pattern')
      complexity = 'moderate'
      architecturalImpact = 'Handles asynchronous operations'
    } else if (line.includes('try') || line.includes('catch')) {
      concepts.push('Error Handling', 'Exception Management')
      patterns.push('Try-Catch Pattern')
      complexity = 'moderate'
      architecturalImpact = 'Provides error resilience'
    }

    if (concepts.length === 0) return null

    const explanation = generateNaturalLanguageExplanation(line, concepts, patterns, complexity)
    const documentationLinks = generateDocumentationLinks(concepts, patterns)

    return {
      id: `explanation_${lineNumber}_${Date.now()}`,
      lineNumber,
      codeSnippet: line,
      explanation,
      complexity,
      concepts,
      relatedPatterns: patterns,
      architecturalImpact,
      documentationLinks
    }
  }

  const generateNaturalLanguageExplanation = (
    line: string, 
    concepts: string[], 
    patterns: string[], 
    complexity: string
  ): string => {
    const conceptText = concepts.join(', ')
    const patternText = patterns.length > 0 ? ` using ${patterns.join(' and ')} patterns` : ''
    
    let explanation = `This line ${line.includes('=') ? 'assigns' : 'declares'} a ${conceptText.toLowerCase()}${patternText}.`
    
    if (complexity === 'complex') {
      explanation += ' This is a complex operation that requires careful understanding of the underlying concepts.'
    } else if (complexity === 'moderate') {
      explanation += ' This involves intermediate concepts that build upon simpler patterns.'
    } else {
      explanation += ' This is a straightforward operation that follows common programming practices.'
    }

    return explanation
  }

  const generateDocumentationLinks = (concepts: string[], patterns: string[]): string[] => {
    const links: string[] = []
    
    concepts.forEach(concept => {
      if (concept.includes('React')) links.push('react-docs')
      if (concept.includes('TypeScript')) links.push('typescript-docs')
      if (concept.includes('Module')) links.push('es6-modules')
      if (concept.includes('Function')) links.push('functions-guide')
      if (concept.includes('Class')) links.push('classes-guide')
      if (concept.includes('Async')) links.push('async-programming')
      if (concept.includes('Error')) links.push('error-handling')
    })

    patterns.forEach(pattern => {
      if (pattern.includes('Hook')) links.push('react-hooks')
      if (pattern.includes('Module')) links.push('module-patterns')
      if (pattern.includes('Class')) links.push('oop-patterns')
    })

    return [...new Set(links)]
  }

  const generateArchitecturalContext = async (
    filePath: string, 
    code: string,
    analysis: CodeAnalysis
  ): Promise<ArchitecturalContext> => {
    // Simulate AI-powered architectural analysis
    await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300))

    const componentName = filePath.split('/').pop()?.replace('.tsx', '').replace('.ts', '') || 'Unknown'
    
    return {
      componentName,
      purpose: `This ${componentName} component serves as a ${getComponentPurpose(code)} in the application architecture.`,
      responsibilities: extractResponsibilities(code),
      dependencies: extractDependencies(code),
      designPatterns: extractDesignPatterns(code),
      architecturalDecisions: generateArchitecturalDecisions(code, analysis),
      relatedComponents: findRelatedComponents(filePath),
      documentationSections: generateDocumentationSections(componentName, code)
    }
  }

  const getComponentPurpose = (code: string): string => {
    if (code.includes('interface') && code.includes('Props')) return 'UI component with defined props interface'
    if (code.includes('useState') || code.includes('useEffect')) return 'stateful React component'
    if (code.includes('export const') && code.includes('React.FC')) return 'functional React component'
    if (code.includes('class') && code.includes('Component')) return 'class-based React component'
    if (code.includes('export interface') || code.includes('export type')) return 'type definition module'
    if (code.includes('export function') && !code.includes('React.FC')) return 'utility function module'
    return 'code module'
  }

  const extractResponsibilities = (code: string): string[] => {
    const responsibilities: string[] = []
    
    if (code.includes('useState')) responsibilities.push('State management')
    if (code.includes('useEffect')) responsibilities.push('Side effect handling')
    if (code.includes('onClick') || code.includes('onChange')) responsibilities.push('User interaction handling')
    if (code.includes('return') && code.includes('JSX')) responsibilities.push('UI rendering')
    if (code.includes('fetch') || code.includes('axios')) responsibilities.push('Data fetching')
    if (code.includes('localStorage') || code.includes('sessionStorage')) responsibilities.push('Data persistence')
    
    return responsibilities
  }

  const extractDependencies = (code: string): string[] => {
    const dependencies: string[] = []
    const importRegex = /import.*from\s+['"]([^'"]+)['"]/g
    let match
    
    while ((match = importRegex.exec(code)) !== null) {
      dependencies.push(match[1])
    }
    
    return dependencies
  }

  const extractDesignPatterns = (code: string): string[] => {
    const patterns: string[] = []
    
    if (code.includes('useState') && code.includes('useEffect')) patterns.push('Hook Pattern')
    if (code.includes('interface') && code.includes('Props')) patterns.push('Props Interface Pattern')
    if (code.includes('children') && code.includes('ReactNode')) patterns.push('Composition Pattern')
    if (code.includes('useContext')) patterns.push('Context Pattern')
    if (code.includes('useMemo') || code.includes('useCallback')) patterns.push('Optimization Pattern')
    if (code.includes('try') && code.includes('catch')) patterns.push('Error Boundary Pattern')
    
    return patterns
  }

  const generateArchitecturalDecisions = (code: string, analysis: CodeAnalysis): string[] => {
    const decisions: string[] = []
    
    if (code.includes('TypeScript')) {
      decisions.push('Chose TypeScript for type safety and better developer experience')
    }
    
    if (code.includes('React.FC')) {
      decisions.push('Used functional components with TypeScript for modern React development')
    }
    
    if (analysis.metrics.cyclomaticComplexity > 10) {
      decisions.push('High complexity detected - consider refactoring into smaller functions')
    }
    
    if (code.includes('getInstance()')) {
      decisions.push('Implemented Singleton pattern for global state management')
    }
    
    return decisions
  }

  const findRelatedComponents = (filePath: string): string[] => {
    // Simulate finding related components based on file path and naming patterns
    const baseName = filePath.split('/').pop()?.replace(/\.(tsx?|jsx?)$/, '') || ''
    const related: string[] = []
    
    if (baseName.includes('Button')) {
      related.push('ButtonGroup', 'IconButton', 'ToggleButton')
    } else if (baseName.includes('Modal')) {
      related.push('Dialog', 'Overlay', 'Backdrop')
    } else if (baseName.includes('Form')) {
      related.push('Input', 'Select', 'Checkbox', 'Radio')
    }
    
    return related
  }

  const generateDocumentationSections = (componentName: string, code: string): string[] => {
    const sections: string[] = ['Getting Started', 'API Reference']
    
    if (code.includes('useState')) sections.push('State Management')
    if (code.includes('useEffect')) sections.push('Lifecycle Methods')
    if (code.includes('props')) sections.push('Props Guide')
    if (code.includes('styling') || code.includes('className')) sections.push('Styling Guide')
    if (code.includes('accessibility') || code.includes('aria-')) sections.push('Accessibility')
    
    return sections
  }

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(section)) {
        newSet.delete(section)
      } else {
        newSet.add(section)
      }
      return newSet
    })
  }

  const handleDocumentationLinkClick = (link: string) => {
    onDocumentationLinkClick?.(link)
    // Store interaction in AIM-OS
    aimosClient.storeMemory(
      `User clicked documentation link: ${link} for ${filePath}`,
      { 'user_interaction': 1.0, 'documentation': 0.8, [`link_${link}`]: 0.7 }
    )
  }

  const handleArchitectureLinkClick = (component: string) => {
    onArchitectureLinkClick?.(component)
    // Store interaction in AIM-OS
    aimosClient.storeMemory(
      `User clicked architecture link: ${component} for ${filePath}`,
      { 'user_interaction': 1.0, 'architecture': 0.8, [`component_${component}`]: 0.7 }
    )
  }

  return (
    <div className="h-full bg-gray-900 text-gray-100 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-2 mb-2">
          <Brain className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold">Syntax & Architecture Layer</h2>
          {isAnalyzing && <Zap className="w-4 h-4 animate-pulse text-yellow-400" />}
        </div>
        <p className="text-sm text-gray-400">
          Real-time code analysis and architectural context for {filePath}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Syntax Explanations Section */}
        <div className="border-b border-gray-700">
          <button
            onClick={() => toggleSection('syntax')}
            className="w-full p-4 text-left hover:bg-gray-800 flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <Code2 className="w-5 h-5 text-green-400" />
              <span className="font-semibold">Syntax Explanations</span>
              <span className="text-sm text-gray-400">({syntaxExplanations.length})</span>
            </div>
            {expandedSections.has('syntax') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSections.has('syntax') && (
            <div className="px-4 pb-4 space-y-3">
              {syntaxExplanations.map((explanation) => (
                <div
                  key={explanation.id}
                  className={`p-3 rounded-lg border ${
                    selectedExplanation === explanation.id
                      ? 'border-blue-500 bg-blue-900/20'
                      : 'border-gray-600 bg-gray-800'
                  }`}
                  onClick={() => setSelectedExplanation(
                    selectedExplanation === explanation.id ? null : explanation.id
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 w-8 h-8 bg-gray-700 rounded flex items-center justify-center text-xs font-mono">
                      {explanation.lineNumber}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-mono text-sm text-gray-300 mb-2 bg-gray-900 p-2 rounded">
                        {explanation.codeSnippet}
                      </div>
                      <p className="text-sm text-gray-200 mb-2">
                        {explanation.explanation}
                      </p>
                      <div className="flex flex-wrap gap-2 mb-2">
                        {explanation.concepts.map((concept, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-600 text-blue-100 text-xs rounded"
                          >
                            {concept}
                          </span>
                        ))}
                        {explanation.relatedPatterns.map((pattern, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-purple-600 text-purple-100 text-xs rounded"
                          >
                            {pattern}
                          </span>
                        ))}
                      </div>
                      <p className="text-xs text-gray-400 mb-2">
                        <strong>Architectural Impact:</strong> {explanation.architecturalImpact}
                      </p>
                      {explanation.documentationLinks.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {explanation.documentationLinks.map((link, index) => (
                            <button
                              key={index}
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDocumentationLinkClick(link)
                              }}
                              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                            >
                              <Link className="w-3 h-3" />
                              {link}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Architectural Context Section */}
        <div className="border-b border-gray-700">
          <button
            onClick={() => toggleSection('architecture')}
            className="w-full p-4 text-left hover:bg-gray-800 flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-purple-400" />
              <span className="font-semibold">Architectural Context</span>
            </div>
            {expandedSections.has('architecture') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSections.has('architecture') && architecturalContext && (
            <div className="px-4 pb-4 space-y-4">
              <div>
                <h4 className="font-semibold text-white mb-2">{architecturalContext.componentName}</h4>
                <p className="text-sm text-gray-300">{architecturalContext.purpose}</p>
              </div>

              <div>
                <h5 className="font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Responsibilities
                </h5>
                <ul className="space-y-1">
                  {architecturalContext.responsibilities.map((responsibility, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-center gap-2">
                      <ArrowRight className="w-3 h-3 text-gray-500" />
                      {responsibility}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h5 className="font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <GitBranch className="w-4 h-4" />
                  Dependencies
                </h5>
                <div className="flex flex-wrap gap-2">
                  {architecturalContext.dependencies.map((dep, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-700 text-gray-200 text-xs rounded"
                    >
                      {dep}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h5 className="font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Design Patterns
                </h5>
                <div className="flex flex-wrap gap-2">
                  {architecturalContext.designPatterns.map((pattern, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-purple-600 text-purple-100 text-xs rounded"
                    >
                      {pattern}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h5 className="font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4" />
                  Architectural Decisions
                </h5>
                <ul className="space-y-1">
                  {architecturalContext.architecturalDecisions.map((decision, index) => (
                    <li key={index} className="text-sm text-gray-300 flex items-start gap-2">
                      <ArrowRight className="w-3 h-3 text-gray-500 mt-0.5 flex-shrink-0" />
                      {decision}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h5 className="font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <BookOpen className="w-4 h-4" />
                  Documentation Sections
                </h5>
                <div className="flex flex-wrap gap-2">
                  {architecturalContext.documentationSections.map((section, index) => (
                    <button
                      key={index}
                      onClick={() => handleDocumentationLinkClick(section.toLowerCase().replace(' ', '-'))}
                      className="px-2 py-1 bg-blue-600 text-blue-100 text-xs rounded hover:bg-blue-700 flex items-center gap-1"
                    >
                      <FileText className="w-3 h-3" />
                      {section}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Code Analysis Summary */}
        {codeAnalysis && (
          <div className="p-4">
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <Search className="w-4 h-4" />
              Analysis Summary
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Lines of Code:</span>
                <span className="ml-2 text-white">{codeAnalysis.metrics.linesOfCode}</span>
              </div>
              <div>
                <span className="text-gray-400">Complexity:</span>
                <span className="ml-2 text-white">{codeAnalysis.metrics.cyclomaticComplexity}</span>
              </div>
              <div>
                <span className="text-gray-400">Issues:</span>
                <span className="ml-2 text-white">{codeAnalysis.issues.length}</span>
              </div>
              <div>
                <span className="text-gray-400">Suggestions:</span>
                <span className="ml-2 text-white">{codeAnalysis.suggestions.length}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
