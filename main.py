import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("usda-api")

# Constants
USDA_API_BASE = "https://api.nal.usda.gov"
API_KEY = os.getenv("USDA_API_KEY")

async def make_usda_request(endpoint: str, params: dict[str, Any] = None) -> dict[str, Any] | None:
    """Make a request to the USDA API with proper error handling."""
    if not API_KEY:
        raise ValueError("USDA_API_KEY environment variable is required")
    
    headers = {
        "User-Agent": "usda-mcp-server/1.0",
        "Accept": "application/json"
    }
    
    # Add API key to parameters
    if params is None:
        params = {}
    params["api_key"] = API_KEY
    
    url = f"{USDA_API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"USDA API request failed: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error: {e}")

@mcp.tool()
async def search_foods(query: str, page_size: int = 50, data_type: str = None, page_number: int = 1) -> str:
    """Search for foods in the USDA FoodData Central database.
    
    Args:
        query: Search term for food items
        page_size: Number of results to return (default: 50, max: 200)
        data_type: Optional data type filter (e.g., 'Foundation', 'SR Legacy', 'Survey')
        page_number: Page number for pagination (default: 1)
    """
    try:
        params = {
            "query": query,
            "pageSize": min(page_size, 200),
            "pageNumber": page_number
        }
        
        if data_type:
            params["dataType"] = data_type
        
        data = await make_usda_request("fdc/v1/foods/search", params)
        
        if not data or "foods" not in data:
            return "No foods found for the given query."
        
        foods = data["foods"]
        total_hits = data.get("totalHits", 0)
        
        if not foods:
            return "No foods found for the given query."
        
        results = []
        for food in foods:
            description = food.get("description", "No description")
            fdc_id = food.get("fdcId", "N/A")
            brand_owner = food.get("brandOwner", "Generic")
            data_type = food.get("dataType", "N/A")
            
            # Include basic nutrition if available
            nutrients_text = ""
            if "foodNutrients" in food and food["foodNutrients"]:
                key_nutrients = []
                for nutrient in food["foodNutrients"][:3]:  # Show first 3 nutrients
                    name = nutrient.get("nutrientName", "Unknown")
                    value = nutrient.get("value", 0)
                    unit = nutrient.get("unitName", "")
                    key_nutrients.append(f"{name}: {value} {unit}")
                if key_nutrients:
                    nutrients_text = f"\nKey Nutrients: {', '.join(key_nutrients)}"
            
            result = f"ID: {fdc_id}\nDescription: {description}\nBrand: {brand_owner}\nData Type: {data_type}{nutrients_text}"
            results.append(result)
        
        return f"Found {total_hits} total foods. Showing page {page_number} ({len(results)} results):\n\n" + "\n---\n".join(results)
        
    except Exception as e:
        return f"Error searching foods: {str(e)}"

@mcp.tool()
async def get_food_details(fdc_id: int, nutrients: str = None) -> str:
    """Get detailed information about a specific food item by its FDC ID.
    
    Args:
        fdc_id: FoodData Central ID of the food item
        nutrients: Optional comma-separated list of nutrient numbers to include
    """
    try:
        params = {}
        if nutrients:
            params["nutrients"] = nutrients
        
        data = await make_usda_request(f"fdc/v1/food/{fdc_id}", params)
        
        if not data:
            return f"No food found with FDC ID: {fdc_id}"
        
        description = data.get("description", "No description")
        brand_owner = data.get("brandOwner", "Generic")
        data_type = data.get("dataType", "N/A")
        ingredients = data.get("ingredients", "Not available")
        
        result = f"FDC ID: {fdc_id}\nDescription: {description}\nBrand: {brand_owner}\nData Type: {data_type}\n"
        
        if ingredients and ingredients != "Not available":
            result += f"Ingredients: {ingredients}\n"
        
        # Add nutrition information
        if "foodNutrients" in data and data["foodNutrients"]:
            result += "\nNutrition Facts (per 100g):\n"
            for nutrient in data["foodNutrients"]:
                name = nutrient.get("nutrient", {}).get("name", "Unknown")
                value = nutrient.get("amount", 0)
                unit = nutrient.get("nutrient", {}).get("unitName", "")
                if value and value > 0:
                    result += f"- {name}: {value} {unit}\n"
        
        # Add food category if available
        if "foodCategory" in data:
            category = data["foodCategory"].get("description", "Unknown")
            result += f"\nCategory: {category}"
        
        return result
        
    except Exception as e:
        return f"Error retrieving food details: {str(e)}"

@mcp.tool()
async def get_multiple_foods(fdc_ids: str, nutrients: str = None) -> str:
    """Get details for multiple food items by their FDC IDs.
    
    Args:
        fdc_ids: Comma-separated list of FDC IDs (e.g., "123456,789012,345678")
        nutrients: Optional comma-separated list of nutrient numbers to include
    """
    try:
        # Parse the comma-separated FDC IDs
        id_list = [int(id.strip()) for id in fdc_ids.split(",")]
        
        if len(id_list) > 20:
            return "Error: Maximum 20 FDC IDs allowed per request"
        
        params = {"fdcIds": id_list}
        if nutrients:
            params["nutrients"] = nutrients
        
        # Use POST method for multiple IDs
        url = f"{USDA_API_BASE}/fdc/v1/foods"
        headers = {
            "User-Agent": "usda-mcp-server/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        request_data = params.copy()
        request_data["api_key"] = API_KEY
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=request_data, timeout=30.0)
            response.raise_for_status()
            data = response.json()
        
        if not data:
            return "No foods found for the provided FDC IDs"
        
        results = []
        for food in data:
            fdc_id = food.get("fdcId", "N/A")
            description = food.get("description", "No description")
            brand_owner = food.get("brandOwner", "Generic")
            
            # Basic nutrition summary
            nutrition_summary = ""
            if "foodNutrients" in food and food["foodNutrients"]:
                calories = next((n.get("amount", 0) for n in food["foodNutrients"] 
                               if n.get("nutrient", {}).get("name") == "Energy"), None)
                if calories:
                    nutrition_summary = f" | Calories: {calories} kcal"
            
            result = f"ID: {fdc_id} | {description} | Brand: {brand_owner}{nutrition_summary}"
            results.append(result)
        
        return f"Retrieved {len(results)} foods:\n\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error retrieving multiple foods: {str(e)}"

@mcp.tool()
async def list_foods(page_size: int = 50, page_number: int = 1, data_type: str = None, sort_by: str = None) -> str:
    """Get a paginated list of foods in abridged format for browsing.
    
    Args:
        page_size: Number of results to return (default: 50, max: 200)
        page_number: Page number for pagination (default: 1)
        data_type: Optional data type filter (e.g., 'Foundation', 'SR Legacy', 'Survey')
        sort_by: Optional sort field (e.g., 'dataType.keyword', 'description.keyword')
    """
    try:
        params = {
            "pageSize": min(page_size, 200),
            "pageNumber": page_number
        }
        
        if data_type:
            params["dataType"] = data_type
        if sort_by:
            params["sortBy"] = sort_by
        
        data = await make_usda_request("fdc/v1/foods/list", params)
        
        if not data:
            return "No foods found"
        
        foods = data
        if not foods:
            return "No foods found"
        
        results = []
        for food in foods:
            fdc_id = food.get("fdcId", "N/A")
            description = food.get("description", "No description")
            data_type = food.get("dataType", "N/A")
            publication_date = food.get("publicationDate", "N/A")
            
            result = f"ID: {fdc_id} | {description} | Type: {data_type} | Published: {publication_date}"
            results.append(result)
        
        return f"Foods list (Page {page_number}, {len(results)} results):\n\n" + "\n".join(results)
        
    except Exception as e:
        return f"Error listing foods: {str(e)}"

@mcp.tool()
async def get_food_nutrients(fdc_id: int, nutrient_names: str = None) -> str:
    """Get detailed nutrient information for a specific food item.
    
    Args:
        fdc_id: FoodData Central ID of the food item
        nutrient_names: Optional comma-separated list of nutrient names to filter (e.g., "Energy,Protein,Total lipid")
    """
    try:
        data = await make_usda_request(f"fdc/v1/food/{fdc_id}")
        
        if not data:
            return f"No food found with FDC ID: {fdc_id}"
        
        description = data.get("description", "No description")
        
        if "foodNutrients" not in data or not data["foodNutrients"]:
            return f"No nutrient data available for {description} (FDC ID: {fdc_id})"
        
        result = f"Nutrient Information for: {description} (FDC ID: {fdc_id})\n\n"
        
        # Filter nutrients if specific names requested
        nutrients_to_show = data["foodNutrients"]
        if nutrient_names:
            filter_names = [name.strip().lower() for name in nutrient_names.split(",")]
            nutrients_to_show = [
                n for n in data["foodNutrients"] 
                if any(filter_name in n.get("nutrient", {}).get("name", "").lower() 
                      for filter_name in filter_names)
            ]
        
        # Group nutrients by category
        macro_nutrients = []
        vitamins = []
        minerals = []
        other_nutrients = []
        
        for nutrient in nutrients_to_show:
            name = nutrient.get("nutrient", {}).get("name", "Unknown")
            value = nutrient.get("amount", 0)
            unit = nutrient.get("nutrient", {}).get("unitName", "")
            
            if value and value > 0:
                nutrient_line = f"{name}: {value} {unit}"
                
                # Categorize nutrients
                name_lower = name.lower()
                if any(macro in name_lower for macro in ["energy", "protein", "carbohydrate", "fat", "lipid", "fiber"]):
                    macro_nutrients.append(nutrient_line)
                elif any(vitamin in name_lower for vitamin in ["vitamin", "folate", "niacin", "thiamin", "riboflavin"]):
                    vitamins.append(nutrient_line)
                elif any(mineral in name_lower for mineral in ["calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc"]):
                    minerals.append(nutrient_line)
                else:
                    other_nutrients.append(nutrient_line)
        
        # Format output by category
        if macro_nutrients:
            result += "Macronutrients:\n" + "\n".join(f"- {n}" for n in macro_nutrients) + "\n\n"
        if vitamins:
            result += "Vitamins:\n" + "\n".join(f"- {n}" for n in vitamins) + "\n\n"
        if minerals:
            result += "Minerals:\n" + "\n".join(f"- {n}" for n in minerals) + "\n\n"
        if other_nutrients:
            result += "Other Nutrients:\n" + "\n".join(f"- {n}" for n in other_nutrients)
        
        return result.strip()
        
    except Exception as e:
        return f"Error retrieving nutrient information: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
