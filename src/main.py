from fastapi import FastAPI
from src.core.sql import Base, engine


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def index():
    return {"diploma": "started"}
