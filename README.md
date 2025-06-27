# 📚 Court of Appeal Case Processor

This project automates the scraping, processing, and classification of UK Court of Appeal judgments. It uses Natural Language Processing (NLP) with spaCy to detect and label appeal outcomes (`GRANTED`, `DISMISSED`, or `UNCLEAR`) from legal documents.

## 🧱 Project Structure

| Script | Purpose |
|--------|---------|
| `scraper.py` | Downloads and stores legal case data from the Court of Appeal website (or other legal data source). |
| `process_legal_cases.py` | Cleans, formats, and structures the raw scraped data into a consistent format. |
| `appeal_verdict_identifier.py` | Applies rule-based NLP to identify and classify appeal outcomes from the full text of judgments. |

## 🧠 How It Works

1. **Scraping (`scraper.py`)**  
   Collects cases by year or date, extracting raw legal texts and metadata for each case.

2. **Processing (`process_legal_cases.py`)**  
   Preprocesses and formats raw case data — e.g., removing HTML, fixing encoding, normalizing structure — and saves the output as `.pkl` files.

3. **Verdict Classification (`appeal_verdict_identifier.py`)**  
   Uses spaCy's `Matcher` to identify phrases indicating whether an appeal was **granted**, **dismissed**, or **unclear**. Matches are based on curated patterns of legal language (e.g. "the appeal is dismissed", "I would allow the appeal", etc.).

## 🛠️ Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/court-of-appeal-case-processor.git
cd court-of-appeal-case-processor
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

3. Install dependencies:
# WIP
```bash
pip install -r requirements.txt
```

4. Download the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Running the Pipeline

### 1. Scrape Cases

```bash
python scraper.py
```

### 2. Process Cases

```bash
python process_legal_cases.py
```

### 3. Identify Appeal Outcomes

```bash
python appeal_verdict_identifier.py
```

## 📦 Outputs

- `data/cases_by_year_processed/` — preprocessed case files
- `data/cases_by_year_with_outcome/` — final outcomes in CSV and Pickle format

## 📋 Example Output

| case_id | year | outcome   |
|---------|------|-----------|
| EWHC123 | 2025 | DISMISSED |
| EWHC456 | 2025 | GRANTED   |
| EWHC789 | 2025 | UNCLEAR   |

## 🧪 Dependencies

- Python 3.7+
- `pandas`
- `spacy`
- `pickle` (built-in)
- `re`, `os`, `datetime` (built-in)

## 🧑‍⚖️ Use Cases

- Legal analytics and decision trend analysis  
- Training data for machine learning in legal NLP  
- Judicial transparency and academic research  

## 📄 License

MIT License. See `LICENSE` for details.
