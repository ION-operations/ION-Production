#!/bin/bash

# AIM-OS Cursor Extension Installation Script (Bash)
# Installs the extension to Cursor/VSCode

echo "🚀 Installing AIM-OS Cursor Extension..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the cursor-addon directory."
    exit 1
fi

# Build the extension
echo "📦 Building extension..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Package the extension
echo "📋 Packaging extension..."
npx vsce package --out aimos-cursor-addon.vsix

if [ $? -ne 0 ]; then
    echo "❌ Packaging failed!"
    exit 1
fi

# Find Cursor executable
CURSOR_CMD=""
if command -v cursor &> /dev/null; then
    CURSOR_CMD="cursor"
elif [ -f "$HOME/.local/share/cursor/bin/cursor" ]; then
    CURSOR_CMD="$HOME/.local/share/cursor/bin/cursor"
elif command -v code &> /dev/null; then
    CURSOR_CMD="code"
elif [ -f "/usr/bin/code" ]; then
    CURSOR_CMD="/usr/bin/code"
else
    echo "⚠️  Cursor/VS Code not found in PATH!"
    echo "   Please install Cursor or VS Code, or install manually:"
    echo "   code --install-extension aimos-cursor-addon.vsix"
    exit 1
fi

# Install the extension
echo "🔌 Installing extension to $CURSOR_CMD..."
$CURSOR_CMD --install-extension aimos-cursor-addon.vsix --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Extension installed successfully!"
    echo "   Please reload Cursor/VSCode to activate the extension."
    echo ""
    echo "   To open the dashboard, use:"
    echo "   - Command Palette (Ctrl+Shift+P) > 'AIM-OS: Show Dashboard'"
    echo "   - Or click the AIM-OS icon in the Activity Bar"
else
    echo "❌ Installation failed!"
    echo "   Try installing manually: $CURSOR_CMD --install-extension aimos-cursor-addon.vsix --force"
    exit 1
fi

