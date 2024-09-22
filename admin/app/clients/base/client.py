from typing import Any
from urllib.parse import urljoin

from requests import Request, Response, Session, codes
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, Timeout
from clients.base.exceptions import (
    BadRequest,
    BaseClientException,
    Forbidden,
    NotAuthorized,
    NotFound,
    ResponseDecodeError,
    ServerError,
)
from urllib3.util import Retry


class BaseClient:
    def __init__(
        self,
        base_url: str,
        timeout: float | None = None,
    ):
        self._base_url = base_url
        self._session = Session()
        self._timeout = timeout

        retries = Retry(total=3, backoff_factor=0.3)

        self._session.mount(self._base_url, HTTPAdapter(max_retries=retries))

    def _make_request(self, method: str, url: str, *args, **kwargs) -> Any | None:
        with self._session as s:
            request = self._session.prepare_request(
                Request(
                    method=method,
                    url=urljoin(self._base_url, url),
                    *args,
                    **kwargs,
                )
            )

            try:
                response = s.send(request, timeout=self._timeout)
            except (RequestsConnectionError, Timeout):
                raise ConnectionError

            handled = self._handle_response(response)
            return self._decode_response(handled)

    def _decode_response(self, response: Response) -> Any | None:
        if response.status_code == 204:
            return None
        try:
            return response.json()
        except ValueError:
            raise ResponseDecodeError

    def _handle_response(self, response: Response) -> Response:
        try:
            response.raise_for_status()
            return response
        except HTTPError as cause:
            status_code = cause.response.status_code
            if 500 <= status_code < 600:
                raise ServerError from cause

            to_raise = BaseClientException

            match status_code:
                case codes.bad_request:
                    to_raise = BadRequest
                case codes.unauthorized:
                    to_raise = NotAuthorized
                case codes.forbidden:
                    to_raise = Forbidden
                case codes.not_found:
                    to_raise = NotFound

            raise to_raise(response) from cause

    def _get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any | None:
        return self._make_request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
        )

    def _post(
        self,
        url: str,
        data: dict[str, Any] | list[tuple[str, Any]] = None,
        params: dict[str, Any] | None = None,
        json: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any | None:
        return self._make_request(
            method="POST",
            url=url,
            data=data,
            params=params,
            json=json,
            headers=headers,
        )

    def _put(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        json: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any | None:
        return self._make_request(
            method="PUT",
            url=url,
            params=params,
            json=json,
            headers=headers,
        )

    def _patch(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        json: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any | None:
        return self._make_request(
            method="PATCH",
            url=url,
            params=params,
            json=json,
            headers=headers,
        )

    def _delete(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any | None:
        return self._make_request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers,
        )
