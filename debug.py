import uvicorn
import asyncio
from fastapi import FastAPI

from src.public_app import app as public_app
from src.internal_app import app as internal_app


async def run_app(app: FastAPI, host: str, port: int):
    config = uvicorn.Config(app, host=host, port=port, workers=8, log_level="info", proxy_headers=True)
    server = uvicorn.Server(config)
    await server.serve()


async def run_apps():
    try:
        await asyncio.gather(
            run_app(public_app, "127.0.0.1", 8000),
            run_app(internal_app, "127.0.0.1", 9000),
        )
    except asyncio.exceptions.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(run_apps())
