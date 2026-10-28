---
name: novel-ideate
description: Use when starting a web novel from scratch or a seed idea, refining premise, platform fit, readership, title, blurb, or selling points before setting design begins.
---

# Novel Ideate：构思期（v3）

## 核心理念

novel-ideate 是核心创作链路的"入口"——**无上游**，是整个工作流的起点。它只做创意引导和候选生成，最终题材、平台定位、读者承诺、书名、简介和卖点都由作者确认。

5 个创作步骤 + 1 个人审闸门（线性）：
1. **brainstorming**（种子/引导 2 模式）
2. **5 问确认**（Q1-Q5 必填）
3. **书名**（3-5 候选）
4. **简介**（100-300 字）
5. **卖点**（6 类型 + 一句话）
6. **人审闸门**（4 类入口）

每步产物先作为候选写入草稿；只有 `workflow_gates.ideate` 人审闸门通过后，才允许写 `checks.ideate_done = true` 并进入设定期。

## 整体架构图

```
用户（种子/引导）
   ↓
brainstorming → 5 问 → 书名 → 简介 → 卖点 → 人审
   ↓
novel-design（5 模块 seed）
   ↓
novel-structure → novel-write
```

novel-meta M1/M4 横向服务。

## 入口路由

| 用户说 | 路由到 | 模式 |
|---|---|---|
| "帮我构思一部小说" | 步骤① | 引导模式 |
| "我有个想法想写..." | 步骤① | 种子模式 |
| "设计书名" | 步骤③ | （仅当 5 问已完成）|
| "写简介" | 步骤④ | （仅当书名已完成）|
| "提炼卖点" | 步骤⑤ | （仅当简介已完成）|
| "novel-ideate 是干嘛的" | — | 解释类 |

未明确路由 → AI 反问 + 提示当前状态。

## 调用前自检

主代理在调用任何步骤前读：

1. 小说项目根目录可写
2. `进度.json` 不存在，或存在但 `checks.ideate_done != true`
3. 初始化新项目时可读取 `assets/progress-template.json` 与 `assets/novel-config-template.json`

## 5 步主循环（v3 核心）

### 步骤① brainstorming（模式选择）

入口：`"帮我构思一部小说"` / `"我有个想法..."`
2 模式：
- **种子模式**：用户带创意来（题材/主角/金手指 等任意一个或多个）→ 从用户输入展开
- **引导模式**：用户无创意 → 跑 5 维 brainstorm + 5 问 prompt（详见 `references/5-question.md`）

必须覆盖：核心创意 / 平台定位 / 目标读者 / 读者承诺 / 差异点。

对标证据闸门：如用户提供榜单、同类书、历史作品或要求参考市场，必须形成"对标样本 / 扫榜观察 / 拆文结论 / 证据等级"四项摘要。排行榜不是结论；AI 只能指出反复出现的模式和风险，不替作者决定题材。

产出：5 维 brainstorm 摘要（200 字左右核心创意）+ 模式判定 + 平台定位草案 + 可选对标证据摘要

### 步骤② 5 问确认

入口：`"确认 5 问"`
5 问：Q1 题材与风格 / Q2 主角设定 / Q3 主角性格 / Q4 核心冲突 / Q5 篇幅规模
辅助校验：平台定位是否清楚、目标读者是否明确、读者承诺是否能在前三章兑现。
详见 `references/5-question.md`

### 灵感库读取（v0.4 新增）

可在 brainstorm 5 问之前先读项目根 `灵感/`（inspiration skill 维护）历史灵感卡，作为 5 问的回答 seed。

例：用户在 novel-ideate 步骤② 报"我有 X 灵感" → 主代理 Grep 灵感库找相关候选 → 询问用户是否纳入 5 问。

灵感卡只能作为候选输入；AI 不得把灵感卡自动升级为题材、平台定位或读者承诺。

产出：5 问确认表（汇总到 `00-核心概念.md`）+ 模式标记

### 步骤③ 书名设计

入口：`"设计书名"`
3-5 候选书名方案（7 类型各 1 候选）
详见 `references/book-title.md`

产出：3-5 候选书名 + 优劣势分析 + 用户选择 1 个

### 步骤④ 简介设计

入口：`"写简介"`
2 模板（玄幻/仙侠 / 都市/言情）
详见 `references/book-blurb.md`

产出：完整简介文案（100-300 字）

### 步骤⑤ 卖点提炼

入口：`"提炼卖点"`
6 类型各 1 句 + 综合"一句话卖点"
详见 `references/selling-points.md`

产出：6 类型卖点 + 一句话卖点

### 步骤⑥ 人审闸门

入口：`"通过"` / `"改书名"` / `"改简介"` / `"重新构思"` / `"完全重来"`

4 类入口模式：
- 通过 → 作者确认平台定位、读者承诺、书名、简介、卖点后，先写 `进度.json.workflow_gates.ideate.human_approved = true`，再写 `进度.json.checks.ideate_done = true`、`进度.json.phases.ideate.status = "done"`、`进度.json.current_phase = "design"` → 可启动 novel-design
- 改书名 → 回到步骤③
- 改简介 → 回到步骤④
- 重新构思 → 回到步骤①
- 完全重来 → 整个 5 步重跑

## 2 模式处理

**强约束**：种子模式与引导模式产物相同，仅起点不同。模式在步骤① 后即可判定，不影响后续 4 步。

| 维度 | 种子模式 | 引导模式 |
|---|---|---|
| 用户输入 | 已有创意（题材/主角/金手指 等任意）| 无创意，从零开始 |
| 步骤① 起点 | 从用户输入展开 | 跑 5 维 brainstorm + 5 问 |
| 步骤② 5 问 | 已问的跳过，仅问未问的 | 完整跑 5 问 |
| 输出 | `00-核心概念.md` + `00-书名简介.md` | 同上 |
| 适用场景 | 用户有完整或部分创意 | 用户无任何想法 |

## 调用频率与触发器

| 项 | 频率 | 自动调用 |
|---|---|---|
| 5 步主循环 | 1 次/故事 | 否 |
| 2 模式选择 | 步骤① 一次性 | 否 |

novel-ideate 整体完成后 → 经 `workflow_gates.ideate` 人审确认 → 写 `进度.json.checks.ideate_done = true` 与 `进度.json.phases.ideate.status = "done"` → novel-design 可启动。

## 错误处理矩阵

| 失败点 | 处理 |
|---|---|
| 缺 seed（用户输入空）| 启动引导提问；不替作者填写答案 |
| 5 问不全 | 拒绝步骤②，提示补全 |
| 书名空 | 重提 3-5 候选 |
| 简介空 | 重写 |
| 人审不通过 | 4 类入口（改书名/改简介/重新构思/完全重来）|
| 跨 sub-project 契约失败 | 仅用户明确要求时可跳过 novel-ideate，并记录跳过原因 |

## 与 superpowers 对应

| superpowers | novel-ideate 对应 |
|---|---|
| brainstorming | 5 维 brainstorm + 5 问 |
| writing-skills | 4 reference（书名/简介/卖点/5 问 设计）|
| receiving-code-review | 步骤⑥ 人审确认 |
| superpowers-evals | novel-meta M4 审计 |

## 输出文件 / 参考资源 / 与其他技能配合

**输出**：
```
00-核心概念.md（5 维 brainstorm + 5 问确认表）
00-书名简介.md（书名 + 简介 + 卖点）
进度.json（先写 `workflow_gates.ideate.human_approved = true`，再写 `checks.ideate_done = true`、`phases.ideate.status = "done"`、`current_phase = "design"`）
```

**references/**：
- `5-question.md` — 5 维 brainstorm + 5 问详细 prompt
- `book-title.md` — 7 类型书名设计（身份/动作/系统/反差/悬念/情感/意境）
- `book-blurb.md` — 2 模板简介（玄幻/仙侠 / 都市/言情）
- `selling-points.md` — 6 类型卖点（金手指/题材/人设/剧情/情感/世界观）
- `genre-guide.md` — 题材/平台定位不清时读取，用于生成题材候选和风险提示
- `title-examples.md` — 书名候选缺参照时读取，只提供命名模式，不替作者定名
- `blurb-examples.md` — 简介文案卡顿时读取，只提供结构参考，不复制示例句

**与其他技能配合**：

| 技能 | 关系 |
|---|---|
| novel-design | 下游：5 问确认表 + 核心概念 → L1 主线 seed（弱约束，可跳过）|
| novel-structure | 下游：00-核心概念.md / 00-书名简介.md → 3 层规划输入 |
| novel-write | 下游：项目元数据（书名/简介）→ 阶段 ① 压缩包生成 |
| novel-meta M1 | M1 流程可改 novel-ideate SKILL.md / 4 reference |
| novel-meta M4 | M4 审计 4 视角 |
