"""Tests for analytics CLI commands."""
from decimal import Decimal
import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from investrak.cli.main import cli
from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType

@pytest.fixture
def sample_portfolio(storage):
    """Create a sample portfolio with investments for testing."""
    # Create portfolio
    portfolio = Portfolio(name="Test Portfolio", description="Test Description")
    storage.save_portfolio(portfolio)
    
    # Add some investments
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
    
    return portfolio

def test_analytics_value_command(runner, storage, sample_portfolio, monkeypatch):
    """Test the portfolio value command."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, ["analytics", "value", str(sample_portfolio.id)])
    
    assert result.exit_code == 0
    assert "Portfolio:" in result.output
    assert "Current Value:" in result.output
    assert "$14,000.00" in result.output  # Expected total: (10 * 150) + (5 * 2500)

def test_analytics_metrics_command(runner, storage, sample_portfolio, monkeypatch):
    """Test the portfolio metrics command."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, ["analytics", "metrics", str(sample_portfolio.id)])
    
    assert result.exit_code == 0
    assert "Portfolio Metrics:" in result.output
    assert "Total Invested" in result.output
    assert "Current Value" in result.output
    assert "Profit/Loss" in result.output
    assert "Number of Investments" in result.output
    assert "$14,000.00" in result.output
    assert "2" in result.output  # Number of investments

def test_analytics_invalid_portfolio(runner, storage, monkeypatch):
    """Test analytics commands with invalid portfolio ID."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # Test value command
    result = runner.invoke(cli, ["analytics", "value", "invalid-id"])
    assert result.exit_code == 1
    assert "Error" in result.output
    
    # Test metrics command
    result = runner.invoke(cli, ["analytics", "metrics", "invalid-id"])
    assert result.exit_code == 1
    assert "Error" in result.output

def test_analytics_help_commands(runner):
    """Test analytics help commands."""
    # Test main analytics help
    result = runner.invoke(cli, ["analytics", "--help"])
    assert result.exit_code == 0
    assert "Portfolio analytics and reporting" in result.output
    
    # Test value command help
    result = runner.invoke(cli, ["analytics", "value", "--help"])
    assert result.exit_code == 0
    assert "Show current value of a portfolio" in result.output
    
    # Test metrics command help
    result = runner.invoke(cli, ["analytics", "metrics", "--help"])
    assert result.exit_code == 0
    assert "Show detailed portfolio metrics" in result.output