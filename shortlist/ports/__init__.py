"""端口：app 实际调用的方法集合，实现见 adapters。"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain.models import Offer, Weights


@runtime_checkable
class StorePort(Protocol):
    def list_offers(self) -> list[Offer]: ...

    def weights(self) -> Weights: ...

    def list_assumptions(self) -> list[tuple[str, str, str]]: ...


@runtime_checkable
class LLMPort(Protocol):
    def write(self, system: str, facts: str) -> str: ...
