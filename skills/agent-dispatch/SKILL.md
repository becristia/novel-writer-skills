---
name: agent-dispatch
description: Use when a novel-writing workflow needs isolated chapter drafting, parallel skill audits, or explicit subagent dispatch; not for normal writing entrypoints.
---

# Agent Dispatch：子代理调度基础设施（v0.4）

## 核心理念

agent-dispatch 是 v3 体系的"子代理调度基础设施"——一个辅助工具，不是创作决策者。它只能隔离上下文、起草文本、并行检查和汇总报告，不能替作者决策。

2 模式（并列）：
- **模式 1**：章节起草子代理（单 subagent + 上下文压缩包）—— 被 novel-write 步骤③ 调用
- **模式 2**：并行审核子代理（4 视角并行 + 主代理合并）—— 被 novel-meta M4 步骤② 调用

主要被现有 skill 内部调用，**用户直接入口较少**（仅手动调度时使用）。

## 整体架构图

```
              agent-dispatch（v0.4 新建）
                  ├─ 模式 1（章节起草子代理）
                  │   ↑
                  │   └─ novel-write 步骤③ 调用
                  └─ 模式 2（并行审核子代理）
                      ↑
                      └─ novel-meta M4 步骤② 调用

novel-write 步骤③ → 模式 1
novel-meta M4 步骤② → 模式 2
```

## 入口路由

| 调用方 | 路由到 |
|---|---|
| novel-write 步骤③ 调用章节起草子代理 | 模式 1（write-chapter-subagent）|
| novel-meta M4 派 4 视角审计子代理 | 模式 2（parallel-audit-subagent）|
| 用户说"调度子代理起草章节" | 先回 novel-write 调用前自检；通过后才可进入模式 1 |
| 用户说"调度 4 视角并行审计" | 模式 2（用户直接入口，少用）|

## 调用前自检

主代理在调度任何模式前读：

1. 目标 skill / 输入文件存在（novel-X SKILL.md / 细纲）
2. 模式 1：小说项目根 `novel-config.json` 存在，格式对齐 `assets/novel-config-template.json`；`进度.json` 使用 `assets/progress-template.json` schema，且 `checks.*` / `phases.*` / `current_*` 在有效状态
3. 模式 1 必须先通过 novel-write 调用前自检，确认 `情节线ID`、`场景任务ID`、`workflow_gates.chapters.<场景任务ID>` 与写作任务矩阵状态有效
4. 模式 2：仓库审计只需目标 skill、references、校验脚本和 `assets/` 模板。真实小说项目是可选输入；没有样本时只检查静态一致性，并标明运行效果未验证，不要求创建小说配置或进度文件

## 2 模式子流程概览

### 模式 1：章节起草子代理（详见 references/write-chapter-subagent.md）

入口：novel-write 步骤③ 调用章节起草子代理；用户直接要求调度时也必须先回 novel-write 自检
4 段式：
  ① 上下文压缩包生成（前情叙事 ≤ 300 字 / 词条快照 / 追踪层 / 风格）
  ② system prompt + user prompt 构造
  ③ 子代理执行（隔离上下文）+ 输出（章节草稿 + 摘要 + 标题方案）
  ④ 失败处理（超时 / 输出错 / 违反铁律）

产出：章节草稿 + 摘要 + 2-3 标题方案；是否定稿由作者决定

### 模式 2：并行审核子代理（详见 references/parallel-audit-subagent.md）

入口：novel-meta M4 派 4 视角审计子代理（用户直接入口少用）
4 段式：
  ① 目标识别（目标 skill + 项目状态）
  ② 4 视角并行派发（流程合规 / 配置一致 / 模板对齐 / 触发器）
  ③ 子代理只读不写（read-only contract）
  ④ 主代理合并报告（写 docs/reviews/<date>-<skill>-audit.md）

产出：4 视角独立报告 → 合并审计报告；报告只给判断和建议，不能直接触发规则修改

## 与 novel-write / novel-meta 的接口契约

| 维度 | novel-write 步骤③（refactor 后）| novel-meta M4 步骤②（refactor 后）|
|---|---|---|
| 调度入口 | 读取本 skill → 执行模式 1 流程 | 读取本 skill → 执行模式 2 流程 |
| 输入参数 | 细纲 + 压缩包（含追踪层）+ novel-config | 目标 skill + 项目状态 |
| 输出 | 章节草稿 | 4 视角报告 |
| 失败处理 | 继承 agent-dispatch 模式 1 失败处理 | 继承 agent-dispatch 模式 2 失败处理 |
| 接口位置 | `skills/novel-write/references/subagent-prompt-template.md`（已精简为引用）| `skills/novel-meta/references/m4-eval-harness.md`（已精简为引用）|

**单一权威源**：子代理模板仅在 agent-dispatch 维护；novel-write / novel-meta 是 consumer 引用方。

**执行约定**：`agent-dispatch` 不是代码 API，也没有可直接调用的运行函数。主代理必须读取本 skill 和对应 reference，使用当前平台真实可用的子代理/并行代理机制执行；如果当前平台没有子代理能力，则主代理按同一输入输出契约顺序执行，并在结果中标注"未使用子代理隔离"。

## 调用频率与触发器

| 模式 | 频率 | 自动调用 |
|---|---|---|
| 模式 1（章节起草）| novel-write 每章按需 | novel-write 步骤③ 触发 |
| 模式 2（并行审核）| novel-meta M4 周期性（每 50 章 + 技能改动后）| novel-meta M4 触发 |

agent-dispatch 自身不被任何自动触发器直接调用——**只被其他 skill 内部调用**。

## 错误处理矩阵

| 失败点 | 处理 |
|---|---|
| 子代理超时 | 重派（首次）；2 次失败 → 简化压缩包 → 重派 |
| 子代理输出格式错 | 不修改 → 重派 |
| 4 视角 1 个超时 | 该视角标 TIMEOUT，其他 3 视角正常 |
| 4 视角 2+ 超时 | 重派超时的子代理 |
| 子代理产出违反铁律 | 拒绝 → 重新起草 |
| 跨 skill 引用检查失败 | 阻塞 refactor 合并 |
| 4 视角全超时 | 不生成报告，标 AUDIT_FAILED |
| 4 视角结论冲突 | 主代理按最严格意见生成报告基线，交用户裁决 |

## 与 superpowers 对应

| superpowers | agent-dispatch 对应 |
|---|---|
| dispatching-parallel-agents | 模式 2（4 视角并行审计）|
| subagent-driven-development | 模式 1（章节起草子代理）|
| verification-before-completion | 模式 1 步骤④ 失败处理 + 模式 2 步骤④ 合并报告 |
| writing-skills | （v0.4 阶段不调用，agent-dispatch 不需要自身演进）|

## 输出文件 / 参考资源 / 与其他技能配合

**输出**：
```
模式 1：章节草稿（novel-write/SKILL.md 用）
模式 2：docs/reviews/<date>-<skill>-audit.md（novel-meta M4 用）
```

**references/**：
- `write-chapter-subagent.md` — 模式 1 详细流程
- `parallel-audit-subagent.md` — 模式 2 详细流程

**与其他技能配合**：

| 技能 | 关系 |
|---|---|
| novel-write | 步骤③ 调模式 1（章节起草子代理）|
| novel-meta | M4 步骤② 调模式 2（并行审核子代理）|
| novel-ideate / novel-design / novel-structure | v0.4 阶段不调用；v0.5+ 按需扩展 |
| novel-meta M1/M2/M3 | agent-dispatch 不调用 novel-meta 流程（避免递归）|
