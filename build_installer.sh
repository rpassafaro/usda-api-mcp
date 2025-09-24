#!/bin/bash

# Build script for creating the Mac GUI installer
# This creates a standalone .app bundle that users can double-click

set -e

echo "🔨 Building USDA Food Tools GUI Installer for Mac..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This build script is for macOS only"
    exit 1
fi

# Check for Python 3.11+
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📋 Python version: $python_version"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Python 3.11+ required"
    exit 1
fi

# Install py2app if not present
if ! python3 -c "import py2app" 2>/dev/null; then
    echo "📦 Installing py2app..."
    pip3 install py2app
fi

# Install requests if not present
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing requests..."
    pip3 install requests
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/

# Build the app
echo "🔨 Building Mac app bundle..."
python3 setup_gui.py py2app

# Check if build was successful
if [ -d "dist/gui_installer.app" ]; then
    echo "✅ Build successful!"
    echo "📱 App created at: dist/gui_installer.app"
    echo ""
    echo "🎯 To distribute:"
    echo "   1. Compress: cd dist && zip -r 'USDA Food Tools Installer.zip' gui_installer.app"
    echo "   2. Share the .zip file with users"
    echo "   3. Users extract and double-click the .app"
    echo ""
    echo "🧪 To test:"
    echo "   open dist/gui_installer.app"
else
    echo "❌ Build failed"
    exit 1
fi
