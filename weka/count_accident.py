import pandas as pd

def count_road_accident():
# if __name__ == '__main__':
    df_path = '../accident_road/accident_count.csv'
    df = pd.read_csv(df_path)

    north_data = df[['RoadSection', 'N']].copy()
    north_data['RoadSection'] = north_data['RoadSection'] + 'N'
    north_data.columns = ['RoadSection', '事故數量']

    south_data = df[['RoadSection', 'S']].copy()
    south_data['RoadSection'] = south_data['RoadSection'] + 'S'
    south_data.columns = ['RoadSection', '事故數量']

    combined_data = pd.concat([north_data, south_data])
    combined_data['Accident_Risk'] = combined_data['事故數量'].apply(lambda x: 
                                                                            '極易發生事故' if x >= 400 else 
                                                                            '易發生事故' if 300 <= x < 400 else 
                                                                            '稍易發生事故' if 100 <= x < 300 else 
                                                                            '不易發生事故')
    # sorted_data = combined_data.sort_values(by='事故數量', ascending=False).reset_index(drop=True)
    # sorted_data.to_csv('count.csv', index=False, encoding='utf-8-sig')
    combined_data = dict(zip(combined_data['RoadSection'], combined_data['Accident_Risk']))

    return combined_data