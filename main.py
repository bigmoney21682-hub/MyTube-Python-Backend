from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List

app = FastAPI(title="MyTube Python Backend")

# Curated playlist for testing
CURATED_PLAYLIST = [
    {
        "title": "Rick Astley - Never Gonna Give You Up",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "uploaderName": "Rick Astley",
        "views": 123456789,
        "duration": "3:33"
    },
    {
        "title": "Coldplay - Viva La Vida",
        "url": "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",
        "uploaderName": "Coldplay",
        "views": 98765432,
        "duration": "4:12"
    },
    {
        "title": "Daft Punk - One More Time",
        "url": "https://www.youtube.com/watch?v=FGBhQbmPwH8",
        "uploaderName": "Daft Punk",
        "views": 87654321,
        "duration": "5:20"
    }
]

@app.get("/trending")
async def trending(region: str = "US"):
    """
    Returns a curated playlist JSON for testing purposes.
    """
    # Currently ignoring region, can be used later
    return JSONResponse(content=CURATED_PLAYLIST)


@app.get("/search")
async def search(q: str):
    """
    Dummy search endpoint returning placeholder JSON.
    """
    result = {
        "title": f"Search result for '{q}'",
        "uploaderName": "Unknown",
        "views": 0,
        "videoStreams": [],
        "relatedStreams": []
    }
    return JSONResponse(content=result)
