"""
Offline Web Scraping Tool
Scraping static HTML files or local sites with BeautifulSoup, for documentation or data extraction tasks.
"""
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import os
import requests
from urllib.parse import urljoin, urlparse
import re
from ...coding_agent.performance import rate_limit
import asyncio
import aiohttp

app = Flask(__name__)

def is_local_file(path):
    """Check if the provided path is a local file"""
    return os.path.exists(path)

def is_local_directory(path):
    """Check if the provided path is a local directory"""
    return os.path.isdir(path)

def scrape_html_file(file_path, selector):
    """Scrape content from an HTML file using BeautifulSoup"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        elements = soup.select(selector)
        
        results = []
        for elem in elements:
            results.append({
                'tag': elem.name,
                'text': elem.get_text(strip=True),
                'attributes': dict(elem.attrs),
                'html': str(elem)
            })
        
        return {
            'file_path': file_path,
            'selector': selector,
            'found_elements': len(results),
            'results': results
        }
    except Exception as e:
        return {'error': str(e)}

def scrape_local_directory(dir_path, selector):
    """Recursively scrape HTML files in a directory"""
    results = []
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.lower().endswith(('.html', '.htm')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    elements = soup.select(selector)
                    
                    for elem in elements:
                        results.append({
                            'file_path': file_path,
                            'tag': elem.name,
                            'text': elem.get_text(strip=True),
                            'attributes': dict(elem.attrs),
                            'html': str(elem)
                        })
                except Exception as e:
                    # Log the error but continue processing other files
                    print(f"Error processing {file_path}: {str(e)}")
    
    return {
        'directory_path': dir_path,
        'selector': selector,
        'total_found': len(results),
        'results': results
    }

@rate_limit(max_calls=5, time_window=60) # 5 calls per minute
async def scrape_url(url, selector):
    """Scrape content from a URL asynchronously using aiohttp."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.text()

        soup = BeautifulSoup(content, 'html.parser')
        elements = soup.select(selector)
        
        results = []
        for elem in elements:
            results.append({
                'tag': elem.name,
                'text': elem.get_text(strip=True),
                'attributes': dict(elem.attrs),
                'html': str(elem)
            })
        
        return {
            'url': url,
            'selector': selector,
            'found_elements': len(results),
            'status_code': response.status_code,
            'results': results
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/scrape', methods=['POST'])
async def scrape():
    """Scrape content from files, directories, or URLs using CSS selectors asynchronously"""
    try:
        target = request.json.get('target', '')
        selector = request.json.get('selector', '*')  # Default to all elements
        
        if not target:
            return jsonify({'error': 'Target (file, directory, or URL) is required'}), 400
        
        # Check if it's a local file
        if is_local_file(target):
            result = scrape_html_file(target, selector)
            return jsonify(result)
        
        # Check if it's a local directory
        elif is_local_directory(target):
            result = scrape_local_directory(target, selector)
            return jsonify(result)
        
        # Otherwise, treat as URL
        else:
            # Validate that it's a URL
            parsed = urlparse(target)
            if parsed.scheme in ['http', 'https']:
                result = await scrape_url(target, selector)
                return jsonify(result)
            else:
                return jsonify({'error': f'Invalid target: {target}. Must be a valid file path, directory, or URL.'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10600)