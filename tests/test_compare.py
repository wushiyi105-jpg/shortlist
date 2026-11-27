"""Offer 对比报告：8 城口径、期权三档、5 个 HR 问题。"""

from __future__ import annotations

import pytest

from shortlist.app.compare import build_report
from shortlist.domain.engine import build
from shortlist.domain.models import Offer, Weights


def test_report_contains_pay_and_questions() -> None:
    offers = [
        Offer(1, "甲公司", 240000, 36000, 5, 30, 0, growth=0.6),
        Offer(2, "乙公司", 200000, 0, 5, 80, 2000, options=5000, strike=10, preferred_price=25, growth=0.4),
    ]
    text = build_report(build(offers, Weights()), offers, "深圳")
    assert "# Offer 对比 · 深圳" in text
    assert "社保基数 4,492–32,376" in text
    assert text.count("该问 HR 的 5 个问题") == 1
    assert "五险一金/年" in text
    assert "半价退出" in text
    assert "假设清单" in text


def test_report_unknown_city() -> None:
    offers = [Offer(1, "甲", 200000, 0, 5, 20, 0)]
    with pytest.raises(ValueError, match="没有 拉萨"):
        build_report(build(offers, Weights()), offers, "拉萨")


def test_report_equity_zero_still_lists() -> None:
    offers = [Offer(1, "甲", 200000, 0, 5, 20, 0)]
    text = build_report(build(offers, Weights()), offers, "成都")
    assert "| 无 | 0 | 0 | 0 | 0 | 0 | 0 |" in text
