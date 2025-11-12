"""
Local Documentation Tool
Finds .md files and extracts answers locally.
"""
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
ROOT = '/path/to/docs'  # This will be set dynamically

@app.route('/doc_search', methods=['GET'])
def doc_search():
    q = request.args.get('q', '').lower()
    root_dir = request.args.get('root', ROOT)
    
    if not q:
        return jsonify({'error': 'No query provided'}), 400
        
    results = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith(('.md', '.txt', '.rst')):
                filepath = os.path.join(dirpath, fname)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, start=1):
                            if q in line.lower():
                                results.append({
                                    'file': os.path.relpath(filepath, start=root_dir),
                                    'line': line_num,
                                    'match': line.strip()[:200]  # Limit line length
                                })
                                # Limit results per file to prevent too many matches
                                if len(results) >= 20:
                                    break
                except Exception:
                    # Skip files that can't be read
                    continue
    return jsonify(results[:50])  # Limit total results

if __name__ == '__main__':
    app.run(port=9600)