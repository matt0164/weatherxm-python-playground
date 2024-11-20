import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def configure_settings():
    """Interactive settings configuration."""
    print("WeatherXM Configuration Menu")

    # Fetch existing values
    api_key = os.getenv("WXM_API_KEY", "")
    device_id = os.getenv("DEVICE_ID", "")
    hours_of_history = os.getenv("HOURS_OF_HISTORY", "1")
    file_save_location = os.getenv("FILE_SAVE_LOCATION", os.getcwd())

    while True:
        print("\nSettings Menu:")
        print(f"1. API Key: {api_key}")
        print(f"2. Device ID: {device_id}")
        print(f"3. Hours of History: {hours_of_history}")
        print(f"4. File Save Location: {file_save_location}")
        print("5. Save and Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            api_key = input("Enter the new API key: ").strip()
        elif choice == "2":
            device_id = input("Enter the new Device ID: ").strip()
        elif choice == "3":
            hours_of_history = input("Enter the number of hours of history: ").strip()
        elif choice == "4":
            file_save_location = input("Enter the new file save location: ").strip()
        elif choice == "5":
            save_settings(api_key, device_id, hours_of_history, file_save_location)
            print("Settings saved. Exiting.")
            break
        else:
            print("Invalid option. Please choose again.")

def save_settings(api_key, device_id, hours_of_history, file_save_location):
    """Save updated settings to .env."""
    updates = {
        "WXM_API_KEY": api_key,
        "DEVICE_ID": device_id,
        "HOURS_OF_HISTORY": hours_of_history,
        "FILE_SAVE_LOCATION": file_save_location
    }

    with open(".env", "w") as env_file:
        for key, value in updates.items():
            env_file.write(f'{key}="{value}"\n')

    print("Settings have been updated successfully.")

if __name__ == "__main__":
    configure_settings()
