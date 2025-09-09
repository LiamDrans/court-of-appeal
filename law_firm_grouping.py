import json
import pandas as pd
from difflib import get_close_matches

stats_df = pd.read_csv('data/law_firm_statistics/law_firm_statistics.csv')

"""BELOW IS FOR THE LAW FIRM GROUPING MECHANISM"""

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

# Step 2: Merge overlapping groups

def merge_overlapping(groups):
    groups = [set(g) for g in groups]
    while True:
        for i, a in enumerate(groups):
            for j in range(i + 1, len(groups)):
                b = groups[j]
                if a & b:
                    groups = groups[:i] + [a | b] + groups[i+1:j] + groups[j+1:]
                    break
            else:
                continue
            break
        else:
            return groups


merge_overlapping(groups)

# Step 3: Sort groups for readability
sorted_groups = [sorted(group) for group in groups]
sorted_groups.sort()

# print(sorted_groups)

with open("law_firms_grouped_raw.json", "w") as f:
    json.dump(sorted_groups, f, indent=4)

with open("data/law_firm_statistics/law_firms_grouped_manual_sorted(BACKUP).json", "r") as f:
    manual_data = json.load(f)

# sort the outer list by the first item in each inner list
sorted_data = sorted(manual_data, key=lambda group: group[0].lower())

with open("law_firms_grouped_manual_sorted.json", "w") as f:
    json.dump(sorted_data, f, indent=4)

