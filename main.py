# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

# ---------------- CORS ----------------
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost:5173",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HELPERS ----------------
def fetch_yt_info(url: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "ignoreerrors": True,
        "format": "bestvideo+bestaudio/best",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            return {"error": str(e)}

# ---------------- TRENDING ----------------
@app.get("/trending")
def trending(region: str = "US"):
    """
    Return trending videos. Currently using YouTube trending via yt-dlp.
    """
    url = f"https://www.youtube.com/feed/trending?gl={region}&hl=en"
    info = fetch_yt_info(url)
    if "error" in info:
        return JSONResponse(status_code=500, content={"detail": info["error"]})

    # Extract top-level videos
    videos = []
    if "entries" in info:
        for v in info["entries"]:
            if not v:
                continue
            videos.append({
                "id": v.get("id"),
                "title": v.get("title", "Untitled"),
                "uploaderName": v.get("uploader", "Unknown"),
                "views": v.get("view_count", 0),
                "duration": v.get("duration"),
                "thumbnail": v.get("thumbnail"),
            })
    return videos

# ---------------- SEARCH ----------------
@app.get("/search")
def search(q: str):
    """
    Search YouTube using yt-dlp.
    """
    if not q.strip():
        return []
    url = f"ytsearch10:{q}"  # Top 10 results
    info = fetch_yt_info(url)
    if "error" in info:
        return JSONResponse(status_code=500, content={"detail": info["error"]})

    results = []
    if "entries" in info:
        for v in info["entries"]:
            if not v:
                continue
            results.append({
                "id": v.get("id"),
                "title": v.get("title", "Untitled"),
                "uploaderName": v.get("uploader", "Unknown"),
                "views": v.get("view_count", 0),
                "duration": v.get("duration"),
                "thumbnail": v.get("thumbnail"),
            })
    return results

# ---------------- STREAMS ----------------
@app.get("/streams/{video_id}")
def streams(video_id: str):
    """
    Return all available streams for a video.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    info = fetch_yt_info(url)
    if "error" in info:
        return JSONResponse(status_code=500, content={"detail": info["error"]})

    streams = []
    # Progressive MP4 first
    for f in info.get("formats", []):
        if f.get("url") and f.get("acodec") != "none" and f.get("vcodec") != "none":
            streams.append({
                "format": f.get("ext"),
                "videoOnly": f.get("vcodec") != "none" and f.get("acodec") == "none",
                "audioOnly": f.get("acodec") != "none" and f.get("vcodec") == "none",
                "url": f.get("url"),
                "height": f.get("height"),
                "width": f.get("width"),
                "bitrate": f.get("tbr"),
            })

    # Fallback HLS
    hls = next((f.get("url") for f in info.get("formats", []) if f.get("protocol") == "m3u8_native"), None)

    return {
        "id": info.get("id"),
        "title": info.get("title", "Untitled"),
        "uploaderName": info.get("uploader", "Unknown"),
        "views": info.get("view_count", 0),
        "duration": info.get("duration"),
        "videoStreams": streams,
        "hls": hls,
        "relatedStreams": [],  # Can add related videos later
    }
