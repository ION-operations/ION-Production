// AIM-OS IDE One-Click Launcher (Node.js)
// Automatically finds an open port and launches the IDE
// Cross-platform launcher script

const { spawn } = require('child_process')
const net = require('net')
const { execSync } = require('child_process')
const path = require('path')
const fs = require('fs')

console.log('')
console.log('========================================')
console.log('  AIM-OS IDE Launcher')
console.log('  Finding open port and starting...')
console.log('========================================')
console.log('')

// Change to script directory
process.chdir(__dirname)

if (!fs.existsSync('package.json')) {
    console.error('[ERROR] package.json not found! Make sure you\'re in the ide_chat_app directory.')
    process.exit(1)
}

// Check if node_modules exists
if (!fs.existsSync('node_modules')) {
    console.log('[INFO] Installing dependencies...')
    try {
        execSync('npm install', { stdio: 'inherit' })
        console.log('[SUCCESS] Dependencies installed!')
        console.log('')
    } catch (error) {
        console.error('[ERROR] Failed to install dependencies!')
        process.exit(1)
    }
}

// Function to check if port is available
function isPortAvailable(port) {
    return new Promise((resolve) => {
        const server = net.createServer()
        server.listen(port, () => {
            server.once('close', () => resolve(true))
            server.close()
        })
        server.on('error', () => resolve(false))
    })
}

// Find an open port starting from 5173
async function findOpenPort(startPort = 5173, maxPort = 6000) {
    console.log('[INFO] Finding an open port...')
    
    for (let port = startPort; port <= maxPort; port++) {
        const available = await isPortAvailable(port)
        if (available) {
            console.log(`[SUCCESS] Found open port: ${port}`)
            return port
        } else {
            console.log(`[INFO] Port ${port} is in use, trying next port...`)
        }
    }
    
    throw new Error('Could not find an open port between 5173-6000!')
}

// Launch the dev server
async function launch() {
    try {
        const port = await findOpenPort()
        
        console.log('')
        console.log(`[INFO] Starting IDE on port ${port}...`)
        console.log(`[INFO] Server will open automatically at http://localhost:${port}`)
        console.log('[INFO] Press Ctrl+C to stop the server')
        console.log('')
        
        // Start vite with the found port
        const vite = spawn('npm', ['run', 'dev', '--', '--port', port.toString(), '--host'], {
            stdio: 'inherit',
            shell: true
        })
        
        vite.on('close', (code) => {
            process.exit(code || 0)
        })
        
    } catch (error) {
        console.error(`[ERROR] ${error.message}`)
        process.exit(1)
    }
}

launch()

