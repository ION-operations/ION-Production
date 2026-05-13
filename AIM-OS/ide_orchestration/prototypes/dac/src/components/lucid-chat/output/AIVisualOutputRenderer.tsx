/**
 * AI Visual Output Renderer
 * Main renderer component that detects output types and routes to appropriate renderers
 */

import React from 'react'
import { CodeBlockRenderer } from './CodeBlockRenderer'
import { YAMLJSONRenderer } from './YAMLJSONRenderer'
import { MathRenderer } from './MathRenderer'
import { DiagramRenderer } from './DiagramRenderer'
import { ChartRenderer } from './ChartRenderer'
import { ImageRenderer } from './ImageRenderer'
import { VideoRenderer } from './VideoRenderer'
import { AnimationRenderer } from './AnimationRenderer'
import { OutputDetector, OutputType } from './OutputDetector'
import type { AdvancedChatMessage } from '../../../store/lucid-chat/advancedLLMStore'

interface AIVisualOutputRendererProps {
  message: AdvancedChatMessage
  content: string
}

export const AIVisualOutputRenderer: React.FC<AIVisualOutputRendererProps> = ({
  message,
  content,
}) => {
  // Detect output types from content and protocol
  const detectedOutputs = OutputDetector.detect(content, message.outputProtocol)
  
  // If no special outputs detected, render as markdown
  if (detectedOutputs.length === 0) {
    return (
      <div className="prose prose-invert prose-sm max-w-none">
        {/* Will be rendered by EnhancedChatInterface markdown renderer */}
        {content}
      </div>
    )
  }
  
  // Render mixed outputs
  return (
    <div className="space-y-4">
      {detectedOutputs.map((output, index) => {
        switch (output.type) {
          case 'code':
            return (
              <CodeBlockRenderer
                key={index}
                code={output.content}
                language={output.language}
              />
            )
          
          case 'yaml':
          case 'json':
            return (
              <YAMLJSONRenderer
                key={index}
                content={output.content}
                format={output.type}
              />
            )
          
          case 'math':
            return (
              <MathRenderer
                key={index}
                expression={output.content}
                inline={output.inline}
              />
            )
          
          case 'diagram':
            return (
              <DiagramRenderer
                key={index}
                diagram={output.content}
                type={output.diagramType}
              />
            )
          
          case 'chart':
            return (
              <ChartRenderer
                key={index}
                data={output.data}
                type={output.chartType}
                config={output.config}
              />
            )
          
          case 'image':
            return (
              <ImageRenderer
                key={index}
                src={output.url}
                alt={output.alt}
                caption={output.caption}
              />
            )
          
          case 'video':
            return (
              <VideoRenderer
                key={index}
                src={output.url}
                type={output.videoType}
                caption={output.caption}
              />
            )
          
          case 'animation':
            return (
              <AnimationRenderer
                key={index}
                animation={output.animation}
                type={output.animationType}
              />
            )
          
          case 'markdown':
          default:
            return (
              <div
                key={index}
                className="prose prose-invert prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: output.content }}
              />
            )
        }
      })}
    </div>
  )
}

