import requests
import pdfplumber
import openai
import pandas as pd
import logging
import time

# Set your OpenAI API key here
openai.api_key = "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"

# Download the paper from PubMed
def download_paper(url, save_path):
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True, timeout=10)

            # Check if we received the expected response type (PDF)
            if response.status_code == 200:
                # Check if the file is a PDF (based on the Content-Type header)
                if 'application/pdf' in response.headers.get('Content-Type', ''):
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    logging.info(f"Downloaded: {save_path}")
                    return True
                else:
                    logging.error(f"URL does not return a PDF: {url}")
                    break
            elif response.status_code == 429:
                logging.warning(f"Rate limited. Retrying... ({attempt + 1}/{retries})")
                time.sleep(5 * (attempt + 1))  # Exponential backoff
            else:
                logging.error(f"Failed to download {url}, status code: {response.status_code}")
                break
        except requests.RequestException as e:
            logging.error(f"Error downloading {url}: {e}")
    return False

# Extract text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if not text.strip():
            logging.warning(f"No text extracted from {pdf_path}.")
            raise ValueError("Empty text extracted.")
        logging.info(f"Text successfully extracted from {pdf_path}")
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
    return text

# Summarize the paper using OpenAI API
def summarize_paper(text):
    try:
        if len(text) < 1000:
            logging.warning("Text too short for summarization.")
            return "Insufficient text for summarization."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following scientific paper."},
                {"role": "user", "content": text}
            ]
        )
        summary = response['choices'][0]['message']['content'].strip()
        logging.info("Summary successfully generated.")
        return summary
    except openai.error.OpenAIError as e:
        logging.error(f"Error with OpenAI API: {e}")
        return "Error generating summary."

# Extract main results table from the PDF
def extract_main_table(pdf_path, output_csv_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    main_table = max(tables, key=len)  # Get the table with most rows
                    df = pd.DataFrame(main_table)
                    df.to_csv(output_csv_path, index=False)
                    logging.info(f"Table extracted and saved to {output_csv_path}")
                    return True
        logging.warning(f"No tables found in {pdf_path}")
    except Exception as e:
        logging.error(f"Error extracting table from {pdf_path}: {e}")
    return False

# Save the summary to a file
def save_summary(paper_id, summary):
    try:
        summary_file = f"summaries/{paper_id}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)
        logging.info(f"Summary saved for {paper_id}.")
    except Exception as e:
        logging.error(f"Error saving summary for {paper_id}: {e}")