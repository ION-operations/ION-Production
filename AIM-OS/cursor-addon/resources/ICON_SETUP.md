# Logo/Icon Setup Instructions

## 🎨 **Logo Requirements**

The logo image should be placed at:
```
cursor-addon/resources/icon.png
```

### **Icon Specifications:**
- **Format:** PNG (preferred) or SVG
- **Size:** 128x128 pixels (minimum)
- **Recommended:** 256x256 pixels for high-DPI displays
- **Background:** Transparent or solid (will be used on dark/light themes)

### **Current Status:**
✅ Extension name updated to "Lucid UI - AIM-OS"  
✅ Icon path configured in `package.json`  
⏳ **Action Required:** Place your logo image at `cursor-addon/resources/icon.png`

### **Quick Setup:**
1. Save your logo image as `icon.png`
2. Place it in `cursor-addon/resources/icon.png`
3. Run `npm run install` to rebuild and reinstall

### **Alternative: SVG Icon**
If you prefer SVG (scalable):
1. Save as `cursor-addon/resources/icon.svg`
2. Update `package.json` to reference `icon.svg` instead
3. SVG works better for high-DPI displays

### **Test the Icon:**
After adding the icon:
1. Rebuild: `npm run install`
2. Reload Cursor (`Ctrl+R`)
3. Check the Activity Bar - you should see your logo! 🎨

---

**Note:** The icon will appear in:
- Activity Bar (left sidebar)
- Extension Marketplace (if published)
- Extension list in Settings
- Command Palette (if configured)

