"""Tests for data models."""
import pytest
from pydantic import ValidationError

from investrak.core.models import Portfolio


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