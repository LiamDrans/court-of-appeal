import pandas as pd
import json
import ast
from collections import defaultdict

# === 1. Load and clean base data ===
df = pd.read_csv('data/law_firm_statistics/law_firm_statistics.csv')
df['Cases'] = df['Cases'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else {})

with open("data/law_firm_statistics/law_firms_grouped_manual_sorted.json", "r") as f:
    grouped_law_firms = json.load(f)

# === 2. Apply canonical names ===
mapping = {}
for group in grouped_law_firms:
    canonical = group[0]
    for variant in group:
        mapping[variant] = canonical

df.rename(columns={'Law_Firm': 'Law_Firm(from_text)'}, inplace=True)
df['Law_Firm'] = df['Law_Firm(from_text)'].map(mapping).fillna(df['Law_Firm(from_text)'])

# === 3. Aggregate stats ===
stats_cols = ['Wins', 'Losses', 'Neutral_Appearances', 'Appellant_Appearances', 'Respondent_Appearances']
df_stats = df.groupby('Law_Firm', as_index=False)[stats_cols].sum()

# === 4. Aggregate law firm name variants ===
df_variants = df.groupby('Law_Firm')['Law_Firm(from_text)'].agg(lambda x: sorted(set(x))).reset_index()

# === 5. Merge all Cases properly ===
def merge_case_dicts(dict_list):
    merged = defaultdict(set)
    for d in dict_list:
        for year, links in d.items():
            merged[year].update(links)
    return {year: sorted(list(links)) for year, links in merged.items()}

df_cases = df.groupby('Law_Firm')['Cases'].agg(merge_case_dicts).reset_index()

# === 6. Merge all parts ===
df_final = (
    df_stats
    .merge(df_variants, on='Law_Firm', how='left')
    .merge(df_cases, on='Law_Firm', how='left')
)

# === 7. Final formatting ===
df_final['Win_Rate'] = round((df_final['Wins'] / (df_final['Wins'] + df_final['Losses'])) * 100, 2)
df_final['Law_Firm(from_text)'] = df_final['Law_Firm(from_text)'].apply(lambda x: ', '.join(x))
df_final['Cases'] = df_final['Cases'].apply(json.dumps)

df_final = df_final[
    [
        'Law_Firm',
        'Wins',
        'Losses',
        'Win_Rate',
        'Neutral_Appearances',
        'Appellant_Appearances',
        'Respondent_Appearances',
        'Law_Firm(from_text)',
        'Cases'
    ]
]

# === 8. Export ===
df_final.to_csv('law_firm_statistics_for_page.csv', index=False)

print("✅ Done. Final shape:", df_final.shape)
