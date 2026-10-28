---
name: novel-meta
description: Use when auditing or changing novel-writer skills, references, validators, asset templates, novel-config, iron rules, or workflow rules; not for novel content creation.
---

# Novel Meta：横向元技能（v3）

## 核心理念

novel-meta 不参与章节写作循环。它是 v3 工作流的"自我演进"通路——管理 4 个核心创作 skill（novel-ideate / design / structure / write）+ 共享资产（`assets/`、`novel-config.json`）。默认只给建议、影响评估和 diff；用户确认后执行。

4 个并列子功能：
- **M1**：技能演进（改 SKILL.md）
- **M2**：配置中央面板（改 `novel-config.json`）
- **M3**：模板治理（改 `assets/`）
- **M4**：评估 harness（审计 skill 合规）

每个 M 独立服务，按需调用。

## 整体架构图

```
              ┌─────────────────────────────┐
              │     novel-meta（横向）        │
              │   M1 演进 / M2 配置 /         │
              │   M3 模板 / M4 审计           │
              └─┬─────┬─────┬─────────────┬───┘
                │     │     │             │
       改 SKILL.md │ 改 config 改 assets/  读全部
                  │     │             │
                ──┘     │             │
              novel-write  ←── 读 config/template
                            │
                       报告 ──> docs/reviews/
```

## 入口路由

按用户意图路由到 4 个 M：

| 用户说 | 路由到 | 备注 |
|---|---|---|
| "我要改 novel-write 的 3 阶段 TDD" | M1 | skill 演进 |
| "启用第 13 条铁律" | M2 | 注意：v3 仅有 12 条，需用户确认 |
| "调 AI 味红线阈值" | M2 | 配置修改 |
| "加新的人物卡片字段" | M3 | 模板扩展 |
| "对 novel-write 做 skill 合规审计" | M4 | 评估 |
| "我刚改完 SKILL.md，跑一遍审计" | M4 | M1 后必接 M4 |
| "novel-meta 是干嘛的" | — | 解释类问题，不进任何 M |

未明确路由的意图 → AI 反问而非猜测。

## 调用前自检

主代理在调用任何 M 前读：

1. 若在小说项目中调用，读取 `进度.json.phases.write.status` 与 `current_chapter`；写作进行中修改流程需先说明影响范围
2. 目标 skill 存在（用户说的 "novel-X" 在 `skills/novel-X/SKILL.md`）
3. 若涉及小说项目配置，项目根 `novel-config.json` 存在，格式对齐 `assets/novel-config-template.json`
4. 若涉及模板，`assets/*.md` 可读
5. 若涉及写入、提交、改配置或改规则，先展示范围和风险，等用户确认后执行

## 4 M 子流程概览

### M1：技能演进（详见 references/m1-skill-evolution.md）

入口：`"我要改 novel-X 的 Y 段"`
4 段式：范围评估 → 讨论改动 → 用户确认 → 执行改动 + 跑 M4 验证
产出：SKILL.md / reference 改动 + M4 报告；是否提交由用户另行确认

### M2：配置中央面板（详见 references/m2-config-panel.md）

入口：`"启用第 X 条铁律"` / `"调整 AI 味阈值"`
3 段式：读当前状态 → 对话修改 → 展示 diff → 用户确认 → 写入 + 校验
产出：修改后的项目根 `novel-config.json` + 字段对齐 `assets/novel-config-template.json`

### M3：模板治理（详见 references/m3-template-governance.md）

入口：`"加新的人物字段"` / `"升级 character-card 模板"`
4 段式：盘点当前模板 → 确定改动范围 → 用户确认 → 执行改动 → 同步校验脚本
产出：`assets/*.md` 改动 + `scripts/validate_assets.py` 同步

### M4：评估 harness（详见 references/m4-eval-harness.md）

入口：`"对 novel-X 做 skill 合规审计"`
5 段式：目标识别 → 4 维度并行审计 → 合并报告 → 报告入 `docs/reviews/<date>-<skill>-audit.md` → 用户决定后续
产出：审计报告（含 4 视角 + 必修/选修/允许分类）；报告不能直接改规则

**v0.4 refactor**：M4 步骤② 派 4 视角子代理改引用 agent-dispatch 模式 2（parallel-audit-subagent）。主代理先读取 `agent-dispatch/SKILL.md` 与其 `parallel-audit-subagent.md`，再用当前平台真实可用的并行子代理机制派发；若无并行子代理能力，则按 4 视角顺序审计并标注未并行。`m4-eval-harness.md` 只保留迁移指针、4 视角名称和报告路径，不能作为执行模板。

## M 之间的协作

4 个 M 频繁连用：

```
M1 改 SKILL.md → M4 审计（确认无回归）
M2 改配置     → M4 审计（确认字段对齐）
M3 改模板     → M2 联动（如加新字段需配 _v2_alias）
M4 报告       → 用户决策 → M1/M2/M3 处置
```

self-correcting loop 是 v3 体系的核心价值——**让 skill 体系可演进而非冻结**。

## 调用频率与触发器

| M | 频率 | 自动调用 |
|---|---|---|
| M1 | 低频（用户主动） | 否 |
| M2 | 低频（用户主动） | 否 |
| M3 | 极低频（项目里程碑） | 否 |
| M4 | 中频（50 章 + 技能改动后） | 提醒用户，不自动改动 |

进度.json triggers 字段：

```
triggers:
  next_periodic_review: 50   ← novel-write 每 50 章触发 M4
  next_skill_change_review: 0 ← M1 改完必跑 M4
```

## 错误处理矩阵

| 失败点 | 处理 |
|---|---|
| 调用前自检失败 | 拒绝进 M，等用户修复 |
| M1 改动后 M4 报告"必修" ≥ 1 项 | 回 M1 步骤②讨论处置 |
| M2 validator 失败 | 阻塞，回 M2 步骤② |
| M3 模板改动未同步 validator | 阻塞，步骤④强制 |
| M4 报告路径冲突（同日已有） | 用 `-vN` 后缀 |
| 用户撤销 | 停止执行；若已写文件，先说明 diff，等待用户决定 |
| 跨 M 错误传播（M1 改坏 → M4 报错 → M2 也尝试改） | 主代理串行化：一个 M 跑完再进下一个 |

## 与 superpowers 对应

| superpowers | novel-meta 对应 |
|---|---|
| writing-skills | M1 |
| brainstorming / writing-plans | M1 内部 L2/L3 改动走 |
| （独创） | M2 配置中央面板 |
| （独创） | M3 模板治理 |
| superpowers-evals | M4 |
| dispatching-parallel-agents | M4 4 视角并行调度 |

## 输出文件 / 参考资源 / 与其他技能配合

**输出**：
```
skills/<skill>/SKILL.md 或 references/*.md 改动（M1）
novel-config.json（M2，小说项目根目录）
assets/*.md（M3）
docs/reviews/<date>-<skill>-audit.md（M4）
可选 git commit（仅用户明确要求后执行）
```

**references/**：
- `m1-skill-evolution.md` — 4 段式演进流程 + L1/L2/L3 改动分级 + commit 约定
- `m2-config-panel.md` — 当前字段速查 + 3 段式对话修改 + 边界处理
- `m3-template-governance.md` — 当前模板清单 + 4 段式治理 + validator 同步原则
- `m4-eval-harness.md` — 迁移 stub；唯一权威在 agent-dispatch 的 `parallel-audit-subagent.md`

**与其他技能配合**：

| 技能 | 关系 |
|---|---|
| novel-ideate | M1 可改其 SKILL.md；M2 改 config 影响其提示 |
| novel-design | 同上 |
| novel-structure | 同上 |
| novel-write | M4 是 novel-write §8 触发器的目标；M2 改 severity 直接影响 novel-write 阶段 B |
