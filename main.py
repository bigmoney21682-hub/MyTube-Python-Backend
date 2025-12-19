# File: main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import yt_dlp

app = FastAPI()

# -----------------------------
# CORS configuration
# -----------------------------
origins = [
    "https://bigmoney21682-hub.github.io",  # Your frontend
    "http://localhost:5173",                # Local dev (Vite default)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Helper to call Piped or yt-dlp
# -----------------------------
async def fetch_json(url: str):
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Trending endpoint
# -----------------------------
@app.get("/trending")
async def trending(region: str = "US"):
    piped_url = f"https://pipedapi.kavin.rocks/trending?region={region}"
    try:
        data = await fetch_json(piped_url)
        return data
    except HTTPException as e:
        return JSONResponse({"detail": f"Server error '{e.detail}' for url '{piped_url}'"}, status_code=521)

# -----------------------------
# Search endpoint
# -----------------------------
@app.get("/search")
async def search(q: str):
    if not q.strip():
        return []
    piped_url = f"https://pipedapi.kavin.rocks/search?q={q}&filter=videos"
    try:
        data = await fetch_json(piped_url)
        return data.get("items", [])
    except HTTPException as e:
        return JSONResponse({"detail": f"Server error '{e.detail}' for url '{piped_url}'"}, status_code=521)

# -----------------------------
# Stream endpoint
# -----------------------------
@app.get("/streams/{video_id}")
async def streams(video_id: str):
    ydl_opts = {
        "format": "best",
        "quiet": True,
        "noplaylist": True,
    }

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Collect MP4 and HLS streams
            streams = []
            hls_url = None

            if "formats" in info:
                for f in info["formats"]:
                    streams.append({
                        "url": f.get("url"),
                        "format": f.get("ext"),
                        "videoOnly": f.get("vcodec") != "none",
                        "bitrate": f.get("tbr"),
                    })
                    if f.get("protocol") == "m3u8":
                        hls_url = f.get("url")

            related = info.get("entries", []) or []

            return {
                "title": info.get("title", "Placeholder"),
                "uploaderName": info.get("uploader", "Unknown"),
                "views": info.get("view_count", 0),
                "videoStreams": streams,
                "hls": hls_url,
                "relatedStreams": related,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
