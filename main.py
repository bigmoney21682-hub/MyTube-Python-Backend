# File: main.py

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import yt_dlp
import asyncio

app = FastAPI(title="MyTube Python Backend")

# ----------------- CORS -----------------
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- yt-dlp utility -----------------
async def extract_info(url: str, is_search=False):
    loop = asyncio.get_event_loop()
    opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": is_search,  # search returns simplified entries
        "dump_single_json": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))

# ----------------- Routes -----------------

@app.get("/")
async def root():
    return {"message": "MyTube Backend is live!"}

# ----------------- Trending -----------------
@app.get("/trending")
async def trending(region: str = Query("US", description="Region code for trending")):
    try:
        url = f"https://www.youtube.com/feed/trending?gl={region}&hl=en"
        info = await extract_info(url)
        # Flatten list of videos
        videos = info.get("entries", [])
        return videos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Search -----------------
@app.get("/search")
async def search(q: str = Query(..., min_length=1, description="Search query")):
    try:
        search_url = f"ytsearch10:{q}"  # top 10 results
        info = await extract_info(search_url, is_search=True)
        return {"items": info.get("entries", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Streams -----------------
@app.get("/streams/{video_id}")
async def streams(video_id: str = Path(..., description="YouTube video ID")):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        info = await extract_info(url)
        
        # Progressive streams (video + audio)
        video_streams = [
            {
                "url": f.get("url"),
                "format": f.get("ext").upper(),
                "videoOnly": f.get("vcodec") != "none"
            }
            for f in info.get("formats", [])
        ]

        # Related videos
        related_streams = info.get("related_videos", [])
        return {
            "title": info.get("title", "Unknown"),
            "uploaderName": info.get("uploader", "Unknown"),
            "views": info.get("view_count", 0),
            "videoStreams": video_streams,
            "relatedStreams": related_streams,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Health Check -----------------
@app.get("/health")
async def health():
    return {"status": "ok"}
