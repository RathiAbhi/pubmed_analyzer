import requests
import pdfplumber
import openai
import pandas as pd
import logging
from bs4 import BeautifulSoup
import time
import json

# Set your OpenAI API key
openai.api_key = "YOUR_KEY"


# Function to get the full-text PDF URL from PubMed
def get_full_text_pdf_url(pubmed_url):
    try:
        response = requests.get(pubmed_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch PubMed page: {pubmed_url}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        # Locate the "Full Text Sources" links
        full_text_section = soup.find('div', class_='full-text-links-list')
        if not full_text_section:
            logging.error(f"No full-text section found for {pubmed_url}")
            return None

        # Get the first external full-text link (or customize if needed)
        link = full_text_section.find('a', href=True)
        if link:
            full_text_url = link['href']
            logging.info(f"Found full-text link: {full_text_url}")
            return full_text_url
        else:
            logging.error(f"No external full-text link found in {pubmed_url}")
            return None
    except Exception as e:
        logging.error(f"Error scraping PubMed page: {e}")
        return None


# Download the paper from the full-text link
def download_paper(url, save_path):
    full_text_url = get_full_text_pdf_url(url)
    if not full_text_url:
        logging.error(f"Unable to find full-text PDF for: {url}")
        return False

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(full_text_url, stream=True, timeout=10)
            if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                logging.info(f"Downloaded PDF to {save_path}")
                return True
            elif response.status_code == 429:
                logging.warning(f"Rate limited. Retrying... ({attempt + 1}/{retries})")
                time.sleep(5 * (attempt + 1))
            else:
                logging.error(f"Failed to download PDF, status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            logging.error(f"Error downloading PDF: {e}")
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


# Save the summary to a file
def save_summary(summary, summary_path):
    try:
        with open(summary_path, 'w') as f:
            f.write(summary)
        logging.info(f"Summary saved to {summary_path}.")
    except Exception as e:
        logging.error(f"Error saving summary: {e}")
