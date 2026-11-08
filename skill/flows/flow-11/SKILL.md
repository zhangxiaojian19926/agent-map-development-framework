---
name: flow-11
description: 在用户提出「发布候选检查」时使用。本路由不点名成员技能。前置登记未完成时停止，不把候选判定为 READY。
---

# flow-11 发布候选检查

## 进入

不点名成员技能。绑定既有命令 `framework candidate --request`。
flow-13 尚未登记产物时停止，不把候选判定为 READY。
完成后不点名下一个技能。
