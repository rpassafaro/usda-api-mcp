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
    'argv_emulation': False,
    'iconfile': None,  # We could add a custom icon here
    'plist': {
        'CFBundleName': 'USDA Food Tools Installer',
        'CFBundleDisplayName': 'USDA Food Tools Installer',
        'CFBundleGetInfoString': 'Install USDA Food and Nutrition Tools for Claude for Desktop',
        'CFBundleIdentifier': 'com.usdaapi.mcp.installer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
    },
    'packages': ['tkinter', 'requests'],
    'includes': ['tkinter.ttk'],
    'excludes': ['test', 'unittest', 'distutils'],
    'strip': True,
    'optimize': 2,
}

setup(
    name='USDA Food Tools Installer',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'requests>=2.25.0',
    ],
)
