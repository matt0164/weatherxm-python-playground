import requests
import os
from dotenv import load_dotenv

# Load .env file with your API key
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('WXM_API_KEY')

# Ensure the API key exists
if not API_KEY:
    raise EnvironmentError("API Key not found. Please check your .env file.")

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

    # Parse and print the device data
    devices = response.json()
    if devices:
        for device in devices:
            print(f"Device Name: {device['name']}")
            print(f"Device ID: {device['id']}")
            print(f"Location: {device['location']}")
            print(f"Timezone: {device['timezone']}\n")
    else:
        print("No devices found.")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
