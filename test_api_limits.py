
# Add this function to fetch and test date limits
import requests
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

load_dotenv()

# Get the WeatherXM API key and device ID from the environment variables
API_KEY = os.getenv('WXM_API_KEY').strip("'")
DEVICE_ID = os.getenv('DEVICE_ID').strip("'")
def test_api_date_limits():
    base_url = f"https://api.weatherxm.com/api/v1/me/devices/{DEVICE_ID}/history"
    start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()  # 30 days ago
    end_date = datetime.utcnow().isoformat()  # Now

    params = {
        'fromDate': start_date,
        'toDate': end_date
    }
    api_headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(base_url, headers=api_headers, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully fetched data for dates from {start_date} to {end_date}.")
        print(data)  # Print response to check the data structure
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to check date limits
test_api_date_limits()
