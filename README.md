# Shortlist · offer 对比

[![test](https://github.com/wushiyi105-jpg/shortlist/workflows/test/badge.svg)](https://github.com/wushiyi105-jpg/shortlist/actions)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

![示例](assets/demo.gif)

三个 offer 摊平成一张表：年化、时薪、通勤与房租成本、期权三档。

## 为什么不是比月薪

月薪 2 万加 4 万年终和月薪 2.2 万十四薪，谁高要看年化；单程 55 分钟和 25 分钟，一年差出一百多个小时；
期权写「8000 股」不写行权价，等于什么都没说。Shortlist 把这几项都换成钱，再按你自己定的权重排名。

## 它做什么

1. **年化**：底薪 + 奖金，不当成月薪乘 12。
2. **时薪**：按每周实际工作天数折算工时。
3. **成本**：通勤时间按本人时薪折半计价，加房租差。
4. **期权三档**：归零、半价退出、按优先价退出，取均值只作参考。
5. **加权排名**：薪酬 / 成长 / 成本三项，权重不凑满 1 就报警。

## 怎么用

```bash
pip install -e ".[dev]"
python -m shortlist seed
python -m shortlist board
python -m shortlist note
python -m shortlist serve        # http://127.0.0.1:8006
```

真实种子：恒锐（26 万 + 4 万奖金、单程 55 分钟、房租 +1800）、青禾（22 万、单程 25 分钟、8000 股期权
行权价 12、优先价 30）、北岸（19.5 万 + 2.5 万、四天半、单程 80 分钟、房租 +2600）；权重 0.5 / 0.3 / 0.2。

`board` 出来：青禾年化 22 万、时薪 110、成本 11,458、期权期望 48,000、分 0.914 排第一；恒锐年化 30 万
但时薪 150 只高 40 块、成本 36,175，分 0.726；北岸年化也是 22 万，成本 43,341 最高，分 0.495。
北岸单程 80 分钟，判一条 `offer.cost`，合计扣 4 分。

## 规则与扣分

| rule_id | 含义 | 扣分 |
| --- | --- | --- |
| `offer.cost` | 单程通勤 > 60 分钟 | 4 |
| `weights.sum` | 权重合计不等于 1 | 6 |
| `equity.assumption` | 有期权没行权价 | 3 |
| `equity.strike_high` | 行权价 ≥ 优先价，三档全 0 | 5 |
| `guard.number` | 模型稿里出现输入没有的数 | 8 |

## 边界

- 期权按面值粗算，不建模稀释与税；
- 成长分是自己打的，不是模型给的；
- 不替代和家人商量。

## 作者

shiyi · GitHub [@wushiyi105-jpg](https://github.com/wushiyi105-jpg) · wushiyi105@gmail.com
