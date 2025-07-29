import pickle
import json
import pandas as pd
import ast
import re
from collections import defaultdict
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

# print(sorted_groups)

with open("law_firms_grouped_raw.json", "w") as f:
    json.dump(sorted_groups, f, indent=4)

# # Display groups nicely
# for idx, group in enumerate(sorted_groups, 1):
#     print(f"Group {idx}:")
#     for firm in group:
#         print(f"  - {firm}")
#     print()

with open("data/law_firm_statistics/law_firms_grouped_manual_sorted(BACKUP).json", "r") as f:
    manual_data = json.load(f)

# sort the outer list by the first item in each inner list
sorted_data = sorted(manual_data, key=lambda group: group[0].lower())

with open("law_firms_grouped_manual_sorted.json", "w") as f:
    json.dump(sorted_data, f, indent=4)
