#!/usr/bin/env python3
"""
USDA API MCP Server Web-Based Installer
Opens a beautiful web interface in your browser
"""

import http.server
import socketserver
import webbrowser
import threading
import json
import subprocess
import os
import sys
from pathlib import Path
import urllib.parse
import time

class InstallerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path.startswith('/install'):
            self.handle_install()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_install(self):
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        api_key = params.get('api_key', [''])[0]
        
        if not api_key:
            self.send_json({'error': 'API key is required'})
            return
        
        try:
            # Installation logic
            install_dir = Path.home() / ".usda-api-mcp"
            claude_config_dir = Path.home() / "Library/Application Support/Claude"
            
            # Create install directory
            if install_dir.exists():
                import shutil
                shutil.rmtree(install_dir)
            install_dir.mkdir(parents=True)
            
            # Copy main.py if it exists
            main_py_source = Path(__file__).parent / "main.py"
            if main_py_source.exists():
                import shutil
                shutil.copy2(main_py_source, install_dir / "main.py")
            else:
                # Create embedded main.py
                with open(install_dir / "main.py", "w") as f:
                    f.write(EMBEDDED_MAIN_PY)
            
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
            
            self.send_json({'success': True, 'message': 'Installation completed successfully!'})
            
        except Exception as e:
            self.send_json({'error': str(e)})
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

# Embedded main.py content
EMBEDDED_MAIN_PY = '''#!/usr/bin/env python3
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

if __name__ == "__main__":
    mcp.run()
'''

# HTML content for the web installer
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>USDA Food Tools - Installer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            width: 90%;
            text-align: center;
        }
        
        .icon {
            font-size: 60px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #2d3748;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            color: #718096;
            margin-bottom: 30px;
            font-size: 16px;
        }
        
        .features {
            text-align: left;
            margin: 30px 0;
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
        }
        
        .feature {
            margin: 8px 0;
            font-size: 14px;
            color: #4a5568;
        }
        
        .input-group {
            margin: 20px 0;
            text-align: left;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2d3748;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .api-link {
            font-size: 12px;
            color: #718096;
            margin-top: 5px;
        }
        
        .api-link a {
            color: #667eea;
            text-decoration: none;
        }
        
        .install-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            margin-top: 20px;
        }
        
        .install-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        
        .install-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        
        .status.success {
            background: #f0fff4;
            color: #22543d;
            border: 1px solid #9ae6b4;
        }
        
        .status.error {
            background: #fed7d7;
            color: #742a2a;
            border: 1px solid #fc8181;
        }
        
        .status.loading {
            background: #ebf8ff;
            color: #2a4365;
            border: 1px solid #90cdf4;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🍎</div>
        <h1>USDA Food Tools</h1>
        <p class="subtitle">Add powerful nutrition and food search tools to Claude for Desktop</p>
        
        <div class="features">
            <div class="feature">🔍 Search 500,000+ foods from the USDA database</div>
            <div class="feature">📊 Get detailed nutrition facts for any food</div>
            <div class="feature">🧪 Analyze nutrients and compare foods</div>
            <div class="feature">📋 Browse food categories and brands</div>
        </div>
        
        <div class="input-group">
            <label for="apiKey">USDA API Key:</label>
            <input type="password" id="apiKey" placeholder="Enter your API key..." />
            <div class="api-link">
                <a href="https://fdc.nal.usda.gov/api-guide.html" target="_blank">Get a free API key here</a>
            </div>
        </div>
        
        <button class="install-btn" onclick="install()">
            🚀 Install USDA Tools
        </button>
        
        <div id="status" class="status"></div>
    </div>
    
    <script>
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.className = `status ${type}`;
            status.innerHTML = message;
            status.style.display = 'block';
        }
        
        function install() {
            const apiKey = document.getElementById('apiKey').value.trim();
            const button = document.querySelector('.install-btn');
            
            if (!apiKey) {
                showStatus('Please enter your USDA API key', 'error');
                return;
            }
            
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> Installing...';
            showStatus('Installing USDA Food Tools... This may take a moment.', 'loading');
            
            fetch(`/install?api_key=${encodeURIComponent(apiKey)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showStatus(`
                            🎉 Installation successful!<br><br>
                            <strong>Next steps:</strong><br>
                            1. Restart Claude for Desktop completely<br>
                            2. Look for the tools icon (🔧) in Claude<br>
                            3. Try: "What's the nutrition info for salmon?"<br><br>
                            Enjoy your new food tools!
                        `, 'success');
                        button.innerHTML = '✅ Installation Complete';
                    } else {
                        showStatus(`Installation failed: ${data.error}`, 'error');
                        button.disabled = false;
                        button.innerHTML = '🚀 Install USDA Tools';
                    }
                })
                .catch(error => {
                    showStatus(`Installation failed: ${error.message}`, 'error');
                    button.disabled = false;
                    button.innerHTML = '🚀 Install USDA Tools';
                });
        }
        
        // Allow Enter key to trigger install
        document.getElementById('apiKey').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                install();
            }
        });
    </script>
</body>
</html>'''

def main():
    """Start the web installer"""
    port = 8765
    
    print("🍎 USDA Food Tools - Web Installer")
    print("=" * 40)
    print(f"Starting installer server on port {port}...")
    
    # Start the HTTP server
    with socketserver.TCPServer(("", port), InstallerHandler) as httpd:
        # Open browser
        url = f"http://localhost:{port}"
        print(f"Opening installer in your browser: {url}")
        
        # Give the server a moment to start
        def open_browser():
            time.sleep(1)
            webbrowser.open(url)
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        print("\\nPress Ctrl+C to stop the installer when done.")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n✅ Installer stopped. Installation should be complete!")

if __name__ == "__main__":
    main()
