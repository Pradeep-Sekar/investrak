"""Data models for InvesTrak."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, PositiveFloat, PositiveInt


class InvestmentType(str, Enum):
    """Type of investment."""
    STOCK = "stock"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"


class InvestmentEntry(BaseModel):
    """Investment entry model representing a single investment."""
    
    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "type": "stock",
                "quantity": 10,
                "purchase_price": "150.50",
                "purchase_date": "2024-01-01T00:00:00Z",
                "category": "Technology"
            }
        }
    )

    id: UUID = Field(default_factory=uuid4)
    portfolio_id: UUID
    symbol: str = Field(..., min_length=1, max_length=10)
    type: InvestmentType
    quantity: PositiveInt
    purchase_price: PositiveFloat
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    category: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class Portfolio(BaseModel):
    """Portfolio model representing an investment portfolio."""
    
    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "name": "Retirement Portfolio",
                "description": "Long-term retirement investment portfolio",
                "creation_date": "2024-01-01T00:00:00Z"
            }
        }
    )

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    creation_date: datetime = Field(default_factory=datetime.utcnow)
