#fetch_weather_data.py
#Main module for fetching and processing weather data from the WeatherXM API

import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
from data_loading import load_existing_data, determine_new_data_range
from api_manager import initialize_api, fetch_data_segment
from data_saving import save_to_csv, save_to_excel, save_raw_data, flatten_data

# Load environment variables
load_dotenv()

DEFAULT_HOURS_HISTORY = int(os.getenv('HOURS_OF_HISTORY', '24'))

def fetch_weather_data(requested_hours=DEFAULT_HOURS_HISTORY):
    """Fetches and saves weather data, returning the processed data and summary."""
    try:
        # Initialize API and fetch existing data
        api_key, device_id = initialize_api()
        existing_data = load_existing_data()

        # Determine the range of data to fetch
        start_date, end_date = determine_new_data_range(existing_data, requested_hours)
        print(f"Fetching data from {start_date} to {end_date}")

        # Fetch data in segments
        all_records = []
        current_date = start_date

        while current_date < end_date:
            next_date = min(current_date + timedelta(hours=24), end_date)
            records = fetch_data_segment(api_key, device_id, current_date, next_date)

            if records:
                all_records.extend(records)

            current_date = next_date

        # Save raw data
        save_raw_data(all_records)

        # Flatten and save the processed data
        flattened_data = flatten_data(all_records)
        save_to_csv(flattened_data)
        save_to_excel(flattened_data)

        # Generate summary
        summary = generate_summary(all_records, start_date, end_date)
        return flattened_data, summary

    except Exception as e:
        print(f"Error in fetch_weather_data: {e}")
        return [], {"error": str(e)}

def generate_summary(data, start_date, end_date):
    """Generates a summary from the fetched data."""
    if not data:
        return {"message": "No data fetched."}

    temperatures = [entry['temperature'] for record in data for entry in record.get('hourly', []) if 'temperature' in entry]

    return {
        "total_records": len(data),
        "start_time": start_date,
        "end_time": end_date,
        "avg_temperature": sum(temperatures) / len(temperatures) if temperatures else None,
        "min_temperature": min(temperatures) if temperatures else None,
        "max_temperature": max(temperatures) if temperatures else None
    }

def calculate_average_temperature(data):
    """Calculate average temperature from the flattened data."""
    temps = [record['temperature'] for record in data if 'temperature' in record]
    return sum(temps) / len(temps) if temps else None

if __name__ == "__main__":
    fetched_data, data_summary = fetch_weather_data()
    print("Summary:", data_summary)
