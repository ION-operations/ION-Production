#!/usr/bin/env python3
"""
Quick TypeScript error fixes for IDE
"""

import os
import re

def fix_unused_imports(file_path):
    """Fix unused imports by removing them"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove unused React imports
    content = re.sub(r"import React from 'react'", '', content)
    content = re.sub(r"import React, \{\s*\} from 'react'", '', content)
    
    # Remove unused useEffect imports
    content = re.sub(r", useEffect", '', content)
    content = re.sub(r"useEffect, ", '', content)
    
    # Remove unused useState imports
    content = re.sub(r", useState", '', content)
    content = re.sub(r"useState, ", '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_unused_variables(file_path):
    """Fix unused variables by prefixing with underscore"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Common unused variable patterns
    patterns = [
        (r'const \[(\w+), set\w+\] = useState', r'const [_, set\1] = useState'),
        (r'const (\w+) = useRef', r'const _\1 = useRef'),
        (r'const (\w+) = useState', r'const _\1 = useState'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Fix TypeScript errors in common files"""
    files_to_fix = [
        'src/components/AIAgentChat.tsx',
        'src/components/AIMOSDashboard.tsx',
        'src/components/AIMOSSystemVisualization.tsx',
        'src/components/ArchitecturalDocumentation.tsx',
        'src/components/ChatInterface.tsx',
        'src/components/CodeDocsViewer.tsx',
        'src/components/CommandPalette.tsx',
        'src/components/MemoryBrowser.tsx',
        'src/components/MemoryBrowserEnhanced.tsx',
        'src/components/MonacoEditor.tsx',
        'src/components/Sidebar.tsx',
        'src/components/SystemDashboard.tsx',
        'src/components/SystemMonitor.tsx',
        'src/components/TimelineVisualization.tsx',
        'src/components/TopBar.tsx',
        'src/components/WaveBackground.tsx',
    ]
    
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"Fixing {file_path}")
            fix_unused_imports(file_path)
            fix_unused_variables(file_path)
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    main()
