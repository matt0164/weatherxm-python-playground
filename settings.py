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

# Function to configure and update user settings
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
        print(f"7. Change file save location (current: {file_save_location})")  # Added file save location option
        print("8. Run fetch_weather_data script")  # Added option to run fetch_weather_data
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
                subprocess.run(["python", "fetch_weather_data.py"], check=True)  # Adjust path if needed
            except subprocess.CalledProcessError as e:
                print(f"Error running fetch_weather_data script: {e}")
        elif choice == '9':
            # Save changes to .env and exit
            update_env_file(username, password, api_key, device_id, temperature_unit, wind_speed_unit,
                            precipitation_unit, pressure_unit, wallet_address, hours_of_history)
            print("Settings saved. Exiting configuration.")
            break
        else:
            print("Invalid choice. Please enter a valid number.")

def configure_file_save_location():
    # Get the current file save location from the .env file, if it exists
    current_location = os.getenv('FILE_SAVE_LOCATION', os.getcwd())  # Default to current working directory
    print(f"Current file save location: {current_location}")

    # Prompt the user to enter a new file save location or press enter to keep the current location
    new_location = input("Enter a new file save location (or press Enter to keep the current location): ").strip()

    # Use the entered location if provided, otherwise, keep the current location
    if new_location:
        if os.path.isdir(new_location):
            save_to_env('FILE_SAVE_LOCATION', new_location)
        else:
            print(f"Invalid directory: {new_location}. Keeping the current location.")
    else:
        print("Keeping the current file save location.")

def configure_history_range():
    print("\nSelect History Range:")
    print("1. Hours")
    print("2. Days")
    print("3. Weeks")
    print("4. Months")
    print("5. Years")

    choice = input("\nEnter the number of the range you'd like to select: ").strip()
    hours = 1  # Default to 1 hour

    if choice == '1':
        hours = int(input("Enter number of hours: ").strip())
    elif choice == '2':
        days = int(input("Enter number of days: ").strip())
        hours = days * 24
    elif choice == '3':
        weeks = int(input("Enter number of weeks: ").strip())
        hours = weeks * 7 * 24
    elif choice == '4':
        months = int(input("Enter number of months: ").strip())
        hours = months * 30 * 24  # Assuming 30 days in a month
    elif choice == '5':
        years = int(input("Enter number of years: ").strip())
        hours = years * 365 * 24
    else:
        print("Invalid choice. Defaulting to 1 hour.")

    set_hours_history(hours)  # Save the selected hours to .env
    return hours

# Function to set hours of history in the .env file
def set_hours_history(hours):
    with open('.env', 'r') as file:
        lines = file.readlines()

    with open('.env', 'w') as file:
        for line in lines:
            if line.startswith('HOURS_OF_HISTORY'):
                file.write(f'HOURS_OF_HISTORY={hours}\n')
            else:
                file.write(line)

# Function to configure the API key (either manually or by fetching a new one)
def configure_api_key():
    global api_key
    print("\nAPI Key Configuration:")
    print("a. Enter a new API key manually")
    print("b. Run script to fetch a new API key")

    choice = input("\nEnter 'a' or 'b': ").strip().lower()

    if choice == 'a':
        api_key = input("Enter your new API key: ").strip()
    elif choice == 'b':
        print("Fetching a new API key...")
        try:
            subprocess.run(["python", "fetch_api_key.py"], check=True)  # Adjust path if needed
            # Reload .env after fetching the new key
            load_dotenv()
            api_key = os.getenv('WXM_API_KEY')
            print(f"New API key set: {api_key}")
        except subprocess.CalledProcessError as e:
            print(f"Error running fetch_api_key script: {e}")
    else:
        print("Invalid option. Returning to main menu.")

# Function to configure the device ID or wallet address
def configure_device_id():
    global device_id, wallet_address
    print("\nDevice ID / Wallet Configuration:")
    print("a. Enter the device ID manually")
    print("b. Enter your wallet address to automatically retrieve the device ID")

    choice = input("\nEnter 'a' or 'b': ").strip().lower()

    if choice == 'a':
        device_id = input("Enter your device ID: ").strip()
    elif choice == 'b':
        wallet_address = input("Enter your wallet address: ").strip()
        # Fetch device ID using wallet address
        try:
            print("Fetching device ID using wallet address...")
            subprocess.run([sys.executable, "get_station_id.py"], check=True)  # Ensures the correct Python interpreter
            # Reload .env after fetching the device ID
            load_dotenv()
            device_id = os.getenv('DEVICE_ID')
            if device_id:
                print(f"Device ID set: {device_id}")
            else:
                print("Failed to retrieve Device ID. Check the wallet address and try again.")
        except subprocess.CalledProcessError as e:
            print(f"Error running get_station_id script: {e}")
    else:
        print("Invalid option. Returning to main menu.")

# Function to configure units (with a submenu)
def configure_units(temp_unit, wind_unit, precip_unit, pressure_unit):
    while True:
        print("\nUnits Configuration:")
        print(f"1. Change temperature unit (current: {temp_unit})")
        print(f"2. Change wind speed unit (current: {wind_unit})")
        print(f"3. Change precipitation unit (current: {precip_unit})")
        print(f"4. Change pressure unit (current: {pressure_unit})")
        print("5. Go back to main menu")

        choice = input("\nEnter the number of the unit you'd like to change: ").strip()

        if choice == '1':
            temp_unit = input("Preferred temperature unit? (C or F): ").strip().upper()
        elif choice == '2':
            wind_unit = input("Preferred wind speed unit? (m/s or mph): ").strip().lower()
        elif choice == '3':
            precip_unit = input("Preferred precipitation unit? (mm or in): ").strip().lower()
        elif choice == '4':
            pressure_unit = input("Preferred pressure unit? (hPa or mb): ").strip().lower()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Returning to units menu.")

    return temp_unit, wind_unit, precip_unit, pressure_unit

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

# Function to update the .env file while preserving other variables and applying appropriate quotes
def update_env_file(username, password, api_key, device_id, temp_unit, wind_unit, precip_unit, pressure_unit,
                    wallet_address, hours_of_history):
    env_vars = {}

    # Read existing environment variables from .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value

    # Update or add the specific keys with appropriate quotes
    if username:
        env_vars['WXM_USERNAME'] = f"'{username}'"
    if password:
        env_vars['WXM_PASSWORD'] = f"'{password}'"
    if api_key:
        env_vars['WXM_API_KEY'] = f"'{api_key}'"
    if device_id:
        env_vars['DEVICE_ID'] = f"'{device_id}'"
    if wallet_address:
        env_vars['WALLET_ADDRESS'] = f"'{wallet_address}'"
    env_vars['TEMP_UNIT'] = f"'{temp_unit}'"
    env_vars['WIND_UNIT'] = f"'{wind_unit}'"
    env_vars['PRECIP_UNIT'] = f"'{precip_unit}'"
    env_vars['PRESSURE_UNIT'] = f"'{pressure_unit}'"
    env_vars['HOURS_OF_HISTORY'] = f"'{hours_of_history}'"

    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

if __name__ == "__main__":
    configure_settings()
