import os
import requests
import base64
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# URLs
LOGIN_URL = "https://api.weatherxm.com/api/v1/auth/login"
DEVICES_URL = "https://api.weatherxm.com/api/v1/me/devices"
BASE_URL = "https://api.weatherxm.com/api/v1/me/devices/{}/history"

# Global Configuration
USERNAME = os.getenv('WXM_USERNAME')
PASSWORD = os.getenv('WXM_PASSWORD')
SAVE_LOCATION = os.getenv('FILE_SAVE_LOCATION', os.getcwd())

# Utility Functions
def get_token_expiration(token):
    """Extract and format the expiration date from the JWT token."""
    try:
        payload_encoded = token.split('.')[1]
        padding = len(payload_encoded) % 4
        if padding > 0:
            payload_encoded += '=' * (4 - padding)
        payload_decoded = base64.urlsafe_b64decode(payload_encoded).decode('utf-8')
        payload = json.loads(payload_decoded)
        exp_timestamp = payload.get('exp')
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp).strftime('%m/%d/%Y %I:%M:%S %p')
    except Exception as e:
        print(f"Error decoding token: {e}")
    return None


def update_env_file(new_api_key, device_id, station_id):
    """Update the .env file with new API key and device information."""
    env_vars = {}

    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            for line in file.readlines():
                if "=" in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

    env_vars['WXM_API_KEY'] = f'"{new_api_key}"'
    env_vars['DEVICE_ID'] = f'"{device_id}"'
    env_vars['STATION_ID'] = f'"{station_id}"'

    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

    print(".env file updated with new API key, device ID, and station ID.")


def login_and_get_api_key():
    """Logs in to fetch a new API key."""
    if not USERNAME or not PASSWORD:
        raise EnvironmentError("Missing WeatherXM username or password. Check your .env file.")
    payload = {"username": USERNAME, "password": PASSWORD}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    try:
        response = requests.post(LOGIN_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        api_key = data.get('token')
        expiration_date = get_token_expiration(api_key)
        if expiration_date:
            print(f"API key will expire on: {expiration_date}")
        return api_key
    except requests.exceptions.RequestException as e:
        print(f"Error during login: {e}")
        return None


def fetch_device_id(api_key):
    """Fetch device information and prompt the user to select a device."""
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(DEVICES_URL, headers=headers)
        response.raise_for_status()
        devices = response.json()
        if not devices:
            print("No devices found.")
            return None, None
        print("Available devices:")
        for i, device in enumerate(devices):
            print(f"{i + 1}: {device['name']} (ID: {device['id']})")
        selected_index = int(input("Select the device by number: ")) - 1
        device = devices[selected_index]
        return device['id'], device['name']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device information: {e}")
        return None, None


def fetch_data_segment(api_key, device_id, from_date, to_date):
    """Fetch data for a specific time segment."""
    params = {'fromDate': from_date.isoformat(), 'toDate': to_date.isoformat()}
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(BASE_URL.format(device_id), headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("records", [])
        else:
            print("Unexpected API response format.")
            return []
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Unauthorized. Attempting to refresh API key...")
            new_api_key = login_and_get_api_key()
            if new_api_key:
                return fetch_data_segment(new_api_key, device_id, from_date, to_date)
        print(f"HTTP error occurred: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error during data fetch: {e}")
        return []


def initialize_api():
    """Initialize API key and device ID."""
    api_key = os.getenv('WXM_API_KEY') or login_and_get_api_key()
    if not api_key:
        raise RuntimeError("Failed to retrieve API key.")

    device_id = os.getenv('DEVICE_ID')
    station_id = os.getenv('STATION_ID')

    if not device_id:
        device_id, station_id = fetch_device_id(api_key)
        if not device_id:
            raise RuntimeError("Failed to retrieve device ID.")

    update_env_file(api_key, device_id, station_id)
    return api_key, device_id
