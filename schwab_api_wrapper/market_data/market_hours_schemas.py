from pydantic import BaseModel, validator, RootModel
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime, date


class Interval(BaseModel):
    start: datetime  # format: YYYY-mm-ddThh:mm:ssZ
    end: datetime


class MarketTypeOption(Enum):
    BOND = "BOND"
    EQUITY = "EQUITY"
    ETF = "ETF"
    EXTENDED = "EXTENDED"
    FOREX = "FOREX"
    FUTURE = "FUTURE"
    FUTURE_OPTION = "FUTURE_OPTION"
    FUNDAMENTAL = "FUNDAMENTAL"
    INDEX = "INDEX"
    INDICATOR = "INDICATOR"
    MUTUAL_FUND = "MUTUAL_FUND"
    OPTION = "OPTION"
    UNKNOWN = "UNKNOWN"


class Hours(BaseModel):
    date: date
    marketType: MarketTypeOption
    product: str
    isOpen: bool
    exchange: Optional[str] = None
    category: Optional[str] = None
    productName: Optional[str] = None
    sessionHours: Optional[Dict[str, List[Interval]]] = None


# Define the QuoteResponse model with dynamic keys
class MarketHoursResponse(RootModel):
    root: Dict[str, Dict[str, Hours]]

    def __getitem__(self, item):
        return self.root[item]

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)
