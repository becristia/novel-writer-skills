# novel-structure Changelog

## v3.0 — 2026-07-08（Phase 2 sub-project 4）

详见 `docs/superpowers/specs/2026-07-08-phase2-novel-structure-design.md`。

### 变更

- **SKILL.md 重写**：v2 ~80 行 → v3 ~200 行（10 段，含 3 层入口路由表 + 3 层顺序循环 + 与 novel-write 8 字段对位表）
- **新建 3 个 reference**（每个 ~80 行，4 段式 + 层特定内容）：
  - `references/main-plot-design.md` — L1 6 维度 prompt
  - `references/map-design.md` — L2 7 维度 prompt（v3 七大维度）
  - `references/chapter-outline-design.md` — L3 8 字段 prompt（与 novel-write 阶段 ① 对位）
- **新建 `scripts/validate_novel_structure_skill.py`**：9 个校验器

### 与 v2 SKILL.md 差异

| 维度 | v2 | v3 |
|---|---|---|
| 章节数 | 5 | 10 |
| 总行数 | ~80 | ~200 |
| 内嵌子流程 | 隐式 | 显式 4 段式（每层）|
| 入口路由 | 无 | 决策表（3 层 + novel-structure 是干嘛的）|
| references | 4（4 章节各自）| 3（每 reference 4 段式）|
| 校验 | 无 | 9 个 validators |
| 跨 skill 契约 | 隐式 | 显式 L3 ↔ novel-write 8 字段对位表 |

### 顺序约束（v3 新增）

3 层**严格顺序**（不可跳）：
- L1 主线规划 → L2 地图规划 → L3 细纲规划
- L2 启动前提：L1 已完成
- L3 启动前提：L2 已完成
- 单层失败 → 回该层第 2 段；不跨层回退

### 与 novel-design / novel-write 协同

- **上游**（novel-design）：5 spec → L1/L2 设定背景
- **下游**（novel-write）：L3 8 字段 → 阶段 ① 必填字段
- **横向**（novel-meta）：M4 审计 4 视角

### Phase 3 关系

本 sub-project 验证静态合规（9 个 validator 全 OK）。Phase 3 用《丹眼因果》跑通完整 3 层流程 → 验证 SKILL.md 在实际场景中可用。

### 兼容性

- v2 reference 内容已重写为 4 段式（v2 brainstorming 内容保留为 L1/L2/L3 步骤① prompt 的一部分）
- v2 模板字段（00-主线规划.md / 0X-地图X-名称.md / 0X-地图X-细纲.md 结构）与 v3 一致

### 后续 sub-project

- Sub-project 5: novel-ideate v3 升级
- README v3 更新（5 sub-project 完成后）
- Phase 3：示例项目《丹眼因果》跑通完整流程
