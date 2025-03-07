"""Tests for export CLI commands."""
from pathlib import Path
import pytest
from click.testing import CliRunner
from uuid import uuid4

from investrak.cli.main import cli
from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType

@pytest.fixture
def test_portfolio(storage):
    """Create a test portfolio with sample data."""
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
    
    return portfolio

def test_export_csv_command(runner, storage, test_portfolio, tmp_path, monkeypatch):
    """Test the export CSV command."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    output_path = tmp_path / "portfolio_export.csv"
    result = runner.invoke(cli, [
        "analytics", "export",
        str(test_portfolio.id),
        "csv",
        str(output_path)
    ])
    
    assert result.exit_code == 0
    assert "Analytics exported" in result.output
    assert output_path.exists()

def test_export_pdf_command(runner, storage, test_portfolio, tmp_path, monkeypatch):
    """Test the export PDF command."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    output_path = tmp_path / "portfolio_export.pdf"
    result = runner.invoke(cli, [
        "analytics", "export",
        str(test_portfolio.id),
        "pdf",
        str(output_path)
    ])
    
    assert result.exit_code == 0
    assert "Analytics exported" in result.output
    assert output_path.exists()

def test_export_invalid_portfolio(runner, storage, tmp_path, monkeypatch):
    """Test export command with invalid portfolio ID."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    output_path = tmp_path / "should_not_exist.csv"
    result = runner.invoke(cli, [
        "analytics", "export",
        str(uuid4()),
        "csv",
        str(output_path)
    ])
    
    assert result.exit_code == 1
    assert "Error" in result.output
    assert not output_path.exists()

def test_export_invalid_path(runner, storage, test_portfolio, monkeypatch):
    """Test export command with invalid output path."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    result = runner.invoke(cli, [
        "analytics", "export",
        str(test_portfolio.id),
        "csv",
        "/invalid/path/file.csv"
    ])
    
    assert result.exit_code == 1
    assert "Error" in result.output