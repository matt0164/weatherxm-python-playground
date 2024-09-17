import requests
import os
from dotenv import load_dotenv

# Load .env file with your API key and wallet address
load_dotenv()

# Get the API key and wallet address from the environment variables
API_KEY = os.getenv('WEATHERXM_API_KEY')
WALLET_ADDRESS = os.getenv('WALLET_ADDRESS')

# Base URL for retrieving station information
BASE_URL = "https://api.weatherxm.com/v1/stations"

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

# Add the wallet address as a parameter to get stations linked to it
params = {
    'wallet': WALLET_ADDRESS
}

# Make the API request to get station information
try:
    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()

    # Print the station data to find the station ID
    stations = response.json()
    print("Stations found:", stations)

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
