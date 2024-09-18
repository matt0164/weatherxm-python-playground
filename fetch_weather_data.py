import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from tabulate import tabulate
from settings import get_units  # Import the unit settings

# Load .env file with your API key and device ID
load_dotenv()

# Get the WeatherXM API key and device ID from the environment variables
API_KEY = os.getenv('WEATHERXM_API_KEY').strip("'")  # Strip the quotes if any
DEVICE_ID = os.getenv('DEVICE_ID').strip("'")

# Function to prompt user for date range or number of days of history
def get_date_range():
    use_default = input("Would you like to use the default 1-day history? (yes/no): ").strip().lower()
    if use_default == 'no':
        while True:
            try:
                num_days = int(input("How many days of history would you like to see? (e.g., 2 for 2 days): ").strip())
                break
            except ValueError:
                print("Invalid input. Please enter a valid number of days.")
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=num_days)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        # Default to 1 day history
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

    return start_date_str, end_date_str

# Function to convert ISO 8601 timestamp to a more readable format
def format_timestamp(iso_timestamp):
    dt_obj = datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S%z")
    return dt_obj.strftime("%B %d, %Y %I:%M %p")

# Conversion functions
def convert_temperature(temp_c, unit):
    if unit == 'F':
        return round((temp_c * 9/5) + 32, 1)
    return round(temp_c, 1)  # Default to Celsius

def convert_wind_speed(speed_ms, unit):
    if unit == 'mph':
        return round(speed_ms * 2.23694, 2)
    return round(speed_ms, 2)  # Default to m/s

def convert_precipitation(precip_mm, unit):
    if unit == 'in':
        return round(precip_mm / 25.4, 2)
    return round(precip_mm, 2)  # Default to mm

def convert_pressure(pressure_hpa, unit):
    if unit == 'mb':
        return round(pressure_hpa, 2)  # hPa and mb are equivalent
    return round(pressure_hpa, 2)

# Get preferred units from settings.py
temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = get_units()

# Get the date range from the user
start_date_str, end_date_str = get_date_range()

# Base URL for the WeatherXM API to fetch device history (measurements)
BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

# Set up headers for the API request
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

# Set up query parameters (e.g., fromDate, toDate)
params = {
    'fromDate': start_date_str,
    'toDate': end_date_str
}

# Make the API request to get weather data
try:
    response = requests.get(BASE_URL, headers=headers, params=params)
    response.raise_for_status()  # Raise an error for bad status codes

    # Parse the JSON response
    data = response.json()

    # Extract hourly weather data from the response
    weather_records = []
    for day in data:
        for hourly_data in day['hourly']:
            record = [
                format_timestamp(hourly_data.get('timestamp')),
                convert_temperature(hourly_data.get('temperature'), temperature_unit),
                hourly_data.get('humidity'),
                convert_wind_speed(hourly_data.get('wind_speed'), wind_speed_unit),
                convert_precipitation(hourly_data.get('precipitation'), precipitation_unit),
                convert_pressure(hourly_data.get('pressure'), pressure_unit)
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

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")
