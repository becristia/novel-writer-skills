# M4 评估 harness（迁移 stub）

## 使用路由

本文件只保留 `novel-meta` M4 的迁移指针、审计视角和报告路径约定。

## 唯一权威

唯一权威：`skills/agent-dispatch/references/parallel-audit-subagent.md`。

执行 M4 审计时，先读 `skills/agent-dispatch/SKILL.md`，再读该 reference。四个审计视角仍为：

- 流程合规
- 配置一致
- 模板对齐
- 触发器

## 报告路径

报告写入 `docs/reviews/<YYYY-MM-DD>-<skill>-audit.md`。

如同日已有报告，使用 `-vN` 后缀。

## 禁止事项

- 不要读取历史 5 段式模板执行审计。
- 不要让 M4 直接改文件；报告交用户决定后续。
