from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(debug=True, description="Diploma")


@app.get("/")
async def index():
    return {"diploma": "started"}
