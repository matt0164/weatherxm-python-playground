import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
from settings import get_units
import pandas as pd

# Load .env file with your API key and device ID
load_dotenv()

# Get the WeatherXM API key and device ID from the environment variables
API_KEY = os.getenv('WXM_API_KEY').strip("'")
DEVICE_ID = os.getenv('DEVICE_ID').strip("'")

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

terminal_display_limit = 24  # Display max 24 hours in the terminal

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
    response.raise_for_status() # This will raise an HTTPError if the status code is not 200 (OK)
    # If the API key is missing or incorrect, the API will return a 401 Unauthorized error.
    # The raise_for_status() method will catch this error, and the program will jump to the except
    # requests.exceptions.HTTPError block at line 125, where the error is printed.

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
    # Check if the number of hours exceeds the terminal display limit
    if num_hours > terminal_display_limit:
        print("\nDisplaying the last 24 hours of data in the terminal:")
        limited_records = weather_records[-terminal_display_limit:]
        print(tabulate(limited_records, headers=headers, tablefmt="grid"))

        # Prompt for CSV or Excel download
        output_method = input(
            "The data exceeds 24 hours. Would you like to download the full data as CSV or Excel? (enter 'csv', 'excel', or 'no'): ").strip().lower()
        if output_method == 'csv':
            save_to_csv(weather_records)
        elif output_method == 'excel':
            save_to_excel(weather_records)
    else:
        print("\nWeather Data:")
        print(tabulate(weather_records, headers=headers, tablefmt="grid"))

except Exception as err:
    print(f"An error occurred: {err}")

def save_to_csv(data):
    df = pd.DataFrame(data, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
    df.to_csv('weather_data.csv', index=False)
    print("Data saved as 'weather_data.csv'.")

def save_to_excel(data):
    df = pd.DataFrame(data, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
    df.to_excel('weather_data.xlsx', index=False)
    print("Data saved as 'weather_data.xlsx'.")
