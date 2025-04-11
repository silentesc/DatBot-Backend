from aiohttp import ClientResponse, ClientResponseError
from fastapi import HTTPException


async def check_for_error(response: ClientResponse):
    try:
        response.raise_for_status()
    except ClientResponseError:
        detail = await response.text()
        raise HTTPException(status_code=response.status, detail=detail)
