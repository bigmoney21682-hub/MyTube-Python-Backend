# File: main.py
# Path: /main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

# -----------------------------
# App
# -----------------------------
app = FastAPI()

# -----------------------------
# CORS (CRITICAL FIX)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bigmoney21682-hub.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Upstream API (Piped)
# -----------------------------
PIPED_API = "https://pipedapi.kavin.rocks"

client = httpx.AsyncClient(timeout=20)

# -----------------------------
# Health check
# -----------------------------
@app.get("/")
async def root():
    return {"status": "ok"}

# -----------------------------
# Trending
# -----------------------------
@app.get("/trending")
async def trending(region: str = "US"):
    try:
        r = await client.get(f"{PIPED_API}/trending", params={"region": region})
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Search
# -----------------------------
@app.get("/search")
async def search(q: str, filter: str = "videos"):
    try:
        r = await client.get(
            f"{PIPED_API}/search",
            params={"q": q, "filter": filter},
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Streams
# -----------------------------
@app.get("/streams/{video_id}")
async def streams(video_id: str):
    try:
        r = await client.get(f"{PIPED_API}/streams/{video_id}")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
