import plotly.express as px
import pandas as pd


def plot_precipitation(weather_records, num_hours):
    # Convert weather_records into a DataFrame
    df = pd.DataFrame(weather_records,
                      columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])

    # Convert Timestamp column to datetime with UTC
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True, errors='coerce')
    df.set_index('Timestamp', inplace=True)  # Set the Timestamp as the index

    # Handle missing or invalid timestamps
    if df.index.isnull().any():
        print("Warning: Some timestamps are invalid and will be dropped.")
        df = df.dropna()

    # If num_hours is greater than 60 days, adjust x-axis labels for readability
    if num_hours > 1440:  # 60 days
        df = df.resample('D').sum()  # Resample data by day for readability
        tick_format = "%b %Y"  # Monthly labels if over 60 days
    else:
        tick_format = "%b %d"  # Daily labels if under 60 days

    # Create bar chart
    fig = px.bar(df, x=df.index, y='Precipitation', labels={'x': 'Date', 'Precipitation': 'Precipitation (inches)'},
                 title="Precipitation Data Over Time")

    # Set y-axis to start at 0 and be 25% higher than max precipitation value
    max_precip = df['Precipitation'].max() * 1.25
    fig.update_layout(yaxis=dict(range=[0, max_precip]), xaxis=dict(tickformat=tick_format))

    # Add labels for each bar
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')

    # Option to save as HTML and display
    fig.write_html("precipitation_chart.html")  # Save as an HTML file
    print("Plot saved as 'precipitation_chart.html'. Open this file in a browser to view.")
