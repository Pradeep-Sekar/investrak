"""Storage interfaces and implementations for InvesTrak."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime
import uuid

from .models import Portfolio


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class StorageInterface(ABC):
    """Abstract base class for storage implementations."""

    @abstractmethod
    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Save a portfolio to storage."""
        pass

    @abstractmethod
    def get_portfolio(self, portfolio_id: uuid.UUID) -> Optional[Portfolio]:
        """Retrieve a portfolio by ID."""
        pass

    @abstractmethod
    def list_portfolios(self) -> List[Portfolio]:
        """List all portfolios."""
        pass

    @abstractmethod
    def delete_portfolio(self, portfolio_id: uuid.UUID) -> bool:
        """Delete a portfolio by ID."""
        pass

    @abstractmethod
    def update_portfolio(self, portfolio: Portfolio) -> None:
        """Update an existing portfolio."""
        pass


class JsonFileStorage(StorageInterface):
    """JSON file-based storage implementation."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.portfolios_file = storage_path / "portfolios.json"
        self._init_storage()

    def _init_storage(self) -> None:
        """Initialize storage directory and files."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.portfolios_file.exists():
            self.portfolios_file.write_text("[]")

    def _read_portfolios(self) -> List[dict]:
        """Read portfolios from JSON file."""
        try:
            return json.loads(self.portfolios_file.read_text())
        except json.JSONDecodeError as e:
            raise StorageError(f"Failed to read portfolios: {e}")

    def _write_portfolios(self, portfolios: List[dict]) -> None:
        """Write portfolios to JSON file."""
        try:
            temp_file = self.portfolios_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(portfolios, default=str, indent=2))
            temp_file.replace(self.portfolios_file)
        except Exception as e:
            raise StorageError(f"Failed to write portfolios: {e}")

    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Save a portfolio to storage."""
        portfolios = self._read_portfolios()
        portfolios.append(portfolio.model_dump())
        self._write_portfolios(portfolios)

    def get_portfolio(self, portfolio_id: uuid.UUID) -> Optional[Portfolio]:
        """Retrieve a portfolio by ID."""
        portfolios = self._read_portfolios()
        for p in portfolios:
            if p["id"] == str(portfolio_id):
                return Portfolio.model_validate(p)
        return None

    def list_portfolios(self) -> List[Portfolio]:
        """List all portfolios."""
        portfolios = self._read_portfolios()
        return [Portfolio.model_validate(p) for p in portfolios]

    def delete_portfolio(self, portfolio_id: uuid.UUID) -> bool:
        """Delete a portfolio by ID."""
        portfolios = self._read_portfolios()
        initial_length = len(portfolios)
        portfolios = [p for p in portfolios if p["id"] != str(portfolio_id)]
        if len(portfolios) < initial_length:
            self._write_portfolios(portfolios)
            return True
        return False

    def update_portfolio(self, portfolio: Portfolio) -> None:
        """Update an existing portfolio."""
        portfolios = self._read_portfolios()
        for i, p in enumerate(portfolios):
            if p["id"] == str(portfolio.id):
                portfolios[i] = portfolio.model_dump()
                self._write_portfolios(portfolios)
                return
        raise StorageError(f"Portfolio {portfolio.id} not found")