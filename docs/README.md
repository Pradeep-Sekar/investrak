# InvesTrak Documentation

## Overview
InvesTrak is a CLI financial portfolio and goal tracking application.

## Project Structure
```
investrak/
├── docs/               # Documentation
├── investrak/          # Main package
│   ├── cli/           # CLI interface modules
│   └── core/          # Core business logic
│       ├── models.py  # Data models (Portfolio, Investment)
│       └── storage.py # Storage implementations
├── tests/             # Test suite
└── pyproject.toml     # Project configuration
```

## Development Setup
1. Create virtual environment:
   ```bash
   uv venv
   ```

2. Activate virtual environment:
   ```bash
   source .venv/bin/activate  # Unix/MacOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

## Usage Guide

### Portfolio Management

The `portfolio` command group provides tools for managing investment portfolios:

```bash
# Show all portfolio commands and options
investrak portfolio --help

# Create a new portfolio
investrak portfolio create "Retirement Fund" -d "Long-term retirement savings"

# List all portfolios
investrak portfolio list

# Update a portfolio (replace <id> with actual portfolio ID)
investrak portfolio update <id> "New Name" -d "New description"

# Delete a portfolio
investrak portfolio delete <id>
```

#### Command Details

- `create`: Creates a new portfolio
  - Required: `name` (in quotes if contains spaces)
  - Optional: `-d, --description` for portfolio description

- `list`: Displays all portfolios in a table format showing:
  - Portfolio ID
  - Name
  - Description
  - Creation date

- `update`: Updates an existing portfolio
  - Required: `portfolio_id` and new `name`
  - Optional: `-d, --description` for new description

- `delete`: Removes a portfolio by ID
  - Required: `portfolio_id`

### Investment Management
The application supports managing various types of investments within portfolios:

#### Supported Investment Types
- Stocks
- ETFs
- Mutual Funds

#### Investment Properties
- Symbol (e.g., "AAPL", "VTI")
- Type (stock/ETF/mutual fund)
- Quantity
- Purchase price
- Purchase date
- Optional category
- Optional notes

#### Data Validation
- Symbol length: 1-10 characters
- Positive quantities and prices only
- Category length: max 50 characters
- Notes length: max 500 characters

## Available Commands
- `investrak --help`: Show help message
- `investrak portfolio`: Manage investment portfolio
- `investrak goals`: Track financial goals *(coming soon)*

## Commit Guidelines
We follow semantic commit messages:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example: `feat: add portfolio command structure`
