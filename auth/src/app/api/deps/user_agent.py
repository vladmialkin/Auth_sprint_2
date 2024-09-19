from typing import Annotated

from fastapi import Depends, Request


def get_user_agent(request: Request) -> str | None:
    return request.headers.get("User-Agent")


UserAgent = Annotated[str | None, Depends(get_user_agent)]
