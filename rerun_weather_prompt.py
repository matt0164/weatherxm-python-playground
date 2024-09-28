import sys
def prompt_rerun(fetch_weather_data):
    while True:
        choice = input("If you would like to rerun the weather script, enter the number of hours of weather history you'd like to fetch (or enter 'no' to exit): ").strip().lower()
        if choice == 'no':
            print("Exiting the script.")
            sys.exit()  # Exit the script properly
        else:
            try:
                num_hours = int(choice)
                fetch_weather_data(num_hours)
            except ValueError:
                print("Invalid input. Please enter a valid number or 'no' to exit.")

def get_new_time_period():
    while True:
        try:
            hours = int(input("Enter the number of hours of weather history you'd like to fetch: ").strip())
            return hours
        except ValueError:
            print("Invalid input. Please enter a valid number.")
