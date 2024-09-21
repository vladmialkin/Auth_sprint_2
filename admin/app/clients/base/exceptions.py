from requests.models import Response
from json import JSONDecodeError


class ServerError(Exception):
    pass


class BaseClientException(Exception):
    def __init__(self, response: Response) -> None:
        self._status_code = response.status_code
        self._data = self._get_data(response)

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def data(self) -> str:
        return self._data
    
    def _get_data(self, response: Response) -> str:
        try:
            return response.json()
        except JSONDecodeError:
            return response.text


class ResponseDecodeError(BaseClientException):
    pass


class BadRequest(BaseClientException):
    pass


class NotFound(BaseClientException):
    pass


class Forbidden(BaseClientException):
    pass


class NotAuthorized(BaseClientException):
    pass
