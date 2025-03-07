"""Main CLI entry point for InvesTrak."""
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from investrak.core.models import Portfolio
from investrak.core.storage import JsonFileStorage, StorageError

console = Console()
storage = JsonFileStorage(Path.home() / ".investrak")

@click.group()
@click.version_option()
def cli():
    """InvesTrak - CLI financial portfolio and goal tracking application."""
    pass

@cli.group()
def portfolio():
    """Manage your investment portfolios."""
    pass

@portfolio.command(name="create")
@click.argument("name")
@click.option("--description", "-d", help="Portfolio description")
def create_portfolio(name: str, description: str | None):
    """Create a new portfolio."""
    try:
        portfolio = Portfolio(name=name, description=description)
        storage.save_portfolio(portfolio)
        console.print(f"[green]✓ Created portfolio:[/green] {portfolio.name}")
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error creating portfolio:[/red] {str(e)}")

@portfolio.command(name="list")
def list_portfolios():
    """List all portfolios."""
    try:
        portfolios = storage.list_portfolios()
        if not portfolios:
            console.print("[yellow]No portfolios found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Created")

        for p in portfolios:
            table.add_row(
                str(p.id),
                p.name,
                p.description or "",
                p.creation_date.strftime("%Y-%m-%d %H:%M:%S")
            )
        console.print(table)
    except StorageError as e:
        console.print(f"[red]Error listing portfolios:[/red] {str(e)}")

@portfolio.command(name="delete")
@click.argument("portfolio_id")
def delete_portfolio(portfolio_id: str):
    """Delete a portfolio by ID."""
    try:
        if storage.delete_portfolio(portfolio_id):
            console.print(f"[green]✓ Deleted portfolio:[/green] {portfolio_id}")
        else:
            console.print(f"[yellow]Portfolio not found:[/yellow] {portfolio_id}")
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error deleting portfolio:[/red] {str(e)}")

@portfolio.command(name="update")
@click.argument("portfolio_id")
@click.argument("name")
@click.option("--description", "-d", help="New portfolio description")
def update_portfolio(portfolio_id: str, name: str, description: str | None):
    """Update a portfolio's name and description."""
    try:
        existing = storage.get_portfolio(portfolio_id)
        if not existing:
            console.print(f"[yellow]Portfolio not found:[/yellow] {portfolio_id}")
            return

        updated = Portfolio(
            id=existing.id,
            name=name,
            description=description
        )
        storage.update_portfolio(updated)
        console.print(f"[green]✓ Updated portfolio:[/green] {updated.name}")
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error updating portfolio:[/red] {str(e)}")

if __name__ == "__main__":
    cli()
