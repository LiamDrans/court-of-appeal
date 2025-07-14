import pickle
import json
import pandas as pd
import ast
import re
from collections import defaultdict
from difflib import get_close_matches

# Issue is law firm name - still susceptable to typos -

years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015]

df = pd.DataFrame()

for year in years:
    df_year = pd.read_csv(f'data/cases_by_year_with_outcome/cases_{year}_processed_with_outcome.csv')
    df_year['year'] = year
    df = pd.concat([df, df_year], ignore_index=True)

df = df.dropna(subset=['citation'])

def string_to_tuple(val):
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except Exception as e:
        print(f"Error parsing value: {val}")
        return []

df['law_firms'] = df['law_firms'].apply(string_to_tuple)

protected_firms = {
    'Slaughter and May',
    'Winston and Strawn London LLP',
    'Competition and Markets Authority',
    'Haynes and Boone, LLP'
}

protected_firms = {f.lower().replace('the ', '').replace('&', 'and').strip() for f in protected_firms}

def extract_firms(firm_string):

    # Split by semicolon first
    segments = [seg.strip() for seg in firm_string.split(';') if seg.strip()]

    result_firms = []

    for seg in segments:
        seg = seg.strip().lower().replace('the ', '')
        seg = ' '.join(seg.split())
        # If it's a protected firm, keep it as is

        if seg in protected_firms:
            result_firms.append(seg)
        else:
            # Otherwise split on ' and ' but preserve protected substrings
            split_firms = [s.strip() for s in re.split(r' and ', seg)]
            for firm in split_firms:
                # If the fragment matches a protected firm, merge it back
                matched = [pf for pf in protected_firms if pf in seg]
                if matched:
                    result_firms.extend(matched)
                    break
                else:
                    result_firms.append(firm)

    return list(set(result_firms)) 

neutral_keywords = ['interested', 'neutral', 'intervener']

results = defaultdict(lambda: {'Wins': 0, 'Losses': 0, 'Neutral_Appearances':0, 'Appellant_Appearances':0, 'Respondent_Appearances':0})

for _, row in df.iterrows():
    outcome = row['outcome']
    firm_roles = row['law_firms']

    if outcome == 'UNCLEAR':
        continue  # Skip these cases

    for firm_string, role in firm_roles:

        # Split firms on " and " to handle joined firm names
        individual_firms = extract_firms(firm_string)

        for firm in individual_firms:
            # Determine win/loss by role + outcome
            role = role.lower()
            all_roles = [r.lower() for _, r in firm_roles]

            neutral_keywords = ['interested', 'intervener']

            # Check if neutral
            if any(neutral_word in role for neutral_word in neutral_keywords):
                for firm in individual_firms:
                    results[firm]['Neutral_Appearances'] += 1
                continue  # Skip win/loss logic

            
                    # Count appearances by role
            
            if 'appellant' in role or 'applicant' in role or ('claimant' in role and not any('appellant' in r for r in all_roles)):
                results[firm]['Appellant_Appearances'] += 1
            elif 'respondent' or 'defendant' in role:
                results[firm]['Respondent_Appearances'] += 1

            is_winner = (
                # this includes situations where there is ONLY the claimant in the law firm column (and no appellant)
                (('appellant' in role or 'applicant' in role or ('claimant' in role and not any('appellant' or 'applicant' in r for r in all_roles))) and outcome == 'GRANTED')
                or
                ('respondent' in role and outcome == 'DISMISSED'))

            if is_winner:
                results[firm]['Wins'] += 1
            else:
                results[firm]['Losses'] += 1

# Convert to a DataFrame
stats_df = pd.DataFrame.from_dict(results, orient='index').reset_index()
stats_df.columns = ['Law_Firm', 'Wins', 'Losses', 'Neutral_Appearances', 'Appellant_Appearances', 'Respondent_Appearances']
stats_df['Win_Rate'] = (stats_df['Wins'] / (stats_df['Wins'] + stats_df['Losses'])) * 100

print(stats_df)

# Save statistics as CSV
stats_df.to_csv('data/law_firm_statistics/law_firm_statistics.csv', index=False)

# firms = ["Government"]
# pattern = '|'.join(firms)
# stats_df = stats_df[stats_df['Law_Firm'].str.contains(pattern, case=False, na=False)]
# print(stats_df)

def firm_match(firm_data, target="government"):
    target = target.lower()
    if not isinstance(firm_data, list):
        return False
    for entry in firm_data:
        if isinstance(entry, tuple):
            name = entry[0]
        else:
            name = str(entry)
        if target in name.lower():
            return True
    return False

# Firm match applies to the original dataframe - i.e. returning all case links for that law firm
print(len(df.loc[df['outcome'] == 'UNCLEAR']))
print((df.loc[df['law_firms'] == 'UNCLEAR']))
# Apply filter
print(df[df['law_firms'].apply(lambda x: firm_match(x))][['link', 'outcome', 'year']])

# group the law firms into matches
visited = set()
groups = []

# Similarity threshold (0.8 is moderate; adjust as needed)
similarity_cutoff = 0.85

# Step 1: Grouping similar names
for firm in stats_df['Law_Firm']:
    if firm not in visited:
        matches = get_close_matches(firm, stats_df['Law_Firm'], cutoff=similarity_cutoff)
        visited.update(matches)
        groups.append(matches)

# Convert all groups to sets before merging
groups = [set(group) for group in groups]

# Step 2: Merge overlapping groups (Union-Find-like)
merged = True
while merged:
    merged = False
    new_groups = []
    while groups:
        first, *rest = groups
        first = set(first)
        changed = True
        while changed:
            changed = False
            rest2 = []
            for g in rest:
                if first & g:  # Overlap found
                    first |= g
                    changed = True
                else:
                    rest2.append(g)
            rest = rest2
        new_groups.append(first)
        groups = rest
        merged = True if changed else merged
    groups = new_groups

# Step 3: Sort groups for readability
sorted_groups = [sorted(group) for group in groups]
sorted_groups.sort()

print(sorted_groups)

# with open("law_firms_grouped_raw.json", "w") as f:
#     json.dump(sorted_groups, f, indent=4)

# # Display groups nicely
# for idx, group in enumerate(sorted_groups, 1):
#     print(f"Group {idx}:")
#     for firm in group:
#         print(f"  - {firm}")
#     print()

with open("law_firms_manual_grouped.json", "r") as f:
    manual_data = json.load(f)

sorted(manual_data[0])

with open("law_firms_grouped_manual_sorted.json", "w") as f:
    json.dump(manual_data, f, indent=4)