import pandas as pd
import json

df = pd.read_csv(f'data/law_firm_statistics/law_firm_statistics.csv')
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

df.drop('Win_Rate', axis=1, inplace=True)


df_grouped = df.groupby('Law_Firm', as_index=False)[
    ['Wins', 'Losses', 'Neutral_Appearances', 'Appellant_Appearances', 'Respondent_Appearances']
].sum()

variants_map = df.groupby('Law_Firm')['Law_Firm(from_text)'].unique().reset_index()
variants_map.rename(columns={'Law_Firm(from_text)': 'Law_Firm(from_text)'}, inplace=True)
df_grouped = pd.merge(df_grouped, variants_map, on='Law_Firm', how='left')
df_grouped['Win_Rate'] = round((df_grouped['Wins'] / (df_grouped['Wins'] + df_grouped['Losses'])) * 100, 2)

df_grouped = df_grouped[
    [
        'Law_Firm',
        'Wins',
        'Losses',
        'Win_Rate',
        'Neutral_Appearances',
        'Appellant_Appearances',
        'Respondent_Appearances',
        'Law_Firm(from_text)'
    ]
]

df_grouped['Law_Firm(from_text)'] = df_grouped['Law_Firm(from_text)'].apply(
    lambda x: ', '.join(map(str, x)) if isinstance(x, (list, tuple)) else str(x)
)

print(df_grouped)

print(df_grouped.loc[df_grouped['Law_Firm'] == 'allen overy shearman sterling llp'])

df_grouped.to_csv('law_firm_statistics_for_page.csv', index=False)
