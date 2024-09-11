import pandas as pd
from count_accident import count_road_accident
import numpy as np
from datetime import timedelta
from calculate_previous import calculate_previous

def categorize_traffic_volume(pcu):
    if pcu < 450:
        return "低流量"
    elif pcu >= 450:
        return "高流量"
    
def categorize_speed(speed):
    if speed < 80:
        return "車速慢"
    elif speed >= 80:
        return "車速快"
    
def categorize_time_1(dt):
    if 0 <= dt.hour < 6:
        return '0-6'
    elif 6 <= dt.hour < 9:
        return '6-9'
    elif 9 <= dt.hour < 12:
        return '9-12'
    elif 12 <= dt.hour < 15:
        return '12-15'
    elif 15 <= dt.hour < 18:
        return '15-18'
    elif 18 <= dt.hour < 21:
        return '18-21'
    elif 21 <= dt.hour < 24:
        return '21-24'
def categorize_time_2(dt):
    if 7 <= dt.hour < 10:
        return '晨間尖峰'
    elif 17 <= dt.hour < 20:
        return '晚間尖峰'
    else:
        return '離峰'
    
def categorize_accident(row): 
    road_section = row['RoadSection'] + " " + row['Direction']
    return accident_dict.get(road_section)


if __name__ == '__main__':

    # df 中 previous_10_min &  previous_20_min 欄位已被填入
    df = calculate_previous()
    high_traffic_df = df.copy()

    # pcu
    high_traffic_df['M03A_PCU'] = high_traffic_df['M03A_PCU'].apply(categorize_traffic_volume)
    high_traffic_df['M05A_PCU'] = high_traffic_df['M05A_PCU'].apply(categorize_traffic_volume)

    # speed
    high_traffic_df.loc[:, 'Speed'] = high_traffic_df['M05A_SpaceMeanSpeed'].apply(categorize_speed)
    high_traffic_df.drop(['M05A_SpaceMeanSpeed'], axis=1, inplace=True)

    # accident
    accident = pd.read_csv('count.csv')
    accident_dict = dict(zip(accident['RoadSection'], accident['Accident_Risk']))
    high_traffic_df['Accident'] = high_traffic_df.apply(categorize_accident, axis=1).astype(str)

    # Holiday or weekday
    high_traffic_df['Week'] = high_traffic_df['Week'].apply(lambda x: '平日' if x in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] else '假日').astype(str)

    # biggap
    high_traffic_df['M03A_PCU_BigGap'] = high_traffic_df['M03A_PCU_BigGap'].apply(lambda x: '差異大' if x == 1 else '差異小').astype(str)

    # holiday
    high_traffic_df['Holiday'] = high_traffic_df['Holiday'].apply(lambda x: '放假' if x == 1 else '無放假').astype(str)

    # time
    high_traffic_df['DateTime'] = pd.to_datetime(high_traffic_df['DateTime']) # Output: 2023-06-10 00:00:00
    high_traffic_df['DateTime_1'] = high_traffic_df['DateTime'].apply(categorize_time_1)
    high_traffic_df['DateTime_2'] = high_traffic_df['DateTime'].apply(categorize_time_2)
    high_traffic_df = high_traffic_df.drop(columns=['DateTime'])

    high_traffic_df.to_csv('integrate_categorized_data.csv', encoding='utf-8-sig', index=False)
    print('.csv檔案已生成')



