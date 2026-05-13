# Cache Fix Instructions

## Problem
Chrome is caching the old version of the app even after reloading.

## Solutions Applied

### 1. Vite Config Changes
- Added cache-busting headers to dev server
- Disabled caching in dev mode
- Force optimized dependencies reload

### 2. HTML Meta Tags
- Added no-cache meta tags to HTML

## Manual Steps to Clear Cache

### Option 1: Hard Refresh (Easiest)
- **Windows/Linux:** `Ctrl + Shift + R` or `Ctrl + F5`
- **Mac:** `Cmd + Shift + R`

### Option 2: Clear Browser Cache
1. Open Chrome DevTools (`F12`)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Disable Cache in DevTools
1. Open Chrome DevTools (`F12`)
2. Go to Network tab
3. Check "Disable cache" checkbox
4. Keep DevTools open while developing

### Option 4: Clear Site Data
1. Open Chrome Settings
2. Privacy and Security → Clear browsing data
3. Select "Cached images and files"
4. Choose "Last hour" or "All time"
5. Click "Clear data"

### Option 5: Incognito Mode
- Open in Incognito/Private window (`Ctrl + Shift + N`)
- No cache, always fresh

## After Making Changes

1. **Restart Dev Server:**
   ```bash
   # Stop current server (Ctrl+C)
   npm run dev
   ```

2. **Hard Refresh Browser:**
   - `Ctrl + Shift + R` (Windows/Linux)
   - `Cmd + Shift + R` (Mac)

3. **Verify Changes:**
   - Check browser console for errors
   - Verify panel buttons work
   - Check that title shows `[AETHER V2]`

## If Still Cached

1. Close all Chrome tabs with the app
2. Clear browser cache completely
3. Restart Chrome
4. Open app fresh

