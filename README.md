# GSB Bugfix Task
## 题面
公会仓库加了副会长和团长权限后，资金开始对不上：没有存款权限的角色也能存，取款上限按角色写死但改了不生效，负数金额反而把余额变大，支出没有审计记录，同一笔取款重复提交扣两次。guild_bank.py 的 GuildBank 负责 deposit、withdraw、set_limit 和 state。实现要按角色权限放行、按角色上限限制单次取款、金额必须是正整数、余额不足拒绝、每次存取记录审计、重复请求不能二次扣款；未知角色和非法参数抛 ValueError。

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
