# GSB Bugfix Task
## 题面
竞技服开始被加速外挂刷榜：一帧移动几百米也被判定通过，服务端瞬移之后照样算违规，被拒绝的坐标反而写回了位置表，斜向移动按单轴计算距离导致误判，同一时间戳连发多帧没有拦截，时间戳倒退还能继续走，连续违规的账号没有进入观察名单。anti_speedhack.py 的 MovementValidator 负责 move、teleport、position、violations 和 state。实现要求首次移动直接登记坐标；之后用欧氏距离除以时间差得到速度，超过 speed 乘以 tolerance 的帧拒收，并且坐标与时间都不更新；同一玩家的时间戳必须严格递增；违规次数累计到 max_violations 时在 state 里标记 flagged；teleport 是服务端授权的落点，重置坐标和时间但不增加违规；查询未知玩家一律报错；构造参数 speed 必须为正数。

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
