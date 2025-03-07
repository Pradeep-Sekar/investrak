"""Tests for storage implementations."""
import json
from pathlib import Path
import pytest
from uuid import uuid4

from investrak.core.models import Portfolio
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