from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.internal import reaction_role, guild, welcome_message, auto_role


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reaction_role.router, prefix="/reaction_role", tags=["reaction_role"])
app.include_router(guild.router, prefix="/guild", tags=["guild"])
app.include_router(welcome_message.router, prefix="/welcome_message", tags=["welcome_message"])
app.include_router(auto_role.router, prefix="/auto_role", tags=["auto_role"])

@app.get("/")
async def root():
    return { "message": "Up and running!" }
