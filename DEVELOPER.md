# USDA API MCP Server - Developer Guide

This guide is for developers who want to build, modify, or distribute the USDA API MCP Server.

## Project Structure

```
usda-api-mcp/
├── main.py              # Main MCP server application
├── pyproject.toml       # Python project configuration
├── install.sh           # Automated installer script
├── README.md            # User installation guide
├── DEVELOPER.md         # This file - developer documentation
├── USER_GUIDE.md        # Simple user guide
└── .env                 # Environment variables (not in git)
```

## Development Setup

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended) or `pip`
- macOS (for Claude for Desktop integration)
- USDA FoodData Central API key

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd usda-api-mcp
   ```

2. **Install dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your USDA_API_KEY
   ```

4. **Test the server:**
   ```bash
   # Using uv
   uv run main.py
   
   # Or using python
   python main.py
   ```

5. **Test with Claude for Desktop:**
   - Add server to `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Restart Claude for Desktop
   - Test the tools

## Architecture Overview

### MCP Server Structure

The server uses the FastMCP framework from the official MCP Python SDK:

- **FastMCP**: Automatic tool registration using decorators
- **Type hints**: Automatic parameter validation and documentation
- **Async/await**: Non-blocking HTTP requests to USDA API

### API Integration

- **Base URL**: `https://api.nal.usda.gov`
- **Authentication**: API key in query parameters
- **Rate limiting**: Handled gracefully with retries
- **Error handling**: Comprehensive error messages for users

### Tools Implemented

1. **search_foods**: Search with pagination and filtering
2. **get_food_details**: Detailed food information and nutrition
3. **get_multiple_foods**: Batch food comparison
4. **list_foods**: Database browsing with sorting
5. **get_food_nutrients**: Categorized nutrient analysis

## Building for Distribution

### Creating Release Packages

1. **Prepare the distribution:**
   ```bash
   # Clean previous builds
   rm -rf dist/
   mkdir dist/
   
   # Copy essential files
   cp main.py pyproject.toml install.sh dist/
   cp README.md USER_GUIDE.md DEVELOPER.md dist/
   ```

2. **Create archive:**
   ```bash
   cd dist/
   tar -czf usda-api-mcp-v1.0.tar.gz *
   ```

3. **Test installation:**
   ```bash
   # Extract and test the installer
   mkdir test-install
   cd test-install
   tar -xzf ../usda-api-mcp-v1.0.tar.gz
   chmod +x install.sh
   # Test with: ./install.sh
   ```

### Installer Script Features

The `install.sh` script provides:

- ✅ **Dependency checking**: Verifies Claude for Desktop installation
- ✅ **Automatic uv installation**: Installs uv if not present
- ✅ **Project setup**: Creates isolated installation directory
- ✅ **Configuration management**: Safely updates Claude config
- ✅ **Error handling**: Clear error messages and validation
- ✅ **Backup protection**: Backs up existing configurations

### Distribution Checklist

Before releasing:

- [ ] Test installer on clean macOS system
- [ ] Verify all tools work correctly
- [ ] Test with different Claude configurations
- [ ] Update version numbers in pyproject.toml
- [ ] Test with fresh USDA API key
- [ ] Verify error handling for invalid API keys
- [ ] Test uninstallation process

## Code Standards

### Python Code Style

- **PEP 8**: Follow Python style guidelines
- **Type hints**: Use comprehensive type annotations
- **Docstrings**: Document all public functions
- **Error handling**: Graceful error messages for users
- **Async/await**: Use async for all I/O operations

### MCP Tool Guidelines

- **Clear descriptions**: Each tool should have a clear purpose
- **Parameter validation**: Validate inputs before API calls
- **User-friendly output**: Format responses for readability
- **Error messages**: Helpful error messages for common issues
- **Documentation**: Complete docstrings with parameter descriptions

### Example Tool Implementation

```python
@mcp.tool()
async def example_tool(param1: str, param2: int = 10) -> str:
    """Brief description of what this tool does.
    
    Args:
        param1: Description of required parameter
        param2: Description of optional parameter (default: 10)
    """
    try:
        # Validate inputs
        if not param1.strip():
            return "Error: param1 cannot be empty"
        
        # Make API call
        data = await make_usda_request("endpoint", {"param": param1})
        
        # Format response
        if not data:
            return "No results found"
        
        return f"Result: {data}"
        
    except Exception as e:
        return f"Error: {str(e)}"
```

## Testing

### Manual Testing

1. **API connectivity:**
   ```bash
   # Test with curl
   curl "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=YOUR_KEY&query=apple"
   ```

2. **MCP server:**
   ```bash
   # Start server and send test messages
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | uv run main.py
   ```

3. **Claude integration:**
   - Test each tool individually
   - Test error scenarios (invalid API key, network issues)
   - Test large result sets and pagination

### Automated Testing

Consider adding:

- Unit tests for individual functions
- Integration tests for API calls
- End-to-end tests for Claude integration
- Performance tests for large datasets

## Troubleshooting Development Issues

### Common Issues

1. **uv not found:**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. **API key issues:**
   - Verify key is valid at USDA website
   - Check environment variable is set
   - Test with curl first

3. **Claude connection issues:**
   - Check logs: `tail -f ~/Library/Logs/Claude/mcp*.log`
   - Verify JSON configuration is valid
   - Restart Claude completely

4. **Python version issues:**
   ```bash
   # Check Python version
   python --version  # Should be 3.11+
   uv python list    # Show available Python versions
   ```

## Contributing

### Adding New Tools

1. Study the USDA API documentation
2. Implement the tool following existing patterns
3. Add comprehensive error handling
4. Test thoroughly with Claude
5. Update documentation

### Modifying Existing Tools

1. Maintain backward compatibility
2. Update docstrings if parameters change
3. Test all existing functionality
4. Consider performance implications

## Release Process

1. **Version bump**: Update version in `pyproject.toml`
2. **Test thoroughly**: Run full test suite
3. **Update documentation**: README, DEVELOPER.md, USER_GUIDE.md
4. **Create release package**: Use distribution process above
5. **Test installer**: On clean system
6. **Tag release**: Git tag with version number
7. **Distribute**: Share installer script and documentation

## API Documentation

### USDA FoodData Central API

- **Documentation**: https://fdc.nal.usda.gov/api-guide.html
- **Rate limits**: 3600 requests per hour per API key
- **Data types**: Foundation, SR Legacy, Survey (FNDDS), Branded
- **Response format**: JSON with nested objects

### Key Endpoints Used

- `GET /fdc/v1/foods/search` - Search foods
- `GET /fdc/v1/food/{fdcId}` - Get food details
- `POST /fdc/v1/foods` - Get multiple foods
- `GET /fdc/v1/foods/list` - List foods

## Security Considerations

- **API key protection**: Never log or expose API keys
- **Input validation**: Sanitize all user inputs
- **Error handling**: Don't expose internal errors to users
- **Dependencies**: Keep dependencies updated for security

## Performance Optimization

- **Caching**: Consider caching frequent requests
- **Batch requests**: Use bulk endpoints when possible
- **Pagination**: Implement reasonable default page sizes
- **Timeouts**: Set appropriate request timeouts
- **Rate limiting**: Respect USDA API rate limits
