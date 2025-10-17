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

df_sample_reviewed = pd.read_csv(f'data/sample_review/sample_150_reviewed.csv')

# df_sample_reviewed = df_sample_reviewed[
#     ~df_sample_reviewed['reality'].isin(['UNCLEAR']) &
#     ~df_sample_reviewed['outcome'].isin(['UNCLEAR'])
#     ]

labels = ['DISMISSED', 'GRANTED', 'UNCLEAR']

cm = metrics.confusion_matrix(
    df_sample_reviewed['reality'],
    df_sample_reviewed['outcome'],
    labels=labels
)

cm_normalized = metrics.confusion_matrix(
    df_sample_reviewed['reality'],
    df_sample_reviewed['outcome'],
    labels=labels,
    normalize='true'
)

print("The confusion matrix for your predictions is:")
print(cm)

# Compute evaluation metrics for 3-class setup
print(f"Accuracy:  {metrics.accuracy_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome']):.3f}")
print(f"Recall:    {metrics.recall_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'], average='weighted'):.3f}")
print(f"Precision: {metrics.precision_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'], average='weighted'):.3f}")
print(f"F1-score:  {metrics.f1_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'], average='weighted'):.3f}")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))

# Raw counts
disp = metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
disp.plot(ax=axes[0], cmap='cividis_r', values_format='d', colorbar=False)
axes[0].set_title('Confusion Matrix – Counts')
axes[0].set_xlabel('Predicted')
axes[0].set_ylabel('Actual')

# Normalized
disp_norm = metrics.ConfusionMatrixDisplay(confusion_matrix=cm_normalized, display_labels=labels)
disp_norm.plot(ax=axes[1], cmap='cividis_r', values_format='.2f', colorbar=False)
axes[1].set_title('Confusion Matrix – Normalized')
axes[1].set_xlabel('Predicted')
axes[1].set_ylabel('Actual')

plt.tight_layout()
plt.show()

count_path = "outputs/confusion_matrix_counts.png"

fig.savefig(count_path) 
print(f"✅ Saved combined confusion matrix plot to {count_path}")