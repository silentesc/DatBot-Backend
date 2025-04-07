import uvicorn
import asyncio
from fastapi import FastAPI, Request
from loguru import logger

from src.public_app import app as public_app
from src.internal_app import app as internal_app


@public_app.middleware("http")
async def log_client_ip(request: Request, call_next):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host
    logger.info(f"Request from client: {client_ip} - {request.method} {request.url}")
    response = await call_next(request)
    return response


async def run_app(app: FastAPI, host: str, port: int):
    config = uvicorn.Config(app, host=host, port=port, workers=8, log_level="info", proxy_headers=True)
    server = uvicorn.Server(config)
    await server.serve()


async def run_apps():
    try:
        await asyncio.gather(
            run_app(public_app, "0.0.0.0", 8000),
            run_app(internal_app, "127.0.0.1", 9000),
        )
    except asyncio.exceptions.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(run_apps())
