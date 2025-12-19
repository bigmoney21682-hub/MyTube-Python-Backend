# File: main.py
# Path: / (root of your backend project)

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# -----------------------------
# CORS Setup
# -----------------------------
origins = [
    "https://bigmoney21682-hub.github.io",  # <- Your frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Health Check
# -----------------------------
@app.get("/ping")
def ping():
    return {"message": "pong"}

# -----------------------------
# Piped API Proxy Endpoints
# -----------------------------
PIPED_BASE = "https://pipedapi.kavin.rocks"

@app.get("/trending")
async def trending(region: str = Query("US")):
    """
    Proxy trending videos from Piped API
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PIPED_BASE}/trending?region={region}")
        response.raise_for_status()
        return response.json()

@app.get("/search")
async def search(query: str, region: str = Query("US")):
    """
    Proxy search results from Piped API
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PIPED_BASE}/search", params={"q": query, "region": region})
        response.raise_for_status()
        return response.json()

@app.get("/video")
async def video(id: str):
    """
    Proxy video details from Piped API
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PIPED_BASE}/video/{id}")
        response.raise_for_status()
        return response.json()
