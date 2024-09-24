# How It Works:
# Initial Check: The script first reads the .env file and checks if the username, password, API key, and device ID are already set.

# Prompt User with Options: It displays a list of options for the user, showing which values are currently set
# and allowing them to select what to update by entering the corresponding number.

# If Missing Values: If username, password, API key, or device ID is not set, it will show "Set username", "Set password", etc. instead.
# Saving to .env: After updating the values, the script saves the values back to the .env file,
# preserving any existing variables not being modified.

# Example Flow:
# If a user runs this for the first time, the script will ask them to enter their username and password
# since those will be empty.
# If units are already set (from a previous run), it defaults to the currently set units unless the user
# chooses to change them.

import subprocess
import sys
import os
from dotenv import load_dotenv

# Load .env file with existing environment variables
load_dotenv()


# Function to configure and update user settings
def configure_settings():
    print("Welcome to the WeatherXM configuration setup.")

    # Get current values from .env file
    username = os.getenv('WXM_USERNAME')
    password = os.getenv('WXM_PASSWORD')
    api_key = os.getenv('WXM_API_KEY')
    device_id = os.getenv('DEVICE_ID')
    wallet_address = os.getenv('WALLET_ADDRESS')
    temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit = get_units()

    while True:
        # List options for user to change
        print("\nCurrent Configuration:")
        print(f"1. Change username (current: {username if username else 'Not set'})")
        print(f"2. Change password (current: [hidden])")
        print(f"3. Set API key (current: {api_key if api_key else 'Not set'})")
        print(f"4. Set Device ID (current: {device_id if device_id else 'Not set'})")
        print(
            f"5. Change units (temperature: {temperature_unit}, wind: {wind_speed_unit}, precipitation: {precipitation_unit}, pressure: {pressure_unit})")
        print("6. Save and Exit")

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
            configure_units(temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit)
        elif choice == '6':
            # Save changes to .env and exit
            update_env_file(username, password, api_key, device_id, temperature_unit, wind_speed_unit,
                            precipitation_unit, pressure_unit, wallet_address)
            print("Settings saved. Exiting configuration.")
            break
        else:
            print("Invalid choice. Please enter a valid number.")


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


# Function to update the .env file while preserving other variables and applying appropriate quotes
def update_env_file(username, password, api_key, device_id, temp_unit, wind_unit, precip_unit, pressure_unit,
                    wallet_address):
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

    # Write all variables back to the .env file
    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

    print(".env file updated with your settings.")


# Function to fetch preferred units from the .env file, with defaults if not present
def get_units():
    temperature_unit = os.getenv('TEMP_UNIT', 'C').strip("'")
    wind_speed_unit = os.getenv('WIND_UNIT', 'm/s').strip("'")
    precipitation_unit = os.getenv('PRECIP_UNIT', 'mm').strip("'")
    pressure_unit = os.getenv('PRESSURE_UNIT', 'hPa').strip("'")
    return temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit


# Main block to run the configuration setup
if __name__ == "__main__":
    configure_settings()
