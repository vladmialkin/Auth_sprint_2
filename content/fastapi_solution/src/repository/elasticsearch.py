from logging import getLogger
from typing import Any, Coroutine

import backoff
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout, NotFoundError

from ..core.config import settings
from ..repository.base import Repository

logger = getLogger(__name__)


class ESRepository(Repository):
    def __init__(self, es_conn: AsyncElasticsearch) -> None:
        self._conn = es_conn

    @backoff.on_exception(
        backoff.expo,
        (ConnectionError, ConnectionTimeout),
        max_tries=settings.MAX_TRIES,
        logger=logger,
    )
    async def get(self, index: str, key: str) -> Coroutine[Any, Any, Any]:
        try:
            return await self._conn.get(index=index, id=key)
        except NotFoundError:
            return None

    @backoff.on_exception(
        backoff.expo,
        (ConnectionError, ConnectionTimeout),
        max_tries=settings.MAX_TRIES,
        logger=logger,
    )
    async def add(
        self, index: str, document: dict[str, Any]
    ) -> Coroutine[Any, Any, None]:
        return await self._conn.index(index=index, document=document)

    @backoff.on_exception(
        backoff.expo,
        (ConnectionError, ConnectionTimeout),
        max_tries=settings.MAX_TRIES,
        logger=logger,
    )
    async def get_all(
        self,
        index: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        query: dict[str, Any] | None = None,
        sort: dict[str, Any] | None = None,
    ) -> Coroutine[Any, Any, list[Any]]:
        body: dict[str, Any] = {}

        if limit:
            body["size"] = limit

        if offset:
            body["from"] = (offset - 1) * limit

        if query:
            body["query"] = query

        if sort:
            body["sort"] = sort

        return await self._conn.search(index=index, body=body)
