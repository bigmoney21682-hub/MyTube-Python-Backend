# File: main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL
import os

app = FastAPI()

# ---------------- CORS ----------------
origins = [
    "https://bigmoney21682-hub.github.io",  # your frontend
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- yt-dlp Options ----------------
COOKIES_FILE = "cookies.txt"  # must be in same folder as main.py
YDL_OPTS = {
    "quiet": True,
    "nocheckcertificate": True,
    "extract_flat": False,
    "cookiefile": COOKIES_FILE,
    "skip_download": True,
    "simulate": True,
}

# ---------------- SEARCH ----------------
@app.get("/search")
async def search(q: str):
    url = f"ytsearch20:{q}"
    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            result = ydl.extract_info(url, download=False)
            videos = [
                {
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "uploaderName": v.get("uploader") or "Unknown",
                    "views": v.get("view_count") or 0,
                    "duration": v.get("duration"),
                    "thumbnail": v.get("thumbnail"),
                }
                for v in result.get("entries", [])
                if v.get("id")
            ]
        return JSONResponse(content=videos)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# ---------------- TRENDING ----------------
@app.get("/trending")
async def trending(region: str = "US"):
    # Fallback using search 'trending'
    url = "ytsearch20:trending"
    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            result = ydl.extract_info(url, download=False)
            videos = [
                {
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "uploaderName": v.get("uploader") or "Unknown",
                    "views": v.get("view_count") or 0,
                    "duration": v.get("duration"),
                    "thumbnail": v.get("thumbnail"),
                }
                for v in result.get("entries", [])
                if v.get("id")
            ]
        return JSONResponse(content=videos)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"ERROR: {str(e)}"})

# ---------------- STREAMS ----------------
@app.get("/streams/{video_id}")
async def streams(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            # Extract video formats
            video_streams = []
            hls_url = None
            for f in info.get("formats", []):
                stream = {
                    "url": f.get("url"),
                    "format": f.get("ext"),
                    "videoOnly": f.get("vcodec") != "none" and f.get("acodec") == "none",
                    "audioOnly": f.get("acodec") != "none" and f.get("vcodec") == "none",
                    "bitrate": f.get("tbr") or 0,
                }
                video_streams.append(stream)
                if f.get("protocol") == "m3u8_native" and not hls_url:
                    hls_url = f.get("url")

            related = []
            for entry in info.get("entries", []) or []:
                related.append({
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "thumbnail": entry.get("thumbnail"),
                    "uploaderName": entry.get("uploader"),
                    "views": entry.get("view_count"),
                    "duration": entry.get("duration"),
                    "type": "stream"
                })

        return JSONResponse(content={
            "title": info.get("title") or "Placeholder",
            "uploaderName": info.get("uploader") or "Unknown",
            "views": info.get("view_count") or 0,
            "videoStreams": video_streams,
            "hls": hls_url,
            "relatedStreams": related
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# ---------------- ROOT ----------------
@app.get("/")
async def root():
    return {"status": "ok"}
