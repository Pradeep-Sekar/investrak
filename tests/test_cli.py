"""Tests for the CLI interface."""
from click.testing import CliRunner

from investrak.cli.main import cli

def test_cli_help():
    """Test the CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "InvesTrak" in result.output

def test_portfolio_command():
    """Test the portfolio command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["portfolio"])
    assert result.exit_code == 0
    assert "Portfolio management" in result.output

def test_goals_command():
    """Test the goals command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["goals"])
    assert result.exit_code == 0
    assert "Financial goals tracking" in result.output