import enum
from json import JSONDecodeError
from typing import Any

from httpx import AsyncClient, ConnectError, Response, TimeoutException, codes

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from src.clients.base.constants import CONNECTION_TIMEOUT, MAX_RETRIES
from src.clients.base.exceptions import (
    BadRequestError,
    NotFoundError,
    ResponseDecodeError,
    ServiceConnectionError,
    UnauthorizedError,
)


class HTTPMethods(enum.StrEnum):
    GET = enum.auto()
    POST = enum.auto()
    PATCH = enum.auto()
    DELETE = enum.auto()
    PUT = enum.auto()


class BaseClient:
    def __init__(self, base_url: str, *, headers: dict[str, Any] | None = None):
        self._base_url = base_url
        self._headers = headers

    @staticmethod
    def _decode_response(response: Response) -> Any:
        try:
            return response.json()
        except JSONDecodeError:
            raise ResponseDecodeError

    def _handle_response(self, response: Response) -> Any:
        if response.status_code == codes.NO_CONTENT:
            return Response(status_code=codes.NO_CONTENT)

        payload = self._decode_response(response)
        match response.status_code:
            case codes.BAD_REQUEST:
                raise BadRequestError(payload.get("detail"))
            case codes.UNAUTHORIZED:
                raise UnauthorizedError(payload.get("detail"))
            case codes.NOT_FOUND:
                raise NotFoundError(payload.get("detail"))
            case _:
                return payload

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_random_exponential(multiplier=2, max=120),
        reraise=True,
    )
    async def _make_request(
        self,
        method: HTTPMethods,
        url: str,
        headers: dict | None = None,
        **kwargs,
    ):
        async with AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=CONNECTION_TIMEOUT,
        ) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs,
            )
            return self._handle_response(response)

    async def _get(
        self,
        *,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        return await self._make_request(
            method=HTTPMethods.GET,
            url=url,
            params=params,
            headers=headers,
            **kwargs,
        )

    async def _post(
        self,
        *,
        url: str,
        json: dict | list | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        return await self._make_request(
            method=HTTPMethods.POST,
            url=url,
            json=json,
            headers=headers,
            **kwargs,
        )

    async def _patch(
        self,
        *,
        url: str,
        params: dict | None = None,
        json: dict | list | None = None,
        **kwargs,
    ):
        return await self._make_request(
            method=HTTPMethods.PATCH,
            url=url,
            params=params,
            json=json,
            **kwargs,
        )

    async def _put(
        self,
        *,
        url: str,
        json: dict | list | None = None,
        headers: dict | None = None,
        **kwargs,
    ):
        return await self._make_request(
            method=HTTPMethods.PUT,
            url=url,
            json=json,
            headers=headers,
            **kwargs,
        )

    async def _delete(
        self,
        *,
        url: str,
        params: dict | None = None,
        json: dict | list | None = None,
        **kwargs,
    ):
        return await self._make_request(
            method=HTTPMethods.DELETE,
            url=url,
            params=params,
            json=json,
            **kwargs,
        )
