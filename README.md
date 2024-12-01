# PubMed Paper Analyzer

## **Project Overview**

The PubMed Paper Analyzer is a Python-based tool designed to download scientific papers from PubMed, extract the text from the PDFs, generate summaries, and extract the main results table from each paper. The application can process multiple papers concurrently, making it scalable and efficient. A simple REST API is also included for triggering the download, summarization, and table extraction process.

## **Project Structure**

pubmed_analyzer/ 
- papers/ (Folder where downloaded PDFs are saved) 
- summaries/ (Folder where paper summaries are saved)
- tables/ (Folder where extracted tables are saved) 
- paper_urls.txt (A text file containing the list of PubMed URLs to process)
- main.py (Main script to execute the paper analysis process)
- utils.py (Utility functions for downloading papers, summarizing, etc)
- api.py (REST API to trigger the process and retrieve results)
- requirements.txt (Python dependencies for the project)
- README.md (This file)


## **Setup and Installation**

### 1. **Clone the repository:**

git clone <repository_url> cd pubmed_analyzer


### 2. **Install Dependencies:**

Make sure Python 3.7+ is installed. Then, install the required dependencies by running:

pip install -r requirements.txt


This will install the necessary libraries for the project, such as `requests`, `pdfplumber`, `openai`, `flask`, `pandas`, etc.

### 3. **Configure OpenAI API Key:**

For paper summarization, an OpenAI API key is required. Set up your OpenAI key by creating an `.env` file in the project root with the following content:

OPENAI_API_KEY=your_openai_api_key


You can get your OpenAI API key from [here](https://platform.openai.com/account/api-keys).

### 4. **Prepare the Paper URLs:**

Create a file named `paper_urls.txt` in the project root directory and populate it with the URLs of PubMed papers, one URL per line.

Example:
https://someurl.com

https://someurl.com ...


## **How to Run the Application**

### 1. **Run the Main Script:**

To download papers, generate summaries, and extract tables for the URLs in `paper_urls.txt`, run the following command:

python main.py


This will:
- Download each paper from PubMed.
- Extract text from the PDFs.
- Generate a summary for each paper.
- Extract the main results table from each paper.
- Save the results (summaries and tables) in the respective directories (`summaries/`, `tables/`).

### 2. **Using the REST API (Optional)**

The project includes a simple REST API to trigger the process programmatically.

To start the API server, run:

python api.py


Once the server is running, you can trigger the download and analysis process via the following API endpoints:

- **POST /analyze**  
  Starts the process of downloading, summarizing, and extracting tables for the papers.  
  Example:  
curl -X POST http://127.0.0.1:5000/analyze


- **GET /summary/<paper_id>**  
Retrieve the summary for a specific paper.  
Example:  
curl http://127.0.0.1:5000/summary/39368806


- **GET /table/<paper_id>**  
Retrieve the extracted results table for a specific paper.  
Example:  
curl http://127.0.0.1:5000/table/39368806


## **Logic and Resources Used**

### **Core Logic:**

1. **Downloading Papers:**  
 The `download_paper` function fetches PDFs from the URLs listed in `paper_urls.txt` using the `requests` library. It checks that the content is indeed a PDF before saving it.

2. **Extracting Text from PDFs:**  
 Once a PDF is downloaded, the `extract_text_from_pdf` function uses `pdfplumber` to extract text. If the text extraction fails due to an invalid or corrupt PDF, an error is logged.

3. **Summarizing Papers:**  
 The paper text is passed to OpenAI's GPT model (using the `openai` library) for summarization. The summary is a concise 250-word description capturing the main objectives, methods, and results of the paper.

4. **Extracting Results Tables:**  
 The `extract_main_table` function uses `pdfplumber` to locate and extract the main results table from the PDF. The extracted table is saved in JSON format for easy use and reference.

5. **Concurrency and Rate Limiting:**  
 The download process respects rate limits by implementing retry logic and exponential backoff in case of errors or HTTP 429 (rate-limited) responses.

### **Libraries and Resources:**

- **`requests`:** For making HTTP requests to download PDFs from PubMed.
- **`pdfplumber`:** For extracting text and tables from PDF files.
- **`openai`:** For generating concise summaries using the GPT model.
- **`pandas`:** For handling and saving extracted tables in a structured format (JSON).
- **`flask`:** For implementing the RESTful API to trigger the process and retrieve results.

---

## **Error Handling**

- **Download Errors:** If a paper URL is incorrect, or the response is not a valid PDF, the system logs an error and skips the paper.
- **Text Extraction Errors:** If text extraction fails for a paper (e.g., corrupt PDF), an error is logged and the paper is skipped.
- **Rate Limiting:** The system handles rate-limited responses by implementing retry logic with exponential backoff.

---

## **License**

This project is intended solely for educational and study purposes. It is designed for personal learning and academic assignments. All data, including scientific papers, should be used exclusively for this project and not shared, redistributed, or used for commercial purposes.


