from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json

app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bigmoney21682-hub.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {"status": "MyTube backend running"}

# -------------------- TRENDING --------------------
@app.get("/trending")
def trending():
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",
            "--yes-playlist",
            "https://www.youtube.com/feed/trending"
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        videos = []

        for line in proc.stdout:
            try:
                data = json.loads(line)

                video_id = data.get("id")
                if not video_id:
                    continue

                videos.append({
                    "id": video_id,
                    "title": data.get("title"),
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                    "uploaderName": data.get("uploader"),
                    "views": data.get("view_count"),
                    "duration": data.get("duration"),
                })

            except Exception:
                continue

        return videos[:25]

    except Exception as e:
        return {"error": str(e)}
