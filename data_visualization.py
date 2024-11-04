import matplotlib.pyplot as plt
import pandas as pd


def plot_precipitation(weather_records, num_hours):
    # Convert the weather records into a DataFrame for easy plotting
    df = pd.DataFrame(weather_records,
                      columns=["Timestamp", "Temperature", "Humidity", "Wind Speed", "Precipitation", "Pressure"])

    # Convert 'Timestamp' to datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Group by date to aggregate precipitation
    df['Date'] = df['Timestamp'].dt.date
    daily_precip = df.groupby('Date')['Precipitation'].sum()

    # Check if there is no precipitation data
    if daily_precip.sum() == 0:
        print(f"No precipitation over the last {num_hours} hours.")
        plt.figure(figsize=(10, 5))
        plt.text(0.5, 0.5, f"No precipitation over the last {num_hours} hours",
                 horizontalalignment='center', verticalalignment='center',
                 fontsize=14, bbox=dict(facecolor='red', alpha=0.5))
        plt.axis('off')  # Turn off the axis
        plt.title('Precipitation Data')
        plt.show()
        return

    # Plotting the precipitation data
    plt.figure(figsize=(10, 5))
    bars = daily_precip.plot(kind='bar', color='blue')

    # Adding data labels
    for bar in bars.patches:
        bars.annotate(f'{bar.get_height():.2f}',
                      (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                      ha='center', va='bottom')

    plt.title('Daily Precipitation')
    plt.xlabel('Date')
    plt.ylabel('Precipitation (inches)')

    # Dynamic y-axis scaling
    max_precip = daily_precip.max()  # Find the maximum precipitation
    if max_precip > 0:
        plt.ylim(0, int(max_precip * 1.25) + 1)  # Set the y-axis limit to 25% higher than max value, rounded up
    else:
        plt.ylim(0, 10)  # Fallback in case of no data

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
