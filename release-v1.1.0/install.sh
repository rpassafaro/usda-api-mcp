#!/bin/bash

# USDA API MCP Server Installer
# This script automatically installs and configures the USDA API MCP server for Claude for Desktop

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This installer is designed for macOS only."
    exit 1
fi

print_status "Starting USDA API MCP Server installation..."

# Check if Claude for Desktop is installed
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    print_error "Claude for Desktop is not installed or not found."
    print_status "Please install Claude for Desktop from: https://claude.ai/download"
    exit 1
fi

print_success "Claude for Desktop found!"

# Get API key from user
echo ""
print_status "You need a USDA FoodData Central API key to use this service."
print_status "Get your free API key at: https://fdc.nal.usda.gov/api-guide.html"
echo ""
read -p "Enter your USDA API key: " USDA_API_KEY

if [ -z "$USDA_API_KEY" ]; then
    print_error "API key is required. Exiting."
    exit 1
fi

# Set installation directory
INSTALL_DIR="$HOME/.usda-api-mcp"
print_status "Installing to: $INSTALL_DIR"

# Remove existing installation if it exists
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Existing installation found. Removing..."
    rm -rf "$INSTALL_DIR"
fi

# Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_status "Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        print_error "Failed to install uv. Please install it manually and try again."
        exit 1
    fi
fi

UV_PATH=$(command -v uv)
print_success "uv found at: $UV_PATH"

# Create pyproject.toml
print_status "Creating project configuration..."
cat > pyproject.toml << 'EOF'
[project]
name = "usda-api-mcp"
version = "0.1.0"
description = "MCP server for USDA API access"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.2.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0"
]
EOF

# Create main.py
print_status "Creating server application..."
cat > main.py << 'EOF'
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("usda-api")

# Constants
USDA_API_BASE = "https://api.nal.usda.gov"
API_KEY = os.getenv("USDA_API_KEY")

async def make_usda_request(endpoint: str, params: dict[str, Any] = None) -> dict[str, Any] | None:
    """Make a request to the USDA API with proper error handling."""
    if not API_KEY:
        raise ValueError("USDA_API_KEY environment variable is required")
    
    headers = {
        "User-Agent": "usda-mcp-server/1.0",
        "Accept": "application/json"
    }
    
    # Add API key to parameters
    if params is None:
        params = {}
    params["api_key"] = API_KEY
    
    url = f"{USDA_API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"USDA API request failed: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

@mcp.tool()
async def search_foods(query: str, page_size: int = 50, data_type: str = None, page_number: int = 1) -> str:
    """Search for foods in the USDA FoodData Central database.
    
    Args:
        query: Search term for food items
        page_size: Number of results to return (default: 50, max: 200)
        data_type: Optional data type filter (e.g., 'Foundation', 'SR Legacy', 'Survey')
        page_number: Page number for pagination (default: 1)
    """
    try:
        params = {
            "query": query,
            "pageSize": min(page_size, 200),
            "pageNumber": page_number
        }
        
        if data_type:
            params["dataType"] = data_type
        
        data = await make_usda_request("fdc/v1/foods/search", params)
        
        if not data or "foods" not in data:
            return "No foods found for the given query."
        
        foods = data["foods"]
        total_hits = data.get("totalHits", 0)
        
        if not foods:
            return "No foods found for the given query."
        
        results = []
        for food in foods:
            description = food.get("description", "No description")
            fdc_id = food.get("fdcId", "N/A")
            brand_owner = food.get("brandOwner", "Generic")
            data_type = food.get("dataType", "N/A")
            
            # Include basic nutrition if available
            nutrients_text = ""
            if "foodNutrients" in food and food["foodNutrients"]:
                key_nutrients = []
                for nutrient in food["foodNutrients"][:3]:  # Show first 3 nutrients
                    name = nutrient.get("nutrientName", "Unknown")
                    value = nutrient.get("value", 0)
                    unit = nutrient.get("unitName", "")
                    key_nutrients.append(f"{name}: {value} {unit}")
                if key_nutrients:
                    nutrients_text = f"\nKey Nutrients: {', '.join(key_nutrients)}"
            
            result = f"ID: {fdc_id}\nDescription: {description}\nBrand: {brand_owner}\nData Type: {data_type}{nutrients_text}"
            results.append(result)
        
        return f"Found {total_hits} total foods. Showing page {page_number} ({len(results)} results):\n\n" + "\n---\n".join(results)
        
    except Exception as e:
        return f"Error searching foods: {str(e)}"

@mcp.tool()
async def get_food_details(fdc_id: int, nutrients: str = None) -> str:
    """Get detailed information about a specific food item by its FDC ID.
    
    Args:
        fdc_id: FoodData Central ID of the food item
        nutrients: Optional comma-separated list of nutrient numbers to include
    """
    try:
        params = {}
        if nutrients:
            params["nutrients"] = nutrients
        
        data = await make_usda_request(f"fdc/v1/food/{fdc_id}", params)
        
        if not data:
            return f"No food found with FDC ID: {fdc_id}"
        
        description = data.get("description", "No description")
        brand_owner = data.get("brandOwner", "Generic")
        data_type = data.get("dataType", "N/A")
        ingredients = data.get("ingredients", "Not available")
        
        result = f"FDC ID: {fdc_id}\nDescription: {description}\nBrand: {brand_owner}\nData Type: {data_type}\n"
        
        if ingredients and ingredients != "Not available":
            result += f"Ingredients: {ingredients}\n"
        
        # Add nutrition information
        if "foodNutrients" in data and data["foodNutrients"]:
            result += "\nNutrition Facts (per 100g):\n"
            for nutrient in data["foodNutrients"]:
                name = nutrient.get("nutrient", {}).get("name", "Unknown")
                value = nutrient.get("amount", 0)
                unit = nutrient.get("nutrient", {}).get("unitName", "")
                if value and value > 0:
                    result += f"- {name}: {value} {unit}\n"
        
        # Add food category if available
        if "foodCategory" in data:
            category = data["foodCategory"].get("description", "Unknown")
            result += f"\nCategory: {category}"
        
        return result
        
    except Exception as e:
        return f"Error retrieving food details: {str(e)}"

@mcp.tool()
async def get_multiple_foods(fdc_ids: str, nutrients: str = None) -> str:
    """Get details for multiple food items by their FDC IDs.
    
    Args:
        fdc_ids: Comma-separated list of FDC IDs (e.g., "123456,789012,345678")
        nutrients: Optional comma-separated list of nutrient numbers to include
    """
    try:
        # Parse the comma-separated FDC IDs
        id_list = [int(id.strip()) for id in fdc_ids.split(",")]
        
        if len(id_list) > 20:
            return "Error: Maximum 20 FDC IDs allowed per request"
        
        params = {"fdcIds": id_list}
        if nutrients:
            params["nutrients"] = nutrients
        
        # Use POST method for multiple IDs
        url = f"{USDA_API_BASE}/fdc/v1/foods"
        headers = {
            "User-Agent": "usda-mcp-server/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        request_data = params.copy()
        request_data["api_key"] = API_KEY
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=request_data, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        if not data:
            return "No foods found for the provided FDC IDs"
        
        results = []
        for food in data:
            fdc_id = food.get("fdcId", "N/A")
            description = food.get("description", "No description")
            brand_owner = food.get("brandOwner", "Generic")
            
            # Basic nutrition summary
            nutrition_summary = ""
            if "foodNutrients" in food and food["foodNutrients"]:
                calories = next((n.get("amount", 0) for n in food["foodNutrients"] 
                               if n.get("nutrient", {}).get("name") == "Energy"), None)
                if calories:
                    nutrition_summary = f" | Calories: {calories} kcal"
            
            result = f"ID: {fdc_id} | {description} | Brand: {brand_owner}{nutrition_summary}"
            results.append(result)
        
        return f"Retrieved {len(results)} foods:\n\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error retrieving multiple foods: {str(e)}"

@mcp.tool()
async def list_foods(page_size: int = 50, page_number: int = 1, data_type: str = None, sort_by: str = None) -> str:
    """Get a paginated list of foods in abridged format for browsing.
    
    Args:
        page_size: Number of results to return (default: 50, max: 200)
        page_number: Page number for pagination (default: 1)
        data_type: Optional data type filter (e.g., 'Foundation', 'SR Legacy', 'Survey')
        sort_by: Optional sort field (e.g., 'dataType.keyword', 'description.keyword')
    """
    try:
        params = {
            "pageSize": min(page_size, 200),
            "pageNumber": page_number
        }
        
        if data_type:
            params["dataType"] = data_type
        if sort_by:
            params["sortBy"] = sort_by
        
        data = await make_usda_request("fdc/v1/foods/list", params)
        
        if not data:
            return "No foods found"
        
        foods = data
        if not foods:
            return "No foods found"
        
        results = []
        for food in foods:
            fdc_id = food.get("fdcId", "N/A")
            description = food.get("description", "No description")
            data_type = food.get("dataType", "N/A")
            publication_date = food.get("publicationDate", "N/A")
            
            result = f"ID: {fdc_id} | {description} | Type: {data_type} | Published: {publication_date}"
            results.append(result)
        
        return f"Foods list (Page {page_number}, {len(results)} results):\n\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error listing foods: {str(e)}"

@mcp.tool()
async def get_food_nutrients(fdc_id: int, nutrient_names: str = None) -> str:
    """Get detailed nutrient information for a specific food item.
    
    Args:
        fdc_id: FoodData Central ID of the food item
        nutrient_names: Optional comma-separated list of nutrient names to filter (e.g., "Energy,Protein,Total lipid")
    """
    try:
        data = await make_usda_request(f"fdc/v1/food/{fdc_id}")
        
        if not data:
            return f"No food found with FDC ID: {fdc_id}"
        
        description = data.get("description", "No description")
        
        if "foodNutrients" not in data or not data["foodNutrients"]:
            return f"No nutrient data available for {description} (FDC ID: {fdc_id})"
        
        result = f"Nutrient Information for: {description} (FDC ID: {fdc_id})\n\n"
        
        # Filter nutrients if specific names requested
        nutrients_to_show = data["foodNutrients"]
        if nutrient_names:
            filter_names = [name.strip().lower() for name in nutrient_names.split(",")]
            nutrients_to_show = [
                n for n in data["foodNutrients"] 
                if any(filter_name in n.get("nutrient", {}).get("name", "").lower() 
                      for filter_name in filter_names)
            ]
        
        # Group nutrients by category
        macro_nutrients = []
        vitamins = []
        minerals = []
        other_nutrients = []
        
        for nutrient in nutrients_to_show:
            name = nutrient.get("nutrient", {}).get("name", "Unknown")
            value = nutrient.get("amount", 0)
            unit = nutrient.get("nutrient", {}).get("unitName", "")
            
            if value and value > 0:
                nutrient_line = f"{name}: {value} {unit}"
                
                # Categorize nutrients
                name_lower = name.lower()
                if any(macro in name_lower for macro in ["energy", "protein", "carbohydrate", "fat", "lipid", "fiber"]):
                    macro_nutrients.append(nutrient_line)
                elif any(vitamin in name_lower for vitamin in ["vitamin", "folate", "niacin", "thiamin", "riboflavin"]):
                    vitamins.append(nutrient_line)
                elif any(mineral in name_lower for mineral in ["calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc"]):
                    minerals.append(nutrient_line)
                else:
                    other_nutrients.append(nutrient_line)
        
        # Format output by category
        if macro_nutrients:
            result += "Macronutrients:\n" + "\n".join(f"- {n}" for n in macro_nutrients) + "\n\n"
        if vitamins:
            result += "Vitamins:\n" + "\n".join(f"- {n}" for n in vitamins) + "\n\n"
        if minerals:
            result += "Minerals:\n" + "\n".join(f"- {n}" for n in minerals) + "\n\n"
        if other_nutrients:
            result += "Other Nutrients:\n" + "\n".join(f"- {n}" for n in other_nutrients)
        
        return result.strip()
        
    except Exception as e:
        return f"Error retrieving nutrient information: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
EOF

# Install dependencies
print_status "Installing Python dependencies..."
"$UV_PATH" sync

# Create .env file with API key
echo "USDA_API_KEY=$USDA_API_KEY" > .env

# Configure Claude for Desktop
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

print_status "Configuring Claude for Desktop..."

# Create config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Check if config file exists and has content
if [ -f "$CLAUDE_CONFIG_FILE" ] && [ -s "$CLAUDE_CONFIG_FILE" ]; then
    # Backup existing config
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_FILE.backup.$(date +%s)"
    print_status "Backed up existing Claude configuration"
    
    # Parse existing config and add our server
    python3 << EOF
import json
import sys

config_file = "$CLAUDE_CONFIG_FILE"
install_dir = "$INSTALL_DIR"
uv_path = "$UV_PATH"
api_key = "$USDA_API_KEY"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['usda-api'] = {
    "command": uv_path,
    "args": [
        "--directory",
        install_dir,
        "run",
        "main.py"
    ],
    "env": {
        "USDA_API_KEY": api_key
    }
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("Successfully updated Claude configuration")
EOF
else
    # Create new config file
    cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "usda-api": {
      "command": "$UV_PATH",
      "args": [
        "--directory",
        "$INSTALL_DIR",
        "run",
        "main.py"
      ],
      "env": {
        "USDA_API_KEY": "$USDA_API_KEY"
      }
    }
  }
}
EOF
    print_status "Created new Claude configuration"
fi

print_success "Installation completed successfully!"
echo ""
print_status "📋 What's installed:"
echo "   • USDA API MCP Server at: $INSTALL_DIR"
echo "   • 5 powerful food and nutrition tools"
echo "   • Automatic Claude for Desktop integration"
echo ""
print_status "🚀 Next steps:"
echo "   1. Restart Claude for Desktop completely"
echo "   2. Look for the tools icon (🔧) in Claude"
echo "   3. Try asking: 'Search for nutrition information about chicken breast'"
echo ""
print_status "💡 Available tools:"
echo "   • search_foods - Search the USDA food database"
echo "   • get_food_details - Get complete nutrition facts"
echo "   • get_multiple_foods - Compare multiple foods"
echo "   • list_foods - Browse the database"
echo "   • get_food_nutrients - Detailed nutrient analysis"
echo ""
print_warning "⚠️  Remember to restart Claude for Desktop to see the new tools!"
echo ""
