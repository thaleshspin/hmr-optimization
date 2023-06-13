import json
import os
import random
from datetime import datetime, timedelta

from model.pig_iron_balance import Maintenance


def check_overlap(tuple1, tuple2):
    start1, end1 = tuple1
    start2, end2 = tuple2

    # Check if the intervals overlap
    if start1 <= end2 and start2 <= end1:
        return True  # Overlap exists
    else:
        return False  # No overlap


def generate_test_case(ct_name):
    filename = f'test_cases/{ct_name}.json'
    # if os.path.exists(filename):
    #     print('Skiping test case generation!')
    #     return None
    # Define the start and end time for the day
    start_time = datetime(2023, 6, 1, 0, 0, 0)
    end_time = datetime(2023, 7, 1, 0, 0, 0)

    # Define the time interval range between converters (1 hour to 1 hour 15 minutes)
    min_interval = timedelta(hours=1)
    max_interval = timedelta(hours=1, minutes=220)

    # Generate random converter start times
    converter_start_times = []
    current_time = start_time + timedelta(minutes=random.randint(50, 80))

    maintenances_cv1 = [{'time': (start_time.replace(second=0) + timedelta(days=5)).isoformat(), 'duration': 7*24}]
    # maintenances_cv1 = []
    converters_1 = []
    while current_time < end_time:
        # Generate a random start time for the converter
        converter_start = current_time
        interval = random.randint(min_interval.total_seconds(), max_interval.total_seconds())
        current_time += timedelta(seconds=interval)

        # Check if the converter start time overlaps with any maintenance duration
        overlap = False
        for maintenance in maintenances_cv1:
            start_maintenance = datetime.fromisoformat(maintenance['time'])
            end_maintenance = start_maintenance + timedelta(hours=maintenance['duration'])
            if converter_start <= end_maintenance and start_maintenance <= current_time:
                overlap = True
                break

        # Add the converter to the list only if there is no overlap with maintenance
        if not overlap:
            converter = {
                'time': converter_start.replace(second=0).isoformat(),
                'hmr': 0.8,
                'cv': 'cv_1'
                # Add other properties of the converter here
            }
            converters_1.append(converter)
    start_time = datetime(2023, 6, 1, 0, 0, 0)
    maintenances_cv2 = [{'time': (start_time.replace(second=0) + timedelta(hours=72)).isoformat(), 'duration': 24}]
    maintenances_cv2 = []
    converter_start_times_2 = []
    current_time = start_time + timedelta(minutes=random.randint(80, 95))
    converters_2 = []
    while current_time < end_time:
        # Generate a random start time for the converter
        converter_start = current_time
        interval = random.randint(min_interval.total_seconds(), max_interval.total_seconds())
        current_time += timedelta(seconds=interval)

        # Check if the converter start time overlaps with any maintenance duration
        overlap = False
        for maintenance in maintenances_cv2:
            start_maintenance = datetime.fromisoformat(maintenance['time'])
            end_maintenance = start_maintenance + timedelta(hours=maintenance['duration'])
            if converter_start <= end_maintenance and start_maintenance <= current_time:
                overlap = True
                break

        # Add the converter to the list only if there is no overlap with maintenance
        if not overlap:
            converter = {
                'time': converter_start.replace(second=0).isoformat(),
                'hmr': 0.8,
                'cv': 'cv_2'
                # Add other properties of the converter here
            }
            converters_2.append(converter)

    # Create the JSON object
    start_time = datetime(2023, 6, 1, 0, 0, 0)
    test_case = {

        "converter_1": converters_1,
        "converter_2": converters_2,
        "initial_conditions": {
            "time": start_time.isoformat(),
            "value": 1500
        },
        "pig_iron_hourly_production": 160,
        "max_restrictive": 2000,
        "allow_auto_spill_events": True,
        "converter_duration": 60,
        "optimize_hmr": True,
        "maintenances_cv1": maintenances_cv1,
        "maintenances_cv2": maintenances_cv2
    }
    # Save the data to a JSON file
    filename = f'test_cases/{ct_name}.json'
    # if os.path.exists(filename):
    #     raise Exception('Test case already exist')
    with open(filename, 'w') as file:
        json.dump(test_case, file, indent=4)

    print(f"JSON data has been saved to {filename}.")
