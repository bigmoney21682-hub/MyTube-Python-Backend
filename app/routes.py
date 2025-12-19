from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from app.yt_utils import search_videos, get_video_stream
from app.proxy_stream import proxy_stream

router = APIRouter()

@router.get("/search")
async def search(q: str):
    try:
        items = await search_videos(q)
        return JSONResponse({"items": items})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@router.get("/stream/{video_id}")
async def stream(video_id: str):
    try:
        stream_url = await get_video_stream(video_id)
        return StreamingResponse(proxy_stream(stream_url))
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
