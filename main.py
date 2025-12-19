# File: main.py
# Path: / (root of backend project)

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

# -----------------------------
# CORS: allow your frontend
# -----------------------------
origins = [
    "https://bigmoney21682-hub.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# API route example
# -----------------------------
@app.get("/api/trending")
async def trending(region: str = "US"):
    try:
        # Example using yt-dlp to get trending videos (placeholder)
        ydl_opts = {"extract_flat": True}
        url = f"https://www.youtube.com/feed/trending?gl={region}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return JSONResponse(content=info)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# -----------------------------
# Serve frontend files
# -----------------------------
frontend_path = os.path.dirname(__file__)

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str, request: Request):
    requested_file = os.path.join(frontend_path, full_path)
    if os.path.isfile(requested_file):
        return FileResponse(requested_file)
    # Fallback: serve index.html for SPA
    return FileResponse(os.path.join(frontend_path, "index.html"))
