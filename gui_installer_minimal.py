#!/usr/bin/env python3
"""
Minimal USDA API MCP Server GUI Installer
Super simple version to debug blank window issues
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os
import sys
import json
from pathlib import Path

def main():
    # Force tkinter to show window
    root = tk.Tk()
    root.withdraw()  # Hide root window initially
    
    # Show a simple message box first to test if GUI works at all
    result = messagebox.askyesno(
        "USDA Food Tools Installer", 
        "🍎 Install USDA Food Tools for Claude?\n\n"
        "This will add powerful nutrition and food search tools to Claude for Desktop.\n\n"
        "Click Yes to continue with installation."
    )
    
    if not result:
        messagebox.showinfo("Cancelled", "Installation cancelled.")
        return
    
    # Get API key
    api_key = simpledialog.askstring(
        "API Key Required",
        "Enter your USDA API key:\n\n"
        "(Get one free at: fdc.nal.usda.gov/api-guide.html)",
        show='*'
    )
    
    if not api_key:
        messagebox.showerror("Error", "API key is required for installation.")
        return
    
    # Show progress
    messagebox.showinfo("Installing", "Installing... This may take a moment.")
    
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
        
        # Success message
        messagebox.showinfo(
            "Success! 🎉", 
            "Installation complete!\n\n"
            "Next steps:\n"
            "1. Restart Claude for Desktop completely\n"
            "2. Look for the tools icon (🔧) in Claude\n"
            "3. Try: 'What's the nutrition info for salmon?'\n\n"
            "Enjoy your new food tools!"
        )
        
    except Exception as e:
        messagebox.showerror("Installation Failed", f"Error: {str(e)}")
    
    finally:
        root.destroy()

if __name__ == "__main__":
    main()
