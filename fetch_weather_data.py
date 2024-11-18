import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import pandas as pd
import base64
import json

# Ensure the environment variables are loaded
load_dotenv()

# Load API_KEY and DEVICE_ID from the .env file
API_KEY = os.getenv('WXM_API_KEY')
DEVICE_ID = os.getenv('DEVICE_ID')

def save_to_env(key, value):
    """
    Updates or adds a key-value pair in the .env file.
    Preserves existing values for other keys.
    """
    env_vars = {}

    # Read the existing .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    k, v = line.strip().split('=', 1)
                    env_vars[k] = v

    # Update or add the specific key with the new value
    env_vars[key] = f"'{value}'"

    # Write all variables back to the .env file
    with open('.env', 'w') as file:
        for k, v in env_vars.items():
            file.write(f"{k}={value}\n")

    print(f"{key} updated in .env.")

try:
    existing_data = pd.read_csv('previous_weather_data.csv')
    latest_timestamp = pd.to_datetime(existing_data['Timestamp'], utc=True).max()  # Specify utc=True
    start_date = latest_timestamp + timedelta(seconds=1)
except FileNotFoundError:
    start_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=num_hours)

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
            expiration_date = datetime.fromtimestamp(exp_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            return expiration_date
    except Exception as e:
        print(f"Error decoding token: {e}")
    return None

def fetch_new_api_key():
    """
    Fetches a new API key directly from the WeatherXM API and updates the .env file.
    """
    print("Attempting to fetch a new API key directly...")
    global API_KEY

    LOGIN_URL = "https://api.weatherxm.com/api/v1/auth/login"
    USERNAME = os.getenv('WXM_USERNAME')
    PASSWORD = os.getenv('WXM_PASSWORD')

    if not USERNAME or not PASSWORD:
        print("Error: Username or password is not set in the environment variables.")
        return None

    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        # Step 1: Authenticate and fetch API key
        response = requests.post(LOGIN_URL, json=payload, headers=headers)
        print("Response status code:", response.status_code)
        print("Response content:", response.text)
        response.raise_for_status()

        data = response.json()
        new_api_key = data.get('token')

        if not new_api_key:
            print("Failed to retrieve API key. API response did not contain a token.")
            return None

        print(f"New API Key: {new_api_key}")

        # Decode and print API key expiration time (optional)
        expiration_date = get_token_expiration(new_api_key)
        if expiration_date:
            print(f"API key will expire on: {expiration_date}")

        # Save the new API key to .env and update the global variable
        save_to_env('WXM_API_KEY', new_api_key)
        load_dotenv()  # Reload .env to refresh the global variables
        API_KEY = new_api_key  # Update global API_KEY
        print("Successfully fetched and saved a new API key.")
        return new_api_key

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the API key: {e}")
        return None

def fetch_weather_data(num_hours=None):
    """
    Fetches weather data from the API and updates the records.
    """
    if num_hours is None:
        num_hours = int(os.getenv('HOURS_OF_HISTORY', 24))

    try:
        existing_data = pd.read_csv('previous_weather_data.csv')
        latest_timestamp = pd.to_datetime(existing_data['Timestamp']).max()
        start_date = latest_timestamp + timedelta(seconds=1)
    except FileNotFoundError:
        start_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=num_hours)

    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
    all_weather_records = []
    max_api_hours = 24

    BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

    for request_num in range((num_hours + max_api_hours - 1) // max_api_hours):
        segment_end_date = end_date - timedelta(hours=request_num * max_api_hours)
        segment_start_date = segment_end_date - timedelta(hours=max_api_hours)

        if segment_start_date < start_date:
            segment_start_date = start_date

        if segment_end_date <= start_date:
            break

        params = {'fromDate': segment_start_date.isoformat(), 'toDate': segment_end_date.isoformat()}

        try:
            response = requests.get(
                BASE_URL,
                headers={'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'},
                params=params
            )
            response.raise_for_status()
            data = response.json()

            weather_records = []
            if isinstance(data, list):
                for day_data in data:
                    hourly_data_list = day_data.get('hourly', [])
                    for hourly_data in hourly_data_list:
                        timestamp = hourly_data.get('timestamp')
                        if timestamp:
                            weather_records.append([
                                timestamp,
                                hourly_data.get('temperature', 0),
                                hourly_data.get('humidity', 0),
                                hourly_data.get('wind_speed', 0),
                                hourly_data.get('precipitation', 0),
                                hourly_data.get('pressure', 0)
                            ])
            if weather_records:
                all_weather_records.extend(weather_records)
            else:
                print("No weather data found for this time range.")

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:  # Unauthorized
                print("Unauthorized. Attempting to fetch a new API key...")
                new_api_key = fetch_new_api_key()
                if new_api_key:
                    headers['Authorization'] = f'Bearer {new_api_key}'  # Update the Authorization header
                    response = requests.get(BASE_URL, headers=headers, params=params)
                    response.raise_for_status()
                continue  # Retry the same request with the new API key
            else:
                print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    if all_weather_records:
        save_previous_data(all_weather_records)
        return all_weather_records
    else:
        print("No weather records found.")
        return []

def save_previous_data(new_weather_records):
    """
    Updates the previous_weather_data.csv file with new records.
    """
    if not new_weather_records:
        print("No new records to save.")
        return

    try:
        existing_data = pd.read_csv('previous_weather_data.csv')
        latest_timestamp = pd.to_datetime(existing_data['Timestamp'], utc=True).max()
        start_date = latest_timestamp + timedelta(seconds=1)
    except FileNotFoundError:
        start_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=num_hours)

    new_data = pd.DataFrame(new_weather_records, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
    combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset="Timestamp", keep="last").sort_values(by="Timestamp")
    combined_data.to_csv('previous_weather_data.csv', index=False)
    print("Updated data saved to 'previous_weather_data.csv'.")

if __name__ == "__main__":
    fetch_weather_data()
