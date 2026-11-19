# GSB Bugfix Task
## 题面
上线后玩家反馈成就明明达成了却不亮，客服手动补发又出现重复到账；还有人前置成就尚未领取，后续成就却先弹了出来。achievement_chain.py 里的 AchievementChain 接收一份成就定义，每项写明触发事件 event、所需次数 need、前置成就 prereq、金币 reward 与点数 points。玩家必须先 register 注册，record 负责累计进度并返回本次刚解锁的成就列表；进度照常累加，但前置成就只有被领取之后才真正生效。claim 发放金币与点数，成就未解锁、重复领取、名称不存在都要抛 ValueError；pending 列出已解锁未领取项，progress 给出已有次数、目标次数和状态，state 返回可以放心修改的深拷贝。零或负的 count、未注册玩家同样算非法输入。

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
