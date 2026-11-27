# 更新记录

## Unreleased

- 新增 8 城社保/公积金基数、租金通勤、个税七档与 5 个 HR 问题（`data/city_costs.json`）
- 新增 `compare` 命令：到手/可支配/期权三档/HR 问题一次成文，附完整假设清单
- `0001_init` 改为显式 `op.create_table` / `op.create_index`，运行期走 `alembic upgrade`
- `app/` 只依赖 `ports`，新增内存假实现用例
- 开 ruff `E2`/`E3`；CI 增加 `docker build` 与 `/health` 探活

## 1.0.0

- 年化与时薪折算
- 通勤与房租成本
- 期权三档估值
- 权重合计校验
- 数字守卫
