# GSB Bugfix Task
## 题面
邮件系统一加附件和过期，玩家开始丢东西：邮箱满了还继续收，附件领取后邮件没标已读，过期邮件里的附件直接删掉，重复点领取拿到两份，同一封邮件发给不存在的角色也成功。mail_claim.py 的 MailBox 负责 send、claim、expire 和 state。实现要按收件人容量限制、附件领取只能一次、过期邮件先保留附件再标记、重复 mail id 拒绝、未知收件人拒绝；空附件、非法时间和超容量抛 ValueError。

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
