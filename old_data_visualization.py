import matplotlib.pyplot as plt
import pandas as pd


def plot_precipitation(weather_records, num_hours):
    # Convert weather_records into a DataFrame for easier manipulation
    df = pd.DataFrame(weather_records,
                      columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])

    # Convert the Timestamp column to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Precipitation'] = pd.to_numeric(df['Precipitation'], errors='coerce')

    # Set the Timestamp as the index
    df.set_index('Timestamp', inplace=True)

    # Plotting
    plt.figure(figsize=(10, 5))

    # Determine the x-axis labeling
    if num_hours > 1440:  # More than 60 days
        # Set monthly ticks
        ax = plt.gca()  # Get current axes
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Automatically manage ticks
        plt.xticks(pd.date_range(start=df.index.min(), end=df.index.max(), freq='MS'),
                   rotation=45)  # 'MS' means month start
    else:
        # Set daily ticks
        plt.xticks(rotation=45)

    plt.bar(df.index, df['Precipitation'], color='blue')
    plt.title('Precipitation Data')
    plt.xlabel('Date')
    plt.ylabel('Precipitation (inches)')

    # Set y-axis limit
    max_y = df['Precipitation'].max() * 1.25  # 25% higher than max
    plt.ylim(0, max_y)

    # Show data labels
    for i, v in enumerate(df['Precipitation']):
        plt.text(df.index[i], v + 0.1, str(v), ha='center', va='bottom')

    plt.tight_layout()  # Adjust layout to prevent clipping of tick-labels
    plt.show()
