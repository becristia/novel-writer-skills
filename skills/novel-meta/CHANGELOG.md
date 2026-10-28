# novel-meta Changelog

## v3.0 — 2026-07-06（Phase 2 sub-project 2）

详见 `docs/superpowers/specs/2026-07-06-phase2-novel-meta-design.md`。

### 变更

- **新建 `skills/novel-meta/SKILL.md`**：v3 新建，~200 行（10 段，含 4 M 入口路由表 + 10 段骨架）
- **新建 4 个 reference**：
  - `references/m1-skill-evolution.md` — 4 段式演进流程
  - `references/m2-config-panel.md` — 3 段式配置中央面板
  - `references/m3-template-governance.md` — 4 段式模板治理
  - `references/m4-eval-harness.md` — 5 段式 4 维度评估（模板层）
- **新建 `scripts/validate_novel_meta_skill.py`**：10 个校验器

### 4 M 与 Phase 1/2 sub-project 1 关系

- M1 用于 sub-project 3-5 改造 novel-ideate / design / structure
- M2 管理 `novel-config.json`（Phase 1 已升级）
- M3 管理 `assets/` 模板（Phase 1 已升级）
- M4 是 novel-write §8 触发器的目标（sub-project 1 已就位）

### Phase 3 关系

M4 本 sub-project 只交付**模板层**（4 维度审计"做什么 / 通过标准 / 输出格式" + 4 视角并行调度 + 报告路径）。**执行层**（实际 dispatch 4 子代理 + 用《丹眼因果》做活样本）由 Phase 3 落地。

### 兼容性

- 无 v2 历史包袱（novel-meta 是 v3 新建）
- 其他 4 skill v3 后才能被 M1-M3 全面处理

### 后续 sub-project

- Sub-project 3: novel-design v3 升级
- Sub-project 4: novel-structure v3 升级
- Sub-project 5: novel-ideate v3 升级
- README v3 更新（5 sub-project 完成后）
- Phase 3：示例项目《丹眼因果》跑通完整流程

## v0.4 — 2026-07-10（agent-dispatch sub-project）

### 变更

- **M4 步骤② 派 4 视角子代理改引用**：v3 内嵌的"4 视角调度 + 合并规则"段改为引用 `agent-dispatch/references/parallel-audit-subagent.md`（v0.4 第 6 个 skill）
- **`m4-eval-harness.md` 精简为历史归档**：v3 内容已迁移到 agent-dispatch 模式 2；本文件保留 v3 内容供回溯

### 与 v0.4 架构

novel-meta M4 调度入口从内嵌改为 `agent-dispatch` 模式 2 的流程说明。4 视角审计模板单一权威源在 `agent-dispatch`。
