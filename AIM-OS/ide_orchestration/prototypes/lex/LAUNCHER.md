# Lex IDE Prototype Launcher Scripts

## Quick Launch

### Windows (PowerShell)
```powershell
npm run launch
```

### Windows (CMD)
```cmd
npm run launch
```

### macOS/Linux
```bash
npm run launch
# or
chmod +x launch.js
./launch.js
```

## What the Launcher Does

1. **Finds Available Port** - Automatically finds an available port starting from 3004 (avoids 3000-3003)
2. **Starts Dev Server** - Launches Vite dev server on the found port
3. **Opens Browser** - Automatically opens your browser to the prototype
4. **Handles Conflicts** - Gracefully handles port conflicts and finds next available port

## Manual Launch

If you prefer to launch manually:

```bash
# Find an available port (e.g., 3004)
npm run dev -- --port 3004 --host

# Then navigate to http://localhost:3004 in your browser
```

## Port Range

The launcher checks ports **3004-3013** (10 ports) to find an available one. If all are taken, it will show an error.

## Troubleshooting

**Port Already in Use:**
- The launcher will automatically try the next port
- If all ports 3004-3013 are taken, manually specify a port:
  ```bash
  npm run dev -- --port 3014 --host
  ```

**Browser Doesn't Open:**
- The launcher will show the URL - just navigate manually
- URL format: `http://localhost:[PORT]`

**Process Hangs:**
- Press `Ctrl+C` to stop the dev server
- The launcher handles cleanup automatically

