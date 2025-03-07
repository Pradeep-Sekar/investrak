"""Tests for investment CLI commands."""
import uuid
from pathlib import Path
from datetime import datetime
import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from investrak.cli.main import cli
from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType
from investrak.core.storage import JsonFileStorage

@pytest.fixture
def storage_path(tmp_path):
    """Create a temporary storage path."""
    return tmp_path / "investrak_test"

@pytest.fixture
def storage(storage_path):
    """Create a test storage instance."""
    return JsonFileStorage(storage_path)

@pytest.fixture
def test_portfolio(storage):
    """Create a test portfolio."""
    portfolio = Portfolio(
        name="Test Portfolio",
        description="Test portfolio for investment commands"
    )
    storage.save_portfolio(portfolio)
    return portfolio

@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()

def test_add_investment(runner, storage, test_portfolio, monkeypatch):
    """Test adding a new investment."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, [
        "investment", "add",
        str(test_portfolio.id),
        "AAPL",
        "stock",
        "10",
        "150.50",
        "-c", "Technology",
        "-n", "Test investment"
    ])
    
    assert result.exit_code == 0
    assert "Added investment: AAPL" in result.output
    
    # Verify investment was saved
    investments = storage.list_investments(test_portfolio.id)
    assert len(investments) == 1
    investment = investments[0]
    assert investment.symbol == "AAPL"
    assert investment.type == InvestmentType.STOCK
    assert investment.quantity == 10
    assert float(investment.purchase_price) == 150.50
    assert investment.category == "Technology"
    assert investment.notes == "Test investment"

def test_add_investment_invalid_portfolio(runner, storage, monkeypatch):
    """Test adding investment to non-existent portfolio."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, [
        "investment", "add",
        str(uuid.uuid4()),
        "AAPL",
        "stock",
        "10",
        "150.50"
    ])
    
    assert result.exit_code == 0
    assert "Portfolio not found" in result.output

def test_list_investments(runner, storage, test_portfolio, monkeypatch):
    """Test listing investments in a portfolio."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # Add test investments
    investment = InvestmentEntry(
        portfolio_id=test_portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50,
        category="Technology"
    )
    storage.save_investment(investment)
    
    result = runner.invoke(cli, ["investment", "list", str(test_portfolio.id)])
    
    assert result.exit_code == 0
    assert "AAPL" in result.output
    # Instead of exact string match, check for presence of category
    assert investment.category in result.output

def test_delete_investment(runner, storage, test_portfolio, monkeypatch):
    """Test deleting an investment."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # Add test investment
    investment = InvestmentEntry(
        portfolio_id=test_portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50
    )
    storage.save_investment(investment)
    
    result = runner.invoke(cli, ["investment", "delete", str(investment.id)])
    
    assert result.exit_code == 0
    assert "Deleted investment" in result.output
    
    # Verify investment was deleted
    assert not storage.get_investment(investment.id)

def test_update_investment(runner, storage, test_portfolio, monkeypatch):
    """Test updating an investment."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # Add test investment
    investment = InvestmentEntry(
        portfolio_id=test_portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50,
        category="Technology"
    )
    storage.save_investment(investment)
    
    # Update quantity and price
    result = runner.invoke(cli, [
        "investment", "update",
        str(investment.id),
        "-q", "15",
        "-p", "160.75",
        "-c", "Tech Stocks"
    ])
    
    assert result.exit_code == 0
    assert "Updated investment: AAPL" in result.output
    
    # Verify investment was updated
    updated = storage.get_investment(investment.id)
    assert updated.quantity == 15
    assert float(updated.purchase_price) == 160.75
    assert updated.category == "Tech Stocks"

def test_update_investment_not_found(runner, storage, monkeypatch):
    """Test updating non-existent investment."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, [
        "investment", "update",
        str(uuid.uuid4()),
        "-q", "15"
    ])
    
    assert result.exit_code == 0
    assert "not found" in result.output

@pytest.mark.parametrize("invalid_input,expected_error", [
    (
        ["investment", "add", str(uuid.uuid4()), "AAPL", "stock", "0", "150.50"],
        "Invalid value for 'QUANTITY'"
    ),
    (
        ["investment", "add", str(uuid.uuid4()), "AAPL", "stock", "10", "-150.50"],
        "Price must be positive"
    ),
    (
        ["investment", "add", str(uuid.uuid4()), "TOOLONGSTOCKSYMBOL", "stock", "10", "150.50"],
        "Symbol too long"
    ),
])
def test_investment_validation(runner, storage, monkeypatch, invalid_input, expected_error):
    """Test investment validation rules."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, invalid_input)
    
    assert result.exit_code == 0  # All validations should return 0
    assert expected_error in result.output
