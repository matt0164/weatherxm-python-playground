import os
from dotenv import load_dotenv
from data_fetching import fetch_latest_weather_data
from data_visualization_v2 import plot_precipitation
from datetime import datetime

def main():
    # Step 1: Load the latest settings from .env
    load_dotenv()
    print(f"[{datetime.now()}] Loaded settings from .env")

    # Step 2: Determine the time range for fetching data
    num_hours = int(os.getenv('NUM_HOURS', 24))  # Default to 24 hours
    print(f"[{datetime.now()}] Fetching latest weather data for the past {num_hours} hours...")

    # Step 3: Fetch the latest weather data
    weather_records = fetch_latest_weather_data(num_hours=num_hours)
    if not weather_records:
        print(f"[{datetime.now()}] Error: No weather data available. Chart generation skipped.")
        return

    # Step 4: Plot the precipitation chart
    print(f"[{datetime.now()}] Generating precipitation chart...")
    plot_precipitation(weather_records, num_hours=num_hours)

    print(f"[{datetime.now()}] Precipitation chart updated successfully.")

if __name__ == "__main__":
    main()
