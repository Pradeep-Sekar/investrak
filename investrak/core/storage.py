"""Storage interfaces and implementations for InvesTrak."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime
import uuid

from .models import Portfolio, InvestmentEntry


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

    @abstractmethod
    def save_investment(self, investment: InvestmentEntry) -> None:
        """Save an investment entry to storage."""
        pass

    @abstractmethod
    def get_investment(self, investment_id: uuid.UUID) -> Optional[InvestmentEntry]:
        """Retrieve an investment entry by ID."""
        pass

    @abstractmethod
    def list_investments(self, portfolio_id: uuid.UUID) -> List[InvestmentEntry]:
        """List all investments in a portfolio."""
        pass

    @abstractmethod
    def delete_investment(self, investment_id: uuid.UUID) -> bool:
        """Delete an investment entry by ID."""
        pass

    @abstractmethod
    def update_investment(self, investment: InvestmentEntry) -> None:
        """Update an existing investment entry."""
        pass


class JsonFileStorage(StorageInterface):
    """JSON file-based storage implementation."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.portfolios_file = storage_path / "portfolios.json"
        self.investments_file = storage_path / "investments.json"
        self._init_storage()

    def _init_storage(self) -> None:
        """Initialize storage directory and files."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.portfolios_file.exists():
            self.portfolios_file.write_text("[]")
        if not self.investments_file.exists():
            self.investments_file.write_text("[]")

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

    def _read_investments(self) -> List[dict]:
        """Read investments from JSON file."""
        try:
            return json.loads(self.investments_file.read_text())
        except json.JSONDecodeError as e:
            raise StorageError(f"Failed to read investments: {e}")

    def _write_investments(self, investments: List[dict]) -> None:
        """Write investments to JSON file."""
        try:
            temp_file = self.investments_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(investments, default=str, indent=2))
            temp_file.replace(self.investments_file)
        except Exception as e:
            raise StorageError(f"Failed to write investments: {e}")

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

    def save_investment(self, investment: InvestmentEntry) -> None:
        """Save an investment entry to storage."""
        # Verify portfolio exists
        if not self.get_portfolio(investment.portfolio_id):
            raise StorageError(f"Portfolio {investment.portfolio_id} not found")
        
        investments = self._read_investments()
        investments.append(investment.model_dump())
        self._write_investments(investments)

    def get_investment(self, investment_id: uuid.UUID) -> Optional[InvestmentEntry]:
        """Retrieve an investment entry by ID."""
        investments = self._read_investments()
        for inv in investments:
            if inv["id"] == str(investment_id):
                return InvestmentEntry.model_validate(inv)
        return None

    def list_investments(self, portfolio_id: uuid.UUID) -> List[InvestmentEntry]:
        """List all investments in a portfolio."""
        investments = self._read_investments()
        return [
            InvestmentEntry.model_validate(inv)
            for inv in investments
            if inv["portfolio_id"] == str(portfolio_id)
        ]

    def delete_investment(self, investment_id: uuid.UUID) -> bool:
        """Delete an investment entry by ID."""
        investments = self._read_investments()
        initial_length = len(investments)
        investments = [inv for inv in investments if inv["id"] != str(investment_id)]
        if len(investments) < initial_length:
            self._write_investments(investments)
            return True
        return False

    def update_investment(self, investment: InvestmentEntry) -> None:
        """Update an existing investment entry."""
        investments = self._read_investments()
        for i, inv in enumerate(investments):
            if inv["id"] == str(investment.id):
                investments[i] = investment.model_dump()
                self._write_investments(investments)
                return
        raise StorageError(f"Investment {investment.id} not found")
