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

df_sample_reviewed = df_sample_reviewed[
    ~df_sample_reviewed['reality'].isin(['UNCLEAR']) &
    ~df_sample_reviewed['outcome'].isin(['UNCLEAR'])
    ]

cm = metrics.confusion_matrix(df_sample_reviewed['reality'], df_sample_reviewed['outcome'])

print("The confusion matrix for your predictions is:")
print(cm)

print(f'The accuracy of your model is: {metrics.accuracy_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'])}')
print(f'The recall of your model is: {metrics.recall_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'], average="weighted")}')
print(f'The precision of your model is: {metrics.precision_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'], average="weighted")}')
print(f'The F1-score of your model is: {metrics.f1_score(df_sample_reviewed['reality'], df_sample_reviewed['outcome'], average="weighted")}')


disp = metrics.ConfusionMatrixDisplay(confusion_matrix=cm)
class_names = ['Dismissed', 'Granted']

# Display confusion matrix with labels
disp = metrics.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(cmap='cividis_r')

plt.title('Confusion Matrix')
plt.xlabel('Predicted label')
plt.ylabel('True label')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()