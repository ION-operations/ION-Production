import React, { useEffect } from 'react';
import { Layout } from './components/Layout/Layout';
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary';
import { useCustomization } from './hooks/useCustomization';
import { useKeyboardNavigation } from './hooks/useKeyboardNavigation';
import './index.css';

function App() {
  const { initializeDefaultTemplates } = useCustomization();
  
  // Initialize keyboard navigation
  useKeyboardNavigation();

  useEffect(() => {
    // Initialize default layout templates on mount
    initializeDefaultTemplates();
    
    // Set dynamic title with port
    const port = window.location.port || '5176';
    document.title = `[MAX] IDE Prototype - Port ${port}`;
  }, [initializeDefaultTemplates]);

  return (
    <ErrorBoundary>
      <div className="app" role="application" aria-label="IDE Prototype">
        <Layout />
      </div>
    </ErrorBoundary>
  );
}

export default App;

