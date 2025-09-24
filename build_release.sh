#!/bin/bash
# Build a clean release with only distribution files

VERSION=${1:-"2.1.0"}
RELEASE_DIR="release-v${VERSION}"

echo "🚀 Building release v${VERSION}..."

# Clean up any existing release directory
rm -rf "$RELEASE_DIR"

# Create release directory
mkdir -p "$RELEASE_DIR"

# Build the Mac app
echo "📦 Building Mac app..."
./create_app.sh

# Create the installer zip
echo "🗜️ Creating installer zip..."
cd dist
rm -f "USDA-Food-Tools-Installer.zip"
zip -r "USDA-Food-Tools-Installer.zip" "USDA Food Tools Installer.app"
cd ..

# Copy files to release directory
echo "📋 Copying release files..."
cp "dist/USDA-Food-Tools-Installer.zip" "$RELEASE_DIR/"
cp "install.sh" "$RELEASE_DIR/"

# Create release README
cat > "$RELEASE_DIR/README.txt" << EOF
🍎 USDA Food Tools for Claude v${VERSION}

QUICK INSTALL:
1. Double-click "USDA-Food-Tools-Installer.zip" to extract
2. Double-click "USDA Food Tools Installer.app"
3. Get free API key: https://fdc.nal.usda.gov/api-key-signup
4. Follow the installer (opens in browser)
5. Restart Claude - tools appear automatically!

ALTERNATIVE:
- Run "install.sh" in Terminal for command-line installation

REQUIREMENTS:
- Claude for Desktop (latest version)
- macOS 10.15+ (for GUI installer)
- Free USDA API key

For help: https://github.com/rpassafaro/usda-api-mcp
EOF

# Show release contents
echo "✅ Release ready!"
echo ""
echo "📁 Release contents:"
ls -la "$RELEASE_DIR/"
echo ""
echo "📏 File sizes:"
du -h "$RELEASE_DIR"/*
echo ""
echo "🚀 To create GitHub release:"
echo "1. Create tag: git tag v${VERSION} && git push origin v${VERSION}"
echo "2. Go to GitHub → Releases → Create new release"
echo "3. Upload files from ${RELEASE_DIR}/"
echo "4. UNCHECK 'Include source code' options"
