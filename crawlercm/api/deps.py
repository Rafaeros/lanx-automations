from fastapi import Request, HTTPException, status
import aiohttp


def get_authenticated_client(request: Request) -> aiohttp.ClientSession:
    """
    Dependency function to provide an authenticated aiohttp client session.

    This function is intended to be used as a FastAPI dependency. It retrieves
    the aiohttp.ClientSession instance that was initialized and stored in
    `app.state` by the application's lifespan handler. This session is used
    for making authenticated requests to external systems (e.g., scraping).

    Raises:
        HTTPException:
            If the client session is not available or has already been closed,
            an HTTP 503 Service Unavailable exception is raised.

    Args:
        request (Request): The FastAPI request object, used to access the
        application state.

    Returns:
        aiohttp.ClientSession: The authenticated aiohttp session for making requests.
    """
    if (
        not hasattr(request.app.state, "http_client")
        or request.app.state.http_client.closed
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No authenticated client session available.",
        )
    return request.app.state.http_client
