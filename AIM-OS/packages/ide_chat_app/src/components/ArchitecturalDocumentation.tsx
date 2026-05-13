/**
 * Architectural Documentation Component
 * Enhanced documentation system that connects code to broader architectural plans,
 * design decisions, and implementation strategies.
 */

import React, { useState, useEffect } from 'react'
import { 
  BookOpen, 
  GitBranch, 
  Lightbulb, 
  Target, 
  Layers, 
  Code2, 
  FileText, 
  Search,
  Link,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Zap,
  Brain,
  Settings,
  Users,
  Clock,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react'
import { aimosClient } from '../lib/aimos-client'

interface ArchitecturalDecision {
  id: string
  title: string
  description: string
  rationale: string
  alternatives: string[]
  consequences: string[]
  status: 'proposed' | 'accepted' | 'rejected' | 'deprecated'
  date: string
  author: string
  relatedComponents: string[]
  relatedPatterns: string[]
}

interface DesignPattern {
  id: string
  name: string
  category: 'creational' | 'structural' | 'behavioral' | 'architectural'
  description: string
  problem: string
  solution: string
  benefits: string[]
  drawbacks: string[]
  examples: string[]
  relatedPatterns: string[]
}

interface ImplementationPlan {
  id: string
  title: string
  description: string
  phases: Phase[]
  dependencies: string[]
  estimatedEffort: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'planned' | 'in_progress' | 'completed' | 'blocked'
  assignedTo: string
  dueDate: string
}

interface Phase {
  id: string
  title: string
  description: string
  tasks: string[]
  deliverables: string[]
  estimatedTime: string
  dependencies: string[]
  status: 'pending' | 'in_progress' | 'completed'
}

interface ArchitecturalDocumentationProps {
  componentName: string
  filePath: string
  onPatternClick?: (pattern: string) => void
  onDecisionClick?: (decision: string) => void
  onPlanClick?: (plan: string) => void
}

export const ArchitecturalDocumentation: React.FC<ArchitecturalDocumentationProps> = ({
  componentName,
  filePath,
  onPatternClick,
  onDecisionClick,
  onPlanClick
}) => {
  const [decisions, setDecisions] = useState<ArchitecturalDecision[]>([])
  const [patterns, setPatterns] = useState<DesignPattern[]>([])
  const [plans, setPlans] = useState<ImplementationPlan[]>([])
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'decisions', 'patterns']))
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadArchitecturalData()
  }, [componentName, filePath])

  const loadArchitecturalData = async () => {
    setIsLoading(true)
    try {
      // Simulate loading architectural data
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Generate mock architectural decisions
      const mockDecisions: ArchitecturalDecision[] = [
        {
          id: 'dec-001',
          title: 'TypeScript for Type Safety',
          description: 'Use TypeScript for all React components to ensure type safety and better developer experience',
          rationale: 'TypeScript provides compile-time type checking, better IDE support, and catches errors early in development',
          alternatives: ['JavaScript with PropTypes', 'Flow', 'No type checking'],
          consequences: ['Better code quality', 'Improved refactoring', 'Learning curve for team', 'Build complexity'],
          status: 'accepted',
          date: '2024-01-15',
          author: 'Lead Developer',
          relatedComponents: ['UserProfile', 'Button', 'Input'],
          relatedPatterns: ['Type Safety Pattern', 'Interface Segregation']
        },
        {
          id: 'dec-002',
          title: 'Functional Components with Hooks',
          description: 'Use functional components with React hooks instead of class components',
          rationale: 'Hooks provide better code reuse, simpler testing, and align with React\'s future direction',
          alternatives: ['Class components', 'Higher-order components', 'Render props'],
          consequences: ['Simpler code', 'Better performance', 'Easier testing', 'Migration effort'],
          status: 'accepted',
          date: '2024-01-20',
          author: 'Architecture Team',
          relatedComponents: ['UserProfile', 'Button', 'Modal'],
          relatedPatterns: ['Hook Pattern', 'Composition Pattern']
        }
      ]

      // Generate mock design patterns
      const mockPatterns: DesignPattern[] = [
        {
          id: 'pattern-001',
          name: 'Props Interface Pattern',
          category: 'structural',
          description: 'Define clear interfaces for component props to ensure type safety and documentation',
          problem: 'Components need clear contracts for their inputs without runtime errors',
          solution: 'Create TypeScript interfaces that define the shape of props',
          benefits: ['Type safety', 'Self-documenting code', 'IDE autocomplete', 'Refactoring safety'],
          drawbacks: ['Initial setup overhead', 'TypeScript learning curve'],
          examples: ['UserProfileProps', 'ButtonProps', 'InputProps'],
          relatedPatterns: ['Interface Segregation', 'Type Safety Pattern']
        },
        {
          id: 'pattern-002',
          name: 'Hook Pattern',
          category: 'behavioral',
          description: 'Use custom hooks to encapsulate and reuse stateful logic',
          problem: 'Stateful logic needs to be shared between components',
          solution: 'Extract stateful logic into custom hooks',
          benefits: ['Logic reuse', 'Easier testing', 'Separation of concerns'],
          drawbacks: ['Hook rules complexity', 'Debugging challenges'],
          examples: ['useUser', 'useApi', 'useLocalStorage'],
          relatedPatterns: ['Composition Pattern', 'State Management Pattern']
        }
      ]

      // Generate mock implementation plans
      const mockPlans: ImplementationPlan[] = [
        {
          id: 'plan-001',
          title: 'Component Library Implementation',
          description: 'Build a comprehensive component library with consistent design and behavior',
          phases: [
            {
              id: 'phase-001',
              title: 'Foundation Components',
              description: 'Implement basic UI components (Button, Input, Modal)',
              tasks: ['Create base components', 'Add TypeScript interfaces', 'Write unit tests'],
              deliverables: ['Button component', 'Input component', 'Modal component'],
              estimatedTime: '2 weeks',
              dependencies: [],
              status: 'completed'
            },
            {
              id: 'phase-002',
              title: 'Complex Components',
              description: 'Build advanced components (DataTable, Form, Chart)',
              tasks: ['Design component APIs', 'Implement components', 'Add documentation'],
              deliverables: ['DataTable component', 'Form component', 'Chart component'],
              estimatedTime: '3 weeks',
              dependencies: ['phase-001'],
              status: 'in_progress'
            }
          ],
          dependencies: ['Design System', 'TypeScript Setup'],
          estimatedEffort: '5 weeks',
          priority: 'high',
          status: 'in_progress',
          assignedTo: 'Frontend Team',
          dueDate: '2024-03-15'
        }
      ]

      setDecisions(mockDecisions)
      setPatterns(mockPatterns)
      setPlans(mockPlans)

      // Store in AIM-OS
      await aimosClient.storeMemory(
        `Architectural documentation loaded for ${componentName}`,
        { 'architectural_docs': 1.0, 'component': 0.9, [`${componentName}`]: 0.8 }
      )

      await aimosClient.addTimelineEntry(
        'architectural_docs_loaded',
        `Architectural documentation loaded for ${componentName}`,
        { componentName, filePath, decisionsCount: mockDecisions.length, patternsCount: mockPatterns.length }
      )

    } catch (error) {
      console.error('Failed to load architectural data:', error)
    } finally {
      setIsLoading(false)
    }
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

  const handleDecisionClick = (decision: ArchitecturalDecision) => {
    onDecisionClick?.(decision.id)
    aimosClient.storeMemory(
      `User clicked architectural decision: ${decision.title}`,
      { 'user_interaction': 1.0, 'architectural_decision': 0.9, [`decision_${decision.id}`]: 0.8 }
    )
  }

  const handlePatternClick = (pattern: DesignPattern) => {
    onPatternClick?.(pattern.name)
    aimosClient.storeMemory(
      `User clicked design pattern: ${pattern.name}`,
      { 'user_interaction': 1.0, 'design_pattern': 0.9, [`pattern_${pattern.id}`]: 0.8 }
    )
  }

  const handlePlanClick = (plan: ImplementationPlan) => {
    onPlanClick?.(plan.id)
    aimosClient.storeMemory(
      `User clicked implementation plan: ${plan.title}`,
      { 'user_interaction': 1.0, 'implementation_plan': 0.9, [`plan_${plan.id}`]: 0.8 }
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'accepted':
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'in_progress':
        return <Clock className="w-4 h-4 text-yellow-400" />
      case 'blocked':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'proposed':
        return <Info className="w-4 h-4 text-blue-400" />
      default:
        return <Info className="w-4 h-4 text-gray-400" />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-600 text-red-100'
      case 'high':
        return 'bg-orange-600 text-orange-100'
      case 'medium':
        return 'bg-yellow-600 text-yellow-100'
      case 'low':
        return 'bg-green-600 text-green-100'
      default:
        return 'bg-gray-600 text-gray-100'
    }
  }

  return (
    <div className="h-full bg-gray-900 text-gray-100 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-green-400" />
            <h2 className="text-lg font-semibold">Architectural Documentation</h2>
            {isLoading && <Zap className="w-4 h-4 animate-pulse text-yellow-400" />}
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search documentation..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1 bg-gray-700 text-white text-sm rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <button className="p-1 hover:bg-gray-700 rounded">
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>
        <p className="text-sm text-gray-400">
          Comprehensive architectural context for {componentName}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {/* Overview Section */}
        <div className="border-b border-gray-700">
          <button
            onClick={() => toggleSection('overview')}
            className="w-full p-4 text-left hover:bg-gray-800 flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-400" />
              <span className="font-semibold">Architecture Overview</span>
            </div>
            {expandedSections.has('overview') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSections.has('overview') && (
            <div className="px-4 pb-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <GitBranch className="w-4 h-4 text-purple-400" />
                    <span className="font-semibold">Decisions</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{decisions.length}</p>
                  <p className="text-sm text-gray-400">Architectural decisions</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Layers className="w-4 h-4 text-green-400" />
                    <span className="font-semibold">Patterns</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{patterns.length}</p>
                  <p className="text-sm text-gray-400">Design patterns</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Code2 className="w-4 h-4 text-yellow-400" />
                    <span className="font-semibold">Plans</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{plans.length}</p>
                  <p className="text-sm text-gray-400">Implementation plans</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Architectural Decisions Section */}
        <div className="border-b border-gray-700">
          <button
            onClick={() => toggleSection('decisions')}
            className="w-full p-4 text-left hover:bg-gray-800 flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-purple-400" />
              <span className="font-semibold">Architectural Decisions</span>
              <span className="text-sm text-gray-400">({decisions.length})</span>
            </div>
            {expandedSections.has('decisions') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSections.has('decisions') && (
            <div className="px-4 pb-4 space-y-3">
              {decisions.map((decision) => (
                <div
                  key={decision.id}
                  className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 cursor-pointer"
                  onClick={() => handleDecisionClick(decision)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-white">{decision.title}</h4>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(decision.status)}
                      <span className="text-xs text-gray-400">{decision.date}</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-300 mb-3">{decision.description}</p>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {decision.relatedComponents.map((component, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-600 text-blue-100 text-xs rounded"
                      >
                        {component}
                      </span>
                    ))}
                    {decision.relatedPatterns.map((pattern, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-purple-600 text-purple-100 text-xs rounded"
                      >
                        {pattern}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-gray-400">
                    By {decision.author} • Status: {decision.status}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Design Patterns Section */}
        <div className="border-b border-gray-700">
          <button
            onClick={() => toggleSection('patterns')}
            className="w-full p-4 text-left hover:bg-gray-800 flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-green-400" />
              <span className="font-semibold">Design Patterns</span>
              <span className="text-sm text-gray-400">({patterns.length})</span>
            </div>
            {expandedSections.has('patterns') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSections.has('patterns') && (
            <div className="px-4 pb-4 space-y-3">
              {patterns.map((pattern) => (
                <div
                  key={pattern.id}
                  className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 cursor-pointer"
                  onClick={() => handlePatternClick(pattern)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-white">{pattern.name}</h4>
                    <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                      {pattern.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-3">{pattern.description}</p>
                  <div className="space-y-2">
                    <div>
                      <span className="text-xs font-semibold text-gray-400">Problem:</span>
                      <p className="text-xs text-gray-300">{pattern.problem}</p>
                    </div>
                    <div>
                      <span className="text-xs font-semibold text-gray-400">Solution:</span>
                      <p className="text-xs text-gray-300">{pattern.solution}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {pattern.examples.map((example, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-green-600 text-green-100 text-xs rounded"
                      >
                        {example}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Implementation Plans Section */}
        <div className="border-b border-gray-700">
          <button
            onClick={() => toggleSection('plans')}
            className="w-full p-4 text-left hover:bg-gray-800 flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <Code2 className="w-5 h-5 text-yellow-400" />
              <span className="font-semibold">Implementation Plans</span>
              <span className="text-sm text-gray-400">({plans.length})</span>
            </div>
            {expandedSections.has('plans') ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedSections.has('plans') && (
            <div className="px-4 pb-4 space-y-3">
              {plans.map((plan) => (
                <div
                  key={plan.id}
                  className="bg-gray-800 p-4 rounded-lg border border-gray-700 hover:border-gray-600 cursor-pointer"
                  onClick={() => handlePlanClick(plan)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-white">{plan.title}</h4>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs rounded ${getPriorityColor(plan.priority)}`}>
                        {plan.priority}
                      </span>
                      {getStatusIcon(plan.status)}
                    </div>
                  </div>
                  <p className="text-sm text-gray-300 mb-3">{plan.description}</p>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <span className="text-gray-400">Effort:</span>
                      <span className="ml-1 text-white">{plan.estimatedEffort}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Assigned:</span>
                      <span className="ml-1 text-white">{plan.assignedTo}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Due:</span>
                      <span className="ml-1 text-white">{plan.dueDate}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Phases:</span>
                      <span className="ml-1 text-white">{plan.phases.length}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
