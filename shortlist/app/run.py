"""用例：摊平 → 排序 → 模型写一页纸 → 数字守卫。"""

from __future__ import annotations

import json

from ..adapters.llm import build_llm
from ..adapters.store import SqliteStore
from ..config import Settings
from ..domain.engine import build, table
from ..domain.guard import check
from ..domain.models import Board

PROMPT = """把给出的一页纸写成五句以内，只能用输入里的数字，不要新造任何比例或金额。
输出 JSON：{"text": "…"}"""


def board(store: SqliteStore) -> Board:
    return build(store.list_offers(), store.weights())


def note(store: SqliteStore, settings: Settings) -> tuple[str, list[str]]:
    b = board(store)
    if not settings.llm_enabled:
        return "", []
    facts = [table(b)] + [f"{k}={v}" for k, v, _ in store.list_assumptions()]
    llm = build_llm(settings.llm_base_url, settings.llm_api_key, settings.llm_model, PROMPT)
    try:
        data = json.loads(llm.write(PROMPT, "\n".join(facts)))
    except Exception:  # noqa: BLE001
        return "", []
    text = str(data.get("text", ""))
    return text, [f.message for f in check(text, [table(b), *facts])]


def assumptions(store: SqliteStore) -> list[str]:
    return [f"{k} = {v}（{why}）" if why else f"{k} = {v}" for k, v, why in store.list_assumptions()]
