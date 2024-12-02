import urllib
import requests
import pdfplumber
import openai
import logging
import re
import os
from bs4 import BeautifulSoup
from fpdf import FPDF

# Set OpenAI API key
openai.api_key = "your_api_key"

# Extract the text from a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if not text.strip():
            logging.warning(f"No text extracted from {pdf_path}.")
        else:
            logging.info(f"Extracted text length: {len(text)}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return None

def get_abstract_and_full_text_links(pubmed_url):
    """Scrape PubMed to get the abstract and full-text PDF URL."""
    try:
        response = requests.get(pubmed_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch PubMed page: {pubmed_url}")
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract abstract
        abstract_section = soup.find('div', class_='abstract')
        abstract_text = ""
        if abstract_section:
            paragraphs = abstract_section.find_all('p')
            abstract_text = "\n".join([p.get_text() for p in paragraphs if p.get_text()])

        # Extract full-text links
        full_text_section = soup.find('div', class_='full-text-links-list')
        full_text_links = []
        if full_text_section:
            links = full_text_section.find_all('a', href=True)
            for link in links:
                full_url = link['href']
                if full_url.startswith('/'):
                    full_url = f"https://{response.url.split('/')[2]}{full_url}"
                full_text_links.append(full_url)

        return abstract_text.strip(), full_text_links
    except Exception as e:
        logging.error(f"Error scraping PubMed page: {e}")
        return None, None

def download_or_extract_content(full_text_links, save_path, pubmed_id):
    """Attempt to download the PDF or extract content as fallback."""
    headers = {"User-Agent": "Mozilla/5.0"}
    for link in full_text_links:
        try:
            # Encode any special characters in the URL
            base_link, sep, remainder = link.partition("(")
            encoded_remainder = urllib.parse.quote(f"{sep}{remainder}")
            combined_link = f"{base_link}{encoded_remainder}"

            logging.info(f"Attempting to access: {combined_link}")
            response = requests.get(combined_link, headers=headers, timeout=10)
            if response.status_code != 200:
                logging.warning(f"Failed to access: {combined_link}")
                continue

            # Search for PDF links on the page
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = [a['href'] for a in soup.find_all('a', href=True) if 'pdf' in a['href'].lower()]

            for pdf_link in pdf_links:
                if not pdf_link.startswith("http"):
                    pdf_link = urllib.parse.urljoin(combined_link, pdf_link)
                logging.info(f"Found PDF link: {pdf_link}")

                pdf_response = requests.get(pdf_link, stream=True, timeout=10)
                if pdf_response.status_code == 200 and 'pdf' in pdf_response.headers.get('Content-Type', ''):
                    pdf_save_path = f"papers/{pubmed_id}.pdf"  # Save with PubMed ID
                    with open(pdf_save_path, 'wb') as f:
                        for chunk in pdf_response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    logging.info(f"Downloaded PDF to {pdf_save_path}")
                    return True

            # Extract entire content if no PDF is found
            article_text = soup.get_text(separator="\n")
            save_text_as_pdf(article_text, f"papers/{pubmed_id}.pdf")
            logging.info("PDF created from extracted content.")
            return False

        except requests.RequestException as e:
            logging.error(f"Error accessing {combined_link}: {e}")
    return False

def save_text_as_pdf(text, save_path):
    """Save extracted text as a PDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Handle problematic characters in the text
    text = text.replace('\u2026', '...')  # Replace ellipsis with regular text
    for line in text.split("\n"):
        pdf.cell(0, 10, line.encode('latin-1', 'ignore').decode('latin-1'), ln=True)  # Ignore non-latin-1 chars
    pdf.output(save_path)

def extract_results_section(text):
    """Extract the 'Results' section from the article."""
    results_keywords = ['Results', 'Conclusion', 'Findings']
    pattern = re.compile(r'(' + '|'.join(results_keywords) + r').*?((?:[A-Za-z0-9\s]+[.:]){3,})', re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(0).strip()
    logging.warning("Results section not found.")
    return None

def summarize_content(content):
    """Summarize the provided content using OpenAI."""
    try:
        if len(content) < 1000:
            logging.warning("Content too short for summarization.")
            return content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following scientific content."},
                {"role": "user", "content": content[:4000]}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"Error with OpenAI API: {e}")
        return content

def save_summary_and_results(summary, results, pubmed_id):
    """Save the summary and results to separate files."""
    try:
        os.makedirs("summaries", exist_ok=True)
        os.makedirs("tables", exist_ok=True)

        summary_path = f"summaries/{pubmed_id}_summary.txt"
        with open(summary_path, 'w') as f:
            f.write(summary)

        if results:
            results_path = f"tables/{pubmed_id}_results.txt"
            with open(results_path, 'w') as f:
                f.write(results)
    except Exception as e:
        logging.error(f"Error saving files: {e}")
