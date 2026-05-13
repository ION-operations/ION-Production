/**
 * Output Detector
 * Detects output types from message content and protocol
 */

import type { AdvancedChatMessage } from '../../../store/lucid-chat/advancedLLMStore'

export type OutputType =
  | 'markdown'
  | 'code'
  | 'yaml'
  | 'json'
  | 'math'
  | 'diagram'
  | 'chart'
  | 'image'
  | 'video'
  | 'animation'

export interface DetectedOutput {
  type: OutputType
  content: string
  language?: string
  inline?: boolean
  diagramType?: 'mermaid' | 'graphviz' | 'plantuml'
  chartType?: 'line' | 'bar' | 'pie' | 'scatter' | 'area'
  data?: any
  config?: any
  url?: string
  alt?: string
  caption?: string
  videoType?: string
  animation?: any
  animationType?: 'css' | 'lottie' | 'gsap'
}

export class OutputDetector {
  /**
   * Detect all output types in content
   */
  static detect(
    content: string,
    protocol?: AdvancedChatMessage['outputProtocol']
  ): DetectedOutput[] {
    const outputs: DetectedOutput[] = []
    
    // 1. Extract from protocol first (most reliable)
    if (protocol) {
      // Diagrams from protocol
      if (protocol.diagrams) {
        protocol.diagrams.forEach((diagram) => {
          outputs.push({
            type: 'diagram',
            content: diagram.content,
            diagramType: diagram.type === 'mermaid' ? 'mermaid' : 'mermaid',
          })
        })
      }
      
      // Charts from protocol
      if (protocol.charts) {
        protocol.charts.forEach((chart) => {
          outputs.push({
            type: 'chart',
            data: chart.data,
            chartType: chart.type as any,
            config: chart.config,
            content: '', // Charts don't need text content
          })
        })
      }
      
      // Images from protocol
      if (protocol.images) {
        protocol.images.forEach((image) => {
          outputs.push({
            type: 'image',
            url: image.url,
            alt: image.alt,
            caption: image.caption,
            content: '', // Images don't need text content
          })
        })
      }
      
      // Video from protocol
      if (protocol.video) {
        protocol.video.forEach((video) => {
          outputs.push({
            type: 'video',
            url: video.url,
            videoType: video.type,
            caption: video.caption,
            content: '', // Video doesn't need text content
          })
        })
      }
    }
    
    // 2. Detect code blocks
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
    let match
    while ((match = codeBlockRegex.exec(content)) !== null) {
      const language = match[1]?.toLowerCase() || 'text'
      const code = match[2]
      
      // Check if it's a special code block type
      if (language === 'mermaid' || language === 'graph' || language === 'diagram') {
        outputs.push({
          type: 'diagram',
          content: code,
          diagramType: 'mermaid',
        })
      } else if (language === 'yaml' || language === 'yml') {
        outputs.push({
          type: 'yaml',
          content: code,
          language: 'yaml',
        })
      } else if (language === 'json') {
        outputs.push({
          type: 'json',
          content: code,
          language: 'json',
        })
      } else {
        outputs.push({
          type: 'code',
          content: code,
          language: language,
        })
      }
    }
    
    // 3. Detect inline code
    const inlineCodeRegex = /`([^`]+)`/g
    while ((match = inlineCodeRegex.exec(content)) !== null) {
      const code = match[1]
      // Skip if already in a code block
      if (!codeBlockRegex.test(code)) {
        outputs.push({
          type: 'code',
          content: code,
          language: 'text',
          inline: true,
        })
      }
    }
    
    // 4. Detect LaTeX/Math
    // Block math: $$ ... $$
    const blockMathRegex = /\$\$([\s\S]*?)\$\$/g
    while ((match = blockMathRegex.exec(content)) !== null) {
      outputs.push({
        type: 'math',
        content: match[1],
        inline: false,
      })
    }
    
    // Inline math: \( ... \) or $ ... $
    const inlineMathRegex = /\\?\(([^)]+)\)|\\?\$([^$]+)\$/g
    while ((match = inlineMathRegex.exec(content)) !== null) {
      outputs.push({
        type: 'math',
        content: match[1] || match[2],
        inline: true,
      })
    }
    
    // 5. Detect images (markdown format)
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g
    while ((match = imageRegex.exec(content)) !== null) {
      outputs.push({
        type: 'image',
        url: match[2],
        alt: match[1],
        content: '', // Images don't need text content
      })
    }
    
    // 6. Detect base64 images
    const base64ImageRegex = /data:image\/([^;]+);base64,([A-Za-z0-9+/=]+)/g
    while ((match = base64ImageRegex.exec(content)) !== null) {
      outputs.push({
        type: 'image',
        url: match[0], // Full data URL
        alt: 'Image',
        content: '',
      })
    }
    
    // 7. Detect video URLs
    const videoRegex = /(https?:\/\/[^\s]+\.(mp4|webm|ogg|mov|avi|mkv))/gi
    while ((match = videoRegex.exec(content)) !== null) {
      outputs.push({
        type: 'video',
        url: match[1],
        videoType: match[2],
        content: '',
      })
    }
    
    // 8. Detect JSON chart configs
    const jsonChartRegex = /```json:chart\s*\n([\s\S]*?)```/g
    while ((match = jsonChartRegex.exec(content)) !== null) {
      try {
        const chartConfig = JSON.parse(match[1])
        outputs.push({
          type: 'chart',
          data: chartConfig.data,
          chartType: chartConfig.type || 'line',
          config: chartConfig.config,
          content: '',
        })
      } catch (e) {
        // Invalid JSON, skip
      }
    }
    
    // 9. Detect Lottie animations
    const lottieRegex = /```json:lottie\s*\n([\s\S]*?)```/g
    while ((match = lottieRegex.exec(content)) !== null) {
      try {
        const animation = JSON.parse(match[1])
        outputs.push({
          type: 'animation',
          animation: animation,
          animationType: 'lottie',
          content: '',
        })
      } catch (e) {
        // Invalid JSON, skip
      }
    }
    
    // 10. Remove detected content from remaining text
    // (This will be handled by the renderer - we'll render detected outputs separately)
    
    return outputs
  }
  
  /**
   * Get remaining markdown content after extracting special outputs
   */
  static getRemainingMarkdown(
    content: string,
    detectedOutputs: DetectedOutput[]
  ): string {
    let remaining = content
    
    // Remove code blocks
    remaining = remaining.replace(/```[\s\S]*?```/g, '')
    
    // Remove math blocks
    remaining = remaining.replace(/\$\$[\s\S]*?\$\$/g, '')
    remaining = remaining.replace(/\\?\([^)]+\)/g, '')
    remaining = remaining.replace(/\\?\$[^$]+\$/g, '')
    
    // Remove images
    remaining = remaining.replace(/!\[[^\]]*\]\([^)]+\)/g, '')
    remaining = remaining.replace(/data:image\/[^;]+;base64,[A-Za-z0-9+/=]+/g, '')
    
    // Remove video URLs (but keep text around them)
    remaining = remaining.replace(/(https?:\/\/[^\s]+\.(mp4|webm|ogg|mov|avi|mkv))/gi, '')
    
    return remaining.trim()
  }
}

