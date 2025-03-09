from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routers import auth


app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return { "message": "Up and running!" }
