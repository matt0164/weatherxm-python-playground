import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import base64
import json

# Load .env file (if username and password are stored there)
load_dotenv()

# Set your email and password for the WeatherXM account
USERNAME = os.getenv('WXM_USERNAME')  # or hardcode it like: "your_email_here"
PASSWORD = os.getenv('WXM_PASSWORD')  # or hardcode it like: "your_password_here"

# Check if username and password are provided
if not USERNAME or not PASSWORD:
    raise EnvironmentError("Missing WeatherXM username or password. Please check your .env file.")

# URL to log in and get the API key
LOGIN_URL = "https://api.weatherxm.com/api/v1/auth/login"

# URL to fetch device information (after getting API key)
DEVICES_URL = "https://api.weatherxm.com/api/v1/me/devices"

# Payload with your credentials
payload = {
    "username": USERNAME,
    "password": PASSWORD
}

# Headers for the request
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


# Function to extract and format the expiration date from the JWT token
def get_token_expiration(token):
    try:
        payload_encoded = token.split('.')[1]
        padding = len(payload_encoded) % 4
        if padding > 0:
            payload_encoded += '=' * (4 - padding)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded).decode('utf-8')
        payload = json.loads(payload_decoded)

        exp_timestamp = payload.get('exp')
        if exp_timestamp:
            expiration_date = datetime.fromtimestamp(exp_timestamp).strftime('%m/%d/%Y %I:%M:%S %p')
            return expiration_date
    except Exception as e:
        print(f"Error decoding token: {e}")
    return None


# Function to update the .env file while preserving other variables and applying appropriate quotes
def update_env_file(new_api_key, device_id, station_id):
    env_vars = {}

    # Read existing environment variables from .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

    # Update or add the specific keys with appropriate quotes
    env_vars['WXM_API_KEY'] = f'"{new_api_key}"'
    env_vars['DEVICE_ID'] = f'"{device_id}"'
    env_vars['STATION_ID'] = f'"{station_id}"'  # Use double quotes for station ID with spaces

    # Write all variables back to the .env file
    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

    print(".env file updated with new API key, device ID, and station ID")


# Step 1: Get the API key
try:
    response = requests.post(LOGIN_URL, json=payload, headers=headers)
    response.raise_for_status()

    # Extract the API key from the response
    data = response.json()
    api_key = data.get('token')

    print(f"New API Key: {api_key}")

    # Print the expiration time of the new API key
    expiration_date = get_token_expiration(api_key)
    if expiration_date:
        print(f"API key will expire on: {expiration_date}")

    # Step 2: Fetch the device information using the API key
    headers['Authorization'] = f'Bearer {api_key}'
    response = requests.get(DEVICES_URL, headers=headers)
    response.raise_for_status()

    devices = response.json()
    if devices:
        # Prompt user to select a device if there are multiple
        print("Available devices:")
        for index, device in enumerate(devices):
            print(f"{index + 1}: {device['name']} (ID: {device['id']})")

        selected_index = int(input("Select the device by number: ")) - 1
        device_id = devices[selected_index]['id']
        station_id = devices[selected_index]['name']
        print(f"Device ID: {device_id} (Device Name: {station_id})")

        # Step 3: Update .env file with API key, device ID, and station ID
        update_env_file(api_key, device_id, station_id)

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
