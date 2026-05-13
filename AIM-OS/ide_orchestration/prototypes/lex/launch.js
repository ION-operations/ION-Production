#!/usr/bin/env node

/**
 * Lex IDE Prototype Launcher
 * Finds an available port (avoiding 3000-3003) and launches the dev server
 */

const { spawn } = require('child_process')
const net = require('net')
const { exec } = require('child_process')
const path = require('path')

const START_PORT = 3004
const MAX_PORT_ATTEMPTS = 10

function checkPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer()
    server.listen(port, () => {
      server.once('close', () => resolve(true))
      server.close()
    })
    server.on('error', () => resolve(false))
  })
}

async function findAvailablePort() {
  for (let i = 0; i < MAX_PORT_ATTEMPTS; i++) {
    const port = START_PORT + i
    const available = await checkPort(port)
    if (available) {
      return port
    }
  }
  throw new Error(`Could not find available port in range ${START_PORT}-${START_PORT + MAX_PORT_ATTEMPTS - 1}`)
}

function openBrowser(url) {
  const platform = process.platform
  let command

  if (platform === 'darwin') {
    command = `open "${url}"`
  } else if (platform === 'win32') {
    command = `start "" "${url}"`
  } else {
    command = `xdg-open "${url}"`
  }

  exec(command, (error) => {
    if (error) {
      console.log(`⚠️  Could not auto-open browser. Please navigate to: ${url}`)
    }
  })
}

async function launch() {
  console.log('🚀 Launching Lex IDE Prototype...\n')

  try {
    // Find available port
    const port = await findAvailablePort()
    console.log(`✅ Found available port: ${port}`)

    // Start Vite dev server with the found port
    console.log(`📦 Starting development server on port ${port}...\n`)

    const viteProcess = spawn('npm', ['run', 'dev', '--', '--port', port.toString(), '--host'], {
      cwd: __dirname,
      stdio: 'inherit', // Show output in terminal
      shell: true,
      env: {
        ...process.env,
        VITE_PORT: port.toString(),
        PORT: port.toString(),
      },
    })

    // Track if server started successfully
    let serverStarted = false
    let startupTimeout

    // Wait for server to start and verify
    viteProcess.stdout?.on('data', (data) => {
      const output = data.toString()
      console.log(output)
      
      // Check for Vite dev server ready message
      if (output.includes('Local:') || output.includes('ready in')) {
        serverStarted = true
        if (startupTimeout) clearTimeout(startupTimeout)
        
        setTimeout(() => {
          const url = `http://localhost:${port}`
          console.log(`\n✅ Server started successfully!`)
          console.log(`🌐 Opening browser at ${url}...\n`)
          openBrowser(url)
        }, 1000)
      }
      
      // Check for errors
      if (output.includes('error') || output.includes('Error') || output.includes('ERROR')) {
        console.error(`\n❌ Error detected in output: ${output}`)
      }
    })

    viteProcess.stderr?.on('data', (data) => {
      const output = data.toString()
      console.error(output)
    })

    // Timeout if server doesn't start within 30 seconds
    startupTimeout = setTimeout(() => {
      if (!serverStarted) {
        console.error(`\n❌ Server did not start within 30 seconds. Check for errors above.`)
      }
    }, 30000)

    // Handle process exit
    viteProcess.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`\n❌ Dev server exited with code ${code}`)
      }
    })

    // Handle Ctrl+C
    process.on('SIGINT', () => {
      console.log('\n\n🛑 Shutting down...')
      if (viteProcess && !viteProcess.killed) {
        viteProcess.kill('SIGTERM')
        // Force kill after 2 seconds if still running
        setTimeout(() => {
          if (!viteProcess.killed) {
            viteProcess.kill('SIGKILL')
          }
        }, 2000)
      }
      process.exit(0)
    })

    process.on('SIGTERM', () => {
      console.log('\n\n🛑 Shutting down...')
      if (viteProcess && !viteProcess.killed) {
        viteProcess.kill('SIGTERM')
        setTimeout(() => {
          if (!viteProcess.killed) {
            viteProcess.kill('SIGKILL')
          }
        }, 2000)
      }
      process.exit(0)
    })

    // Handle uncaught exceptions
    process.on('uncaughtException', (error) => {
      console.error('\n❌ Uncaught exception:', error)
      if (viteProcess && !viteProcess.killed) {
        viteProcess.kill('SIGTERM')
      }
      process.exit(1)
    })

    // Cleanup on exit
    process.on('exit', () => {
      if (viteProcess && !viteProcess.killed) {
        viteProcess.kill('SIGTERM')
      }
    })

  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`)
    process.exit(1)
  }
}

launch()

