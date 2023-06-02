import json
import random
from datetime import datetime, timedelta


def generate_test_case():
    # Define the start and end time for the day
    start_time = datetime(2023, 6, 2, 0, 0, 0)
    end_time = datetime(2023, 6, 2, 23, 59, 59)

    # Define the time interval range between converters (1 hour to 1 hour 15 minutes)
    min_interval = timedelta(hours=1)
    max_interval = timedelta(hours=1, minutes=90)

    # Generate random converter start times
    converter_start_times = []
    current_time = start_time + timedelta(minutes=15)

    while current_time < end_time:
        converter_start_times.append(current_time)
        interval = random.randint(min_interval.total_seconds(), max_interval.total_seconds())
        current_time += timedelta(seconds=interval)

    # Create a list of converter objects
    converters_1 = []
    for start_time in converter_start_times:
        converter = {
            'time': start_time.isoformat(),
            'hmr': 0.8,
            'cv': 'cv_1'
            # Add other properties of the converter here
        }
        converters_1.append(converter)
    start_time = datetime(2023, 6, 2, 0, 0, 0)
    converter_start_times_2 = []
    current_time = start_time + timedelta(minutes=36)

    while current_time < end_time:
        converter_start_times_2.append(current_time)
        interval = random.randint(min_interval.total_seconds(), max_interval.total_seconds())
        current_time += timedelta(seconds=interval)

    # Create a list of converter objects
    converters_2 = []
    for start_time in converter_start_times_2:
        converter = {
            'time': start_time.isoformat(),
            'hmr': 0.8,
            'cv': 'cv_2'
            # Add other properties of the converter here
        }
        converters_2.append(converter)

    # Create the JSON object
    test_case = {
        "initial_conditions": {
            "time": start_time.isoformat(),
            "value": 1600
        },
        "converter_1": converters_1,
        "converter_2": converters_2,
        "pig_iron_hourly_production": 470,
        "max_restrictive": 2000,
        "allow_auto_spill_events": True,
        "converter_duration": 60
    }
    # Save the data to a JSON file
    filename = 'test_cases/test_case.json'
    with open(filename, 'w') as file:
        json.dump(test_case, file, indent=4)

    print(f"JSON data has been saved to {filename}.")


if __name__ == '__main__':
    generate_test_case()