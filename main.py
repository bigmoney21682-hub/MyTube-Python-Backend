# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import json

app = FastAPI()

# Allow your frontend origin
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost:5173",  # local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your exported browser cookies file
COOKIE_FILE = "cookies.txt"

def fetch_ytdlp_data(url: str):
    ydl_opts = {
        "cookiefile": COOKIE_FILE,  # ✅ use cookies
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "extract_flat": True,  # improves search speed for playlists
        "simulate": True,       # no actual download
        "forcejson": True,      # always return JSON
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/trending")
async def trending(region: str = "US"):
    url = f"https://www.youtube.com/feed/trending?gl={region}"
    data = fetch_ytdlp_data(url)
    # flatten playlists into videos if needed
    videos = data.get("entries", []) if isinstance(data, dict) else []
    return videos

@app.get("/search")
async def search(q: str):
    url = f"ytsearch10:{q}"  # fetch top 10 results
    data = fetch_ytdlp_data(url)
    videos = data.get("entries", []) if isinstance(data, dict) else []
    return videos

@app.get("/streams/{video_id}")
async def streams(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    data = fetch_ytdlp_data(url)

    video_streams = []
    hls_url = None

    formats = data.get("formats", [])
    for f in formats:
        if f.get("acodec") != "none" and f.get("vcodec") != "none":
            video_streams.append({
                "url": f.get("url"),
                "format": f.get("ext"),
                "videoOnly": f.get("vcodec") != "none" and f.get("acodec") == "none",
                "bitrate": f.get("tbr") or 0,
            })
        if f.get("protocol") == "m3u8_native":
            hls_url = f.get("url")

    return {
        "title": data.get("title", "Placeholder"),
        "uploaderName": data.get("uploader", "Unknown"),
        "views": data.get("view_count", 0),
        "videoStreams": video_streams,
        "hls": hls_url,
        "relatedStreams": [],  # optional: extend with related
    }
