# Web Scraper Server

## Overview
The Web Scraper Server provides offline web scraping capabilities using BeautifulSoup. It can scrape content from static HTML files, local directories, and URLs using CSS selectors. It runs on port 10600.

## Key Features

### Source Support
- Local HTML files
- Local directory structures with HTML files
- Remote URLs (with rate limiting)
- Asynchronous scraping for URLs

### CSS Selectors
- Full CSS selector support using BeautifulSoup
- Extract specific elements by tag, class, ID, or attributes
- Access element text, attributes, and HTML content
- Default to '*' to match all elements

### Rate Limiting
- Built-in rate limiting (5 calls per minute)
- Prevents excessive requests to remote servers
- Preserves server resources for local operations

### Asynchronous Processing
- Asynchronous URL scraping using aiohttp
- Non-blocking operations for better performance
- Thread pool execution for CPU-intensive tasks

## API Endpoints

### POST /scrape
Scrape content from files, directories, or URLs using CSS selectors.

**Request:**
```json
{
  "target": "/path/to/file.html",  // File path, directory path, or URL
  "selector": ".class-name"        // CSS selector (optional, defaults to '*')
}
```

### Response for files and directories:
```json
{
  "file_path": "/path/to/file.html",  // Or directory_path for directories
  "selector": ".class-name",
  "found_elements": 3,
  "results": [
    {
      "tag": "div",
      "text": "Content of the element",
      "attributes": {"class": ["class-name"], "id": "element-id"},
      "html": "<div class=\"class-name\">Content of the element</div>"
    }
  ]
}
```

### Response for URLs:
```json
{
  "url": "https://example.com",
  "selector": ".class-name",
  "found_elements": 2,
  "status_code": 200,
  "results": [
    {
      "tag": "h1",
      "text": "Page Title",
      "attributes": {"class": ["title"]},
      "html": "<h1 class=\"title\">Page Title</h1>"
    }
  ]
}
```

## Response Structure

### File/Directory Response
- `file_path` or `directory_path`: Path to the source
- `selector`: The CSS selector used
- `found_elements` or `total_found`: Number of matching elements
- `results`: Array of matching elements with tag, text, attributes, and HTML

### URL Response
- `url`: The URL that was scraped
- `selector`: The CSS selector used
- `found_elements`: Number of matching elements
- `status_code`: HTTP status code of the response
- `results`: Array of matching elements

## Usage Examples

### Scraping a Local HTML File
```python
import requests

response = requests.post('http://localhost:10600/scrape', json={
    'target': 'docs/reference.html',
    'selector': 'h2'
})

result = response.json()
for element in result['results']:
    print(f"Found heading: {element['text']}")
```

### Scraping a Local Directory
```python
import requests

response = requests.post('http://localhost:10600/scrape', json={
    'target': 'website/pages/',
    'selector': 'a[href]'
})

result = response.json()
print(f"Found {result['total_found']} links in the directory:")
for element in result['results']:
    print(f"  - {element['attributes']['href']} -> {element['text']}")
```

### Scraping a URL
```python
import requests

response = requests.post('http://localhost:10600/scrape', json={
    'target': 'https://example.com',
    'selector': '.content p'
})

result = response.json()
if 'error' not in result:
    print("Extracted paragraphs:")
    for element in result['results']:
        print(f"  - {element['text'][:100]}...")
else:
    print(f"Error: {result['error']}")
```

## Implementation Notes

### Selector Handling
The server uses BeautifulSoup's CSS selector engine to find matching elements. This supports a wide range of CSS selectors including:
- Element selectors: `p`, `div`
- Class selectors: `.class-name`
- ID selectors: `#element-id`
- Attribute selectors: `[href^="http"]`
- Pseudo-selectors: `:first-child`

### Asynchronous Operations
URL scraping is performed asynchronously using aiohttp to improve performance and avoid blocking operations. Local file operations use asyncio with thread pools for file I/O operations.

## Security Considerations
- Only allows scraping of local files and directories in the project
- Validates URL formats to prevent malicious requests
- Implements rate limiting to prevent abuse
- No execution of JavaScript or other active content from scraped pages

## Error Handling
- 400: When no target is provided or invalid target format is used
- 429: When rate limit is exceeded for URL scraping
- 500: For scraping errors or other server-side issues during content extraction