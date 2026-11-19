# GSB Bugfix Task
## 题面
更新后玩家发现同一商店在不同区服刷出的商品不一样，半夜刷新时还出现了整天错位，客服那边也复现不出同一份列表。shop_rotation.py 里的 ShopRotation 接收商品池、每日槽位数、随机种子以及相对 UTC 的分钟偏移，同一个种子在同一天必须得到完全一致的序列，换一个实例也不能有偏差。rotation_for(day) 按天序号返回定长列表，槽位内禁止重复；rotation_at(ts) 先结合时区偏移算出本地日序号再取轮换，day_index(ts) 返回该序号，时间戳为负时按向下取整处理。remaining_seconds(ts) 给出距本地零点的剩余秒数，next_reset(ts) 返回下一次刷新的 UTC 时间戳。槽位数超过池子大小、池内商品重复、槽位非正、时区偏移超出正负十四小时，构造时都要抛 ValueError。

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
