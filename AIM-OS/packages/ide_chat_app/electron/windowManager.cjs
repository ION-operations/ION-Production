/**
 * Window Management Service
 * Manages Cursor window (open, restore, minimize, bring to front)
 */

const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class WindowManager {
  /**
   * Find Cursor window process
   */
  async findCursorWindow() {
    const platform = process.platform;
    
    try {
      if (platform === 'win32') {
        const { stdout } = await execAsync('tasklist /FI "IMAGENAME eq Cursor.exe"');
        return stdout.includes('Cursor.exe');
      } else if (platform === 'darwin') {
        const { stdout } = await execAsync('pgrep -f Cursor');
        return stdout.trim().length > 0;
      } else {
        const { stdout } = await execAsync('pgrep -f cursor');
        return stdout.trim().length > 0;
      }
    } catch (error) {
      return false;
    }
  }

  /**
   * Open Cursor window if not already open
   */
  async ensureCursorOpen() {
    const isOpen = await this.findCursorWindow();
    
    if (!isOpen) {
      const platform = process.platform;
      
      if (platform === 'win32') {
        // Windows: Try common installation paths
        const possiblePaths = [
          process.env.LOCALAPPDATA + '\\Programs\\cursor\\Cursor.exe',
          process.env.APPDATA + '\\..\\Local\\Programs\\cursor\\Cursor.exe',
          'C:\\Users\\' + process.env.USERNAME + '\\AppData\\Local\\Programs\\cursor\\Cursor.exe'
        ];
        
        for (const cursorPath of possiblePaths) {
          try {
            await execAsync(`start "" "${cursorPath}"`);
            await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for Cursor to open
            break;
          } catch (error) {
            // Try next path
            continue;
          }
        }
      } else if (platform === 'darwin') {
        await execAsync('open -a Cursor');
        await new Promise(resolve => setTimeout(resolve, 2000));
      } else {
        await execAsync('cursor');
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    // Bring Cursor to front (but overlay will be on top)
    await this.bringCursorToFront();
  }

  /**
   * Bring Cursor window to front
   */
  async bringCursorToFront() {
    const platform = process.platform;
    
    try {
      if (platform === 'win32') {
        // Use PowerShell to bring window to front
        await execAsync(`powershell -Command "[Microsoft.VisualBasic.Interaction]::AppActivate((Get-Process | Where-Object {$_.MainWindowTitle -like '*Cursor*'}).Id)"`);
      } else if (platform === 'darwin') {
        await execAsync('osascript -e \'tell application "Cursor" to activate\'');
      } else {
        // Linux: Use wmctrl
        await execAsync('wmctrl -a Cursor');
      }
    } catch (error) {
      // Silently fail - window might not be available
    }
  }

  /**
   * Minimize Cursor window
   */
  async minimizeCursor() {
    const platform = process.platform;
    
    try {
      if (platform === 'win32') {
        // Use PowerShell to minimize window
        await execAsync(`powershell -Command "$proc = Get-Process | Where-Object {$_.MainWindowTitle -like '*Cursor*'}; if ($proc) { $hwnd = $proc[0].MainWindowHandle; [void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.SendKeys]::SendWait('{F11}'); }"`);
      } else if (platform === 'darwin') {
        await execAsync('osascript -e \'tell application "Cursor" to set miniaturized of every window to true\'');
      } else {
        // Linux: Use wmctrl
        await execAsync('wmctrl -r Cursor -b add,hidden');
      }
    } catch (error) {
      // Silently fail
    }
  }
}

module.exports = new WindowManager();

