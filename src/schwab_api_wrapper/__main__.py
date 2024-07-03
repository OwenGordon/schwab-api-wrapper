import json
import click
import redis
from cryptography.fernet import Fernet

from schwab_api_wrapper import FileClient, RedisClient
from schwab_api_wrapper.utils import (
    KEY_REDIS_HOST,
    KEY_REDIS_PORT,
    KEY_REDIS_PASSWORD,
    KEY_REDIS_ENCRYPTION_KEY,
)


MODES = ["restart-oauth", "new-oauth", "prime-redis-cache", "generate-encryption-key"]


class ModeOptions(click.Choice):
    def __init__(self):
        super().__init__(choices=MODES)


class ClientTypeOptions(click.Choice):
    def __init__(self):
        super().__init__(choices=["file", "redis"])


def validate_client(ctx, param, value):
    mode = ctx.params.get("mode")
    if mode in ["restart-oauth"] and not value:
        raise click.BadParameter(
            "Client type must be specified when using restart-oauth mode."
        )
    if mode == "prime-redis-cache":
        return "redis"  # Automatically use Redis for prime-redis-cache
    return value


@click.command()
@click.argument("mode", type=ModeOptions())
@click.option("-p", "--parameters", type=click.Path(exists=True), required=False)
@click.option(
    "-c",
    "--client",
    type=ClientTypeOptions(),
    callback=validate_client,
    help="Choose the client type: file or redis (required for restart-oauth or new-oauth)",
)
@click.option(
    "-t",
    "--token",
    type=click.Path(exists=True),
    help="The token to use for the operation",
    required=False,
)
def main(mode, parameters, client, token):
    """A command line tool for managing Schwab API interactions."""

    if parameters:
        click.echo(f"Parameters file path: {parameters}")

    if mode == "prime-redis-cache" and not token:
        raise click.BadParameter(
            "Token file path must be specified when using prime-redis-cache mode."
        )

    api_client = None

    if mode == "restart-oauth":
        # Instantiate the appropriate client based on the command line option
        api_client = (
            FileClient(parameters, renew_refresh_token=True, immediate_refresh=False)
            if client == "file"
            else RedisClient(
                parameters, renew_refresh_token=True, immediate_refresh=False
            )
        )

        click.echo(f"Using {client} client.")

    if mode == "restart-oauth":
        click.echo("Restarting OAuth2 and renewing refresh token.")

        api_client.renew_refresh_token()
        print(f"API OAuth Refresh Token has been renewed and written to {parameters}")
    elif mode == "new-oauth":
        click.echo("Generating new parameters JSON.")

        empty_parameters = {
            "client_id": "App Key here",
            "client_secret": "Secret here",
            "redirect_uri": "Callback URL here",
            "expires_in": 0,
            "token_type": "",
            "scope": "",
            "refresh_token": "",
            "access_token": "",
            "id_token": "",
            "access_token_valid_until": "1970-01-01T00:00:00+00:00",
            "refresh_token_valid_until": "1970-01-01T00:00:00+00:00",
        }

        with open(parameters, "w") as fin:
            json.dump(empty_parameters, fin, indent=4)

        print(f"New parameters json file created at {parameters}")

    elif mode == "prime-redis-cache":
        click.echo("Priming the Redis cache.")

        with open(parameters, "r") as fin:
            redis_parameters = json.load(fin)

        r = redis.Redis(
            host=redis_parameters[KEY_REDIS_HOST],
            port=redis_parameters[KEY_REDIS_PORT],
            password=redis_parameters[KEY_REDIS_PASSWORD],
        )

        encryption_key = redis_parameters[KEY_REDIS_ENCRYPTION_KEY].encode()

        with open(token, "r") as fin:
            token = json.load(fin)

        cipher_suite = Fernet(encryption_key)
        encrypted_token = cipher_suite.encrypt(json.dumps(token).encode())

        r.set("token", encrypted_token)

        print("Redis cache primed with token data.")

    elif mode == "generate-encryption-key":
        click.echo("Generating encryption key.")

        key = Fernet.generate_key()

        print(f"Encryption key: {key.decode()}")


if __name__ == "__main__":
    main()
