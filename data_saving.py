import os
import pandas as pd

SAVE_LOCATION = os.getenv('FILE_SAVE_LOCATION', os.getcwd())

def save_to_csv(data, filename="weather_data.csv"):
    """Saves weather data to a CSV file."""
    file_path = os.path.join(SAVE_LOCATION, filename)
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Data saved to: {file_path}")


def save_to_excel(data, filename="weather_data.xlsx"):
    """Saves weather data to an Excel file."""
    file_path = os.path.join(SAVE_LOCATION, filename)
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    print(f"Data saved to: {file_path}")
