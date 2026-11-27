"""真实内存 Store 跑 board：不建 SQLite，mypy 校验 StorePort。"""

from __future__ import annotations

from shortlist.app.run import board
from shortlist.domain.models import Offer, Weights
from shortlist.ports import StorePort


class InMemoryStore:
    def list_offers(self) -> list[Offer]:
        return []

    def weights(self) -> Weights:
        return Weights()

    def list_assumptions(self) -> list[tuple[str, str, str]]:
        return []


def test_board_with_memory_store() -> None:
    store: StorePort = InMemoryStore()
    out = board(store)
    assert out.rows == []
