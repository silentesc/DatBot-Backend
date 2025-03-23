from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.internal import reaction_role


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reaction_role.router, prefix="/reaction_role", tags=["reaction_role"])

@app.get("/")
async def root():
    return { "message": "Up and running!" }
