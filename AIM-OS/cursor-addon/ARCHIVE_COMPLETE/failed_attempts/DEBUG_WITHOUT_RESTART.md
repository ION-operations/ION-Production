# 🔍 Debug Dashboard WITHOUT Restarting

## **STEP 1: Check Extension Host Console**
1. In Cursor, press `Ctrl+Shift+P`
2. Type: `Developer: Toggle Developer Tools`
3. Click **"Extension Host"** tab (at top)
4. Look for `[AIM-OS]` messages
5. **Copy ALL messages starting with `[AIM-OS]`** and share them

## **STEP 2: Inspect Webview (NO RESTART NEEDED)**
1. **Right-click** inside the blank dashboard panel
2. Select **"Inspect"** or **"Inspect Element"**
3. This opens the **Webview Developer Tools**
4. Check **Console** tab for errors
5. Check **Network** tab - are scripts loading? (look for `.js` files)
6. **Copy any errors** you see

## **STEP 3: Check What HTML Was Loaded**
In the Webview Inspector:
1. Go to **Elements** tab
2. Look for `<div id="root">` - does it exist?
3. Look for `<script>` tags - what `src` do they have?
4. Are the script URLs `vscode-webview://` format?

## **STEP 4: Check Extension Files**
The extension is installed at:
```
C:\Users\bombe\.cursor\extensions\aimos.aimos-cursor-addon-1.2.0
```

Check if assets exist:
- `dist/index.html` ✅ (confirmed exists)
- `dist/assets/main-5fYGI1t7.js` - does this exist?
- `dist/assets/main-DftvcEcs.css` - does this exist?

---

## **CRITICAL: What We're Looking For**

### **If Scripts Aren't Loading:**
- Network tab shows 404 errors
- Console shows "Failed to load resource"
- Script URLs are wrong format

### **If Scripts Are Blocked:**
- Console shows Trusted Types errors
- Console shows CSP violations
- Scripts load but don't execute

### **If React Isn't Mounting:**
- Scripts load successfully
- Console shows `[AIM-OS] main-cursor.tsx loaded` message
- But React doesn't render

---

**Please do Step 2 (Inspect Webview) - this will show us EXACTLY what's wrong without restarting!**

