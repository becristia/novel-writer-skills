# agent-dispatch Changelog

## v0.4 — 2026-07-10（v0.4 第 1 个 sub-project，v3 第 6 个 skill）

详见 `docs/superpowers/specs/2026-07-10-v04-agent-dispatch-design.md`。

### 变更

- **新建 `skills/agent-dispatch/SKILL.md`**（~200 行，10 段）：2 模式入口路由 + 接口契约
- **新建 2 个 reference**（每个 ~80 行）：
  - `references/write-chapter-subagent.md` — 模式 1 详细流程（4 段式）
  - `references/parallel-audit-subagent.md` — 模式 2 详细流程（4 段式）
- **新建 `scripts/validate_agent_dispatch_skill.py`**：11 个校验器（含 4 跨 skill 引用检查）
- **重构 5 文件**：
  - `skills/novel-write/SKILL.md` — 步骤③ 改引用 agent-dispatch 模式 1
  - `skills/novel-write/references/subagent-prompt-template.md` — 精简为历史归档
  - `skills/novel-meta/SKILL.md` — M4 步骤② 改引用 agent-dispatch 模式 2
  - `skills/novel-meta/references/m4-eval-harness.md` — 精简为历史归档
  - `skills/novel-write/CHANGELOG.md` + `skills/novel-meta/CHANGELOG.md` — 各加 v0.4 条目

### 2 模式核心定位

| 模式 | 用户场景 | 入口词 | 调用方 |
|---|---|---|---|
| 模式 1：写章节子代理 | 写正文子代理，给定足够上下文 | 模式 1 | novel-write 步骤③ |
| 模式 2：并行审核子代理 | 4 视角并行审计 | 模式 2 | novel-meta M4 步骤② |

### v0.4 架构改进

agent-dispatch 是**首个被其他 skill 调用的 skill**——Phase 2 5 sub-project 都没出现"被调用"模式。

**单一权威源**：子代理模板仅在 agent-dispatch 维护；novel-write / novel-meta 是 consumer 引用方。

### 兼容性

- novel-write / novel-meta / 其他 5 skill 的 validator 不动（VALIDATORS 字典 / 关键词列表）
- v0.4 完成后所有 6 skill 的 67 个 validators 全 OK
- 跨 skill 引用 4 项检查强制 refactor 实际生效

### 后续任务

- **Phase 3**：《丹眼因果》跑通完整流程（验证 agent-dispatch 在 novel-write / novel-meta 实际调用时正常）
- **v0.5**：novel-ideate / novel-design / novel-structure 也可调用 agent-dispatch 模式 1（按需扩展）
- **README v3 更新**：v0.4 完成后统一更新（已与 v0.4 sub-project 一起列入下一个规划）
