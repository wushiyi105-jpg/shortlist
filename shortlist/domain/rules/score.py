"""加权排名：薪酬、成长、成本三项，权重必须凑满 1。"""

from __future__ import annotations

from ..models import Finding, Weights

PENALTY = 6
TOLERANCE = 1e-6


def check(weights: Weights) -> list[Finding]:
    if abs(weights.total - 1.0) > TOLERANCE:
        return [
            Finding(
                "weights.sum",
                f"权重合计 {weights.total:.2f}，不是 1，排名不可比",
                PENALTY,
                "weights",
            )
        ]
    if min(weights.pay, weights.growth, weights.cost) < 0:
        return [Finding("weights.sum", "权重不能为负", PENALTY, "weights")]
    return []


def norm(values: list[float]) -> list[float]:
    hi = max(values) if values else 0.0
    if hi <= 0:
        return [0.0 for _ in values]
    return [v / hi for v in values]
