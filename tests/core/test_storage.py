"""Tests for storage implementations."""
import json
from pathlib import Path
import pytest
from uuid import uuid4

from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType
from investrak.core.storage import JsonFileStorage, StorageError


@pytest.fixture
def temp_storage(tmp_path):
    """Create a temporary storage directory."""
    return JsonFileStorage(tmp_path)


def test_storage_initialization(temp_storage, tmp_path):
    """Test storage initialization."""
    assert temp_storage.portfolios_file.exists()
    assert json.loads(temp_storage.portfolios_file.read_text()) == []


def test_save_and_get_portfolio(temp_storage):
    """Test saving and retrieving a portfolio."""
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    retrieved = temp_storage.get_portfolio(portfolio.id)
    assert retrieved is not None
    assert retrieved.name == portfolio.name
    assert retrieved.id == portfolio.id


def test_list_portfolios(temp_storage):
    """Test listing portfolios."""
    portfolio1 = Portfolio(name="Portfolio 1")
    portfolio2 = Portfolio(name="Portfolio 2")
    
    temp_storage.save_portfolio(portfolio1)
    temp_storage.save_portfolio(portfolio2)
    
    portfolios = temp_storage.list_portfolios()
    assert len(portfolios) == 2
    assert any(p.id == portfolio1.id for p in portfolios)
    assert any(p.id == portfolio2.id for p in portfolios)


def test_delete_portfolio(temp_storage):
    """Test deleting a portfolio."""
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    assert temp_storage.delete_portfolio(portfolio.id)
    assert temp_storage.get_portfolio(portfolio.id) is None


def test_update_portfolio(temp_storage):
    """Test updating a portfolio."""
    portfolio = Portfolio(name="Original Name")
    temp_storage.save_portfolio(portfolio)
    
    updated = Portfolio(id=portfolio.id, name="Updated Name")
    temp_storage.update_portfolio(updated)
    
    retrieved = temp_storage.get_portfolio(portfolio.id)
    assert retrieved is not None
    assert retrieved.name == "Updated Name"


def test_invalid_portfolio_operations(temp_storage):
    """Test operations with invalid portfolios."""
    # Test getting non-existent portfolio
    assert temp_storage.get_portfolio(uuid4()) is None
    
    # Test deleting non-existent portfolio
    assert not temp_storage.delete_portfolio(uuid4())
    
    # Test updating non-existent portfolio
    with pytest.raises(StorageError):
        temp_storage.update_portfolio(Portfolio(name="Non-existent"))


def test_save_and_get_investment(temp_storage):
    """Test saving and retrieving an investment."""
    # Create a portfolio first
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    # Create and save investment
    investment = InvestmentEntry(
        portfolio_id=portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50
    )
    temp_storage.save_investment(investment)
    
    # Retrieve and verify
    retrieved = temp_storage.get_investment(investment.id)
    assert retrieved is not None
    assert retrieved.symbol == investment.symbol
    assert retrieved.type == investment.type
    assert retrieved.quantity == investment.quantity
    assert retrieved.purchase_price == investment.purchase_price


def test_list_investments(temp_storage):
    """Test listing investments in a portfolio."""
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    investments = [
        InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.50
        ),
        InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="VTI",
            type=InvestmentType.ETF,
            quantity=5,
            purchase_price=220.75
        )
    ]
    
    for inv in investments:
        temp_storage.save_investment(inv)
    
    retrieved = temp_storage.list_investments(portfolio.id)
    assert len(retrieved) == 2
    assert any(inv.symbol == "AAPL" for inv in retrieved)
    assert any(inv.symbol == "VTI" for inv in retrieved)


def test_delete_investment(temp_storage):
    """Test deleting an investment."""
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    investment = InvestmentEntry(
        portfolio_id=portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50
    )
    temp_storage.save_investment(investment)
    
    assert temp_storage.delete_investment(investment.id)
    assert temp_storage.get_investment(investment.id) is None


def test_update_investment(temp_storage):
    """Test updating an investment."""
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    investment = InvestmentEntry(
        portfolio_id=portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50
    )
    temp_storage.save_investment(investment)
    
    updated = InvestmentEntry(
        id=investment.id,
        portfolio_id=portfolio.id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=20,  # Updated quantity
        purchase_price=155.75  # Updated price
    )
    temp_storage.update_investment(updated)
    
    retrieved = temp_storage.get_investment(investment.id)
    assert retrieved is not None
    assert retrieved.quantity == 20
    assert retrieved.purchase_price == 155.75


def test_invalid_investment_operations(temp_storage):
    """Test operations with invalid investments."""
    portfolio = Portfolio(name="Test Portfolio")
    temp_storage.save_portfolio(portfolio)
    
    # Test saving investment with non-existent portfolio
    with pytest.raises(StorageError):
        investment = InvestmentEntry(
            portfolio_id=uuid4(),
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.50
        )
        temp_storage.save_investment(investment)
    
    # Test getting non-existent investment
    assert temp_storage.get_investment(uuid4()) is None
    
    # Test deleting non-existent investment
    assert not temp_storage.delete_investment(uuid4())
    
    # Test updating non-existent investment
    with pytest.raises(StorageError):
        investment = InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.50
        )
        temp_storage.update_investment(investment)
