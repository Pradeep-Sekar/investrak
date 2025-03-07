"""Export functionality for portfolio data."""
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Dict
from uuid import UUID
import csv
import json
from fpdf import FPDF  # We'll need to add fpdf to requirements.txt

from .models import Portfolio, PortfolioSnapshot
from .analytics import PortfolioAnalytics

class PortfolioExporter:
    """Handles exporting portfolio data in various formats."""
    
    def __init__(self, analytics: PortfolioAnalytics):
        self.analytics = analytics

    def export_csv(self, portfolio_id: UUID, path: Path) -> None:
        """Export portfolio data to CSV format."""
        metrics = self.analytics.calculate_portfolio_metrics(portfolio_id)
        performance = self.analytics.calculate_performance_metrics(portfolio_id)
        
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Portfolio Analytics Report'])
            writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])
            
            # Current metrics
            writer.writerow(['Current Metrics'])
            writer.writerow(['Total Invested', f"${metrics['total_invested']:.2f}"])
            writer.writerow(['Current Value', f"${metrics['current_value']:.2f}"])
            writer.writerow(['Profit/Loss', f"${metrics['profit_loss']:.2f}"])
            writer.writerow(['Return %', f"{metrics['profit_loss_percentage']:.2f}%"])
            writer.writerow([])
            
            # Performance metrics
            writer.writerow(['Performance Metrics'])
            writer.writerow(['Total Return', f"${performance['total_return']:.2f}"])
            writer.writerow(['Total Return %', f"{performance['total_return_percentage']:.2f}%"])
            writer.writerow(['Annualized Return', f"{performance['annualized_return']:.2f}%"])
            writer.writerow(['Best Daily Return', f"{performance['best_day_return']:.2f}%"])
            writer.writerow(['Worst Daily Return', f"{performance['worst_day_return']:.2f}%"])

    def export_pdf(self, portfolio_id: UUID, path: Path) -> None:
        """Export portfolio data to PDF format."""
        metrics = self.analytics.calculate_portfolio_metrics(portfolio_id)
        performance = self.analytics.calculate_performance_metrics(portfolio_id)
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Portfolio Analytics Report', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        
        # Current metrics
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Current Metrics', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Total Invested: ${metrics['total_invested']:.2f}", 0, 1)
        pdf.cell(0, 10, f"Current Value: ${metrics['current_value']:.2f}", 0, 1)
        pdf.cell(0, 10, f"Profit/Loss: ${metrics['profit_loss']:.2f}", 0, 1)
        pdf.cell(0, 10, f"Return %: {metrics['profit_loss_percentage']:.2f}%", 0, 1)
        
        # Performance metrics
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Performance Metrics', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Total Return: ${performance['total_return']:.2f}", 0, 1)
        pdf.cell(0, 10, f"Total Return %: {performance['total_return_percentage']:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Annualized Return: {performance['annualized_return']:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Best Daily Return: {performance['best_day_return']:.2f}%", 0, 1)
        pdf.cell(0, 10, f"Worst Daily Return: {performance['worst_day_return']:.2f}%", 0, 1)
        
        pdf.output(str(path))