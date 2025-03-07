# InvesTrak Documentation

## Overview
InvesTrak is a CLI financial portfolio and goal tracking application.

## Project Structure
```
investrak/
├── docs/                    # Documentation
│   ├── README.md           # Main documentation
│   ├── ROADMAP.md          # Development roadmap
│   └── CHANGELOG.md        # Version history
├── investrak/              # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli/               # CLI interface modules
│   │   ├── __init__.py
│   │   └── main.py        # CLI command definitions
│   └── core/              # Core business logic
│       ├── __init__.py
│       ├── models.py      # Data models (Portfolio, Investment, Goal)
│       ├── storage.py     # Storage implementations
│       └── analytics.py   # Portfolio analytics and metrics
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py       # Test configurations
│   ├── test_cli/         # CLI tests
│   │   ├── __init__.py
│   │   └── test_main.py
│   └── test_core/        # Core functionality tests
│       ├── __init__.py
│       ├── test_models.py
│       └── test_storage.py
├── .gitignore            # Git ignore rules
├── pyproject.toml        # Project configuration and dependencies
└── uv.lock              # Dependency lock file
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

The `investment` command group allows managing investments within portfolios:

```bash
# Add a new investment to a portfolio
investrak investment add <portfolio-id> AAPL stock 10 150.50 -d 2024-01-15 -c "Technology" -n "Initial purchase"

# List all investments in a portfolio
investrak investment list <portfolio-id>

# Update an investment
investrak investment update <investment-id> -q 15 -p 160.75 -c "Tech Stocks" -n "Updated position"

# Delete an investment
investrak investment delete <investment-id>
```

#### Command Details

- `add`: Adds a new investment to a portfolio
  - Required:
    - `portfolio-id`: ID of the target portfolio
    - `symbol`: Stock symbol (e.g., "AAPL")
    - `type`: Investment type (stock/etf/mutual_fund)
    - `quantity`: Number of shares/units
    - `price`: Purchase price per share/unit
  - Optional:
    - `-d, --date`: Purchase date (YYYY-MM-DD, defaults to today)
    - `-c, --category`: Investment category
    - `-n, --notes`: Additional notes

- `list`: Shows all investments in a portfolio
  - Required: `portfolio-id`
  - Displays:
    - Investment ID
    - Symbol
    - Type
    - Quantity
    - Purchase Price
    - Purchase Date
    - Category

- `update`: Modifies an existing investment
  - Required: `investment-id`
  - Optional:
    - `-q, --quantity`: New quantity
    - `-p, --price`: New purchase price
    - `-c, --category`: New category
    - `-n, --notes`: New notes

- `delete`: Removes an investment
  - Required: `investment-id`

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

### Financial Goals Management

The `goals` command group provides tools for managing financial goals:

```bash
# Show all goal commands and options
investrak goals --help

# Create a new financial goal
investrak goals create "Emergency Fund" 10000 2024-12-31 -c "Savings" -d "6 months of expenses"

# List all goals
investrak goals list

# List goals with specific status
investrak goals list -s in_progress

# Update a goal
investrak goals update <goal-id> -n "New Name" -a 15000 -s completed

# Delete a goal
investrak goals delete <goal-id>
```

#### Command Details

- `create`: Creates a new financial goal
  - Required:
    - `name`: Goal name (in quotes if contains spaces)
    - `target-amount`: Target amount in currency units
    - `target-date`: Target completion date (YYYY-MM-DD)
  - Optional:
    - `-c, --category`: Goal category
    - `-d, --description`: Goal description
    - `-p, --portfolio`: Associated portfolio ID

- `list`: Shows all financial goals
  - Optional:
    - `-s, --status`: Filter by status (in_progress/completed/on_hold)
  - Displays:
    - Goal ID
    - Name
    - Target Amount
    - Target Date
    - Category
    - Status

- `update`: Modifies an existing goal
  - Required: `goal-id`
  - Optional:
    - `-n, --name`: New goal name
    - `-a, --target-amount`: New target amount
    - `-d, --target-date`: New target date (YYYY-MM-DD)
    - `-c, --category`: New category
    - `-d, --description`: New description
    - `-s, --status`: New status (in_progress/completed/on_hold)

- `delete`: Removes a goal
  - Required: `goal-id`
  - Includes confirmation prompt

#### Goal Properties
- Name
- Target amount (must be positive)
- Target date (must be in the future)
- Optional category
- Optional description
- Status (in_progress/completed/on_hold)
- Optional associated portfolio

#### Data Validation
- Target amount must be positive
- Target date must be in the future
- Status must be one of: in_progress, completed, on_hold

### Portfolio Analytics

The `analytics` command group provides tools for analyzing portfolio performance:

```bash
# Show current value of a portfolio
investrak analytics value <portfolio-id>

# Take a snapshot of current portfolio state
investrak analytics snapshot <portfolio-id>

# Show portfolio performance metrics
investrak analytics performance <portfolio-id> --from YYYY-MM-DD --to YYYY-MM-DD
```

#### Command Details

- `value`: Shows the current total value of a portfolio
  - Required: `portfolio-id`
  - Displays:
    - Portfolio name
    - Current total value

- `snapshot`: Creates a point-in-time snapshot of portfolio value
  - Required: `portfolio-id`
  - Records:
    - Total value
    - Invested amount
    - Timestamp

- `performance`: Shows portfolio performance metrics
  - Required: 
    - `portfolio-id`
    - `--from`: Start date (YYYY-MM-DD)
    - `--to`: End date (YYYY-MM-DD)
  - Displays:
    - Total Return ($)
    - Total Return (%)
    - Annualized Return
    - Best Daily Return
    - Worst Daily Return

## Available Commands
- `investrak --help`: Show help message
- `investrak portfolio`: Manage investment portfolios
- `investrak investment`: Manage investments
- `investrak goals`: Track financial goals
- `investrak analytics`: Analyze portfolio performance

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
