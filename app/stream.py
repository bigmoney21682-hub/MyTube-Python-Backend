from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import yt_dlp
import io

router = APIRouter()

@router.get("/{video_id}")
async def stream_video(video_id: str):
    """
    Minimal proxy to stream a YouTube video via yt-dlp
    """
    try:
        # yt-dlp extract
        ydl_opts = {
            "format": "best",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            video_url = info.get("url")

        if not video_url:
            raise HTTPException(status_code=404, detail="Stream URL not found")

        # Return a streaming response that redirects to video_url
        return StreamingResponse(io.BytesIO(b""), media_type="video/mp4", headers={"Location": video_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
