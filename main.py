import os
import logging
import time
from utils import download_paper, extract_text_from_pdf, summarize_paper, save_summary, extract_main_table

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to store downloaded PDFs
PAPER_DIRECTORY = 'papers'
SUMMARY_DIRECTORY = 'summaries'
TABLES_DIRECTORY = 'tables'


# Function to read the list of PubMed URLs from a file
def read_paper_urls(file_path):
    with open(file_path, 'r') as file:
        urls = file.readlines()
    return [url.strip() for url in urls]


# Main function to download, summarize and extract tables
def main():
    logging.info("Starting PubMed Paper Analyzer...")

    # Create necessary directories if they don't exist
    os.makedirs(PAPER_DIRECTORY, exist_ok=True)
    os.makedirs(SUMMARY_DIRECTORY, exist_ok=True)
    os.makedirs(TABLES_DIRECTORY, exist_ok=True)

    # Read the URLs from the file
    paper_urls = read_paper_urls('paper_urls.txt')

    # Iterate through each URL
    for url in paper_urls:
        paper_id = url.split('/')[-1].split('?')[0]  # Extract the paper ID from the URL
        pdf_path = os.path.join(PAPER_DIRECTORY, f"{paper_id}.pdf")

        # Download the PDF
        if download_paper(url, pdf_path):
            logging.info(f"Processing paper: {paper_id}")

            # Extract text from the PDF
            try:
                text = extract_text_from_pdf(pdf_path)
                if text:
                    # Summarize the paper
                    summary = summarize_paper(text)
                    summary_path = os.path.join(SUMMARY_DIRECTORY, f"{paper_id}_summary.txt")
                    save_summary(summary, summary_path)

                    # Extract the main table
                    table = extract_main_table(pdf_path)
                    if table:
                        table_path = os.path.join(TABLES_DIRECTORY, f"{paper_id}_table.json")
                        with open(table_path, 'w') as table_file:
                            json.dump(table, table_file)
                        logging.info(f"Table extracted for {paper_id}")
                    else:
                        logging.warning(f"No table found in {paper_id}")
                else:
                    logging.error(f"Failed to extract text from {paper_id}. Skipping.")
            except Exception as e:
                logging.error(f"Error processing {paper_id}: {e}")
        else:
            logging.error(f"Failed to download or process {paper_id}")

    logging.info("All tasks completed.")


if __name__ == '__main__':
    main()