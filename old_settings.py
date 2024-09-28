import subprocess
import sys
import os
from dotenv import load_dotenv

# Load .env file with existing environment variables
load_dotenv()

# Function to fetch preferred units from the .env file, with defaults if not present
def get_units():
    temperature_unit = os.getenv('TEMP_UNIT', 'C').strip("'")
    wind_speed_unit = os.getenv('WIND_UNIT', 'm/s').strip("'")
    precipitation_unit = os.getenv('PRECIP_UNIT', 'mm').strip("'")
    pressure_unit = os.getenv('PRESSURE_UNIT', 'hPa').strip("'")
    return temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit

# Function to get days of history from the .env file
def get_days_history():
    return int(os.getenv('DAYS_OF_HISTORY', 1))  # Use 1 day as the default

# Function to update the .env file while preserving other variables
def update_env_file(username, password, api_key, device_id, temp_unit, wind_unit, precip_unit, pressure_unit,
                    wallet_address, days_of_history):
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
    env_vars['DAYS_OF_HISTORY'] = f"'{days_of_history}'"  # Add days_of_history

    # Write all variables back to the .env file
    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")

    print(".env file updated with your settings.")

# Function to configure and update user settings
def configure_settings():
    print("Welcome to the WeatherXM configuration setup.")
    days_of_history = get_days_history()

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
        print(f"5. Change units (temperature: {temperature_unit}, wind: {wind_speed_unit}, precipitation: {precipitation_unit}, pressure: {pressure_unit})")
        print(f"6. Change history range (current: {days_of_history} days)")
        print("7. Save and Exit")

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
            days_of_history = configure_history_range()
        elif choice == '7':
            # Save changes to .env and exit
            update_env_file(username, password, api_key, device_id, temperature_unit, wind_speed_unit,
                             precipitation_unit, pressure_unit, wallet_address, days_of_history)
            print("Settings saved. Exiting configuration.")
            break
        else:
            print("Invalid choice. Please enter a valid number.")

def configure_history_range():
    print("\nSelect History Range:")
    print("1. Days")
    print("2. Weeks")
    print("3. Months")
    print("4. Years")

    choice = input("\nEnter the number of the range you'd like to select: ").strip()

    if choice == '1':
        days = int(input("Enter number of days: ").strip())
    elif choice == '2':
        weeks = int(input("Enter number of weeks: ").strip())
        days = weeks * 7
    elif choice == '3':
        months = int(input("Enter number of months: ").strip())
        days = months * 30  # Assuming 30 days in a month
    elif choice == '4':
        years = int(input("Enter number of years: ").strip())
        days = years * 365
    else:
        print("Invalid choice. Returning to main menu.")
        return get_days_history()

    # Update the .env file with the new settings
    set_days_history(days)
    print(f"History range set to {days} days.")
    return days  # Return the updated days

# Function to set days of history in the .env file
def set_days_history(days):
    # Set the DAYS_OF_HISTORY in the .env file
    update_env_file(username=None, password=None, api_key=None, device_id=None,
                    temp_unit=None, wind_unit=None, precip_unit=None,
                    pressure_unit=None, wallet_address=None, days_of_history=days)

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

        choice = input("\nEnter the number of the setting you'd like to change: ").strip()

        if choice == '1':
            temp_unit = input("Enter temperature unit (C/F): ").strip().upper()
        elif choice == '2':
            wind_unit = input("Enter wind speed unit (m/s or km/h): ").strip()
        elif choice == '3':
            precip_unit = input("Enter precipitation unit (mm/in): ").strip()
        elif choice == '4':
            pressure_unit = input("Enter pressure unit (hPa/atm): ").strip()
        elif choice == '5':
            return temp_unit, wind_unit, precip_unit, pressure_unit  # Return updated units
        else:
            print("Invalid choice. Please enter a valid number.")

if __name__ == "__main__":
    configure_settings()
