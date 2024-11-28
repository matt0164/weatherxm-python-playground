# api_requests.py
import requests

BASE_URL = "https://api.weatherxm.com/api/v1/me/devices/{}/history"

def fetch_data_segment(api_key, device_id, from_date, to_date):
    """Fetches data for a specific time segment."""
    params = {'fromDate': from_date.isoformat(), 'toDate': to_date.isoformat()}
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(BASE_URL.format(device_id), headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        # Handle API response structure
        if isinstance(data, list):
            return data  # API returned a list of records
        elif isinstance(data, dict):
            return data.get("records", [])
        else:
            print("Unexpected API response format.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return []
