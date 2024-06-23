import pandas as pd

df_main = pd.read_csv('main06.csv', encoding='utf-8')
df_weather = pd.read_csv('weather_data.csv', encoding='utf-8')

df_weather = df_weather.drop_duplicates(subset=['DateTime', 'Highway', 'Midpoint'])
new_df = pd.merge(df_main, df_weather, how='left', on=['DateTime', 'Highway', 'Midpoint'])
new_df = new_df.drop(columns=['Highway'])

new_df.to_csv('merge.csv', encoding='utf-8-sig', index=False)