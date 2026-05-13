/**
 * Math Renderer
 * LaTeX/Math equation rendering using KaTeX
 */

import React from 'react'
import { BlockMath, InlineMath } from 'react-katex'
import 'katex/dist/katex.min.css'

interface MathRendererProps {
  expression: string
  inline?: boolean
}

export const MathRenderer: React.FC<MathRendererProps> = ({
  expression,
  inline = false,
}) => {
  try {
    if (inline) {
      return (
        <span className="inline-block">
          <InlineMath math={expression} />
        </span>
      )
    } else {
      return (
        <div className="my-4 p-4 bg-gray-800 rounded-lg overflow-x-auto">
          <BlockMath math={expression} />
        </div>
      )
    }
  } catch (error) {
    // If KaTeX fails to parse, show raw expression
    return (
      <code className={inline ? 'text-blue-300' : 'block p-2 bg-gray-800 rounded'}>
        {inline ? `$${expression}$` : `$$${expression}$$`}
      </code>
    )
  }
}

