from flask import Flask, request, jsonify
from utils import download_paper, extract_text_from_pdf, summarize_paper, extract_main_table, save_summary
import os

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_paper():
    urls = request.json.get('urls', [])
    results = []

    for url in urls:
        paper_id = url.split('/')[-2]
        file_path = download_paper(url)
        if file_path:
            text = extract_text_from_pdf(file_path)
            if text:
                summary = summarize_paper(text)
                save_summary(summary, paper_id)
                extract_main_table(file_path)
                results.append({"paper_id": paper_id, "status": "Success"})
            else:
                results.append({"paper_id": paper_id, "status": "Text extraction failed"})
        else:
            results.append({"paper_id": paper_id, "status": "Download failed"})

    return jsonify(results)

@app.route('/results/<paper_id>', methods=['GET'])
def get_results(paper_id):
    summary_path = f"summaries/{paper_id}_summary.txt"
    table_path = f"tables/{paper_id}_table.csv"

    if not os.path.exists(summary_path) and not os.path.exists(table_path):
        return jsonify({"error": "Paper not found"}), 404

    response = {}
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            response['summary'] = f.read()

    if os.path.exists(table_path):
        response['table'] = table_path

    return jsonify(response)

if __name__ == '__main__':
    app.run(port=5000)
