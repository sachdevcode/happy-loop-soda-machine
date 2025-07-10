#  AI-Powered Soda Vending Machine API

A FastAPI-based RESTful API for a soda vending machine that uses AI to process natural language requests.

## Features

- **Natural Language Processing**: Use AI to interpret purchase requests
- **Inventory Management**: Track stock levels for all products
- **Transaction History**: Record all purchases
- **RESTful API**: Clean, documented endpoints
- **SQLite Database**: Persistent data storage

##  Tech Stack

- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL database toolkit
- **Instructor**: AI-powered natural language parsing
- **SQLite**: Lightweight database

##  Requirements

- Python 3.8+
- pip

##  Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/sachdevcode/happy-loop-soda-machine
cd soda-vending-machine
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///./soda_vending.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# OpenAI Configuration (for AI parsing)
OPENAI_API_KEY=dummy-key-for-testing
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=gpt-3.5-turbo

# Application Configuration
APP_TITLE=Soda Vending Machine API
APP_DESCRIPTION=AI-powered soda vending machine with natural language processing
APP_VERSION=1.0.0

# Environment
ENVIRONMENT=development
DEBUG=true

# CORS Configuration
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

### 4. Run the Application

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`


### 6. Test the API

```bash
# Check inventory
curl http://localhost:8000/api/v1/inventory

# Make a purchase
curl -X POST "http://localhost:8000/api/v1/purchase" \
     -H "Content-Type: application/json" \
     -d '{"message": "I want to buy 3 cokes"}'

# Check transactions
curl http://localhost:8000/api/v1/transactions
```

##  API Endpoints

### Root
- `GET /` - Welcome message and endpoint overview

### Vending Machine
- `POST /api/v1/purchase` - Process natural language purchase request
- `GET /api/v1/inventory` - Get current inventory
- `GET /api/v1/transactions` - Get transaction history

##  Usage Examples

### Purchase Request
```bash
curl -X POST "http://localhost:8000/api/v1/purchase" \
     -H "Content-Type: application/json" \
     -d '"I want to buy 3 cokes"'
```

### Check Inventory
```bash
curl "http://localhost:8000/api/v1/inventory"
```

##  Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLModel models
│   └── routers/
│       ├── __init__.py
│       └── vending.py       # Vending machine endpoints
├── requirements.txt
└── README.md
```

##  Development

### Running in Development Mode
```bash
uvicorn app.main:app --reload
```

### Database
The SQLite database file (`soda_vending.db`) will be created automatically on first run.
