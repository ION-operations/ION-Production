/**
 * Basic Example - Advanced Monaco Editor
 * 
 * Demonstrates basic usage of the AdvancedMonacoEditor component
 * with minimal configuration
 */

import React, { useState } from 'react';
import { AdvancedMonacoEditor } from '../src/components/AdvancedMonacoEditor';

export const BasicExample: React.FC = () => {
  const [code, setCode] = useState(`// Basic Example
function greetUser(name) {
  console.log(\`Hello, \${name}!\`);
  return \`Welcome, \${name}!\`;
}

const user = "World";
const message = greetUser(user);
console.log(message);
`);

  const handleChange = (newCode: string) => {
    setCode(newCode);
  };

  const handleMount = (editor: any) => {
    console.log('Editor mounted:', editor);
  };

  return (
    <div style={{ height: '400px', border: '1px solid #ccc', borderRadius: '4px' }}>
      <AdvancedMonacoEditor
        value={code}
        language="javascript"
        onChange={handleChange}
        onMount={handleMount}
      />
    </div>
  );
};

export default BasicExample;
