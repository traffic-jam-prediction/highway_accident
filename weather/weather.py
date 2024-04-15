from datetime import date, time, datetime, timedelta
import sys
from enum import Enum
from tdx_api import get_data, get_data_and_save_to_json
from location import get_mileage_GPS, haversine_distance


class WeatherStationType(Enum):
    automatic_weather_station = "AWS"
    central_weather_station = "CWS"


def date_is_ISO_format(date_string: str) -> bool:
    try:
        target_date = date.fromisoformat(date_string)
    except ValueError:
        print(f"ERROR: {date_string} isn't a valid ISO format date!")
        return False
    return True


def time_is_ISO_format(time_string: str) -> bool:
    try:
        target_time = time.fromisoformat(time_string)
    except ValueError:
        print(f"ERROR: {time_string} isn't a valid ISO format time!")
        return False
    return True


def time_to_minutes(time_str: str) -> int:
    """Convert time string to minutes since midnight."""
    time_obj = None
    try:
        time_obj = datetime.strptime(time_str, "%H:%M:%S")
    except ValueError:
        time_obj = datetime.strptime(time_str, "%H:%M")
    return time_obj.hour * 60 + time_obj.minute


def weather_to_minutes(weather: dict) -> int:
    date_and_time = weather["ObsTime"]
    time_string = date_and_time.split(" ")[1]
    return time_to_minutes(time_string)


def interpolation(time_1: int, value_1: float, time_2: int,  time_3: int, value_3: float) -> float:
    time_distance_between_1_and_2 = time_2 - time_1
    time_total_distance = time_3 - time_1
    value_base = value_1
    value_total_distance = value_3 - value_1
    value_2 = value_base + value_total_distance * \
        time_distance_between_1_and_2/time_total_distance
    return value_2


def get_weather(date_string: str, time_string: str, mileage: float):

    if (not date_is_ISO_format(date_string) or (not time_is_ISO_format(time_string))):
        sys.exit()
    mileage_position = get_mileage_GPS("國道1號", mileage)

    # get weather from both automatic-weather-stations and central-weather-stations
    weather_data = list()
    for station_type in WeatherStationType:
        weather_station_type = station_type.value
        maximum_station_amount = 2000
        weather_api_url = f"https://tdx.transportdata.tw/api/historical/v1/Weather/Observation/{weather_station_type}?Dates={date_string}&$format=json&$top={maximum_station_amount*24}"
        weather_data_for_station_type = get_data(api_url=weather_api_url)
        weather_data.extend(weather_data_for_station_type)

    # filter weather based on the closest station
    shortest_distance = float("inf")
    for index, weather in enumerate(weather_data):
        weather_station_position = (weather["Lat"], weather["Lon"])
        current_distance = haversine_distance(
            mileage_position, weather_station_position)
        if current_distance < shortest_distance:
            shortest_distance = current_distance
            weather_index = index
    closest_station_id = weather_data[weather_index]["StationID"]
    closest_weather = list()
    for weather in weather_data:
        current_station_id = weather["StationID"]
        if current_station_id == closest_station_id:
            closest_weather.append(weather)

    # filter weather to the closest time
    target_minute = time_to_minutes(time_string)
    after_index = None
    before_index = None
    for index, weather in enumerate(closest_weather):
        current_minute = weather_to_minutes(weather)

        if current_minute >= target_minute and (after_index is None or current_minute < weather_to_minutes(closest_weather[after_index])):
            after_index = index
        if current_minute <= target_minute and (before_index is None or current_minute > weather_to_minutes(closest_weather[before_index])):
            before_index = index
    target_weather = [closest_weather[before_index],
                      closest_weather[after_index]]

    # interpolation
    target_time_weather = dict()
    required_attributes = ["WDSD", "Temp", "HUMD", "PRES"]
    for attribute in required_attributes:
        start_weather = target_weather[0]
        end_weather = target_weather[1]
        start_time = weather_to_minutes(start_weather)
        end_time = weather_to_minutes(end_weather)
        value = interpolation(
            time_1=start_time, value_1=start_weather[attribute], time_2=target_minute, time_3=end_time, value_3=end_weather[attribute])
        target_time_weather[attribute] = value
    return target_time_weather


def next_time(current_time: time) -> time:
    new_hour = current_time.hour
    new_minute = None
    if current_time.minute == 55:
        new_minute = 0
        if new_hour == 23:
            return time(23, 59)
        else:
            new_hour += 1
    else:
        new_minute = current_time.minute + 5
    return time(hour=new_hour, minute=new_minute)


# if __name__ == "__main__":
#     # date loop
#     start_date = date(2023, 1, 1)
#     end_date = date(2023, 10, 31)
#     current_date = start_date
#     while current_date <= end_date:
#         current_date += timedelta(days=1)
#         # time loop
#         start_time = time(0, 0)
#         end_time = time(23, 55)
#         current_time = start_time
#         while current_time <= end_time:
#             time_string = current_time.strftime("%H:%M")
#             current_time = next_time(current_time)
#             # road section
#             print(get_weather(current_date, time_string, 3.5))