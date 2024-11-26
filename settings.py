import requests
import subprocess
import sys
import os
from dotenv import load_dotenv
import time  # For adding delay between retries

# Load .env file with existing environment variables
load_dotenv()

# Constants for retry logic
MAX_RETRIES = 3  # Maximum number of retries
RETRY_DELAY = 5  # Delay between retries in seconds

# Function to get current units from the environment variables
def get_units():
    temperature_unit = os.getenv('TEMP_UNIT', 'C')  # Default to Celsius
    wind_speed_unit = os.getenv('WIND_UNIT', 'm/s')  # Default to meters per second
    precipitation_unit = os.getenv('PRECIP_UNIT', 'mm')  # Default to millimeters
    pressure_unit = os.getenv('PRESSURE_UNIT', 'hPa')  # Default to hPa
    return temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit

def configure_plot_period():
    """
    Configure the time period for the precipitation chart in hours.
    """
    current_period = os.getenv('PLOT_PERIOD_HOURS', '24')  # Default to 24 hours
    print(f"Current plot period: {current_period} hours")

    new_period = input("Enter new plot period in hours (e.g., 24, 72, 168 for 1 week): ").strip()
    if new_period.isdigit():
        save_to_env('PLOT_PERIOD_HOURS', new_period)  # Save new value to .env
        print(f"Plot period updated to {new_period} hours.")
    else:
        print("Invalid input. Plot period remains unchanged.")

def retry_operation(operation, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
    """
    General retry logic for operations.

    Parameters:
        - operation: A callable function representing the operation.
        - max_retries: Maximum number of retries.
        - retry_delay: Delay between retries in seconds.

    Returns:
        - Result of the operation if successful.
        - None if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All retry attempts failed.")
                return None

# Function to configure the API key (with retry logic)
def configure_api_key():
    def fetch_api_key():
        print("Fetching a new API key. You may need to enter the device name...")
        subprocess.run([sys.executable, "fetch_api_key.py"], check=True)
        load_dotenv()  # Reload the updated .env file after fetching the key
        api_key = os.getenv('WXM_API_KEY')
        if api_key:
            print(f"New API key set: {api_key}")
        else:
            raise ValueError("Failed to fetch API key. API key is empty.")

    retry_operation(fetch_api_key)

# Function to configure the device ID or wallet address (with retry logic)
def configure_device_id():
    def fetch_device_id():
        print("\nDevice ID / Wallet Configuration:")
        print("a. Enter the device ID manually")
        print("b. Enter your wallet address to automatically retrieve the device ID")

        choice = input("\nEnter 'a' or 'b': ").strip().lower()

        if choice == 'a':
            return input("Enter your device ID: ").strip()
        elif choice == 'b':
            wallet_address = input("Enter your wallet address: ").strip()
            print("Fetching device ID using wallet address...")
            subprocess.run([sys.executable, "get_station_id.py"], check=True)  # Run the script to fetch device ID
            load_dotenv()  # Reload .env after fetching the device ID
            device_id = os.getenv('DEVICE_ID')
            if not device_id:
                raise ValueError("Failed to retrieve Device ID. Check the wallet address and try again.")
            print(f"Device ID set: {device_id}")
            return device_id
        else:
            raise ValueError("Invalid option selected.")

    device_id = retry_operation(fetch_device_id)
    if device_id:
        save_to_env('DEVICE_ID', device_id)

# Function to update the .env file
def save_to_env(key, value):
    """Updates or adds a key-value pair in the .env file."""
    env_vars = {}

    # Read the existing .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    k, v = line.strip().split('=', 1)
                    env_vars[k] = v

    # Update or add the specific key with the new value
    env_vars[key] = f"'{value}'"

    # Write all variables back to the .env file
    with open('.env', 'w') as file:
        for k, v in env_vars.items():
            file.write(f"{k}={v}\n")

# Main configuration setup
def configure_settings():
    print("Welcome to the WeatherXM Python Playground Configuration Setup.")

    while True:
        print("\nCurrent Configuration:")
        print(f"1. Configure API Key")
        print(f"2. Configure Device ID")
        print(f"3. Set Chart Plot Period (current: {os.getenv('PLOT_PERIOD_HOURS', '24')} hours)")
        print("4. Save and Exit")

        choice = input("\nEnter the number of the setting you'd like to change: ").strip()

        if choice == '1':
            configure_api_key()
        elif choice == '2':
            configure_device_id()
        elif choice == '3':
            configure_plot_period()
        elif choice == '4':
            print("Settings saved. Exiting configuration.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    configure_settings()
