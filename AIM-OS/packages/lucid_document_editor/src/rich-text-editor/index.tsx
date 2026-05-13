/**
 * LUCID Document Editor - Slate Rich Text Editor
 * 
 * Slate.js integration for rich text editing with formatting support
 */

import React, { useMemo, useCallback } from 'react';
import { createEditor, Descendant, Editor, Transforms, Text, Element as SlateElement } from 'slate';
import { Slate, Editable, withReact, RenderElementProps, RenderLeafProps, useSlate } from 'slate-react';
import { withHistory } from 'slate-history';
import { MathRenderer, extractMathBlocks } from '../math-renderer';
import { FormattingToolbar } from '../formatting-toolbar';

export interface RichTextEditorProps {
  content: string;
  onChange: (value: string) => void;
  placeholder?: string;
  readOnly?: boolean;
  onSelectionChange?: (selection: any) => void;
}

// Custom types for Slate
type CustomElement = {
  type: 'paragraph' | 'heading' | 'math-block' | 'code-block' | 'list-item' | 'quote';
  level?: number;
  children: CustomText[];
};

type CustomText = {
  text: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  code?: boolean;
  math?: boolean;
  mathContent?: string;
};

declare module 'slate' {
  interface CustomTypes {
    Editor: Editor;
    Element: CustomElement;
    Text: CustomText;
  }
}

// Default value
const initialValue: Descendant[] = [
  {
    type: 'paragraph',
    children: [{ text: '' }],
  },
];

// Serialize Slate value to markdown
function serialize(value: Descendant[]): string {
  return value
    .map((node) => {
      if (SlateElement.isElement(node)) {
        const children = node.children.map((n) => (Text.isText(n) ? n.text : '')).join('');
        
        switch (node.type) {
          case 'heading':
            const level = node.level || 1;
            return `${'#'.repeat(level)} ${children}\n`;
          case 'math-block':
            return `$$\n${children}\n$$\n`;
          case 'code-block':
            return `\`\`\`\n${children}\n\`\`\`\n`;
          case 'quote':
            return `> ${children}\n`;
          case 'list-item':
            return `- ${children}\n`;
          default:
            return `${children}\n`;
        }
      }
      return '';
    })
    .join('\n');
}

// Deserialize markdown to Slate value
function deserialize(markdown: string): Descendant[] {
  const lines = markdown.split('\n');
  const nodes: Descendant[] = [];
  
  for (const line of lines) {
    if (line.startsWith('# ')) {
      nodes.push({
        type: 'heading',
        level: 1,
        children: [{ text: line.substring(2) }],
      });
    } else if (line.startsWith('## ')) {
      nodes.push({
        type: 'heading',
        level: 2,
        children: [{ text: line.substring(3) }],
      });
    } else if (line.startsWith('### ')) {
      nodes.push({
        type: 'heading',
        level: 3,
        children: [{ text: line.substring(4) }],
      });
    } else if (line.startsWith('> ')) {
      nodes.push({
        type: 'quote',
        children: [{ text: line.substring(2) }],
      });
    } else if (line.startsWith('- ')) {
      nodes.push({
        type: 'list-item',
        children: [{ text: line.substring(2) }],
      });
    } else if (line.trim()) {
      nodes.push({
        type: 'paragraph',
        children: [{ text: line }],
      });
    }
  }
  
  return nodes.length > 0 ? nodes : initialValue;
}

// Element renderer
const Element = ({ attributes, children, element }: RenderElementProps) => {
  switch (element.type) {
    case 'heading':
      const level = element.level || 1;
      const HeadingTag = `h${level}` as keyof JSX.IntrinsicElements;
      return <HeadingTag {...attributes}>{children}</HeadingTag>;
    case 'math-block':
      return (
        <div {...attributes} style={{ margin: '16px 0', textAlign: 'center' }}>
          <MathRenderer content={element.children.map((n: any) => n.text).join('')} display="block" />
        </div>
      );
    case 'code-block':
      return (
        <pre {...attributes} style={{ backgroundColor: '#f5f5f5', padding: '8px', borderRadius: '4px' }}>
          <code>{children}</code>
        </pre>
      );
    case 'quote':
      return (
        <blockquote {...attributes} style={{ borderLeft: '4px solid #ccc', paddingLeft: '16px', margin: '8px 0' }}>
          {children}
        </blockquote>
      );
    case 'list-item':
      return (
        <li {...attributes}>{children}</li>
      );
    default:
      return <p {...attributes}>{children}</p>;
  }
};

// Leaf renderer
const Leaf = ({ attributes, children, leaf }: RenderLeafProps) => {
  if (leaf.bold) {
    children = <strong>{children}</strong>;
  }
  if (leaf.italic) {
    children = <em>{children}</em>;
  }
  if (leaf.underline) {
    children = <u>{children}</u>;
  }
  if (leaf.code) {
    children = <code style={{ backgroundColor: '#f5f5f5', padding: '2px 4px', borderRadius: '2px' }}>{children}</code>;
  }
  if (leaf.math && leaf.mathContent) {
    return (
      <span {...attributes}>
        <MathRenderer content={leaf.mathContent} display="inline" />
      </span>
    );
  }
  return <span {...attributes}>{children}</span>;
};

export const RichTextEditor: React.FC<RichTextEditorProps> = ({
  content,
  onChange,
  placeholder = 'Start typing...',
  readOnly = false,
  onSelectionChange,
}) => {
  const editor = useMemo(() => withHistory(withReact(createEditor())), []);
  
  const value = useMemo(() => {
    try {
      return deserialize(content);
    } catch {
      return initialValue;
    }
  }, [content]);

  const handleChange = useCallback((newValue: Descendant[]) => {
    const serialized = serialize(newValue);
    onChange(serialized);
  }, [onChange]);

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <Slate editor={editor} initialValue={value} onChange={handleChange}>
        <FormattingToolbar />
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          <Editable
            readOnly={readOnly}
            renderElement={Element}
            renderLeaf={Leaf}
            placeholder={placeholder}
            style={{
              minHeight: '200px',
              outline: 'none',
            }}
          />
        </div>
      </Slate>
    </div>
  );
};

