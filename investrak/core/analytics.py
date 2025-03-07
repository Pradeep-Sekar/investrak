"""Portfolio analytics and calculations."""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional
from uuid import UUID

from .models import Portfolio, InvestmentEntry
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