"""Serve the demo UI from the frontend/ directory."""

from pathlib import Path

from fastapi.responses import FileResponse

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend"

# Demo app pages only — no marketing landing pages
APP_PAGES: list[tuple[str, str]] = [
    ("/", "index.html"),
    ("/tryon", "tryon.html"),
    ("/admin", "admin.html"),
]


def register_frontend_routes(app) -> None:
    """Mount static assets and register HTML page routes on the FastAPI app."""
    if not FRONTEND_DIR.exists():
        return

    from fastapi.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    for route, filename in APP_PAGES:
        html_path = FRONTEND_DIR / filename

        def _make_handler(path=html_path):
            async def handler():
                return FileResponse(str(path))
            return handler

        app.add_api_route(route, _make_handler(), methods=["GET"], include_in_schema=False)
