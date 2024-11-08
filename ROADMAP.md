# WeatherXM Python Playground Feature and Bug Roadmap

## Bug & Feature Roadmap
### The main bug I am aware of is that the settings file doesn't automatically run the script to fetch a new API key. Right now, you need to manually run fetch_api_key before running fetch_weather_data.py. 
### Other bugs: 

1. **Error in fetching new API key due to missing requests module**: Ensure the requests library is properly imported and available in the environment.
2. **Error when running fetch_weather_data script from settings.py**: The script raises a `ModuleNotFoundError` for the requests module when executed.
3. **Unauthorized Access Error Handling**: Ensure that when a 401 error occurs, the application automatically fetches a new API key and retries the request.

### Current Features
- **Fetch Weather Data**: Retrieve and display real-time weather data in a human-readable format. Automatically re-runs the script with user-defined parameters.
- **Plot Precip**: New feature to plot precipitation and retreive the data from a saved file (for quicker display). Uses matlab.
- **Device Information**: Get detailed information about your WeatherXM station and devices.
- **API Key Management**: Automatically fetch and manage your WeatherXM API key, with automatic re-fetching if unauthorized.
- **Unit Settings**: Customize units for temperature (Celsius/Fahrenheit), wind speed (m/s or mph), precipitation (mm or inches), and pressure (hPa or mb).
- **User-friendly Configuration**: Easily update settings like username, password, device ID, and API key through interactive prompts.
- **Output Method Configuration**: Added a configuration to select output methods (print to terminal, download Excel, download CSV). Default to CSV for more than 7 days of history.

### Features Roadmap
1. **Data Visualization**: Integrate data visualization tools to graphically represent weather data trends over time.
   - Improve quality of charting/graphics using other libraries or third-party tools like Tableau or similar free options.
   - Create data visualization scripts to plot other data elements (e.g., temperature, humidity, etc.).
2. **File Save Location**: Allow users to specify the file save location in the config menu.
3. **Automatic API Key Fetching**: Automatically run the `fetch_api_key.py` script in `fetch_weather_data.py` if an unauthorized error is encountered.
4. **Create a GUI**: Add a graphical user interface leveraging a package like Kivy or completely rebasing code in javascript in a framework like react
5. **User Authentication Management**: Add functionality to manage user authentication more securely, possibly integrating OAuth.
5. **Notifications for Data Updates**: Implement a notification system that alerts users when new data is available or when certain thresholds are met.
6. **Export Options**: Provide additional formats for data export, such as JSON or XML.
7. **API Rate Limiting Handling**: Implement logic to handle API rate limits gracefully, with user notifications.
8. **Error Handling Improvements**: Review and enhance error handling throughout the application for a better user experience.
9. **Performance Optimization**: Analyze the performance of the application and optimize any bottlenecks, particularly in data fetching and processing.
10. **Custom Recommendations**: Suggest clothing or actions based on the most recent hour of data.
11. **Documentation Updates**: Regularly update the documentation to reflect new features, changes, and usage examples.

## Release Notes:

### 2024-11-08
- **Data Fetching Bug**: When fetching data for periods longer than 2 days, the API returns repeated data from the last day.- **24 Hours Bug**: Corrected bug which would prevent users from retreiving more than 48 hours of data
- **Sort Bug**: Corrected bug to sort data in decending date (most recent first)

### 2024-11-04
- **24 Hours Bug**: Corrected bug which would prevent users from retreiving more than 48 hours of data
- **Sort Bug**: Corrected bug to sort data in decending date (most recent first)
- **Improved error handling for API requests.
- **Corrected data extraction from the API response.
- **Fixed output formatting issues in the terminal and CSV/Excel files.

### 2024-09-28
- **Rerun Option**: After fetching weather data, users are prompted to rerun the script with a custom time period or exit.
- **Dynamic Time Period Selection**: Users can specify a custom number of hours for weather data retrieval.
- **Output Method Configuration**: Users can choose to display weather data in the terminal or save it as CSV or Excel.
- **File Save Location**: Users can specify the file save location through the settings menu.
- **Automatic API Key Fetching**: If the API key is missing or unauthorized, the script will automatically attempt to fetch a new key without manual intervention.
- **Default Weather Data**: The program will ask users if they want to run the fetch weather script from the settings.
- **Test Weather History Duration**: Users can select different time durations for fetching weather history.