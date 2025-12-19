# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from yt_dlp import YoutubeDL
import os

app = FastAPI()

# -------------------------
# CORS (unchanged)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# CONSTANTS
# -------------------------
COOKIES_PATH = os.path.join(os.getcwd(), "cookies.txt")

if not os.path.exists(COOKIES_PATH):
    print("⚠️ cookies.txt NOT FOUND at backend root")

# -------------------------
# STREAM ENDPOINT
# -------------------------
@app.get("/streams/{video_id}")
def get_streams(video_id: str):
    """
    Returns playable streams for a YouTube video.
    Cookies are REQUIRED to avoid bot verification.
    """

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,

        # ✅ THIS IS THE FIX
        "cookiefile": COOKIES_PATH,

        # Safer format selection
        "format": "bestvideo+bestaudio/best",

        # Prevent throttling issues
        "noplaylist": True,
        "extract_flat": False,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False,
            )

        formats = info.get("formats", [])

        streams = []
        for f in formats:
            if f.get("url") and f.get("vcodec") != "none":
                streams.append({
                    "url": f["url"],
                    "mimeType": f.get("ext"),
                    "quality": f.get("format_note") or f.get("resolution"),
                })

        if not streams:
            raise HTTPException(status_code=404, detail="No playable streams found")

        return {
            "id": video_id,
            "title": info.get("title"),
            "streams": streams,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"yt-dlp error: {str(e)}"
        )
