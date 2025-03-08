"""Storage interfaces and implementations for InvesTrak."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime
import uuid
from uuid import UUID
from decimal import Decimal

from .models import Portfolio, InvestmentEntry, Goal, PortfolioSnapshot


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

    @abstractmethod
    def save_goal(self, goal: Goal) -> None:
        """Save or update a goal."""
        pass

    @abstractmethod
    def get_goal(self, goal_id: uuid.UUID) -> Optional[Goal]:
        """Retrieve a goal by ID."""
        pass

    @abstractmethod
    def list_goals(self) -> List[Goal]:
        """List all goals."""
        pass

    @abstractmethod
    def delete_goal(self, goal_id: uuid.UUID) -> bool:
        """Delete a goal by ID."""
        pass

    @abstractmethod
    def update_goal(self, goal: Goal) -> None:
        """Update an existing goal."""
        pass


class JsonFileStorage(StorageInterface):
    """JSON file-based storage implementation."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.portfolios_file = storage_path / "portfolios.json"
        self.investments_file = storage_path / "investments.json"
        self.goals_file = storage_path / "goals.json"
        self.snapshots_file = storage_path / "snapshots.json"
        
        # Initialize empty files if they don't exist
        if not self.goals_file.exists():
            self._write_goals([])

    def _init_storage(self) -> None:
        """Initialize storage directory and files."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        if not self.portfolios_file.exists():
            self.portfolios_file.write_text("[]")
        if not self.investments_file.exists():
            self.investments_file.write_text("[]")
        if not self.goals_file.exists():
            self.goals_file.write_text("[]")
        if not self.snapshots_file.exists():
            self.snapshots_file.write_text("[]")

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

    def get_portfolio(self, portfolio_id: str | UUID) -> Optional[Portfolio]:
        """Get a portfolio by ID."""
        portfolios = self._read_portfolios()
        for p in portfolios:  # portfolios is a list, not a dict
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
        investments = self._read_investments()
        investments.append(investment.model_dump())
        self._write_investments(investments)

    def get_investment(self, investment_id: uuid.UUID) -> Optional[InvestmentEntry]:
        """Retrieve an investment by ID."""
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
        investments = [
            inv for inv in investments
            if inv["id"] != str(investment_id)
        ]
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

    def save_goal(self, goal: Goal) -> None:
        """Save a goal."""
        goals = self._read_goals()
        
        # Update existing goal or append new one
        updated = False
        for i, g in enumerate(goals):
            if g["id"] == str(goal.id):
                goals[i] = goal.model_dump()
                updated = True
                break
        
        if not updated:
            goals.append(goal.model_dump())
        
        self._write_goals(goals)

    def get_goal(self, goal_id: UUID | str) -> Optional[Goal]:
        """Get a goal by ID."""
        goals = self._read_goals()
        goal_id_str = str(goal_id)
        for goal in goals:
            if goal["id"] == goal_id_str:
                return Goal.model_validate(goal)
        return None

    def list_goals(self) -> List[Goal]:
        """List all goals."""
        goals = self._read_goals()
        return [Goal.model_validate(g) for g in goals]

    def delete_goal(self, goal_id: UUID | str) -> bool:
        """Delete a goal by ID."""
        goals = self._read_goals()
        initial_length = len(goals)
        goals = [g for g in goals if g["id"] != str(goal_id)]
        if len(goals) < initial_length:
            self._write_goals(goals)
            return True
        return False

    def update_goal(self, goal: Goal) -> None:
        """Update an existing goal."""
        goals = self._read_goals()
        goal_id_str = str(goal.id)
        
        for i, g in enumerate(goals):
            if g["id"] == goal_id_str:
                goals[i] = goal.model_dump()
                self._write_goals(goals)
                return
                
        raise StorageError("Goal not found")

    def _read_goals(self) -> List[dict]:
        """Read goals from JSON file."""
        try:
            if not self.goals_file.exists():
                return []
            return json.loads(self.goals_file.read_text())
        except json.JSONDecodeError as e:
            raise StorageError(f"Failed to read goals: {e}")

    def _write_goals(self, goals: List[dict]) -> None:
        """Write goals to JSON file."""
        try:
            temp_file = self.goals_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(goals, default=str, indent=2))
            temp_file.replace(self.goals_file)
        except Exception as e:
            raise StorageError(f"Failed to write goals: {e}")

    def get_portfolio_snapshots(self, portfolio_id: uuid.UUID, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[PortfolioSnapshot]:
        """Retrieve portfolio snapshots within the given date range."""
        try:
            snapshots = json.loads(self.snapshots_file.read_text())
            filtered = []
            
            for snap in snapshots:
                if str(snap['portfolio_id']) != str(portfolio_id):
                    continue
                    
                timestamp = datetime.fromisoformat(snap['timestamp'])
                if start_date and timestamp < start_date:
                    continue
                if end_date and timestamp > end_date:
                    continue
                    
                filtered.append(PortfolioSnapshot(
                    portfolio_id=uuid.UUID(snap['portfolio_id']),
                    total_value=Decimal(str(snap['total_value'])),
                    invested_amount=Decimal(str(snap['invested_amount'])),
                    timestamp=timestamp
                ))
            
            return filtered
        except json.JSONDecodeError as e:
            raise StorageError(f"Failed to read snapshots: {e}")

    def save_portfolio_snapshot(self, snapshot: PortfolioSnapshot) -> None:
        """Save a portfolio snapshot."""
        try:
            snapshots = json.loads(self.snapshots_file.read_text())
            snapshots.append({
                'portfolio_id': str(snapshot.portfolio_id),
                'total_value': str(snapshot.total_value),
                'invested_amount': str(snapshot.invested_amount),
                'timestamp': snapshot.timestamp.isoformat()
            })
            
            temp_file = self.snapshots_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(snapshots, indent=2))
            temp_file.replace(self.snapshots_file)
        except Exception as e:
            raise StorageError(f"Failed to save snapshot: {e}")

    def _load_data(self) -> dict:
        """Load all data from storage."""
        if not self.storage_path.exists():
            return {"portfolios": [], "investments": [], "goals": [], "snapshots": []}
        
        data = {
            "portfolios": self._read_portfolios(),
            "investments": self._read_investments(),
            "goals": self._read_goals(),
            "snapshots": json.loads(self.snapshots_file.read_text()) if self.snapshots_file.exists() else []
        }
        return data

    def _save_data(self, data: dict) -> None:
        """Save all data to storage."""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Save each data type to its respective file
        if "portfolios" in data:
            self._write_portfolios(data["portfolios"])
        if "investments" in data:
            self._write_investments(data["investments"])
        if "goals" in data:
            self._write_goals(data["goals"])
        if "snapshots" in data:
            temp_file = self.snapshots_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(data["snapshots"], default=str, indent=2))
            temp_file.replace(self.snapshots_file)
