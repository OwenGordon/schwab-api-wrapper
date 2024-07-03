from pydantic import BaseModel
from typing import List, Optional, Union


class Error(BaseModel):
    id: str  # unique error id
    status: int  # The HTTP status code
    title: str  # Short error description
    detail: Optional[str] = None  # Detailed error description


class AccountsAndTradingError(BaseModel):
    message: Optional[str] = None
    errors: Optional[Union[List[Error], List[str]]] = None
