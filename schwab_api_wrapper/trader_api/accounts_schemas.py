from pydantic import BaseModel, RootModel, validator
from typing import Optional, List, Dict, Union, Literal, Iterator
from datetime import datetime
from enum import Enum


class AccountNumberHash(BaseModel):
    accountNumber: str
    hashValue: str


class AccountNumbersResponse(RootModel[List[AccountNumberHash]]):
    root: List[AccountNumberHash]

    def __getitem__(self, item: int) -> AccountNumberHash:
        return self.root[item]

    def __iter__(self):
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class AssetType(str, Enum):
    EQUITY = "EQUITY"
    MUTUAL_FUND = "MUTUAL_FUND"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    FOREX = "FOREX"
    INDEX = "INDEX"
    CASH_EQUIVALENT = "CASH_EQUIVALENT"
    FIXED_INCOME = "FIXED_INCOME"
    PRODUCT = "PRODUCT"
    CURRENCY = "CURRENCY"
    COLLECTIVE_INVESTMENT = "COLLECTIVE_INVESTMENT"


class CashEquivalentType(Enum):
    SWEEP_VEHICLE = "SWEEP_VEHICLE"
    SAVINGS = "SAVINGS"
    MONEY_MARKET_FUND = "MONEY_MARKET_FUND"
    UNKNOWN = "UNKNOWN"


class AccountCashEquivalent(BaseModel):
    assetType: Literal[AssetType.CASH_EQUIVALENT]
    cusip: str
    symbol: str
    description: str
    instrumentId: int
    netChange: float
    type: CashEquivalentType


class AccountEquity(BaseModel):
    assetType: Literal[AssetType.EQUITY]
    cusip: Optional[str] = None
    symbol: str
    description: Optional[str] = None
    instrumentId: Optional[int] = None
    netChange: Optional[float] = None


class AccountFixedIncome(BaseModel):
    assetType: Literal[AssetType.FIXED_INCOME]
    cusip: str
    symbol: str
    description: str
    instrumentId: int
    netChange: float
    maturityDate: datetime
    factor: float
    variableRate: float


class AccountMutualFund(BaseModel):
    assetType: Literal[AssetType.MUTUAL_FUND]
    cusip: str
    symbol: str
    description: str
    instrumentId: int
    netChange: float


class CurrencyType(Enum):
    USD = "USD"
    CAD = "CAD"
    EUR = "EUR"
    JPY = "JPY"


class AccountAPIOptionDeliverable(BaseModel):
    symbol: int  # TODO not sure what the docs should be
    deliverableUnits: float
    apiCurrencyType: CurrencyType
    assetType: AssetType


class PutCall(Enum):
    PUT = "PUT"
    CALL = "CALL"
    UNKNOWN = "UNKNOWN"


class OptionType(Enum):
    VANILLA = "VANILLA"
    BINARY = "BINARY"
    BARRIER = "BARRIER"
    UNKNOWN = "UNKNOWN"


class AccountOption(BaseModel):
    assetType: Literal[AssetType.OPTION]
    cusip: str
    symbol: str
    description: str
    instrumentId: int
    netChange: float
    optionDeliverables: (
        AccountAPIOptionDeliverable  # TODO not quite sure what this mapping should be
    )
    putCall: PutCall
    optionMultiplier: int
    type: OptionType
    underlyingSymbol: str


AccountsInstrument = Union[
    AccountCashEquivalent,
    AccountEquity,
    AccountFixedIncome,
    AccountMutualFund,
    AccountOption,
]


class Position(BaseModel):
    shortQuantity: float
    averagePrice: float
    currentDayProfitLoss: float
    currentDayProfitLossPercentage: float
    longQuantity: float
    settledLongQuantity: float
    settledShortQuantity: float
    instrument: AccountsInstrument
    marketValue: float
    maintenanceRequirement: float
    currentDayCost: float
    agedQuantity: Optional[float] = None
    averageLongPrice: Optional[float] = None
    averageShortPrice: Optional[float] = None
    taxLotAverageLongPrice: Optional[float] = None
    taxLotAverageShortPrice: Optional[float] = None
    longOpenProfitLoss: Optional[float] = None
    shortOpenProfitLoss: Optional[float] = None
    previousSessionLongQuantity: Optional[float] = None
    previousSessionShortQuantity: Optional[float] = None


class AccountType(Enum):
    CASH = "CASH"
    MARGIN = "MARGIN"


class MarginInitialBalance(BaseModel):
    accruedInterest: float
    availableFundsNonMarginableTrade: float
    bondValue: float
    buyingPower: float
    cashBalance: float
    cashAvailableForTrading: float
    cashReceipts: float
    dayTradingBuyingPower: float
    dayTradingBuyingPowerCall: float
    dayTradingEquityCall: float
    equity: float
    equityPercentage: float
    liquidationValue: float
    longMarginValue: float
    longOptionMarketValue: float
    longStockValue: float
    maintenanceCall: float
    maintenanceRequirement: float
    margin: float
    marginEquity: float
    moneyMarketFund: float
    mutualFundValue: float
    regTCall: float
    shortMarginValue: float
    shortOptionMarketValue: float
    shortStockValue: float
    totalCash: float
    isInCall: float
    unsettledCash: Optional[float] = None
    pendingDeposits: float
    marginBalance: float
    shortBalance: float
    accountValue: float


class MarginBalance(BaseModel):
    accruedInterest: float
    cashBalance: float
    cashReceipts: float
    longOptionMarketValue: float
    liquidationValue: float
    longMarketValue: float
    moneyMarketFund: float
    savings: float
    shortMarketValue: float
    pendingDeposits: float
    mutualFundValue: float
    bondValue: float
    shortOptionMarketValue: float
    availableFunds: float
    availableFundsNonMarginableTrade: float
    buyingPower: float
    buyingPowerNonMarginableTrade: float
    dayTradingBuyingPower: float
    equity: float
    equityPercentage: float
    longMarginValue: float
    maintenanceCall: float
    maintenanceRequirement: float
    marginBalance: float
    regTCall: float
    shortBalance: float
    shortMarginValue: float
    sma: float


class MarginProjectedBalance(BaseModel):
    availableFunds: float
    availableFundsNonMarginableTrade: float
    buyingPower: float
    dayTradingBuyingPower: float
    dayTradingBuyingPowerCall: float
    maintenanceCall: float
    regTCall: float
    isInCall: float
    stockBuyingPower: float


class CashInitialBalance(BaseModel):
    accruedInterest: float
    cashAvailableForTrading: float
    cashAvailableForWithdrawal: float
    cashBalance: float
    bondValue: float
    cashReceipts: float
    liquidationValue: float
    longOptionMarketValue: float
    longStockValue: float
    moneyMarketFund: float
    mutualFundValue: float
    shortOptionMarketValue: float
    shortStockValue: float
    isInCall: bool
    unsettledCash: float
    cashDebitCallValue: float
    pendingDeposits: float
    accountValue: float


class CashBalance(BaseModel):
    accruedInterest: float
    cashBalance: float
    cashReceipts: float
    longOptionMarketValue: float
    liquidationValue: float
    longMarketValue: float
    moneyMarketFund: float
    savings: float
    shortMarketValue: float
    pendingDeposits: float
    mutualFundValue: float
    bondValue: float
    shortOptionMarketValue: float
    cashAvailableForTrading: float
    cashAvailableForWithdrawal: float
    cashCall: float
    longNonMarginableMarketValue: float
    totalCash: float
    cashDebitCallValue: float
    unsettledCash: float


class CashProjectedBalance(BaseModel):
    cashAvailableForTrading: float
    cashAvailableForWithdrawal: float


class BaseAccount(BaseModel):
    type: AccountType
    accountNumber: str
    roundTrips: int
    isDayTrader: bool = False
    isClosingOnlyRestricted: bool = False
    pfcbFlag: bool = False
    positions: Optional[List[Position]] = None


class MarginAccount(BaseAccount):
    initialBalances: MarginInitialBalance
    currentBalances: MarginBalance
    projectedBalances: MarginProjectedBalance


class CashAccount(BaseAccount):
    initialBalances: CashInitialBalance
    currentBalances: CashBalance
    projectedBalances: CashProjectedBalance


SecuritiesAccount = Union[CashAccount, MarginAccount]


class Account(BaseModel):
    securitiesAccount: SecuritiesAccount


class AccountsResponse(RootModel):
    root: List[Account]

    def __getitem__(self, item):
        return self.root[item]

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)
