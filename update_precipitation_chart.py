import os
from dotenv import load_dotenv
from data_fetching import fetch_latest_weather_data
from data_visualization_v2 import plot_precipitation
from datetime import datetime

def validate_num_hours():
    """
    Validate and retrieve the number of hours from the environment variable.
    Returns a default value (24) if invalid or missing.
    """
    try:
        num_hours = int(os.getenv('NUM_HOURS', 24))  # Default to 24 hours
        if num_hours <= 0:
            raise ValueError("NUM_HOURS must be a positive integer.")
        return num_hours
    except ValueError as e:
        print(f"[{datetime.now()}] Invalid NUM_HOURS value in .env: {e}. Defaulting to 24 hours.")
        return 24

def main():
    # Step 1: Load the latest settings from .env
    load_dotenv()
    print(f"[{datetime.now()}] Loaded settings from .env")

    # Step 2: Validate and retrieve the time range for fetching data
    num_hours = validate_num_hours()
    print(f"[{datetime.now()}] Fetching latest weather data for the past {num_hours} hours...")

    # Step 3: Fetch the latest weather data
    try:
        weather_records = fetch_latest_weather_data(num_hours=num_hours)
        if not weather_records:
            print(f"[{datetime.now()}] Error: No weather data available. Chart generation skipped.")
            return
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching weather data: {e}")
        return

    # Step 4: Plot the precipitation chart
    try:
        print(f"[{datetime.now()}] Generating precipitation chart...")
        plot_precipitation(weather_records, num_hours=num_hours)
        print(f"[{datetime.now()}] Precipitation chart updated successfully.")
    except Exception as e:
        print(f"[{datetime.now()}] Error generating precipitation chart: {e}")

if __name__ == "__main__":
    main()
