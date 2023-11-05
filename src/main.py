from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.users.api import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(debug=True, description="Diploma")

app.include_router(user_router, tags=["users"])


@app.get("/")
async def index():
    return {"diploma": "started"}
