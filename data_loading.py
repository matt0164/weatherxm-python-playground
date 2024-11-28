import os
import pandas as pd
from datetime import datetime, timedelta, timezone

SAVE_LOCATION = os.getenv('FILE_SAVE_LOCATION', os.getcwd())

def load_existing_data(filename="weather_data.csv"):
    """Loads data from an existing CSV file."""
    try:
        file_path = os.path.join(SAVE_LOCATION, filename)
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print("No existing data found.")
        return pd.DataFrame()


def determine_new_data_range(existing_data, requested_hours):
    """Determines the range of new data to fetch based on existing data."""
    if existing_data.empty:
        end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        start_date = end_date - timedelta(hours=requested_hours)
        return start_date, end_date

    last_timestamp = pd.to_datetime(existing_data["Timestamp"].max(), utc=True)
    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
    start_date = max(last_timestamp, end_date - timedelta(hours=requested_hours))
    return start_date, end_date
