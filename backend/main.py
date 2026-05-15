import subprocess
import sys
import os
import asyncio
import httpx
import websockets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import inflation

STREAMLIT_PORT = 8501
STREAMLIT_URL  = f"http://localhost:{STREAMLIT_PORT}"
STREAMLIT_WS   = f"ws://localhost:{STREAMLIT_PORT}"
FRONTEND_APP   = Path(__file__).resolve().parent.parent / "frontend" / "app.py"


@asynccontextmanager
async def lifespan(app: FastAPI):
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            str(FRONTEND_APP),
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", "localhost",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false",
        ],
        env={**os.environ, "API_BASE": "http://localhost:8000/api"}
    )
    print(f"Streamlit started (pid {proc.pid})")
    yield
    proc.terminate()


app = FastAPI(title="India Inflation Dashboard", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inflation.router, prefix="/api", tags=["inflation"])

@app.get("/api")
def api_root():
    return {"message": "India Inflation Dashboard API", "docs": "/docs"}


# ── WebSocket proxy ───────────────────────────────────────────────────────────
@app.websocket("/{path:path}")
async def websocket_proxy(client_ws: WebSocket, path: str):
    await client_ws.accept()

    qs = client_ws.scope.get("query_string", b"").decode()
    target = f"{STREAMLIT_WS}/{path}"
    if qs:
        target += f"?{qs}"

    # Forward all original headers — Streamlit needs Origin to match
    forward_headers = [
        (k.decode(), v.decode())
        for k, v in client_ws.scope.get("headers", [])
        if k.lower() not in (b"host",)
    ]
    # Override host to point to local streamlit
    forward_headers.append(("Host", f"localhost:{STREAMLIT_PORT}"))
    forward_headers.append(("Origin", f"http://localhost:{STREAMLIT_PORT}"))

    try:
        async with websockets.connect(
            target,
            extra_headers=forward_headers,
            max_size=None,
            open_timeout=10,
        ) as server_ws:

            async def client_to_server():
                try:
                    while True:
                        msg = await client_ws.receive()
                        if msg.get("bytes"):
                            await server_ws.send(msg["bytes"])
                        elif msg.get("text"):
                            await server_ws.send(msg["text"])
                        elif msg.get("type") == "websocket.disconnect":
                            break
                except Exception:
                    pass

            async def server_to_client():
                try:
                    async for msg in server_ws:
                        if isinstance(msg, bytes):
                            await client_ws.send_bytes(msg)
                        else:
                            await client_ws.send_text(msg)
                except Exception:
                    pass

            await asyncio.gather(client_to_server(), server_to_client())

    except Exception as e:
        print(f"WS proxy error: {e}")
    finally:
        try:
            await client_ws.close()
        except Exception:
            pass


# ── HTTP proxy ────────────────────────────────────────────────────────────────
@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    include_in_schema=False,
)
async def http_proxy(request: Request, path: str):
    target_url = f"{STREAMLIT_URL}/{path}"
    if str(request.url.query):
        target_url += f"?{request.url.query}"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            proxy_resp = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items()
                         if k.lower() not in ("host", "content-length")},
                content=await request.body(),
                follow_redirects=True,
            )
        except httpx.ConnectError:
            return Response(
                content="Dashboard starting up, please refresh in a few seconds...",
                status_code=503,
                media_type="text/plain"
            )

    skip = {"transfer-encoding", "content-encoding", "content-length", "connection"}
    headers = {k: v for k, v in proxy_resp.headers.items() if k.lower() not in skip}

    return StreamingResponse(
        content=iter([proxy_resp.content]),
        status_code=proxy_resp.status_code,
        headers=headers,
        media_type=proxy_resp.headers.get("content-type"),
    )
