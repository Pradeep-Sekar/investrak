"""Data models for InvesTrak."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


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
