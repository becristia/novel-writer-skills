---
name: novel-write
description: Use when an outlined web-novel project needs chapter drafting, review, revision, continuation, checkpoint resumption, cross-model review, or final prose audit.
---

# Novel Write：创作审核期（v3）

## 核心理念

**写审改一体。3 阶段 TDD = 测试先于正文**。AI 起草/协写，主代理做系统自检，人审定稿。子代理只读压缩包，不能替作者决定正文是否通过。

v3 与 v2 核心区别：
1. **3 阶段 TDD**：阶段 A 细纲验证（红=不写；不得自动补齐）→ 阶段 B 起草+5 维自检（红=不交）→ 阶段 C 人审 4 项红绿灯（红=不存）
2. **上下文隔离**：每次只传入压缩包（前情 ≤300 字 / 词条快照 / 伏笔 / 风格），避免上下文膨胀
3. **决策日志触发**：5 类规则（人物生死/CP 配对/伏笔方向/新设定/跨地图衔接），其余不记
4. **状态门禁**：章节门禁按 `workflow_gates.chapters.<场景任务ID>` 记录；AI 只能建议状态变更，不能替作者推进人审门禁

详见 `references/3-stage-tdd.md`。

## 整体架构图

```
地图循环 ──→ 章节循环 ──→ 地图完成确认（人审）──→ 周期复盘（每50章）──→ 终审（人审）

章节循环（v3）：
  读细纲 → 准备压缩包 → AI起草/协写 → 5 维自检 → [跨模型审核(可选)] → 人审定稿 → 反馈处理(L1-L4) → 知识提取 → 下一章
       ↓阶段A     ↓阶段B         ↓阶段B            ↓阶段C
```

## 入口触发

`"开始写第X章"` / `"继续写"` / `"断点续作《书名》"` / `"修改第X章"` 四种入口。

调用前自检（详见下节）。

## 调用前自检

主代理读 `进度.json`：

1. 若 `checks.structure_done != true` 或 `phases.structure.status != "done"` → 拒绝："该章细纲未生成，先回 novel-structure"
2. 若该章在 `03-大纲/0X-地图X-细纲.md` 中无对应条目 → 拒绝并指出缺失
3. 若细纲缺 `情节线ID` 或 `场景任务ID` → 拒绝并回 novel-structure 补矩阵绑定
4. `current_chapter = 已定稿章节号`；若用户说"继续写"，先根据 `追踪/写作任务.md` 找下一条未完成任务并向作者确认
5. 按本章 `场景任务ID` 读 `workflow_gates.chapters.<场景任务ID>`；若记录不存在，按 `chapter_gate_template` 创建提案并等作者确认
6. 若上一章任务未到 `knowledge_reviewed`，提醒作者还有收尾门禁未过

## 章节写作循环（v3 核心）

### 步骤①：读取细纲

Read 对应地图文件中的本章细纲：章节元数据（POV / 场景地点 / 故事时间 / 出场人物 / 知识库更新标记 / 追踪更新 / 情节线ID / 场景任务ID）+ 8 字段（核心事件 / 冲突 / 人物动态 / 爽点 / 节奏标签 / 伏笔操作 / 关联词条 / 结尾钩子）。

若通过阶段 A，建议 `workflow_gates.chapters.<场景任务ID>.outline_ready = true`，但写入前仍需人审门禁。

### 步骤②：准备上下文压缩包

主代理先做写前查询包：读 `知识库/_index.md` → 按细纲 `关联词条` 读取具体词条 → 读取相关暂存提案 → 读取追踪层 `追踪/当前上下文.md`、`追踪/伏笔.md`、`追踪/时间线.md`、`追踪/角色状态.md`、`追踪/情节线.md`、`追踪/写作任务.md` → 生成自包含压缩包（前情叙事 ≤ 300 字 / 词条快照 / 暂存提醒 / 追踪提醒 / 风格要求）。

压缩包字段由本节定义；子代理调度细节见 agent-dispatch 的 `write-chapter-subagent.md`。`references/subagent-prompt-template.md` 仅为迁移 stub，不用于起草。

### 步骤③：AI 起草/协写章节

把压缩包传给子代理或当前主会话（隔离上下文优先）；AI 返回正文草稿后，主代理生成摘要 + 2-3 标题方案。此处产物是草稿，不是定稿。
草稿生成后只建议 `workflow_gates.chapters.<场景任务ID>.draft_ready = true`，不得标定稿。

**v0.4 refactor**：本步骤可执行 agent-dispatch 模式 1（chapter-draft-subagent）。主代理先读取 `agent-dispatch/SKILL.md` 与该 skill 的 write-chapter-subagent reference，再用当前平台真实可用的子代理机制辅助起草；若无子代理能力，则按同一输入输出契约顺序执行并标注未隔离。详细 4 段式（步骤①②③④）见 `agent-dispatch` skill 的 write-chapter-subagent reference。

### 步骤④：系统自检（5 维）

按顺序：红线（仅检查 `iron_rules.enabled` 中的编号，按 `severity` 区分 block / warn / info）→ 硬性（AI 味 Grep）→ 软性（朗读）→ 设定（Grep 漂移）→ 伏笔（对照 `追踪/伏笔.md`）。任一硬拦截红灯 → 局部修订 → 重跑；3 次命中 → 紧急关卡。warn 列为人审疑点，info 只提示。
自检通过后只建议 `workflow_gates.chapters.<场景任务ID>.self_check_passed = true`，再提交作者。

完整规则见 `[details] → references/3-stage-tdd.md §2 阶段 B`

### 步骤④b：跨模型交叉审核（可选）

用户说"发审核包给 X 审一下" → 主代理生成审核包 → 用户复制给外部模型 → 贴回 → 主代理合并。进度.json 记录用了哪个模型 + 用了/没用/跳过。

详见 `references/cross-model-review.md`。

### 步骤⑤：提交人审（4 项红绿灯）

展示：正文草稿 + 速览 + 自检报告 + 系统疑点 + 标题方案 → 人 4 项打勾：读感 / 人物 / AI 味 / 钩子。全绿 → 人审定稿；任一红 → 携 L1-L4 标签回退。
作者明确通过后才写 `workflow_gates.chapters.<场景任务ID>.human_finalized = true`，并把 `current_chapter` 推进到该已定稿章节号。

完整规则见 `[details] → references/3-stage-tdd.md §3 阶段 C`

### 步骤⑥：反馈处理（L1-L4）

- **L1 `[改章节]`** → 阶段 B/C 重跑
- **L2 `[改细纲]`** → 暂停本章，回 novel-structure 修订 → 重启
- **L3 `[改地图]`** → 同上，影响更大
- **L4 `[改设定]`** → **影响评估前置**（扫描受影响章节 + 估工作量 + 人决策回溯 vs 接受为弧光）

### 步骤⑦：知识提取

人审定稿后扫描本章 → 对照细纲标记 → 生成写后变更提案 → 写入 `知识库/暂存区/` → **人审** → 人审入库 + 更新 `_index.md` + 提取决策日志（5 类触发规则，详见 `references/knowledge-extraction.md`）。
知识库与追踪提案经作者确认后，才写 `workflow_gates.chapters.<场景任务ID>.knowledge_reviewed = true`。

### 步骤⑧：更新伏笔表 + 摘要 + 触发器检查

- 追踪更新：按细纲 `追踪更新` 更新 `追踪/当前上下文.md`、`追踪/伏笔.md`、`追踪/时间线.md`、`追踪/角色状态.md`、`追踪/情节线.md`、`追踪/写作任务.md`
- 写作任务：把对应 `场景任务ID` 按 `planned -> drafting -> self_checked -> human_review -> finalized -> kb_reviewed` 单步推进；不满足门禁则写 `blocked_reason`
- 章节摘要：写入 `摘要/章X.md`
- 触发器检查：`进度.json.triggers` — 若 50 章到/地图切换等 → 主动提醒

## L1-L4 反馈层

| 层级 | 标签 | 范围 | 处理 |
|---|---|---|---|
| L1 | `[改章节]` | 本章文字 | 阶段 B/C 重跑 |
| L2 | `[改细纲]` | 当前+后续细纲 | 暂停 → novel-structure 修订 → 重启 |
| L3 | `[改地图]` | 当前地图规划 | 同上 |
| L4 | `[改设定]` | 知识库 + 回溯 | 影响评估前置 → 人决策 |

L4 影响评估前置：扫描受影响章节 + 估工作量 + 人决策（回溯 vs 接受为人物弧光）。详见 `references/3-stage-tdd.md §4`。

## 知识提取

章节阶段 C 人审定稿后运行：

1. 扫描本章 → 对照细纲标记 → 识别新实体 / 状态变化 / 重大决定
2. 生成写后变更提案 → 写入 `知识库/暂存区/`
3. **人审**（v3 关键：人不审不入库）
4. 通过 → 人审入库，移入 `人物/` 等正式目录 + 更新 `_index.md` + 提取决策日志

决策日志触发规则：仅 5 类（人物生死/CP 配对/伏笔方向/新设定/跨地图衔接），普通行文选择不记。详见 `references/knowledge-extraction.md`。

## 触发器机制

novel-write 每章完成后检查 `进度.json.triggers`：

```
current_chapter ≥ next_periodic_review → 提醒"是否周期性复盘？"
pending_map_transition_check = true → 提醒"地图已切换，是否跨地图衔接检查？"
```

响应后写入 next_xxx 字段。详见 `references/periodic-review.md`。

## 跨模型交叉审核（可选）

详见 `references/cross-model-review.md`。进度.json 记录用了哪个模型。

## 错误处理矩阵

| 失败点 | 处理 |
|---|---|
| 阶段 A 缺细纲 | 拒绝，回 novel-structure |
| 缺情节线ID/场景任务ID | 拒绝，回 novel-structure 补矩阵绑定 |
| 阶段 B 红线命中 | 修订 → 重跑；3 次命中 → 紧急关卡 |
| 阶段 C 任一红灯 | L1-L4 回退 |
| workflow_gates.chapters.<场景任务ID> 阻塞 | 写 blocked_reason，提交作者裁决 |
| 阶段 C 3 轮不过 | 暂停，询问切换策略 |
| 子代理超时 | 重派；2 次失败 → 简化压缩包 |
| L4 影响范围过大 | 提供回溯 vs 接受为弧光 二选一 |

## 与 superpowers 对应

| superpowers | novel-write v3 对应 |
|---|---|
| subagent-driven-development | 阶段 B 隔离上下文起草章节 |
| test-driven-development | 3 阶段 TDD 强制关卡 |
| verification-before-completion | 阶段 B 自检 + 阶段 C 红绿灯 |
| requesting-code-review | 阶段 C 人审 = code review |
| receiving-code-review | L1-L4 反馈处理 |

## 输出文件 / 参考资源

**输出**：
```
正文/章X.md
摘要/章X.md
追踪/当前上下文.md
追踪/伏笔.md
追踪/时间线.md
追踪/角色状态.md
追踪/情节线.md
追踪/写作任务.md
知识库/暂存区/（人审后入正式目录）
进度.json（定稿后更新 current_chapter / feedback_history / checks / workflow_gates.chapters）
```

正文草稿默认只在对话或审核包中呈现；`正文/章X.md` 仅在人审定稿后写入。

**references/**：
- `3-stage-tdd.md` — 完整 3 阶段规则
- `subagent-prompt-template.md` — 迁移 stub；唯一权威在 agent-dispatch 的 `write-chapter-subagent.md`
- `writing-constraints.md` — 12 条铁律 + severity 字段
- `knowledge-extraction.md` — 词条提取 + 决策日志触发
- `de-ai-patterns.md` — AI 味检测 + 阶段 B 一次过 vs 重写
- `review-standards.md` — 章节审核细则
- `periodic-review.md` — 50 章周期复盘
- `map-transition-check.md` — 跨地图衔接 7 维度
- `cross-model-review.md` — Gemini 等外部审核
- `style-guide.md` — 风格指南
- `dialogue-techniques.md` — 对话技巧

## 与其他技能配合

| 技能 | 配合方式 |
|---|---|
| novel-ideate | 读入核心概念作为章节知识背景 |
| novel-design | 读入设定+知识库，撰写时持续更新 |
| novel-structure | 细纲作为本章写作计划 |
| novel-meta | [M2] 调整 `novel-config.json`（如阶段 B 阈值）|
