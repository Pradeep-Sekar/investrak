"""Tests for goals CLI commands."""
from datetime import datetime, timedelta
import pytest
from click.testing import CliRunner
from freezegun import freeze_time

from investrak.cli.main import cli
from investrak.core.models import Goal, GoalStatus, Portfolio
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
        description="Test portfolio for goal commands"
    )
    storage.save_portfolio(portfolio)
    return portfolio

@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()

def test_create_goal(runner, storage, monkeypatch):
    """Test creating a new goal."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    result = runner.invoke(cli, [
        "goals", "create",
        "Emergency Fund",
        "10000",
        future_date,
        "-c", "Savings",
        "-d", "Test goal"
    ])
    
    assert result.exit_code == 0
    assert "Created goal" in result.output
    
    # Verify goal was saved
    goals = storage.list_goals()
    assert len(goals) == 1
    goal = goals[0]
    assert goal.name == "Emergency Fund"
    assert float(goal.target_amount) == 10000.0
    assert goal.category == "Savings"
    assert goal.description == "Test goal"

def test_create_goal_with_portfolio(runner, storage, test_portfolio, monkeypatch):
    """Test creating a goal with associated portfolio."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    result = runner.invoke(cli, [
        "goals", "create",
        "Investment Goal",
        "50000",
        future_date,
        "-p", str(test_portfolio.id),
        "-c", "Investment"
    ])
    
    assert result.exit_code == 0
    assert "Created goal" in result.output
    
    goals = storage.list_goals()
    assert len(goals) == 1
    assert goals[0].portfolio_id == test_portfolio.id

def test_create_goal_validation(runner, storage, monkeypatch):
    """Test goal creation validation."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # Test past date
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    result = runner.invoke(cli, [
        "goals", "create",
        "Test Goal",
        "10000",
        past_date
    ])
    assert result.exit_code == 1
    assert "Target date must be in the future" in result.output
    
    # Test negative amount
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    result = runner.invoke(cli, [
        "goals", "create",
        "Test Goal",
        "-1000",
        future_date
    ])
    assert result.exit_code == 1
    assert "Target amount must be positive" in result.output

def test_list_goals(runner, storage, monkeypatch):
    """Test listing goals."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # Create test goals
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    runner.invoke(cli, [
        "goals", "create",
        "Goal 1",
        "10000",
        future_date,
        "-s", "in_progress"
    ])
    runner.invoke(cli, [
        "goals", "create",
        "Goal 2",
        "20000",
        future_date,
        "-s", "completed"
    ])
    
    # Test listing all goals
    result = runner.invoke(cli, ["goals", "list"])
    assert result.exit_code == 0
    assert "Goal 1" in result.output
    assert "Goal 2" in result.output
    
    # Test filtering by status
    result = runner.invoke(cli, ["goals", "list", "-s", "completed"])
    assert result.exit_code == 0
    assert "Goal 1" not in result.output
    assert "Goal 2" in result.output

def test_update_goal(runner, storage, monkeypatch):
    """Test updating a goal."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # First create a goal
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    runner.invoke(cli, [
        "goals", "create",
        "Original Goal",
        "10000",
        future_date
    ])
    
    goal_id = storage.list_goals()[0].id
    
    # Update the goal
    result = runner.invoke(cli, [
        "goals", "update",
        str(goal_id),
        "-n", "Updated Goal",
        "-a", "15000",
        "-s", "completed"
    ])
    
    assert result.exit_code == 0
    assert "Updated goal" in result.output
    
    # Verify updates
    updated_goal = storage.get_goal(goal_id)
    assert updated_goal.name == "Updated Goal"
    assert float(updated_goal.target_amount) == 15000.0
    assert updated_goal.status == GoalStatus.COMPLETED

def test_delete_goal(runner, storage, monkeypatch):
    """Test deleting a goal."""
    monkeypatch.setattr("investrak.cli.main.storage", storage)
    
    # First create a goal
    future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    runner.invoke(cli, [
        "goals", "create",
        "Test Goal",
        "10000",
        future_date
    ])
    
    goal_id = storage.list_goals()[0].id
    
    # Delete the goal
    result = runner.invoke(cli, ["goals", "delete", str(goal_id)])
    assert result.exit_code == 0
    assert "Deleted goal" in result.output
    
    # Verify deletion
    assert len(storage.list_goals()) == 0