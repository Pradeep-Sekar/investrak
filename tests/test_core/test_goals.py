"""Tests for goal models and storage."""
from datetime import datetime, timedelta
import pytest
from uuid import uuid4
from pydantic import ValidationError

from investrak.core.models import Goal, GoalStatus
from investrak.core.storage import JsonFileStorage

def test_goal_creation():
    """Test creating a valid goal."""
    future_date = datetime.now() + timedelta(days=365)
    goal = Goal(
        name="Test Goal",
        target_amount=10000,
        target_date=future_date,
        category="Savings"
    )
    
    assert goal.name == "Test Goal"
    assert float(goal.target_amount) == 10000.0
    assert goal.target_date == future_date
    assert goal.category == "Savings"
    assert goal.status == GoalStatus.IN_PROGRESS
    assert goal.id is not None

def test_goal_validation():
    """Test goal validation rules."""
    future_date = datetime.now() + timedelta(days=365)
    
    # Test empty name
    with pytest.raises(ValidationError):
        Goal(
            name="",
            target_amount=10000,
            target_date=future_date
        )
    
    # Test negative amount
    with pytest.raises(ValidationError):
        Goal(
            name="Test Goal",
            target_amount=-1000,
            target_date=future_date
        )
    
    # Test too long name
    with pytest.raises(ValidationError):
        Goal(
            name="x" * 101,
            target_amount=10000,
            target_date=future_date
        )
    
    # Test invalid status
    with pytest.raises(ValidationError):
        Goal(
            name="Test Goal",
            target_amount=10000,
            target_date=future_date,
            status="invalid_status"
        )

def test_goal_storage(tmp_path):
    """Test goal storage operations."""
    storage = JsonFileStorage(tmp_path)
    
    # Create and save a goal
    goal = Goal(
        name="Test Goal",
        target_amount=10000,
        target_date=datetime.now() + timedelta(days=365)
    )
    storage.save_goal(goal)
    
    # Test retrieval
    retrieved = storage.get_goal(goal.id)
    assert retrieved is not None
    assert retrieved.name == goal.name
    assert float(retrieved.target_amount) == float(goal.target_amount)
    
    # Test listing
    goals = storage.list_goals()
    assert len(goals) == 1
    assert goals[0].id == goal.id
    
    # Test updating
    updated_goal = Goal(
        id=goal.id,
        name="Updated Goal",
        target_amount=15000,
        target_date=goal.target_date,
        status=GoalStatus.COMPLETED
    )
    storage.save_goal(updated_goal)
    
    retrieved = storage.get_goal(goal.id)
    assert retrieved.name == "Updated Goal"
    assert float(retrieved.target_amount) == 15000.0
    assert retrieved.status == GoalStatus.COMPLETED
    
    # Test deletion
    storage.delete_goal(goal.id)
    assert storage.get_goal(goal.id) is None
    assert len(storage.list_goals()) == 0

def test_goal_with_portfolio(tmp_path):
    """Test goal with portfolio association."""
    storage = JsonFileStorage(tmp_path)
    portfolio_id = uuid4()
    
    goal = Goal(
        name="Portfolio Goal",
        target_amount=10000,
        target_date=datetime.now() + timedelta(days=365),
        portfolio_id=portfolio_id
    )
    storage.save_goal(goal)
    
    retrieved = storage.get_goal(goal.id)
    assert retrieved.portfolio_id == portfolio_id