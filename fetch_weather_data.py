import requests
import os
from dotenv import load_dotenv

# Load .env file with your API key and station ID
load_dotenv()

# Get the WeatherXM API key and Station ID from environment variables
API_KEY = os.getenv('WEATHERXM_API_KEY')
STATION_ID = os.getenv('STATION_ID')

# Base URL for the WeatherXM API
BASE_URL = f"https://api.weatherxm.com/v1/stations/{STATION_ID}/measurements"

# Set up headers for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

# Make the API request
try:
    response = requests.get(BASE_URL, headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the JSON response
    data = response.json()

    # Extract and print the temperature
    temperature = data.get('measurements', {}).get('temperature')
    print(f"Current temperature: {temperature}°C")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
