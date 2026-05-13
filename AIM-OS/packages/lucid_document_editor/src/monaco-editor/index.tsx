/**
 * LUCID Document Editor - Monaco Editor Integration
 * 
 * Monaco Editor wrapper for section editing
 */

import React, { useRef, useEffect, useState } from 'react';
import Editor from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

export interface MonacoSectionEditorProps {
  content: string;
  onChange: (value: string) => void;
  language?: string;
  readOnly?: boolean;
  showLineNumbers?: boolean;
  theme?: string;
  fontSize?: number;
  wordWrap?: 'on' | 'off';
  minimap?: boolean;
  onSelectionChange?: (selection: monaco.Selection | null) => void;
}

export const MonacoSectionEditor: React.FC<MonacoSectionEditorProps> = ({
  content,
  onChange,
  language = 'markdown',
  readOnly = false,
  showLineNumbers = true,
  theme = 'vs-dark',
  fontSize = 14,
  wordWrap = 'on',
  minimap = true,
  onSelectionChange,
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;
    setIsMounted(true);

    // Register selection change listener
    if (onSelectionChange) {
      editor.onDidChangeCursorSelection(() => {
        const selection = editor.getSelection();
        onSelectionChange(selection);
      });
    }

    // Register math syntax highlighting (custom language)
    monaco.languages.register({ id: 'markdown-math' });
    
    // Configure markdown language for math support
    monaco.languages.setMonarchTokensProvider('markdown-math', {
      tokenizer: {
        root: [
          [/\$\$[\s\S]*?\$\$/, 'math-block'],
          [/\$[^\$]+\$/, 'math-inline'],
          [/\\\([\s\S]*?\\\)/, 'math-inline'],
          [/\\\[[\s\S]*?\\\]/, 'math-block'],
        ],
      },
    });
  };

  useEffect(() => {
    if (editorRef.current && content !== editorRef.current.getValue()) {
      editorRef.current.setValue(content);
    }
  }, [content]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <Editor
        height="100%"
        language={language}
        value={content}
        theme={theme}
        onChange={(value) => onChange(value || '')}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          lineNumbers: showLineNumbers ? 'on' : 'off',
          fontSize,
          wordWrap,
          minimap: { enabled: minimap },
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          insertSpaces: true,
          formatOnPaste: true,
          formatOnType: true,
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnEnter: 'on',
          quickSuggestions: true,
        }}
      />
    </div>
  );
};

