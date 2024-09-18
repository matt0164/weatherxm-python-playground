import requests
import os
from dotenv import load_dotenv

# Load .env file with your API key
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('WEATHERXM_API_KEY')

# Debugging: Print the API key to verify it is loaded
print(f"API Key: {API_KEY}")

# New URL for retrieving devices
BASE_URL = "https://api.weatherxm.com/api/v1/me/devices"

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

# Make the API request to get device information
try:
    response = requests.get(BASE_URL, headers=headers)
    response.raise_for_status()

    # Print the device data to find the station ID
    devices = response.json()
    print("Devices found:", devices)

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
