from schwab_api_wrapper.schemas.oauth import OAuthError


class OAuthException(Exception):
    def __init__(self, title, error: OAuthError, parameters: dict):
        super().__init__(title)
        self.title = title
        self.error = error
        self.parameters = parameters
