from pydantic import BaseModel, root_validator
from typing import List, Optional, Union
from enum import Enum


class ErrorSource(BaseModel):
    """
    Who is responsible for triggering these errors
    """

    pointer: Optional[List[str]] = (
        None  # list of attributes which lead to this error message
    )
    parameter: Optional[str] = None  # parameters name which lead to this error message
    header: Optional[str] = None  # header name which lead to this error message


class Status(Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

    @classmethod
    def _missing_(cls, value):
        """
        This method is called when an attempt is made to construct the enum
        with a value that's not in the enum, allowing for custom behavior.
        """
        if isinstance(value, str) and value.isdigit():
            return cls(int(value))
        elif isinstance(value, int):
            return cls(value)
        return super()._missing_(value)


class Error(BaseModel):
    id: str  # unique error id
    status: Status  # The HTTP status code
    title: str  # Short error description
    detail: Optional[str] = None  # Detailed error description
    source: Optional[ErrorSource] = None


class MarketDataError(BaseModel):
    errors: List[Error]

    message: Optional[str] = None  # i added this field to alert for retry failures
