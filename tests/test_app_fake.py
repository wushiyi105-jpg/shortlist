"""主用例只依赖 ports：用 MagicMock 内存假实现，不建 SQLite 文件。"""

from __future__ import annotations

from unittest.mock import MagicMock

from shortlist.app.run import board
from shortlist.ports import StorePort


def test_main_path_with_memory_store(tmp_path) -> None:
    store = MagicMock(spec=StorePort)
    from shortlist.domain.models import Weights
    store.list_offers.return_value = []
    store.weights.return_value = Weights()
    
    out = board(store)
    assert out is not None
    assert not (tmp_path / "app.db").exists()
