/**
 * FilePreview Component - Cursor IDE-style File Preview
 * 
 * Displays markdown files with proper text formatting and syntax-highlighted code blocks.
 * Supports:
 * - Markdown rendering (headings, lists, bold, italic, etc.)
 * - Syntax-highlighted code blocks using Monaco Editor
 * - Math rendering with KaTeX (LaTeX support)
 * - Inline code highlighting
 * - Copy buttons for code blocks
 */

import React, { useMemo, useState } from 'react'
import Editor from '@monaco-editor/react'
import { marked } from 'marked'
import { InlineMath, BlockMath } from 'react-katex'
import 'katex/dist/katex.min.css'
import { 
  Copy, Check, Image as ImageIcon, AlertCircle, 
  CheckCircle, XCircle, Info, Star, Heart, Zap,
  Sparkles, Moon, Sun, Cloud, Leaf, Flower, Diamond,
  Target, Shield, Rocket, Trophy, Gem, Crown, Flame,
  Lightbulb, Brain, Code, FileText, Folder, Settings,
  Search, Bell, Bookmark, Tag, Link, Download, Upload,
  Play, Pause, Square, SkipForward, SkipBack, Volume2,
  Music, Video, Camera, Film, Palette, Brush, PenTool
} from 'lucide-react'
import type { TokensList, Token } from 'marked'

export interface FilePreviewProps {
  content: string
  language?: string
  theme?: 'vs-dark' | 'vs-light'
  showLineNumbers?: boolean
  className?: string
}

interface CodeBlockState {
  copied: boolean
}

export const FilePreview: React.FC<FilePreviewProps> = ({
  content,
  language = 'markdown',
  theme = 'vs-dark',
  showLineNumbers = false,
  className = '',
}) => {
  const [copiedBlocks, setCopiedBlocks] = useState<Record<number, boolean>>({})

  const renderedContent = useMemo(() => {
    return renderMarkdownWithCodeHighlighting(
      content,
      theme,
      showLineNumbers,
      copiedBlocks,
      setCopiedBlocks
    )
  }, [content, theme, showLineNumbers, copiedBlocks])

  return (
    <div className={`file-preview h-full overflow-y-auto p-6 bg-gray-900 text-gray-100 ${className}`}>
      <div className="max-w-4xl mx-auto prose prose-invert prose-sm max-w-none">
        {renderedContent}
      </div>
    </div>
  )
}

/**
 * Render markdown content with code blocks and math support
 */
function renderMarkdownWithCodeHighlighting(
  content: string,
  theme: string,
  showLineNumbers: boolean,
  copiedBlocks: Record<number, boolean>,
  setCopiedBlocks: React.Dispatch<React.SetStateAction<Record<number, boolean>>>
): React.ReactNode[] {
  // Configure marked options
  marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true,
    mangle: false,
    pedantic: false,
    sanitize: false,
    smartLists: true,
    smartypants: false,
  })

  // Parse markdown
  const tokens = marked.lexer(content)
  const elements: React.ReactNode[] = []
  let codeBlockIndex = 0
  let tokenIndex = 0

  for (const token of tokens) {
    if (token.type === 'code') {
      // Render code block with Monaco
      const codeToken = token as Token.Code
      elements.push(
        <MonacoCodeBlock
          key={`code-${codeBlockIndex}`}
          code={codeToken.text}
          language={codeToken.lang || 'plaintext'}
          theme={theme}
          showLineNumbers={showLineNumbers}
          blockIndex={codeBlockIndex}
          copied={copiedBlocks[codeBlockIndex] || false}
          onCopy={() => {
            navigator.clipboard.writeText(codeToken.text)
            setCopiedBlocks(prev => ({ ...prev, [codeBlockIndex]: true }))
            setTimeout(() => {
              setCopiedBlocks(prev => ({ ...prev, [codeBlockIndex]: false }))
            }, 2000)
          }}
        />
      )
      codeBlockIndex++
    } else if (token.type === 'image') {
      // Render images with professional styling
      const imageToken = token as Token.Image
      elements.push(
        <ProfessionalImage
          key={`image-${tokenIndex}`}
          src={imageToken.href}
          alt={imageToken.text}
          title={imageToken.title || imageToken.text}
        />
      )
    } else if (token.type === 'paragraph') {
      // Check for math and images in paragraph
      const paraToken = token as Token.Paragraph
      const text = paraToken.text
      
      // Check if paragraph contains only an image (common markdown pattern)
      const imageMatch = text.match(/^!\[([^\]]*)\]\(([^)]+)\)(?:\s+"([^"]+)")?$/)
      if (imageMatch) {
        elements.push(
          <ProfessionalImage
            key={`image-inline-${tokenIndex}`}
            src={imageMatch[2]}
            alt={imageMatch[1]}
            title={imageMatch[3]}
          />
        )
      } else {
        // Regular paragraph with math and emoji replacement
        const mathNodes = renderContentWithMath(text)
        elements.push(
          <p key={`para-${tokenIndex}`} className="mb-4 text-gray-300 leading-relaxed">
            {mathNodes}
          </p>
        )
      }
    } else if (token.type === 'heading') {
      // Render headings with proper styling
      const headingToken = token as Token.Heading
      const HeadingTag = `h${headingToken.depth}` as keyof JSX.IntrinsicElements
      const headingText = headingToken.text
      const headingId = headingText.toLowerCase().replace(/[^a-z0-9]+/g, '-')
      
      const headingClasses = {
        1: 'text-3xl font-bold text-white mt-8 mb-4 pb-2 border-b border-gray-700',
        2: 'text-2xl font-bold text-white mt-6 mb-3 pb-2 border-b border-gray-700',
        3: 'text-xl font-semibold text-white mt-5 mb-2',
        4: 'text-lg font-semibold text-white mt-4 mb-2',
        5: 'text-base font-semibold text-white mt-3 mb-2',
        6: 'text-sm font-semibold text-gray-300 mt-3 mb-2',
      }

      elements.push(
        <HeadingTag
          key={`heading-${tokenIndex}`}
          id={headingId}
          className={headingClasses[headingToken.depth as keyof typeof headingClasses]}
        >
          {renderContentWithMath(headingText)}
        </HeadingTag>
      )
    } else if (token.type === 'list') {
      // Render lists
      const listToken = token as Token.List
      const ListTag = listToken.ordered ? 'ol' : 'ul'
      const listItems = listToken.items.map((item, idx) => {
        const itemText = typeof item.text === 'string' ? item.text : item.text.map(t => t.raw).join('')
        return (
          <li key={`item-${idx}`} className="mb-2 text-gray-300">
            {renderContentWithMath(itemText)}
          </li>
        )
      })

      elements.push(
        <ListTag
          key={`list-${tokenIndex}`}
          className={`mb-4 ${listToken.ordered ? 'list-decimal ml-6' : 'list-disc ml-6'}`}
        >
          {listItems}
        </ListTag>
      )
    } else if (token.type === 'blockquote') {
      // Render blockquotes
      const blockquoteToken = token as Token.Blockquote
      const blockquoteText = blockquoteToken.tokens.map(t => t.raw).join('')
      elements.push(
        <blockquote
          key={`blockquote-${tokenIndex}`}
          className="border-l-4 border-gray-600 pl-4 py-2 my-4 italic text-gray-400 bg-gray-800/50 rounded-r"
        >
          {renderContentWithMath(blockquoteText)}
        </blockquote>
      )
    } else if (token.type === 'hr') {
      // Render horizontal rule
      elements.push(
        <hr key={`hr-${tokenIndex}`} className="my-6 border-gray-700" />
      )
    } else {
      // Render other tokens as HTML (including HTML img tags)
      try {
        const html = marked.parser([token] as TokensList)
        // Replace HTML img tags with ProfessionalImage components
        const processedHtml = html.replace(
          /<img\s+([^>]*?)>/gi,
          (match, attributes) => {
            const srcMatch = attributes.match(/src=["']([^"']+)["']/i)
            const altMatch = attributes.match(/alt=["']([^"']*)["']/i)
            const titleMatch = attributes.match(/title=["']([^"']*)["']/i)
            
            if (srcMatch) {
              const src = srcMatch[1]
              const alt = altMatch ? altMatch[1] : ''
              const title = titleMatch ? titleMatch[1] : alt
              return `<!--PROFESSIONAL_IMAGE:${src}:${alt}:${title}-->`
            }
            return match
          }
        )
        
        // Check if we have any professional image placeholders
        if (processedHtml.includes('<!--PROFESSIONAL_IMAGE:')) {
          const parts = processedHtml.split(/(<!--PROFESSIONAL_IMAGE:[^>]+-->)/)
          const htmlParts = parts.map((part, idx) => {
            const imageMatch = part.match(/<!--PROFESSIONAL_IMAGE:([^:]+):([^:]*):([^>]*)-->/)
            if (imageMatch) {
              return (
                <ProfessionalImage
                  key={`html-image-${tokenIndex}-${idx}`}
                  src={imageMatch[1]}
                  alt={imageMatch[2]}
                  title={imageMatch[3] || imageMatch[2]}
                />
              )
            }
            return (
              <div
                key={`html-${tokenIndex}-${idx}`}
                className="markdown-content"
                dangerouslySetInnerHTML={{ __html: part }}
              />
            )
          })
          elements.push(...htmlParts)
        } else {
          elements.push(
            <div
              key={`token-${tokenIndex}`}
              className="markdown-content"
              dangerouslySetInnerHTML={{ __html: processedHtml }}
            />
          )
        }
      } catch (error) {
        // Fallback for unsupported tokens
        console.warn('Unsupported token type:', token.type, token)
      }
    }
    tokenIndex++
  }

  return elements.length > 0 ? elements : [<div key="empty" className="text-gray-500">No content to display</div>]
}

/**
 * Professional Emoji-to-Icon Mapping
 * Replaces standard emojis with high-grade professional icons
 */
const EMOJI_TO_ICON_MAP: Record<string, React.ComponentType<{ className?: string; size?: number }>> = {
  // Status & Actions
  '✅': CheckCircle,
  '✓': CheckCircle,
  '✔': CheckCircle,
  '❌': XCircle,
  '✗': XCircle,
  '✖': XCircle,
  '⚠️': AlertCircle,
  '⚠': AlertCircle,
  '❗': AlertCircle,
  '❓': Info,
  'ℹ️': Info,
  'ℹ': Info,
  
  // Stars & Quality
  '⭐': Star,
  '🌟': Sparkles,
  '✨': Sparkles,
  '💫': Sparkles,
  
  // Emotions & Feelings
  '❤️': Heart,
  '💙': Heart,
  '💚': Heart,
  '💛': Heart,
  '🧡': Heart,
  '💜': Heart,
  
  // Energy & Power
  '⚡': Zap,
  '🔥': Flame,
  '💎': Diamond,
  '💍': Gem,
  '👑': Crown,
  
  // Nature
  '🌙': Moon,
  '🌛': Moon,
  '🌜': Moon,
  '☀️': Sun,
  '☀': Sun,
  '☁️': Cloud,
  '☁': Cloud,
  '🌿': Leaf,
  '🍀': Leaf,
  '🌺': Flower,
  '🌸': Flower,
  
  // Objects & Tools
  '🎯': Target,
  '🛡️': Shield,
  '🛡': Shield,
  '🚀': Rocket,
  '🏆': Trophy,
  '💡': Lightbulb,
  '🧠': Brain,
  '📝': FileText,
  '📄': FileText,
  '📁': Folder,
  '⚙️': Settings,
  '⚙': Settings,
  '🔍': Search,
  '🔎': Search,
  '🔔': Bell,
  '🔖': Bookmark,
  '🏷️': Tag,
  '🏷': Tag,
  '🔗': Link,
  '📥': Download,
  '📤': Upload,
  
  // Media
  '▶️': Play,
  '▶': Play,
  '⏸️': Pause,
  '⏸': Pause,
  '⏹️': Square,
  '⏹': Square,
  '⏭️': SkipForward,
  '⏭': SkipForward,
  '⏮️': SkipBack,
  '⏮': SkipBack,
  '🔊': Volume2,
  '🎵': Music,
  '🎶': Music,
  '🎬': Film,
  '📹': Video,
  '📷': Camera,
  '🎨': Palette,
  '🖌️': Brush,
  '🖊️': PenTool,
  '🖊': PenTool,
}

/**
 * Replace emojis with professional icons
 */
function replaceEmojisWithIcons(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{FE00}-\u{FE0F}]|[\u{1F900}-\u{1F9FF}]|[\u{1F1E0}-\u{1F1FF}]/gu
  let lastIndex = 0
  let match

  while ((match = emojiRegex.exec(text)) !== null) {
    // Add text before emoji
    if (match.index > lastIndex) {
      const beforeText = text.substring(lastIndex, match.index)
      if (beforeText) {
        nodes.push(<span key={`text-${lastIndex}`}>{beforeText}</span>)
      }
    }

    // Replace emoji with icon
    const emoji = match[0]
    const IconComponent = EMOJI_TO_ICON_MAP[emoji]
    
    if (IconComponent) {
      nodes.push(
        <IconComponent
          key={`icon-${match.index}`}
          className="inline-block w-4 h-4 mx-0.5 align-middle text-blue-400"
          size={16}
        />
      )
    } else {
      // Keep emoji if no icon mapping found
      nodes.push(<span key={`emoji-${match.index}`}>{emoji}</span>)
    }

    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < text.length) {
    const remainingText = text.substring(lastIndex)
    if (remainingText) {
      nodes.push(<span key={`text-final-${lastIndex}`}>{remainingText}</span>)
    }
  }

  return nodes.length > 0 ? nodes : [<span key="text">{text}</span>]
}

/**
 * Render content with math blocks (inline and block) and emoji replacement
 */
function renderContentWithMath(content: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  let lastIndex = 0

  // Inline math: $...$ or \(...\)
  const inlineMathRegex = /\$([^$\n]+)\$|\\\(([^)]+)\\\)/g
  let match

  while ((match = inlineMathRegex.exec(content)) !== null) {
    // Add text before math
    if (match.index > lastIndex) {
      const text = content.substring(lastIndex, match.index)
      if (text) {
        nodes.push(<span key={`text-${lastIndex}`}>{renderInlineCodeAndEmojis(text)}</span>)
      }
    }

    // Add inline math
    const mathContent = match[1] || match[2]
    nodes.push(
      <InlineMath
        key={`math-inline-${match.index}`}
        math={mathContent}
        errorColor="#cc0000"
      />
    )

    lastIndex = match.index + match[0].length
  }

  // Block math: $$...$$ or \[...\]
  const blockMathRegex = /\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\]/g
  lastIndex = 0

  while ((match = blockMathRegex.exec(content)) !== null) {
    // Add text before math
    if (match.index > lastIndex) {
      const text = content.substring(lastIndex, match.index)
      if (text) {
        nodes.push(<span key={`text-block-${lastIndex}`}>{renderInlineCodeAndEmojis(text)}</span>)
      }
    }

    // Add block math
    const mathContent = match[1] || match[2]
    nodes.push(
      <div key={`math-block-${match.index}`} className="my-4">
        <BlockMath math={mathContent} errorColor="#cc0000" />
      </div>
    )

    lastIndex = match.index + match[0].length
  }

  // Add remaining text
  if (lastIndex < content.length) {
    const text = content.substring(lastIndex)
    if (text) {
      nodes.push(<span key={`text-final-${lastIndex}`}>{renderInlineCodeAndEmojis(text)}</span>)
    }
  }

  return nodes.length > 0 ? nodes : [<span key="empty">{renderInlineCodeAndEmojis(content)}</span>]
}

/**
 * Render inline code with syntax highlighting and emoji replacement
 */
function renderInlineCodeAndEmojis(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  const codeRegex = /`([^`]+)`/g
  let lastIndex = 0
  let match

  while ((match = codeRegex.exec(text)) !== null) {
    // Add text before code (with emoji replacement)
    if (match.index > lastIndex) {
      const beforeText = text.substring(lastIndex, match.index)
      if (beforeText) {
        nodes.push(<span key={`text-${lastIndex}`}>{replaceEmojisWithIcons(beforeText)}</span>)
      }
    }

    // Add inline code
    nodes.push(
      <code
        key={`code-${match.index}`}
        className="bg-gray-800 text-green-400 px-1.5 py-0.5 rounded text-sm font-mono"
      >
        {match[1]}
      </code>
    )

    lastIndex = match.index + match[0].length
  }

  // Add remaining text (with emoji replacement)
  if (lastIndex < text.length) {
    const remainingText = text.substring(lastIndex)
    if (remainingText) {
      nodes.push(<span key={`text-final-${lastIndex}`}>{replaceEmojisWithIcons(remainingText)}</span>)
    }
  }

  return nodes.length > 0 ? nodes : [<span key="text">{replaceEmojisWithIcons(text)}</span>]
}

/**
 * Monaco Code Block Component
 */
interface MonacoCodeBlockProps {
  code: string
  language: string
  theme: string
  showLineNumbers: boolean
  blockIndex: number
  copied: boolean
  onCopy: () => void
}

const MonacoCodeBlock: React.FC<MonacoCodeBlockProps> = ({
  code,
  language,
  theme,
  showLineNumbers,
  copied,
  onCopy,
}) => {
  const lineCount = code.split('\n').length
  const height = Math.min(lineCount * 20 + 40, 600) // Max 600px height

  return (
    <div className="code-block-wrapper my-6 rounded-lg overflow-hidden border border-gray-700 bg-gray-950">
      {/* Code Block Header */}
      <div className="code-block-header bg-gray-800 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400 font-mono uppercase">{language}</span>
          <span className="text-xs text-gray-500">
            {lineCount} {lineCount === 1 ? 'line' : 'lines'}
          </span>
        </div>
        <button
          onClick={onCopy}
          className="flex items-center gap-1.5 px-2 py-1 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded transition-colors"
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Monaco Editor */}
      <div style={{ height: `${height}px` }} className="monaco-code-block">
        <Editor
          height="100%"
          language={language}
          value={code}
          theme={theme}
          options={{
            readOnly: true,
            lineNumbers: showLineNumbers ? 'on' : 'off',
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 13,
            wordWrap: 'on',
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
            scrollbar: {
              vertical: 'auto',
              horizontal: 'auto',
              useShadows: false,
            },
          }}
        />
      </div>
    </div>
  )
}

/**
 * Professional Image Component
 * Renders images with high-grade professional styling
 */
interface ProfessionalImageProps {
  src: string
  alt: string
  title?: string
}

const ProfessionalImage: React.FC<ProfessionalImageProps> = ({ src, alt, title }) => {
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)

  const handleImageLoad = () => {
    setImageLoading(false)
  }

  const handleImageError = () => {
    setImageError(true)
    setImageLoading(false)
  }

  if (imageError) {
    return (
      <div className="my-6 p-8 bg-gray-800/50 border border-gray-700 rounded-lg flex flex-col items-center justify-center min-h-[200px]">
        <ImageIcon className="w-12 h-12 text-gray-500 mb-3" />
        <p className="text-sm text-gray-400 mb-1">{alt || 'Image'}</p>
        <p className="text-xs text-gray-500">Failed to load image</p>
        <p className="text-xs text-gray-600 mt-2 font-mono break-all max-w-md text-center">{src}</p>
      </div>
    )
  }

  return (
    <div className="my-6 group">
      <div className="relative bg-gray-800/30 border border-gray-700/50 rounded-lg overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-300 hover:border-gray-600">
        {imageLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800/80">
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-gray-400">Loading image...</span>
            </div>
          </div>
        )}
        <img
          src={src}
          alt={alt}
          title={title}
          onLoad={handleImageLoad}
          onError={handleImageError}
          className={`w-full h-auto transition-opacity duration-300 ${
            imageLoading ? 'opacity-0' : 'opacity-100'
          }`}
          style={{
            maxHeight: '600px',
            objectFit: 'contain',
          }}
        />
        {(title || alt) && (
          <div className="px-4 py-2 bg-gray-800/80 border-t border-gray-700/50">
            <p className="text-xs text-gray-300 font-medium">{title || alt}</p>
            {title && alt && title !== alt && (
              <p className="text-xs text-gray-500 mt-0.5">{alt}</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default FilePreview

