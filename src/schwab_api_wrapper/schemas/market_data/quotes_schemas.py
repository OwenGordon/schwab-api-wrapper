from pydantic import BaseModel, Field, RootModel
from typing import Optional, Union, Dict, Literal
from enum import Enum
from datetime import datetime


class ExtendedMarket(BaseModel):
    """
    Quote data for extended hours
    """

    askPrice: float  # Extended market ask price
    askSize: int  # Extended market ask size
    bidPrice: float  # Extended market bid price
    bidSize: int  # Extended market bid size
    lastPrice: float  # Extended market last price
    lastSize: int  # Regular market last size TODO documentation must be wrong
    mark: float  # mark price
    quoteTime: int  # Extended market quote time in milliseconds since Epoch
    totalVolume: int  # Total volume
    tradeTime: int  # Extended market trade time in milliseconds since Epoch


class DivFreqOption(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    SIX = 6
    ELEVEN = 11
    TWELVE = 12


class FundStrategyOption(Enum):
    A = "A"
    L = "L"
    P = "P"
    Q = "Q"
    S = "S"


class Fundamental(BaseModel):
    """
    Fundamentals of a security
    """

    avg10DaysVolume: float  # Average 10 day volume
    avg1YearVolume: (
        float  # Average 1 day volume  TODO this documentation must be incorrect
    )
    declarationDate: datetime | None = None  # Declaration date in yyyy-mm-ddThh:mm:ssZ
    divAmount: float  # Dividend Amount
    divExDate: datetime | None = None  # Dividend date in yyyy-mm-ddThh:mm:ssZ
    # 1 - once a year or annually
    # 2 - 2x a year of semi-annualy
    # 3 - 3x a year
    # 4 - 4x a year or quarterly
    # 6 - 6x per yr or every other month
    # 11 - 11x a year
    # 12 - 12x a year or monthly
    divPayAmount: float  # Dividend Pay Amount
    divPayDate: datetime | None = None  # Dividend pay date in yyyy-mm-ddThh:mm:ssZ
    divYield: float  # Dividend yield
    eps: float  # Earnings per Share
    fundLeverageFactor: float  # Fund Leverage Factor + > 0 <-
    nextDivExDate: datetime | None = None  # Next Dividend date in yyyy-MM-ddThh:mm:ssZ
    nextDivPayDate: datetime | None = (
        None  # Next Dividend pay date in yyyy-MM-ddThh:mm:ssZ
    )
    peRatio: float  # P/E Ratio
    divFreq: Optional[DivFreqOption] = None  # Dividend frequency
    fundStrategy: Optional[FundStrategyOption] = None  # FundStrategy
    # "A" - Active
    # "L" - Leveraged
    # "P" - Passive
    # "Q" - Quantitative
    # "S" - Short


class QuoteEquity(BaseModel):
    """
    Quote data of Equity security
    """

    fiftyTwoWeekHigh: float = Field(
        ..., alias="52WeekHigh"
    )  # Highest price traded in the past 12 months, or 52 weeks
    fiftyTwoWeekLow: float = Field(
        ..., alias="52WeekLow"
    )  # Lowest price traded in the past 12 months, or 52 weeks
    askMICId: Optional[str] = None  # ask MIC code
    askPrice: float  # Current Best Ask Price
    askSize: int  # Number of shares for ask
    askTime: int  # Last ask time in milliseconds since Epoch
    bidMICId: Optional[str] = None  # bid MIC code
    bidPrice: float  # Current Best Bid Price
    bidSize: int  # Number of shares for bid
    bidTime: int  # last bid tim in milliseconds since Epoch
    closePrice: float  # Previous day's closing price
    highPrice: float  # Day's high trade price
    lastMICId: Optional[str] = None  # Last MIC code
    lastPrice: float  # TODO documentation missing on site
    lastSize: int  # Number of sahres traded with last trade
    lowPrice: float  # Day's low trade price
    mark: float  # Mark price
    markChange: float  # Mark Price change
    markPercentChange: float  # Mark Price percent change
    netChange: float  # Current Last-Prev Close
    netPercentChange: float  # Net Percentage Change
    openPrice: float  # Price at market open
    quoteTime: int  # Last quote time in milliseconds since Epoch
    securityStatus: str  # Status of security
    totalVolume: int  # Aggregated shares traded throughout the day, includig pre/post market hours
    tradeTime: int  # Last trade time in milliseconds since Epoch
    volatility: Optional[float] = None  # Option Risk/Volatility Measurement


class QuoteIndex(BaseModel):
    """
    Quote data of Index security
    """

    fiftyTwoWeekHigh: float = Field(
        ..., alias="52WeekHigh"
    )  # Highest price traded in the past 12 months, or 52 weeks
    fiftyTwoWeekLow: float = Field(
        ..., alias="52WeekLow"
    )  # Lowest price traded in the past 12 months, or 52 weeks
    closePrice: float  # Previous day's closing price
    highPrice: float  # Day's high trade price
    lowPrice: float  # Day's low trade price
    netChange: float  # Current Last-Prev Close
    netPercentChange: float  # Net Percentage Change
    openPrice: float  # Price at market open
    securityStatus: str  # Status of security
    totalVolume: int  # Aggregated shares traded throughout the day, includig pre/post market hours
    tradeTime: int  # Last trade time in milliseconds since Epoch


class QuoteMutualFund(BaseModel):
    """
    Quote data of Mutual Fund security
    """

    fiftyTwoWeekHigh: float = Field(
        ..., alias="52WeekHigh"
    )  # Highest price traded in the past 12 months, or 52 weeks
    fiftyTwoWeekLow: float = Field(
        ..., alias="52WeekLow"
    )  # Lowest price traded in the past 12 months, or 52 weeks
    closePrice: float  # Previous day's closing price
    nAV: float  # Net Asset Value
    netChange: float  # Current Last-Prev Close
    netPercentChange: Optional[float] = None  # Net Percentage Change
    securityStatus: str  # Status of security
    tradeTime: int  # Last trade time in milliseconds since Epoch
    totalVolume: Optional[int] = (
        None  # Aggregated shares traded throughout the day, includig pre/post market hours
    )
    lastPrice: Optional[float] = (
        None  # TODO why is this in the response when the api docs make no mention...
    )


class ReferenceEquity(BaseModel):
    """
    Reference data of Equity security
    """

    cusip: str  # CUSIP of Instrument
    description: str  # Description of Instrument
    exchange: str  # Exchange Code
    exchangeName: str  # Exchange Name
    fsiDesc: Optional[str] = None  # FSI Desc
    htbQuantity: Optional[int] = None  # Hard to borrow quantity
    htbRate: Optional[float] = None  # Hard to borrow rate
    isHardToBorrow: Optional[bool] = None  # is Hard to borrow security
    isShortable: Optional[bool] = None  # is shortable security
    otcMarketTier: Optional[str] = None  # OTC Market Tier


class ReferenceIndex(BaseModel):
    """
    Reference data of Index security
    """

    description: str  # Description of Instrument
    exchange: str  # Exchange Code
    exchangeName: str  # Exchange Name


class ReferenceMutualFund(BaseModel):
    """
    Reference data of MutualFund security
    """

    cusip: Optional[str] = None  # CUSIP of Instrument
    description: str  # Description of Instrument
    exchange: str  # Exchange Code
    exchangeName: str  # Exchange Name


class RegularMarket(BaseModel):
    """
    Market info of security
    """

    regularMarketLastPrice: float  # Regular market last price
    regularMarketLastSize: int  # Regular market last size
    regularMarketNetChange: float  # Regular market net change
    regularMarketPercentChange: float  # Regular market percent change
    regularMarketTradeTime: int  # Regular market trade time in milliseconds since Epoch


class AssetMainType(str, Enum):
    BOND = "BOND"
    EQUITY = "EQUITY"
    FOREX = "FOREX"
    FUTURE = "FUTURE"
    FUTURE_OPTION = "FUTURE_OPTION"
    INDEX = "INDEX"
    MUTUAL_FUND = "MUTUAL_FUND"
    OPTION = "OPTION"


class AssetSubType(Enum):
    COE = "COE"
    PRF = "PRF"
    ADR = "ADR"
    GDR = "GDR"
    CEF = "CEF"
    ETF = "ETF"
    ETN = "ETN"
    UIT = "UIT"
    WAR = "WAR"
    RGT = "RGT"


class QuoteType(Enum):
    NBBO = "NBBO"
    NFL = "NFL"


class EquityResponse(BaseModel):
    """
    Quote info of Equity security
    """

    assetMainType: Literal[AssetMainType.EQUITY]  # instrument's asset type
    ssid: Optional[int] = None  # SSID of instrument
    symbol: str  # Symbol of instrument
    realtime: Optional[bool] = None  # is quote realtime
    assetSubType: Optional[AssetSubType] = (
        None  # Asset Sub Type (only there if applicable)
    )
    quoteType: Optional[QuoteType] = None  # NBBO - realtime, NFL - Non-fee liable quote
    extended: Optional[ExtendedMarket] = None
    fundamental: Optional[Fundamental] = None
    quote: Optional[QuoteEquity] = None
    reference: Optional[ReferenceEquity] = None
    regular: Optional[RegularMarket] = None


class IndexResponse(BaseModel):
    """
    Quote info for Index security
    """

    assetMainType: Literal[AssetMainType.INDEX]  # instrument's asset type
    ssid: int  # SSID of instrument
    symbol: str  # Symbol of instrument
    realtime: bool  # is quote realtime
    quote: Optional[QuoteIndex] = None
    reference: Optional[ReferenceIndex] = None


class MutaulFundAssetSubTypeOption(Enum):
    OEF = "OEF"
    CEF = "CEF"
    MMF = "MMF"


class MutualFundResponse(BaseModel):
    """
    Quote info of MutualFund security
    """

    assetMainType: Literal[AssetMainType.MUTUAL_FUND]  # instrument's asset type
    ssid: Optional[int] = None  # SSID of Instrument
    symbol: str  # Symbol of instrument
    realtime: bool  # is quote realtime
    assetSubType: Optional[MutaulFundAssetSubTypeOption] = (
        None  # Asset Sub Type (only there if applicable)
    )
    fundamental: Optional[Fundamental] = None
    quote: Optional[QuoteMutualFund] = None
    reference: Optional[ReferenceMutualFund] = None


class QuoteError(BaseModel):
    """
    Partial or Custom errors per request
    """

    invalidCusips: Optional[list[str]] = None  # list of invalid cusips from request
    invalidSSIDs: Optional[list[int]] = None  # list of invalid SSIDs from request
    invalidSymbols: list[str]  # list of invalid symbols from request


QuoteResponseObject = Union[
    EquityResponse, IndexResponse, MutualFundResponse, QuoteError
]


# Define the QuoteResponse model with dynamic keys
class QuoteResponse(RootModel):
    root: Dict[str, QuoteResponseObject]
    """
    a (symbol, QuoteResponseObject) map
    """

    def __getitem__(self, item):
        return self.root[item]

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)
