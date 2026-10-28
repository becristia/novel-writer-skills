---
name: novel-design
description: Use when a confirmed web-novel concept needs worldbuilding, characters, power systems, items, factions, relationships, or canon-setting work; not for prose drafting or outlines.
---

# Novel Design：设定期（v3）

## 核心理念

novel-design 是核心创作链路的"中段"——把 novel-ideate 的核心概念细化为 5 模块设定，再交给 novel-structure 做大纲、novel-write 写章节。AI 负责提出设定草案、发现矛盾和整理卡片；作者确认设定是否成为正史。

5 模块并列：
- **M1**：世界观（地理/历史/势力/规则）
- **M2**：人物（主角/配角/反派）
- **M3**：力量体系（境界/技能/突破）
- **M4**：物品（法宝/丹药/材料）
- **M5**：关系（势力/盟友/敌对）

每个 M 独立服务，按需调用。**5 模块有强依赖关系**：M1 → M2/M3 → M4 → M5。每个模块都必须经过人审闸门；未经作者确认，只能写草稿或暂存区，不能写入正式知识库。

**知识库正史规则**：`知识库/` 下的正式词条会被 novel-structure 和 novel-write 当作正史读取。AI 可以写设定草案和词条草稿，但只有人审确认后才能生成或修改正式词条；每次正式词条变更必须同步 `_index.md`。

**增量设定规则**：写作期临时新增人物、地点、物品、势力或概念时，不重开整个设计期。AI 先做影响评估（影响哪些正式词条、细纲、情节线和已定稿章节），再把候选写入 `知识库/暂存区/`；作者确认后才入正式知识库并同步 `_index.md`。

## 整体架构图

```
novel-ideate ──[核心概念]──> novel-design ──[5 模块设定]──> novel-structure
                                  │                              │
                                  │                              ↓
                                  │                          novel-write
                                  │
                                  └──[5 知识库卡]──> (被 novel-write 读)

novel-meta M4 审计 ─────────> novel-design (4 视角)
```

## 入口路由

按用户意图路由到 5 个模块：

| 用户说 | 路由到 | 备注 |
|---|---|---|
| "创建世界观" | M1 | 世界观 |
| "加新大陆" | M1 | 世界观 |
| "加新人物" | M2 | 人物 |
| "完善 X 设定" | M2（默认）| 也可能是 M3/M4，看 X 是人物/技能/物品 |
| "加新境界" | M3 | 力量体系 |
| "完善力量体系" | M3 | 力量体系 |
| "加新法宝" | M4 | 物品 |
| "X 物品升级" | M4 | 物品 |
| "加新势力" | M5 | 关系 |
| "X 与 Y 结盟" | M5 | 关系 |
| "novel-design 是干嘛的" | — | 解释类，不进任何 M |

未明确路由 → AI 反问（"X 是人物、境界、还是物品？"）。

## 调用前自检

主代理在调用任何 M 前读：

1. `进度.json.checks.ideate_done == true`（避免 novel-ideate 未完成时设计）
2. `知识库/_index.md` 存在（如不存在 → 初始化）
3. 项目根 `novel-config.json` 存在，格式对齐 `assets/novel-config-template.json`
4. `assets/*.md` 模板可读

## 5 模块子流程概览

### M1：世界观（详见 references/worldbuilding-guide.md）

入口：`"创建世界观"` / `"加新大陆"`
4 段式：brainstorming（6 维度）→ spec 草案（`01-世界观.md`）→ 作者确认 → execution（写地点卡）→ validation（location validator + 一致性 grep）
产出：`01-世界观.md` + `知识库/地点/` + `_index.md` 同步

### M2：人物（详见 references/character-design.md）

入口：`"加新人物"` / `"完善 X 设定"`
4 段式：brainstorming（6 维度）→ spec 草案（`02-人物档案.md`）→ 作者确认 → execution（写人物卡）→ validation（character validator）
产出：`02-人物档案.md` + `知识库/人物/` + `_index.md` 同步

### M3：力量体系（详见 references/power-system-guide.md）

入口：`"加新境界"` / `"完善力量体系"`
4 段式：brainstorming（6 维度）→ spec 草案（`03-力量体系.md`）→ 作者确认 → execution（写境界/技能卡）→ validation（concept validator）
产出：`03-力量体系.md` + `知识库/概念/` + `_index.md` 同步

### M4：物品（详见 references/item-design.md）

入口：`"加新法宝"` / `"X 物品升级"`
4 段式：brainstorming（6 维度）→ spec 草案（`04-物品装备.md`）→ 作者确认 → execution（写物品卡）→ validation（item validator）
产出：`04-物品装备.md` + `知识库/物品/` + `_index.md` 同步

### M5：关系（详见 references/relationship-design.md）

入口：`"加新势力"` / `"X 与 Y 结盟"`
4 段式：brainstorming（6 维度）→ spec 草案（`05-人物关系.md`）→ 作者确认 → execution（写势力卡）→ validation（faction validator）
产出：`05-人物关系.md` + `知识库/势力/` + `_index.md` 同步

## 5 模块之间的衔接

**强依赖**：
- 世界观 **先于** 人物（人物在世界框架内）
- 力量体系 **先于** 物品（物品依附等级体系）
- 关系 **最后**（依赖前 4 模块）

**衔接详情**（每 reference 段 4 详述）：

| 当前模块 | 必读依赖 | 不直接依赖但可关联 |
|---|---|---|
| M1 世界观 | 无 | — |
| M2 人物 | M1（人物在世界中）| M3（人物境界）|
| M3 力量体系 | M1（力量是世界规则）| — |
| M4 物品 | M3（物品等级体系）| M1（物品来源地）|
| M5 关系 | M1+M2+M3+M4 | — |

**单模块失败**：回该模块第 2 段；不跨模块回退。

## 调用频率与触发器

| 模块 | 频率 | 自动调用 |
|---|---|---|
| M1 世界观 | 设计期高，写作期低 | 否 |
| M2 人物 | 设计期高，写作期中 | 否 |
| M3 力量体系 | 设计期中，写作期中 | 否 |
| M4 物品 | 设计期中，写作期高 | 否 |
| M5 关系 | 设计期中，写作期低 | 否 |

novel-design 整体完成且作者通过总人审闸门后 → 先写 `进度.json.workflow_gates.design.human_approved = true`，再写 `进度.json.checks.design_done = true`、`进度.json.phases.design.status = "done"`、`进度.json.current_phase = "structure"` → novel-structure 可启动。

## 错误处理矩阵

| 失败点 | 处理 |
|---|---|
| 衔接顺序错（如 M2 在 M1 之前）| 拒绝并提示"先完成 M1" |
| 知识库卡与 spec 漂移 | 4 段式第 4 段同时跑两套 validator，强制同步 `_index.md` |
| 词条未经人审确认 | 不写正式词条；保留为草稿或写入 `知识库/暂存区/` |
| 写作期新增设定 | 先做影响评估和暂存提案；作者确认后再入正式知识库 |
| 5 模块 brainstorming prompt 不全 | reference 段 5 反模式显式警告 |
| 跨模块设定不一致 | M4 审计 4 视角检查 |
| SKILL.md 行数超 280 | validator 阻塞 |
| Phase 1 模板 validator 漏字段 | 5 reference 段 4 必跑；缺漏记 CHANGELOG |
| 用户撤销 | 停止执行；若已写文件，展示 diff 并等待用户决定 |

## 与 superpowers 对应

| superpowers | novel-design 对应 |
|---|---|
| brainstorming | 5 模块步骤① |
| writing-plans | 5 模块步骤②（写 spec 文档）|
| writing-skills（间接）| 4 段式内嵌子流程的"TDD 风格" |
| receiving-code-review | 5 模块步骤③人审 |
| verification-before-completion | 5 模块步骤④（两套 validator）|
| test-driven-development（间接）| "先有可验证 spec → 再写知识库卡" |

## 输出文件 / 参考资源 / 与其他技能配合

**输出**：
```
01-世界观.md / 02-人物档案.md / 03-力量体系.md / 04-物品装备.md / 05-人物关系.md
知识库/地点/ / 人物/ / 概念/ / 物品/ / 势力/  + _index.md
进度.json（先写 `workflow_gates.design.human_approved = true`，再更新 `checks.design_done = true`、`phases.design.status = "done"`、`current_phase = "structure"`）
```

**references/**：
- `worldbuilding-guide.md` — M1 4 段式（6 维度 prompt + 模板 + 衔接 + 反模式）
- `character-design.md` — M2 4 段式
- `power-system-guide.md` — M3 4 段式
- `item-design.md` — M4 4 段式
- `relationship-design.md` — M5 4 段式

**与其他技能配合**：

| 技能 | 关系 |
|---|---|
| novel-ideate | 上游：接收 00-核心概念.md 的"题材"作为 M1 seed |
| novel-structure | 下游：5 spec + 知识库 → 3 层规划输入 |
| novel-write | 下游：知识库卡 → 每章压缩包 |
| novel-meta M1 | M1 流程可改 novel-design SKILL.md / 5 reference |
| novel-meta M4 | M4 审计 novel-design 4 视角 |
