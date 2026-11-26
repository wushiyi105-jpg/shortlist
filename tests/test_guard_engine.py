from __future__ import annotations

from shortlist.domain.engine import build, table
from shortlist.domain.guard import check
from shortlist.domain.models import Offer, Weights


def _offers() -> list[Offer]:
    return [
        Offer(1, "甲", 260000, 40000, 5, 55, 1800, 0, 0.0, 0.0, 0.45),
        Offer(2, "乙", 220000, 0, 5, 25, 0, 8000, 12.0, 30.0, 0.7),
        Offer(3, "丙", 195000, 25000, 4.5, 80, 2600, 0, 0.0, 0.0, 0.3),
    ]


def test_board_rows_sorted():
    b = build(_offers(), Weights())
    assert len(b.rows) == 3
    assert b.rows[0].score >= b.rows[-1].score


def test_cost_finding_for_long_commute():
    b = build(_offers(), Weights())
    assert any(f.rule_id == "offer.cost" for f in b.findings)


def test_weights_finding_on_board():
    b = build(_offers(), Weights(0.6, 0.3, 0.3))
    assert any(f.rule_id == "weights.sum" for f in b.findings)


def test_table_has_header():
    assert table(build(_offers(), Weights())).splitlines()[0].startswith("公司")


def test_guard_drops_invented_number():
    b = build(_offers(), Weights())
    findings = check("涨幅 37%，闭眼选乙", [table(b)])
    assert findings and findings[0].rule_id == "guard.number"


def test_guard_accepts_number_from_facts():
    b = build(_offers(), Weights())
    findings = check("年化 300000 最高", [table(b), "300000"])
    assert findings == []
