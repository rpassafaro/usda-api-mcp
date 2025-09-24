# Release Checklist

## Creating a New Release

### 1. Prepare Release
```bash
# Ensure everything is working
python3 gui_installer.py  # Test web installer
./install.sh             # Test command line installer
uv run main.py            # Test MCP server

# Build the Mac app
./create_app.sh

# Create distribution zip
cd dist
rm -f "USDA-Food-Tools-Installer.zip"
zip -r "USDA-Food-Tools-Installer.zip" "USDA Food Tools Installer.app"
cd ..

# Test the final app
open "dist/USDA Food Tools Installer.app"
```

### 2. Version Bump
- Update version in `pyproject.toml`
- Update version in `create_app.sh` if needed
- Update any version references in documentation

### 3. Commit and Tag
```bash
git add .
git commit -m "Release v1.0.0"
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

### 4. Create GitHub Release
1. Go to GitHub repository → Releases → "Create a new release"
2. Choose tag: `v1.0.0`
3. Release title: `USDA Food Tools v1.0.0`
4. Description:
```markdown
## 🍎 USDA Food Tools for Claude

Add powerful food and nutrition data to Claude for Desktop!

### 🚀 Quick Install
1. Download `USDA-Food-Tools-Installer.zip` below
2. Extract and double-click the app
3. Get free API key at [api.nal.usda.gov](https://api.nal.usda.gov/signup)
4. Follow the installer (opens in browser)
5. Restart Claude - tools appear automatically!

### ✨ What's New
- Beautiful web-based installer
- Automatic port conflict resolution  
- Self-contained Mac app bundle
- Improved error handling

### 🔍 Features
- Search 500,000+ foods from USDA database
- Complete nutrition facts and analysis
- Brand information and ingredients
- Bulk lookups for multiple foods
- Research-quality data

**Full Changelog**: https://github.com/yourusername/usda-api-mcp/compare/v0.9.0...v1.0.0
```

5. Attach files:
   - `USDA-Food-Tools-Installer.zip` (from `dist/`)
   - `install.sh` (command-line installer)
   - `gui_installer.py` (Python script installer)

6. Check "Set as the latest release"
7. Click "Publish release"

### 5. Update README Links
After release is published, update README.md download links to point to:
```
https://github.com/yourusername/usda-api-mcp/releases/latest/download/USDA-Food-Tools-Installer.zip
```

### 6. Test Release
- Download from GitHub release page
- Test installation on clean system
- Verify all tools work in Claude

## File Sizes Reference
- `USDA-Food-Tools-Installer.zip`: ~11KB (Mac app bundle)
- `gui_installer.py`: ~15KB (Python script)
- `install.sh`: ~2KB (Shell script)

## Distribution Files
```
dist/
├── USDA Food Tools Installer.app/    # Mac app bundle
└── USDA-Food-Tools-Installer.zip     # Release artifact
```
