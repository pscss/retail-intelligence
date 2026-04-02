"""API key authentication dependency for gateway."""

from fastapi import Header, HTTPException, Request, status

from shared.config import settings


async def require_api_key(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> None:
    """Validate API key — skip for GET requests (playground)."""
    if request.method == "GET":
        return

    api_key = None
    if authorization and authorization.startswith("Bearer "):
        api_key = authorization.removeprefix("Bearer ")
    elif x_api_key:
        api_key = x_api_key

    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
