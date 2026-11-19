# GSB Bugfix Task
## 题面
拍卖行一开跨服交易，挂单和竞价开始对不上：同一个 auction id 能挂两次，卖家自己抬价也能成交，出价刚好等于起拍价被拒，买断价到了却不立刻结束，过期挂单没有结算，结算时手续费从错误的一方扣。auction_house.py 的 AuctionHouse 负责 list_item、bid、settle 和 state。实现要校验卖家与买家不同、起拍价和买断价关系、出价必须高于当前价、买断立即成交、过期按最高价结算、手续费从卖家所得扣除，重复 id 和非法价格抛 ValueError。

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
