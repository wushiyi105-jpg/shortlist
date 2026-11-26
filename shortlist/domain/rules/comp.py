"""年化与时薪：奖金算进去，周工作天数折算工时。"""

from __future__ import annotations

from ..models import HOURS_PER_DAY, WORK_DAYS, Offer


def annual(offer: Offer) -> float:
    if offer.base < 0 or offer.bonus < 0:
        raise ValueError("薪酬不能为负")
    return offer.base + offer.bonus


def hours(offer: Offer) -> float:
    if not 1 <= offer.days_per_week <= 7:
        raise ValueError("每周工作天数要在 1-7")
    return WORK_DAYS * HOURS_PER_DAY * offer.days_per_week / 5.0


def hourly(offer: Offer) -> float:
    return annual(offer) / hours(offer)


def cost_of(offer: Offer) -> float:
    """通勤时间按本人时薪折成钱，加上房租差。"""
    commute_hours = offer.commute_min / 60.0 * 2 * WORK_DAYS
    return round(commute_hours * hourly(offer) * 0.5 + offer.rent_delta, 2)
