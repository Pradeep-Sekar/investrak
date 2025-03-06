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

## Available Commands
- `investrak --help`: Show help message
- `investrak portfolio`: Manage investment portfolio
- `investrak goals`: Track financial goals

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