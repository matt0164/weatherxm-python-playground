import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from time import sleep

# Load .env file
load_dotenv()

# Get the WeatherXM API key and device ID from environment variables
API_KEY = os.getenv('WXM_API_KEY', '').strip("'")
DEVICE_ID = os.getenv('DEVICE_ID', '').strip("'")

if not API_KEY or not DEVICE_ID:
    raise ValueError("API_KEY or DEVICE_ID is missing. Check your .env file.")

def fetch_latest_weather_data(num_hours=24):
    """
    Fetch the latest weather data and return it as a list of dictionaries.

    Parameters:
    - num_hours (int): Number of hours of historical data to fetch.

    Returns:
    - List[dict]: A list of dictionaries containing weather data.

    Raises:
    - ValueError: If API_KEY or DEVICE_ID is missing.
    - requests.exceptions.HTTPError: For HTTP errors during API requests.
    """
    all_weather_records = []
    max_api_hours = 24  # API limitation
    num_requests = (num_hours + max_api_hours - 1) // max_api_hours  # Ceiling division

    end_date = datetime.utcnow().replace(tzinfo=timezone.utc)
    BASE_URL = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"

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

        for attempt in range(3):  # Retry logic
            try:
                response = requests.get(BASE_URL, headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Accept': 'application/json'
                }, params=params)
                response.raise_for_status()
                data = response.json()

                if isinstance(data, list):
                    for day_data in data:
                        hourly_data_list = day_data.get('hourly', [])
                        for hourly_data in hourly_data_list:
                            timestamp = hourly_data.get('timestamp')
                            if timestamp:
                                record = {
                                    "Timestamp": timestamp,
                                    "Temperature": hourly_data.get('temperature', 0),
                                    "Humidity": hourly_data.get('humidity', 0),
                                    "Wind Speed": hourly_data.get('wind_speed', 0),
                                    "Precipitation": hourly_data.get('precipitation', 0),  # In mm
                                    "Pressure": hourly_data.get('pressure', 0)
                                }
                                all_weather_records.append(record)
                break  # Exit retry loop if successful
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}. URL: {response.url}")
                if attempt < 2:
                    sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
            except Exception as err:
                print(f"An error occurred: {err}. Parameters: {params}")
                if attempt == 2:
                    raise

    if not all_weather_records:
        print("No weather records found for the specified period.")

    return all_weather_records
