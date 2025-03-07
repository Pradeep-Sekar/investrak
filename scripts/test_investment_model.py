"""Manual testing script for investment entry model."""
from uuid import uuid4
from rich import print
from rich.table import Table

from investrak.core.models import InvestmentEntry, InvestmentType

def test_valid_entries():
    """Test creating valid investment entries."""
    portfolio_id = uuid4()
    
    # Test different investment types
    entries = [
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.50,
            category="Technology"
        ),
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="VTI",
            type=InvestmentType.ETF,
            quantity=5,
            purchase_price=220.75,
            category="Index Funds"
        ),
        InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol="VFIAX",
            type=InvestmentType.MUTUAL_FUND,
            quantity=100,
            purchase_price=400.00,
            category="Mutual Funds",
            notes="S&P 500 Index Fund"
        )
    ]

    # Display entries in a table
    table = Table(title="Valid Investment Entries")
    table.add_column("Symbol")
    table.add_column("Type")
    table.add_column("Quantity")
    table.add_column("Price")
    table.add_column("Category")
    
    for entry in entries:
        table.add_row(
            entry.symbol,
            entry.type.value,
            str(entry.quantity),
            f"${entry.purchase_price:.2f}",
            entry.category or ""
        )
    
    print(table)

def test_invalid_entries():
    """Test invalid investment entries."""
    portfolio_id = uuid4()
    
    print("\n[bold red]Testing Invalid Entries[/bold red]")
    
    test_cases = [
        {
            "desc": "Empty symbol",
            "data": {
                "portfolio_id": portfolio_id,
                "symbol": "",
                "type": InvestmentType.STOCK,
                "quantity": 10,
                "purchase_price": 150.50
            }
        },
        {
            "desc": "Zero quantity",
            "data": {
                "portfolio_id": portfolio_id,
                "symbol": "AAPL",
                "type": InvestmentType.STOCK,
                "quantity": 0,
                "purchase_price": 150.50
            }
        },
        {
            "desc": "Negative price",
            "data": {
                "portfolio_id": portfolio_id,
                "symbol": "AAPL",
                "type": InvestmentType.STOCK,
                "quantity": 10,
                "purchase_price": -150.50
            }
        }
    ]
    
    for case in test_cases:
        try:
            InvestmentEntry(**case["data"])
            print(f"❌ {case['desc']}: Should have failed")
        except Exception as e:
            print(f"✓ {case['desc']}: Failed as expected")
            print(f"  Error: {str(e)}\n")

if __name__ == "__main__":
    print("\n[bold green]Testing Investment Entry Model[/bold green]")
    test_valid_entries()
    test_invalid_entries()