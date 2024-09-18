import os
from dotenv import load_dotenv

# Load .env file if it exists to keep track of user settings
load_dotenv()


# Function to ask for unit preferences with clear choices
def configure_units():
    # Ask for temperature unit (Celsius or Fahrenheit)
    while True:
        temperature_unit = input("Preferred temperature unit? (C or F): ").strip().upper()
        if temperature_unit in ['C', 'F']:
            break
        print("Invalid input. Please enter 'C' or 'F'.")

    # Ask for wind speed unit (m/s or mph)
    while True:
        wind_speed_unit = input("Preferred wind speed unit? (m/s or mph): ").strip().lower()
        if wind_speed_unit in ['m/s', 'mph']:
            break
        print("Invalid input. Please enter 'm/s' or 'mph'.")

    # Ask for precipitation unit (mm or in)
    while True:
        precipitation_unit = input("Preferred precipitation unit? (mm or in): ").strip().lower()
        if precipitation_unit in ['mm', 'in']:
            break
        print("Invalid input. Please enter 'mm' or 'in'.")

    # Ask for pressure unit (hPa or mb)
    while True:
        pressure_unit = input("Preferred pressure unit? (hPa or mb): ").strip().lower()
        if pressure_unit in ['hpa', 'mb']:  # Convert user input to lowercase
            break
        print("Invalid input. Please enter 'hPa' or 'mb'.")

    # Save preferences to .env for persistence
    with open('.env', 'w') as f:  # Overwrite existing .env file
        f.write(f"TEMPERATURE_UNIT={temperature_unit}\n")
        f.write(f"WIND_SPEED_UNIT={wind_speed_unit}\n")
        f.write(f"PRECIPITATION_UNIT={precipitation_unit}\n")
        f.write(f"PRESSURE_UNIT={pressure_unit}\n")

    print("Settings updated successfully.")


# Main function to handle the update prompt
def main():
    # Ask if the user wants to update settings
    update = input("Do you want to update your unit settings? (yes/no): ").strip().lower()

    if update == 'yes':
        configure_units()
    else:
        print("Settings were not updated.")


# Run the main function if this script is executed
if __name__ == '__main__':
    main()
