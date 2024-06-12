from requests.adapters import MaxRetryError, Retry
from requests import Response
from requests.structures import CaseInsensitiveDict
from urllib3 import HTTPResponse
import json


class ResponseAwareRetry(Retry):
    def increment(self, *args, **kwargs):
        """
        Attaches previous response to MaxRetryError exception
        """
        try:
            return super().increment(*args, **kwargs)
        except MaxRetryError as ex:
            response = kwargs.get("response")
            if response:
                requests_response = self.build_requests_response(response)
                ex.response = requests_response
            else:
                ex.response = Response()
            raise

    def build_requests_response(self, urllib3_response: HTTPResponse) -> Response:
        """Convert an urllib3 response to a Requests Response object."""
        requests_response = Response()
        requests_response.status_code = urllib3_response.status
        requests_response.headers = CaseInsensitiveDict(
            urllib3_response.headers.items()
        )
        requests_response.reason = urllib3_response.reason or ""
        requests_response.url = urllib3_response.geturl() or ""
        requests_response.raw = urllib3_response

        # Get the content encoding from headers
        content_encoding = requests_response.headers.get("content-encoding", "").lower()
        body = urllib3_response.data.decode(content_encoding or "utf-8")

        # Inject the extra attribute into the response body
        try:
            response_body = json.loads(body)
        except ValueError:
            response_body = {}

        response_body["message"] = "Maximum number of retries reached"
        requests_response._content = json.dumps(response_body).encode("utf-8")

        requests_response.encoding = urllib3_response.headers.get("content-type")
        return requests_response
