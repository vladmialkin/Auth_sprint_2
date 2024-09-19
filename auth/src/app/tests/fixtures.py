# from collections.abc import AsyncGenerator
#
# import pytest
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import (
#     AsyncConnection,
#     AsyncSession,
#     AsyncTransaction,
# )
#
# from app.db.postgresql import async_engine, get_async_session
# from app.main import app
#
#
# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"
#
#
# @pytest.fixture(scope="session")
# async def connection(anyio_backend) -> AsyncGenerator[AsyncConnection, None]:
#     async with async_engine.connect() as connection:
#         yield connection
#
#
# @pytest.fixture
# async def transaction(
#     connection: AsyncConnection,
# ) -> AsyncGenerator[AsyncTransaction, None]:
#     async with connection.begin() as transaction:
#         yield transaction
#
#
# @pytest.fixture
# async def session(
#     connection: AsyncConnection, transaction: AsyncTransaction
# ) -> AsyncGenerator[AsyncSession, None]:
#     async_session = AsyncSession(
#         bind=connection,
#         join_transaction_mode="create_savepoint",
#         expire_on_commit=False,
#     )
#
#     async with async_session as session:
#         yield session
#
#     await transaction.rollback()
#
#
# @pytest.fixture
# async def client(session) -> AsyncGenerator[AsyncClient, None]:
#     async def override_get_async_session() -> (
#         AsyncGenerator[AsyncSession, None]
#     ):
#         yield session
#
#     app.dependency_overrides[get_async_session] = override_get_async_session
#     return AsyncClient(app=app, base_url="http://localhost:8010")
