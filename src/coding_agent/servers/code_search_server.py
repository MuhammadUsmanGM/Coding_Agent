"""
Code Search & Navigation Tool
Scans local project files for function/class/TODO definitions.
"""
from flask import Flask, request, jsonify
import os
import re
import asyncio
import aiofiles

app = Flask(__name__)
ROOT = '/path/to/code'  # This will be set dynamically

PATTERNS = {
    "function": re.compile(r'def\s+(\w+)\s*\('),
    "class": re.compile(r'class\s+(\w+)'),
    "todo": re.compile(r'#\s*TODO(.*)')
}

def search_files(pattern, root_dir):
    async def _async_search_files(pattern, root_dir):
        results = []
        loop = asyncio.get_event_loop()

        # Run os.walk in a separate thread to avoid blocking the event loop
        for dirpath, _, filenames in await loop.run_in_executor(None, lambda: list(os.walk(root_dir))):
            for fname in filenames:
                if fname.endswith('.py'):
                    path = os.path.join(dirpath, fname)
                    try:
                        async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                            # Read line by line asynchronously
                            i = 0
                            async for line in f:
                                i += 1
                                m = pattern.search(line)
                                if m:
                                    results.append({
                                        'file': os.path.relpath(path, start=root_dir),
                                        'line': i,
                                        'match': m.group(0)
                                    })
                    except Exception:
                        # Skip files that can't be read
                        continue
        return results
    return asyncio.run(_async_search_files(pattern, root_dir))

@app.route('/search', methods=['GET'])
def search():
    search_type = request.args.get('type', 'function')
    pattern = PATTERNS.get(search_type, PATTERNS['function'])
    root_dir = request.args.get('root', ROOT)
    return jsonify(search_files(pattern, root_dir))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9300)