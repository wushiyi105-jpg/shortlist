"""数字守卫：模型写的每个数都要能在输入里找到。"""

from __future__ import annotations

import re

from .models import Finding

PENALTY = 8
NUM = re.compile(r"(\d+(?:\.\d+)?)")


def allowed_numbers(*texts: object) -> set[str]:
    out: set[str] = set()
    for t in texts:
        for m in NUM.findall(str(t)):
            out.add(m.rstrip("0").rstrip(".") if "." in m else m)
            out.add(m)
    return out


def check(text: str, facts: list[object]) -> list[Finding]:
    ok = allowed_numbers(*facts)
    bad = [n for n in NUM.findall(text) if n.rstrip("0").rstrip(".") not in ok and n not in ok]
    if not bad:
        return []
    return [Finding("guard.number", f"稿里出现输入没有的数：{'、'.join(sorted(set(bad)))}，整句删掉", PENALTY, ",".join(sorted(set(bad))))]
