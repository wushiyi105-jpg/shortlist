"""Offer 对比成文：到手、可支配、期权三档、5 个 HR 问题。"""

from __future__ import annotations

from ..domain.catalog import city as city_data
from ..domain.catalog import employee_rates, hr_questions, tax_brackets
from ..domain.models import Board, Offer, Row


def _tax(monthly_taxable: float) -> float:
    if monthly_taxable <= 0:
        return 0.0
    for b in tax_brackets():
        up = b["up_to"]
        if up is None or monthly_taxable <= up:
            return monthly_taxable * b["rate"] - b["quick"]
    return 0.0


def _pay(offer: Offer, city_name: str) -> tuple[float, float, float, float, float, float]:
    c = city_data(city_name)
    gross = offer.base + offer.bonus
    monthly = gross / 12
    social_base = min(max(monthly, c["social_min"]), c["social_max"])
    rates = employee_rates()
    employee_monthly = social_base * (
        rates["pension"] + rates["medical"] + rates["unemployment"] + c["housing_rate"]
    )
    taxable = max(0.0, monthly - employee_monthly - 5000)
    tax_monthly = _tax(taxable)
    net = gross - (employee_monthly + tax_monthly) * 12
    rent = c["rent"] * 12 + offer.rent_delta * 12
    commute = c["commute"] * 12
    return gross, employee_monthly * 12, tax_monthly * 12, net, rent, commute


def build_report(board: Board, offers: list[Offer], city_name: str) -> str:
    c = city_data(city_name)
    by_name = {o.company: o for o in offers}
    lines = [
        f"# Offer 对比 · {city_name}",
        "",
        f"> 社保基数 {c['social_min']:,}–{c['social_max']:,} 元/月，公积金个人 {c['housing_rate']:.0%}；"
        f"一居室租金按 {c['rent']:,} 元/月、通勤 {c['commute']:,} 元/月估算。",
        "> 个税按月度速算乘 12，年终奖并入当年，不做累计预扣；这是比较口径，不是报税口径。",
        "",
        "## 一、摊平到年",
        "",
        "| 公司 | 年化 | 五险一金/年 | 个税/年 | 到手/年 | 房租/年 | 通勤/年 | 可支配/年 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    rows: list[tuple[Row, Offer, tuple[float, float, float, float, float, float]]] = []
    for r in board.rows:
        o = by_name[r.company]
        pay = _pay(o, city_name)
        rows.append((r, o, pay))
        lines.append(
            f"| {r.company} | {pay[0]:,.0f} | {pay[1]:,.0f} | {pay[2]:,.0f} | {pay[3]:,.0f} | "
            f"{pay[4]:,.0f} | {pay[5]:,.0f} | {pay[3] - pay[4] - pay[5]:,.0f} |"
        )

    lines += [
        "",
        "## 二、加权排名",
        "",
        "| 名次 | 公司 | 分 | 时薪 | 通勤成本/年 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, r in enumerate(board.rows, 1):
        lines.append(f"| {i} | {r.company} | {r.score:.3f} | {r.hourly:,.0f} | {r.cost:,.0f} |")

    lines += [
        "",
        "## 三、期权三档（不是承诺，是三个情景）",
        "",
        "| 公司 | 股数 | 行权价 | 归零 | 半价退出 | 按优先价退出 | 三档平均 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in board.rows:
        e = r.equity
        if e.count <= 0:
            continue
        lines.append(
            f"| {r.company} | {e.count:,} | {e.strike:g} | {e.scenarios['归零']:,.0f} | "
            f"{e.scenarios['半价退出']:,.0f} | {e.scenarios['按优先价退出']:,.0f} | {e.expected:,.0f} |"
        )
    if not any(r.equity.count > 0 for r in board.rows):
        lines.append("| 无 | 0 | 0 | 0 | 0 | 0 | 0 |")

    lines += ["", "## 四、该问 HR 的 5 个问题", ""]
    lines += [f"{i}. {q}" for i, q in enumerate(hr_questions(), 1)]

    lines += [
        "",
        "## 五、假设清单（每个数字能追到这里）",
        "",
        f"- 社保下限 {c['social_min']:,}、上限 {c['social_max']:,}，来自 `data/city_costs.json` 的 {city_name} 行。",
        f"- 个人费率：养老 {employee_rates()['pension']:.0%}、医疗 {employee_rates()['medical']:.0%}、"
        f"失业 {employee_rates()['unemployment']:.1%}、公积金 {c['housing_rate']:.0%}。",
        f"- 房租 {c['rent']:,} 元/月、通勤 {c['commute']:,} 元/月；offer 里的 `rent_delta` 已叠加。",
        "- 个税：月度速算（3%–45% 七档，含速算扣除数），乘 12；未计专项附加扣除。",
        "- 工作天数按 250 天/年，时薪 = 年化 / 实际工时。",
        "- 期权三档：归零 0、半价退出 50%、按优先价退出 90%；期望值只作排序，不承诺。",
        "",
        "---",
        "",
        f"口径说明：不同城市的社保基数和租金会改变结论，换城市请重跑 `compare --city`。"
        f"本报告共 {len(board.rows)} 个 offer、{len(rows)} 行摊平数据。",
        "",
    ]
    return "\n".join(lines)
