"""Tests for portfolio export functionality."""
import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from fpdf import FPDF

from investrak.core.export import PortfolioExporter
from investrak.core.models import Portfolio, InvestmentEntry, InvestmentType
from investrak.core.analytics import PortfolioAnalytics
from investrak.core.storage import JsonFileStorage

@pytest.fixture
def test_portfolio(tmp_path):
    """Create a test portfolio with sample data."""
    storage = JsonFileStorage(tmp_path)
    
    portfolio = Portfolio(name="Test Portfolio")
    storage.save_portfolio(portfolio)
    
    investments = [
        InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="AAPL",
            type=InvestmentType.STOCK,
            quantity=10,
            purchase_price=150.00
        ),
        InvestmentEntry(
            portfolio_id=portfolio.id,
            symbol="GOOGL",
            type=InvestmentType.STOCK,
            quantity=5,
            purchase_price=2500.00
        )
    ]
    
    for inv in investments:
        storage.save_investment(inv)
    
    return storage, portfolio

def test_csv_export(test_portfolio, tmp_path):
    """Test exporting portfolio data to CSV."""
    storage, portfolio = test_portfolio
    analytics = PortfolioAnalytics(storage)
    exporter = PortfolioExporter(analytics)
    
    output_path = tmp_path / "test_export.csv"
    exporter.export_csv(portfolio.id, output_path)
    
    # Verify file was created
    assert output_path.exists()
    
    # Read and verify content
    with open(output_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)
        
        # Check headers
        assert "Portfolio Analytics Report" in rows[0][0]
        assert "Generated:" in rows[1][0]
        
        # Check metrics
        metrics_found = False
        for row in rows:
            if row and "Current Metrics" in row[0]:
                metrics_found = True
            if metrics_found and "Total Invested" in row[0]:
                assert "$14000.00" in row[1]  # Expected total investment
    
def test_pdf_export(test_portfolio, tmp_path):
    """Test exporting portfolio data to PDF."""
    storage, portfolio = test_portfolio
    analytics = PortfolioAnalytics(storage)
    exporter = PortfolioExporter(analytics)
    
    output_path = tmp_path / "test_export.pdf"
    exporter.export_pdf(portfolio.id, output_path)
    
    # Verify file was created and is a valid PDF
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    
    # Basic PDF validation (check first few bytes for PDF signature)
    with open(output_path, 'rb') as f:
        assert f.read(4) == b'%PDF'

def test_export_invalid_portfolio(tmp_path):
    """Test exporting with invalid portfolio ID."""
    storage = JsonFileStorage(tmp_path)
    analytics = PortfolioAnalytics(storage)
    exporter = PortfolioExporter(analytics)
    
    with pytest.raises(Exception):
        exporter.export_csv(uuid4(), tmp_path / "should_not_exist.csv")
    
    with pytest.raises(Exception):
        exporter.export_pdf(uuid4(), tmp_path / "should_not_exist.pdf")