/**
 * LUCID Document Editor - KaTeX Math Renderer
 * 
 * Math rendering component using KaTeX
 */

import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';

export interface MathRendererProps {
  content: string;
  display?: 'inline' | 'block';
  errorColor?: string;
}

export const MathRenderer: React.FC<MathRendererProps> = ({
  content,
  display = 'inline',
  errorColor = '#cc0000',
}) => {
  try {
    if (display === 'block') {
      return <BlockMath math={content} errorColor={errorColor} />;
    }
    return <InlineMath math={content} errorColor={errorColor} />;
  } catch (error) {
    return (
      <span style={{ color: errorColor }}>
        [Math Error: {error instanceof Error ? error.message : 'Unknown error'}]
      </span>
    );
  }
};

/**
 * Extract math blocks from text content
 */
export function extractMathBlocks(content: string): Array<{ type: 'inline' | 'block'; content: string; start: number; end: number }> {
  const blocks: Array<{ type: 'inline' | 'block'; content: string; start: number; end: number }> = [];
  
  // Inline math: $...$ or \(...\)
  const inlineRegex = /\$([^$]+)\$|\\\(([^)]+)\\\)/g;
  let match;
  while ((match = inlineRegex.exec(content)) !== null) {
    blocks.push({
      type: 'inline',
      content: match[1] || match[2],
      start: match.index,
      end: match.index + match[0].length,
    });
  }

  // Block math: $$...$$ or \[...\]
  const blockRegex = /\$\$([^$]+)\$\$|\\\[([^\]]+)\\\]/gs;
  while ((match = blockRegex.exec(content)) !== null) {
    blocks.push({
      type: 'block',
      content: match[1] || match[2],
      start: match.index,
      end: match.index + match[0].length,
    });
  }

  return blocks.sort((a, b) => a.start - b.start);
}

/**
 * Render content with math blocks
 */
export function renderContentWithMath(content: string): React.ReactNode[] {
  const mathBlocks = extractMathBlocks(content);
  const nodes: React.ReactNode[] = [];
  let lastIndex = 0;

  for (const block of mathBlocks) {
    // Add text before math block
    if (block.start > lastIndex) {
      const text = content.substring(lastIndex, block.start);
      if (text) {
        nodes.push(<span key={`text-${lastIndex}`}>{text}</span>);
      }
    }

    // Add math block
    nodes.push(
      <MathRenderer
        key={`math-${block.start}`}
        content={block.content}
        display={block.type}
      />
    );

    lastIndex = block.end;
  }

  // Add remaining text
  if (lastIndex < content.length) {
    const text = content.substring(lastIndex);
    if (text) {
      nodes.push(<span key={`text-${lastIndex}`}>{text}</span>);
    }
  }

  return nodes.length > 0 ? nodes : [<span key="empty">{content}</span>];
}

