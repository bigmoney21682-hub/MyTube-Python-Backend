from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="MyTube Python Backend")

app.include_router(router)
