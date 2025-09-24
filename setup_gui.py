"""
Setup script to create a native Mac .app bundle for the USDA installer
Uses py2app to create a standalone Mac application
"""

from setuptools import setup
import sys

# Ensure we're on macOS
if sys.platform != 'darwin':
    print("This setup script is for macOS only")
    sys.exit(1)

APP = ['gui_installer.py']
DATA_FILES = [
    ('', ['main.py', 'pyproject.toml']),  # Include the actual server files
]

OPTIONS = {
    'argv_emulation': True,  # Enable this for better compatibility
    'iconfile': None,  # We could add a custom icon here
    'plist': {
        'CFBundleName': 'USDA Food Tools Installer',
        'CFBundleDisplayName': 'USDA Food Tools Installer',
        'CFBundleGetInfoString': 'Install USDA Food and Nutrition Tools for Claude for Desktop',
        'CFBundleIdentifier': 'com.usdaapi.mcp.installer',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
    'packages': ['http', 'socketserver', 'webbrowser', 'threading', 'urllib', 'json', 'subprocess', 'pathlib'],
    'includes': [
        'http.server', 'socketserver', 'webbrowser', 'threading', 
        'urllib.parse', 'pathlib', 'json', 'time', 'subprocess', 
        'os', 'sys', 'shutil'
    ],
    'excludes': ['test', 'unittest', 'distutils', 'tkinter', 'email', 'xml'],
    'site_packages': True,  # Include site-packages
    'strip': False,  # Don't strip for debugging
    'optimize': 0,  # No optimization for debugging
}

setup(
    name='USDA Food Tools Installer',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        # No external dependencies needed for web installer
    ],
)
