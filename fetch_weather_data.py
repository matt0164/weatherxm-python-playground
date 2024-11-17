import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
import subprocess
import pandas as pd
import webbrowser  # Import the webbrowser module
from data_visualization_v2 import plot_precipitation

# Ensure SAVE_LOCATION is loaded correctly and set a default if not found
def get_save_location():
    return os.getenv('FILE_SAVE_LOCATION', os.getcwd())  # Default to current directory if not set

SAVE_LOCATION = get_save_location()  # Set the file save location

def save_to_csv(data):
    df = pd.DataFrame(data, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
    file_path = os.path.join(SAVE_LOCATION, 'weather_data.csv')  # Save in the specified directory
    df.to_csv(file_path, index=False)
    print(f"Data saved as 'weather_data.csv' at {file_path}.")

# Function to save data as Excel
def save_to_excel(data):
    df = pd.DataFrame(data, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
    file_path = os.path.join(SAVE_LOCATION, 'weather_data.xlsx')  # Save in the specified directory
    df.to_excel(file_path, index=False)
    print(f"Data saved as 'weather_data.xlsx' at {file_path}.")

# Load .env file with your API key and device ID
load_dotenv()

# Get the WeatherXM API key and device ID from the environment variables
API_KEY = os.getenv('WXM_API_KEY').strip("'")
DEVICE_ID = os.getenv('DEVICE_ID').strip("'")

# Function to fetch new API key
def fetch_new_api_key():
    print("Attempting to fetch a new API key...")
    try:
        subprocess.run(["python", "fetch_api_key.py"], check=True)
        load_dotenv()  # Reload the updated .env file after fetching the key
        global API_KEY
        API_KEY = os.getenv('WXM_API_KEY').strip("'")
        print(f"New API key set: {API_KEY}")
    except subprocess.CalledProcessError as e:
        print(f"Error fetching new API key: {e}")

# Function to get hours of history from .env file (defaults to 1 hour)
def get_hours_history():
    hours = os.getenv('HOURS_OF_HISTORY', '1')  # gets hours of history from .env
    print(f"Hours of history from .env: {hours}")  # prints hours of history to confirm correct
    try:
        return int(hours)
    except ValueError:
        print(f"Invalid value for HOURS_OF_HISTORY in .env: {hours}. Defaulting to 1 hour.")
        return 1

# Function to load previous data
def load_previous_data():
    try:
        df = pd.read_csv('previous_weather_data.csv')
        print("Loaded previous weather data.")
        return df
    except FileNotFoundError:
        print("No previous data found. Please fetch data first.")
        return None

# Function to save previous data
def save_previous_data(weather_records):
    if weather_records:  # Only save if there are records
        df = pd.DataFrame(weather_records,
                          columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
        df.to_csv('previous_weather_data.csv', index=False)
        print("Previous data saved to 'previous_weather_data.csv'.")
    else:
        print("No records to save.")

# Function to fetch weather data
def fetch_weather_data(num_hours=None):
    if num_hours is None:
        num_hours = get_hours_history()

    all_weather_records = []
    max_api_hours = 24  # API limitation
    num_requests = (num_hours + max_api_hours - 1) // max_api_hours  # Ceiling division

    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Define BASE_URL for the API
    BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

    for request_num in range(num_requests):
        segment_end_date = end_date - timedelta(hours=request_num * max_api_hours)
        segment_start_date = segment_end_date - timedelta(hours=max_api_hours)
        if segment_start_date < end_date - timedelta(hours=num_hours):
            segment_start_date = end_date - timedelta(hours=num_hours)

        params = {
            'fromDate': segment_start_date.isoformat(),
            'toDate': segment_end_date.isoformat()
        }

        print(f"Fetching data from {params['fromDate']} to {params['toDate']}")

        try:
            response = requests.get(BASE_URL, headers={
                'Authorization': f'Bearer {API_KEY}',
                'Accept': 'application/json'
            }, params=params)
            print(f"Raw Response: {response.text}")  # Log raw response
            response.raise_for_status()

            data = response.json()
            print(f"Parsed Data: {data}")  # Log parsed data

            weather_records = []

            # Handle the response as a list of dictionaries
            if isinstance(data, list):
                for day_data in data:
                    hourly_data_list = day_data.get('hourly', [])
                    for hourly_data in hourly_data_list:
                        timestamp = hourly_data.get('timestamp')
                        if timestamp:
                            # Convert precipitation from mm to inches if necessary
                            precipitation_mm = hourly_data.get('precipitation', 0)
                            precipitation_in = precipitation_mm / 25.4  # Convert mm to inches

                            record = [
                                timestamp,
                                hourly_data.get('temperature', 0),
                                hourly_data.get('humidity', 0),
                                hourly_data.get('wind_speed', 0),
                                precipitation_in,  # Use converted precipitation
                                hourly_data.get('pressure', 0)
                            ]

                            weather_records.append(record)
            else:
                print("Unexpected response format. Please verify the API response structure.")

                timestamp = hourly_data.get('timestamp')
                if timestamp:
                    record = [
                        timestamp,
                        hourly_data.get('temperature', 0),
                        hourly_data.get('humidity', 0),
                        hourly_data.get('wind_speed', 0),
                        hourly_data.get('precipitation', 0),
                        hourly_data.get('pressure', 0)
                    ]
                    weather_records.append(record)

            if weather_records:
                all_weather_records.extend(weather_records)
            else:
                print("No weather data found for this time range.")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    if all_weather_records:
        save_previous_data(all_weather_records)
        print("Weather data fetched and saved successfully.")
    else:
        print("No weather records found for the specified period.")

# Start the first fetch
fetch_weather_data()
