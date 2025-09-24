# 🍎 USDA Food Tools for Claude

Add powerful food and nutrition data to Claude for Desktop using the USDA's comprehensive food database.

## 🚀 For Users - Quick Install

### Option 1: GUI Installer (Recommended)
1. **Download**: [`USDA Food Tools Installer.zip`](https://github.com/rpassafaro/usda-api-mcp/releases/latest) (11KB)
2. **Extract** and double-click the app
3. **Get API Key**: Free at [api.nal.usda.gov](https://api.nal.usda.gov/signup)
4. **Follow the installer** - opens in your browser
5. **Restart Claude** - tools appear automatically!

### Option 2: Command Line
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/usda-api-mcp/main/install.sh | bash
```

## 🔍 What You Get

- **Search Foods** - Find any food with detailed nutrition facts
- **Nutrition Analysis** - Complete nutrient breakdowns  
- **Brand Information** - Ingredients, categories, manufacturers
- **Bulk Lookups** - Multiple foods at once
- **Research Data** - USDA's gold-standard food database

## 📋 Requirements

- Claude for Desktop (latest version)
- Free USDA API key from [api.nal.usda.gov](https://api.nal.usda.gov/signup)
- macOS 10.15+ (GUI installer) or Python 3.11+ (command line)

## 💬 Example Usage

Once installed, ask Claude:
- *"What's the nutrition info for salmon?"*
- *"Compare chicken breast vs tofu protein"*
- *"Find high-fiber breakfast foods"*
- *"Show vitamin content of spinach"*

---

## 🛠️ For Developers

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/usda-api-mcp.git
cd usda-api-mcp

# Install dependencies
uv sync

# Set up environment
echo "USDA_API_KEY=your_key_here" > .env

# Run the MCP server
uv run main.py
```

### Project Structure

```
usda-api-mcp/
├── main.py              # MCP server implementation
├── gui_installer.py     # Web-based GUI installer
├── install.sh          # Command-line installer
├── pyproject.toml      # Dependencies
├── create_app.sh       # Build Mac app bundle
└── dist/               # Distribution files
```

### Available MCP Tools

- `search_foods(query, page_size, page_number)` - Search food database
- `get_food_details(fdc_id, nutrients)` - Get detailed food information
- `get_multiple_foods(fdc_ids, nutrients)` - Bulk food lookup
- `list_foods(data_type, page_size, page_number)` - Browse foods
- `get_food_nutrients(fdc_ids, nutrients)` - Get specific nutrients

### Building Releases

```bash
# Build Mac app bundle
./create_app.sh

# Create distribution zip
cd dist && zip -r "USDA-Food-Tools-Installer.zip" "USDA Food Tools Installer.app"

# Test the app
open "USDA Food Tools Installer.app"
```

### API Integration

The server integrates with USDA FoodData Central API v2:
- **Base URL**: `https://api.nal.usda.gov/fdc/v2/`
- **Authentication**: API key in query parameters
- **Rate Limits**: 3600 requests/hour (free tier)
- **Data Types**: Foundation, SR Legacy, Survey, Branded foods

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request

### Testing

```bash
# Test MCP server directly
uv run main.py

# Test GUI installer
python3 gui_installer.py

# Test command-line installer
./install.sh
```

### Deployment

The project uses a simple Mac app bundle approach:
- No complex packaging (py2app issues resolved)
- Shell script launcher with embedded Python
- Self-contained with port conflict resolution
- Automatic cleanup of existing processes
