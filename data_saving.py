# data_saving.py

import os
import json
import pandas as pd
import csv
from datetime import datetime

# Define base data directories
BASE_DIR = os.path.join(os.getcwd(), "data")
RAW_DIR = os.path.join(BASE_DIR, "raw")
CSV_DIR = os.path.join(BASE_DIR, "csv")
EXCEL_DIR = os.path.join(BASE_DIR, "excel")
CUMULATIVE_CSV = os.path.join(CSV_DIR, "all_weather_data.csv")

# Ensure directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)

# Function to save raw JSON data
def save_raw_data(raw_data, filename=None):
    """Saves raw JSON data to the raw data directory."""
    if not filename:
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.json"
    file_path = os.path.join(RAW_DIR, filename)
    with open(file_path, 'w') as f:
        json.dump(raw_data, f, indent=4)
    print(f"Raw data saved to: {file_path}")

# Function to flatten data for CSV and Excel
def flatten_data(json_data):
    """Flattens nested JSON data into tabular format."""
    flattened = []
    for record in json_data:
        # Ensure the 'hourly' key exists
        if 'hourly' in record:
            for hourly_entry in record['hourly']:
                flattened.append({
                    'timestamp': hourly_entry.get('timestamp', None),
                    'temperature': hourly_entry.get('temperature', None),
                    'precipitation_accumulated': hourly_entry.get('precipitation_accumulated', None),
                    'wind_speed': hourly_entry.get('wind_speed', None),
                    'humidity': hourly_entry.get('humidity', None),
                    'pressure': hourly_entry.get('pressure', None),
                    'icon': hourly_entry.get('icon', ''),  # Optional field
                })
        else:
            print(f"Skipping record without 'hourly' data: {record}")
    return flattened

# Function to save flattened data to a daily CSV
def save_to_csv(data, filename=None):
    """Saves flattened data to a daily CSV file in the CSV directory."""
    if not filename:
        filename = f"{datetime.now().strftime('%Y-%m-%d')}.csv"
    file_path = os.path.join(CSV_DIR, filename)
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Flattened data saved to: {file_path}")

# Function to save flattened data to an Excel file
def save_to_excel(data, filename="weather_data.xlsx"):
    """Saves weather data to an Excel file in the data/excel directory."""
    file_path = os.path.join(EXCEL_DIR, filename)
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    print(f"Flattened data saved to: {file_path}")

# Function to append data to a cumulative CSV
def append_to_cumulative_csv(data):
    """Appends flattened data to a cumulative CSV file."""
    file_path = CUMULATIVE_CSV
    keys = data[0].keys() if data else []

    # Check if the cumulative file exists
    write_header = not os.path.exists(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if write_header:
            writer.writeheader()
        writer.writerows(data)
    print(f"Data appended to cumulative CSV: {file_path}")

# Example Usage
if __name__ == "__main__":
    # Mocked API response for demonstration
    example_response = [
        {
            'timestamp': '2024-11-28T00:00:00-05:00',
            'temperature': 6.5,
            'precipitation_accumulated': 0,
            'wind_speed': 0,
            'humidity': 70,
            'pressure': 1009.7,
            'icon': 'partly-cloudy-night',
        },
        {
            'timestamp': '2024-11-28T01:00:00-05:00',
            'temperature': 6.3,
            'precipitation_accumulated': 0.1,
            'wind_speed': 1.2,
            'humidity': 75,
            'pressure': 1008.2,
            'icon': 'rain',
        },
    ]

    # Save raw JSON
    save_raw_data(example_response)

    # Flatten and save to daily CSV
    flattened = flatten_data(example_response)
    save_to_csv(flattened)

    # Append to cumulative CSV
    append_to_cumulative_csv(flattened)

    # Save to Excel
    save_to_excel(flattened)
