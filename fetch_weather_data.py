import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from tabulate import tabulate
from settings import get_units
import subprocess
from rerun_weather_prompt import prompt_rerun
import pandas as pd
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

# Function to load previous data from CSV
def load_previous_data():
    try:
        df = pd.read_csv('previous_weather_data.csv')
        print("Loaded previous weather data.")
        return df
    except FileNotFoundError:
        print("No previous data found. Please fetch data first.")
        return None

# Function to save previous data to CSV
def save_previous_data(weather_records):
    if weather_records:
        df = pd.DataFrame(weather_records, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
        df.to_csv('previous_weather_data.csv', index=False)
        print("Previous data saved to 'previous_weather_data.csv'.")
    else:
        print("No records to save.")

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

# Main function to fetch weather data
# Function to fetch weather data
def fetch_weather_data(num_hours=None):
    load_choice = input("Do you want to (1) fetch new data or (2) load previous data for visualization? (enter '1' or '2'): ")

    if load_choice == '1':
        if num_hours is None:
            num_hours = get_hours_history()  # Default to the existing method to get hours
        all_weather_records = []

        max_api_hours = 24
        num_requests = (num_hours + max_api_hours - 1) // max_api_hours

        print(f"num_requests: {num_requests}")

        end_date = datetime.utcnow().replace(tzinfo=timezone.utc)

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
                response = requests.get(
                    f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history",
                    headers={'Authorization': f'Bearer {API_KEY}'},
                    params=params
                )
                response.raise_for_status()  # Raises HTTPError for bad responses

                # Debug: print response content to see if data is returned
                print("Response JSON:", response.json())  # Show raw response

                data = response.json()
                if data:  # Check if data is returned
                    weather_records = []  # Temporary storage for current request

                    for day in data:
                        hourly_data_list = day.get('hourly', [])
                        if isinstance(hourly_data_list, list):
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

                    all_weather_records.extend(weather_records)  # Add to main list

                else:
                    print("No data returned for this range.")

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
            except Exception as err:
                print(f"An error occurred: {err}")

        save_previous_data(all_weather_records)  # Save all fetched records

    elif load_choice == '2':
        df = load_previous_data()
        if df is not None:
            all_weather_records = df.values.tolist()
        else:
            print("No data to visualize. Exiting.")
            return

    # Check if we have any records to process
    if all_weather_records:
        # Prompt user for how they would like to view or save the weather data
        print("\nHow would you like to handle the weather data?")
        print("1. Display as a table")
        print("2. Download as CSV")
        print("3. Download as Excel")
        print("4. Plot data")

        choice = input("Enter the number of your choice: ").strip()

        if choice == '1':
            print("\nWeather Data:")
            print(tabulate(all_weather_records, headers=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"], tablefmt="grid"))
        elif choice == '2':
            save_to_csv(all_weather_records)
        elif choice == '3':
            save_to_excel(all_weather_records)
        elif choice == '4':
            if num_hours is None:
                num_hours = get_hours_history()
            plot_precipitation(all_weather_records, num_hours)
        else:
            print("Invalid choice. Exiting.")
    else:
        print("No weather records found for the specified period.")

# Function to get hours of history from .env file (defaults to 1 hour)
def get_hours_history():
    hours = os.getenv('HOURS_OF_HISTORY', '1')
    print(f"Hours of history from .env: {hours}")
    try:
        return int(hours)
    except ValueError:
        print(f"Invalid value for HOURS_OF_HISTORY in .env: {hours}. Defaulting to 1 hour.")
        return 1

# Start the first fetch
fetch_weather_data()
