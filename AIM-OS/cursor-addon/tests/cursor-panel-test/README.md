# Cursor Panel Test

**Completely separate extension to test if panels work in Cursor**

## Setup

```bash
cd cursor-panel-test
npm install
npm run compile
```

## Test

1. Open `cursor-panel-test` folder in Cursor
2. Press `F5` to launch Extension Development Host
3. In the new window: `Ctrl+Shift+P` → `Open Panel Test`
4. Check if panel opens with green border

## What This Tests

- ✅ Can `createWebviewPanel` work in Cursor?
- ✅ Can HTML render?
- ✅ Can CSS work?
- ✅ Can JavaScript work?

**If this works, we know panels CAN work.**  
**If this fails, we know Cursor has a deeper issue.**
