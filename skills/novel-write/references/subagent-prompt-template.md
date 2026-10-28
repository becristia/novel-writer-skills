# 子代理章节起草 Prompt 模板（迁移 stub）

## 使用路由

本文件只保留迁移指针。`novel-write` 步骤 ③ 不再从这里取 prompt。

## 唯一权威

唯一权威：`skills/agent-dispatch/references/write-chapter-subagent.md`。

需要章节起草子代理时，先读取 `skills/agent-dispatch/SKILL.md`，再读取该 reference，并按 `novel-write` 调用前自检确认：

- `情节线ID`
- `场景任务ID`
- `workflow_gates.chapters.<场景任务ID>`
- 写作上下文压缩包完整性

## 禁止事项

- 不要读取历史模板起草正文。
- 不要从本文件复制 system prompt 或 user prompt。
- 不要让子代理绕过作者人审门禁。
