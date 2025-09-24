#!/bin/bash
# Create a simple Mac app bundle manually

set -euo pipefail

APP_NAME="USDA Food Tools Installer"
ICON_SOURCE="icon.png"
ICON_NAME="AppIcon"
BUNDLE_DIR="dist/${APP_NAME}.app"
CONTENTS_DIR="${BUNDLE_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# Clean up and create directories
rm -rf "$BUNDLE_DIR"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create icns icon if source PNG exists
if [[ -f "$ICON_SOURCE" ]]; then
  ICONSET_DIR="${RESOURCES_DIR}/${ICON_NAME}.iconset"
  rm -rf "$ICONSET_DIR"
  mkdir -p "$ICONSET_DIR"

  for SIZE in 16 32 64 128 256 512; do
    sips -z "$SIZE" "$SIZE" "$ICON_SOURCE" --out "${ICONSET_DIR}/icon_${SIZE}x${SIZE}.png" >/dev/null
    DOUBLE_SIZE=$((SIZE * 2))
    sips -z "$DOUBLE_SIZE" "$DOUBLE_SIZE" "$ICON_SOURCE" --out "${ICONSET_DIR}/icon_${SIZE}x${SIZE}@2x.png" >/dev/null
  done

  iconutil -c icns "$ICONSET_DIR" -o "${RESOURCES_DIR}/${ICON_NAME}.icns"
  rm -rf "$ICONSET_DIR"
else
  echo "⚠️  Warning: icon source '$ICON_SOURCE' not found; proceeding without custom app icon." >&2
fi

# Create the main executable script
cat > "${MACOS_DIR}/${APP_NAME}" << 'EOF'
#!/bin/bash
# Get the Resources directory
RESOURCES_DIR="$(dirname "$0")/../Resources"
cd "$RESOURCES_DIR"

# Launch the Python installer
python3 gui_installer.py
EOF

# Make it executable
chmod +x "${MACOS_DIR}/${APP_NAME}"

# Copy required files to Resources
cp gui_installer.py "$RESOURCES_DIR/"
cp main.py "$RESOURCES_DIR/"
cp pyproject.toml "$RESOURCES_DIR/"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << EOF
<?xml version="2.1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 2.1.0//EN" "http://www.apple.com/DTDs/PropertyList-2.1.0.dtd">
<plist version="2.1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.usdaapi.mcp.installer</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>2.1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.1.0</string>
    <key>CFBundleIconFile</key>
    <string>${ICON_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

echo "✅ Created app bundle: $BUNDLE_DIR"
echo "🚀 Ready to test!"
