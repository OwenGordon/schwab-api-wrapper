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


def default_instrument_response(symbol) -> InstrumentResponse:
    instrument = {
        "cusip": None,
        "symbol": symbol,
        "description": None,
        "exchange": "",
        "assetType": AssetType.UNKNOWN,
        "bondFactor": None,
        "bondMultiplier": None,
        "bondPrice": None,
        "fundamental": {
            "symbol": "",
            "low52": 0,
            "dividendAmount": 0,
            "dividendYield": 0,
            "dividendDate": None,
            "peRatio": 0,
            "pegRatio": 0,
            "pbRatio": 0,
            "prRatio": 0,
            "pcfRatio": 0,
            "grossMarginTTM": 0,
            "grossMarginMRQ": 0,
            "netProfitMarginTTM": 0,
            "netProfitMarginMRQ": 0,
            "operatingMarginTTM": 0,
            "operatingMarginMRQ": 0,
            "returnOnEquity": 0,
            "returnOnAssets": 0,
            "returnOnInvestment": 0,
            "quickRatio": 0,
            "currentRatio": 0,
            "interestCoverage": 0,
            "totalDebtToCapital": 0,
            "ltDebtToEquity": 0,
            "totalDebtToEquity": 0,
            "epsTTM": 0,
            "epsChangePercentTTM": 0,
            "epsChangeYear": 0,
            "epsChange": 0,
            "revChangeYear": 0,
            "revChangeTTM": 0,
            "revChangeIn": 0,
            "sharesOutstanding": 0,
            "marketCapFloat": 0,
            "marketCap": 0,
            "bookValuePerShare": 0,
            "shortIntToFloat": 0,
            "shortIntDayToCover": 0,
            "divGrowthRate3Year": 0,
            "dividendPayAmount": 0,
            "dividendPayDate": None,
            "beta": 0,
            "vol1DayAvg": 0,
            "vol10DayAvg": 0,
            "vol3MonthAvg": 0,
            "avg10DaysVolume": 0,
            "avg1DayVolume": 0,
            "avg3MonthVolume": 0,
            "declarationDate": None,
            "dividendFreq": 0,
            "eps": 0,
            "corpactionDate": None,
            "dtnVolume": 0,
            "nextDividendPayDate": None,
            "nextDividendDate": None,
            "fundLeverageFactor": 0,
            "fundStrategy": None,
        },
        "instrumentInfo": {
            "cusip": "",
            "symbol": symbol,
            "description": "",
            "exchange": "",
            "assetType": AssetType.UNKNOWN,
        },
        "bondInstrumentInfo": None,
    }

    return InstrumentResponse(**instrument)
