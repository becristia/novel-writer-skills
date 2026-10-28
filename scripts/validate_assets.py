"""模板校验脚本。校验 assets/ 下所有 v3 模板。

用法：
    python scripts/validate_assets.py --template progress
    python scripts/validate_assets.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"


class ValidationError(Exception):
    """模板校验失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_progress() -> None:
    """校验 progress-template.json 含 v3 必填字段。"""
    path = ASSETS_DIR / "progress-template.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    _require("triggers" in data, "progress: 缺 triggers 块")
    _require("checks" in data, "progress: 缺 checks 块（v3 新增）")
    _require("feedback_history" in data, "progress: 缺 feedback_history 块（v3 新增）")
    _require("tracking" in data, "progress: 缺 tracking 块（外部审计新增）")

    checks = data["checks"]
    for key in ("ideate_done", "design_done", "structure_done",
                "iron_rules_passed_last_run", "human_review_pending"):
        _require(key in checks, f"progress.checks: 缺 {key}")

    feedback = data["feedback_history"]
    _require(isinstance(feedback, list), "progress.feedback_history: 必须是数组")

    triggers = data["triggers"]
    for key in ("next_periodic_review", "next_index_sync",
                "pending_map_transition_check", "next_cross_model_review",
                "next_skill_change_review"):
        _require(key in triggers, f"progress.triggers: 缺 {key}")

    tracking = data["tracking"]
    for key in ("active_context_path", "foreshadowing_path", "timeline_path",
                "character_state_path", "plotline_path", "writing_tasks_path",
                "last_active_context_chapter", "pending_tracking_updates"):
        _require(key in tracking, f"progress.tracking: 缺 {key}")

    gates = data.get("workflow_gates", {})
    _require(gates, "progress: 缺 workflow_gates 块（状态机/人审门禁）")
    for key in ("ideate", "design", "structure"):
        _require(key in gates, f"progress.workflow_gates: 缺 {key}")
        gate = gates[key]
        for field in ("status", "human_approved", "approved_by",
                      "approved_at", "blocked_reason"):
            _require(field in gate, f"progress.workflow_gates.{key}: 缺 {field}")

    _require("chapter" not in gates,
             "progress.workflow_gates: 不允许单例 chapter gate；必须按章节/场景任务ID记录")
    _require("chapter_gate_template" in gates,
             "progress.workflow_gates: 缺 chapter_gate_template")
    _require("chapters" in gates and isinstance(gates["chapters"], dict),
             "progress.workflow_gates: 缺 chapters 对象（按 WT-* / CH-* 存放章节门禁）")

    chapter_gate = gates["chapter_gate_template"]
    for field in ("chapter_id", "scene_task_id", "status",
                  "approved_by", "approved_at", "blocked_reason"):
        _require(field in chapter_gate,
                 f"progress.workflow_gates.chapter_gate_template: 缺 {field}")
    _require("human_approved" not in chapter_gate,
             "progress.workflow_gates.chapter_gate_template: 章节门禁不应含 human_approved；使用 human_finalized / knowledge_reviewed")
    for field in ("outline_ready", "draft_ready", "self_check_passed",
                  "human_finalized", "knowledge_reviewed"):
        _require(field in chapter_gate,
                 f"progress.workflow_gates.chapter_gate_template: 缺 {field}")

    required_templates = {
        "tracking-active-context-template.md": "当前上下文",
        "tracking-foreshadowing-template.md": "伏笔",
        "tracking-timeline-template.md": "时间线",
        "tracking-character-state-template.md": "角色状态",
        "tracking-plotlines-template.md": "情节线",
        "tracking-writing-tasks-template.md": "写作任务",
    }
    for template_name, keyword in required_templates.items():
        template_path = ASSETS_DIR / template_name
        _require(template_path.is_file(), f"progress: 缺追踪模板 {template_name}")
        _require(keyword in template_path.read_text(encoding="utf-8"),
                 f"progress: {template_name} 缺关键词 '{keyword}'")

    task_template = (ASSETS_DIR / "tracking-writing-tasks-template.md").read_text(
        encoding="utf-8"
    )
    for keyword in ("状态转移表", "planned -> drafting -> self_checked",
                    "human_review -> finalized -> kb_reviewed",
                    "一个任务只能有一个当前状态"):
        _require(keyword in task_template,
                 f"progress: tracking-writing-tasks-template.md 缺 '{keyword}'")


def validate_novel_config() -> None:
    """校验 novel-config-template.json 含 v3 必填字段。"""
    path = ASSETS_DIR / "novel-config-template.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    iron = data.get("iron_rules", {})
    _require("enabled" in iron, "novel-config.iron_rules: 缺 enabled 数组（v3 新增）")
    _require(isinstance(iron["enabled"], list), "novel-config.iron_rules.enabled: 必须是数组")
    _require(len(iron["enabled"]) == 12, "novel-config.iron_rules.enabled: 必须含 12 条")
    _require("severity" in iron, "novel-config.iron_rules: 缺 severity 字段（v3 新增）")

    ai_flavor = data.get("ai_flavor", {})
    for key in ("red_line_grep_threshold", "hard_pattern_max_per_chapter", "soft_read_aloud"):
        _require(key in ai_flavor, f"novel-config.ai_flavor: 缺 {key}")

    authority = data.get("creative_authority", {})
    _require(authority, "novel-config.creative_authority: 缺人类创作主权配置")
    for key in ("human_decides", "ai_assists", "requires_human_approval"):
        _require(isinstance(authority.get(key), list) and authority[key],
                 f"novel-config.creative_authority.{key}: 必须是非空数组")


def _validate_card_template(path: Path, name: str) -> None:
    """校验 card 模板含 v3 '决策日志关联' 区。"""
    content = path.read_text(encoding="utf-8")
    _require("决策日志关联" in content,
             f"{name}: 缺 '决策日志关联' 区（v3 新增）")
    # Grep 速查格式校验：至少 3 个 **字段**：值 行
    grep_fields = re.findall(r"\*\*[^*]+\*\*：", content)
    _require(len(grep_fields) >= 3,
             f"{name}: 至少 3 个 '**字段名**：' 速查行（当前 {len(grep_fields)}）")
    for field in ("**词条ID**：", "**别名**：", "**正史状态**："):
        _require(field in content, f"{name}: 缺稳定索引字段 {field}")


def validate_character() -> None:
    _validate_card_template(ASSETS_DIR / "character-card-template.md", "character")


def validate_location() -> None:
    _validate_card_template(ASSETS_DIR / "location-card-template.md", "location")


def validate_faction() -> None:
    _validate_card_template(ASSETS_DIR / "faction-card-template.md", "faction")


def validate_item() -> None:
    _validate_card_template(ASSETS_DIR / "item-card-template.md", "item")


def validate_concept() -> None:
    _validate_card_template(ASSETS_DIR / "concept-card-template.md", "concept")


def validate_index() -> None:
    """校验 _index-template.md 含 v3 triggers 关联列。"""
    content = (ASSETS_DIR / "_index-template.md").read_text(encoding="utf-8")
    _require("人物索引" in content, "index: 缺 '人物索引' 表")
    _require("最近触发" in content or "triggers" in content.lower(),
             "index: 缺 v3 '最近触发' 列或 triggers 引用")


def validate_decision_log() -> None:
    """校验 decision-log-template.md 含 v3 5 类触发规则模板。"""
    content = (ASSETS_DIR / "decision-log-template.md").read_text(encoding="utf-8")
    for rule in ("人物生死", "CP 配对", "伏笔方向", "新设定增补", "跨地图衔接"):
        _require(rule in content,
                 f"decision-log: 缺触发规则 '{rule}' 模板")


def validate_project_contract() -> None:
    """校验项目级约定未漂移。"""
    agents = PROJECT_ROOT / "AGENTS.md"
    _require(agents.is_file(), "project-contract: 缺 AGENTS.md")

    files = [
        *PROJECT_ROOT.glob("skills/*/SKILL.md"),
        *PROJECT_ROOT.glob("skills/*/references/*.md"),
        PROJECT_ROOT / "README.md",
    ]
    ignore_names = {"CHANGELOG.md"}
    checked = []
    combined = ""
    for path in files:
        if path.name in ignore_names or not path.is_file():
            continue
        checked.append(path)
        combined += f"\n--- {path.relative_to(PROJECT_ROOT)}\n"
        combined += path.read_text(encoding="utf-8")

    _require(checked, "project-contract: 未找到可检查文档")

    forbidden_patterns = {
        r"进度\.json\.(ideate_done|design_done|structure_done)": "旧式顶层完成字段",
        r"phase\.(structure|design|write)": "旧式 phase.* 字段",
        r"进度\.json\.current\.(map|chapter)": "旧式 current.* 字段",
        r"agent_dispatch\.run": "不存在的 agent_dispatch.run API",
        r"assets/novel-config\.json": "把项目配置误放入 assets/",
        r"assets/暂存区": "把小说项目暂存区误放入 assets/",
        r"assets/03-大纲": "把小说项目大纲目录误放入 assets/",
        r"→\s*自动补齐|自动补齐（主代理": "写作阶段自动补齐关键创作字段",
        r"自动更新知识库": "无人审自动更新知识库",
        r"AI 做所有机械劳动": "把 AI 定位成全流程执行者",
        r"半自动化创作工作流": "把项目定位成半自动生产线",
        r"子代理写章节": "把子代理定位成章节执行核心",
        r"删除或归档|清理暂存区.*删除": "未经用户确认删除或归档暂存知识",
    }
    for pattern, message in forbidden_patterns.items():
        _require(re.search(pattern, combined) is None,
                 f"project-contract: 发现{message}（pattern: {pattern}）")


VALIDATORS = {
    "progress": validate_progress,
    "novel-config": validate_novel_config,
    "character": validate_character,
    "location": validate_location,
    "faction": validate_faction,
    "item": validate_item,
    "concept": validate_concept,
    "index": validate_index,
    "decision-log": validate_decision_log,
    "project-contract": validate_project_contract,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="v3 模板校验")
    parser.add_argument("--template", choices=list(VALIDATORS.keys()))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    targets = list(VALIDATORS.keys()) if args.all else (
        [args.template] if args.template else []
    )
    if not targets:
        parser.print_help()
        return 2

    failed = 0
    for name in targets:
        try:
            VALIDATORS[name]()
            print(f"OK  {name}")
        except ValidationError as e:
            print(f"FAIL {name}: {e}", file=sys.stderr)
            failed += 1
        except FileNotFoundError:
            print(f"FAIL {name}: file not found", file=sys.stderr)
            failed += 1
        except (json.JSONDecodeError, ValueError):
            print(f"FAIL {name}: invalid JSON", file=sys.stderr)
            failed += 1
        except Exception as e:  # noqa: BLE001 — 容错：任何意外都报告而不中断 --all
            print(f"FAIL {name}: {type(e).__name__}: {e}", file=sys.stderr)
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
