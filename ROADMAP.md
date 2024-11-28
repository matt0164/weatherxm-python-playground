# WeatherXM Python Playground Feature and Bug Roadmap

## Bug & Feature Roadmap

### Bugs

1. **Unauthorized Access Error Handling**: Ensure that when a `401 Unauthorized` error occurs, the application automatically fetches a new API key and retries the request.
2. **Historical Data Handling**: Ensure that if multiple devices are used, historical data from one device is cleared when switching to another to avoid data mixing.
3. **Long Function Complexity**: Break up the `fetch_weather_data` function into smaller, modular components for better readability and maintainability.
4. **Environment Variable Consistency**: Ensure all variables (e.g., username, password, device ID) are stored in the `.env` file and loaded dynamically.
5. **Unnecessary API Calls**: Avoid fetching already saved data from the API. When a user requests a specific range of data, only fetch and append new data to the CSV.
6. **Initial Configuration Workflow**: Add logic for initial setup (e.g., username, password, and base data fetch). These settings should only appear in a separate "Initial Configuration" menu after setup.

---

### Current Features

- **Fetch Weather Data**: Retrieve and display real-time weather data in a human-readable format. Automatically re-runs the script with user-defined parameters.
- **Plot Precipitation**: New feature to plot precipitation and retrieve the data from a saved file (for quicker display). Uses `matplotlib`.
- **Device Information**: Get detailed information about your WeatherXM station and devices.
- **API Key Management**: Automatically fetch and manage your WeatherXM API key, with automatic re-fetching if unauthorized.
- **Unit Settings**: Customize units for temperature (Celsius/Fahrenheit), wind speed (m/s or mph), precipitation (mm or inches), and pressure (hPa or mb).
- **User-Friendly Configuration**: Easily update settings like username, password, device ID, and API key through interactive prompts.
- **Output Method Configuration**: Added a configuration to select output methods (print to terminal, download Excel, download CSV). Default to CSV for more than 7 days of history.

---

### Features Roadmap

1. **Data Visualization**: Integrate data visualization tools to graphically represent weather data trends over time.
   - Improve quality of charting/graphics using advanced libraries like `plotly` or `seaborn`.
   - Create data visualization scripts to plot additional data elements (e.g., temperature, humidity, etc.).
2. **File Save Location**: Allow users to specify the file save location in the config menu.
3. **Automatic API Key Fetching**: Automatically run the `fetch_api_key.py` script in `fetch_weather_data.py` if an unauthorized error is encountered.
4. **Create a GUI**: Add a graphical user interface using tools like `Kivy` or rebase the project using React or another web framework.
5. **User Authentication Management**: Add functionality to manage user authentication more securely, possibly integrating OAuth.
6. **Notifications for Data Updates**: Implement a notification system that alerts users when new data is available or when certain thresholds are met.
7. **Export Options**: Provide additional formats for data export, such as JSON or XML.
8. **API Rate Limiting Handling**: Implement logic to handle API rate limits gracefully, with user notifications.
9. **Error Handling Improvements**: Review and enhance error handling throughout the application for a better user experience.
10. **Performance Optimization**: Analyze the performance of the application and optimize any bottlenecks, particularly in data fetching and processing.
11. **Custom Recommendations**: Suggest clothing or actions based on the most recent hour of data.
12. **Documentation Updates**: Regularly update the documentation to reflect new features, changes, and usage examples.

---

## Release Notes


### 2024-11-28

### Created Separate Modules:
- **data_saving.py**: Handles saving data to CSV and Excel files.
- **data_loading.py**: Manages loading existing data from files and checking for new data requirements.
- **api_requests.py**: Handles API requests, including login, fetching the device ID, and fetching weather data.
- **config.py**: Manages configurations like API key, device ID, and environment variable loading.


- **Core Functionality in fetch_weather_data.py:**

  - ***Determining the range of data to fetch based on existing data.***
  - ***Fetching the data using api_requests.py.***
  - ***Saving the new data using data_saving.py.***

### 2024-11-27
- **Modularization**: Began breaking up `fetch_weather_data` into smaller functions for modularity.
- **Unauthorized Error Handling**: Improved handling of `401 Unauthorized` errors with automatic retries after fetching a new API key.
- **CSV Optimization**: Logic added to check existing data in the CSV file and only fetch new data when requested.
- **Initial Configuration Workflow**: Added initial setup for username, password, and base data fetch, nested under a separate configuration menu.

### 2024-11-09
- **Fixed API Key Error**: Resolved issues with fetching a new API key due to a missing `requests` module.
- **ModuleNotFoundError**: Fixed error when running the `fetch_weather_data` script from `settings.py`.

### 2024-11-08
- **Data Fetching Bug**: Corrected repeated data being fetched for overlapping time ranges.
- **Sort Bug**: Fixed sorting to display the most recent data first.

### 2024-09-28
- **Rerun Option**: Prompted users to rerun the script with custom time periods or exit.
- **Dynamic Time Period Selection**: Allowed users to specify a custom number of hours for data retrieval.
- **Default Weather Data**: Asked users whether they wanted to run the fetch weather script directly from settings.
