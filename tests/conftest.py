"""Test configuration and fixtures."""
import pytest
from click.testing import CliRunner

@pytest.fixture
def cli_runner():
    """Fixture for CLI testing."""
    return CliRunner()