# USDA Food & Nutrition Tools for Claude

Get instant access to comprehensive food and nutrition data directly in Claude for Desktop! 🍎📊

## What You Get

After installation, you'll have **5 powerful tools** in Claude:

- 🔍 **Search foods** - Find any food in the USDA database
- 📊 **Nutrition facts** - Get detailed nutrition information
- 🍎 **Compare foods** - Side-by-side nutrition comparison
- 📋 **Browse database** - Explore thousands of foods
- 🧪 **Nutrient analysis** - Deep dive into specific nutrients

## Super Simple Installation

Choose your preferred method:

### 🖱️ **Option 1: GUI Installer (Easiest)**
1. **Get API Key**: Go to https://fdc.nal.usda.gov/api-guide.html and get your free key
2. **Download**: Get [`USDA Food Tools Installer.zip`](dist/USDA%20Food%20Tools%20Installer.zip)
3. **Install**: Extract and double-click the app
4. **Follow prompts**: Beautiful interface guides you through everything
5. **Restart Claude**: Quit and restart Claude for Desktop

### ⚡ **Option 2: Command Line (Quick)**
1. **Get API Key**: Go to https://fdc.nal.usda.gov/api-guide.html and get your free key
2. **Download**: Get [`install.sh`](./install.sh)
3. **Run**: Open Terminal, navigate to the file, and run:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
4. **Enter API key** when prompted
5. **Restart Claude**: Quit and restart Claude for Desktop

## That's It! 🎉

Now you can ask Claude things like:
- "What's the nutrition information for salmon?"
- "Compare the protein content of chicken breast vs tofu"
- "Search for high-fiber breakfast foods"
- "Show me the vitamin content of spinach"

## Examples

**Search for foods:**
> "Search for organic apples"

**Get detailed nutrition:**
> "Get nutrition facts for avocado"

**Compare foods:**
> "Compare the nutrition of brown rice vs quinoa"

**Find specific nutrients:**
> "What foods are high in iron?"

## Troubleshooting

### Common Issues

**Tools not showing in Claude?**
- Make sure you completely quit and restarted Claude for Desktop
- Check that you entered your API key correctly during installation
- Look for the tools/search icon (🔧) in Claude's interface

**GUI Installer opens in Xcode instead of running?**
- Use the Mac App version instead: [`USDA Food Tools Installer.zip`](dist/USDA%20Food%20Tools%20Installer.zip)
- Extract the zip and double-click the `.app` file

**Installation failed?**
- Ensure you have an internet connection
- Verify your API key is correct at: https://fdc.nal.usda.gov/api-guide.html
- Try the alternative installation method (GUI vs command line)
- Check that Claude for Desktop is installed

**API key issues?**
- Get a fresh key from: https://fdc.nal.usda.gov/api-guide.html
- Make sure you're copying the entire key (no extra spaces)
- The key should be a long string of letters and numbers

**Commands not working?**
- The USDA database only includes foods (not supplements or medications)
- Try more specific food names: "chicken breast" instead of just "chicken"
- Check that the tools are actually available in Claude's interface

## What's Installed

The installer creates a folder at `~/.usda-api-mcp` with everything needed to run the tools. It also automatically configures Claude for Desktop to use these tools.

**Uninstalling:** Just delete the `~/.usda-api-mcp` folder and remove the "usda-api" entry from your Claude configuration.

---

*Powered by the USDA FoodData Central database - the most comprehensive nutrition database available!*
