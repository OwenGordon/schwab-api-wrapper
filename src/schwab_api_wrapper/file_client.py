import json

from .base_client import BaseClient
from schwab_api_wrapper.schemas.oauth import Token


class FileClient(BaseClient):
    def __init__(
        self,
        parameters_file: str,
        renew_refresh_token: bool = False,
        immediate_refresh: bool = True,
    ):
        super().__init__()

        self.parameters_file = parameters_file

        self.parameters = self.load_parameters(self.parameters_file)

        self.set_parameter_instance_values(self.parameters)

        self.assert_refresh_token_not_expired(
            renew_refresh_token
        )  # check if refresh token is expired and exit if so

        if immediate_refresh:
            self.refresh()

    def save_token(self, token: Token, refresh_token_reset: bool = False):
        self.update_parameters(token, refresh_token_reset)
        self.dump_parameters(self.parameters_file)

    def load_parameters(self, filepath: str | None = None) -> dict:
        with open(filepath, "r") as fin:
            return json.load(fin)

    def dump_parameters(self, filepath: str | None = None):
        with open(filepath, "w") as fin:
            json.dump(self.parameters, fin, indent=4)

    def configurable_refresh(self):
        pass
