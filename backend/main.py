import subprocess
import sys
import os
import httpx
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
import websockets

from backend.routers import inflation

STREAMLIT_PORT = 8501
STREAMLIT_URL = f"http://localhost:{STREAMLIT_PORT}"
STREAMLIT_WS  = f"ws://localhost:{STREAMLIT_PORT}"
FRONTEND_APP  = Path(__file__).resolve().parent.parent / "frontend" / "app.py"

streamlit_process = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global streamlit_process
    streamlit_process = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run",
            str(FRONTEND_APP),
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", "localhost",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--server.allowRunOnSave", "false",
            "--browser.gatherUsageStats", "false",
            # Allow all origins for WebSocket
            "--server.enableWebsocketCompression", "false",
        ],
        env={**os.environ, "API_BASE": "http://localhost:8000/api"}
    )
    print(f"Streamlit started (pid {streamlit_process.pid})")
    yield
    if streamlit_process:
        streamlit_process.terminate()


app = FastAPI(
    title="India Inflation Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST API ──────────────────────────────────────────────────────────────────
app.include_router(inflation.router, prefix="/api", tags=["inflation"])

@app.get("/api")
def api_root():
    return {"message": "India Inflation Dashboard API", "docs": "/docs"}


# ── WebSocket proxy → Streamlit ───────────────────────────────────────────────
@app.websocket("/{path:path}")
async def websocket_proxy(client_ws: WebSocket, path: str):
    await client_ws.accept()
    target = f"{STREAMLIT_WS}/{path}"
    if client_ws.query_string:
        target += f"?{client_ws.query_string.decode()}"
    try:
        async with websockets.connect(
            target,
            extra_headers={"Host": f"localhost:{STREAMLIT_PORT}"},
            max_size=None,
        ) as server_ws:
            import asyncio

            async def client_to_server():
                try:
                    while True:
                        data = await client_ws.receive_bytes()
                        await server_ws.send(data)
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


# ── HTTP proxy → Streamlit ────────────────────────────────────────────────────
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
