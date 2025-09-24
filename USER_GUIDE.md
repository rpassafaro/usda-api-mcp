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

### Step 1: Get Your API Key (Free!)
1. Go to: https://fdc.nal.usda.gov/api-guide.html
2. Click "Get Data API Key" 
3. Fill out the simple form
4. Save the API key they email you

### Step 2: Download & Run
1. Download this file: [`install.sh`](./install.sh)
2. Open Terminal (found in Applications > Utilities)
3. Type: `cd Downloads` (or wherever you saved the file)
4. Type: `chmod +x install.sh`
5. Type: `./install.sh`
6. Enter your API key when prompted

### Step 3: Restart Claude
- Completely quit and restart Claude for Desktop
- Look for the tools icon (🔧) in Claude

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

**Tools not showing in Claude?**
- Make sure you completely restarted Claude for Desktop
- Check that you entered your API key correctly during installation

**Installation failed?**
- Make sure you have an internet connection
- Try running the installer again
- Make sure your API key is correct

**Need help?**
- Double-check your API key at: https://fdc.nal.usda.gov/api-guide.html
- The USDA database only includes foods (not supplements or medications)

## What's Installed

The installer creates a folder at `~/.usda-api-mcp` with everything needed to run the tools. It also automatically configures Claude for Desktop to use these tools.

**Uninstalling:** Just delete the `~/.usda-api-mcp` folder and remove the "usda-api" entry from your Claude configuration.

---

*Powered by the USDA FoodData Central database - the most comprehensive nutrition database available!*
