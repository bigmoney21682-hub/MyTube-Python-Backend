# File: main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI()

# ✅ Allow your frontend origin
origins = [
    "https://bigmoney21682-hub.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HELPERS ----------------
def get_ydl_options():
    return {
        "cookies": "cookies.txt",  # <-- your cookies file in backend root
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
        "noplaylist": True,
        "quiet": True,
    }

# ---------------- TRENDING ----------------
@app.get("/trending")
async def trending(region: str = "US"):
    url = f"https://www.youtube.com/feed/trending?gl={region}"
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)
        return info.get("entries", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- SEARCH ----------------
@app.get("/search")
async def search(q: str):
    if not q.strip():
        return []
    url = f"https://www.youtube.com/results?search_query={q}"
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)
        return info.get("entries", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- STREAMS ----------------
@app.get("/streams/{video_id}")
async def streams(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(get_ydl_options()) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title", "Unknown"),
            "uploaderName": info.get("uploader", "Unknown"),
            "views": info.get("view_count", 0),
            "videoStreams": [
                {
                    "url": f["url"],
                    "format": f.get("ext"),
                    "videoOnly": f.get("vcodec") != "none",
                    "audioOnly": f.get("acodec") != "none",
                    "bitrate": f.get("tbr"),
                }
                for f in info.get("formats", [])
            ],
            "relatedStreams": info.get("related_videos", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- HEALTH CHECK ----------------
@app.get("/")
async def root():
    return {"status": "Backend running"}
