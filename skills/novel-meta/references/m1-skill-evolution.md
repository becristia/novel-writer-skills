# M1 技能演进

> 配合 `SKILL.md` §5 M1 子流程使用。
> 让你安全地修改任何一个 SKILL.md，包括 novel-meta 自己。

---

## 1. 入口与适用范围

入口触发：
- `"我要改 novel-write 的 3 阶段 TDD"`
- `"加一条铁律"` / `"把 X 步骤移到 Y"`

M1 是 v3 体系的"自我演进"通路——明确修改 SKILL.md、reference 或 skill 流程契约的请求走 M1。

---

## 2. 4 段式子流程

### 步骤①：范围评估

读当前 SKILL.md + 受影响 reference → 生成"修改范围报告"。

报告含：
- 目标 skill（哪个 skill 被改）
- 受影响章节（具体 H2 / H3 段）
- 受影响 reference（哪些 .md 文件）
- 关联 consumer（哪些其他 skill 间接依赖）

### 步骤②：讨论改动

基于范围报告与用户讨论：
- 改动目标是 L1（文字润色）/ L2（结构调整）/ L3（流程变更）
- 改动后是否影响其他 skill 行为
- 是否需要 brainstorming 走 spec → plan → 实施流程

### 步骤③：用户确认后执行改动

展示计划和风险，用户确认后写新 SKILL.md / 改 reference。每次改动必须：
- 通过 validator（`validate_<skill>.py --all`）
- 改动 spec 文件引用（如果有 spec 的话）

commit 不是默认动作；只有用户明确要求提交时，才按 §4 约定提交。

### 步骤④：M4 验证

跑 M4 4 维度审计改完的 skill：
```
进入 M4 流程 → 跑 4 视角并行审计 → 生成报告 → 用户审
```

如 M4 报告"必修项"有 ≥ 1 项，回到步骤②讨论处置。

---

## 3. L1/L2/L3 改动分级

| Level | 类型 | 例 | 处理 |
|---|---|---|---|
| L1 | 文字润色 | "把 §5 步骤①的'对话压缩包'改成'写作压缩包'" | 可直改，仍需用户确认 |
| L2 | 结构调整 | "把 §5 的步骤②③合并" | 需 brainstorming + spec，再实施 |
| L3 | 流程变更 | "把 3 阶段 TDD 改成 4 阶段" | 需完整 sub-project 流程（spec → plan → 实施） |

---

## 4. 可选 commit 约定

仅当用户明确要求提交时使用。

格式：`[M1] <动作> <目标>`

示例：
- `[M1] fix typo in novel-write §5 step 2`
- `[M1] restructure novel-design §3 (L2)`
- `[M1] add "反模式" section to m1-skill-evolution.md`

---

## 5. 反模式

- ❌ **跳过 M4 验证**：改了 SKILL.md 不跑 M4 → 后续 skill 调用会带 bug
- ❌ **跳过 spec 直接改**：L2/L3 改动不经 spec 流程 → 改动难以回溯
- ❌ **未经用户确认就提交**：commit 改变项目历史，必须由用户明确要求
- ❌ **改完 SKILL.md 但忘了 sync**：validator 还是旧版 → 误判通过
