from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers.public import auth, log, reaction_role, user


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(reaction_role.router, prefix="/reaction_role", tags=["reaction_role"])
app.include_router(log.router, prefix="/log", tags=["log"])

@app.get("/")
async def root():
    return { "message": "Up and running!" }
