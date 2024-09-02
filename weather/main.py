from datetime import date, time, timedelta
from weather import get_road_sections, get_weather
from database import save_weather_data_to_database


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


if __name__ == "__main__":
    start_date = date(2023, 1, 1)
    end_date = date(2023, 10, 31)
    # get_weather_for_date_range(start_date, end_date)
    road_section_list = get_road_sections()

    # date loop
    current_date = start_date
    while current_date <= end_date:
        print(current_date)
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
                save_weather_data_to_database(f'{current_date.isoformat()} {current_time.isoformat()}', road_section.highway_name,
                                              road_section.mileage, weather['WDSD'], weather['Temp'], weather['HUMD'])
            print(current_time)
            current_time = next_time(current_time)
        current_date += timedelta(days=1)
