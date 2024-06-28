import pandas as pd
from count_accident import count_road_accident
import numpy as np
from datetime import timedelta
    
def categorize_traffic_volume(pcu):
    if pcu < 250:
        return '超低流量'
    elif 250 <= pcu < 350:
        return '低流量'
    elif 350 <= pcu < 450:
        return '中流量'
    elif 450 <= pcu < 550:
        return '高流量'
    elif pcu >= 550:
        return '超高流量'
    
def categorize_speed(speed):
    if speed>=90:
        return '車速快'
    elif 80<=speed<90:
        return '車速稍慢'
    elif 60<=speed<80:
        return '車速慢'
    elif speed<60:
        return '車速非常慢'

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
    
def classify_time(dt):
    # 06:00-09:00
    if dt.hour >= 6 and dt.hour < 9:
        return '晨間尖峰'
    # 16:00-19:30
    elif (dt.hour >= 16 and dt.hour < 19) or (dt.hour == 19 and dt.minute <= 30):
        return '晚間尖峰'
    # 09:00-16:00
    elif dt.hour >= 9 and dt.hour < 16:
        return '白天離峰'
    # 19:30-21:00
    elif (dt.hour >= 19 and dt.hour < 21) or (dt.hour == 19 and dt.minute > 30 ):
        return '晚間離峰'
    else:
        return '夜間'

def categorize_accident(row): 
    road_section = row['RoadSection'] + row['Direction']
    return accident_dict.get(road_section)


if __name__ == '__main__':
    df = pd.read_csv('main06.csv', encoding='utf-8')
    
    # speed
    df['Speed'] = df['M05A_SpaceMeanSpeed'].apply(categorize_speed)
    df = df.drop(['M05A_SpaceMeanSpeed'], axis=1)
    # accident
    accident_dict = count_road_accident()
    df['Accident'] = df[['RoadSection', 'Direction']].apply(categorize_accident, axis=1)
    # Holiday or weekday
    df['Week'] = df['Week'].apply(lambda x: '平日' if x in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] else '假日')
    # biggap
    df['M03A_PCU_BigGap'] = df['M03A_PCU_BigGap'].apply(lambda x: '前後交通量差異大' if x==1 else '差異小')

    # time
    df['DateTime'] = pd.to_datetime(df['DateTime']) # Output: 2023-06-10 00:00:00
    # previous_N_min
    df['Previous_10min'] = pd.Series([np.nan] * len(df), dtype=object)
    df['Previous_20min'] = pd.Series([np.nan] * len(df), dtype=object)
    for (road_section, direction), group_data in df.groupby(['RoadSection', 'Direction']):
        group_data = group_data.sort_values(by='DateTime')
        for idx in group_data.index:
            row = group_data.loc[idx]
            df.at[idx, 'Previous_10min'] = calculate_previous_N_min(row, group_data, 10)
            df.at[idx, 'Previous_20min'] = calculate_previous_N_min(row, group_data, 20)
        print('一個路段已完成')
    df['DateTime'] = df['DateTime'].apply(classify_time)

    # traffic_volume
    df['M03A_PCU'] = df['M03A_PCU'].apply(categorize_traffic_volume)
    df['M05A_PCU'] = df['M05A_PCU'].apply(categorize_traffic_volume)

    
    df.to_csv('nominal_diff50.csv', encoding='utf-8-sig', index=False)
    print(df.head())
