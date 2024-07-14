from fastapi import FastAPI

from models.base_model import Base
from routes import auth
from db import engine


app = FastAPI()

app.include_router(auth.router, prefix="/auth")

Base.metadata.create_all(engine)
