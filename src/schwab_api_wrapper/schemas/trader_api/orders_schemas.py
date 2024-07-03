from pydantic import BaseModel, RootModel
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

from .accounts_schemas import AccountsInstrument


class Session(Enum):
    NORMAL = "NORMAL"
    AM = "AM"
    PM = "PM"
    SEAMLESS = "SEAMLESS"


class Duration(Enum):
    DAY = "DAY"
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"
    END_OF_WEEK = "END_OF_WEEK"
    END_OF_MONTH = "END_OF_MONTH"
    NEXT_END_OF_MONTH = "NEXT_END_OF_MONTH"
    UNKNOWN = "UNKNOWN"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"
    CABINET = "CABINET"
    NON_MARKETABLE = "NON_MARKETABLE"
    MARKET_ON_CLOSE = "MARKET_ON_CLOSE"
    EXERCISE = "EXERCISE"
    TRAILING_STOP_LIMIT = "TRAILING_STOP_LIMIT"
    NET_DEBIT = "NET_DEBIT"
    NET_CREDIT = "NET_CREDIT"
    NET_ZERO = "NET_ZERO"
    LIMIT_ON_CLOSE = "LIMIT_ON_CLOSE"
    UNKNOWN = "UNKNOWN"


class ComplexOrderStrategyType(Enum):
    NONE = "NONE"
    COVERED = "COVERED"
    VERTICAL = "VERTICAL"
    BACK_RATIO = "BACK_RATIO"
    CALENDAR = "CALENDAR"
    DIAGONAL = "DIAGONAL"
    STRADDLE = "STRADDLE"
    STRANGLE = "STRANGLE"
    COLLAR_SYNTHETIC = "COLLAR_SYNTHETIC"
    BUTTERFLY = "BUTTERFLY"
    CONDOR = "CONDOR"
    IRON_CONDOR = "IRON_CONDOR"
    VERTICAL_ROLL = "VERTICAL_ROLL"
    COLLAR_WITH_STOCK = "COLLAR_WITH_STOCK"
    DOUBLE_DIAGONAL = "DOUBLE_DIAGONAL"
    UNBALANCED_BUTTERFLY = "UNBALANCED_BUTTERFLY"
    UNBALANCED_CONDOR = "UNBALANCED_CONDOR"
    UNBALANCED_IRON_CONDOR = "UNBALANCED_IRON_CONDOR"
    UNBALANCED_VERTICAL_ROLL = "UNBALANCED_VERTICAL_ROLL"
    MUTUAL_FUND_SWAP = "MUTUAL_FUND_SWAP"
    CUSTOM = "CUSTOM"


class RequestedDestination(Enum):
    INET = "INET"
    ECN_ARCA = "ECN_ARCA"
    CBOE = "CBOE"
    AMEX = "AMEX"
    PHLX = "PHLX"
    ISE = "ISE"
    BOX = "BOX"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    BATS = "BATS"
    C2 = "C2"
    AUTO = "AUTO"


class StopPriceLinkBasis(Enum):
    MANUAL = "MANUAL"
    BASE = "BASE"
    TRIGGER = "TRIGGER"
    LAST = "LAST"
    BID = "BID"
    ASK = "ASK"
    ASK_BID = "ASK_BID"
    MARK = "MARK"
    AVERAGE = "AVERAGE"


class StopPriceLinkType(Enum):
    VALUE = "VALUE"
    PERCENT = "PERCENT"
    TICK = "TICK"


class StopType(Enum):
    STANDARD = "STANDARD"
    BID = "BID"
    ASK = "ASK"
    LAST = "LAST"
    MARK = "MARK"


class PriceLinkBasis(Enum):
    MANUAL = "MANUAL"
    BASE = "BASE"
    TRIGGER = "TRIGGER"
    LAST = "LAST"
    BID = "BID"
    ASK = "ASK"
    ASK_BID = "ASK_BID"
    MARK = "MARK"
    AVERAGE = "AVERAGE"


class PriceLinkType(Enum):
    VALUE = "VALUE"
    PERCENT = "PERCENT"
    TICK = "TICK"


class TaxLotMethod(Enum):
    FIFO = "FIFO"
    LIFO = "LIFO"
    HIGH_COST = "HIGH_COST"
    LOW_COST = "LOW_COST"
    AVERAGE_COST = "AVERAGE_COST"
    SPECIFIC_LOT = "SPECIFIC_LOT"
    LOSS_HARVESTER = "LOSS_HARVESTER"


class OrderLegType(Enum):
    EQUITY = "EQUITY"
    OPTION = "OPTION"
    INDEX = "INDEX"
    MUTUAL_FUND = "MUTUAL_FUND"
    CASH_EQUIVALENT = "CASH_EQUIVALENT"
    FIXED_INCOME = "FIXED_INCOME"
    CURRENCY = "CURRENCY"
    COLLECTIVE_INVESTMENT = "COLLECTIVE_INVESTMENT"


class Instruction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_TO_COVER = "BUY_TO_COVER"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_OPEN = "BUY_TO_OPEN"
    BUY_TO_CLOSE = "BUY_TO_CLOSE"
    SELL_TO_OPEN = "SELL_TO_OPEN"
    SELL_TO_CLOSE = "SELL_TO_CLOSE"
    EXCHANGE = "EXCHANGE"
    SELL_SHORT_EXEMPT = "SHORT_SELL_EXEMPT"


class PositionEffect(Enum):
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    AUTOMATIC = "AUTOMATIC"


class QuantityType(Enum):
    ALL_SHARES = "ALL_SHARES"
    DOLLARS = "DOLLARS"
    SHARES = "SHARES"


class DivCapGains(Enum):
    REINVEST = "REINVEST"
    PAYOUT = "PAYOUT"


class OrderLegCollection(BaseModel):
    orderLegType: Optional[OrderLegType] = None
    legId: Optional[int] = None
    instrument: AccountsInstrument
    instruction: Instruction
    positionEffect: Optional[PositionEffect] = None
    quantity: float
    quantityType: Optional[QuantityType] = None
    divCapGains: Optional[DivCapGains] = None
    toSymbol: Optional[str] = None


class SpecialInstruction(Enum):
    ALL_OR_NONE = "ALL_OR_NONE"
    DO_NOT_REDUCE = "DO_NOT_REDUCE"
    ALL_OR_NONE_DO_NOT_REDUCE = "ALL_OR_NONE_DO_NOT_REDUCE"


class OrderStrategyType(Enum):
    SINGLE = "SINGLE"
    CANCEL = "CANCEL"
    RECALL = "RECALL"
    PAIR = "PAIR"
    FLATTEN = "FLATTEN"
    TWO_DAY_SWAP = "TWO_DAY_SWAP"
    BLAST_ALL = "BLAST_ALL"
    OCO = "OCO"
    TRIGGER = "TRIGGER"


class Status(Enum):
    AWAITING_PARENT_ORDER = "AWAITING_PARENT_ORDER"
    AWAITING_CONDITION = "AWAITING_CONDITION"
    AWAITING_STOP_CONDITION = "AWAITING_STOP_CONDITION"
    AWAITING_MANUAL_REVIEW = "AWAITING_MANUAL_REVIEW"
    ACCEPTED = "ACCEPTED"
    AWAITING_UR_OUT = "AWAITING_UR_OUT"
    PENDING_ACTIVATION = "PENDING_ACTIVATION"
    QUEUED = "QUEUED"
    WORKING = "WORKING"
    REJECTED = "REJECTED"
    PENDING_CANCEL = "PENDING_CANCEL"
    CANCELED = "CANCELED"
    PENDING_REPLACE = "PENDING_REPLACE"
    REPLACED = "REPLACED"
    FILLED = "FILLED"
    EXPIRED = "EXPIRED"
    NEW = "NEW"
    AWAITING_RELEASE_TIME = "AWAITING_RELEASE_TIME"
    PENDING_ACKNOWLEDGEMENT = "PENDING_ACKNOWLEDGEMENT"
    PENDING_RECALL = "PENDING_RECALL"
    UNKNOWN = "UNKNOWN"


class ActivityType(Enum):
    EXECUTION = "EXECUTION"
    ORDER_ACTION = "ORDER_ACTION"


class ExecutionType(Enum):
    FILL = "FILL"
    CANCELED = "CANCELED"


class ExecutionLeg(BaseModel):
    legId: int
    price: float
    quantity: float
    mismarkedQuantity: float
    instrumentId: int
    time: datetime


class OrderActivity(BaseModel):
    activityType: ActivityType
    executionType: ExecutionType
    quantity: float
    orderRemainingQuantity: float
    executionLegs: List[ExecutionLeg]


class Order(BaseModel):
    session: Session
    duration: Duration
    orderType: OrderType
    cancelTime: Optional[datetime] = None
    complexOrderStrategyType: ComplexOrderStrategyType
    quantity: float
    filledQuantity: float
    remainingQuantity: float
    requestedDestination: RequestedDestination
    destinationLinkName: str
    releaseTime: Optional[datetime] = None
    stopPrice: Optional[float] = None
    stopPriceLinkBasis: Optional[StopPriceLinkBasis] = None
    stopPriceLinkType: Optional[StopPriceLinkType] = None
    stopType: Optional[StopType] = None
    priceLinkBasis: Optional[PriceLinkBasis] = None
    priceLinkType: Optional[PriceLinkType] = None
    price: float
    taxLotMethod: Optional[TaxLotMethod] = None
    orderLegCollection: List[OrderLegCollection]
    activationPrice: Optional[float] = None
    specialInstruction: Optional[SpecialInstruction] = None
    orderStrategyType: OrderStrategyType
    orderId: int
    cancelable: bool = False
    editable: bool = False
    status: Status
    enteredTime: datetime
    closeTime: Optional[datetime] = None
    tag: Optional[str] = None
    accountNumber: int
    orderActivityCollection: Optional[List[OrderActivity]] = None
    replacingOrderCollection: Optional[None] = None
    childOrderStategies: Optional[None] = None
    statusDescription: Optional[str] = None


class OrderRequest(BaseModel):
    session: Session
    duration: Duration
    orderType: OrderType
    cancelTime: Optional[datetime] = None
    complexOrderStrategyType: Optional[ComplexOrderStrategyType] = None
    quantity: Optional[float] = None
    filledQuantity: Optional[float] = None
    remainingQuantity: Optional[float] = None
    destinationLinkName: Optional[str] = None
    releaseTime: Optional[datetime] = None
    stopPrice: Optional[float] = None
    stopPriceLinkBasis: Optional[StopPriceLinkBasis] = None
    stopPriceLinkType: Optional[StopPriceLinkType] = None
    stopPriceOffset: Optional[float] = None
    stopType: Optional[StopType] = None
    priceLinkBasis: Optional[PriceLinkBasis] = None
    priceLinkType: Optional[PriceLinkType] = None
    price: float  #
    taxLotMethod: Optional[TaxLotMethod] = None
    orderLegCollection: List[OrderLegCollection]  #
    activationPrice: Optional[float] = None
    specialInstruction: Optional[SpecialInstruction] = None
    orderStrategyType: OrderStrategyType  #
    orderId: Optional[int] = None
    cancelable: bool = False
    editable: bool = False
    status: Optional[Status] = None
    enteredTime: Optional[datetime] = None
    closeTime: Optional[datetime] = None
    accountNumber: Optional[int] = None
    orderActivityCollection: Optional[List[OrderActivity]] = None
    replacingOrderCollection: Optional[List[Dict]] = None  # TODO
    childOrderStategies: Optional[List[Dict]] = None  # TODO
    statusDescription: Optional[str] = None


class OrderResponse(RootModel):
    root: List[Order]

    def __getitem__(self, item):
        return self.root[item]

    def __iter__(self):
        return iter(self.root)

    def __len__(self):
        return len(self.root)


class PreviewOrder(BaseModel):
    pass
