# M2 配置中央面板

> 配合 `SKILL.md` §5 M2 子流程使用。
> 单一入口修改小说项目根目录的 `novel-config.json`。本仓库的 `assets/novel-config-template.json` 只作为模板和 schema 参照。

---

## 1. 当前字段速查（v3 schema）

| 字段 | 类型 | 含义 | 典型值 |
|---|---|---|---|
| `iron_rules.enabled` | 数组 | 启用的铁律编号列表 | `[1..12]` |
| `iron_rules.severity` | 对象 | 每条铁律的拦截等级 | `{"1": "block", "11": "warn", ...}` |
| `ai_flavor.red_line_grep_threshold` | 整数 | 红线 Grep 阈值 | `0` |
| `ai_flavor.hard_pattern_max_per_chapter` | 整数 | 硬性模式最大次数 | `3` |
| `ai_flavor.soft_read_aloud` | 布尔 | 是否启用朗读检查 | `true` |
| `_v2_alias` | 嵌套 | v2 字段名映射（保留兼容）| 见文件 |
| `writing_preferences` | 嵌套 | 写作偏好（v3 不主动改）| 见文件 |

---

## 2. 3 段式子流程

### 步骤①：读当前状态

```bash
cat novel-config.json
```

向用户展示关键字段汇总：哪些铁律启用 / 阈值是多少 / 平台 / 风格偏好。

### 步骤②：对话修改

用户提改动诉求（例："启用第 13 条铁律"）→ AI 反问澄清（"v3 仅有 12 条；是否要新增第 13 条？还是改启用列表内某条？"）→ 展示拟改字段、影响范围和 diff 草案 → 用户确认后编辑 JSON。

### 步骤③：用户确认后写入 + 校验

```bash
# 写回
python -c "import json; json.dump(<new>, open('novel-config.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)"

# 校验
python scripts/validate_assets.py --template novel-config
```

显示 diff 后等用户确认。

---

## 3. 典型入口词

| 用户说 | AI 操作 |
|---|---|
| "启用第 X 条铁律" | 改 `iron_rules.enabled` 数组加 X |
| "关闭第 X 条铁律" | 改 `iron_rules.enabled` 数组移除 X |
| "调整 AI 味红线阈值到 Y" | 改 `ai_flavor.red_line_grep_threshold` |
| "切换到起点平台" | 改 `project.platform` |
| "看当前配置" | 步骤①：列出当前状态，不改 |
| "禁用硬性 AI 味检测" | 不建议用阈值模拟禁用；如必须临时放宽，改 `ai_flavor.hard_pattern_max_per_chapter = 999` 并记录原因。`0` 表示零容忍，不是禁用 |
| "启用跨模型审核" | 改 `review_density.cross_model_review.enabled = true` |

---

## 4. 边界处理

- **v2 字段读写**（`iron_rules._v2_alias`, `writing_preferences`）允许读写
- **v3 字段必须有 `_v2_alias` 对应**：未在 alias 出现的新字段，AI 应提示"这是新设定，建议加 decision log"
- **validator 失败**：阻塞，必须修复（不允许"忽略"通过）

---

## 5. 与 Phase 1 模板的关系

```
用户 ──M2──> novel-config.json ──> 对齐 assets/novel-config-template.json 的字段约定
                       ↑
              Phase 1 已固化 validator
```

M2 不直接改 `scripts/validate_assets.py`——那是 M3 模板治理的范畴。
