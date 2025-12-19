# File: main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from yt_dlp import YoutubeDL
import os

app = FastAPI(title="MyTube Backend")

# ---------------- CORS ----------------
origins = [
    "https://bigmoney21682-hub.github.io",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Cookies ----------------
COOKIE_FILE = "cookies.txt"  # must be in backend root

if not os.path.exists(COOKIE_FILE):
    print("⚠️ Warning: cookies.txt not found. Trending may fail.")

# ---------------- YT-DLP Options ----------------
YDL_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "cookiefile": COOKIE_FILE,
    "format": "bestvideo+bestaudio/best",
    "noplaylist": True,
}

YDL_OPTS_TRENDING = {
    **YDL_OPTS,
    "noplaylist": False,
}

# ---------------- ROUTES ----------------
@app.get("/trending")
async def trending(region: str = "US"):
    url = f"https://www.youtube.com/feed/trending?gl={region}"
    try:
        with YoutubeDL(YDL_OPTS_TRENDING) as ydl:
            result = ydl.extract_info(url, download=False)
            if "entries" in result:
                videos = [
                    {
                        "id": v.get("id"),
                        "title": v.get("title"),
                        "uploaderName": v.get("uploader") or v.get("channel") or "Unknown",
                        "views": v.get("view_count") or 0,
                        "duration": v.get("duration"),
                        "thumbnail": v.get("thumbnail"),
                    }
                    for v in result["entries"]
                    if v.get("id")
                ]
            else:
                videos = []
        return JSONResponse(content=videos)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"ERROR: {str(e)}"},
        )

@app.get("/search")
async def search(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query missing")
    url = f"ytsearch10:{q}"
    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            result = ydl.extract_info(url, download=False)
            items = [
                {
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "uploaderName": v.get("uploader") or v.get("channel") or "Unknown",
                    "views": v.get("view_count") or 0,
                    "duration": v.get("duration"),
                    "thumbnail": v.get("thumbnail"),
                }
                for v in result.get("entries", [])
                if v.get("id")
            ]
        return JSONResponse(content={"items": items})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"ERROR: {str(e)}"},
        )

@app.get("/streams/{video_id}")
async def streams(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_streams = [
                {
                    "url": f"{f['url']}",
                    "format": f.get("ext"),
                    "videoOnly": f.get("vcodec") != "none" and f.get("acodec") == "none",
                    "audioOnly": f.get("acodec") != "none" and f.get("vcodec") == "none",
                    "bitrate": f.get("tbr") or 0,
                }
                for f in info.get("formats", [])
            ]
            related = [
                {
                    "title": v.get("title"),
                    "url": f"https://www.youtube.com/watch?v={v.get('id')}",
                    "thumbnail": v.get("thumbnail"),
                    "uploaderName": v.get("uploader") or "Unknown",
                    "views": v.get("view_count") or 0,
                    "duration": v.get("duration"),
                    "type": "stream",
                }
                for v in info.get("related_videos", [])
            ]
            response = {
                "title": info.get("title") or "Placeholder",
                "uploaderName": info.get("uploader") or "Unknown",
                "views": info.get("view_count") or 0,
                "videoStreams": video_streams,
                "relatedStreams": related,
                "hls": info.get("url") if info.get("url").endswith(".m3u8") else None,
            }
        return JSONResponse(content=response)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"ERROR: {str(e)}"},
        )

# ---------------- RUN ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
