#!/usr/bin/env node

/**
 * Production Build Script
 * Optimized build process for production deployment
 */

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

console.log('🚀 Starting production build...')

// Set production environment
process.env.NODE_ENV = 'production'
process.env.VITE_NODE_ENV = 'production'

try {
  // Clean previous builds
  console.log('🧹 Cleaning previous builds...')
  if (fs.existsSync('dist')) {
    fs.rmSync('dist', { recursive: true, force: true })
  }

  // Run TypeScript compilation
  console.log('📝 Compiling TypeScript...')
  execSync('npx tsc --noEmit', { stdio: 'inherit' })

  // Run Vite build with production optimizations
  console.log('⚡ Building with Vite...')
  execSync('npx vite build --mode production', { stdio: 'inherit' })

  // Generate build report
  console.log('📊 Generating build report...')
  generateBuildReport()

  // Optimize assets
  console.log('🔧 Optimizing assets...')
  optimizeAssets()

  // Generate service worker
  console.log('⚙️ Generating service worker...')
  generateServiceWorker()

  console.log('✅ Production build completed successfully!')
  console.log('📦 Build artifacts are in the dist/ directory')

} catch (error) {
  console.error('❌ Build failed:', error.message)
  process.exit(1)
}

function generateBuildReport() {
  const distPath = path.join(__dirname, '..', 'dist')
  const report = {
    timestamp: new Date().toISOString(),
    buildTime: Date.now(),
    files: [],
    totalSize: 0,
  }

  function scanDirectory(dir, relativePath = '') {
    const items = fs.readdirSync(dir)
    
    for (const item of items) {
      const fullPath = path.join(dir, item)
      const relativeItemPath = path.join(relativePath, item)
      
      if (fs.statSync(fullPath).isDirectory()) {
        scanDirectory(fullPath, relativeItemPath)
      } else {
        const stats = fs.statSync(fullPath)
        const fileInfo = {
          path: relativeItemPath,
          size: stats.size,
          modified: stats.mtime,
        }
        
        report.files.push(fileInfo)
        report.totalSize += stats.size
      }
    }
  }

  scanDirectory(distPath)
  
  // Write report
  fs.writeFileSync(
    path.join(distPath, 'build-report.json'),
    JSON.stringify(report, null, 2)
  )
  
  console.log(`📊 Build report generated: ${report.files.length} files, ${(report.totalSize / 1024).toFixed(2)} KB`)
}

function optimizeAssets() {
  const distPath = path.join(__dirname, '..', 'dist')
  
  // Add compression headers for common file types
  const htaccessContent = `
# Production optimizations
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/plain
  AddOutputFilterByType DEFLATE text/html
  AddOutputFilterByType DEFLATE text/xml
  AddOutputFilterByType DEFLATE text/css
  AddOutputFilterByType DEFLATE application/xml
  AddOutputFilterByType DEFLATE application/xhtml+xml
  AddOutputFilterByType DEFLATE application/rss+xml
  AddOutputFilterByType DEFLATE application/javascript
  AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache control
<IfModule mod_expires.c>
  ExpiresActive on
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header always set X-Content-Type-Options nosniff
  Header always set X-Frame-Options DENY
  Header always set X-XSS-Protection "1; mode=block"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
</IfModule>
`

  fs.writeFileSync(path.join(distPath, '.htaccess'), htaccessContent)
  console.log('🔧 .htaccess file created with optimizations')
}

function generateServiceWorker() {
  const serviceWorkerContent = `
// Service Worker for IDE Chat App
const CACHE_NAME = 'ide-chat-app-v1'
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  )
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        return response || fetch(event.request)
      })
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
})
`

  const distPath = path.join(__dirname, '..', 'dist')
  fs.writeFileSync(path.join(distPath, 'sw.js'), serviceWorkerContent)
  console.log('⚙️ Service worker generated')
}
