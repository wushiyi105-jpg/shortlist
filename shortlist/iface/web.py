"""FastAPI + Jinja2：对比表。"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..adapters.store import SqliteStore
from ..app.run import assumptions, board
from ..config import Settings

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


def create_app(settings: Settings, store: SqliteStore | None = None) -> FastAPI:
    app = FastAPI(title="Shortlist", version="1.0.0")
    app.mount(
        "/static",
        StaticFiles(directory=str(Path(__file__).resolve().parents[2] / "static")),
        name="static",
    )
    store = store or SqliteStore(settings.db_path)

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        b = board(store)
        return TEMPLATES.TemplateResponse(
            request, "index.html",
            {"b": b, "weights": store.weights(), "assumptions": assumptions(store)},
        )

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "offers": len(store.list_offers())}

    return app


def app_factory(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        from ..config import settings as default_settings

        settings = default_settings
    return create_app(settings)

