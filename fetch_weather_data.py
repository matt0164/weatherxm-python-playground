import os
from dotenv import load_dotenv
from datetime import timedelta
from data_loading import load_existing_data, determine_new_data_range
from api_manager import initialize_api, fetch_data_segment
from data_saving import save_to_csv, save_to_excel

# Load environment variables
load_dotenv()

DEFAULT_HOURS_HISTORY = int(os.getenv('HOURS_OF_HISTORY', '24'))

def fetch_weather_data(requested_hours=DEFAULT_HOURS_HISTORY):
    """Fetches and saves weather data."""
    # Initialize API credentials
    api_key, device_id = initialize_api()

    # Load existing data
    existing_data = load_existing_data()

    # Determine range of new data to fetch
    start_date, end_date = determine_new_data_range(existing_data, requested_hours)
    print(f"Fetching data from {start_date} to {end_date}")

    # Fetch data in hourly segments
    all_records = []
    while start_date < end_date:
        segment_end_date = min(start_date + timedelta(hours=24), end_date)
        records = fetch_data_segment(api_key, device_id, start_date, segment_end_date)
        all_records.extend(records)
        start_date = segment_end_date

    # Save new data
    if all_records:
        save_to_csv(all_records)
        save_to_excel(all_records)
    else:
        print("No new records to save.")

if __name__ == "__main__":
    fetch_weather_data()
