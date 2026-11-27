"""用例：摊平 → 排序 → 模型写一页纸 → 数字守卫。"""

from __future__ import annotations

import json
from pathlib import Path

from ..config import Settings
from ..domain.engine import build, table
from ..domain.guard import check
from ..domain.models import Board
from ..ports import LLMPort, StorePort

PROMPT = (Path(__file__).resolve().parents[2] / "prompts" / "note.md").read_text(encoding="utf-8")


def board(store: StorePort) -> Board:
    return build(store.list_offers(), store.weights())


def note(store: StorePort, settings: Settings, llm: LLMPort | None = None) -> tuple[str, list[str]]:
    b = board(store)
    if llm is None:
        return "", []
    facts = [table(b)] + [f"{k}={v}" for k, v, _ in store.list_assumptions()]
    try:
        data = json.loads(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, [table(b), *facts])]


def assumptions(store: StorePort) -> list[str]:
    return [f"{k} = {v}（{why}）" if why else f"{k} = {v}" for k, v, why in store.list_assumptions()]
