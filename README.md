# GSB Bugfix Task
## 题面
剧情组改了对话表之后，玩家能反复绕回同一句台词刷标志，本该隐藏的选项也一直显示；有一张表还因为互相跳转把客户端卡死。dialogue_flags.py 的 DialogueGraph 接收节点表，每个节点含 options，选项带 goto 目标、if 条件字典与 set 效果字典；条件按键值逐一比较，缺失的标志视为 False。构造时必须检查所有 goto 指向真实节点，只要从任意节点出发能走回自身就抛 ValueError，菱形这种重复到达却不成环的结构应当接受。visible_options(node) 按定义顺序返回当前条件成立的选项下标；select(node, index) 应用 set 效果并返回下一个节点 id，条件不满足、下标越界、节点不存在都抛 ValueError。flags 返回当前标志副本，改动副本不得影响内部状态。

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
