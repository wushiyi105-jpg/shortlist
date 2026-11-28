from __future__ import annotations

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from shortlist.adapters.store import SqliteStore
from shortlist.doctor import run_doctor
from shortlist.iface.cli import app
from shortlist.iface.web import create_app


def _seed(store: SqliteStore):
    store.add_offer("甲", 260000, 40000, commute_min=55, growth=0.45)
    store.add_offer("乙", 220000, 0, options=8000, strike=12, preferred_price=30, growth=0.7)
    store.set_assumption("pay", "0.5")
    store.set_assumption("growth", "0.3")
    store.set_assumption("cost", "0.2")


def test_index(store, settings):
    _seed(store)
    client = TestClient(create_app(settings, store))
    body = client.get("/").text
    assert client.get("/").status_code == 200
    assert "摊开的录用信" in body


def test_index_without_offers(store, settings):
    assert TestClient(create_app(settings, store)).get("/").status_code == 200


def test_cli_board_and_negative(tmp_path):
    runner = CliRunner()
    db = str(tmp_path / "c.db")
    assert runner.invoke(app, ["board", "--db", db]).exit_code == 0
    assert runner.invoke(app, ["note", "--db", db]).exit_code == 0


def test_doctor_green(settings):
    checks, ok = run_doctor(settings)
    assert ok is True

