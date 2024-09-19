import asyncio

import click
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.repository.user import user_repository
from app.settings.postgresql import settings


@click.command()
@click.option("--email", prompt="Enter email", help="Email of the user")
@click.option(
    "--password",
    prompt="Enter password",
    hide_input=True,
    confirmation_prompt=True,
    help="Password of the user",
)
def createsuperuser(email, password) -> str:
    asyncio.run(create_superuser_async(email, password))


async def create_superuser_async(email, password):
    async_engine: AsyncEngine = create_async_engine(
        settings.DSN, echo=settings.LOG_QUERIES
    )
    async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
        async_engine, expire_on_commit=False
    )

    async with async_session() as session:
        is_exists = await user_repository.exists(session, email=email)

        if is_exists:
            print(f"Superuser {email} already exists.")
            return

        await user_repository.create(
            session,
            {
                "email": email,
                "hashed_password": PasswordHelper().hash(password),
                "is_active": True,
                "is_superuser": True,
            },
        )

    print(f"Superuser {email} created.")


if __name__ == "__main__":
    createsuperuser()
