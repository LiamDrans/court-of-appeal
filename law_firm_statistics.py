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

print(df)

def string_to_tuple(val):
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except Exception as e:
        print(f"Error parsing value: {val}")
        return []

df['law_firms'] = df['law_firms'].apply(string_to_tuple)

firms_to_protect_df = df.loc[
    df['law_firms'].apply(
        lambda firm_list: any(' and ' in tup[0] for tup in firm_list)
    )
]

print(len(firms_to_protect_df))

firms_to_protect_df['parties'] = firms_to_protect_df['parties'].str.replace('\n', ' ', regex=True).str.strip()

firms_to_protect_df.to_csv('data/law_firm_statistics/firms_to_protect.csv', columns=['link','representation','law_firms'], index=False)

protected_firms = {
    'general counsel and solicitor',
    'general solicitor and counsel',
    'general solicitors and counsel',
    'general counsel and\r\nsolicitor',
    'law and advocacy',
    'and associates',
    'and co',
    'and company',
    'and partners',
    'and sons',
    'and law centre',
    'avon and somerset',
    'prosecutions and inquests',
    'legal and democratic',
    'law and governance'
    'Wealden and Rother',
    'disclosure and barring',
    'comptroller and city',
    'governance and legal',
    'legal and governance',
    'governance and law',
    'nuneaton and bedworth',
    'solicitors and advocates',
    'office and legal service',
    'legal and democratic services',
    'corporate and legal services',
    'slaughter and may',
    'allen and overy',
    'winston and strawn',
    'competition and markets authority',
    'Enforcement and Market Oversight'
    'revenue and customs'
    'equality and human',
    'kensington and chelsea',
    'haynes and boone',
    'slater and gordon',
    'hackett and dabbs',
    'miles and partners',
    'pinder reaux and associates',
    'morgan, lewis and bockius',
    'lawrence and associates',
    'horwich farrelly and keoghs',
    'kirklees citizens advice and law centre',
    'shepherd and wedderburn',
    'britton and time',
    'child and child',
    'simmons and simmons',
    'dentons uk and middle east',
    'hodge jones and allen',
    'sullivan and cromwell',
    'aaron and partners',
    'crane and walton',
    'kilgannon and partners',
    'tedstone, george and tedstone',
    'richard slade and co',
    'richard slade and company',
    'clyde and co',
    'kirkland and ellis',
    'watkins and gunn',
    'manchester and salford',
    'wilmer cutler pickering hale and dorr',
    'thomson snell and passmore',
    'wealden and rother',
    'hunt and coombs',
    'folkestone and hythe',
    'paul martin and co',
    'luke and bridger',
    'peters and peters',
    'faegre drinker biddle and reath',
    'kleyman and co',
    'mills and reeve',
    'southampton and fareham',
    'hammersmith and fulham',
    'watch tower bible and tract society',
    'rich and carr',
    'kesar and co',
    'byrne and partners',
    'johnson and boon',
    'christchurch and poole',
    'public and regulatory',
    'debevoise and plimpton',
    'staffordshire and west',
    'harrison drury and co',
    'shuttari paul and co'
    'cheshire west and chester council',
    'shropshire council legal and democratic services',
    'avon and bristol',
    'gibson dunn and crutcher',
    'matthew gold and co.',
    'environmental and public',
    'richard buxton environmental and public law',
    'environmental and planning',
    'lexlaw solicitors and advocates',
    'avon and somerset police',
    'richmond and barnes',
    'milbank, tweed, hadley and mccloy',
    'hinckley and bosworth borough council',
    'kerman and co',
    'anti-trafficking and labour',
    'lamb and holmes',
    'bentleys, stokes and lowless',
    'ashfield and mansfield',
    'trowers and hamlins', 
    'snell and passmore',
    'imran khan and partners',
    'city and district',
    'appeals and review',
    'green and olive',
    'bates wells and braithwaite',
    'mcdermott will and emery',
    'law and public services',
    'rbs and natwest',
    'white and case',
    'legal and regulatory services',
    'solicitors and financial advisors',
    'fox and partners',
    'stockinger advocates and solicitors',
    'nursing and midwifery council',
    'david price solicitors and advocates',
    'davis simmonds and donaghey',
    'richard max and co',
    'tonbridge and malling',
    'steptoe and johnson',
    'rice-jones and smiths',
    'barnes, harrild and dyer',
    'beale and company',
    'bower and bailey',
    'litigation and review team',
    'oadby and wigston',
    'birmingham city council legal and democratic services',
    'birnberg peirce and partners',
    'leo abse and cohen',
    'jackson and canter',
    'croydon and sutton',
    'legal services and legal team',
    'regents and co',
    'harney and wells',
    'brighton and hove city council',
    'breeze and wyles',
    'newark and sherwood',
    'lambeth and Mayor of London',
    'richard leighton hill',
    'wainwright and cummins',
    'warren\'s law and advocacy',
    'blandy and blandy',
    'royal borough of windsor and maidenhead',
    'butcher and barlow',
    'st albans city and district council'
}

import re

def extract_firms(firm_string, protected_firms):
    segments = [seg.strip() for seg in firm_string.split(';') if seg.strip()]
    result_firms = []

    for seg in segments:
        original = seg.strip()
        normalized = original.lower().replace('the ', '')
        normalized = ' '.join(normalized.split())

        protected_map = {}
        temp_seg = normalized

        # 1. Mask protected firm substrings
        for i, pf in enumerate(sorted(protected_firms, key=len, reverse=True)):
            norm_pf = pf.lower().replace('the ', '').strip()
            if norm_pf in temp_seg:
                placeholder = f"__PROTECTED_{i}__"
                temp_seg = temp_seg.replace(norm_pf, placeholder)
                protected_map[placeholder] = pf  # keep original protected string casing

        # 2. Split on ' and '
        parts = [part.strip() for part in re.split(r'\band\b', temp_seg) if part.strip()]

        # 3. Restore protected substrings
        for part in parts:
            for placeholder, original_pf in protected_map.items():
                part = part.replace(placeholder, original_pf)
            result_firms.append(part)

    return list(set(result_firms))


neutral_keywords = ['interested', 'neutral', 'intervener']

results = defaultdict(lambda: {'Wins': 0, 'Losses': 0, 'Neutral_Appearances':0, 'Appellant_Appearances':0, 'Respondent_Appearances':0})

case_links = defaultdict(lambda: defaultdict(list))

for _, row in df.iterrows():
    outcome = row['outcome']
    firm_roles = row['law_firms']

    if outcome == 'UNCLEAR':
        continue

    for firm_string, role in firm_roles:
        individual_firms = extract_firms(firm_string, protected_firms)
        role_lower = role.lower()
        all_roles = [r.lower() for _, r in firm_roles]
        year = str(row['year'])
        link = row['link']

        for firm in individual_firms:
            # Determine result first
            if any(n in role_lower for n in ['interested', 'neutral', 'intervener']):
                result_label = "Neutral"
                results[firm]['Neutral_Appearances'] += 1
            else:
                is_appellant = (
                    'appellant' in role_lower or
                    'applicant' in role_lower or
                    ('claimant' in role_lower and not any('appellant' in r or 'applicant' in r for r in all_roles))
                )

                is_respondent = 'respondent' in role_lower or 'defendant' in role_lower

                is_winner = (
                    (is_appellant and outcome == 'GRANTED') or
                    (is_respondent and outcome == 'DISMISSED')
                )

                if is_appellant:
                    results[firm]['Appellant_Appearances'] += 1
                elif is_respondent:
                    results[firm]['Respondent_Appearances'] += 1

                result_label = "Win" if is_winner else "Loss"
                if is_winner:
                    results[firm]['Wins'] += 1
                else:
                    results[firm]['Losses'] += 1

            # ✅ Log per-case data with result
            case_links[firm][year].append({
                "url": link,
                "role": role_lower,
                "outcome": outcome.lower(),
                "result": result_label
            })

stats_df = pd.DataFrame.from_dict(results, orient='index').reset_index()
stats_df.columns = ['Law_Firm', 'Wins', 'Losses', 'Neutral_Appearances', 'Appellant_Appearances', 'Respondent_Appearances']

# Attach Cases as a new column
stats_df['Cases'] = stats_df['Law_Firm'].map(
    lambda f: {year: list(links) for year, links in sorted(case_links.get(f, {}).items())}
)

stats_df['Win_Rate'] = (stats_df['Wins'] / (stats_df['Wins'] + stats_df['Losses'])) * 100

# Save statistics as CSV
stats_df.to_csv('data/law_firm_statistics/law_firm_statistics.csv', index=False)
