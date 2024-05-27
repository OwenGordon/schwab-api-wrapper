from __future__ import annotations
import json
import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta, timezone, date
from typing import Optional, Union, List
from collections.abc import Iterable
import logging
from devtools import pprint, pformat
from urllib.parse import quote

from .response_aware_retry import ResponseAwareRetry
from .utils import *

from .market_data.quotes_schemas import QuoteResponse
from .market_data.market_hours_schemas import MarketHoursResponse
from .market_data.price_history_schemas import CandleList
from .market_data.errors_schema import MarketDataError

from .trader_api.accounts_schemas import (
    AccountNumbersResponse,
    AccountsResponse,
    Account,
)
from .trader_api.transactions_schemas import (
    TransactionResponse,
    Transaction,
    TransactionType,
)
from .trader_api.orders_schemas import Order, OrderRequest, PreviewOrder, OrderResponse
from .trader_api.errors_schema import AccountsAndTradingError

from .oauth_schemas import Token, OAuthError


class OAuthException(Exception):
    def __init__(self, title, error: OAuthError):
        super().__init__(title)
        self.title = title
        self.error = error



# TODO if the response doesn't have a .json() field it will error at us
# I think we just let it fail in this case because pydantic verification will fail anyways too
# Either this or we specifically check for a missing json field in an otherwise well-formed response


class SchwabAPI:
    def __init__(
        self,
        parameters_file: str,
        renew_refresh_token: bool = False,
        immediate_refresh: bool = True,
    ):
        self.parameters_file = parameters_file
        with open(self.parameters_file, "r") as fin:
            self.parameters = json.load(fin)

        self.client_id = self.parameters[
            KEY_CLIENT_ID
        ]  # client id is "app key" on the dev site
        self.client_secret = self.parameters[
            KEY_CLIENT_SECRET
        ]  # client secret is the "app secret" on dev site
        self.redirect_uri = self.parameters[
            KEY_URI_REDIRECT
        ]  # "callback url" on dev site
        self.refresh_token = self.parameters[KEY_TOKEN_REFRESH]
        self.access_token = self.parameters[KEY_TOKEN_ACCESS]
        self.id_token = self.parameters[KEY_TOKEN_ID]
        self.refresh_token_valid_until = datetime.fromisoformat(
            self.parameters[KEY_REFRESH_TOKEN_VALID_UNTIL]
        )
        self.access_token_valid_until = datetime.fromisoformat(
            self.parameters[KEY_ACCESS_TOKEN_VALID_UNTIL]
        )

        if (
            not renew_refresh_token
            and datetime.now(timezone.utc) >= self.refresh_token_valid_until
        ):
            logging.getLogger(__name__).fatal(
                "The API OAuth Refresh token has expired. Please renew this token by running `python3 -m schwab_api_wrapper [parameters.json]`"
            )
            print(
                "The API OAuth Refresh token has expired. Please renew this token by running `python3 -m schwab_api_wrapper [parameters.json]`"
            )
            exit(1)

        self.retry_strategy = ResponseAwareRetry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 501, 502, 503],
            allowed_methods=["GET"],
        )

        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)

        self.retry_session = requests.Session()
        self.retry_session.mount("http://", self.adapter)
        self.retry_session.mount("https://", self.adapter)

        self.session = requests.Session()

        if immediate_refresh:
            self.refresh()

    def __get(
        self,
        url: str,
        params: Optional[dict] = None,
        retry: bool = False,
        headers: Optional[dict] = None,
    ) -> Response:
        if retry:
            try:
                response = self.retry_session.get(url, params=params, headers=headers)
            except requests.exceptions.RetryError as e:
                response = e.args[0].response
                logging.getLogger(__name__).warning(
                    "Maximum number of retries reached."
                )
        else:
            response = self.session.get(url, params=params, headers=headers)

        return response

    @property
    def need_refresh(self) -> bool:
        return datetime.now(timezone.utc) >= self.access_token_valid_until

    @property
    def headers(self):
        """
        Return's headers containing access token authorization. If access token is invalid, token will be refreshed here
        """
        if self.need_refresh:
            self.refresh()

        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
    
    def get_refresh_token_expiration(self) -> datetime:
        return self.refresh_token_valid_until

    def refresh(self):
        token, error = self.refresh_access_token()

        if error is not None:
            raise OAuthException(f"Unable to generate refresh token", error)
        
        self.save_token(token)

        self.retry_session = requests.Session()
        self.retry_session.mount("http://", self.adapter)
        self.retry_session.mount("https://", self.adapter)

        self.session = requests.Session()

    def app_authorization(self) -> str:
        # request template:
        # https://api.schwabapi.com/v1/oauth/authorize?client_id={CONSUMER _KEY}&redirect_uri={APP_CALLBACK_URL}

        # response template: final landing url
        # https://{APP_CALLBACK_URL}/?code={AUTHORIZATION_CODE_GENERATED}&session={SESSION_ID}

        params = {KEY_CLIENT_ID: self.client_id, KEY_URI_REDIRECT: self.redirect_uri}

        logging.getLogger(__name__).debug(
            "App Authorization Params:\n" + pformat(params)
        )

        response = self.__get(AUTH_URL, params=params)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{AUTH_URL}` | Status: {response.status_code}"
        )

        assert (
            response.status_code == STATUS_CODE_FORBIDDEN
        ), "Failed to obtain authorization URL [error code = %s]" % (
            response.status_code
        )

        logging.getLogger(__name__).debug(
            f"OAuth Authorize Response url: {response.url}"
        )

        return response.url

    def generate_refresh_token(self, authorization_code) -> tuple[Optional[Token], Optional[OAuthError]]:
        # Access Token" - Request Example (CURL)
        # {curl -X POST \https://api.schwabapi.com/v1/oauth/token \-H 'Authorization: Basic {BASE64_ENCODED_Client_ID:Client_Secret} \-H 'Content-Type: application/x-www-form-urlencoded' \-d 'grant_type=authorization_code&code={AUTHORIZATION_CODE_VALUE}&redirect_uri=https://example_url.com/callback_example'}
        # Response Example (body)
        # Example - Access Token Response
        # {  "expires_in": 1800,  //Number of seconds access_token is valid for  "token_type": "Bearer",  "scope": "api",  "refresh_token": "{REFRESH_TOKEN_HERE}", //Valid for 7 days  "access_token": "{ACCESS_TOKEN_HERE}", //Valid for 30 minutes  "id_token": "{JWT_HERE}"}

        payload = {
            KEY_GRANT_TYPE: VALUE_CODE_AUTHORIZATION,
            KEY_CODE: authorization_code,
            KEY_URI_REDIRECT: self.redirect_uri,
        }

        logging.getLogger(__name__).debug(
            "Generate Refresh Token Payload:\n" + pformat(payload)
        )

        return self.__get_token(payload)

    def __get_token(self, payload) -> tuple[Optional[Token], Optional[OAuthError]]:
        response = requests.post(
            TOKEN_URL,
            auth=HTTPBasicAuth(username=self.client_id, password=self.client_secret),
            data=payload,
        )

        logging.getLogger(__name__).info(
            f"Schwab API | POST `{TOKEN_URL}` | Status: {response.status_code}"
        )

        if response.status_code == STATUS_CODE_OK:
            token = Token(**response.json())
            logging.getLogger(__name__).debug("Response JSON:\n" + pformat(token))

            return token, None
        else:
            error = OAuthError(**response.json())
            logging.getLogger(__name__).debug("Response JSON:\n" + pformat(error))

            return None, error

    def renew_refresh_token(self):

        authorization_url = self.app_authorization()

        print()
        print("Authorization URL:")
        print(authorization_url)
        print()
        print("1. Use the above URL to authenticate and authorize via browser")
        print("2. Copy the resulting redirected URL from the browser address bar")
        print()

        url = input("Enter resulting redirected URL here: ")

        authorization_code, session_id = get_code_from_url(url)

        token, error = self.generate_refresh_token(authorization_code)

        if error is not None:
            raise OAuthException(f"Unable to generate refresh token", error)
        
        self.save_token(token)

    def save_token(self, token: Token):
        self.refresh_token = token.refresh_token # valid for 7 days
        self.refresh_token_valid_until = datetime.now(timezone.utc) + timedelta(
            days=7
        )  # utc time refresh token is valid until
        self.access_token = token.access_token  # valid for 30 minutes
        self.access_token_valid_until = datetime.now(timezone.utc) + timedelta(
            seconds=1800
        )  # utc time when access token is invalid
        self.id_token = token.id_token

        self.parameters[KEY_ACCESS_TOKEN_VALID_UNTIL] = (
            self.access_token_valid_until.isoformat()
        )
        self.parameters[KEY_REFRESH_TOKEN_VALID_UNTIL] = (
            self.refresh_token_valid_until.isoformat()
        )

        self.parameters.update(token.model_dump())

        with open(self.parameters_file, "w") as fin:
            json.dump(self.parameters, fin, indent=4)

    def refresh_access_token(self) -> tuple[Optional[Token], Optional[OAuthError]]:
        # "Refresh Token" - Request Example (cURL)
        # curl -X POST \
        #     https://api.schwabapi.com/v1/oauth/token \
        #     -H 'Authorization: Basic {BASE64_ENCODED_Client_ID:Client_Secret} \
        #     -H 'Content-Type: application/x-www-form-urlencoded' \
        #     -d 'grant_type=refresh_token&refresh_token={REFRESH_TOKEN_GENERATED_FROM_PRIOR_STEP}
        # Response Example (body)
        # Example - Refresh Token Response
        # {  "expires_in": 1800,  //Number of seconds access_token is valid for  "token_type": "Bearer",  "scope": "api",  "refresh_token": "{REFRESH_TOKEN_HERE}", //Valid for 7 days  "access_token":  "{NEW_ACCESS_TOKEN_HERE}",//Valid for 30 minutes  "id_token": "{JWT_HERE}"}

        payload = {
            KEY_GRANT_TYPE: KEY_TOKEN_REFRESH,
            KEY_TOKEN_REFRESH: self.refresh_token,
        }

        logging.getLogger(__name__).debug(
            "Refresh Access Token Payload:\n" + pformat(payload)
        )

        return self.__get_token(payload)

    def quotes(
        self,
        symbols: list[str],
        quotes_fields: Optional[list[QuotesField]] = None,
        indicative: bool = False,
        retry: bool = False,
    ) -> tuple[Optional[QuoteResponse], Optional[MarketDataError]]:
        """
        Get Quote by list of symbols

        Parameters:
            symbols: list of symbols to look up quote
            quotes_fields: request for subset of data by passing list of root nodes, possible root nodes are quote, fundamental, extended, regular, reference. don't send this attribute for full response.
            indicative: include indicative symbol quotes for all ETF symbols in request
        """
        if quotes_fields is None:
            quotes_fields = []

        params = {
            "symbols": ",".join(symbols),
            "fields": ",".join([field.value for field in quotes_fields]),
            "indicative": str(indicative).lower(),
        }

        logging.getLogger(__name__).debug("Quotes Params:\n" + pformat(params))

        response = self.__get(
            QUOTES_URL, params=params, headers=self.headers, retry=retry
        )

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{QUOTES_URL}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return QuoteResponse(**response.json()), None
        else:
            return None, MarketDataError(**response.json())

    def market_hours(
        self,
        markets: list[MarketID],
        query_date: Optional[date] = None,
        retry: bool = False,
    ) -> tuple[Optional[MarketHoursResponse], Optional[MarketDataError]]:
        """
        Get market hours for dates in the future across different markets

        Parameters:
            markets: list of markets, available values: equity, option, bond, future, forex
            date: valid date range is from currentdate to 1 year from today. It will default to current day if not entered.
        """

        date_format = "%Y-%m-%d"

        if query_date is None:
            query_date = datetime.now(timezone.utc).date()

        today = datetime.now(timezone.utc).date()
        range_beginning = today
        range_ending = today + timedelta(days=365)

        assert (
            range_beginning <= query_date <= range_ending
        ), f"Query date ({query_date.strftime(date_format)}) outside range [today ({range_beginning.strftime(date_format)}), today + 1 year ({range_ending.strftime(date_format)})]"

        params = {
            "markets": [market_id.value for market_id in markets],
            "date": query_date.strftime(date_format),
        }

        logging.getLogger(__name__).debug("Market Hours Params:\n" + pformat(params))

        response = self.__get(
            MARKET_HOURS_URL, params=params, headers=self.headers, retry=retry
        )

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{MARKET_HOURS_URL}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return MarketHoursResponse(**response.json()), None
        else:
            return None, MarketDataError(**response.json())

    def single_market_hours(
        self,
        market_id: MarketID,
        query_date: Optional[date] = None,
        retry: bool = False,
    ) -> tuple[Optional[MarketHoursResponse], Optional[MarketDataError]]:
        """
        Get Market Hours for dates in the future for a single market

        Parameters:
            market_id: market id, equity, option, bond, future, forex
            date: valid date range is from currentdate to 1 year from today. It will default to current day if not enetered
        """

        date_format = "%Y-%m-%d"

        if query_date is None:
            query_date = datetime.now(timezone.utc).date()

        today = datetime.now(timezone.utc).date()
        range_beginning = today
        range_ending = today + timedelta(days=365)

        assert (
            range_beginning <= query_date <= range_ending
        ), f"Query date ({query_date.strftime(date_format)}) outside range [today ({range_beginning.strftime(date_format)}), today + 1 year ({range_ending.strftime(date_format)})]"

        single_market_hours_url = f"{MARKET_HOURS_URL}/{market_id.value}"

        params = {"date": query_date.strftime(date_format)}

        logging.getLogger(__name__).debug(
            "Single Market Hours Params:\n" + pformat(params)
        )

        response = self.__get(
            single_market_hours_url, params=params, headers=self.headers, retry=retry
        )

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{single_market_hours_url}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return MarketHoursResponse(**response.json()), None
        else:
            return None, MarketDataError(**response.json())

    def price_history(
        self,
        symbol: str,
        period_frequency_params: PeriodFrequencyParameters,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        need_extended_hours_data: bool = False,
        need_previous_close: bool = False,
        retry: bool = False,
    ) -> tuple[Optional[CandleList], Optional[MarketDataError]]:
        """
        Get PriceHistory for a single symbol and date ranges

        Get historical Open, High, Low, Close, and Volume for a given frequency (i.e. aggregation).
        Frequency available is dependent on periodType selected.
        The datetime format sent in the get request is in EPOCH milliseconds.

        Parameters:
            symbol: The Equity symbol used to look up price history
            period_type: The chart period being requested. Available values: day, month, year, ytd
            period: The number of chart period types
            frequency_type: The time frequency_type
            frequency: the time frequency duration
            start_date: the start date. If not specified start_date will be (end_date - period) excluding weekends and holidays
            end_date: the end date. If not specified, the end_date will default to the market close of previous business day
            need_extended_hours_data: Need extended hours data
            need_previous_close: Need previous close price/date
        """

        # build params
        params: dict[str, int | str] = {"symbol": symbol}
        params.update(**period_frequency_params.get_params())

        if start_date:
            params["startDate"] = int(start_date.timestamp() * 1000)

        if end_date:
            params["endDate"] = int(end_date.timestamp() * 1000)

        params["needExtendedHoursData"] = need_extended_hours_data
        params["needPreviousClose"] = need_previous_close

        logging.getLogger(__name__).debug("Price History Params:\n" + pformat(params))

        response = self.__get(
            PRICE_HISTORY_URL, params=params, headers=self.headers, retry=retry
        )

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{PRICE_HISTORY_URL}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return CandleList(**response.json()), None
        else:
            return None, MarketDataError(**response.json())

    def account_numbers(
        self, retry: bool = False
    ) -> tuple[Optional[AccountNumbersResponse], Optional[AccountsAndTradingError]]:
        """
        Get list of account numbers and their encrypted values

        Account numbers in plain text cannot be used outside of headers or request/response bodies.
        As the first step consumers must invoke this service to retrieve the list of plain text/encrypted value pairs,
        and use encrypted account values for all subsequent calls for any accountNumber request.
        """

        response = self.__get(ACCOUNT_NUMBERS_URL, headers=self.headers, retry=retry)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{ACCOUNT_NUMBERS_URL}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return AccountNumbersResponse(
                response.json()
            ), None  # response.json() is a list if 200 OK so don't destructure
        else:
            return None, AccountsAndTradingError(**response.json())

    def accounts(
        self, account_field: Optional[AccountsField] = None, retry: bool = False
    ) -> tuple[Optional[AccountsResponse], Optional[AccountsAndTradingError]]:
        """
        Get linked account(s) balances and positions for the logged in user

        All the linked account information for the user logged in.
        The balances on these accounts are displaed by default
        however the positions on these accounts will be displayed based on the "positions" flag

        Parameters:
            fields: this allows one to determine which fields they want returned
        """

        params = {"fields": account_field.value if account_field else ""}

        logging.getLogger(__name__).debug("Accounts Params:\n" + pformat(params))

        response = self.__get(
            ACCOUNTS_URL, params=params, headers=self.headers, retry=retry
        )

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{ACCOUNTS_URL}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return AccountsResponse(
                response.json()  # json is a list not a dict
            ), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def single_account(
        self,
        encrypted_account_number: str,
        account_field: Optional[AccountsField] = None,
        retry: bool = False,
    ) -> tuple[Optional[Account], Optional[AccountsAndTradingError]]:
        """
        Get linked account(s) balances and positions for the logged in user

        All the linked account information for the user logged in.
        The balances on these accounts are displaed by default
        however the positions on these accounts will be displayed based on the "positions" flag

        Parameters:
            encrypted_account_number: encrypted ID of the account
            fields: this allows one to determine which fields they want returned
        """

        account_url = f"{ACCOUNTS_URL}/{encrypted_account_number}"

        params = {"fields": account_field.value if account_field else ""}

        logging.getLogger(__name__).debug("Single Account Params:\n" + pformat(params))

        response = self.__get(
            account_url, params=params, headers=self.headers, retry=retry
        )

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{account_url}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return Account(**response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def get_all_orders(
        self,
        from_entered_time: datetime,
        to_entered_time: datetime,
        max_results: int = 3000,
        status: Optional[OrderStatus] = None,
    ) -> tuple[Optional[OrderResponse], Optional[AccountsAndTradingError]]:
        """
        Get all orders for all accounts

        from_entered_time: Specifies that no orders entered before this time should be returned. Date must be within 60 days from today's date
        to_entered_time: Specifies that no orders entered after this time should be returned
        status: Specifies that only orders of this status should be returned
        max_results: The max number of orders to retrieve. Default is 3000
        """

        if (
            from_entered_time.tzinfo is None
            or from_entered_time.tzinfo.utcoffset(from_entered_time) is None
        ):
            from_entered_time = from_entered_time.replace(tzinfo=timezone.utc)

        if (
            to_entered_time.tzinfo is None
            or to_entered_time.tzinfo.utcoffset(to_entered_time) is None
        ):
            to_entered_time = to_entered_time.replace(tzinfo=timezone.utc)

        params = {
            "fromEnteredTime": from_entered_time.isoformat(),
            "toEnteredTime": to_entered_time.isoformat(),
            "maxResults": max_results,
            "status": status.value if status else "",
        }

        logging.getLogger(__name__).debug("Get All Orders Params:\n" + pformat(params))

        response = self.__get(ORDERS_URL, params=params, headers=self.headers)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{ORDERS_URL}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return OrderResponse(response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def get_account_orders(
        self,
        encrypted_account_number: str,
        from_entered_time: datetime,
        to_entered_time: datetime,
        max_results: int = 3000,
        status: Optional[OrderStatus] = None,
    ) -> tuple[Optional[OrderResponse], Optional[AccountsAndTradingError]]:
        """
        Get all orders for all accounts

        encrypted_account_number: The exrypted ID of the account
        from_entered_time: Specifies that no orders entered before this time should be returned. Date must be within 60 days from today's date
        to_entered_time: Specifies that no orders entered after this time should be returned
        status: Specifies that only orders of this status should be returned
        max_results: The max number of orders to retrieve. Default is 3000
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/orders"

        if (
            from_entered_time.tzinfo is None
            or from_entered_time.tzinfo.utcoffset(from_entered_time) is None
        ):
            from_entered_time = from_entered_time.replace(tzinfo=timezone.utc)

        if (
            to_entered_time.tzinfo is None
            or to_entered_time.tzinfo.utcoffset(to_entered_time) is None
        ):
            to_entered_time = to_entered_time.replace(tzinfo=timezone.utc)

        params = {
            "fromEnteredTime": from_entered_time.isoformat(),
            "toEnteredTime": to_entered_time.isoformat(),
            "maxResults": max_results,
            "status": status.value if status else "",
        }

        logging.getLogger(__name__).debug("Get All Orders Params:\n" + pformat(params))

        response = self.__get(url, params=params, headers=self.headers)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{url}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return OrderResponse(response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def get_single_order(
        self, encrypted_account_number: str, order_id: int
    ) -> tuple[Optional[Order], Optional[AccountsAndTradingError]]:
        """
        Get all orders for all accounts

        encrypted_account_number: The exrypted ID of the account
        order_id: the ID of the order being retrieved
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/orders/{order_id}"

        response = self.__get(url, headers=self.headers)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{url}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return Order(**response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def place_order(
        self, encrypted_account_number: str, order_request: OrderRequest
    ) -> tuple[Optional[Order], Optional[AccountsAndTradingError]]:
        """
        Place order for a specific amount

        Parameters:
            encrypted_account_number: The encrypted ID of the account
            order_request: The new order object for request body
        """
        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/orders"

        logging.getLogger(__name__).debug(
            "Place Order Request\n"
            + pformat(order_request.model_dump(mode="json", exclude_none=True))
        )

        response = self.session.post(
            url,
            json=order_request.model_dump(mode="json", exclude_none=True),
            headers=self.headers,
        )

        logging.getLogger(__name__).info(
            f"Schwab API | POST `{url}` | Status: {response.status_code}"
        )

        if response.status_code == STATUS_CODE_CREATED:
            location = response.headers["Location"]
            order_id = location.split("/")[-1]
            order_details, error = self.get_single_order(encrypted_account_number, order_id)
            if order_details:
                return order_details, None
            else:
                order_error_json = {**error.model_dump(mode="json", exclude_none=True)}
                new_message = "Order placed successfully. GET order API call failed."
                if "message" in order_error_json:
                    new_message = f"{new_message} {order_error_json['message']}"
                return None, AccountsAndTradingError(**{**order_error_json, "message": new_message})
        else:
            return None, AccountsAndTradingError(**response.json())

    # TOOO the three methods left don't even work on scwhab, but i'll implement them anyways
    def cancel_order(
        self, encrypted_account_number: str, order_id: int
    ) -> tuple[None, Optional[AccountsAndTradingError]]:
        """
        Cancel a specific order for a specific account

        encrypted_account_number: The enrypted ID of the account
        order_id: the ID of the order being cancelled
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/orders/{order_id}"

        response = self.session.delete(url, headers=self.headers)

        logging.getLogger(__name__).info(
            f"Schwab API | DELETE `{url}` | Status: {response.status_code}"
        )

        if response.status_code == STATUS_CODE_OK:
            return None, None  # is there something else we can return here?
        else:
            logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))
            return None, AccountsAndTradingError(**response.json())


    def replace_order(
        self, encrypted_account_number: str, order_id: int, order_request: OrderRequest
    ) -> tuple[Optional[Order], Optional[AccountsAndTradingError]]:
        """
        Replace a specific order for a specific account

        encrypted_account_number: The enrypted ID of the account
        order_id: the ID of the order being retrieved
        order_request: The new order object for request body
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/orders/{order_id}"

        logging.getLogger(__name__).debug(
            "Replace Order Request\n"
            + pformat(order_request.model_dump(mode="json", exclude_none=True))
        )

        response = self.session.put(
            url,
            json=order_request.model_dump(mode="json", exclude_none=True),
            headers=self.headers,
        )

        logging.getLogger(__name__).info(
            f"Schwab API | PUT `{url}` | Status: {response.status_code}"
        )

        if response.status_code == STATUS_CODE_CREATED:
            location = response.headers["Location"]
            order_id = location.split("/")[-1]
            order_details, error = self.get_single_order(encrypted_account_number, order_id)
            if order_details:
                return order_details, None
            else:
                order_error_json = {**error.model_dump(mode="json", exclude_none=True)}
                new_message = "Order placed successfully. GET order API call failed."
                if "message" in order_error_json:
                    new_message = f"{new_message} {order_error_json['message']}"
                return None, AccountsAndTradingError(**{**order_error_json, "message": new_message})
        else:
            return None, AccountsAndTradingError(**response.json())

    def preview_order(
        self, encrypted_account_number: str, order_request: OrderRequest
    ) -> tuple[Optional[PreviewOrder], Optional[AccountsAndTradingError]]:
        """
        Preview an order for a specific amount

        Parameters:
            encrypted_account_number: The encrypted ID of the account
            order_request: The new order object for request body
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/previewOrder"

        logging.getLogger(__name__).debug(
            "Preview Order Request\n"
            + pformat(order_request.model_dump(mode="json", exclude_none=True))
        )

        response = self.session.post(
            url,
            json=order_request.model_dump(mode="json", exclude_none=True),
            headers=self.headers,
        )

        logging.getLogger(__name__).info(
            f"Schwab API | POST `{url}` | Status: {response.status_code}"
        )

        if response.status_code == STATUS_CODE_OK:
            return Order(**response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def get_transactions(
        self,
        encrypted_account_number: str,
        start_date: datetime,
        end_date: datetime,
        transaction_type: Union[TransactionType, Iterable[TransactionType]],
        symbol: Optional[str] = None,
    ) -> tuple[Optional[TransactionResponse], Optional[AccountsAndTradingError]]:
        """
        Get all transactions information for a specific account

        Parameters:
            encrypted_account_number: The encrypted ID of the account
            start_date: Specifies that no transactions entered before this time should be returned. Date must be within 60 days from today's date
            end_date: Specifies that no transactions entered after this time should be returned.
            symbol: filter all transactions based on the symbol
            types: Specifies that only transacitons of this status should be returned
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/transactions"

        if start_date.tzinfo is None or start_date.tzinfo.utcoffset(start_date) is None:
            start_date = start_date.replace(tzinfo=timezone.utc)

        if end_date.tzinfo is None or end_date.tzinfo.utcoffset(end_date) is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        params = {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "types": ",".join(
                map(
                    lambda t_type: t_type.value, 
                    transaction_type
                )
            ) if isinstance(transaction_type, Iterable) else transaction_type.value,
        }
        
        if symbol:
            params["symbol"] = quote(symbol)

        logging.getLogger(__name__).debug(
            "Get Transactions Params:\n" + pformat(params)
        )

        response = self.__get(url, params=params, headers=self.headers)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{url}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return TransactionResponse(response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())

    def get_single_transaction(
        self,
        encrypted_account_number: str,
        transaction_id: int,
    ) -> tuple[Optional[Transaction], Optional[AccountsAndTradingError]]:
        """
        Get specific transaction information for a specific account

        Parameters:
            encrypted_account_number: The encrypted ID of the account
            transaction_id: the id of the transaction being retrieved
        """

        url = f"{TRADER_API_ENDPOINT}/accounts/{encrypted_account_number}/transactions/{transaction_id}"

        response = self.__get(url, headers=self.headers)

        logging.getLogger(__name__).info(
            f"Schwab API | GET `{url}` | Status: {response.status_code}"
        )

        logging.getLogger(__name__).debug("Response JSON:\n" + pformat(response.json()))

        if response.status_code == STATUS_CODE_OK:
            return Transaction(**response.json()), None
        else:
            return None, AccountsAndTradingError(**response.json())
