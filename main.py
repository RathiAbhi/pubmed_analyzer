import logging
import os
import re
from utils import (
    get_abstract_and_full_text_links,
    download_or_extract_content,
    extract_text_from_pdf,
    extract_results_section,
    summarize_content,
    save_summary_and_results
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_pubmed_id(pubmed_url):
    """Extract the PubMed ID from the given PubMed URL."""
    match = re.search(r"(\d+)$", pubmed_url)  # Match the number at the end of the URL
    if match:
        return match.group(1)
    return None

def main(pubmed_url, paper_id):
    """Main function to process a PubMed URL."""
    logging.info(f"Processing PubMed URL: {pubmed_url}")

    # Extract PubMed ID from URL for naming files
    pubmed_id = extract_pubmed_id(pubmed_url)
    if not pubmed_id:
        logging.error(f"Failed to extract PubMed ID from URL: {pubmed_url}")
        return

    # Create directories for saving outputs
    os.makedirs("summaries", exist_ok=True)
    os.makedirs("papers", exist_ok=True)
    os.makedirs("tables", exist_ok=True)

    # Step 1: Get abstract and full-text links
    abstract, full_text_links = get_abstract_and_full_text_links(pubmed_url)
    if not abstract:
        logging.error("Failed to extract abstract.")
    else:
        logging.info("Abstract extracted successfully.")

    # Step 2: Attempt to download PDF or extract content
    pdf_save_path = f"papers/{pubmed_id}.pdf"
    pdf_downloaded = download_or_extract_content(full_text_links, pdf_save_path, pubmed_id)

    if pdf_downloaded:
        logging.info("PDF downloaded successfully.")
        # Step 3: Extract text from the downloaded PDF
        extracted_text = extract_text_from_pdf(pdf_save_path)
    else:
        logging.info("No PDF found. Using extracted article content.")
        extracted_text = None

    # Step 4: Summarize content
    if extracted_text:
        summary = summarize_content(extracted_text)
    else:
        logging.warning("No text extracted from PDF.")
        summary = summarize_content(abstract)

    # Step 5: Extract the results section from the text
    results = None
    if extracted_text:
        results = extract_results_section(extracted_text)

    # Step 6: Save summary and results
    save_summary_and_results(summary, results, pubmed_id)

if __name__ == "__main__":
    if not os.path.isfile("paper_urls.txt"):
        logging.error("The file 'paper_urls.txt' does not exist. Please create it and add URLs.")
    else:
        with open("paper_urls.txt", "r") as file:
            urls = [line.strip() for line in file if line.strip()]

        for url in urls:
            main(url, None)
