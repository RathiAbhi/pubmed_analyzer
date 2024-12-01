import os
import logging
from concurrent.futures import ThreadPoolExecutor
from utils import download_paper, extract_text_from_pdf, summarize_paper, save_summary, extract_main_table

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_urls(file_path='paper_urls.txt'):
    """Load PubMed URLs from the given file."""
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(urls)} URLs from {file_path}")
        return urls
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        return []

def process_paper(url):
    """Download, summarize, and extract data from a single paper."""
    try:
        pdf_path = download_paper(url)
        if pdf_path:
            text = extract_text_from_pdf(pdf_path)
            if text:
                summary = summarize_paper(text)
                save_summary(summary, pdf_path)
                extract_main_table(pdf_path)
    except Exception as e:
        logging.error(f"Error processing paper {url}: {e}")

def main():
    urls = load_urls()
    if urls:
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(process_paper, urls)
        logging.info("Completed processing all papers.")
    else:
        logging.warning("No URLs to process.")

if __name__ == '__main__':
    main()
