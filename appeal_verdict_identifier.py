"""
Appeal Outcome Extractor

This script analyzes legal judgment texts to determine the outcome of appeals—
classifying them as 'GRANTED', 'DISMISSED', or 'UNCLEAR'—based on rule-based 
natural language patterns.

It uses spaCy's Matcher to identify key phrases in judicial decisions that 
indicate whether an appeal was granted or dismissed. The script processes a 
preloaded dataset of documents, applies the classification, and exports the 
results to a CSV file.
"""

import pickle
import pandas as pd
import spacy
from spacy.matcher import Matcher
import re
import os
from datetime import datetime

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

dismiss_patterns = [

    # Direct: "dismiss the appeal", "I would dismiss the appeal", etc.
    [
        {"LOWER": {"IN": ["i"]}, "OP": "?"},
        {"LOWER": {"IN": ["too", "would"]}, "OP": "*"},
        {"LEMMA": {"IN": ["deny", "dismiss", "reject", "refuse"]}},
        {"LOWER": {"IN": ["the", "this", "both", "all"]}},
        {"LOWER": {"IN": ["appeal", "appeals", "application", "applications"]}},
        {"IS_ALPHA": True, "OP": "*"}  # optional trailing words like "accordingly"
    ],

    # Passive: "the appeal is dismissed", "the appeal was refused"
    [
        {"LOWER": {"IN": ["the", "this", "both", "all"]}},
        {"LOWER": {"IN": ["appeal", "appeals", "application", "applications"]}},
        {"LEMMA": "be"},
        {"IS_ALPHA": True, "OP": "*"},  # allow optional tokens like "therefore"
        {"LOWER": {"IN": ["denied", "dismissed", "rejected", "refused"]}}
    ],

    # Permission refused: "permission to appeal is refused"
    [
        {"LOWER": "permission"},
        {"LOWER": "to"},
        {"LOWER": "appeal"},
        {"LEMMA": "be"},
        {"IS_ALPHA": True, "OP": "*"},  # allow optional tokens like "therefore"
        {"LOWER": {"IN": ["denied", "dismissed", "rejected", "refused"]}}
    ],

    # Active form: "refuse permission to appeal"
    [
        {"LEMMA": {"IN": ["deny", "dismiss", "reject", "refuse"]}},
        {"LOWER": "permission"},
        {"LOWER": "to"},
        {"LOWER": "appeal"}
    ],

    # Flexible: "dismiss ... appeal", with anything in between
    [
        {"LEMMA": {"IN": ["deny", "dismiss", "reject", "refuse"]}},
        {"IS_ALPHA": True, "OP": "*"},
        {"LOWER": {"IN": ["appeal", "appeals", "application", "applications"]}}
    ]
]

grant_patterns = [

    # Direct: "I would allow the appeal", "I too would allow this appeal", etc.
    [
        {"LOWER": {"IN": ["i"]}, "OP": "?"},
        {"LOWER": {"IN": ["too", "would"]}, "OP": "*"},
        {"LEMMA": {"IN": ["allow", "grant"]}},
        {"LOWER": {"IN": ["the", "this", "both", "all"]}},
        {"LOWER": {"IN": ["appeal", "appeals", "application", "applications"]}},
        {"IS_ALPHA": True, "OP": "*"}  # optional trailing like "accordingly"
    ],

    # Passive: "the appeal is allowed", "permission to appeal is granted"
    [
        {"LOWER": {"IN": ["the", "this", "both", "all"]}},
        {"LOWER": {"IN": ["appeal", "appeals", "application", "applications"]}},
        {"LEMMA": "be"},
        {"IS_ALPHA": True, "OP": "*"},  # allow optional tokens like "therefore"
        {"LOWER": {"IN": ["allowed", "granted"]}}
    ],
    [
        {"LOWER": "permission"},
        {"LOWER": "to"},
        {"LOWER": "appeal"},
        {"LEMMA": "be"},
        {"IS_ALPHA": True, "OP": "*"},  # allow optional tokens like "therefore"
        {"LOWER": {"IN": ["allowed", "granted"]}}
    ],

    # Active: "grant permission to appeal"
    [
        {"LEMMA": "grant"},
        {"LOWER": "permission"},
        {"LOWER": "to"},
        {"LOWER": "appeal"}
    ],

    # Flexible: "allow ... appeal", with anything in between
    [
        {"LEMMA": {"IN": ["allow", "grant"]}},
        {"IS_ALPHA": True, "OP": "*"},
        {"LOWER": {"IN": ["appeal", "appeals", "application", "applications"]}}
    ]
]

matcher.add("DISMISS", dismiss_patterns)
matcher.add("GRANT", grant_patterns)

# with open("all_2015_processed.pkl", "rb") as f:
#     df_2015 = pickle.load(f)

def determine_outcome(text):

    # tracking how long it takes
    print(datetime.now())

    # performs nlp on the document
    doc = nlp(text)
    # last_tokens = doc[-100:]

    # # takes the last 100 tokens (words) to perform the nlp analysis on

    matches = matcher(doc)
    
    # Dictionary to keep rack of how many times each decision-related keyword appears
    decision = {"GRANT": 0, "DISMISS": 0}

    last_grant_pos = -1
    last_dismiss_pos = -1

    for match_id, start, _ in matches:
        label = nlp.vocab.strings[match_id]
        if label in decision:
            decision[label] += 1
            if label == "GRANT" and start > last_grant_pos:
                last_grant_pos = start
            elif label == "DISMISS" and start > last_dismiss_pos:
                last_dismiss_pos = start

    if decision["GRANT"] == 0 and decision["DISMISS"] == 0:
        return "UNCLEAR"
    elif decision["GRANT"] > 0 and decision["DISMISS"] == 0:
        return "GRANTED"
    elif decision["DISMISS"] > 0 and decision["GRANT"] == 0:
        return "DISMISSED"
    else:
        # Resolve tie by whichever appears later in the document
        if last_grant_pos > last_dismiss_pos:
            return "GRANTED"
        else:
            return "DISMISSED"
        
def process_outcomes_for_year(filename):
    """
    Processes a pickled DataFrame of legal cases for a given year, applies
    NLP-based appeal outcome classification, and saves the results.

    Outputs:
    - A CSV file without full text (for lighter analysis)
    - A Pickle file including full text and outcomes
    """

    output_dir = "data/cases_by_year_with_outcome"
    os.makedirs(output_dir, exist_ok=True)

    output_dir = "data/cases_by_year_with_outcome"
    base_name = os.path.splitext(os.path.basename(filename))[0] 
    output_path_pkl = os.path.join(output_dir, f"{base_name}_with_outcome.pkl")
    output_path_csv = os.path.join(output_dir, f"{base_name}_with_outcome.csv")

    with open(filename, "rb") as f:
        df = pickle.load(f)

    if "text" not in df.columns:
        raise ValueError("Input DataFrame must contain a 'text' column.")
    
    df["outcome"] = df["text"].apply(determine_outcome)
    df_text_excluded = df.drop(columns=['text'])

    df_text_excluded.to_csv(output_path_csv, index=False, encoding="utf-8")
    
    with open(output_path_pkl, "wb") as file:
        pickle.dump(df, file)

if __name__ == "__main__":
    process_outcomes_for_year(r'data\cases_by_year_processed\cases_2015_processed.pkl')