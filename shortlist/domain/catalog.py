"""本地假设：8 城社保/租金、个税档、HR 问题。"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parents[2] / "data"


def _load() -> dict[str, Any]:
    return json.loads((DATA / "city_costs.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def city_costs() -> dict[str, Any]:
    return _load()


def city(name: str) -> dict[str, Any]:
    for c in city_costs()["cities"]:
        if c["name"] == name:
            return c
    names = "、".join(c["name"] for c in city_costs()["cities"])
    raise ValueError(f"没有 {name} 的数据，可选：{names}")


def tax_brackets() -> list[dict[str, Any]]:
    return city_costs()["tax_brackets"]


def employee_rates() -> dict[str, float]:
    return city_costs()["employee_rates"]


def hr_questions() -> list[str]:
    return city_costs()["hr_questions"]
