# WeatherXM Python Playground

**WeatherXM Python Playground** is an open-source project designed to interact with WeatherXM's API. It allows users to fetch real-time weather data, retrieve device information, and manage their API keys. The project also includes functionality to configure units for temperature, wind speed, precipitation, and pressure, making it flexible for various use cases.

# Bug Roadmap
* The main bug I am aware of is that the settings file doesn't automatically run the script to fetch a new API key. Right now, you need to manually run fetch_api_key before running fetch_weather_data.py. Other bugs:
### [See ROADMAP.md for full bug list and feature roadmap](ROADMAP.md)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Support the Project
If you'd like to support this project by donating WXM or ETH, you can send your contributions to the following Arbitrum One wallet address:

0xdB81065a8A9B16FD07765CE0F75CeAc68CE167Fa

Alternatively, [click here to donate directly using MetaMask](https://metamask.app.link/send/0xdB81065a8A9B16FD07765CE0F75CeAc68CE167Fa?chain=arbitrum) or scan this QR code:

![Donate to My Project](donate_to_my_project.png)

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
# WeatherXM Configuration
WXM_USERNAME="youremail@domain.com"
WXM_PASSWORD="yourpasswordshouldalwaysbeasecret!"
WXM_API_KEY="your_api_key"
DEVICE_ID="5f96e380-1c7c-11ed-9972-4f669f2d96bd"
STATION_ID="Expert Pecan Twister"

# Units Configuration
TEMP_UNIT="F"
WIND_UNIT="mph"
PRECIP_UNIT="in"
PRESSURE_UNIT="mb"

# History Configuration
DAYS_OF_HISTORY="1"
HOURS_OF_HISTORY="3"

# File Configuration
FILE_SAVE_LOCATION="."

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

## Contact

If you have any questions or need assistance, feel free to contact me at `matt0164@outlook.com`.

---

Enjoy the WeatherXM Python Playground! 🎉
