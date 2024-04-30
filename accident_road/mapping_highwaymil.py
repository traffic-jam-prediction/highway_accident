import pandas as pd
from datetime import datetime

# 定義函式來判斷事件位置
def detect_location(kilometer, highway):
    # 根據所在國道選擇相應的 CSV 檔案
    csv_file = f"../highway_information/{highway}.csv"
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    for index, row in df.iterrows():
        if row['里程K+000'] <= kilometer <= df.iloc[index+1]['里程K+000']:
            return f"{row['設施名稱']}-{ df.iloc[index+1]['設施名稱']}"

df = pd.read_csv("A3_accident.csv", encoding='utf-8')
new_df = pd.DataFrame(columns=['Date','Time','Class', 'RoadSection', 'Direction'])

for index, row in df.iterrows():
    if not pd.isnull(row['公里']):  # 檢查 '公里' 欄位是否為 NaN
        row['公里'] = int(row['公里']) 
        highway, ai, kilometer, direction = row['路線'], row['事故類別'], row['公里'], 'N' if '北側' in row['向'] else 'S'
        if row[' 道路型態'] == "高架道路":
            if kilometer>71:
                continue    
            if highway in ["國道1號"]:
                if kilometer<13:
                    continue
                else:
                    highway = highway+"_高架"
                    location = detect_location(kilometer, highway) 
                location = location + "(高架)"
                
        else :
            if highway in ["國道1號","國道3號","國道5號"]:
                location = detect_location(kilometer, highway) 
        
        date = datetime.strptime(f"{int(row['年'])}-{int(row['月'])}-{int(row['日'])}", '%Y-%m-%d')
        time = datetime.strptime(f"{int(row['時'])}:{int(row['分'])}:{int(row['秒'])}", '%H:%M:%S')
        minute = 5 * (time.minute // 5)
        time = f"{time.hour:02d}:{minute:02d}"

        if new_df.empty:     
            new_df = pd.DataFrame({'Date': [date], 'Time':[time],'Class':[ai], 'RoadSection': [location], 'Direction': [direction]})
        else:
            new_df = pd.concat([new_df, pd.DataFrame({'Date': [date], 'Time':[time],'Class':[ai], 'RoadSection': [location], 'Direction': [direction]})], ignore_index=True)
    

new_df.to_csv('accident3_info.csv', index=False, encoding='utf-8-sig')
print("新的 CSV 檔案已生成。")