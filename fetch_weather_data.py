import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import pandas as pd

# Load environment variables
load_dotenv()

# Fetch settings from .env
API_KEY = os.getenv("WXM_API_KEY")
DEVICE_ID = os.getenv("DEVICE_ID")
SAVE_LOCATION = os.getenv("FILE_SAVE_LOCATION", os.getcwd())
HOURS_OF_HISTORY = int(os.getenv("HOURS_OF_HISTORY", 1))

# File to save previous data
PREVIOUS_DATA_FILE = os.path.join(SAVE_LOCATION, "previous_weather_data.csv")

def fetch_weather_data():
    """
    Fetches weather data from the API and updates the local CSV file.
    """
    try:
        # Determine the latest timestamp in the existing data
        if os.path.exists(PREVIOUS_DATA_FILE):
            existing_data = pd.read_csv(PREVIOUS_DATA_FILE)
            print("Existing data loaded.")

            # Ensure valid timestamps
            existing_data["Timestamp"] = pd.to_datetime(existing_data["Timestamp"], errors="coerce")
            valid_data = existing_data.dropna(subset=["Timestamp"])
            print(f"Valid timestamps found: {len(valid_data)}")
            latest_timestamp = valid_data["Timestamp"].max()
            print(f"Latest timestamp in existing data: {latest_timestamp}")
        else:
            latest_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=HOURS_OF_HISTORY)
            print(f"No previous data found. Starting from: {latest_timestamp}")

        # Set the date range for the API call
        end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        start_date = latest_timestamp
        print(f"Requesting data from {start_date} to {end_date}")

        # API URL and headers
        BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"
        params = {
            "fromDate": start_date.isoformat(),
            "toDate": end_date.isoformat()
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }

        # API request
        response = requests.get(BASE_URL, headers=headers, params=params)
        print("API response status:", response.status_code)
        print("API response content (truncated):", response.text[:1000])  # Truncated for readability

        response.raise_for_status()

        # Parse response
        data = response.json()
        print(f"Fetched {len(data)} records from API.")

        # Prepare the data for saving
        weather_records = []
        for record in data:
            if "hourly" in record:
                for hourly_record in record["hourly"]:
                    try:
                        weather_records.append({
                            "Timestamp": hourly_record.get("timestamp"),
                            "Temperature": hourly_record.get("temperature"),
                            "Humidity": hourly_record.get("humidity"),
                            "Wind Speed": hourly_record.get("wind_speed"),
                            "Precipitation": hourly_record.get("precipitation"),
                            "Pressure": hourly_record.get("pressure"),
                        })
                    except KeyError as e:
                        print(f"Error parsing hourly record {hourly_record}: {e}")
                        continue

        if not weather_records:
            print("No valid records parsed from API response.")
            return

        new_data = pd.DataFrame(weather_records)
        print(f"New data shape: {new_data.shape}")

        # Validate and combine data
        if not new_data.empty:
            new_data["Timestamp"] = pd.to_datetime(new_data["Timestamp"], errors="coerce")
            combined_data = pd.concat([valid_data, new_data], ignore_index=True).drop_duplicates(subset="Timestamp",
                                                                                                 keep="last")
            combined_data.to_csv(PREVIOUS_DATA_FILE, index=False)
            print(f"Updated data saved to '{PREVIOUS_DATA_FILE}'.")
        else:
            print("No new data fetched. Skipping update.")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

def save_weather_data(new_weather_records):
    """
    Save new weather data to the CSV file, appending to existing data and avoiding duplicates.
    """
    try:
        # Load existing data if it exists
        if os.path.exists(PREVIOUS_DATA_FILE):
            existing_data = pd.read_csv(PREVIOUS_DATA_FILE)
            print("Loaded existing data.")
        else:
            existing_data = pd.DataFrame(columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
            print("No existing data found. Creating a new file.")

        # Combine new and existing data
        new_data = pd.DataFrame(new_weather_records, columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset="Timestamp", keep="last")

        # Save to file
        combined_data.to_csv(PREVIOUS_DATA_FILE, index=False)
        print(f"Updated data saved to '{PREVIOUS_DATA_FILE}'.")

    except Exception as err:
        print(f"Error saving data: {err}")

if __name__ == "__main__":
    fetch_weather_data()
