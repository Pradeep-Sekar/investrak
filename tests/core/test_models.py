"""Tests for data models."""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError

from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType


def test_portfolio_creation():
    """Test creating a valid portfolio."""
    portfolio = Portfolio(name="Test Portfolio")
    assert portfolio.name == "Test Portfolio"
    assert portfolio.id is not None
    assert portfolio.creation_date is not None


def test_portfolio_validation():
    """Test portfolio validation rules."""
    # Test empty name
    with pytest.raises(ValidationError):
        Portfolio(name="")

    # Test too long name
    with pytest.raises(ValidationError):
        Portfolio(name="x" * 101)

    # Test too long description
    with pytest.raises(ValidationError):
        Portfolio(name="Test", description="x" * 501)


def test_investment_entry_creation():
    """Test creating a valid investment entry."""
    portfolio_id = uuid4()
    entry = InvestmentEntry(
        portfolio_id=portfolio_id,
        symbol="AAPL",
        type=InvestmentType.STOCK,
        quantity=10,
        purchase_price=150.50,
        category="Technology"
    )
    
    assert entry.symbol == "AAPL"
    assert entry.type == InvestmentType.STOCK
    assert entry.quantity == 10
    assert entry.purchase_price == 150.50
    assert entry.category == "Technology"
    assert entry.id is not None
    assert entry.purchase_date is not None


def test_investment_entry_validation():
    """Test investment entry validation rules."""
    portfolio_id = uuid4()
    
    # Test empty symbol
    with pytest.raises(ValidationError):
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.50
        )

    # Test invalid quantity
    with pytest.raises(ValidationError):
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=0,
            purchase_price=150.50
        )

    # Test negative price
    with pytest.raises(ValidationError):
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=-150.50
        )

    # Test invalid category length
    with pytest.raises(ValidationError):
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.50,
            category="x" * 51
        )
