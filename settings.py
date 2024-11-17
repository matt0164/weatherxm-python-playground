import requests
import subprocess
import sys
import os
from dotenv import load_dotenv

# Load .env file with existing environment variables
load_dotenv()

# Function to get current units from the environment variables
def get_units():
    temperature_unit = os.getenv('TEMP_UNIT', 'C')  # Default to Celsius
    wind_speed_unit = os.getenv('WIND_UNIT', 'm/s')  # Default to meters per second
    precipitation_unit = os.getenv('PRECIP_UNIT', 'mm')  # Default to millimeters
    pressure_unit = os.getenv('PRESSURE_UNIT', 'hPa')  # Default to hPa
    return temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit

# Main function to configure settings
def configure_settings():
    print("Welcome to the WeatherXM Python Playground Configuration Setup.")

    # Get current values from .env file
    username = os.getenv('WXM_USERNAME')
    password = os.getenv('WXM_PASSWORD')
    api_key = os.getenv('WXM_API_KEY')
    device_id = os.getenv('DEVICE_ID')
    wallet_address = os.getenv('WALLET_ADDRESS')
    file_save_location = os.getenv('FILE_SAVE_LOCATION', os.getcwd())  # Default to current working directory
    temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = get_units()
    hours_of_history = 1  # Default to 1 hour

    while True:
        # List options for user to change
        print("\nCurrent Configuration:")
        print(f"1. Change username (current: {username if username else 'Not set'})")
        print(f"2. Change password (current: [hidden])")
        print(f"3. Set API key (current: {api_key if api_key else 'Not set'})")
        print(f"4. Set Device ID (current: {device_id if device_id else 'Not set'})")
        print(f"5. Change units (temperature: {temperature_unit}, wind: {wind_speed_unit}, precipitation: {precipitation_unit}, pressure: {pressure_unit})")
        print(f"6. Change history range (current: {hours_of_history} hours)")
        print(f"7. Change file save location (current: {file_save_location})")
        print("8. Run the software to fetch weather history")
        print("9. Save and Exit")

        # Ask user what they'd like to update
        choice = input("\nEnter the number of the setting you'd like to change: ").strip()

        # Handle user input
        if choice == '1':
            username = input("Enter your WeatherXM username (email): ").strip()
        elif choice == '2':
            password = input("Enter your WeatherXM password: ").strip()
        elif choice == '3':
            configure_api_key()
        elif choice == '4':
            configure_device_id()
        elif choice == '5':
            temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = configure_units(
                temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit)
        elif choice == '6':
            hours_of_history = configure_history_range()
        elif choice == '7':  # Add file save location change
            configure_file_save_location()
        elif choice == '8':  # Run fetch_weather_data script
            try:
                from fetch_weather_data import fetch_weather_data, save_previous_data
                all_weather_records = fetch_weather_data()
                if all_weather_records:
                    save_previous_data(all_weather_records)
            except Exception as e:
                print(f"Error running fetch_weather_data: {e}")
        elif choice == '9':
            # Save changes to .env and exit
            update_env_file(username, password, api_key, device_id, temperature_unit, wind_speed_unit,
                            precipitation_unit, pressure_unit, wallet_address, hours_of_history)
            print("Settings saved. Exiting configuration.")
            break
        else:
            print("Invalid choice. Please enter a valid number.")

# Function to configure the API key
def configure_api_key():
    try:
        subprocess.run([sys.executable, "fetch_api_key.py"], check=True)
        load_dotenv()  # Reload updated .env file
        new_api_key = os.getenv('WXM_API_KEY')
        print(f"New API key set: {new_api_key}")
    except subprocess.CalledProcessError as e:
        print(f"Error fetching API key: {e}")

# Main section to run the program
if __name__ == "__main__":
    try:
        configure_settings()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
