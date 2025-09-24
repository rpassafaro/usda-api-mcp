# Changelog

All notable changes to USDA Food Tools for Claude will be documented in this file.

## [Unreleased]

## [1.0.0] - 2025-09-24

### Added
- Complete USDA FoodData Central API integration
- 5 powerful MCP tools for food and nutrition data
- Beautiful web-based GUI installer
- Native Mac app bundle distribution
- Command-line installer script
- Automatic port conflict resolution
- Self-contained installer with embedded dependencies
- Comprehensive documentation

### Features
- **search_foods** - Search USDA food database (500,000+ foods)
- **get_food_details** - Detailed nutrition facts and information
- **get_multiple_foods** - Bulk lookup for multiple foods
- **list_foods** - Browse foods with pagination
- **get_food_nutrients** - Get specific nutrient data

### Technical
- MCP (Model Context Protocol) server implementation
- FastMCP framework integration
- HTTPX for async API requests
- Python-dotenv for environment management
- Simple Mac app bundle (no py2app complexity)
- Automatic cleanup of existing processes
- Smart port detection and binding

### Distribution
- 11KB Mac app installer
- Web-based installation interface
- GitHub releases with downloadable assets
- Cross-platform command-line installer

## [0.1.0] - Initial Development

### Added
- Basic MCP server structure
- USDA API integration
- Initial search functionality
