import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import subprocess
import pandas as pd
from data_visualization_v2 import plot_precipitation
from data_fetching import fetch_latest_weather_data  # Import from new module
import sys

# Ensure SAVE_LOCATION is loaded correctly and set a default if not found
def get_save_location():
    return os.getenv('FILE_SAVE_LOCATION', os.getcwd())  # Default to current directory if not set

SAVE_LOCATION = get_save_location()  # Set the file save location

def save_to_csv(data):
    """Save data to a CSV file."""
    try:
        df = pd.DataFrame(data, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
        file_path = os.path.join(SAVE_LOCATION, 'weather_data.csv')  # Save in the specified directory
        df.to_csv(file_path, index=False)
        print(f"Data saved as 'weather_data.csv' at {file_path}.")
    except Exception as e:
        print(f"Error saving CSV: {e}")

def save_to_excel(data):
    """Save data to an Excel file."""
    try:
        df = pd.DataFrame(data, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
        file_path = os.path.join(SAVE_LOCATION, 'weather_data.xlsx')  # Save in the specified directory
        df.to_excel(file_path, index=False)
        print(f"Data saved as 'weather_data.xlsx' at {file_path}.")
    except Exception as e:
        print(f"Error saving Excel: {e}")

# Load environment variables
load_dotenv()

# Get the WeatherXM API key and device ID from the environment variables
API_KEY = os.getenv('WXM_API_KEY', '').strip("'")
DEVICE_ID = os.getenv('DEVICE_ID', '').strip("'")

if not API_KEY or not DEVICE_ID:
    raise ValueError("API_KEY or DEVICE_ID is missing in the environment variables.")

# Function to fetch new API key
def fetch_new_api_key():
    print("Attempting to fetch a new API key...")
    try:
        subprocess.run([sys.executable, "fetch_api_key.py"], check=True)
        load_dotenv()  # Reload the updated .env file after fetching the key
        global API_KEY
        API_KEY = os.getenv('WXM_API_KEY', '').strip("'")
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

# Save previous weather data
def save_previous_data(weather_records):
    if weather_records:
        try:
            df = pd.DataFrame(weather_records,
                              columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
            df.to_csv('previous_weather_data.csv', index=False)
            print("Previous data saved to 'previous_weather_data.csv'.")
        except Exception as e:
            print(f"Error saving previous data: {e}")
    else:
        print("No records to save.")

if __name__ == "__main__":
    # Fetch weather data and save
    weather_data = fetch_latest_weather_data()
    save_to_csv(weather_data)
    save_to_excel(weather_data)
    plot_precipitation(weather_data, get_hours_history())
