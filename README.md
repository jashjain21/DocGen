# DocGen

DocGen is an offline PDF report generator that converts structured data (like invoices) into well-formatted PDF documents. It provides both a REST API and a command-line interface for generating PDFs, with built-in storage management and error handling.

## Features

- Generate PDFs from JSON invoice data
- Customizable page settings (size, orientation, margins)
- REST API with FastAPI
- Command-line interface for batch processing
- Organized file storage with manifest tracking
- Template-based rendering with Jinja2
- Error handling with custom exceptions
- Offline operation (no external dependencies)

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -e .`

## Usage

### Starting the API Server

```bash
python src/main.py
```

The server will run on `http://127.0.0.1:8000`.

### API Endpoints

#### POST /generate
Generate a PDF from invoice JSON.

**Request Body:**
```json
{
  "invoice_number": "INV-001",
  "date": "2023-10-01",
  "customer": {
    "name": "John Doe",
    "address": "123 Main St"
  },
  "line_items": [
    {
      "description": "Service",
      "quantity": 2,
      "unit_price": 50.0
    }
  ]
}
```

**Query Parameters:**
- `page_size`: "a4", "letter", "legal" (default: "a4")
- `orientation`: "portrait", "landscape" (default: "portrait")
- `margins`: e.g., "10mm" (default: "10mm")
- `save_to_disk`: true/false (default: false)

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/generate?page_size=a4&save_to_disk=true" \
  -H "Content-Type: application/json" \
  -d @invoice.json \
  --output invoice.pdf
```

#### GET /documents
List generated documents.

**Query Parameters:**
- `year`: Filter by year
- `month`: Filter by month
- `invoice_number`: Filter by invoice number

**Example:**
```bash
curl "http://127.0.0.1:8000/documents?year=2023"
```

#### GET /document/{filename}
Download a specific document.

**Example:**
```bash
curl "http://127.0.0.1:8000/document/INV-001.pdf" --output downloaded.pdf
```

#### DELETE /document/{filename}
Delete a document.

**Example:**
```bash
curl -X DELETE "http://127.0.0.1:8000/document/INV-001.pdf"
```

#### GET /health
Check service health.

**Example:**
```bash
curl "http://127.0.0.1:8000/health"
```

### CLI Usage

#### Generate PDF from JSON
```bash
python src/cli.py generate invoice.json -o output.pdf
```

#### Batch Process JSON Files
```bash
python src/cli.py batch json_folder/
```

#### List Documents
```bash
python src/cli.py list
python src/cli.py list -y 2023 -m 10
```

## Project Structure

- `src/`: Source code
  - `main.py`: FastAPI application
  - `cli.py`: Command-line interface
  - `engine.py`: Template rendering and PDF generation
  - `storage.py`: File management
  - `schema.py`: Pydantic models
  - `exceptions.py`: Custom exceptions
  - `templates/`: Jinja2 templates
  - `static/`: Static assets
- `tests/`: Unit tests
- `output/`: Generated PDFs and manifest

## Error Handling

The system uses custom exceptions for different error types:
- `TemplateError`: Template rendering issues
- `PDFGenerationError`: PDF creation failures
- `InvalidDocumentError`: Invalid input data
- `StorageError`: File storage problems

All errors are handled gracefully with appropriate HTTP status codes and JSON responses.

## Testing

Run tests:
```bash
pytest tests/
```

## Requirements

- Python 3.8+
- Dependencies: FastAPI, Uvicorn, Jinja2, WeasyPrint, Pydantic, tqdm

## License

MIT
