"""Tests for portfolio analytics."""
from decimal import Decimal
from uuid import uuid4
import pytest
from datetime import datetime

from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType, PortfolioSnapshot
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

@pytest.mark.freeze_time("2024-01-15")
def test_portfolio_snapshot(test_portfolio):
    """Test taking portfolio snapshot."""
    storage, portfolio = test_portfolio
    analytics = PortfolioAnalytics(storage)
    
    snapshot = analytics.take_portfolio_snapshot(portfolio.id)
    
    assert snapshot.portfolio_id == portfolio.id
    assert snapshot.total_value == Decimal('14000.00')
    assert snapshot.invested_amount == Decimal('14000.00')
    assert snapshot.timestamp.date() == datetime(2024, 1, 15).date()

@pytest.mark.freeze_time("2024-01-15")
def test_performance_metrics(test_portfolio):
    """Test calculating performance metrics."""
    storage, portfolio = test_portfolio
    analytics = PortfolioAnalytics(storage)
    
    # Create some historical snapshots
    snapshots = [
        PortfolioSnapshot(
            portfolio_id=portfolio.id,
            total_value=Decimal('10000.00'),
            invested_amount=Decimal('10000.00'),
            timestamp=datetime(2024, 1, 1)
        ),
        PortfolioSnapshot(
            portfolio_id=portfolio.id,
            total_value=Decimal('14000.00'),
            invested_amount=Decimal('14000.00'),
            timestamp=datetime(2024, 1, 15)
        )
    ]
    
    for snapshot in snapshots:
        storage.save_portfolio_snapshot(snapshot)
    
    metrics = analytics.calculate_performance_metrics(portfolio.id)
    
    assert metrics["total_return"] == Decimal('4000.00')
    assert metrics["total_return_percentage"] == Decimal('40.00')
    assert metrics["annualized_return"] > Decimal('0')
