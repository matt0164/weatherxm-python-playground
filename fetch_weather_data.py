import os
from dotenv import load_dotenv
from datetime import timedelta
from data_loading import load_existing_data, determine_new_data_range
from api_manager import initialize_api, fetch_data_segment
from data_saving import save_to_csv, save_to_excel, save_raw_data, flatten_data

# Load environment variables
load_dotenv()

DEFAULT_HOURS_HISTORY = int(os.getenv('HOURS_OF_HISTORY', '24'))

def fetch_weather_data(requested_hours=DEFAULT_HOURS_HISTORY):
    """Fetches and saves weather data and returns a summary."""
    # Existing logic to fetch weather data...

    # Generate a summary of the data
    summary = {
        "total_records": len(all_records),
        "start_time": start_date,
        "end_time": end_date,
        "avg_temperature": calculate_average_temperature(all_records),
        "min_temperature": min(all_records, key=lambda x: x["temp"])[0]["temp"],
        "max_temperature": max(all_records, key=lambda x: x["temp"])[0]["temp"],
    }
    return all_records, summary

def calculate_average_temperature(data):
    """Calculate average temperature from the data."""
    temps = [record["temp"] for record in data if "temp" in record]
    return sum(temps) / len(temps) if temps else None

if __name__ == "__main__":
    fetch_weather_data()
