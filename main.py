import os
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load environment variables (your API key)
load_dotenv()

# Initialize the FastMCP server
mcp = FastMCP("AccuWeather Server 🌦️")

# AccuWeather API configuration
ACCUWEATHER_API_KEY = os.getenv("ACCUWEATHER_API_KEY")
ACCUWEATHER_BASE_URL = "http://dataservice.accuweather.com"

@mcp.tool
def get_weather_by_city(city: str) -> dict:
    """
    Fetches the current weather for a specific city using the AccuWeather API.
    This is a two-step process: first find the location, then get the weather.
    """
    if not ACCUWEATHER_API_KEY:
        return {"error": "AccuWeather API key not configured on server."}

    try:
        # --- Step 1: Get the AccuWeather Location Key for the city ---
        location_url = f"{ACCUWEATHER_BASE_URL}/locations/v1/cities/search"
        location_params = {
            "apikey": ACCUWEATHER_API_KEY,
            "q": city
        }
        
        location_response = requests.get(location_url, params=location_params)
        location_response.raise_for_status() # Raise an error for bad responses
        
        locations = location_response.json()
        if not locations:
            return {"error": f"City '{city}' not found."}
        
        # Use the first match
        location_key = locations[0]['Key']
        location_name = locations[0]['QualifiedName']

        # --- Step 2: Get the Current Conditions using the Location Key ---
        conditions_url = f"{ACCUWEATHER_BASE_URL}/currentconditions/v1/{location_key}"
        conditions_params = {
            "apikey": ACCUWEATHER_API_KEY
        }
        
        conditions_response = requests.get(conditions_url, params=conditions_params)
        conditions_response.raise_for_status()
        
        current_conditions = conditions_response.json()
        if not current_conditions:
            return {"error": "Could not retrieve current conditions."}

        # --- Step 3: Format and return the result ---
        weather_data = current_conditions[0]
        return {
            "location": location_name,
            "condition": weather_data.get('WeatherText'),
            "temperature_c": weather_data.get('Temperature', {}).get('Metric', {}).get('Value'),
            "temperature_f": weather_data.get('Temperature', {}).get('Imperial', {}).get('Value'),
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

# This allows us to run the server locally for testing
if __name__ == "__main__":
    # Use the FastMCP built-in runner for local testing
    print("Starting FastMCP server on http://127.0.0.1:8200...")
    # This runs it as an HTTP server by default if no transport is specified
    mcp.run(host="127.0.0.1", port=8200, transport="http")