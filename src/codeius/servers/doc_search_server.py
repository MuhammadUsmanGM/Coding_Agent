"""
Local Documentation Tool
Finds .md files and extracts answers locally.
"""
from flask import Flask, request, jsonify
import os
import asyncio
import aiofiles

app = Flask(__name__)
ROOT = '/path/to/docs'  # This will be set dynamically

@app.route('/doc_search', methods=['GET'])
async def doc_search():
    q = request.args.get('q', '').lower()
    root_dir = request.args.get('root', ROOT)

    if not q:
        return jsonify({'error': 'No query provided'}), 400

    results = []
    loop = asyncio.get_event_loop()

    # Run os.walk in a separate thread to avoid blocking the event loop
    for dirpath, _, filenames in await loop.run_in_executor(None, lambda: list(os.walk(root_dir))):
        for fname in filenames:
            if fname.lower().endswith(('.md', '.txt', '.rst')):
                filepath = os.path.join(dirpath, fname)
                try:
                    async with aiofiles.open(filepath, mode='r', encoding='utf-8', errors='ignore') as f:
                        line_num = 0
                        async for line in f:
                            line_num += 1
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9600)