from datetime import datetime


def convert_dates_to_datetime(obj):
    if isinstance(obj, list):
        return [convert_dates_to_datetime(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_dates_to_datetime(value) for key, value in obj.items()}
    elif isinstance(obj, str):
        try:
            return datetime.strptime(obj, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return obj
    return obj
