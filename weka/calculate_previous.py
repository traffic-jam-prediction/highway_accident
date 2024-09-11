import pandas as pd
from count_accident import count_road_accident
import numpy as np
from datetime import timedelta

def calculate_previous_N_min(row, group_data, N):
    N_minutes_ago = row['DateTime'] - timedelta(minutes=N)
    previous_row = group_data[group_data['DateTime'] == N_minutes_ago]
    # if not previous_row.empty:
    #     return previous_row['M03A_PCU'].values[0]
    if not previous_row.empty:
        if abs(previous_row['M03A_PCU'].values[0] - row['M03A_PCU']) < 50:
            return '無差異'
        else:
            return f'前 {N} 分鐘車流量差異大'
    else:
        return '無差異'


def calculate_previous():
    df = pd.read_csv('categorized_traffic_weather_6.csv', encoding='utf-8')
    df = df.drop(columns=['WindSpeed','Temperature','Humidity'])

    df['DateTime'] = pd.to_datetime(df['DateTime']) # Output: 2023-06-10 00:00:00
 
    df['Previous_10min'] = pd.Series([np.nan] * len(df), dtype=object)
    df['Previous_20min'] = pd.Series([np.nan] * len(df), dtype=object)
    i=0
    for (road_section, direction), group_data in df.groupby(['RoadSection', 'Direction']):
        i+=1
        group_data = group_data.sort_values(by='DateTime')
        for idx in group_data.index:
            row = group_data.loc[idx]
            df.at[idx, 'Previous_10min'] = calculate_previous_N_min(row, group_data, 10)
            df.at[idx, 'Previous_20min'] = calculate_previous_N_min(row, group_data, 20)
        print(f'{i}個路段已完成')

    df['DateTime'] = df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df