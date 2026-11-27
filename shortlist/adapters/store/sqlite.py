"""SQLite：offers / assumptions / jobs。"""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Float, Integer, String, inspect, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker
from sqlalchemy.orm import Session as OrmSession

from ...domain.models import Offer, Weights
from .base import Base, make_engine, make_session


class OfferRow(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(60))
    base: Mapped[float] = mapped_column(Float)
    bonus: Mapped[float] = mapped_column(Float, default=0.0)
    days_per_week: Mapped[int] = mapped_column(Integer, default=5)
    commute_min: Mapped[int] = mapped_column(Integer, default=0)
    rent_delta: Mapped[float] = mapped_column(Float, default=0.0)
    options: Mapped[int] = mapped_column(Integer, default=0)
    strike: Mapped[float] = mapped_column(Float, default=0.0)
    preferred_price: Mapped[float] = mapped_column(Float, default=0.0)
    growth: Mapped[float] = mapped_column(Float, default=0.5)
    note: Mapped[str] = mapped_column(String(200), default="")


class AssumptionRow(Base):
    __tablename__ = "assumptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(60), unique=True)
    value: Mapped[str] = mapped_column(String(120))
    why: Mapped[str] = mapped_column(String(200), default="")


class JobRow(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    idem_key: Mapped[str] = mapped_column(String(80), unique=True)


def _upgrade_schema(engine) -> None:
    root = next(p for p in Path(__file__).resolve().parents if (p / "alembic.ini").exists())
    cfg = Config(str(root / "alembic.ini"))
    cfg.set_main_option("script_location", str(root / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{engine.url.database}")
    command.upgrade(cfg, "head")


class SqliteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.engine = make_engine(self.path)
        self.session: sessionmaker[OrmSession] = make_session(self.engine)
        self.init_schema()

    def init_schema(self) -> None:
        _upgrade_schema(self.engine)

    def schema_ok(self) -> bool:
        return {"offers", "assumptions", "jobs"} <= set(inspect(self.engine).get_table_names())

    def summary(self) -> str:
        return f"{len(self.list_offers())} 个 offer、{len(self.list_assumptions())} 条假设"

    def add_offer(
        self,
        company: str,
        base: float,
        bonus: float = 0.0,
        days_per_week: int = 5,
        commute_min: int = 0,
        rent_delta: float = 0.0,
        options: int = 0,
        strike: float = 0.0,
        preferred_price: float = 0.0,
        growth: float = 0.5,
        note: str = "",
    ) -> int:
        if base < 0 or bonus < 0:
            raise ValueError("薪酬不能为负")
        with self.session() as s:
            row = OfferRow(
                company=company,
                base=base,
                bonus=bonus,
                days_per_week=days_per_week,
                commute_min=commute_min,
                rent_delta=rent_delta,
                options=options,
                strike=strike,
                preferred_price=preferred_price,
                growth=growth,
                note=note,
            )
            s.add(row)
            s.commit()
            return int(row.id)

    def list_offers(self) -> list[Offer]:
        with self.session() as s:
            rows = s.scalars(select(OfferRow)).all()
        return [
            Offer(r.id, r.company, float(r.base), float(r.bonus), r.days_per_week, r.commute_min,
                  float(r.rent_delta), r.options, float(r.strike), float(r.preferred_price), float(r.growth), r.note)
            for r in rows
        ]

    def set_assumption(self, key: str, value: str, why: str = "") -> int:
        with self.session() as s:
            old = s.scalars(select(AssumptionRow).where(AssumptionRow.key == key)).first()
            if old:
                old.value = value
                old.why = why
                s.commit()
                return int(old.id)
            row = AssumptionRow(key=key, value=value, why=why)
            s.add(row)
            s.commit()
            return int(row.id)

    def list_assumptions(self) -> list[tuple[str, str, str]]:
        with self.session() as s:
            rows = s.scalars(select(AssumptionRow)).all()
        return [(r.key, r.value, r.why) for r in rows]

    def weights(self) -> Weights:
        vals = {k: float(v) for k, v, _ in self.list_assumptions() if k in ("pay", "growth", "cost")}
        return Weights(vals.get("pay", 0.5), vals.get("growth", 0.3), vals.get("cost", 0.2))
