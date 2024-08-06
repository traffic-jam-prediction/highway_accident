import pandas as pd
from roadsection_with_nearest import find_nearest_detection_points

def count_trafficvolume(main_df):
    # 為了保留原始資料路段的排序順序(才能呈現由北到南的順序)
    data1 = find_nearest_detection_points()
    original_order = data1['roadsection'].unique().tolist()
    
    count_file = pd.DataFrame(columns=['RoadSection','Direction','M03A_PCU'])
    for (road_section, direction), group_data in main_df.groupby(['RoadSection', 'Direction']):
        count_pcu = group_data['M03A_PCU'].sum()
        RoadSection = group_data['RoadSection'].values[0] 
        Direction = group_data['Direction'].values[0]
        count_file = pd.concat([count_file, pd.DataFrame({'RoadSection': [RoadSection],'Direction':[Direction],'M03A_PCU':[count_pcu]})])
    
    count_file = count_file.sort_values(by=['RoadSection'], key=lambda x: x.map({v: i for i, v in enumerate(original_order)}))
    count_file.to_csv('count_file.csv', index=False, encoding='utf-8-sig')
    print("數據已保存到 'count_file.csv'")

print("traffic data csv file name: ", end="")
traffic_data_file = input()
df = pd.read_csv(traffic_data_file)
count_trafficvolume(df)