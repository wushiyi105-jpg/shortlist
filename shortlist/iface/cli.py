"""命令行：seed / board / note / doctor / serve。"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ..adapters.llm import build_llm
from ..adapters.notify import WebhookNotifier
from ..adapters.store import SqliteStore
from ..app.compare import build_report
from ..app.run import PROMPT, assumptions, board, note, table
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


def _notify(settings: Settings, text: str) -> None:
    if not text or not settings.webhook_url:
        return
    ok = WebhookNotifier(settings.webhook_url).send(text)
    console.print(f"[dim]webhook {'ok' if ok else 'failed'}[/]")


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


@app.command("board")
def board_cmd(db: Path = typer.Option(None)) -> None:
    """摊平表与扣分。"""
    store = _store(_settings(db))
    b = board(store)
    console.print(table(b))
    for f in b.findings:
        console.print(f"  [yellow]{f.rule_id}[/] -{f.penalty} {f.message}")
    console.print(f"合计扣 {b.penalty_total} 分")


@app.command()
def compare(
    city: str = typer.Option("深圳", help="北京/上海/深圳/杭州/成都/广州/南京/武汉"),
    out: Path = typer.Option(None, help="输出 Markdown；不填打印到终端"),
    db: Path = typer.Option(None),
) -> None:
    """一张对比表 + 5 个该问 HR 的问题，导出就能转发。"""
    store = _store(_settings(db))
    offers = store.list_offers()
    if not offers:
        console.print("[red]还没有 offer，先跑 seed 或加一条[/]")
        raise typer.Exit(code=2)
    try:
        body = build_report(board(store), offers, city)
    except ValueError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=2) from exc
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body, encoding="utf-8")
        console.print(f"[green]已写出[/] {out}（{len(body.splitlines())} 行）")
    else:
        console.print(body)


@app.command("note")
def note_cmd(db: Path = typer.Option(None)) -> None:
    """模型写一页纸（无 key 时打印假设）。"""
    s = _settings(db)
    store = _store(s)
    llm = build_llm(s.llm_base_url, s.llm_api_key, s.llm_model, PROMPT) if s.llm_enabled else None
    text, notes = note(store, s, llm)
    body: list[str] = []
    if text:
        console.print(text)
        body.append(text)
    for n in notes:
        console.print(f"  [yellow]{n}[/]")
        body.append(n)
    if not text:
        for line in assumptions(store):
            console.print(line)
            body.append(line)
    _notify(s, "\n".join(body))


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
