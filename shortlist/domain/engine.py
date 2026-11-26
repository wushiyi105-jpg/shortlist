"""本地核算：逐家年化、时薪、成本、加权分。"""

from __future__ import annotations

from .models import Board, Finding, Offer, Row, Weights
from .rules.comp import annual, cost_of, hourly
from .rules.equity import check as equity_check
from .rules.equity import value
from .rules.score import check as weights_check
from .rules.score import norm


def build(offers: list[Offer], weights: Weights) -> Board:
    b = Board()
    aes = [annual(o) for o in offers]
    costs = [cost_of(o) for o in offers]
    growths = [o.growth for o in offers]
    eqs = []
    for o in offers:
        try:
            eqs.append(value(o))
        except ValueError:
            from .models import Equity

            eqs.append(Equity(0, 0.0, {"归零": 0.0, "半价退出": 0.0, "按优先价退出": 0.0}))
    na, nc, ng = norm(aes), norm(costs), norm(growths)
    ne = norm([e.expected for e in eqs])
    findings: list[Finding] = []
    findings += weights_check(weights)
    findings += equity_check(offers)
    for o in offers:
        if o.commute_min > 60:
            findings.append(
                Finding(
                    "offer.cost",
                    f"{o.company} 单程通勤 {o.commute_min} 分钟，每天来回超过 2 小时",
                    4,
                    o.company,
                )
            )
    for i, o in enumerate(offers):
        score = (
            na[i] * weights.pay
            + ng[i] * weights.growth
            + (1 - nc[i]) * weights.cost
            + ne[i] * 0.1
        )
        b.rows.append(Row(o.company, round(aes[i], 2), round(hourly(o), 2), costs[i], eqs[i], round(score, 3)))
    b.findings = findings
    b.rows.sort(key=lambda r: r.score, reverse=True)
    return b


def table(b: Board) -> str:
    lines = ["公司 | 年化 | 时薪 | 成本 | 期权期望 | 分"]
    for r in b.rows:
        lines.append(
            f"{r.company} | {r.annual:,.0f} | {r.hourly:,.0f} | {r.cost:,.0f} | {r.equity.expected:,.0f} | {r.score:.3f}"
        )
    return "\n".join(lines)
