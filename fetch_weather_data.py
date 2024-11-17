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
def save_previous_data(new_weather_records):
    # Ensure new records are provided
    if not new_weather_records:
        print("No new records to save.")
        return

    try:
        # Load existing data from CSV
        existing_data = pd.read_csv('previous_weather_data.csv')
        print("Loaded existing data from 'previous_weather_data.csv'.")
    except FileNotFoundError:
        # If the file doesn't exist, create it with the new records
        existing_data = pd.DataFrame(columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
        print("'previous_weather_data.csv' does not exist. Creating a new file.")

    # Convert new data to DataFrame
    new_data = pd.DataFrame(new_weather_records, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])

    # Concatenate new data with existing data
    combined_data = pd.concat([existing_data, new_data])

    # Drop duplicate records based on the "Timestamp" column
    combined_data = combined_data.drop_duplicates(subset="Timestamp", keep="last")

    # Sort the data by timestamp for better readability
    combined_data["Timestamp"] = pd.to_datetime(combined_data["Timestamp"])
    combined_data = combined_data.sort_values(by="Timestamp")

    # Save the updated data back to the CSV
    combined_data.to_csv('previous_weather_data.csv', index=False)
    print("Updated data saved to 'previous_weather_data.csv'.")

# Function to fetch weather data
from data_visualization_v2 import plot_precipitation


def fetch_weather_data(num_hours=None):
    """
    Fetches weather data from the API and appends new records to `previous_weather_data.csv`.
    Updates the precipitation chart after fetching data.
    """
    if num_hours is None:
        num_hours = get_hours_history()

    try:
        # Load the previous data to determine the latest timestamp
        existing_data = pd.read_csv('previous_weather_data.csv')
        latest_timestamp = pd.to_datetime(existing_data['Timestamp']).max()
        start_date = latest_timestamp + timedelta(seconds=1)  # Start right after the latest timestamp
        print(f"Starting data fetch from {start_date} based on existing data.")
    except FileNotFoundError:
        print("No previous data found. Starting from the default end date.")
        start_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=num_hours)

    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
    all_weather_records = []  # Initialize list to hold fetched data
    max_api_hours = 24  # API limitation

    # Calculate the number of requests needed
    total_hours = (end_date - start_date).total_seconds() / 3600
    num_requests = int((total_hours + max_api_hours - 1) // max_api_hours)  # Ceiling division

    BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

    for request_num in range(num_requests):
        segment_end_date = end_date - timedelta(hours=request_num * max_api_hours)
        segment_start_date = segment_end_date - timedelta(hours=max_api_hours)

        # Ensure the start date does not go beyond the determined start_date
        if segment_start_date < start_date:
            segment_start_date = start_date

        # Stop fetching if we've gone past the start date
        if segment_end_date <= start_date:
            break

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
            response.raise_for_status()

            data = response.json()
            weather_records = []

            if isinstance(data, list):
                for day_data in data:
                    hourly_data_list = day_data.get('hourly', [])
                    for hourly_data in hourly_data_list:
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
            else:
                print("Unexpected response format. Please verify the API response structure.")
                return []

            if weather_records:
                all_weather_records.extend(weather_records)
            else:
                print("No weather data found for this time range.")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            if response.status_code == 401:
                print("Unauthorized. Attempting to refresh the API key...")
                fetch_new_api_key()
                continue  # Retry the current segment
        except Exception as err:
            print(f"An error occurred: {err}")

    if all_weather_records:
        save_previous_data(all_weather_records)
        print("Weather data fetched and saved successfully.")

        # Generate and update the precipitation chart
        try:
            print("Updating precipitation chart...")
            updated_data = pd.read_csv('previous_weather_data.csv')
            plot_precipitation(updated_data)
            print("Precipitation chart updated successfully.")
        except Exception as chart_err:
            print(f"An error occurred while updating the precipitation chart: {chart_err}")

        return all_weather_records
    else:
        print("No weather records found for the specified period.")
        return []

# Start the first fetch
fetch_weather_data()
