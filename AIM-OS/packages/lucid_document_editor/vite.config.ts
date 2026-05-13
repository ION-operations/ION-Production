import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { copyFileSync, existsSync, mkdirSync } from 'fs';

// Copy PDF.js worker to public directory
function copyPdfWorker() {
  return {
    name: 'copy-pdf-worker',
    buildStart() {
      // Try multiple possible locations for the worker file
      const possiblePaths = [
        path.resolve(__dirname, 'node_modules/pdfjs-dist/build/pdf.worker.min.js'),
        path.resolve(__dirname, 'node_modules/pdfjs-dist/build/pdf.worker.min.mjs'),
        path.resolve(__dirname, 'node_modules/pdfjs-dist/build/pdf.worker.js'),
        path.resolve(__dirname, 'node_modules/pdfjs-dist/build/pdf.worker.mjs'),
      ];
      
      const publicDir = path.resolve(__dirname, 'public');
      const workerDest = path.resolve(publicDir, 'pdf.worker.min.js');
      
      if (!existsSync(publicDir)) {
        mkdirSync(publicDir, { recursive: true });
      }
      
      for (const workerSrc of possiblePaths) {
        if (existsSync(workerSrc)) {
          copyFileSync(workerSrc, workerDest);
          console.log('✅ PDF.js worker copied to public directory from:', workerSrc);
          return;
        }
      }
      
      console.warn('⚠️ PDF.js worker file not found. Will use CDN fallback.');
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const isLibrary = mode === 'library';
  
  return {
    plugins: [react(), copyPdfWorker()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    build: isLibrary ? {
      // Build as library for npm package
      lib: {
        entry: path.resolve(__dirname, 'src/index.ts'),
        name: 'LucidDocumentEditor',
        formats: ['es', 'cjs'],
        fileName: (format) => `index.${format === 'es' ? 'mjs' : 'cjs'}`,
      },
      rollupOptions: {
        external: ['react', 'react-dom'],
        output: {
          globals: {
            react: 'React',
            'react-dom': 'ReactDOM',
          },
        },
      },
    } : {
      // Build as demo app
      outDir: 'dist',
      rollupOptions: {
        input: path.resolve(__dirname, 'index.html'),
      },
    },
    server: {
      port: 3004,
      open: true,
    },
    publicDir: 'public', // Serve static files from public directory
    define: {
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
    },
  };
});

