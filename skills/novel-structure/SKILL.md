---
name: novel-structure
description: Use when a designed web-novel project needs main plot, map or volume planning, chapter outlines, outline revisions, or new planned chapters; not for prose or canon-card edits.
---

# Novel Structure：大纲期（v3）

## 核心理念

novel-structure 是核心创作链路的"中后段"——把 novel-design 的设定细化为 3 层大纲，再交给 novel-write 写章节。AI 负责拆结构、补盲点和检查字段；主线取舍、地图节奏、章节顺序和开篇钩子必须由作者确认。

3 层**严格顺序**（不可跳）：
- **Layer 1**：主线规划（故事整体走向）
- **Layer 2**：地图规划（每卷/地图的展开）
- **Layer 3**：细纲规划（每章具体规划）

每层 4 段式（brainstorming → spec → 人审闸门 → execution → validation）。**L3 8 字段与 novel-write 阶段 ① 必填字段对位**——保证下游能无歧义消费。前三章额外读取 `references/opening-design.md`，通过开篇人审闸门后才能启动正文。

## 整体架构图

```
novel-ideate ──[核心概念]──> novel-design ──[5 模块设定]──> novel-structure
                                                                      │
                                                                      ↓
                                                                  novel-write
                                                                  (阶段 ① 读 L3)
```

## 入口路由

按用户意图路由到 3 层：

| 用户说 | 路由到 | 备注 |
|---|---|---|
| "开始做大纲" | Layer 1 | 主线规划 |
| "重做主线" | Layer 1 | 主线规划 |
| "做地图" | Layer 2 | 地图规划（需 L1 已完成）|
| "加新地图" | Layer 2 | 地图规划 |
| "做细纲" | Layer 3 | 细纲规划（需 L2 已完成）|
| "加新章" | Layer 3 | 细纲规划 |
| "修改细纲" | Layer 3 | 细纲规划 |
| "novel-structure 是干嘛的" | — | 解释类，不进任何 L |

未明确路由 → AI 反问。

## 调用前自检

主代理在调用任何 L 前读：

1. `进度.json.checks.design_done == true`（避免 novel-design 未完成时开始大纲）
2. 当前层依赖层已完成（调 L2 时 L1 完成；调 L3 时 L2 完成）
3. 项目根 `novel-config.json` 存在，格式对齐 `assets/novel-config-template.json`
4. 项目根 `03-大纲/` 目录可写
5. `current_chapter = 已定稿章节号`，大纲阶段不得用它表示规划游标；规划覆盖范围写 `phases.structure.total_chapters_planned` 与 `追踪/写作任务.md`

## 3 层顺序循环（v3 核心）

### Layer 1：主线规划（详见 references/main-plot-design.md）

入口：`"开始做大纲"` / `"重做主线"`
4 段式：brainstorming（6 维度）→ spec（`03-大纲/00-主线规划.md`）→ execution（写 spec + 生成进度变更提案；人审后写入）→ validation（10-20 节点覆盖 + 伏笔大布局 grep + 节奏密度自检）
产出：`03-大纲/00-主线规划.md` + `进度.json.phases.structure.status = "in_progress"` 变更提案（人审后写入）

### Layer 2：地图规划（详见 references/map-design.md）

入口：`"做地图"` / `"加新地图"`（需 L1 已完成）
4 段式：brainstorming（7 维度 = 七大维度）→ spec（`03-大纲/0X-地图X-名称.md`）→ execution（写 spec + 生成进度变更提案；人审后写入）→ validation（7 维度完整性 + 跨地图衔接双向 + 节奏密度自检）
产出：`03-大纲/0X-地图X-名称.md` + 跨地图衔接检查

### Layer 3：细纲规划（详见 references/chapter-outline-design.md）

入口：`"做细纲"` / `"加新章"`（需 L2 已完成）
4 段式：brainstorming（8 字段 + 章节元数据 + 情节线/任务绑定）→ spec（`03-大纲/0X-地图X-细纲.md`，每章 1 条 8 字段 + 元数据）→ execution（写 spec + 生成进度变更提案；人审后写入）→ validation（8 字段齐全 + 元数据齐全 + 矩阵绑定 + 节奏密度自检 + **与 novel-write §5 阶段 ① 字段对位**）
产出：`03-大纲/0X-地图X-细纲.md`

**知识库接口**：L3 的关联词条必须可解析到 `知识库/_index.md` 或具体词条路径。缺词条时不得跳过；AI 要列出缺失词条、说明影响，并让作者选择：回 novel-design 补词条 / 临时改细纲 / 标记为待建词条。

**矩阵接口**：L3 每章必须写入或引用 `追踪/情节线.md` 的 `情节线ID` 与 `追踪/写作任务.md` 的 `场景任务ID`。只要该章推进主线、支线、人物弧光、关系线或伏笔线，就要在情节线矩阵中有对应行。

### 开篇专项闸门（详见 references/opening-design.md）

入口：L3 已生成第 1-3 章细纲。
检查：首章冲突是否够早、主角承诺是否明确、前三章是否兑现读者承诺、章末钩子是否能拉到下一章。
处理：AI 只列问题和改法候选；作者确认后才允许进入 novel-write 第 1 章。

## 3 层之间的衔接

**强依赖**（不可跳）：

| 当前层 | 必读依赖 | 输出消费者 |
|---|---|---|
| L1 主线规划 | 无（无依赖）| L2 地图规划（卷划分）|
| L2 地图规划 | L1（卷划分）| L3 细纲规划（每章设计）|
| L3 细纲规划 | L2（地图 X 名称）| novel-write 阶段 ①（读细纲）|

**L3 8 字段与 novel-write 阶段 ① 8 字段对位**（跨 sub-project 强契约）：

| L3 字段 | novel-write 字段 |
|---|---|
| 核心事件 | 核心事件 |
| 冲突类型+双方 | 冲突 |
| 人物动态 | 人物动态 |
| 爽点类型+强度 | 爽点 |
| 节奏标签 | 节奏标签 |
| 伏笔操作 | 伏笔操作 |
| 关联词条 | 关联词条 |
| 结尾钩子 | 结尾钩子 |

**单层失败**：回该层第 2 段；不跨层回退。

## 调用频率与触发器

| 层 | 频率 | 自动调用 |
|---|---|---|
| L1 主线规划 | 1 次/故事 | 否 |
| L2 地图规划 | 1 次/地图（多卷项目可多次）| 否 |
| L3 细纲规划 | 1 次/章 | 否 |

当前写作窗口的 3 层完成 + 前三章开篇人审通过 → 建议写 `进度.json.workflow_gates.structure.outline_ready = true`，经人审门禁通过后再写 `进度.json.workflow_gates.structure.human_approved = true`、`进度.json.checks.structure_done = true`、`进度.json.phases.structure.status = "done"`、`进度.json.current_phase = "write"` → novel-write 可启动。

## 错误处理矩阵

| 失败点 | 处理 |
|---|---|
| 顺序依赖错（跳过 L1/L2）| 拒绝并提示"先完成 L1/L2" |
| L3 8 字段与 novel-write 不一致 | 拒绝写入；显式提示字段名/类型 |
| 关联词条缺词条或不可解析 | 拒绝进入 novel-write；列出缺失词条并让作者决定补设定或改细纲 |
| 情节线ID / 场景任务ID 缺失 | 不进入 novel-write；补 `追踪/情节线.md` 与 `追踪/写作任务.md` 后再人审 |
| 前三章开篇闸门未通过 | 不进入 novel-write；回 L3 调整前 3 章细纲 |
| 节奏密度异常（如 > 3 大场景/10 章）| 提示并要求重排 |
| 字段不齐全（如 8 字段缺 1）| 拒绝；缺 ≥3 项回 L3 第 2 段 |
| 跨地图衔接单向 | 提示并要求补双向 |

## 与 superpowers 对应

| superpowers | novel-structure 对应 |
|---|---|
| brainstorming | 3 层步骤① |
| writing-plans | 3 层步骤②（写 spec 文档）|
| receiving-code-review | 3 层步骤③人审 |
| verification-before-completion | 3 层步骤④ |
| test-driven-development（间接）| "先有可验证 spec → 再写细纲" |
| superpowers-evals | novel-meta M4 审计 |

## 输出文件 / 参考资源 / 与其他技能配合

**输出**：
```
03-大纲/00-主线规划.md
03-大纲/0X-地图X-名称.md（含跨地图衔接）
03-大纲/0X-地图X-细纲.md（每章 8 字段 + 章节元数据）
进度.json（先生成变更提案；人审后写入 `workflow_gates.structure.human_approved = true`、`checks.structure_done = true`、`phases.structure.status = "done"`、`current_map`；不更新 `current_chapter`）
```

**references/**：
- `main-plot-design.md` — L1 4 段式（6 维度 prompt + 主线模板 + 衔接 + 反模式）
- `map-design.md` — L2 4 段式（7 维度 prompt + 地图模板 + 跨地图衔接 + 反模式）
- `chapter-outline-design.md` — L3 4 段式（8 字段 prompt + 细纲模板 + novel-write 对位表 + 反模式）
- `opening-design.md` — 前三章黄金开篇检查与人审闸门
- `plot-structures.md` — 主线结构卡顿时读取，只给结构候选和适用风险
- `conflict-and-scene.md` — L3 冲突弱、场景目标不清时读取
- `foreshadowing-guide.md` — 伏笔线规划或回收密度异常时读取
- `pace-control.md` — 地图/章节节奏失衡时读取

**与其他技能配合**：

| 技能 | 关系 |
|---|---|
| novel-ideate | 上游：核心概念 → L1 主线 seed |
| novel-design | 上游：5 spec → L1/L2 设定背景 |
| novel-write | 下游：L3 8 字段 → 阶段 ① 必填字段 |
| novel-meta M1 | M1 流程可改 novel-structure SKILL.md / 3 reference |
| novel-meta M4 | M4 审计 4 视角 |
