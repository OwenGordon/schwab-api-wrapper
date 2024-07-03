import logging
import re


class TokenCensorFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        id_token_pattern = r"id_token=\((.+?)\)"
        id_json_pattern = r"'id_token': \((.+?)\)"

        refresh_token_pattern = r"refresh_token=\((.+?)\)"
        refresh_json_pattern = r"'refresh_token': \((.+?)\)"

        access_token_pattern = r"access_token='([^']+)'"
        access_json_pattern = r"'access_token': '([^']+)'"

        self.patterns = [
            (id_token_pattern, "id_token=[ID_TOKEN]"),
            (id_json_pattern, "'id_token': [ID_TOKEN]"),
            (refresh_token_pattern, "refresh_token=[REFRESH_TOKEN]"),
            (refresh_json_pattern, "'refresh_token': [REFRESH_TOKEN]"),
            (access_token_pattern, "access_token=[ACCESS_TOKEN]"),
            (access_json_pattern, "'access_token': [ACCESS_TOKEN]"),
        ]

    def filter(self, record):
        message = record.getMessage()

        for pattern, replacement in self.patterns:
            message = re.sub(pattern, replacement, message, flags=re.DOTALL)

        record.msg = message
        return True
