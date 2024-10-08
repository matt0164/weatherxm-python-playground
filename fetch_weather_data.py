import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
from settings import get_units
import subprocess
from rerun_weather_prompt import prompt_rerun
import sys
import pandas as pd  # Ensure pandas is imported

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
    hours = os.getenv('HOURS_OF_HISTORY', '1')
    try:
        return int(hours)
    except ValueError:
        print(f"Invalid value for HOURS_OF_HISTORY in .env: {hours}. Defaulting to 1 hour.")
        return 1

# Conversion functions
def convert_temperature(temp_c, unit):
    if unit == 'F':
        return round((temp_c * 9/5) + 32, 1)
    return round(temp_c, 1)

def convert_wind_speed(speed_ms, unit):
    if unit == 'mph':
        return round(speed_ms * 2.23694, 2)
    return round(speed_ms, 2)

terminal_display_limit = 24  # Display max 24 hours in the terminal

def convert_precipitation(precip_mm, unit):
    if unit == 'in':
        return round(precip_mm / 25.4, 2)
    return round(precip_mm, 2)

def convert_pressure(pressure_hpa, unit):
    if unit == 'mb':
        return round(pressure_hpa, 2)
    return round(pressure_hpa, 2)

# Function to convert ISO 8601 timestamp to a more readable format
def format_timestamp(iso_timestamp):
    dt_obj = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S%z")
    return dt_obj.strftime("%B %d, %Y %I:%M %p")

# Function to fetch weather data
def fetch_weather_data(num_hours=None):
    if num_hours is None:
        num_hours = get_hours_history()  # Default to the existing method to get hours

    all_weather_records = []  # Initialize at the start of the function

    # Calculate number of requests needed based on terminal display limit
    num_requests = (num_hours + terminal_display_limit - 1) // terminal_display_limit  # Ceiling division

    for request_num in range(num_requests):
        current_hours = min(terminal_display_limit, num_hours - (request_num * terminal_display_limit))
        end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        start_date = end_date - timedelta(hours=current_hours)
        today_str = end_date.strftime('%Y-%m-%d')

        # Get preferred units from settings.py
        temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = get_units()

        # Base URL for the WeatherXM API to fetch device history (measurements)
        BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

        # Set up headers for the API request
        api_headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Accept': 'application/json'
        }

        # Define the table headers with preferred units
        headers = [
            "Timestamp",
            f"Temperature ({temperature_unit})",
            "Humidity (%)",
            f"Wind Speed ({wind_speed_unit})",
            f"Precipitation ({precipitation_unit})",
            f"Pressure ({pressure_unit})"
        ]

        # Set up query parameters with only the date
        params = {
            'fromDate': today_str,
            'toDate': today_str
        }

        # Make the API request to get weather data for the day
        try:
            response = requests.get(BASE_URL, headers=api_headers, params=params)
            response.raise_for_status()  # This will raise an HTTPError if the status code is not 200 (OK)

            # Parse the JSON response
            data = response.json()

            # Extract hourly weather data from the response
            weather_records = []
            for day in data:
                hourly_data_list = day.get('hourly', [])
                if isinstance(hourly_data_list, list):
                    for hourly_data in hourly_data_list:
                        timestamp = hourly_data.get('timestamp')
                        if timestamp:
                            record_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
                            if start_date <= record_timestamp <= end_date:
                                wind_speed = convert_wind_speed(hourly_data.get('wind_speed', 0), wind_speed_unit)
                                record = [
                                    format_timestamp(timestamp),
                                    convert_temperature(hourly_data.get('temperature', 0), temperature_unit),
                                    hourly_data.get('humidity', 0),
                                    wind_speed,
                                    convert_precipitation(hourly_data.get('precipitation', 0), precipitation_unit),
                                    convert_pressure(hourly_data.get('pressure', 0), pressure_unit)
                                ]
                                weather_records.append(record)

            all_weather_records.extend(weather_records)  # Combine results from each request

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            return

    # Check if the number of hours exceeds the terminal display limit
    if num_hours > terminal_display_limit:
        print("\nDisplaying the last 24 hours of data in the terminal:")
        limited_records = all_weather_records[-terminal_display_limit:]
        print(tabulate(limited_records, headers=headers, tablefmt="grid"))

        # Prompt for CSV or Excel download
        output_method = input(
            "The data exceeds 24 hours. Would you like to download the full data as CSV or Excel? (enter 'csv', 'excel', or 'no'): "
        ).strip().lower()

        if output_method == 'csv':
            save_to_csv(all_weather_records)
        elif output_method == 'excel':
            save_to_excel(all_weather_records)
    else:
        print("\nWeather Data:")
        print(tabulate(all_weather_records, headers=headers, tablefmt="grid"))

    # After displaying the weather data
    # Ask if the user wants to rerun the weather script
    prompt_rerun(fetch_weather_data)

# Start the first fetch
fetch_weather_data()
