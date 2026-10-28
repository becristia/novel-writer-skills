# novel-design Changelog

## v3.0 — 2026-07-07（Phase 2 sub-project 3）

详见 `docs/superpowers/specs/2026-07-07-phase2-novel-design-design.md`。

### 变更

- **SKILL.md 重写**：v2 ~80 行 → v3 ~220 行（10 段，含 5 模块入口路由表 + 5 模块子流程概览 + 5 模块衔接约束）
- **新建 5 个 reference**（每个 ~80 行，4 段式 + 模块特定内容）：
  - `references/worldbuilding-guide.md` — M1 6 维度 prompt
  - `references/character-design.md` — M2 6 维度 prompt
  - `references/power-system-guide.md` — M3 6 维度 prompt
  - `references/item-design.md` — M4 6 维度 prompt
  - `references/relationship-design.md` — M5 6 维度 prompt
- **新建 `scripts/validate_novel_design_skill.py`**：11 个校验器

### 与 v2 SKILL.md 差异

| 维度 | v2 | v3 |
|---|---|---|
| 章节数 | 5 | 10 |
| 总行数 | ~80 | ~220 |
| 内嵌子流程 | 隐式 | 显式 4 段式（5 模块各自）|
| 入口路由 | 无 | 决策表（5 模块 + novel-design 是干嘛的）|
| references | 5（5 模块各自）| 5（每 reference 4 段式）|
| 校验 | 无 | 11 个 validators |

### 与 novel-write / novel-meta 协同

- **下游**：novel-design 输出 5 spec + 知识库 → novel-structure 3 层规划 → novel-write 每章查询
- **横向**：novel-meta M4 审计 4 视角（流程合规 / 配置一致 / 模板对齐 / 触发器）
- **M1 演进**：novel-meta M1 可改 novel-design SKILL.md / 5 reference

### Phase 3 关系

本 sub-project 验证静态合规（11 个 validator 全 OK）。Phase 3 用《丹眼因果》跑通完整 novel-design 5 模块 → 验证 SKILL.md 在实际场景中可用。

### 兼容性

- v2 reference 内容已重写为 4 段式（v2 brainstorming 内容保留为 M1/M2/M3/M4/M5 步骤① prompt 的一部分）
- v2 模板字段（5 模块 spec 文档结构）与 Phase 1 模板一致

### 后续 sub-project

- Sub-project 4: novel-structure v3 升级
- Sub-project 5: novel-ideate v3 升级
- README v3 更新（5 sub-project 完成后）
- Phase 3：示例项目《丹眼因果》跑通完整流程
