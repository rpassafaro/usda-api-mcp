#!/usr/bin/env python3
"""
Fixed USDA API MCP Server GUI Installer
Simpler version without complex threading
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import json
import webbrowser
from pathlib import Path
import requests

class USDAInstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("USDA Food Tools for Claude - Installer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Ensure window is visible
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        
        # Variables
        self.api_key = tk.StringVar()
        self.install_dir = Path.home() / ".usda-api-mcp"
        self.claude_config_dir = Path.home() / "Library/Application Support/Claude"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame, 
            text="🍎 USDA Food Tools for Claude",
            font=("Arial", 20, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="Add powerful food and nutrition tools to Claude for Desktop",
            font=("Arial", 12)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Features section
        features_frame = ttk.LabelFrame(main_frame, text="What You'll Get", padding="10")
        features_frame.pack(fill=tk.X, pady=(0, 20))
        
        features = [
            "🔍 Search 500,000+ foods from USDA database",
            "📊 Get complete nutrition facts for any food",
            "🍎 Compare foods side-by-side",
            "🧪 Analyze nutrients in detail",
            "📋 Browse food categories"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text=feature).pack(anchor=tk.W, pady=2)
        
        # API Key section
        api_frame = ttk.LabelFrame(main_frame, text="USDA API Key", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        api_info = ttk.Label(
            api_frame,
            text="You need a free API key from USDA FoodData Central:"
        )
        api_info.pack(anchor=tk.W, pady=(0, 5))
        
        api_button_frame = ttk.Frame(api_frame)
        api_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            api_button_frame,
            text="🌐 Get Free API Key",
            command=self.open_api_page
        ).pack(side=tk.LEFT)
        
        api_entry_frame = ttk.Frame(api_frame)
        api_entry_frame.pack(fill=tk.X)
        
        ttk.Label(api_entry_frame, text="Enter your API key:").pack(anchor=tk.W)
        self.api_entry = ttk.Entry(api_entry_frame, textvariable=self.api_key, width=50, show="*")
        self.api_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Status section
        self.status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(self.status_frame, text="Ready to install")
        self.status_label.pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.install_button = ttk.Button(
            button_frame,
            text="🚀 Install USDA Tools",
            command=self.start_installation
        )
        self.install_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self.root.quit
        ).pack(side=tk.RIGHT)
    
    def open_api_page(self):
        """Open USDA API registration page"""
        webbrowser.open("https://fdc.nal.usda.gov/api-guide.html")
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message)
        self.root.update()
    
    def start_installation(self):
        """Start the installation process"""
        api_key = self.api_key.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter your USDA API key")
            return
        
        # Disable install button
        self.install_button.config(state="disabled")
        
        try:
            # Step 1: Check Claude
            self.update_status("Checking for Claude for Desktop...")
            if not self.claude_config_dir.exists():
                messagebox.showerror("Error", "Claude for Desktop not found. Please install it first.")
                self.install_button.config(state="normal")
                return
            
            # Step 2: Test API key
            self.update_status("Validating API key...")
            if not self.validate_api_key(api_key):
                messagebox.showerror("Error", "Invalid API key. Please check and try again.")
                self.install_button.config(state="normal")
                return
            
            # Step 3: Install
            self.update_status("Installing...")
            success = self.install_tools(api_key)
            
            if success:
                self.update_status("Installation complete!")
                messagebox.showinfo("Success!", 
                    "🎉 Installation successful!\n\n"
                    "Next steps:\n"
                    "1. Restart Claude for Desktop completely\n"
                    "2. Look for the tools icon (🔧) in Claude\n"
                    "3. Try: 'What's the nutrition info for salmon?'"
                )
            else:
                messagebox.showerror("Error", "Installation failed. Please try again.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
        
        self.install_button.config(state="normal")
    
    def validate_api_key(self, api_key):
        """Simple API key validation"""
        try:
            response = requests.get(
                "https://api.nal.usda.gov/fdc/v1/foods/search",
                params={"api_key": api_key, "query": "test"},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def install_tools(self, api_key):
        """Install the tools"""
        try:
            # Create installation directory
            if self.install_dir.exists():
                import shutil
                shutil.rmtree(self.install_dir)
            self.install_dir.mkdir(parents=True)
            
            # Copy main.py from current directory
            main_py_source = Path(__file__).parent / "main.py"
            if main_py_source.exists():
                import shutil
                shutil.copy2(main_py_source, self.install_dir / "main.py")
            
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
            with open(self.install_dir / "pyproject.toml", "w") as f:
                f.write(pyproject_content)
            
            # Create .env file
            with open(self.install_dir / ".env", "w") as f:
                f.write(f"USDA_API_KEY={api_key}\n")
            
            # Install dependencies with uv
            self.update_status("Installing dependencies...")
            uv_path = self.get_uv_path()
            if uv_path:
                subprocess.run([uv_path, "sync"], cwd=self.install_dir, check=True)
            
            # Configure Claude
            self.update_status("Configuring Claude...")
            self.configure_claude(uv_path or "python3", api_key)
            
            return True
        except Exception as e:
            print(f"Installation error: {e}")
            return False
    
    def get_uv_path(self):
        """Get uv path or install it"""
        # Check common locations
        paths = [
            Path.home() / ".local/bin/uv",
            Path("/usr/local/bin/uv"),
            Path("/opt/homebrew/bin/uv")
        ]
        
        for path in paths:
            if path.exists():
                return str(path)
        
        # Try to install uv
        try:
            subprocess.run([
                "curl", "-LsSf", "https://astral.sh/uv/install.sh"
            ], capture_output=True, text=True, check=True, input="y\n")
            
            uv_path = Path.home() / ".local/bin/uv"
            if uv_path.exists():
                return str(uv_path)
        except:
            pass
        
        return None
    
    def configure_claude(self, python_cmd, api_key):
        """Configure Claude for Desktop"""
        config_file = self.claude_config_dir / "claude_desktop_config.json"
        
        # Read existing config
        config = {}
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
            except:
                config = {}
        
        # Add our server
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        if python_cmd.endswith("uv"):
            config["mcpServers"]["usda-api"] = {
                "command": python_cmd,
                "args": [
                    "--directory",
                    str(self.install_dir),
                    "run",
                    "main.py"
                ],
                "env": {
                    "USDA_API_KEY": api_key
                }
            }
        else:
            config["mcpServers"]["usda-api"] = {
                "command": python_cmd,
                "args": [str(self.install_dir / "main.py")],
                "env": {
                    "USDA_API_KEY": api_key
                }
            }
        
        # Write config
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    print("Starting USDA Food Tools GUI Installer...")
    
    if sys.platform != "darwin":
        print("This installer is designed for macOS only.")
        sys.exit(1)
    
    app = USDAInstallerGUI()
    app.run()

if __name__ == "__main__":
    main()
