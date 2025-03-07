"""Tests for portfolio analytics."""
from decimal import Decimal
from uuid import uuid4
import pytest
from datetime import datetime

from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType
from investrak.core.storage import JsonFileStorage
from investrak.core.analytics import PortfolioAnalytics

@pytest.fixture
def test_portfolio(tmp_path):
    """Create a test portfolio with investments."""
    storage = JsonFileStorage(tmp_path)
    
    portfolio = Portfolio(name="Test Portfolio")
    storage.save_portfolio(portfolio)
    
    investments = [
        InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.00
        ),
        InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="GOOGL",
            type=InvestmentType.STOCK,
            quantity=5,
            purchase_price=2500.00
        )
    ]
    
    for inv in investments:
        storage.save_investment(inv)
    
    return storage, portfolio

def test_portfolio_value_calculation(test_portfolio):
    """Test calculating portfolio total value."""
    storage, portfolio = test_portfolio
    analytics = PortfolioAnalytics(storage)
    
    # Expected: (10 * 150.00) + (5 * 2500.00) = 14,000.00
    expected_value = Decimal('14000.00')
    calculated_value = analytics.calculate_portfolio_value(portfolio.id)
    
    assert calculated_value == expected_value

def test_portfolio_metrics(test_portfolio):
    """Test calculating portfolio metrics."""
    storage, portfolio = test_portfolio
    analytics = PortfolioAnalytics(storage)
    
    metrics = analytics.calculate_portfolio_metrics(portfolio.id)
    
    assert metrics["total_invested"] == Decimal('14000.00')
    assert metrics["current_value"] == Decimal('14000.00')
    assert metrics["profit_loss"] == Decimal('0')
    assert metrics["profit_loss_percentage"] == Decimal('0')
    assert metrics["investment_count"] == 2