from datetime import date, time, datetime, timedelta
from enum import Enum
import csv
import os
from typing import List
from tdx_api import get_data, get_data_and_save_to_json
from location import get_mileage_GPS, haversine_distance
from file import write_json_to_file, read_json_file, write_list_to_file
from database import add_data

VALUE_NOT_FOUND = -99.0


class WeatherStationType(Enum):
    automatic_weather_station = "AWS"
    central_weather_station = "CWS"


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
    if time_1 == time_3:
        return value_1
    
    if value_1 == VALUE_NOT_FOUND and value_3 == VALUE_NOT_FOUND:
        return VALUE_NOT_FOUND
    elif value_3 == VALUE_NOT_FOUND:
        return value_1
    elif value_1 == VALUE_NOT_FOUND:
        return value_3
    else:
        time_distance_between_1_and_2 = time_2 - time_1
        time_total_distance = time_3 - time_1
        value_base = value_1
        value_total_distance = value_3 - value_1
        value_2 = value_base + value_total_distance * \
            time_distance_between_1_and_2/time_total_distance
        return round(value_2, 3)


def get_weather_for_date(target_date: date):
    date_string = target_date.isoformat()
    year = target_date.year
    month = target_date.month
    folder_path = f'history/{year}/{month}'
    json_file_path = f'{folder_path}/{date_string}.json'
    if not os.path.exists(json_file_path):
        # get data from api
        weather_data = list()
        for station_type in WeatherStationType:
            weather_station_type = station_type.value
            maximum_station_amount = 2000
            weather_api_url = f"https://tdx.transportdata.tw/api/historical/v1/Weather/Observation/{weather_station_type}?Dates={date_string}&$format=json&$top={maximum_station_amount*24}"
            weather_data_for_station_type = get_data(api_url=weather_api_url)
            weather_data.extend(weather_data_for_station_type)

        # save to file
        os.makedirs(folder_path, exist_ok=True)
        write_json_to_file(json_file_path, weather_data)
    else:
        file_path = f'history/{year}/{month}/{date_string}.json'
        return read_json_file(file_path)


def find_closest_station_weather(weather_data: list, mileage_position: tuple) -> int:
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
    return closest_weather


def find_first_weather(weather_data: list) -> dict:
    first_index = None
    for index, weather in enumerate(weather_data):
        minutes = weather_to_minutes(weather)
        if first_index == None or minutes < weather_to_minutes(weather_data[first_index]):
            first_index = index
    return weather_data[first_index]


def get_weather(target_date: date, time_string: str, highway_name: str, mileage: float):
    road_section_position = get_road_section_position()
    mileage_position = road_section_position[highway_name][str(mileage)]

    weather_data = get_weather_for_date(target_date)
    closest_weather = find_closest_station_weather(
        weather_data, mileage_position)

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

    after_weather = None
    if after_index == None:
        tomorrow_weather = get_weather_for_date(
            target_date + timedelta(days=1))
        tomorrow_closest_weather = find_closest_station_weather(
            weather_data, mileage_position)
        after_weather = find_first_weather(tomorrow_closest_weather)
    else:
        after_weather = closest_weather[after_index]
    target_weather = [closest_weather[before_index],
                      after_weather]

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
        if (int(value) == -99):
            value = int(-99)
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


def get_weather_for_date_range(start_date: date, end_date: date):
    current_date = start_date
    while current_date <= end_date:
        get_weather_for_date(current_date)
        current_date += timedelta(days=1)


class RoadSection:
    def __init__(self, highway_name, mileage):
        self.highway_name = highway_name
        self.mileage = mileage


def get_road_sections() -> List[RoadSection]:
    road_section_list = []
    with open('roadsectiondata_with_nearest.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        attributes = next(csvreader)
        highway_index = attributes.index('highway')
        mileage_index = attributes.index('midpoint')
        for row in csvreader:
            highway = row[highway_index]
            if highway == "國道1號_高架":
                continue
            mileage = float(row[mileage_index])
            new_road_section = RoadSection(highway, mileage)
            road_section_list.append(new_road_section)
    return road_section_list


def get_road_section_position() -> dict:
    road_section_list = get_road_sections()
    road_section_position_file = "road_section_position.json"
    road_section_position = read_json_file(road_section_position_file)
    for road_section in road_section_list:
        highway = road_section.highway_name
        mileage = road_section.mileage
        if highway in road_section_position and str(mileage) in road_section_position[highway]:
            continue

        print(highway, mileage)
        position = get_mileage_GPS(highway, mileage)
        if not highway in road_section_position:
            road_section_position[highway] = dict()
        road_section_position[highway][mileage] = list(position)
        write_list_to_file(road_section_position, road_section_position)
        time.sleep(1)
    return road_section_position


if __name__ == "__main__":
    start_date = date(2023, 1, 1)
    end_date = date(2023, 10, 31)
    # get_weather_for_date_range(start_date, end_date)
    road_section_list = get_road_sections()

    # date loop
    current_date = start_date
    while current_date <= end_date:
        # time loop
        start_time = time(0, 0)
        end_time = time(23, 55)
        current_time = start_time
        while current_time <= end_time:
            time_string = current_time.strftime("%H:%M")
            # road section loop
            for road_section in road_section_list:
                weather = get_weather(
                    current_date, time_string, road_section.highway_name, road_section.mileage)
                add_data(current_date.isoformat(), current_time.isoformat(), road_section.highway_name,
                      road_section.mileage, weather['WDSD'], weather['Temp'], weather['HUMD'], weather['PRES'])
            current_time = next_time(current_time)
        current_date += timedelta(days=1)
