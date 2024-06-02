from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class AssetType(Enum):
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


class FundamentalInst(BaseModel):
    symbol: str
    low52: float
    dividendAmount: float
    dividendYield: float
    dividendDate: datetime | None = None
    peRatio: float
    pegRatio: float
    pbRatio: float
    prRatio: float
    pcfRatio: float
    grossMarginTTM: float
    grossMarginMRQ: float
    netProfitMarginTTM: float
    netProfitMarginMRQ: float
    operatingMarginTTM: float
    operatingMarginMRQ: float
    returnOnEquity: float
    returnOnAssets: float
    returnOnInvestment: float
    quickRatio: float
    currentRatio: float
    interestCoverage: float
    totalDebtToCapital: float
    ltDebtToEquity: float
    totalDebtToEquity: float
    epsTTM: float
    epsChangePercentTTM: float
    epsChangeYear: float
    epsChange: float
    revChangeYear: float
    revChangeTTM: float
    revChangeIn: float
    sharesOutstanding: float
    marketCapFloat: float
    marketCap: float
    bookValuePerShare: float
    shortIntToFloat: float
    shortIntDayToCover: float
    divGrowthRate3Year: float
    dividendPayAmount: float
    dividendPayDate: datetime | None = None
    beta: float
    vol1DayAvg: float
    vol10DayAvg: float
    vol3MonthAvg: float
    avg10DaysVolume: int
    avg1DayVolume: int
    avg3MonthVolume: int
    declarationDate: datetime | None = None
    dividendFreq: int
    eps: float
    corpactionDate: str | None = None
    dtnVolume: int
    nextDividendPayDate: datetime | None = None
    nextDividendDate: datetime | None = None
    fundLeverageFactor: float
    fundStrategy: str | None = None


class Instrument(BaseModel):
    cusip: str
    symbol: str
    description: str
    exchange: str
    assetType: AssetType


class Bond(BaseModel):
    cusip: str
    symbol: str
    description: str
    exchange: str
    assetType: AssetType
    bondFactor: str
    bondMultiplier: str
    bondPrice: float


class InstrumentResponse(BaseModel):
    cusip: str | None = None
    symbol: str
    description: str | None = None
    exchange: str
    assetType: AssetType
    bondFactor: str | None = None
    bondMultiplier: str | None = None
    bondPrice: float | None = None
    fundamental: FundamentalInst | None = None
    instrumentInfo: Instrument | None = None
    bondInstrumentInfo: Bond | None = None


class InstrumentsRoot(BaseModel):
    instruments: list[InstrumentResponse]
