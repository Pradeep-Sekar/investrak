"""Main CLI entry point for InvesTrak."""
import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option()
def cli():
    """InvesTrak - CLI financial portfolio and goal tracking application."""
    pass

@cli.command()
def portfolio():
    """Manage your investment portfolio."""
    console.print("[bold green]Portfolio management[/bold green]")

@cli.command()
def goals():
    """Track your financial goals."""
    console.print("[bold blue]Financial goals tracking[/bold blue]")

if __name__ == "__main__":
    cli()