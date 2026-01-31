# OFF Slicer API

A lightweight FastAPI service for parsing ingredient lists using the **ingredient-slicer** library. This service can parse ingredient strings into structured data (name, quantity, unit, preparation, etc.) either as a standalone service or integrated with MongoDB for Open Food Facts-style product data.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)
- [Development](#development)

## ✨ Features

- **Lightweight Parsing**: Uses `ingredient-slicer` for fast, rule-based ingredient parsing (no heavy NLP models)
- **Standalone Operation**: Works without MongoDB for ad-hoc ingredient parsing
- **MongoDB Integration**: Optional integration with MongoDB for barcode-based product lookups
- **Smart Splitting**: Intelligently splits comma-separated ingredient lists while preserving nested structures
- **HTML Viewer**: Built-in HTML endpoints for quick testing and visualization
- **Docker Support**: Full containerization with Docker and Docker Compose
- **Error Handling**: Graceful error handling with detailed error messages

## 🛠 Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **ingredient-slicer**: Python library for parsing ingredient strings
- **MongoDB**: Optional database for product storage (Open Food Facts format)
- **Pydantic**: Data validation and serialization
- **Docker**: Containerization for easy deployment

## 📦 Prerequisites

- Python 3.9–3.12 (recommended: 3.11)
- (Optional) MongoDB 6+ if you want to use barcode endpoints
- (Optional) Docker + Docker Compose for containerized deployment

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd off-slicer-api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```env
# MongoDB Configuration (Optional)
MONGO_URI=mongodb://localhost:27017
MONGO_DB=off
MONGO_COLLECTION=products

# Server Configuration
PORT=8001
```

**Note**: If MongoDB is not configured, the service will still run and the `/parse` endpoints will work. Only the `/ingredients/*` endpoints require MongoDB.

## 💻 Usage

### Running the API

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --port 8001

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

The API will be available at `http://127.0.0.1:8001`

### Quick Tests

#### Ad-hoc Parsing (No MongoDB Required)

```bash
# GET request
curl "http://127.0.0.1:8001/parse?text=3%20tbsp%20unsalted%20butter,%20softened"

# POST request
curl -X POST "http://127.0.0.1:8001/parse" \
  -H "Content-Type: application/json" \
  -d '{"text": "2 (15-oz) cans chickpeas, rinsed and drained"}'
```

#### HTML Viewer

Visit in your browser:
```
http://127.0.0.1:8001/parse/html?text=2%20(15-oz)%20cans%20chickpeas,%20rinsed%20and%20drained
```

#### MongoDB-backed Endpoints (After Seeding)

```bash
# Seed test data
python scripts/seed_off.py

# Get parsed ingredients by barcode
curl "http://127.0.0.1:8001/ingredients/demo-0001/parsed"
```

## 📡 API Endpoints

### Health Check

- **GET** `/health`
  - Returns: `{"status": "ok"}`
  - Description: Simple health check endpoint

### Ad-hoc Parsing (No MongoDB Required)

- **GET** `/parse?text=<ingredient_string>`
  - Query Parameters:
    - `text` (required): Comma-separated ingredient string
  - Returns: `ParsedResponse` with parsed ingredients
  - Example: `/parse?text=3%20tbsp%20butter,%20sugar`

- **POST** `/parse`
  - Request Body: `{"text": "<ingredient_string>"}`
  - Returns: `ParsedResponse` with parsed ingredients
  - Example:
    ```json
    {
      "text": "3 tbsp unsalted butter, softened, sugar (12%)"
    }
    ```

- **GET** `/parse/html?text=<ingredient_string>`
  - Query Parameters:
    - `text` (required): Comma-separated ingredient string
  - Returns: HTML page with formatted parsing results
  - Description: Visual HTML viewer for quick testing

### MongoDB-backed Endpoints (Requires MongoDB)

- **GET** `/ingredients/{barcode}`
  - Path Parameters:
    - `barcode` (required): Product barcode
  - Returns: `IngredientOut` with raw ingredient text
  - Example: `/ingredients/demo-0001`

- **GET** `/ingredients/{barcode}/parsed`
  - Path Parameters:
    - `barcode` (required): Product barcode
  - Returns: `ParsedResponse` with parsed ingredients array
  - Example: `/ingredients/demo-0001/parsed`

- **GET** `/ingredients/{barcode}/parsed/html`
  - Path Parameters:
    - `barcode` (required): Product barcode
  - Returns: HTML page with formatted parsing results
  - Description: HTML viewer for barcode-based parsing

- **GET** `/ingredients/parsed?limit=10`
  - Query Parameters:
    - `limit` (optional, default: 10, max: 50): Number of products to parse
  - Returns: Array of `ParsedResponse` objects
  - Description: Batch parsing of first N products in database

### Response Schema

#### ParsedResponse

```json
{
  "barcode": "string",
  "ingredients_raw": "string",
  "parsed": [
    {
      "raw": "string",
      "name": "string | null",
      "amount": {
        "quantity": "number | null",
        "unit": "string | null"
      } | null,
      "preparation": "string | null",
      "comment": "string | null",
      "confidence": "number | null",
      "error": "string | null"
    }
  ]
}
```

#### IngredientOut

```json
{
  "barcode": "string",
  "ingredients": "string | null"
}
```

## 📁 Project Structure

```
off-slicer-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application and routes
│   ├── models.py               # Pydantic models
│   ├── utils.py                # Utility functions (smart_split, strip_tags)
│   ├── core/
│   │   └── config.py           # Configuration and MongoDB setup
│   └── parsing/
│       └── slicer_adapter.py  # ingredient-slicer integration
├── scripts/
│   └── seed_off.py             # MongoDB seeding script
├── tests/
│   └── test_parse.py           # Unit tests
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── Makefile                    # Make commands for common tasks
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🧪 Testing

Run the test suite:

```bash
# Using pytest
pytest -q

# Or using Make
make test
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

This will start both the API and MongoDB:

```bash
docker compose up --build
```

The API will be available at `http://127.0.0.1:8001`

### Using Docker Only

```bash
# Build the image
docker build -t off-slicer-api:local .

# Run the container
docker run --rm -p 8001:8001 --env-file .env off-slicer-api:local
```

**Note**: When using Docker only (without Compose), ensure MongoDB is accessible via the `MONGO_URI` in your `.env` file, or the service will run in standalone mode.

## 🔧 Development

### Make Commands

The project includes a `Makefile` with common tasks:

```bash
# Setup virtual environment and install dependencies
make setup

# Run the API in production mode
make run

# Run the API in development mode (with auto-reload)
make dev

# Run tests
make test

# Seed MongoDB with test data
make seed
```

### Key Components

1. **`app/main.py`**: Main FastAPI application with all route handlers
2. **`app/parsing/slicer_adapter.py`**: Adapter for `ingredient-slicer` library, converts output to standardized format
3. **`app/utils.py`**: Utility functions for smart ingredient splitting and HTML tag removal
4. **`app/core/config.py`**: Configuration management and MongoDB connection setup
5. **`app/models.py`**: Pydantic models for request/response validation

### How It Works

1. **Ingredient Splitting**: The `smart_split()` function uses regex to split comma-separated ingredients while preserving nested parentheses, brackets, and braces.

2. **Parsing**: Each ingredient piece is passed to `ingredient-slicer`, which extracts:
   - Food name
   - Quantity and unit
   - Preparation instructions
   - Additional metadata

3. **Error Handling**: If parsing fails for an ingredient, it's included in the response with error details, allowing partial success.

4. **MongoDB Integration**: When MongoDB is configured, the service can look up products by barcode and parse their ingredient lists from Open Food Facts-style documents.

## 📝 Notes

- This service uses **ingredient-slicer** exclusively for parsing. No heavyweight NLP models are required.
- The output schema includes: `name`, `amount.quantity`, `amount.unit`, `preparation`, `comment`, and `confidence` (currently always `None`).
- MongoDB integration is optional. The service gracefully handles missing MongoDB configuration.
- The service supports both English (`ingredients_text_en`) and generic (`ingredients_text`) ingredient fields from Open Food Facts format.

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

---

**Built with FastAPI and ingredient-slicer**
