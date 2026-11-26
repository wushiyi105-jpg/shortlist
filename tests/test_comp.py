from __future__ import annotations

import pytest

from shortlist.domain.models import Offer
from shortlist.domain.rules.comp import annual, cost_of, hourly, hours


def _o(**kw) -> Offer:
    base = dict(id=1, company="甲", base=200000, bonus=20000)
    base.update(kw)
    return Offer(**base)


def test_annual_includes_bonus():
    assert annual(_o()) == 220000


def test_negative_base_raises():
    with pytest.raises(ValueError):
        annual(_o(base=-1))


def test_hours_five_days():
    assert hours(_o()) == 2000.0


def test_hours_four_and_half_days():
    assert hours(_o(days_per_week=4)) == 1600.0


def test_bad_days_raises():
    with pytest.raises(ValueError):
        hours(_o(days_per_week=0))


def test_hourly_and_cost():
    o = _o(commute_min=60, rent_delta=0)
    assert hourly(o) == 110.0
    assert cost_of(o) == 250 * 2 * 110.0 * 0.5
