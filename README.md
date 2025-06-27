# court-of-appeal

📚 Court of Appeal Case Processor

This project automates the scraping, processing, and classification of UK Court of Appeal judgments. It uses Natural Language Processing (NLP) with spaCy to detect and label appeal outcomes (GRANTED, DISMISSED, or UNCLEAR) from legal documents.

🧱 Project Structure

Script	Purpose

scraper.py	Downloads and stores legal case data from the Court of Appeal website (or other legal data source).
process_legal_cases.py	Cleans, formats, and structures the raw scraped data into a consistent format.
appeal_verdict_identifier.py	Applies rule-based NLP to identify and classify appeal outcomes from the full text of judgments.

🧠 How It Works

Scraping (scraper.py)
Collects cases by year or date, extracting raw legal texts and metadata for each case.

Processing (process_legal_cases.py)
Preprocesses and formats raw case data — e.g., removing HTML, fixing encoding, normalizing structure — and saves the output as .pkl files.

Verdict Classification (appeal_verdict_identifier.py)
Uses spaCy's Matcher to identify phrases indicating whether an appeal was granted, dismissed, or unclear. Matches are based on curated patterns of legal language (e.g. "the appeal is dismissed", "I would allow the appeal", etc.).
