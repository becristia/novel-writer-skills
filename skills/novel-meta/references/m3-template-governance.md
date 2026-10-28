# M3 模板治理

> 配合 `SKILL.md` §5 M3 子流程使用。
> 管理 `assets/` 下所有模板文件的演进。

---

## 使用路由

- 盘点或新增模板时读“当前模板清单”。
- 修改模板字段时读“4 段式子流程”和“validator 同步原则”。
- 只确认模板范围时读“当前模板清单”，不要顺手修改 validator。

---

## 1. 当前模板清单（Phase 1 升级后）

```
assets/
├── _index-template.md                全局索引模板
├── character-card-template.md        人物卡片
├── location-card-template.md         地点卡片
├── faction-card-template.md          势力卡片
├── item-card-template.md             物品卡片
├── concept-card-template.md          概念卡片
├── decision-log-template.md          决策日志（5 类触发规则）
├── progress-template.json            进度.json schema
├── novel-config-template.json        配置 schema
├── tracking-active-context-template.md
├── tracking-foreshadowing-template.md
├── tracking-timeline-template.md
├── tracking-character-state-template.md
├── tracking-plotlines-template.md
├── tracking-writing-tasks-template.md
├── 灵感/
│   └── 灵感卡.md                      灵感卡模板（路径：assets/灵感/灵感卡.md）
└── CHANGELOG.md                      模板升级日志
```

按当前设计，16 个模板 + 1 个 CHANGELOG。`assets/灵感/` 只放模板和分类占位目录，live 灵感卡写项目根 `灵感/`。

---

## 2. 4 段式子流程

### 步骤①：盘点当前模板

```bash
ls assets/
wc -l assets/*.md assets/*.json
```

向用户展示每个模板的"字段速查表"（前 20 行）。

### 步骤②：确定改动范围

4 类改动：
- **单模板升级**：升级某个 .md 模板的内容（加新必填字段等）
- **整套更新**：所有模板统一升一版（如 v3.0 → v3.1）
- **加新模板**：完全新增（如加 `scene-card-template.md`）
- **模板废弃**：标记 .md 为 deprecated（保留 .md 但不再使用）

### 步骤③：用户确认后执行改动

展示字段变化、受影响 skill、validator 变化；用户确认后写新模板 / 改旧模板 / 加迁移说明。**关键**：
- 改模板之前先 grep 现有使用：`grep -r "new_field" skills/`
- 决定 schema 变更是否需要 `_v2_alias` 兼容
- CHANGELOG 加一行

### 步骤④：同步校验脚本

如改了 template 必填字段，**必须同步**改 `scripts/validate_assets.py`：
- 添加新 validator function
- 在 VALIDATORS 字典注册
- 写测试用例（如适用）

**单一变更集原则**：模板改动 + validator 改动必须在同一轮修改中完成。如分两轮，中间状态会让 validator 误判。commit 仅在用户明确要求时执行。

---

## 3. validator 同步原则

| 模板改动 | validator 必须 |
|---|---|
| 加新必填字段 | 加 `_require` 检查 |
| 改字段名（v3 → v4） | 同步 validator 的字段名 |
| 删字段 | validator 移除对应检查 |
| 重命名 validator 模板 | 同步 VALIDATORS 字典键名 |

如不同步：
- 模板合规但校验过时（误判通过）
- 模板不合规但校验缺失（误判失败）

---

## 4. 版本号与 CHANGELOG

- 模板版本号在文件头部：`<!-- version: v3.1 -->` （v2 没有，v3 才加）
- 每次升级 +1 minor（v3.0 → v3.1）
- CHANGELOG.md 加一行：
  ```
  ## v3.1 — <日期>
  - <做了什么>
  - <哪些 validator 同步>
  ```

---

## 5. 反模式

- ❌ **改模板忘同步 validator**：CI 误判通过
- ❌ **分两轮改动**：中间状态让 validator 报 FAIL
- ❌ **大版本不写 CHANGELOG**：未来回看不知为啥改了
- ❌ **新模板无 validator**：CHANGELOG 写了但 skill 不会卡
