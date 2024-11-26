import pandas as pd
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from settings import get_units
from settings import configure_plot_period
from data_fetching import fetch_latest_weather_data

# Load environment variables
load_dotenv()

def get_plot_period():
    """
    Retrieve the chart plotting period from .env.
    """
    plot_period = os.getenv('PLOT_PERIOD_HOURS', '24')  # Default to 24 hours
    try:
        return int(plot_period)
    except ValueError:
        print(f"Invalid PLOT_PERIOD_HOURS value: {plot_period}. Defaulting to 24 hours.")
        return 24

def plot_precipitation(weather_records, num_hours=get_plot_period()):
    """
    Plot precipitation data from weather records using Plotly.

    Parameters:
    - weather_records: List of weather records (dicts) containing precipitation data.
    - num_hours: The number of hours to display data for, determining resampling granularity.
    """

    # Convert weather_records into a DataFrame for easier manipulation
    df = pd.DataFrame(weather_records,
                      columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])

    # Validate the input DataFrame
    if df.empty or 'Precipitation' not in df.columns:
        raise ValueError("No valid data found for precipitation chart.")

    # Convert the Timestamp column to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)

    # Convert Precipitation to numeric
    df['Precipitation'] = pd.to_numeric(df['Precipitation'], errors='coerce')

    # Get the preferred unit for precipitation from settings
    _, _, precipitation_unit, _ = get_units()
    print(f"DEBUG: Current precipitation unit: {precipitation_unit}")

    # Convert Precipitation to the correct unit
    if precipitation_unit.lower() == 'in':
        df['Precipitation'] = df['Precipitation'] / 25.4  # Convert mm to inches
        y_axis_title = "Precipitation (inches)"
    elif precipitation_unit.lower() == 'mm':
        y_axis_title = "Precipitation (mm)"
    else:
        precipitation_unit = 'mm'
        print("Invalid precipitation unit in settings. Defaulting to 'mm'.")
        y_axis_title = "Precipitation (mm)"

    # Resample data for readability if the range is too large
    if num_hours > 1440:  # More than 60 days of data
        df = df.set_index('Timestamp').resample('D').sum()  # Sum precipitation per day
        df.reset_index(inplace=True)

    # Create the bar chart
    fig = go.Figure()

    # Add the precipitation data as a bar trace
    fig.add_trace(go.Bar(
        x=df['Timestamp'],  # Use the resampled index or original timestamps
        y=df['Precipitation'],
        text=[f"{val:.2f}" if val > 0 else "" for val in df['Precipitation']],  # Show labels only for non-zero values
        textposition='outside',
        marker_color='blue',
        name="Precipitation"
    ))

    # Update layout for better readability
    fig.update_layout(
        title="Precipitation Data",
        xaxis_title="Date",
        yaxis_title=y_axis_title,
        xaxis=dict(
            tickangle=-45,
            showgrid=False,
            type="date"  # Ensure the x-axis is treated as a date axis
        ),
        yaxis=dict(
            range=[0, df['Precipitation'].max() * 1.25],  # Set y-axis range to 25% above the max value
            showgrid=True
        ),
        margin=dict(l=40, r=40, t=50, b=40),  # Adjust margins for better layout
        height=500,
        width=900,
        template="plotly_white"  # Use a clean and modern theme
    )

    # Save the chart as an HTML file
    output_file = os.getenv('OUTPUT_FILE', 'precipitation_chart.html')
    fig.write_html(output_file)
    print(f"Precipitation chart saved as '{output_file}'.")

if __name__ == "__main__":
    weather_records = fetch_latest_weather_data()
    plot_precipitation(weather_records, num_hours=24)
