# 模板升级日志

## v3.1 — 2026-07-04

### 变更

- **progress-template.json**
  - 章节门禁模板移除 `human_approved`，章节级人审只使用 `human_finalized` 与 `knowledge_reviewed`。

- **character / location / faction / item / concept card templates**
  - 新增 `**词条ID**：`、`**别名**：`、`**正史状态**：` 三个 Grep 速查字段。

- **_index-template.md**
  - 各索引表新增 `词条ID`、`别名`、`正史状态` 列。
  - 移除对不存在 `docs/superpowers/specs/` 路径的依赖说明，改为指向 `assets/progress-template.json`。

- **inspiration assets**
  - `assets/灵感/` 明确为模板与分类占位目录；live 灵感卡写小说项目根 `灵感/`。

### validator 同步

- `scripts/validate_assets.py` 新增章节门禁字段、稳定索引字段校验。

## v3.0 — 2026-07-04（全面重构 Phase 1）

详见 `docs/superpowers/specs/2026-07-04-novel-workflow-v3-design.md`。

### 变更

- **progress-template.json**
  - 新增 `checks` 块（ideate_done / design_done / structure_done / iron_rules_passed_last_run / human_review_pending）
  - 新增 `feedback_history` 块（L1-L4 反馈历史，顶层数组）
  - 新增顶层 `cross_model_reviews` 数组（跨模型审核结果）
  - `triggers` 块加 `next_cross_model_review` / `last_periodic_review_chapter` / `last_index_sync_chapter`

- **novel-config-template.json**
  - `iron_rules` 改为编号制（`enabled: [1..12]`）+ `severity` 字段
  - `ai_flavor_rules` 重命名为 `ai_flavor`，加 `soft_read_aloud` 字段
  - 加 `_v2_alias` 字段保留 v2 兼容（含 `iron_rules._v2_alias` 12 个规则名 + `ai_flavor._v2_alias` 4 个旧字段名映射）
  - 保留顶层 `writing_preferences`（v2 字段，v3 不再主动修改，供旧项目降级）

- **character / location / faction / item / concept card templates**
  - 全部加 `## 决策日志关联` 区（5 类触发规则模板中适用的子集 + 见下）

- **_index-template.md**
  - 加 `## v3 触发器关联` 区（从 `进度.json.triggers` 读字段）
  - 修概念索引表格列数错位（原 5 cell 数据行 vs 4 cell 表头）

- **decision-log-template.md**
  - 加 `## v3 触发规则模板` 区（5 类规则的具体格式）

### 兼容性

- v2 字段以 `_v2_alias` 形式保留（含 `iron_rules._v2_alias`、`ai_flavor._v2_alias`、顶层 `writing_preferences`）
- AI 主流程只读 v3 字段
- 旧项目文件可直接用 v3 校验脚本校验（缺失 v3 字段则提示升级）

### v2 → v3 字段映射

| v2 字段 | v3 位置 | 备注 |
|---------|---------|------|
| `iron_rules.{mc_no_death, ...}` (布尔) | `iron_rules.enabled: [1..12]` + `iron_rules.severity: {"1": "block", ...}` | 12 条规则编号化，severity 控制拦截强度 |
| `iron_rules.{...}` (人类名) | `iron_rules._v2_alias` | 旧字段名映射，保留可读性 |
| `ai_flavor_rules.{transition_word_threshold, ...}` | `ai_flavor.{red_line_grep_threshold, hard_pattern_max_per_chapter, soft_read_aloud}` | 重命名 + 字段重映射 |
| `ai_flavor_rules.adjective_piling_threshold` | `ai_flavor._v2_alias.adjective_piling_threshold` | v3 不再主动修改，保留供人审 |
| `writing_preferences.*` (顶层) | `writing_preferences` 保留原位 | v3 不再主动修改，保留供旧项目降级 |
| `triggers.*` (旧 5 字段) | `triggers.*` 加 3 字段（next_cross_model_review, last_periodic_review_chapter, last_index_sync_chapter） | 增量扩展，旧字段不动 |
| （无对应） | `checks.*` + `feedback_history.*` + `cross_model_reviews` | v3 新增 |

### 与 v2 设计差异

详见 `docs/superpowers/specs/2026-07-04-novel-workflow-v3-design.md` §附录 B。

### 新增工具

- `scripts/validate_assets.py` — 模板校验脚本（--template <name> 或 --all）

### 升级路径

1. 复制本目录的 v3 模板覆盖你项目的 `assets/`
2. 跑 `python scripts/validate_assets.py --all` —— 9 行 `OK` 才算成功
3. 旧的 `进度.json` 文件增加 `checks`、`feedback_history`、`cross_model_reviews` 字段（默认初始值即可）
4. 旧的 `novel-config.json` 文件迁移布尔字段到 `iron_rules._v2_alias`（AI 主流程不再用）
