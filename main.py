# File: main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Path, Query
import asyncio
import yt_dlp
from typing import List

app = FastAPI(title="MyTube Python Backend")

# ----------------- CORS -----------------
origins = [
    "https://bigmoney21682-hub.github.io",  # your FE
    "http://localhost:5173",  # local Vite dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Routes -----------------

@app.get("/")
async def root():
    return {"message": "MyTube Backend is live!"}


@app.get("/trending")
async def trending(region: str = Query("US", description="Region code for trending")):
    """
    Fetch trending videos.
    Currently returns placeholder list. Replace with PipedAPI or yt-dlp extraction.
    """
    try:
        # Placeholder empty list for now
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search(q: str = Query(..., min_length=1, description="Search query")):
    """
    Search videos by query.
    Currently returns placeholder array. Replace with real PipedAPI or yt-dlp extraction.
    """
    try:
        return {"items": []}  # shape matches FE expectation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/streams/{video_id}")
async def streams(
    video_id: str = Path(..., description="YouTube or Piped video ID")
):
    """
    Returns video info & stream URLs
    Currently returns placeholder object.
    Replace with yt-dlp extraction for real streams.
    """
    try:
        return {
            "title": "Placeholder",
            "uploaderName": "Unknown",
            "views": 0,
            "videoStreams": [],       # FE expects list of streams
            "relatedStreams": [],     # FE expects related video objects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Optional: Health Check -----------------
@app.get("/health")
async def health():
    return {"status": "ok"}
