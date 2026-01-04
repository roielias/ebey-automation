# Quick Start Guide

## Installation

### Windows:
```bash
setup.bat
```

### Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

## Running Tests

### Activate virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Run all tests:
```bash
pytest tests/ -v
```

### Run with Allure:
```bash
pytest tests/ -v --alluredir=allure-results
allure serve allure-results
```

### Run specific markers:
```bash
pytest tests/ -v -m smoke
pytest tests/ -v -m e2e
pytest tests/ -v -m cart
```

## Project Structure

```
e2e_automation/
├── pages/              # Page Object Models
├── tests/              # Test files
├── utils/              # Utilities (logger, data reader, screenshots)
├── config/             # Configuration
├── data/               # Test data (JSON/YAML)
└── ecommerce_automation.py  # Main service class
```

## Core Functions

1. **search_items_by_name_under_price(query, max_price, limit)**
   - Search with price filtering and pagination

2. **add_items_to_cart(urls)**
   - Add items with variant selection

3. **assert_cart_total_not_exceeds(budget_per_item, items_count)**
   - Validate cart total

## Documentation

- Full README: `README.md`
- Bug Analysis: `ReadMeAIBugs.md`

## Troubleshooting

**Browser not opening:**
```bash
playwright install chromium
```

**Timeout errors:**
Edit `config/config.py` and increase `DEFAULT_TIMEOUT`

**Can't find elements:**
Set `HEADLESS=False` in `.env` to see browser
