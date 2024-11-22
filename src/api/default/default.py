"""
This module defines API default routes for a router.

These routes handle health checks and basic information requests.
"""
from fastapi import APIRouter, Response, Request

default_router = APIRouter()


@default_router.get("/health")
async def health() -> Response:
    """
    Health check route to indicate the service is running properly.

    Returns:
        Response: A response with a 200 status code.
    """
    return Response(status_code=200)


@default_router.get("/")
async def home() -> Response:
    """
    Home route to return a simple "Hello World" message.

    Returns:
        Response: A response with a "Hello World" message and a 200 status code.
    """
    return Response(content='{"message": "Hello World"}', status_code=200)


@default_router.get("/version")
def last_version(request: Request) -> Response:
    """
    Route to get the application's version.

    Args:
        request (Request): The incoming request.

    Returns:
        Response: A response containing the application's version and a 200 status code.
    """
    return Response(
        content=f'{{"version": "{request.app.state.version}"}}', status_code=200
    )
