from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.public import auth, guild, log, reaction_role, welcome_message, auto_role, leave_message


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(guild.router, prefix="/guild", tags=["guild"])
app.include_router(reaction_role.router, prefix="/reaction_role", tags=["reaction_role"])
app.include_router(log.router, prefix="/log", tags=["log"])
app.include_router(welcome_message.router, prefix="/welcome_message", tags=["welcome_message"])
app.include_router(auto_role.router, prefix="/auto_role", tags=["auto_role"])
app.include_router(leave_message.router, prefix="/leave_message", tags=["leave_message"])

@app.get("/")
async def root():
    return { "message": "Up and running!" }
