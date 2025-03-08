"""Main CLI entry point for InvesTrak."""
from pathlib import Path
from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import Optional
import click
from rich.console import Console
from rich.table import Table

from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType, Goal, GoalStatus
from investrak.core.storage import JsonFileStorage, StorageError
from investrak.core.analytics import PortfolioAnalytics
from ..core.export import PortfolioExporter

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
        table.add_column("ID", no_wrap=True, min_width=36)  # UUID is 36 characters
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

@cli.group()
def goals():
    """Manage your financial goals."""
    pass

@goals.command(name="create")
@click.argument("name")
@click.argument("target-amount", type=float)
@click.argument("target-date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option("--category", "-c", help="Goal category")
@click.option("--description", "-d", help="Goal description")
@click.option("--portfolio", "-p", help="Associated portfolio ID")
def create_goal(name: str, target_amount: float, target_date: datetime, 
                category: str | None, description: str | None, portfolio: str | None):
    """Create a new financial goal."""
    try:
        if target_amount <= 0:
            console.print("[red]Error:[/red] Target amount must be positive")
            return 1

        # Convert target_date to UTC if it's naive
        if target_date.tzinfo is None:
            target_date = target_date.replace(tzinfo=UTC)
            
        current_time = datetime.now(UTC)
        if target_date <= current_time:  # Changed from < to <= for stricter validation
            console.print("[red]Error:[/red] Target date must be in the future")
            return 1

        portfolio_id = None
        if portfolio:
            if not storage.get_portfolio(portfolio):
                console.print("[red]Error:[/red] Portfolio not found")
                return 1
            portfolio_id = portfolio

        goal = Goal(
            name=name,
            target_amount=target_amount,
            target_date=target_date,
            category=category,
            description=description,
            portfolio_id=portfolio_id
        )
        storage.save_goal(goal)
        console.print(f"[green]✓ Created goal:[/green] {goal.name}")
        return 0
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

@goals.command(name="list")
@click.option("--status", "-s", 
              type=click.Choice(["in_progress", "completed", "on_hold"]),
              help="Filter by status")
def list_goals(status: str | None):
    """List all financial goals."""
    try:
        goals = storage.list_goals()
        if not goals:
            console.print("No goals found")
            return 0

        table = Table(title="Financial Goals")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Target Amount")
        table.add_column("Target Date")
        table.add_column("Status")
        table.add_column("Category")

        for goal in goals:
            if status and goal.status.value != status:
                continue
            table.add_row(
                str(goal.id),
                goal.name,
                f"${goal.target_amount:,.2f}",
                goal.target_date.strftime("%Y-%m-%d"),
                goal.status.value,
                goal.category or ""
            )
        
        console.print(table)
        return 0
    except StorageError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

@goals.command(name="update")
@click.argument("goal-id")
@click.option("--name", "-n", help="New goal name")
@click.option("--target-amount", "-a", type=float, help="New target amount")
@click.option("--target-date", "-d", 
              type=click.DateTime(formats=["%Y-%m-%d"]),
              help="New target date (YYYY-MM-DD)")
@click.option("--category", "-c", help="New category")
@click.option("--description", "-d", help="New description")
@click.option("--status", "-s", 
              type=click.Choice(["in_progress", "completed", "on_hold"]),
              help="New status")
def update_goal(goal_id: str, name: str | None, target_amount: float | None,
                target_date: datetime | None, category: str | None,
                description: str | None, status: str | None):
    """Update an existing goal."""
    try:
        goal = storage.get_goal(goal_id)
        if not goal:
            console.print("[red]Error:[/red] Goal not found")
            return 1

        updates = {}
        if name is not None:
            updates["name"] = name
        if target_amount is not None:
            if target_amount <= 0:
                console.print("[red]Error:[/red] Target amount must be positive")
                return 1
            updates["target_amount"] = target_amount
        if target_date is not None:
            if target_date < datetime.now(UTC):
                console.print("[red]Error:[/red] Target date must be in the future")
                return 1
            updates["target_date"] = target_date
        if category is not None:
            updates["category"] = category
        if description is not None:
            updates["description"] = description
        if status is not None:
            updates["status"] = GoalStatus(status)

        updated_goal = goal.model_copy(update=updates)
        storage.update_goal(updated_goal)
        console.print(f"[green]✓ Updated goal:[/green] {updated_goal.name}")
        return 0
    except (StorageError, ValueError) as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

@goals.command(name="delete")
@click.argument("goal-id")
def delete_goal(goal_id: str):
    """Delete a financial goal."""
    try:
        if storage.delete_goal(goal_id):
            console.print("[green]✓ Deleted goal[/green]")
            return 0
        console.print("[red]Error:[/red] Goal not found")
        return 1
    except StorageError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return 1

@cli.group()
def analytics():
    """Portfolio analytics and reporting."""
    pass

@analytics.command(name="value")
@click.argument("portfolio_id")
def portfolio_value(portfolio_id: str):
    """Show current value of a portfolio."""
    try:
        portfolio = storage.get_portfolio(UUID(portfolio_id))
        if not portfolio:
            console.print("[red]Error:[/red] Portfolio not found")
            return 1

        from investrak.core.analytics import PortfolioAnalytics
        analytics = PortfolioAnalytics(storage)
        value = analytics.calculate_portfolio_value(UUID(portfolio_id))
        
        console.print(f"\n[bold]Portfolio:[/bold] {portfolio.name}")
        console.print(f"[bold]Current Value:[/bold] ${value:,.2f}\n")
        return 0
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid portfolio ID")
        return 1

@analytics.command(name="metrics")
@click.argument("portfolio_id")
def portfolio_metrics(portfolio_id: str):
    """Show detailed portfolio metrics."""
    try:
        portfolio = storage.get_portfolio(UUID(portfolio_id))
        if not portfolio:
            console.print("[red]Error:[/red] Portfolio not found")
            return 1

        from investrak.core.analytics import PortfolioAnalytics
        analytics = PortfolioAnalytics(storage)
        metrics = analytics.calculate_portfolio_metrics(UUID(portfolio_id))
        
        table = Table(title=f"Portfolio Metrics: {portfolio.name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Invested", f"${metrics['total_invested']:,.2f}")
        table.add_row("Current Value", f"${metrics['current_value']:,.2f}")
        table.add_row("Profit/Loss", f"${metrics['profit_loss']:,.2f}")
        table.add_row("Profit/Loss %", f"{metrics['profit_loss_percentage']:.2f}%")
        table.add_row("Number of Investments", str(metrics['investment_count']))
        
        console.print(table)
        return 0
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid portfolio ID")
        return 1

@analytics.command(name="performance")
@click.argument("portfolio_id")
@click.option("--from", "start_date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Start date (YYYY-MM-DD)")
@click.option("--to", "end_date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="End date (YYYY-MM-DD)")
def portfolio_performance(portfolio_id: str, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None):
    """Show portfolio performance metrics."""
    try:
        portfolio = storage.get_portfolio(UUID(portfolio_id))
        if not portfolio:
            console.print("[red]Error:[/red] Portfolio not found")
            return 1

        analytics = PortfolioAnalytics(storage)
        metrics = analytics.calculate_performance_metrics(
            UUID(portfolio_id), start_date, end_date
        )
        
        table = Table(title=f"Portfolio Performance: {portfolio.name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Return", f"${metrics['total_return']:,.2f}")
        table.add_row("Total Return %", f"{metrics['total_return_percentage']:.2f}%")
        table.add_row("Annualized Return", f"{metrics['annualized_return']:.2f}%")
        table.add_row("Best Daily Return", f"{metrics['best_day_return']:.2f}%")
        table.add_row("Worst Daily Return", f"{metrics['worst_day_return']:.2f}%")
        
        console.print(table)
        return 0
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid portfolio ID")
        return 1

@analytics.command(name="snapshot")
@click.argument("portfolio_id")
def take_snapshot(portfolio_id: str):
    """Take a snapshot of current portfolio state."""
    try:
        portfolio = storage.get_portfolio(UUID(portfolio_id))
        if not portfolio:
            console.print("[red]Error:[/red] Portfolio not found")
            return 1

        analytics = PortfolioAnalytics(storage)
        snapshot = analytics.take_portfolio_snapshot(UUID(portfolio_id))
        storage.save_portfolio_snapshot(snapshot)
        
        console.print("[green]✓ Portfolio snapshot saved[/green]")
        return 0
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid portfolio ID")
        return 1

@analytics.command(name="export")
@click.argument("portfolio_id")
@click.argument("format", type=click.Choice(['csv', 'pdf']))
@click.argument("output_path")
def export_analytics(portfolio_id: str, format: str, output_path: str):
    """Export portfolio analytics to CSV or PDF format."""
    try:
        portfolio = storage.get_portfolio(UUID(portfolio_id))
        if not portfolio:
            console.print("[red]Error:[/red] Portfolio not found")
            return 1

        analytics = PortfolioAnalytics(storage)
        exporter = PortfolioExporter(analytics)
        
        output_path = Path(output_path)
        if format == 'csv':
            exporter.export_csv(UUID(portfolio_id), output_path)
        else:  # pdf
            exporter.export_pdf(UUID(portfolio_id), output_path)
        
        console.print(f"[green]✓ Analytics exported to {output_path}[/green]")
        return 0
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid portfolio ID")
        return 1
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to export analytics: {str(e)}")
        return 1

if __name__ == "__main__":
    cli()
