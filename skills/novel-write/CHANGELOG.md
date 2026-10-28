# novel-write Changelog

## v3.0 — 2026-07-05（Phase 2 sub-project 1）

详见 `docs/superpowers/specs/2026-07-05-phase2-novel-write-design.md`。

### 变更

- **SKILL.md 重写**：v2 ~150 行 → v3 ~250 行（13 段，含 4 段式 + 3 阶段 TDD）
- **新增 `references/3-stage-tdd.md`**：完整 3 阶段 TDD 规则（~200 行）
- **新增 `references/subagent-prompt-template.md`**：可复用子代理 prompt 模板（~100 行）
- **更新 `references/writing-constraints.md`**：顶部加 severity 字段说明
- **更新 `references/knowledge-extraction.md`**：加 5 类决策日志触发规则
- **更新 `references/de-ai-patterns.md`**：加"阶段 B 一次过 vs 重写"判断矩阵
- **标记 6 个保持型 reference**（仅顶部 v3 marker）：review-standards / periodic-review / map-transition-check / cross-model-review / style-guide / dialogue-techniques
- **新增 `scripts/validate_novel_write_skill.py`**：8 个校验器（结构性静态检查）

### 与 v2 SKILL.md 差异

详见 spec 附录 B。

### 兼容性

- v2 概念保留在 references/（铁律 12 条、5 维 AI 味检测、6 维度跨地图衔接等）
- v3 在概念层升级（4 段式 + 3 阶段 TDD 强制关卡）
- 调用方式不变（"开始写第X章" / "继续写" / "断点续作" / "修改第X章"）

### Phase 3 验证

待《丹眼因果》示例项目跑通完整流程 → 反馈修订。

## v0.4 — 2026-07-10（agent-dispatch sub-project）

### 变更

- **步骤③ 派子代理写章节改引用**：v3 内嵌的"子代理写章节 prompt template"段改为引用 `agent-dispatch/references/write-chapter-subagent.md`（v0.4 第 6 个 skill）
- **`subagent-prompt-template.md` 精简为历史归档**：v3 内容已迁移到 agent-dispatch 模式 1；本文件保留 v3 内容供回溯

### 与 v0.4 架构

novel-write 步骤③ 调度入口从内嵌改为 `agent-dispatch` 模式 1 的流程说明。子代理模板单一权威源在 `agent-dispatch`。
