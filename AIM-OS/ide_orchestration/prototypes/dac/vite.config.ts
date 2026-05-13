import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3002,
    open: true,
    // Proxy API requests to Router & Log-Sentinels API Server
    proxy: {
      '/api/router': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api/log-sentinels': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api/system-indexes': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api/system-maps': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api/super-index': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api/goal-tree': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api/hierarchical-navigation': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  },
  // Environment variables support
  envPrefix: ['VITE_', 'MESHY_', 'PENTOPIX_', 'GOOGLE_', 'OPENAI_', 'ELEVENLABS_'],
})

