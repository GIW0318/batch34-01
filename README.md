# GSB Bugfix Task
## 题面
体力系统改成按秒回复后，玩家开始卡体力：离线很久回来只回一格，花体力时没有先结算到当前时间，超过上限的回复被吞掉，负数消耗反而加体力，升级后上限变了但当前值没截断。energy_regen.py 的 EnergyPool 负责 spend、current 和 state。实现要按上次结算时间累积回复、支持部分进度、达到上限停止、消耗前先结算、负数和非整数消耗拒绝、上限变化时截断当前值并保留进度；非法容量和回复间隔抛 ValueError。

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
