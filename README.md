# WeatherXM Python Playground

**WeatherXM Python Playground** is an open-source project designed to interact with WeatherXM's API. It allows users to fetch real-time weather data, retrieve device information, and manage their API keys. The project also includes functionality to configure units for temperature, wind speed, precipitation, and pressure, making it flexible for various use cases.

## Features
- **Plot Precip**: New feature to plot precipitation and retreive the data from a saved file (for quicker display). Uses matlab.
- **Fetch Weather Data**: Retrieve and display real-time weather data in a human-readable format. Automatically re-runs the script with user-defined parameters.
- **Device Information**: Get detailed information about your WeatherXM station and devices.
- **API Key Management**: Automatically fetch and manage your WeatherXM API key, with automatic re-fetching if unauthorized.
- **Unit Settings**: Customize units for temperature (Celsius/Fahrenheit), wind speed (m/s or mph), precipitation (mm or inches), and pressure (hPa or mb).
- **User-friendly Configuration**: Easily update settings like username, password, device ID, and API key through interactive prompts.

## Bug Fixes (Added 2024-11-04)
- **24 Hours Bug**: Corrected bug which would prevent users from retreiving more than 48 hours of data
- **Sort Bug**: Corrected bug to sort data in decending date (most recent first)
  
## New Features and Bug Fixes (Added 2024-09-28)
- **Rerun Option**: After fetching weather data, users are prompted to rerun the script with a custom time period or exit.
- **Dynamic Time Period Selection**: Users can specify a custom number of hours for weather data retrieval.
- **Output Method Configuration**: Users can choose to display weather data in the terminal or save it as CSV or Excel.
- **File Save Location**: Users can specify the file save location through the settings menu.
- **Automatic API Key Fetching**: If the API key is missing or unauthorized, the script will automatically attempt to fetch a new key without manual intervention.
- **Default Weather Data**: The program will ask users if they want to run the fetch weather script from the settings.
- **Test Weather History Duration**: Users can select different time durations for fetching weather history.

### Bug Fixes
- Improved error handling for API requests.
- Corrected data extraction from the API response.
- Fixed output formatting issues in the terminal and CSV/Excel files.

## Pending Items

### Feature Roadmap
1. **Default Weather Data**: 
   - **Status**: Pending
   - **Description**: Ask the user if they want to run the fetch weather script from settings and prompt the user for the time period each time it runs.

2. **Test Weather History Duration**: 
   - **Status**: Pending
   - **Description**: Allow users to select days, weeks, months, or years of weather history and set defaults.

---

### Note
- Further enhancements will continue to improve user experience and functionality.


## Installation

To set up this project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/[YourUsername]/weatherxm-python-playground.git
cd weatherxm-python-playground

### 2. Create and Activate Virtual Environment

Create a virtual environment to manage project dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Required Packages

Install the project dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory. This file will hold your WeatherXM credentials and other required environment variables.

Example `.env` file:
```env
TEMPERATURE_UNIT=C # gets updated from settings.py
WIND_SPEED_UNIT=m/s # gets updated from settings.py
PRECIPITATION_UNIT=mm # gets updated from settings.py
PRESSURE_UNIT='mb'
WXM_API_KEY="your_api_key"
WXM_USERNAME='youremail@domain.com'
WXM_PASSWORD='yourpasswordshouldalwaysbeasecret!'
DEVICE_ID="5f96e380-1c7c-11ed-9972-4f669f2d96bd"
TEMP_UNIT='F'
WIND_UNIT='mph'
PRECIP_UNIT='in'
STATION_ID="Expert Pecan Twister"
DAYS_OF_HISTORY='1'
HOURS_OF_HISTORY='3'
```

These values will be automatically updated as you interact with the configuration script.

## Usage

### 1. Run the Settings Script

First, run the `settings.py` script to configure your environment variables such as API key, device ID, username, and units of measurement:

```bash
python settings.py
```

### 2. Fetch API Key

If you don't have an API key, or if you'd like to fetch a new one, run the `fetch_api_key.py` script:

```bash
python fetch_api_key.py
```

### 3. Get Device Information

To retrieve the details of your WeatherXM devices:

```bash
python get_station_id.py
```

### 4. Fetch Weather Data

Finally, to fetch weather data and display it in a table format:

```bash
python fetch_weather_data.py
```

You can customize the history dates or use default values to view real-time weather information.

## Contributing

Contributions are welcome! If you have any feature requests, bug reports, or general suggestions, feel free to open an issue or submit a pull request.

### Steps to Contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Support the Project
If you'd like to support this project by donating WXM tokens, you can send your contributions to the following wallet address:

WXM Token Donations (Arbitrum Network): 0xdB81065a8A9B16FD07765CE0F75CeAc68CE167Fa
Alternatively, [click here to donate directly using MetaMask](https://metamask.app.link/send/0xdB81065a8A9B16FD07765CE0F75CeAc68CE167Fa?chain=arbitrum).

## Contact

If you have any questions or need assistance, feel free to contact me at `matt0164@outlook.com`.

---

Enjoy the WeatherXM Python Playground! 🎉
