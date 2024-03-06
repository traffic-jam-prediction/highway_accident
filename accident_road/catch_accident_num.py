import pandas as pd

# 读取所有 CSV 文件
df1 = pd.read_csv("accident1_info.csv", encoding='utf-8')
df2 = pd.read_csv("accident2_info.csv", encoding='utf-8')
df3 = pd.read_csv("accident3_info.csv", encoding='utf-8')

# 合并 DataFrame
merged_df = pd.concat([df1, df2, df3], ignore_index=True)

# 根据路段和事故类别分组，并计算每个组内的行数
grouped_df = merged_df.groupby(['路段', '事故類別']).size().reset_index(name='事故數量')

# 使用 pivot_table 将事故类别作为列，路段作为索引，并填充每个单元格的值为对应事故类型的数量
pivot_table_df = grouped_df.pivot_table(index='路段', columns='事故類別', values='事故數量', fill_value=0, aggfunc='first')

# 将事故數量列添加到新的 DataFrame
pivot_table_df['事故數量'] = grouped_df.groupby('路段')['事故數量'].sum()

# 重新排列列的顺序，将'事故數量'列移到'路段'列后面
pivot_table_df = pivot_table_df.reindex(columns=['事故數量'] + pivot_table_df.columns[:-1].tolist())

# 保存结果到新的 CSV 文件
pivot_table_df.to_csv("accident_count_with_types.csv",encoding='utf-8-sig')

print("结果已保存到 accident_count_with_types.csv 文件中。")
