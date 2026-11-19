# GSB Bugfix Task
## 题面
新手池上线当天就有人连续九十抽没有出稀有，保底计数像是没生效；另一批玩家歪了之后下一发却不是当期，客服补偿口径完全对不上。loot_pity.py 的 LootPity 用 hard_pity、soft_pity、base_rate 与 guarantee 开关构造，玩家先 register 才能抽。draw(player, roll, flip) 两个参数都取零到一的浮点数，roll 决定是否出稀有，flip 决定稀有是否算当期；累计抽数达到 soft_pity 后每抽让出率增加零点零六，到达 hard_pity 时不管 roll 多大都强制出稀有。出过稀有后计数器归零，若 flip 判定为歪且大保底开启，下一次稀有必定是当期。返回值含 rare、featured、counter、guaranteed、pulls 五个字段。roll 或 flip 越界、重复注册、未注册玩家抽卡都抛 ValueError，构造时 soft_pity 必须小于 hard_pity。

## 运行方式
```bash
python -m pytest tests -q
```

## 平台字段

所属领域：安全
子方向：游戏开发
任务类型：Bugfix
语言 / 框架：Python 3, pytest
环境可复现等级：有外部依赖，未容器化
