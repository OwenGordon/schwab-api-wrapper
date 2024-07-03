import json
import redis
from cryptography.fernet import Fernet

from .utils import *
from .base_client import BaseClient
from schwab_api_wrapper.schemas.oauth import Token


class RedisClient(BaseClient):
    def __init__(
        self,
        redis_config_filepath: str,
        renew_refresh_token: bool = False,
        immediate_refresh: bool = True,
    ):
        super().__init__()

        self.redis_config_filepath = redis_config_filepath
        with open(self.redis_config_filepath, "r") as fin:
            self.redis_parameters = json.load(fin)

        self.encryption_key = self.get_encryption_key()

        self.cipher_suite = Fernet(self.encryption_key)

        self.redis = self.create_redis_client()

        self.parameters = self.load_parameters()
        self.set_parameter_instance_values(self.parameters)

        self.assert_refresh_token_not_expired(
            renew_refresh_token
        )  # check if refresh token is expired and exit if so

        if immediate_refresh:
            self.refresh()

    def create_redis_client(self) -> redis.Redis:
        return redis.Redis(
            host=self.redis_parameters[KEY_REDIS_HOST],
            port=self.redis_parameters[KEY_REDIS_PORT],
            password=self.redis_parameters[KEY_REDIS_PASSWORD],
        )

    def get_encryption_key(self) -> bytes:
        return self.redis_parameters[KEY_REDIS_ENCRYPTION_KEY].encode()

    def save_token(self, token: Token, refresh_token_reset: bool = False):
        self.update_parameters(token, refresh_token_reset)

        self.dump_parameters()

    def configurable_refresh(self):
        self.redis.close()
        self.redis = self.create_redis_client()

    def load_parameters(self, _: str | None = None) -> dict:
        encrypted_token = self.redis.get("token")
        return self.decrypt_token(encrypted_token)

    def dump_parameters(self, _: str | None = None) -> bool:
        encrypted_token = self.encrypt_token()
        return self.redis.set("token", encrypted_token)

    def encrypt_token(self) -> bytes:
        return self.cipher_suite.encrypt(json.dumps(self.parameters).encode())

    def decrypt_token(self, encrypted_token: bytes) -> dict:
        return json.loads(self.cipher_suite.decrypt(encrypted_token).decode())
