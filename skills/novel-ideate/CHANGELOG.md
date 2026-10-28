# novel-ideate Changelog

## v3.0 — 2026-07-09（Phase 2 sub-project 5，**最后一个**）

详见 `docs/superpowers/specs/2026-07-09-phase2-novel-ideate-design.md`。

### 变更

- **SKILL.md 重写**：v2 ~80 行 → v3 177 行（10 段，含 5 步主循环 + 2 模式 + 4 类入口）
- **新建 4 个 reference**（每个 ~80 行）：
  - `references/5-question.md` — 5 维 brainstorm + 5 问详细 prompt
  - `references/book-title.md` — 7 类型书名设计（身份/动作/系统/反差/悬念/情感/意境）
  - `references/book-blurb.md` — 2 模板简介（玄幻/仙侠 / 都市/言情）
  - `references/selling-points.md` — 6 类型卖点（金手指/题材/人设/剧情/情感/世界观）
- **新建 `scripts/validate_novel_ideate_skill.py`**：9 个校验器

### 与 v2 SKILL.md 差异

| 维度 | v2 | v3 |
|---|---|---|
| 章节数 | 5 | 10 |
| 总行数 | ~80 | 177 |
| 模式处理 | 2 模式描述散落 | 段 6 显式差异表 |
| 入口路由 | 无 | 决策表（5 步 + novel-ideate 是干嘛的）|
| references | 3（3 章节）| 4（5 问/书名/简介/卖点 各 1）|
| 校验 | 无 | 9 个 validators |
| 跨 skill 契约 | 隐式 | 显式 4 接口（5 问 → novel-design L1 seed 等）|

### 2 模式处理（v3 新增显式）

| 维度 | 种子模式 | 引导模式 |
|---|---|---|
| 用户输入 | 已有创意 | 无创意 |
| 步骤① 起点 | 从用户输入展开 | 跑 5 问 prompt |
| 步骤② 5 问 | 跳已问的 | 完整跑 |

### Phase 2 完成

**5 个 sub-project 全部完成**：
- ✅ Sub-project 1: novel-write
- ✅ Sub-project 2: novel-meta
- ✅ Sub-project 3: novel-design
- ✅ Sub-project 4: novel-structure
- ✅ Sub-project 5: novel-ideate（本 sub-project）

v3 体系完整：5 skill + 5 validator scripts + 1 meta-skill = 全栈

### 后续任务

- **README v3 更新**（下一个规划任务）：5 sub-project 完成后统一更新 README.md
- **Phase 3**：示例项目《丹眼因果》跑通完整 5 skill 流程
