from __future__ import annotations

from shortlist.domain.models import Offer, Weights
from shortlist.domain.rules.equity import check, value
from shortlist.domain.rules.score import check as w_check
from shortlist.domain.rules.score import norm


def _opt(**kw) -> Offer:
    base = dict(id=1, company="甲", base=200000, bonus=0, options=5000, strike=12, preferred_price=30)
    base.update(kw)
    return Offer(**base)


def test_three_scenarios():
    e = value(_opt())
    assert e.scenarios["归零"] == 0.0
    assert e.scenarios["半价退出"] == 5000 * (15 - 12)


def test_expected_is_mean():
    e = value(_opt())
    assert e.expected == sum(e.scenarios.values()) / 3


def test_strike_above_preferred_all_zero():
    e = value(_opt(strike=35))
    assert all(v == 0 for v in e.scenarios.values())


def test_missing_strike_flagged():
    findings = check([_opt(strike=0)])
    assert findings[0].rule_id == "equity.assumption"


def test_strike_high_flagged():
    findings = check([_opt(strike=30)])
    assert findings[0].rule_id == "equity.strike_high"


def test_no_options_no_finding():
    assert check([_opt(options=0)]) == []


def test_weights_must_sum_one():
    assert w_check(Weights(0.5, 0.3, 0.3))[0].rule_id == "weights.sum"
    assert w_check(Weights(0.5, 0.3, 0.2)) == []


def test_norm_handles_zero():
    assert norm([0, 0]) == [0.0, 0.0]
