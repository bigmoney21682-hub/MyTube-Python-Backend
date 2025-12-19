import httpx

def proxy_stream(url: str):
    client = httpx.stream("GET", url)
    for chunk in client.iter_bytes():
        yield chunk
