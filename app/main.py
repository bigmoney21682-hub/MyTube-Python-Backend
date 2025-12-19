from fastapi import FastAPI
from app.stream import router as stream_router

app = FastAPI(title="MyTube Python Backend")

# Include streaming routes
app.include_router(stream_router, prefix="/stream")

@app.get("/")
async def root():
    return {"message": "Python MyTube Backend is alive!"}
