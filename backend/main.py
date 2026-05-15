import subprocess
import sys
import os
import httpx
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import inflation

STREAMLIT_PORT = 8501
STREAMLIT_URL = f"http://localhost:{STREAMLIT_PORT}"
FRONTEND_APP = Path(__file__).resolve().parent.parent / "frontend" / "app.py"

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
            "--browser.gatherUsageStats", "false",
        ],
        env={**os.environ, "API_BASE": "http://localhost:8000/api"}
    )
    print(f"Streamlit started (pid {streamlit_process.pid})")
    yield
    if streamlit_process:
        streamlit_process.terminate()


app = FastAPI(
    title="India Inflation Dashboard",
    description="CPI analysis — API + Dashboard on a single port",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inflation.router, prefix="/api", tags=["inflation"])


@app.get("/api")
def api_root():
    return {
        "message": "India Inflation Dashboard API",
        "docs": "/docs",
        "endpoints": ["/api/summary", "/api/trend", "/api/annual",
                      "/api/heatmap", "/api/categories"]
    }


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    include_in_schema=False,
)
async def proxy_to_streamlit(request: Request, path: str):
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
                content="Dashboard is starting up, please refresh in a moment...",
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
