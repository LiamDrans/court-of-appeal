import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn import metrics

years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015]

df = pd.DataFrame()

for year in years:
    df_year = pd.read_csv(f'data/cases_by_year_with_outcome/cases_{year}_processed_with_outcome.csv')
    df_year['year'] = year
    df = pd.concat([df, df_year], ignore_index=True)

df = df.dropna(subset=['citation'])

sample_df, rest_df = train_test_split(df, train_size=150, random_state=42)
sample_df_sorted = sample_df.sort_values(by='link', ascending=False)
sample_df_sorted.to_csv('data/sample_review/sample_150.csv', index=False)