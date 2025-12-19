# File: main.py

from fastapi import FastAPI

app = FastAPI()

# Root endpoint for testing
@app.get("/")
async def root():
    return {"message": "MyTube backend is live!"}

# Example: add more endpoints here for search, streams, etc.
