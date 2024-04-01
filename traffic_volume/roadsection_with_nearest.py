import pandas as pd
import json

csv_file = 'C:\\Users\\julia\\Desktop\\交通局\\TDCS_M03A_20240227_153500.csv'

def get_highway_midpoint():
    highway1 = pd.read_csv('../highway_information/國道1號.csv', encoding='utf-8')
    highway1_h = pd.read_csv('../highway_information/國道1號_高架.csv', encoding='utf-8')
    highway3 = pd.read_csv('../highway_information/國道3號.csv', encoding='utf-8')
    highway5 = pd.read_csv('../highway_information/國道5號.csv', encoding='utf-8')
    new_df = pd.DataFrame(columns=['roadsection', 'highway','direction','midpoint', 'from_mil', 'to_mil'])

    for index, row in highway1.iterrows():
        # 確保不是最後一個索引
        if index < len(highway1) - 1:
            from_mil = row['里程K+000']
            to_mil = highway1.loc[index + 1, '里程K+000']
            midpoint = (from_mil + to_mil) / 2  # 計算里程的平均值
            roadsection = f"{highway1.loc[index , '設施名稱']}-{highway1.loc[index+1 , '設施名稱']}"
        
            # 如果新 DataFrame 是空的，直接添加新的數據，否則排除空的列再添加
            if new_df.empty:
                new_df = pd.DataFrame({'roadsection': [roadsection, roadsection], 
                                    'highway': ['國道1號','國道1號'],
                                    'direction':['N','S'],
                                    'midpoint': [midpoint,midpoint], 
                                    'from_mil': [from_mil,from_mil], 
                                    'to_mil': [to_mil,to_mil]})
            else:
                new_df = pd.concat([new_df, pd.DataFrame({'roadsection': [roadsection, roadsection], 
                                                       'highway': ['國道1號','國道1號'], 
                                                       'direction':['N','S'],
                                                       'midpoint': [midpoint,midpoint], 
                                                       'from_mil': [from_mil,from_mil],  
                                                       'to_mil': [to_mil,to_mil]})], ignore_index=True)
    # 合併國道一號高架的資料
    for index, row in highway1_h.iterrows():
        if index < len(highway1_h) - 1:
            from_mil = row['里程K+000']
            to_mil = highway1_h.loc[index + 1, '里程K+000']
            midpoint = (from_mil + to_mil) / 2  
            roadsection = f"{highway1_h.loc[index , '設施名稱']}-{highway1_h.loc[index+1 , '設施名稱']}"  
            new_df = pd.concat([new_df, pd.DataFrame({'roadsection': [roadsection, roadsection], 
                                                   'highway': ['國道1號_高架','國道1號_高架'], 
                                                   'direction':['N','S'],
                                                   'midpoint': [midpoint,midpoint], 
                                                   'from_mil': [from_mil,from_mil], 
                                                   'to_mil': [to_mil,to_mil]})], ignore_index=True)
    # 合併國道三號的資料
    for index, row in highway3.iterrows():
        if index < len(highway3) - 1:
            from_mil = row['里程K+000']
            to_mil = highway3.loc[index + 1, '里程K+000']
            midpoint = (from_mil + to_mil) / 2 
            roadsection = f"{highway3.loc[index , '設施名稱']}-{highway3.loc[index+1 , '設施名稱']}" 
            new_df = pd.concat([new_df, pd.DataFrame({'roadsection': [roadsection, roadsection], 
                                                   'highway': ['國道3號','國道3號'], 
                                                   'direction':['N','S'],
                                                   'midpoint': [midpoint,midpoint], 
                                                   'from_mil': [from_mil,from_mil], 
                                                   'to_mil': [to_mil,to_mil]})], ignore_index=True)
    # 合併國道五號的資料
    for index, row in highway5.iterrows():
        if index < len(highway5) - 1:
            from_mil = row['里程K+000']
            to_mil = highway5.loc[index + 1, '里程K+000']
            midpoint = (from_mil + to_mil) / 2  
            roadsection = f"{highway5.loc[index , '設施名稱']}-{highway5.loc[index+1 , '設施名稱']}" 
            new_df = pd.concat([new_df, pd.DataFrame({'roadsection': [roadsection, roadsection], 
                                                   'highway': ['國道5號','國道5號'], 
                                                   'direction':['N','S'],
                                                   'midpoint': [midpoint,midpoint], 
                                                   'from_mil': [from_mil,from_mil], 
                                                   'to_mil': [to_mil,to_mil]})], ignore_index=True)
    #new_df.to_csv('../highway_information/roadsection_TEST.csv', encoding='utf-8-sig', index=False)
    #print("roadsection.csv已儲存")
    return(new_df)


def get_gantrid():
    with open('traffic_volume_attributes.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    gantryID = []
    for key, value in data["RoadSection"].items():
        gantryID.append(key)
    return gantryID


def find_nearest_detection_points(roadsection_and_midpoint, gantryID):
    df = roadsection_and_midpoint
    df['nearest_gantry1'] = None
    df['nearest_gantry2'] = None
    for index, row in df.iterrows():
        if row['highway'] == '國道1號' and row['direction'] == 'S':
            distances = []
            for gid in gantryID:
                if gid[:3] == '01F'and gid.endswith("S"):  
                    distance = abs(row['midpoint'] - int(gid[3:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]  
        if row['highway'] == '國道1號' and row['direction'] == 'N':
            distances = []
            for gid in gantryID:
                if gid[:3] == '01F'and gid.endswith("N"):  
                    distance = abs(row['midpoint'] - int(gid[3:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]  
        if row['highway'] == '國道1號_高架' and row['direction'] == 'S':
            distances = []
            for gid in gantryID:
                if gid[:3] == '01H'and gid.endswith("S"):  
                    distance = abs(row['midpoint'] - int(gid[3:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]  
        if row['highway'] == '國道1號_高架' and row['direction'] == 'N':
            distances = []
            for gid in gantryID:
                if gid[:3] == '01H'and gid.endswith("N"):  
                    distance = abs(row['midpoint'] - int(gid[3:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]  
        if row['highway'] == '國道3號' and row['direction'] == 'S':
            distances = []
            for gid in gantryID:
                if gid[:3] == '03F'and gid.endswith("S"):  
                    distance = abs(row['midpoint'] - int(gid[3:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]
        if row['highway'] == '國道3號' and row['direction'] == 'N':
            distances = []
            for gid in gantryID:
                if gid[:3] == '03F'and gid.endswith("N"):  
                    distance = abs(row['midpoint'] - int(gid[3:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]    
        if row['highway'] == '國道5號' and row['direction'] == 'S':
            distances = []
            for gid in gantryID:
                if gid[:3] == '05F'and gid.endswith("S"):  
                    distance = abs(row['midpoint'] - int(gid[4:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]
        if row['highway'] == '國道5號' and row['direction'] == 'N':
            distances = []
            for gid in gantryID:
                if gid[:3] == '05F'and gid.endswith("N"):  
                    distance = abs(row['midpoint'] - int(gid[4:7])/10)
                    distances.append((gid, distance))
            distances.sort(key=lambda x: x[1])
            nearest_two = distances[:2] if len(distances) >= 2 else None
            if nearest_two:
                df.at[index, 'nearest_gantry1'] = nearest_two[0][0]  
                df.at[index, 'nearest_gantry2'] = nearest_two[1][0]    

    df.to_csv('../highway_information/roadsectiondata_with_nearest.csv', encoding='utf-8-sig', index=False)
    print("roadsection_with_nearest.csv已儲存")


if __name__ == '__main__':
    roadsection_and_midpoint = get_highway_midpoint()
    gantryID = get_gantrid()
    nearest_two_points = find_nearest_detection_points(roadsection_and_midpoint, gantryID)
