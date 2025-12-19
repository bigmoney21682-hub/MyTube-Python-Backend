import yt_dlp

async def search_videos(query: str):
    ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch10:{query}", download=False)
        videos = []
        for entry in result.get("entries", []):
            videos.append({
                "id": entry.get("id"),
                "title": entry.get("title"),
                "thumbnail": entry.get("thumbnail"),
                "uploaderName": entry.get("uploader"),
                "views": entry.get("view_count"),
                "duration": entry.get("duration")
            })
        return videos

async def get_video_stream(video_id: str):
    ydl_opts = {"quiet": True, "format": "best"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return info["url"]
