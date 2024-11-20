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

    # Update the API key
    env_vars["WXM_API_KEY"] = f'"{api_key}"'

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
    Fetch a new API key directly from the WeatherXM API.
    """
    try:
        response = requests.post(
            "https://api.weatherxm.com/api/v1/auth/login",
            json={"username": os.getenv("WXM_USERNAME"), "password": os.getenv("WXM_PASSWORD")},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        response.raise_for_status()

        # Parse the response and extract the API key
        data = response.json()
        new_api_key = data.get("token")

        if new_api_key:
            print(f"New API Key: {new_api_key}")

            # Update only the API key in the .env file
            update_env_file(new_api_key)
            load_dotenv()  # Reload .env variables to ensure the new key is used
        else:
            print("Failed to fetch a new API key. No token found in the response.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching a new API key: {http_err}")
    except Exception as e:
        print(f"An error occurred while fetching a new API key: {e}")

def fetch_weather_data():
    """
    Fetch weather data using the WeatherXM API and save to a local file.
    """
    import requests
    from datetime import datetime, timedelta
    import pandas as pd
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()

    API_KEY = os.getenv("WXM_API_KEY")
    DEVICE_ID = os.getenv("DEVICE_ID")
    if not API_KEY or not DEVICE_ID:
        raise ValueError("API key or Device ID is missing. Check your .env file.")

    BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    # Determine the time range for the API call
    try:
        existing_data = pd.read_csv("previous_weather_data.csv")
        latest_timestamp = pd.to_datetime(existing_data["Timestamp"]).max()
        start_time = latest_timestamp + pd.Timedelta(seconds=1)
    except FileNotFoundError:
        start_time = datetime.utcnow() - timedelta(days=7)

    end_time = datetime.utcnow()

    params = {
        "fromDate": start_time.isoformat(),
        "toDate": end_time.isoformat(),
    }

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            print("No new weather data available.")
            return

        # Process and save the data
        save_previous_data(data)
        print("Weather data fetched and saved successfully.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 401:  # Unauthorized
            print("Unauthorized. Attempting to fetch a new API key...")
            try:
                new_api_key = fetch_new_api_key()  # Function to fetch a new API key
                headers["Authorization"] = f"Bearer {new_api_key}"  # Update headers with new API key
                # Retry the request
                response = requests.get(BASE_URL, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if data:
                    save_previous_data(data)
                    print("Weather data fetched and saved successfully.")
                else:
                    print("No new weather data available.")

            except Exception as e:
                print(f"An error occurred while fetching the API key: {e}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

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
