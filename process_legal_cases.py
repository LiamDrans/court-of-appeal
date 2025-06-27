"""
process_legal_cases.py

This script processes legal case data scraped from the web, extracting law firm-party representations,
filtering out cases by domain (e.g., Family, Immigration, Criminal), cleaning text, and saving the
result as a pickle file.

"""

import pandas as pd
import json
import re
import pickle
import os

# function to retrieve the representation for the parties - outputs a tuple i.e. [('DAC Beachcroft LLP', 'Appellant'), ('Mishcon de Reya LLP', 'Respondent')]
def extract_law_firm_and_party(x):

    # Regex pattern to retrieve the representation for the parties
    pattern_for_the = r"\(instructed by ([^)]+(?:\([^)]+\)[^)]+)*)\)\s+for the ([^\(\n]+)"
    pattern_appeared_on_behalf = r"\(instructed by ([^)]+)\)\s+appeared on behalf of the ([^\(\n]+)"

    if isinstance(x, str):

        if "appeared on behalf" in x:
            result = re.findall(pattern_appeared_on_behalf, x)
        else:
            result = re.findall(pattern_for_the, x)
        
        # Strip any \r or \n characters from the results
        if result:
            return [(firm.strip(), party.strip()) for firm, party in result]
    return None

# Flattens a dictionary into a string of just the values
def flatten_and_clean_text_dict(x):
    if isinstance(x, dict):
        x=" ".join(str(v) for v in x.values())
    
    # Clean text (remove non-word characters)
    x = re.sub(r"[^a-zA-Z\s]", "", x) 
    return x

# Filter out the court cases we are not interested in i.e. Family, Immigration, Criminal
def filter_by_keywords(df, column, keywords):
    pattern = "|".join(keywords)
    return df[~df[column].str.contains(pattern, case=False, na=False)]


# One stop shop to transform the data
def data_transformation(filename, keywords=["FAMILY", "IMMIGRATION", "CRIMINAL"]):

    output_dir = "data/cases_by_year_processed"
# Retrieves the webscrapped data
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

#   Saves the webscrapped data into a dataframe
    df = pd.DataFrame(data)

    df['law_firms'] = df["representation"].apply(extract_law_firm_and_party)
    df["text"] = df["text"].apply(flatten_and_clean_text_dict)
    df_filtered = filter_by_keywords(
    df,
    column="court",
    keywords=keywords
    )

    print(f'{len(df_filtered)-len(df)} number of rows filtered out by way of the keywords: {keywords}')

    base_name = os.path.splitext(os.path.basename(filename))[0] 
    output_path = os.path.join(output_dir, f"{base_name}_processed.pkl")

    with open(output_path, "wb") as file:
        pickle.dump(df_filtered, file)
    
    return df_filtered

if __name__ == "__main__":
    data_transformation(r'data\cases_by_year\cases_2025.json')