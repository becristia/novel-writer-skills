# inspiration Changelog

## v0.4 — 2026-07-11（v0.4 第 2 个 sub-project，v3 第 7 个 skill）

详见 `docs/superpowers/specs/2026-07-11-v04-inspiration-design.md`。

### 变更

- **新建 `skills/inspiration/SKILL.md`**（~200 行，10 段）：5 步生命周期 + 3 态迁移
- **新建 2 个 reference**（每个 ~80 行）：
  - `references/灵感分类.md` — 6 维度分类（人物/情节/伏笔/世界/金句/其他）
  - `references/双人对谈.md` — 主代理化身书评人 4 段式对话模板
- **新建 `scripts/validate_inspiration_skill.py`**：9 个 validators（含 1 个弱 novel-ideate 契约）
- **新建 `assets/灵感/灵感卡.md`**：Phase 1 模板扩展（7 段 `**字段**：值` 格式）
- **新建 `assets/灵感/{人物,情节,伏笔,世界,金句,其他}/.gitkeep`**：6 个维度子目录占位
- **轻量 refactor**：`novel-ideate/SKILL.md` 步骤② + `5-question.md` 步骤① 加灵感库读取提示

### 与 novel-ideate 集成

- 灵感库（`assets/灵感/`）作为 novel-ideate 5 问 brainstorm 的 seed
- v0.4 阶段为弱约束（验证器只 INFO 提示，不阻塞）
- v0.5+ 强约束（可考虑 refactor 提升为强引用）

### v0.4 架构改进

inspiration 是**首个不与现有 skill 强耦合**的新 skill——v3 体系的"灵感收集器"位置。

3 态生命周期（active/dormant/promoted）让灵感可临时存储、可升级为正式 card（人物/地点/物品/势力/概念）。

### 兼容性

- 现有 7 skill validator 不动（refactor 仅 novel-ideate 1 段 + 1 句）
- 8 个 validator scripts 全部 OK（Phase 1 9 + 5 sub-project 47 + agent-dispatch 11 + inspiration 9 = 76 个 validators）
- novel-ideate 集成是**轻量级**——SKILL.md 步骤② 1 段 + 5-question.md 步骤① 1 句

### 后续任务

- **README v3 更新**：v0.4 第 2 个 sub-project 完成后统一更新（7 skill + 8 validator scripts）
- **Phase 3**：《丹眼因果》跑通完整 7 skill 流程（验证 inspiration 双人对谈 + 升级路径）
- **v0.5**：inspiration 升级到 novel-design 的自动转换；与 novel-ideate 强契约
