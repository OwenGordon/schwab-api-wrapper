from pydantic import BaseModel, RootModel, Field
from typing import List, Union, Literal, Optional
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    TRADE = "TRADE"
    RECEIVE_AND_DELIVER = "RECEIVE_AND_DELIVER"
    DIVIDEND_OR_INTEREST = "DIVIDEND_OR_INTEREST"
    ACH_RECEIPT = "ACH_RECEIPT"
    ACH_DISBURSEMENT = "ACH_DISBURSEMENT"
    CASH_RECEIPT = "CASH_RECEIPT"
    CASH_DISBURSEMENT = "CASH_DISBURSEMENT"
    ELECTRONIC_FUND = "ELECTRONIC_FUND"
    WIRE_OUT = "WIRE_OUT"
    WIRE_IN = "WIRE_IN"
    JOURNAL = "JOURNAL"
    MEMORANDUM = "MEMORANDUM"
    MARGIN_CALL = "MARGIN_CALL"
    MONEY_MARKET = "MONEY_MARKET"
    SMA_ADJUSTMENT = "SMA_ADJUSTMENT"


class TransactionStatus(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"


class SubAccount(Enum):
    CASH = "CASH"
    MARGIN = "MARGIN"
    SHORT = "SHORT"
    DIV = "DIV"
    INCOME = "INCOME"
    UNKNOWN = "UNKNOWN"


class ActivityType(Enum):
    ACTIVITY_CORRECTION = "ACTIVITY_CORRECTION"
    EXECUTION = "EXECUTION"
    ORDER_ACTION = "ORDER_ACTION"
    TRANSFER = "TRANSFER"
    UNKNOWN = "UNKNOWN"


class UserDetailsType(Enum):
    ADVISOR_USER = "ADVISOR_USER"
    BROKER_USER = "BROKER_USER"
    CLIENT_USER = "CLIENT_USER"
    SYSTEM_USER = "SYSTEM_USER"
    UNKNOWN = "UNKNOWN"


class UserDetails(BaseModel):
    cdDomainId: str
    login: str
    type: UserDetailsType
    userId: int
    systemUserName: str
    firstName: str
    lastName: str
    brokerRepCode: str


class AssetType(Enum):
    EQUITY = "EQUITY"
    OPTION = "OPTION"
    INDEX = "INDEX"
    MUTUAL_FUND = "MUTUAL_FUND"
    CASH_EQUIVALENT = "CASH_EQUIVALENT"
    FIXED_INCOME = "FIXED_INCOME"
    CURRENCY = "CURRENCY"
    COLLECTIVE_INVESTMENT = "COLLECTIVE_INVESTMENT"


class CashEquivalentType(Enum):
    SWEEP_VEHICLE = "SWEEP_VEHICLE"
    SAVINGS = "SAVINGS"
    MONEY_MARKET_FUND = "MONEY_MARKET_FUND"
    UNKNOWN = "UNKNOWN"


class TransactionCashEquivalent(BaseModel):
    assetType: Literal[AssetType.CASH_EQUIVALENT]
    cusip: str
    symbol: str
    description: str
    instrumentId: int
    netChange: float
    type: CashEquivalentType


class CollectiveInvestment(BaseModel):
    pass


class Currency(BaseModel):
    assetType: Literal[AssetType.CURRENCY]
    status: str
    cusip: Optional[str] = None
    symbol: str
    description: str
    instrumentid: int
    netChange: Optional[float]
    closingPrice: float


class EquityType(Enum):
    COMMON_STOCK = "COMMON_STOCK"
    PREFERRED_STOCK = "PREFERRED_STOCK"
    DEPOSITORY_RECEIPT = "DEPOSITORY_RECEIPT"
    PREFERRED_DEPOSITORY_RECEIPT = "PREFERRED_DEPOSITORY_RECEIPT"
    RESTRICTED_STOCK = "RESTRICTED_STOCK"
    COMPONENT_UNIT = "COMPONENT_UNIT"
    RIGHT = "RIGHT"
    WARRANT = "WARRANT"
    CONVERTIBLE_PREFERRED_STOCK = "CONVERTIBLE_PREFERRED_STOCK"
    CONVERTIBLE_STOCK = "CONVERTIBLE_STOCK"
    LIMITED_PARTNERSHIP = "LIMITED_PARTNERSHIP"
    WHEN_ISSUED = "WHEN_ISSUED"
    UNKNOWN = "UNKNOWN"


class TransactionEquity(BaseModel):
    assetType: Literal[AssetType.EQUITY]
    status: str
    cusip: str
    symbol: str
    description: Optional[str] = None
    instrumentId: int
    netChange: Optional[float] = None
    closingPrice: float
    type: EquityType


class TransactionFixedIncome(BaseModel):
    pass


class Forex(BaseModel):
    pass


class Future(BaseModel):
    pass


class Index(BaseModel):
    pass


class TransactionMutualFund(BaseModel):
    pass


class TransactionOption(BaseModel):
    pass


class Product(BaseModel):
    pass


TransactionInstrument = Union[
    TransactionCashEquivalent,
    CollectiveInvestment,
    Currency,
    TransactionEquity,
    TransactionFixedIncome,
    Forex,
    Future,
    Index,
    TransactionMutualFund,
    TransactionOption,
    Product,
]


class FeeType(Enum):
    COMMISSION = "COMMISSION"
    SEC_FEE = "SEC_FEE"
    STR_FEE = "STR_FEE"
    R_FEE = "R_FEE"
    CDSC_FEE = "CDSC_FEE"
    OPT_REG_FEE = "OPT_REG_FEE"
    ADDITIONAL_FEE = "ADDITIONAL_FEE"
    MISCELLANEOUS_FEE = "MISCELLANEOUS_FEE"
    FUTURES_EXCHANGE_FEE = "FUTURES_EXCHANGE_FEE"
    LOW_PROCEEDS_COMMISSION = "LOW_PROCEEDS_COMMISSION"
    BASE_CHARGE = "BASE_CHARGE"
    GENERAL_CHARGE = "GENERAL_CHARGE"
    GST_FEE = "GST_FEE"
    TAF_FEE = "TAF_FEE"
    INDEX_OPTION_FEE = "INDEX_OPTION_FEE"
    UNKNOWN = "UNKNOWN"


class PositionEffect(Enum):
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    AUTOMATIC = "AUTOMATIC"
    UNKNOWN = "UNKNOWN"


class TransferItem(BaseModel):
    instrument: TransactionInstrument
    amount: float
    cost: float
    price: Optional[float] = None
    feeType: Optional[FeeType] = None
    positionEffect: Optional[PositionEffect] = None


class Transaction(BaseModel):
    activityId: int
    time: datetime
    user: Optional[UserDetails] = None
    description: Optional[str] = None
    accountNumber: str
    type: TransactionType
    status: TransactionStatus
    subAccount: SubAccount
    tradeDate: datetime
    settlementDate: Optional[datetime] = None
    positionId: Optional[int] = None
    orderId: Optional[int] = None
    netAmount: float
    activityType: Optional[ActivityType] = None
    transferItems: List[TransferItem]


class TransactionResponse(RootModel):
    root: List[Transaction]

    def __getitem__(self, item):
        return self.root[item]

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)
