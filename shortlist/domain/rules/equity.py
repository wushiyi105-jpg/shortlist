"""期权三档：归零、半价、按优先股价格出。"""

from __future__ import annotations

from ..models import Equity, Finding, Offer

PENALTY_ASSUMPTION = 3
PENALTY_STRIKE = 5
SCENARIO = {"归零": 0.0, "半价退出": 0.5, "按优先价退出": 0.9}


def value(offer: Offer) -> Equity:
    if offer.options <= 0:
        return Equity(0, offer.strike, {k: 0.0 for k in SCENARIO})
    if offer.strike <= 0:
        raise ValueError("写了期权却没写行权价")
    out: dict[str, float] = {}
    for name, mult in SCENARIO.items():
        price = offer.preferred_price * mult
        per = max(0.0, price - offer.strike)
        out[name] = round(per * offer.options, 2)
    return Equity(offer.options, offer.strike, out)


def check(offers: list[Offer]) -> list[Finding]:
    out: list[Finding] = []
    for o in offers:
        if o.options > 0 and o.strike <= 0:
            out.append(
                Finding("equity.assumption", f"{o.company} 的期权没填行权价，按 0 算", PENALTY_ASSUMPTION, o.company)
            )
        elif o.options > 0 and o.strike >= o.preferred_price:
            out.append(
                Finding(
                    "equity.strike_high",
                    f"{o.company} 行权价 {o.strike:g} 不低于优先价 {o.preferred_price:g}，三档全是 0",
                    PENALTY_STRIKE,
                    o.company,
                )
            )
    return out
