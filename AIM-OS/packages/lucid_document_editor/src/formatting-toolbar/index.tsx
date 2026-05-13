/**
 * LUCID Document Editor - Formatting Toolbar
 * 
 * Toolbar component for text formatting (bold, italic, underline, etc.)
 */

import React from 'react';
import { useSlate } from 'slate-react';
import { Editor, Transforms, Text, Element as SlateElement } from 'slate';
import { Bold, Italic, Underline, Code, Heading1, Heading2, Heading3, List, Quote } from 'lucide-react';

export interface FormattingToolbarProps {
  className?: string;
}

const isMarkActive = (editor: Editor, format: string) => {
  const marks = Editor.marks(editor);
  return marks ? marks[format as keyof typeof marks] === true : false;
};

const toggleMark = (editor: Editor, format: string) => {
  const isActive = isMarkActive(editor, format);
  
  if (isActive) {
    Editor.removeMark(editor, format);
  } else {
    Editor.addMark(editor, format, true);
  }
};

const isBlockActive = (editor: Editor, format: string) => {
  const { selection } = editor;
  if (!selection) return false;
  
  const [match] = Array.from(
    Editor.nodes(editor, {
      at: Editor.unhangRange(editor, selection),
      match: (n) => !Editor.isEditor(n) && Editor.isBlock(editor, n) && (n as any).type === format,
    })
  );
  
  return !!match;
};

const toggleBlock = (editor: Editor, format: string, level?: number) => {
  const isActive = isBlockActive(editor, format);
  const isList = format === 'list-item';
  
  Transforms.unwrapNodes(editor, {
    match: (n) => !Editor.isEditor(n) && Editor.isBlock(editor, n) && (n as any).type === 'list-item',
    split: true,
  });
  
  let newProperties: Partial<any>;
  if (isActive) {
    newProperties = { type: 'paragraph' };
  } else if (isList) {
    newProperties = { type: 'list-item' };
  } else if (format === 'heading') {
    newProperties = { type: 'heading', level: level || 1 };
  } else {
    newProperties = { type: format };
  }
  
  Transforms.setNodes<SlateElement>(editor, newProperties);
  
  if (!isActive && isList) {
    const block = { type: 'list-item', children: [] };
    Transforms.wrapNodes(editor, block);
  }
};

const ToolbarButton: React.FC<{
  icon: React.ReactNode;
  isActive: boolean;
  onMouseDown: (e: React.MouseEvent) => void;
  title: string;
}> = ({ icon, isActive, onMouseDown, title }) => {
  return (
    <button
      onMouseDown={onMouseDown}
      style={{
        padding: '6px 10px',
        margin: '0 2px',
        backgroundColor: isActive ? '#094771' : 'transparent',
        border: '1px solid #3e3e42',
        borderRadius: '3px',
        cursor: 'pointer',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: isActive ? '#ffffff' : '#cccccc',
        transition: 'all 0.15s ease',
      }}
      title={title}
    >
      {icon}
    </button>
  );
};

export const FormattingToolbar: React.FC<FormattingToolbarProps> = ({ className }) => {
  const editor = useSlate();

  return (
    <div
      className={className}
      style={{
        display: 'flex',
        gap: '4px',
        padding: '8px 12px',
        borderBottom: '1px solid #3e3e42',
        backgroundColor: '#252526',
        flexWrap: 'wrap',
      }}
      onMouseDown={(e) => e.preventDefault()}
    >
      <ToolbarButton
        icon={<Bold size={16} />}
        isActive={isMarkActive(editor, 'bold')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleMark(editor, 'bold');
        }}
        title="Bold"
      />
      <ToolbarButton
        icon={<Italic size={16} />}
        isActive={isMarkActive(editor, 'italic')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleMark(editor, 'italic');
        }}
        title="Italic"
      />
      <ToolbarButton
        icon={<Underline size={16} />}
        isActive={isMarkActive(editor, 'underline')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleMark(editor, 'underline');
        }}
        title="Underline"
      />
      <ToolbarButton
        icon={<Code size={16} />}
        isActive={isMarkActive(editor, 'code')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleMark(editor, 'code');
        }}
        title="Code"
      />
      <div style={{ width: '1px', backgroundColor: '#ccc', margin: '0 4px' }} />
      <ToolbarButton
        icon={<Heading1 size={16} />}
        isActive={isBlockActive(editor, 'heading')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleBlock(editor, 'heading', 1);
        }}
        title="Heading 1"
      />
      <ToolbarButton
        icon={<Heading2 size={16} />}
        isActive={false}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleBlock(editor, 'heading', 2);
        }}
        title="Heading 2"
      />
      <ToolbarButton
        icon={<Heading3 size={16} />}
        isActive={false}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleBlock(editor, 'heading', 3);
        }}
        title="Heading 3"
      />
      <div style={{ width: '1px', backgroundColor: '#ccc', margin: '0 4px' }} />
      <ToolbarButton
        icon={<List size={16} />}
        isActive={isBlockActive(editor, 'list-item')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleBlock(editor, 'list-item');
        }}
        title="List"
      />
      <ToolbarButton
        icon={<Quote size={16} />}
        isActive={isBlockActive(editor, 'quote')}
        onMouseDown={(e) => {
          e.preventDefault();
          toggleBlock(editor, 'quote');
        }}
        title="Quote"
      />
    </div>
  );
};

