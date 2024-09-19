# WeatherXM Python Playground

**WeatherXM Python Playground** is an open-source project designed to interact with WeatherXM's API. It allows users to fetch real-time weather data, retrieve device information, and manage their API keys. The project also includes functionality to configure units for temperature, wind speed, precipitation, and pressure, making it flexible for various use cases.

## Features
- **Fetch Weather Data**: Retrieve and display real-time weather data in a human-readable format.
- **Device Information**: Get detailed information about your WeatherXM station and devices.
- **API Key Management**: Automatically fetch and manage your WeatherXM API key.
- **Unit Settings**: Customize units for temperature (Celsius/Fahrenheit), wind speed (m/s or mph), precipitation (mm or inches), and pressure (hPa or mb).
- **User-friendly configuration**: Easily update settings like username, password, device ID, and API key through interactive prompts.

## Installation

To set up this project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/[YourUsername]/weatherxm-python-playground.git
cd weatherxm-python-playground
```

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
WXM_USERNAME="your_email_here"
WXM_PASSWORD="your_password_here"
WXM_API_KEY="your_api_key_here"
DEVICE_ID="your_device_id_here"
STATION_ID="your_station_id_here"
WALLET_ADDRESS="your_wallet_address_here"
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

## Contact

If you have any questions or need assistance, feel free to contact me at `matt0164@outlook.com`.

---

Enjoy the WeatherXM Python Playground! 🎉
