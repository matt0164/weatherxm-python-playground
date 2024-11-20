import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_units():
    """Fetch weather data units from .env or set defaults."""
    temperature_unit = os.getenv('TEMP_UNIT', 'C')
    wind_speed_unit = os.getenv('WIND_UNIT', 'm/s')
    precipitation_unit = os.getenv('PRECIP_UNIT', 'mm')
    pressure_unit = os.getenv('PRESSURE_UNIT', 'hPa')
    return temperature_unit, wind_speed_unit, precipitation_unit, pressure_unit


def configure_settings():
    print("Welcome to the WeatherXM Python Playground Configuration Setup.")

    # Load existing values with proper type conversions
    username = os.getenv('WXM_USERNAME')
    password = os.getenv('WXM_PASSWORD')
    api_key = os.getenv('WXM_API_KEY')
    device_id = os.getenv('DEVICE_ID')
    station_id = os.getenv('STATION_ID', 'Not set')
    file_save_location = os.getenv('FILE_SAVE_LOCATION', os.getcwd())
    hours_of_history = int(os.getenv('HOURS_OF_HISTORY', '1'))  # Ensure integer type
    days_of_history = hours_of_history // 24  # Calculate days based on hours

    while True:
        print("\nCurrent Configuration:")
        print(f"1. Username: {username if username else 'Not set'}")
        print(f"2. Password: [hidden]")
        print(f"3. Device ID: {device_id if device_id else 'Not set'}")
        print(f"4. Station ID: {station_id}")
        print(f"5. File Save Location: {file_save_location}")
        print(f"6. Hours of History: {hours_of_history}")
        print(f"7. Days of History: {days_of_history}")
        print(f"8. Change Units (temperature, wind speed, precipitation, pressure)")
        print("9. Save and Exit")

        choice = input("Select an option to update (1-9): ").strip()

        if choice == '1':
            username = input("Enter your WeatherXM username (email): ").strip()
        elif choice == '2':
            password = input("Enter your WeatherXM password: ").strip()
        elif choice == '3':
            device_id = input("Enter your Device ID: ").strip()
        elif choice == '4':
            station_id = input("Enter your Station ID: ").strip()
        elif choice == '5':
            file_save_location = configure_file_save_location()
        elif choice == '6':
            try:
                hours_of_history = int(input("Enter the number of hours of history to fetch: ").strip())
                if hours_of_history < 0:
                    print("Hours of history cannot be negative.")
                else:
                    days_of_history = hours_of_history // 24  # Automatically update days
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        elif choice == '7':
            try:
                days_of_history = int(input("Enter the number of days of history to fetch: ").strip())
                if days_of_history < 0:
                    print("Days of history cannot be negative.")
                else:
                    hours_of_history = days_of_history * 24  # Automatically update hours
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        elif choice == '8':
            configure_units()
        elif choice == '9':
            # Save changes to the .env file
            update_env_file(
                WXM_USERNAME=username,
                WXM_PASSWORD=password,
                DEVICE_ID=device_id,
                STATION_ID=station_id,
                FILE_SAVE_LOCATION=file_save_location,
                HOURS_OF_HISTORY=hours_of_history,
                DAYS_OF_HISTORY=days_of_history
            )
            print("Settings saved. Exiting.")
            break
        else:
            print("Invalid option. Please select a valid number.")

def configure_hours_of_history(current_hours):
    """Configure the number of hours of history."""
    while True:
        try:
            hours = int(input("Enter the number of hours of history to fetch: ").strip())
            if hours < 0:
                print("Please enter a non-negative number.")
            else:
                return hours
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def configure_days_of_history(current_days):
    """Configure the number of days of history."""
    while True:
        try:
            days = int(input("Enter the number of days of history to fetch: ").strip())
            if days < 0:
                print("Please enter a non-negative number.")
            else:
                return days
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def configure_file_save_location():
    """Allow user to set or validate file save location."""
    current_location = os.getenv('FILE_SAVE_LOCATION', os.getcwd())
    print(f"Current file save location: {current_location}")
    new_location = input("Enter new file save location (or press Enter to keep current): ").strip()
    if new_location:
        if os.path.isdir(new_location):
            return new_location
        else:
            print(f"Invalid directory: {new_location}. Keeping current location.")
    return current_location


def configure_units():
    """Configure units for temperature, wind speed, precipitation, and pressure."""
    temp_unit = input("Enter preferred temperature unit (C/F): ").strip().upper()
    wind_unit = input("Enter preferred wind speed unit (m/s or mph): ").strip().lower()
    precip_unit = input("Enter preferred precipitation unit (mm or in): ").strip().lower()
    pressure_unit = input("Enter preferred pressure unit (hPa or mb): ").strip().lower()

    # Update the .env file with new unit preferences
    update_env_file(
        TEMP_UNIT=temp_unit,
        WIND_UNIT=wind_unit,
        PRECIP_UNIT=precip_unit,
        PRESSURE_UNIT=pressure_unit
    )
    print("Units updated successfully.")


def configure_hours_of_history(current_hours):
    """Configure the number of hours of weather history to fetch."""
    print(f"Current Hours of History: {current_hours}")
    new_hours = input("Enter the number of hours of history to fetch: ").strip()
    if new_hours.isdigit():
        return new_hours
    else:
        print("Invalid input. Keeping the current value.")
        return current_hours


def update_env_file(**kwargs):
    """
    Updates or adds key-value pairs in the .env file.
    Preserves other existing variables.
    """
    env_vars = {}

    # Read the existing .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if "=" in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value.strip('"\'')

    # Update with new values
    for key, value in kwargs.items():
        env_vars[key] = str(value)

    # Write all variables back to the .env file
    with open('.env', 'w') as file:
        for key, value in env_vars.items():
            file.write(f'{key}="{value}"\n')

    print(".env file updated successfully.")
    # Reload the updated environment variables
    load_dotenv()


if __name__ == "__main__":
    configure_settings()
