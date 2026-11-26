"""领域对象：offer、假设、三档估值、加权排名。"""

from __future__ import annotations

from dataclasses import dataclass, field

WORK_DAYS = 250
HOURS_PER_DAY = 8.0


@dataclass(frozen=True)
class Offer:
    id: int
    company: str
    base: float
    bonus: float
    days_per_week: int = 5
    commute_min: int = 0
    rent_delta: float = 0.0
    options: int = 0
    strike: float = 0.0
    preferred_price: float = 0.0
    growth: float = 0.5
    note: str = ""


@dataclass(frozen=True)
class Weights:
    pay: float = 0.5
    growth: float = 0.3
    cost: float = 0.2

    @property
    def total(self) -> float:
        return self.pay + self.growth + self.cost


@dataclass
class Equity:
    count: int
    strike: float
    scenarios: dict[str, float]

    @property
    def expected(self) -> float:
        return sum(self.scenarios.values()) / max(1, len(self.scenarios))


@dataclass
class Row:
    company: str
    annual: float
    hourly: float
    cost: float
    equity: Equity
    score: float


@dataclass
class Finding:
    rule_id: str
    message: str
    penalty: int
    target: str = ""


@dataclass
class Board:
    rows: list[Row] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def penalty_total(self) -> int:
        return sum(f.penalty for f in self.findings)
