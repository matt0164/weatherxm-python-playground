import pandas as pd
import plotly.graph_objects as go
from settings import get_units  # Import unit settings function

def plot_precipitation(weather_records, num_hours):
    # Convert weather_records into a DataFrame for easier manipulation
    df = pd.DataFrame(weather_records,
                      columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])

    # Convert the Timestamp column to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)

    # Convert Precipitation to numeric
    df['Precipitation'] = pd.to_numeric(df['Precipitation'], errors='coerce')

    # Get the preferred unit for precipitation from settings
    _, _, precipitation_unit, _ = get_units()

    # Convert Precipitation to the correct unit
    if precipitation_unit == 'in':
        df['Precipitation'] = df['Precipitation'] / 25.4  # Convert mm to inches
        y_axis_title = "Precipitation (inches)"
    else:
        y_axis_title = "Precipitation (mm)"

    # Resample data by day if the range is too large for detailed plotting
    if num_hours > 1440:  # More than 60 days
        df = df.resample('D', on='Timestamp').sum()  # Sum precipitation per day

    # Create the bar chart
    fig = go.Figure()

    # Add the precipitation data as a bar trace
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Precipitation'],
        text=[f"{val:.2f}" if val > 0 else "" for val in df['Precipitation']],  # Show labels only for non-zero values
        textposition='outside',
        marker_color='blue'
    ))

    # Update layout for better readability
    fig.update_layout(
        title="Precipitation Data",
        xaxis_title="Date",
        yaxis_title=y_axis_title,
        xaxis=dict(
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            range=[0, df['Precipitation'].max() * 1.25],  # Set y-axis range to 25% above the max value
            showgrid=True
        ),
        margin=dict(l=40, r=40, t=50, b=40),  # Adjust margins
        height=500,
        width=900
    )

    # Save the chart as an HTML file
    fig.write_html("precipitation_chart.html")
    print("Precipitation chart saved as 'precipitation_chart.html'.")
