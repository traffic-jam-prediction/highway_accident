import pandas as pd

df = pd.read_csv('integrate_categorized_data.csv', encoding='utf-8')
high_traffic_df = df[df['M03A_PCU'] == "高流量"].copy()
high_traffic_df.to_csv('high_volume_data.csv', encoding='utf-8-sig', index=False)