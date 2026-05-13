#!/usr/bin/env node
/**
 * Electron Restart Script
 * Kills existing Electron processes and launches fresh instance
 * 
 * Usage: npm run restart
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const os = require('os');

const isWindows = os.platform() === 'win32';
const isMac = os.platform() === 'darwin';
const isLinux = os.platform() === 'linux';

console.log('🔄 Restarting Electron app...');

// Kill existing Electron processes
function killElectronProcesses() {
  return new Promise((resolve) => {
    if (isWindows) {
      // Windows: Use taskkill
      exec('taskkill /F /IM electron.exe 2>nul', (error) => {
        // Ignore errors (process might not be running)
        setTimeout(resolve, 1000); // Wait 1 second for cleanup
      });
    } else if (isMac) {
      // macOS: Use killall
      exec('killall Electron 2>/dev/null || true', (error) => {
        setTimeout(resolve, 1000);
      });
    } else if (isLinux) {
      // Linux: Use pkill
      exec('pkill -f electron || true', (error) => {
        setTimeout(resolve, 1000);
      });
    } else {
      setTimeout(resolve, 1000);
    }
  });
}

// Launch Electron
function launchElectron() {
  console.log('🚀 Launching Electron app...');
  const electronProcess = spawn('npm', ['run', 'electron'], {
    cwd: __dirname,
    shell: true,
    stdio: 'inherit'
  });
  
  electronProcess.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.log(`Electron exited with code ${code}`);
    }
  });
  
  return electronProcess;
}

// Main restart flow
async function restart() {
  try {
    await killElectronProcesses();
    launchElectron();
  } catch (error) {
    console.error('❌ Failed to restart Electron:', error);
    process.exit(1);
  }
}

restart();

