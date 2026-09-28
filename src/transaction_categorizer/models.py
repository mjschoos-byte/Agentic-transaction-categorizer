from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    REVENUE = "Revenue"
    RENT = "Rent"
    PAYROLL = "Payroll"
    TRAVEL = "Travel"
    MEALS = "Meals"
    SOFTWARE = "Software"
    OFFICE_SUPPLIES = "Office Supplies"
    UTILITIES = "Utilities"
    PROFESSIONAL_SERVICES = "Professional Services"
    BANK_FEES = "Bank Fees"
    TRANSFER = "Transfer"
    UNCATEGORIZED = "Uncategorized"


class AgentClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0, le=1)
    merchant: str = Field(min_length=1, max_length=100)
    reason: str = Field(min_length=1, max_length=240)


@dataclass(frozen=True)
class Transaction:
    date: str
    description: str
    amount: float


@dataclass(frozen=True)
class Classification:
    category: Category
    confidence: float
    merchant: str
    source: str
    reason: str

