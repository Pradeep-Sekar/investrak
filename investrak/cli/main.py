"""Main CLI entry point for InvesTrak."""
from pathlib import Path
from datetime import datetime, UTC
import click
from rich.console import Console
from rich.table import Table

from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType
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

@cli.group()
def investment():
    """Manage your investments within portfolios."""
    pass

@investment.command(name="add")
@click.argument("portfolio-id")
@click.argument("symbol")
@click.argument("type", type=click.Choice(["stock", "etf", "mutual_fund"]))
@click.argument("quantity", type=int)
@click.argument("price", type=float)
@click.option("--date", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), 
              default=str(datetime.now(UTC).strftime("%Y-%m-%d")),
              help="Purchase date (YYYY-MM-DD)")
@click.option("--category", "-c", help="Investment category")
@click.option("--notes", "-n", help="Additional notes")
def add_investment(portfolio_id: str, symbol: str, type: str, quantity: int, 
                  price: float, date: datetime, category: str | None, notes: str | None):
    """Add a new investment to a portfolio."""
    try:
        if quantity <= 0:
            console.print("[red]Error:[/red] Invalid value for 'QUANTITY': must be positive")
            return 0  # Return 0 for validation errors
            
        if price <= 0:
            console.print("[red]Error:[/red] Price must be positive")
            return 0  # Return 0 for validation errors
            
        if len(symbol) > 10:
            console.print("[red]Error:[/red] Symbol too long")
            return 0  # Return 0 for validation errors
            
        portfolio = storage.get_portfolio(portfolio_id)
        if not portfolio:
            console.print("[red]Error:[/red] Portfolio not found")
            return 0  # Return 0 for validation errors

        investment = InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol=symbol.upper(),
            type=InvestmentType(type),
            quantity=quantity,
            purchase_price=price,
            purchase_date=date,
            category=category,
            notes=notes
        )
        storage.save_investment(investment)
        console.print(f"[green]✓ Added investment:[/green] {investment.symbol}")
        return 0
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

@investment.command(name="list")
@click.argument("portfolio-id")
def list_investments(portfolio_id: str):
    """List all investments in a portfolio."""
    try:
        portfolio = storage.get_portfolio(portfolio_id)
        if not portfolio:
            console.print(f"[red]Error:[/red] Portfolio {portfolio_id} not found")
            return

        investments = storage.list_investments(portfolio_id)
        if not investments:
            console.print("[yellow]No investments found in this portfolio[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Symbol")
        table.add_column("Type")
        table.add_column("Quantity")
        table.add_column("Purchase Price")
        table.add_column("Purchase Date")
        table.add_column("Category")  # Make sure this is displayed

        for inv in investments:
            table.add_row(
                str(inv.id),
                inv.symbol,
                inv.type.value,
                str(inv.quantity),
                f"${inv.purchase_price:.2f}",
                inv.purchase_date.strftime("%Y-%m-%d"),
                inv.category or "-"  # Use "-" for empty categories
            )
        console.print(table)
    except StorageError as e:
        console.print(f"[red]Error listing investments:[/red] {str(e)}")

@investment.command(name="delete")
@click.argument("investment-id")
def delete_investment(investment_id: str):
    """Delete an investment entry."""
    try:
        if storage.delete_investment(investment_id):
            console.print(f"[green]✓ Deleted investment[/green]")
        else:
            console.print(f"[red]Error:[/red] Investment {investment_id} not found")
    except StorageError as e:
        console.print(f"[red]Error deleting investment:[/red] {str(e)}")

@investment.command(name="update")
@click.argument("investment-id")
@click.option("--quantity", "-q", type=int, help="New quantity")
@click.option("--price", "-p", type=float, help="New purchase price")
@click.option("--category", "-c", help="New category")
@click.option("--notes", "-n", help="New notes")
def update_investment(investment_id: str, quantity: int | None, price: float | None,
                     category: str | None, notes: str | None):
    """Update an existing investment."""
    try:
        investment = storage.get_investment(investment_id)
        if not investment:
            console.print(f"[red]Error:[/red] Investment {investment_id} not found")
            return

        updates = {}
        if quantity is not None:
            updates["quantity"] = quantity
        if price is not None:
            updates["purchase_price"] = price
        if category is not None:
            updates["category"] = category
        if notes is not None:
            updates["notes"] = notes

        updated_investment = investment.model_copy(update=updates)
        storage.update_investment(updated_investment)
        console.print(f"[green]✓ Updated investment:[/green] {updated_investment.symbol}")
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error updating investment:[/red] {str(e)}")

if __name__ == "__main__":
    cli()
