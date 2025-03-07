"""Tests for the CLI interface."""
from pathlib import Path
import pytest
from click.testing import CliRunner

from investrak.cli.main import cli
from investrak.core.storage import JsonFileStorage

@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()

@pytest.fixture
def test_storage(tmp_path):
    """Create a test storage."""
    storage = JsonFileStorage(tmp_path)
    return storage

def test_cli_help():
    """Test the CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "InvesTrak" in result.output

def test_portfolio_create(runner, test_storage, monkeypatch):
    """Test creating a portfolio."""
    monkeypatch.setattr("investrak.cli.main.storage", test_storage)
    
    result = runner.invoke(cli, ["portfolio", "create", "Test Portfolio", "-d", "Test Description"])
    assert result.exit_code == 0
    assert "Created portfolio" in result.output

    # Verify portfolio was created
    portfolios = test_storage.list_portfolios()
    assert len(portfolios) == 1
    assert portfolios[0].name == "Test Portfolio"
    assert portfolios[0].description == "Test Description"

def test_portfolio_list(runner, test_storage, monkeypatch):
    """Test listing portfolios."""
    monkeypatch.setattr("investrak.cli.main.storage", test_storage)
    
    # First create a portfolio
    runner.invoke(cli, ["portfolio", "create", "Test Portfolio"])
    
    # Then list portfolios
    result = runner.invoke(cli, ["portfolio", "list"])
    assert result.exit_code == 0
    assert "Test Portfolio" in result.output

def test_portfolio_delete(runner, test_storage, monkeypatch):
    """Test deleting a portfolio."""
    monkeypatch.setattr("investrak.cli.main.storage", test_storage)
    
    # First create a portfolio
    runner.invoke(cli, ["portfolio", "create", "Test Portfolio"])
    portfolio_id = test_storage.list_portfolios()[0].id
    
    # Then delete it
    result = runner.invoke(cli, ["portfolio", "delete", str(portfolio_id)])
    assert result.exit_code == 0
    assert "Deleted portfolio" in result.output
    assert len(test_storage.list_portfolios()) == 0

def test_portfolio_update(runner, test_storage, monkeypatch):
    """Test updating a portfolio."""
    monkeypatch.setattr("investrak.cli.main.storage", test_storage)
    
    # First create a portfolio
    runner.invoke(cli, ["portfolio", "create", "Test Portfolio"])
    portfolio_id = test_storage.list_portfolios()[0].id
    
    # Then update it
    result = runner.invoke(cli, [
        "portfolio", "update", 
        str(portfolio_id), 
        "Updated Portfolio",
        "-d", "Updated Description"
    ])
    assert result.exit_code == 0
    assert "Updated portfolio" in result.output
    
    # Verify update
    updated = test_storage.get_portfolio(portfolio_id)
    assert updated.name == "Updated Portfolio"
    assert updated.description == "Updated Description"
