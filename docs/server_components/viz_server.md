# Visualization Server

## Overview
The Visualization Server generates data visualizations such as plots and charts based on code metrics, test coverage, or database query results using matplotlib. It runs on port 10200 and returns images in base64-encoded format.

## Key Features

### Chart Types
- Bar charts for categorical data
- Line charts for trends over time
- Pie charts for proportional data
- Scatter plots for correlation analysis
- Default to bar chart if type is not specified

### Data Visualization
- Plot custom data provided by the client
- Generate code metrics visualizations (test coverage, complexity, file sizes)
- Visualize database query results
- Supports axis labels and custom titles

### Base64 Image Output
- Generates images using matplotlib with non-interactive backend
- Returns plots as base64-encoded PNG images
- Client applications can easily embed the returned images

## API Endpoints

### POST /plot
Generate a custom plot based on provided data.

**Request:**
```json
{
  "type": "bar",  // "bar", "line", "pie", or "scatter"
  "data": [
    ["Category A", 10],
    ["Category B", 20],
    ["Category C", 15]
  ],
  "title": "Sample Data Visualization",
  "xlabel": "Categories",
  "ylabel": "Values"
}
```

**Response:**
```json
{
  "success": true,
  "plot": "iVBORw0KGgoAAAANSUhEUgAAAY... (base64 image data)",
  "type": "bar",
  "title": "Sample Data Visualization"
}
```

### POST /plot_metrics
Generate plots for code metrics.

**Request:**
```json
{
  "metric_type": "coverage"  // "coverage", "complexity", or "size"
}
```

**Response:**
```json
{
  "success": true,
  "plot": "iVBORw0KGgoAAAANSUhEUgAAAY... (base64 image data)",
  "metric_type": "coverage",
  "title": "Test Coverage Over Time"
}
```

### POST /plot_database
Generate plots for database query results.

**Request:**
```json
{
  "query_results": [10, 20, 15, 25],
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "title": "Sales by Quarter"
}
```

**Response:**
```json
{
  "success": true,
  "plot": "iVBORw0KGgoAAAANSUhEUgAAAY... (base64 image data)",
  "title": "Sales by Quarter"
}
```

## Response Structure

### Success Response
- `success`: Boolean indicating if the operation was successful
- `plot`: Base64-encoded PNG image of the generated plot
- `title`: Title of the plot
- Additional fields depending on the specific endpoint

### Error Response
- `success`: Boolean indicating failure
- `error`: Description of the error that occurred

## Usage Examples

### Creating a Custom Bar Chart
```python
import requests
import base64

response = requests.post('http://localhost:10200/plot', json={
    'type': 'bar',
    'data': [
        ['Jan', 45],
        ['Feb', 52],
        ['Mar', 68],
        ['Apr', 78]
    ],
    'title': 'Monthly Growth',
    'xlabel': 'Month',
    'ylabel': 'Growth (%)'
})

result = response.json()
if result['success']:
    # Save the image to a file
    image_data = base64.b64decode(result['plot'])
    with open('monthly_growth.png', 'wb') as f:
        f.write(image_data)
else:
    print(f"Error: {result['error']}")
```

### Generating Code Metrics Visualization
```python
import requests
import base64

response = requests.post('http://localhost:10200/plot_metrics', json={
    'metric_type': 'complexity'
})

result = response.json()
if result['success']:
    image_data = base64.b64decode(result['plot'])
    with open('complexity_analysis.png', 'wb') as f:
        f.write(image_data)
```

### Creating a Database Query Result Chart
```python
import requests
import base64

response = requests.post('http://localhost:10200/plot_database', json={
    'query_results': [100, 150, 120, 180],
    'labels': ['Product A', 'Product B', 'Product C', 'Product D'],
    'title': 'Product Sales Comparison'
})

result = response.json()
if result['success']:
    image_data = base64.b64decode(result['plot'])
    with open('product_sales.png', 'wb') as f:
        f.write(image_data)
```

## Implementation Notes

### Backend Configuration
The server uses matplotlib with the 'Agg' backend, which is non-interactive and suitable for server environments where no display is available.

### Image Format
All generated plots are returned as PNG images encoded in base64 format, which can be easily embedded in web pages or saved to files.

### Chart Customization
The server supports custom titles and axis labels for all chart types, allowing for better context in the generated visualizations.

## Security Considerations
- Only generates images based on provided data
- No file system access beyond temporary image creation
- All operations happen in memory before encoding to base64

## Error Handling
- 400: When no data is provided for the /plot endpoint
- 400: When invalid metric type is provided for /plot_metrics
- 500: For image generation errors or other unexpected server errors