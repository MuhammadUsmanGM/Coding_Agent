# Package Inspector Server

## Overview
The Package Inspector Server probes installed Python packages to retrieve information about them, including license details, potential vulnerabilities, and dependencies. It works offline using pip and related tools. It runs on port 10400.

## Key Features

### Package Information
- Retrieves detailed metadata about installed packages
- Provides summary, author, license, homepage, and other package details
- Lists files included in the package
- Shows location where the package is installed

### Dependency Analysis
- Retrieves the list of dependencies for a package
- Shows a simulated dependency tree
- Identifies direct dependencies of a package

### Vulnerability Checking
- Simulated vulnerability checking (in offline mode)
- Shows known vulnerabilities for packages
- Provides severity and description for each vulnerability

### Package Listing
- Lists all installed packages in the environment
- Shows package names and their versions

## API Endpoints

### POST /inspect
Inspect a specific Python package for information, dependencies, and vulnerabilities.

**Request:**
```json
{
  "package": "requests"
}
```

**Response:**
```json
{
  "package": {
    "name": "requests",
    "version": "2.31.0",
    "summary": "Python HTTP for Humans.",
    "description": "...",
    "author": "Kenneth Reitz",
    "author_email": "me@kennethreitz.org",
    "license": "Apache-2.0",
    "homepage": "https://requests.readthedocs.io",
    "requires_dist": ["certifi", "charset-normalizer", "idna", "urllib3"],
    "files_count": 33,
    "location": "/path/to/site-packages"
  },
  "vulnerabilities": {
    "package": "requests",
    "version": "2.31.0",
    "vulnerabilities": [
      {
        "id": "CVE-2023-1234",
        "severity": "medium",
        "description": "Simulated vulnerability for demonstration"
      }
    ],
    "count": 1
  },
  "dependencies": {
    "package": "requests",
    "dependencies": ["certifi", "charset-normalizer", "idna", "urllib3"],
    "count": 4
  },
  "inspection_time": "offline"
}
```

### GET /list_packages
List all installed packages in the environment.

**Response:**
```json
{
  "packages": [
    {
      "name": "requests",
      "version": "2.31.0"
    },
    {
      "name": "flask",
      "version": "2.3.2"
    }
  ],
  "count": 2
}
```

## Usage Examples

### Inspecting a Package
```python
import requests

response = requests.post('http://localhost:10400/inspect', json={
    'package': 'requests'
})

result = response.json()
package_info = result['package']
print(f"Package: {package_info['name']}")
print(f"Version: {package_info['version']}")
print(f"License: {package_info['license']}")
print(f"Dependencies: {result['dependencies']['dependencies']}")
```

### Listing All Packages
```python
import requests

response = requests.get('http://localhost:10400/list_packages')

result = response.json()
print(f"Found {result['count']} packages:")
for pkg in result['packages']:
    print(f"  - {pkg['name']}: {pkg['version']}")
```

## Implementation Notes

### Offline Operation
This server operates entirely offline using Python's built-in metadata capabilities (importlib.metadata). It doesn't require internet access to retrieve basic package information.

### Vulnerability Simulation
The vulnerability checking is simulated in the current implementation. A production version would connect to a vulnerability database like PyUp's safety or similar.

### Dependency Tree
The dependency tree is simulated. A more advanced implementation could use tools like pipdeptree for accurate dependency information.

## Security Considerations
- Only inspects packages from the local environment
- No external connections for basic package information
- Vulnerability information is read-only and simulated in this implementation

## Error Handling
- 400: When package name is missing in inspect requests
- 404: When requested package is not found
- 500: For unexpected server errors during package inspection