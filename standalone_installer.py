#!/usr/bin/env python3
"""
Standalone USDA API MCP Server Installer
Single file with no dependencies - works anywhere
"""

import subprocess
import os
import sys
import json
from pathlib import Path
import webbrowser
import tempfile

def show_message(title, message, is_error=False):
    """Show message using macOS native notification"""
    try:
        if is_error:
            cmd = f'display dialog "{message}" with title "{title}" with icon stop'
        else:
            cmd = f'display dialog "{message}" with title "{title}" with icon note'
        subprocess.run(['osascript', '-e', cmd], check=True)
    except:
        print(f"{title}: {message}")

def get_input(prompt, title="Input", is_password=False):
    """Get input using macOS native dialog"""
    try:
        if is_password:
            cmd = f'display dialog "{prompt}" with title "{title}" default answer "" with hidden answer'
        else:
            cmd = f'display dialog "{prompt}" with title "{title}" default answer ""'
        
        result = subprocess.run(['osascript', '-e', cmd], 
                              capture_output=True, text=True, check=True)
        
        # Extract the answer from AppleScript result
        output = result.stdout.strip()
        if "text returned:" in output:
            return output.split("text returned:")[1].strip()
        return ""
    except:
        return input(f"{prompt}: ")

def validate_api_key(api_key):
    """Simple API key validation"""
    try:
        import urllib.request
        import urllib.parse
        
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = urllib.parse.urlencode({
            'api_key': api_key,
            'query': 'test'
        })
        
        req = urllib.request.Request(f"{url}?{params}")
        response = urllib.request.urlopen(req, timeout=10)
        return response.getcode() == 200
    except:
        return False

def install_tools(api_key):
    """Install the USDA tools"""
    try:
        install_dir = Path.home() / ".usda-api-mcp"
        claude_config_dir = Path.home() / "Library/Application Support/Claude"
        
        # Create install directory
        if install_dir.exists():
            import shutil
            shutil.rmtree(install_dir)
        install_dir.mkdir(parents=True)
        
        # Create main.py with embedded content
        main_py_content = '''#!/usr/bin/env python3
"""
USDA API MCP Server
Provides access to USDA FoodData Central API through MCP
"""

import os
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("USDA API")

async def make_usda_request(endpoint: str, params: dict = None) -> dict:
    """Make a request to the USDA API with error handling"""
    api_key = os.getenv("USDA_API_KEY")
    if not api_key:
        raise ValueError("USDA_API_KEY environment variable is required")
    
    base_url = "https://api.nal.usda.gov"
    url = f"{base_url}/{endpoint}"
    
    if params is None:
        params = {}
    params["api_key"] = api_key
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise Exception("API request timed out")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

@mcp.tool()
async def search_foods(query: str, page_size: int = 10, page_number: int = 1) -> str:
    """Search for foods in the USDA database."""
    try:
        params = {
            "query": query,
            "pageSize": min(page_size, 200),
            "pageNumber": page_number
        }
        
        data = await make_usda_request("fdc/v1/foods/search", params)
        
        if not data.get("foods"):
            return f"No foods found for query: {query}"
        
        result = f"Found {data.get('totalHits', 0)} foods for '{query}':\\n\\n"
        
        for i, food in enumerate(data["foods"][:page_size], 1):
            fdc_id = food.get("fdcId", "N/A")
            description = food.get("description", "No description")
            brand_owner = food.get("brandOwner", "Generic")
            data_type = food.get("dataType", "N/A")
            
            result += f"{i}. {description}\\n"
            result += f"   FDC ID: {fdc_id} | Brand: {brand_owner} | Type: {data_type}\\n\\n"
        
        if data.get("totalHits", 0) > page_size:
            result += f"Showing {page_size} of {data['totalHits']} results. Use page_number parameter for more."
        
        return result
        
    except Exception as e:
        return f"Error searching foods: {str(e)}"

@mcp.tool()
async def get_food_details(fdc_id: int, nutrients: str = None) -> str:
    """Get detailed information about a specific food item by its FDC ID."""
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
        
        result = f"FDC ID: {fdc_id}\\nDescription: {description}\\nBrand: {brand_owner}\\nData Type: {data_type}\\n"
        
        if ingredients and ingredients != "Not available":
            result += f"Ingredients: {ingredients}\\n"
        
        if "foodNutrients" in data and data["foodNutrients"]:
            result += "\\nNutrition Facts (per 100g):\\n"
            for nutrient in data["foodNutrients"]:
                name = nutrient.get("nutrient", {}).get("name", "Unknown")
                value = nutrient.get("amount", 0)
                unit = nutrient.get("nutrient", {}).get("unitName", "")
                if value and value > 0:
                    result += f"- {name}: {value} {unit}\\n"
        
        if "foodCategory" in data:
            category = data["foodCategory"].get("description", "Unknown")
            result += f"\\nCategory: {category}"
        
        return result
        
    except Exception as e:
        return f"Error retrieving food details: {str(e)}"

if __name__ == "__main__":
    mcp.run()
'''
        
        with open(install_dir / "main.py", "w") as f:
            f.write(main_py_content)
        
        # Create pyproject.toml
        pyproject_content = '''[project]
name = "usda-api-mcp"
version = "0.1.0"
description = "MCP server for USDA API access"
requires-python = ">=3.11"
dependencies = [
    "mcp>=1.2.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0"
]
'''
        with open(install_dir / "pyproject.toml", "w") as f:
            f.write(pyproject_content)
        
        # Create .env file
        with open(install_dir / ".env", "w") as f:
            f.write(f"USDA_API_KEY={api_key}\n")
        
        # Try to install with uv
        uv_paths = [
            Path.home() / ".local/bin/uv",
            Path("/usr/local/bin/uv"),
            Path("/opt/homebrew/bin/uv")
        ]
        
        uv_path = None
        for path in uv_paths:
            if path.exists():
                uv_path = str(path)
                break
        
        if uv_path:
            subprocess.run([uv_path, "sync"], cwd=install_dir, check=True)
        
        # Configure Claude
        config_file = claude_config_dir / "claude_desktop_config.json"
        config = {}
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
            except:
                config = {}
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        if uv_path:
            config["mcpServers"]["usda-api"] = {
                "command": uv_path,
                "args": [
                    "--directory",
                    str(install_dir),
                    "run",
                    "main.py"
                ],
                "env": {
                    "USDA_API_KEY": api_key
                }
            }
        else:
            config["mcpServers"]["usda-api"] = {
                "command": "python3",
                "args": [str(install_dir / "main.py")],
                "env": {
                    "USDA_API_KEY": api_key
                }
            }
        
        # Write config
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        return True
        
    except Exception as e:
        show_message("Installation Error", f"Failed to install: {str(e)}", True)
        return False

def main():
    """Main installer function"""
    # Welcome message
    if not show_message("USDA Food Tools Installer", 
                       "Welcome! This will install USDA Food and Nutrition tools for Claude for Desktop.\n\nClick OK to continue."):
        return
    
    # Check for Claude
    claude_config_dir = Path.home() / "Library/Application Support/Claude"
    if not claude_config_dir.exists():
        show_message("Error", "Claude for Desktop not found. Please install Claude for Desktop first.", True)
        webbrowser.open("https://claude.ai/download")
        return
    
    # Get API key
    api_key = get_input("Please enter your USDA API key\n(Get one free at: fdc.nal.usda.gov/api-guide.html)", 
                       "API Key Required", True)
    
    if not api_key:
        show_message("Error", "API key is required for installation.", True)
        return
    
    # Validate API key
    show_message("Validating", "Validating your API key...")
    if not validate_api_key(api_key):
        show_message("Error", "Invalid API key. Please check and try again.", True)
        webbrowser.open("https://fdc.nal.usda.gov/api-guide.html")
        return
    
    # Install
    show_message("Installing", "Installing USDA Food Tools...")
    if install_tools(api_key):
        show_message("Success! 🎉", 
                    "Installation complete!\n\nNext steps:\n1. Restart Claude for Desktop completely\n2. Look for the tools icon (🔧) in Claude\n3. Try: 'What's the nutrition info for salmon?'\n\nEnjoy your new food tools!")
    else:
        show_message("Error", "Installation failed. Please try again.", True)

if __name__ == "__main__":
    main()
