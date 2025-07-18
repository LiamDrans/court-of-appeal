import pandas as pd
import json

df = pd.read_csv(f'law_firm_statistics_for_page.csv')
print(df)

with open("data/law_firm_statistics/law_firms_grouped_manual_sorted.json", "r") as f:
    grouped_law_firms = json.load(f)

mapping = {}
for group in grouped_law_firms:
    top_level = group[0]
    for variant in group:
        mapping[variant] = top_level

df.rename(columns={'Law_Firm': 'Law_Firm(from_text)'}, inplace=True)
df['Law_Firm'] = df['Law_Firm(from_text)'].map(mapping).fillna(df['Law_Firm(from_text)'])
cols = df.columns.tolist()
cols.insert(0, cols.pop(cols.index('Law_Firm')))
df = df[cols]

df.to_csv('law_firm_statistics_for_page.csv', index=False)
