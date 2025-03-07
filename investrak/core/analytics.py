"""Portfolio analytics and calculations."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from uuid import UUID

from .models import Portfolio, InvestmentEntry, PortfolioSnapshot
from .storage import StorageInterface

class PortfolioAnalytics:
    """Portfolio analytics calculations."""

    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def calculate_portfolio_value(self, portfolio_id: UUID) -> Decimal:
        """Calculate current total value of a portfolio."""
        investments = self.storage.list_investments(portfolio_id)
        return sum(
            Decimal(str(inv.quantity)) * Decimal(str(inv.purchase_price))
            for inv in investments
        )

    def calculate_portfolio_metrics(self, portfolio_id: UUID) -> Dict:
        """Calculate basic portfolio metrics."""
        investments = self.storage.list_investments(portfolio_id)
        total_invested = Decimal('0')
        total_current = Decimal('0')

        for inv in investments:
            invested = Decimal(str(inv.quantity)) * Decimal(str(inv.purchase_price))
            total_invested += invested
            # TODO: Fetch current price from market data integration
            # For now, using purchase price as current price
            total_current += invested

        return {
            "total_invested": total_invested,
            "current_value": total_current,
            "profit_loss": total_current - total_invested,
            "profit_loss_percentage": (
                ((total_current - total_invested) / total_invested * 100)
                if total_invested > 0 else Decimal('0')
            ),
            "investment_count": len(investments)
        }

    def calculate_performance_metrics(self, portfolio_id: UUID, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict:
        """Calculate performance metrics for a given time period."""
        snapshots = self.storage.get_portfolio_snapshots(
            portfolio_id, start_date, end_date
        )
        
        if not snapshots:
            return {
                "total_return": Decimal('0'),
                "total_return_percentage": Decimal('0'),
                "annualized_return": Decimal('0'),
                "best_day_return": Decimal('0'),
                "worst_day_return": Decimal('0')
            }

        # Sort snapshots by timestamp
        sorted_snapshots = sorted(snapshots, key=lambda x: x.timestamp)
        first, last = sorted_snapshots[0], sorted_snapshots[-1]
        
        # Calculate total return
        total_return = last.total_value - first.total_value
        total_return_pct = (
            (last.total_value / first.total_value - 1) * 100
            if first.total_value > 0 else Decimal('0')
        )
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(sorted_snapshots)):
            prev, curr = sorted_snapshots[i-1], sorted_snapshots[i]
            daily_return = (curr.total_value / prev.total_value - 1) * 100
            daily_returns.append(daily_return)
        
        # Calculate annualized return
        days = (last.timestamp - first.timestamp).days
        if days > 0:
            annualized_return = (
                ((1 + total_return_pct/100) ** (365/days) - 1) * 100
            )
        else:
            annualized_return = Decimal('0')

        return {
            "total_return": total_return,
            "total_return_percentage": total_return_pct,
            "annualized_return": annualized_return,
            "best_day_return": max(daily_returns) if daily_returns else Decimal('0'),
            "worst_day_return": min(daily_returns) if daily_returns else Decimal('0')
        }

    def take_portfolio_snapshot(self, portfolio_id: UUID) -> PortfolioSnapshot:
        """Take a snapshot of current portfolio state."""
        metrics = self.calculate_portfolio_metrics(portfolio_id)
        
        return PortfolioSnapshot(
            portfolio_id=portfolio_id,
            total_value=metrics["current_value"],
            invested_amount=metrics["total_invested"],
            timestamp=datetime.utcnow()
        )
