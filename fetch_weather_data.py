import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
from settings import get_units
import subprocess
from rerun_weather_prompt import prompt_rerun
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
    hours = os.getenv('HOURS_OF_HISTORY', '1') #gets hours of history from .env
    print(f"hours of history from .env: {hours}") #prints hours of history to confirm correct
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
        print(f"Number of hours: {num_hours}") #prints number of hours as a 2nd check. should match hours from .env

    all_weather_records = []  # Initialize at the start of the function

    # Calculate the total number of hours to fetch
    total_hours = num_hours or get_hours_history()  # Defaults to the number of hours specified or 1 if not set

    # Calculate number of requests needed based on API limits
    max_api_hours = 24  # API limitation
    num_requests = (total_hours + max_api_hours - 1) // max_api_hours  # Ceiling division.
    #The script calculates how many API requests are needed based on the total hours requested = num_requests
    print(f"num_requests {num_requests}")

    # Start the end date as the current UTC time
    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Loop through each 24-hour segment request
    for request_num in range(num_requests):
        # Calculate the start and end dates for the current request
        segment_end_date = end_date - timedelta(hours=request_num * max_api_hours)
        segment_start_date = segment_end_date - timedelta(hours=max_api_hours)

        # Ensure the start date does not go beyond the total requested hours
        if segment_start_date < end_date - timedelta(hours=total_hours):
            segment_start_date = end_date - timedelta(hours=total_hours)

        # Set the params for the API request
        params = {
            'fromDate': segment_start_date.isoformat(),
            'toDate': segment_end_date.isoformat()
        }

        print(f"Fetching data from {params['fromDate']} to {params['toDate']}")

        # Fetch data as before (API request, response handling, etc.)

        # Get preferred units from settings.py
        temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = get_units()

        # Base URL for the WeatherXM API to fetch device history (measurements)
        BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

        # Set up headers for the API request
        api_headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Accept': 'application/json'
        }

        while True:  # Start of the retry loop
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
                                # Use segment_start_date and segment_end_date for validation
                                if segment_start_date <= record_timestamp <= segment_end_date:
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
                break  # Exit the loop if the request was successful

            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 401:  # If it's a 401 error
                    print("Unauthorized access. Fetching new API key...")
                    fetch_new_api_key()  # Fetch a new API key if unauthorized
                    api_headers['Authorization'] = f'Bearer {API_KEY}'  # Update the headers with the new API key
                    continue  # Retry the request with the new API key
                else:
                    print(f"HTTP error occurred: {http_err}")
                    break  # Exit the loop for other HTTP errors
            except Exception as err:
                print(f"An error occurred: {err}")
                break  # Exit the loop for other exceptions

    # Sort all_weather_records by the first column (timestamp) in descending order
    all_weather_records.sort(key=lambda x: datetime.strptime(x[0], "%B %d, %Y %I:%M %p"), reverse=True)

    # Display sorted data
    print("\nWeather Data:")
    print(tabulate(all_weather_records, headers=[
        "Timestamp",
        f"Temperature ({temperature_unit})",
        "Humidity (%)",
        f"Wind Speed ({wind_speed_unit})",
        f"Precipitation ({precipitation_unit})",
        f"Pressure ({pressure_unit})"
    ], tablefmt="grid"))

    # Prompt for CSV or Excel download
    output_method = input(
        "Would you like to download the full data as CSV or Excel? (enter 'csv', 'excel', or 'no'): "
    ).strip().lower()

    if output_method == 'csv':
        save_to_csv(all_weather_records)
    elif output_method == 'excel':
        save_to_excel(all_weather_records)

    # After displaying the weather data
    # Ask if the user wants to rerun the weather script
    prompt_rerun(fetch_weather_data)

# Start the first fetch
fetch_weather_data()