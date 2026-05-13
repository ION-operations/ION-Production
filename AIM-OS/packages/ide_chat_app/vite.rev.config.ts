import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

/**
 * Vite Config for Rev's IDE Prototype
 * 
 * Uses port 5180 (Rev's assigned port per protocol)
 * IMPORTANT: Sam's IDE uses port 3000 - DO NOT CONFLICT
 * Entry point: indexRev.html -> mainRev.tsx -> AppRev.tsx -> RevIDELayout
 */

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5180, // Rev's assigned port (DO NOT CHANGE - conflicts with Sam's IDE on 3000)
    strictPort: true, // FAIL if port is taken (prevents confusion with Sam's IDE)
    host: true,
    open: false // Don't auto-open, launcher will handle it
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      input: resolve(__dirname, 'indexRev.html')
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})

