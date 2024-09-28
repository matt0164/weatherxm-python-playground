import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
from settings import get_units
import subprocess

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

# Get the number of hours of history
end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
num_hours = get_hours_history()
start_date = end_date - timedelta(hours=num_hours)
today_str = end_date.strftime('%Y-%m-%d')

# Debugging: Print the dates to ensure they're correct
print(f"Fetching weather data for {today_str}")

# Function to convert ISO 8601 timestamp to a more readable format
def format_timestamp(iso_timestamp):
    dt_obj = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S%z")
    return dt_obj.strftime("%B %d, %Y %I:%M %p")

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

# Get preferred units from settings.py
temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = get_units()

# Base URL for the WeatherXM API to fetch device history (measurements)
BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

# Set up headers for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

# Set up query parameters with only the date
params = {
    'fromDate': today_str,
    'toDate': today_str
}

# Make the API request to get weather data for the day
try:
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 401:  # Unauthorized
        print("Unauthorized access. Fetching new API key...")
        fetch_new_api_key()  # Fetch a new API key if unauthorized
        headers['Authorization'] = f'Bearer {API_KEY}'  # Update the headers with the new API key
        response = requests.get(BASE_URL, headers=headers, params=params)  # Retry the request
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # Extract hourly weather data from the response
    weather_records = []
    for day in data:
        for hourly_data in day['hourly']:
            # Filter only the records that are within the last few hours
            record_timestamp = datetime.strptime(hourly_data.get('timestamp'), "%Y-%m-%dT%H:%M:%S%z")
            if start_date <= record_timestamp <= end_date:
                wind_speed = convert_wind_speed(hourly_data.get('wind_speed') or 0, wind_speed_unit)
                record = [
                    format_timestamp(hourly_data.get('timestamp')),
                    convert_temperature(hourly_data.get('temperature') or 0, temperature_unit),
                    hourly_data.get('humidity') or 0,
                    wind_speed,
                    convert_precipitation(hourly_data.get('precipitation') or 0, precipitation_unit),
                    convert_pressure(hourly_data.get('pressure') or 0, pressure_unit)
                ]
                weather_records.append(record)

    # Define the table headers with preferred units
    headers = [
        "Timestamp",
        f"Temperature ({temperature_unit})",
        "Humidity (%)",
        f"Wind Speed ({wind_speed_unit})",
        f"Precipitation ({precipitation_unit})",
        f"Pressure ({pressure_unit})"
    ]

    # Display the table in a human-readable format
    print("\nWeather Data:")
    print(tabulate(weather_records, headers=headers, tablefmt="grid"))

    # Display the last wind speed recorded for reference
    if weather_records:
        last_wind_speed = weather_records[-1][3]  # Wind speed is the 4th item in the record
        print(f"Last Wind Speed: {last_wind_speed} {wind_speed_unit}")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
