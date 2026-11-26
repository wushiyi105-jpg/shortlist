"""命令行：seed / board / note / doctor / serve。"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.store import SqliteStore
from ..app.run import assumptions, board, note, table
from ..config import Settings
from ..config import settings as default_settings
from ..doctor import main as doctor_main

app = typer.Typer(help="offer 对比：摊平再选", no_args_is_help=True)
console = Console()


def _settings(db: Path | None, port: int | None = None) -> Settings:
    s = default_settings.model_copy(deep=True)
    if db:
        s.db_path = db
    if port:
        s.port = port
    return s


def _store(settings: Settings) -> SqliteStore:
    return SqliteStore(settings.db_path)


@app.command()
def seed(db: Path = typer.Option(None)) -> None:
    """写入 offer 与权重假设。"""
    s = _settings(db)
    store = _store(s)
    data = json.loads(
        (Path(__file__).resolve().parents[2] / "data" / "seed.json").read_text(encoding="utf-8")
    )
    for o in data["offers"]:
        store.add_offer(
            o["company"], o["base"], o.get("bonus", 0.0),
            days_per_week=o.get("days_per_week", 5), commute_min=o.get("commute_min", 0),
            rent_delta=o.get("rent_delta", 0.0), options=o.get("options", 0),
            strike=o.get("strike", 0.0), preferred_price=o.get("preferred_price", 0.0),
            growth=o.get("growth", 0.5), note=o.get("note", ""),
        )
    for a in data.get("assumptions", []):
        store.set_assumption(a["key"], a["value"], a.get("why", ""))
    console.print(f"已写入 {len(data['offers'])} 个 offer")


@app.command()
def board_cmd(db: Path = typer.Option(None)) -> None:
    """摊平表与扣分。"""
    store = _store(_settings(db))
    b = board(store)
    console.print(table(b))
    for f in b.findings:
        console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")
    console.print(f"合计扣 {b.penalty_total} 分")


app.command(name="board")(board_cmd)


@app.command()
def note_cmd(db: Path = typer.Option(None)) -> None:
    """模型写一页纸（无 key 时打印假设）。"""
    s = _settings(db)
    store = _store(s)
    text, notes = note(store, s)
    if text:
        console.print(text)
    for n in notes:
        console.print(f"  [yellow]{n}[/]")
    if not text:
        for line in assumptions(store):
            console.print(line)


app.command(name="note")(note_cmd)


@app.command()
def doctor(db: Path = typer.Option(None)) -> None:
    """四项体检。"""
    raise typer.Exit(code=doctor_main(_settings(db)))


@app.command()
def serve(port: int = typer.Option(None), db: Path = typer.Option(None)) -> None:
    """Web 界面。"""
    import uvicorn

    from .web import create_app

    s = _settings(db, port)
    uvicorn.run(create_app(s), host="127.0.0.1", port=s.port)


if __name__ == "__main__":
    app()
