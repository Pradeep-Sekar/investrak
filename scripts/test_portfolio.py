"""Manual testing script for portfolio operations."""
from pathlib import Path
from rich import print
from rich.table import Table

from investrak.core.models import Portfolio
from investrak.core.storage import JsonFileStorage

def main():
    """Run manual tests for portfolio operations."""
    # Initialize storage in a test directory
    storage_path = Path("test_data")
    storage = JsonFileStorage(storage_path)
    
    print("\n[bold green]Testing Portfolio Operations[/bold green]")
    
    # Create some test portfolios
    portfolios = [
        Portfolio(name="Retirement Fund", description="Long-term retirement savings"),
        Portfolio(name="Tech Stocks", description="Technology sector investments"),
        Portfolio(name="Emergency Fund", description="Liquid emergency savings")
    ]
    
    # Save portfolios
    print("\n[bold]Saving portfolios...[/bold]")
    for portfolio in portfolios:
        storage.save_portfolio(portfolio)
        print(f"✓ Saved portfolio: {portfolio.name}")
    
    # List all portfolios
    print("\n[bold]Listing all portfolios:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created")
    
    for p in storage.list_portfolios():
        table.add_row(
            str(p.id),
            p.name,
            p.description or "",
            p.creation_date.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    print(table)
    
    # Test updating a portfolio
    print("\n[bold]Testing portfolio update:[/bold]")
    first_portfolio = storage.list_portfolios()[0]
    updated = Portfolio(
        id=first_portfolio.id,
        name=f"{first_portfolio.name} (Updated)",
        description=first_portfolio.description
    )
    storage.update_portfolio(updated)
    print(f"✓ Updated portfolio: {updated.name}")
    
    # Test deleting a portfolio
    print("\n[bold]Testing portfolio deletion:[/bold]")
    last_portfolio = storage.list_portfolios()[-1]
    storage.delete_portfolio(last_portfolio.id)
    print(f"✓ Deleted portfolio: {last_portfolio.name}")
    
    # Show final state
    print("\n[bold]Final portfolio list:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Created")
    
    for p in storage.list_portfolios():
        table.add_row(
            str(p.id),
            p.name,
            p.description or "",
            p.creation_date.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    print(table)

if __name__ == "__main__":
    main()