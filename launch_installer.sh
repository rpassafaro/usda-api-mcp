#!/bin/bash
# USDA Food Tools Installer Launcher
# This script launches the web-based installer

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to that directory
cd "$SCRIPT_DIR"

# Launch the Python web installer
python3 gui_installer.py
