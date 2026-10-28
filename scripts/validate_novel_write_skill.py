"""novel-write skill 静态校验脚本。

校验 SKILL.md 与 references/ 的 v3 升级完整性。

用法：
    python scripts/validate_novel_write_skill.py --template <name>
    python scripts/validate_novel_write_skill.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "novel-write"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Design §2.2 — 13 段标题顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口触发",
    "调用前自检",
    "章节写作循环",
    "L1-L4 反馈层",
    "知识提取",
    "触发器机制",
    "跨模型交叉审核",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
    "与其他技能配合",
]

# Design §3.4 — 段 5 必填 8 步骤
REQUIRED_STEP_HEADINGS = [
    "步骤①",
    "步骤②",
    "步骤③",
    "步骤④",
    "步骤④b",
    "步骤⑤",
    "步骤⑥",
    "步骤⑦",
    "步骤⑧",
]

# Design §3.1 — 3-stage-tdd 5 章
REQUIRED_TDD_CHAPTERS = [
    "阶段 A",
    "阶段 B",
    "阶段 C",
    "异常路径",
    "与 superpowers TDD 对位",
]

# Design §3.2 — 子代理模板 4 节
REQUIRED_TEMPLATE_SECTIONS = [
    "压缩包生成",
    "prompt 模板",
    "隔离策略",
    "错误处理",
]

# 6 个保持型 reference
MARKER_REFERENCES = [
    "review-standards.md",
    "periodic-review.md",
    "map-transition-check.md",
    "cross-model-review.md",
    "style-guide.md",
    "dialogue-techniques.md",
]

# Decision log 5 类触发
DECISION_LOG_TRIGGERS = ["人物生死", "CP 配对", "伏笔方向", "新设定增补", "跨地图衔接"]

TRACKING_FILES = [
    "追踪/当前上下文.md",
    "追踪/伏笔.md",
    "追踪/时间线.md",
    "追踪/角色状态.md",
]
MATRIX_AND_GATE_KEYWORDS = [
    "追踪/情节线.md",
    "追踪/写作任务.md",
    "workflow_gates.chapters",
    "chapter_gate_template",
    "outline_ready",
    "draft_ready",
    "self_check_passed",
    "human_finalized",
    "knowledge_reviewed",
    "AI 只能建议状态变更",
    "current_chapter = 已定稿章节号",
]


class ValidationError(Exception):
    """校验失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _file_exists(path: Path) -> bool:
    return path.is_file()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_skill_md() -> None:
    """校验 SKILL.md 含 13 段 + ≤280 行 + 段 5 含 8 步骤。"""
    _require(_file_exists(SKILL_MD), "skill-md: 文件不存在")

    content = _read(SKILL_MD)
    lines = content.splitlines()
    _require(len(lines) <= 280, f"skill-md: 行数超 280（实际 {len(lines)}）")

    for sec in REQUIRED_SKILL_SECTIONS:
        _require(f"## {sec}" in content, f"skill-md: 缺段 '## {sec}'")

    # 段 5 必须含 8 步骤
    sec5 = content.split("## 章节写作循环")[1].split("## L1-L4")[0] if "## 章节写作循环" in content else ""
    for step in REQUIRED_STEP_HEADINGS:
        _require(f"### {step}" in sec5, f"skill-md §5: 缺步骤 '### {step}'")


def validate_three_stage_tdd() -> None:
    """校验 3-stage-tdd.md 含设计 §3.1 表列 5 章。"""
    path = REFS_DIR / "3-stage-tdd.md"
    _require(_file_exists(path), "3-stage-tdd: 文件不存在")

    content = _read(path)
    for chap in REQUIRED_TDD_CHAPTERS:
        _require(f"## {chap}" in content or f"### {chap}" in content,
                 f"3-stage-tdd: 缺章节 '{chap}'")
    _require("→ 自动补齐" not in content and "自动补齐（主代理" not in content,
             "3-stage-tdd: 不允许 AI 自动补齐缺失细纲字段")
    _require("不得自动补齐" in content and "询问作者" in content,
             "3-stage-tdd: 缺人主导的缺字段处理规则")


def validate_subagent_template() -> None:
    """校验 subagent-prompt-template.md 已降为短迁移 stub。"""
    path = REFS_DIR / "subagent-prompt-template.md"
    _require(_file_exists(path), "subagent-template: 文件不存在")

    content = _read(path)
    _require(len(content.splitlines()) <= 80,
             "subagent-template: 历史归档 stub 不应超过 80 行")
    for sec in ("唯一权威", "agent-dispatch", "write-chapter-subagent.md",
                "不要读取历史模板起草正文"):
        _require(sec in content, f"subagent-template: 缺迁移说明 '{sec}'")


def validate_writing_constraints() -> None:
    """校验 writing-constraints.md 含 12 铁律 + severity 字段。"""
    path = REFS_DIR / "writing-constraints.md"
    _require(_file_exists(path), "writing-constraints: 文件不存在")

    content = _read(path)
    # 必须提及 severity（v3 新增）
    _require("severity" in content.lower(),
             "writing-constraints: 缺 'severity' 字段说明（v3 新增）")
    # 必须有 12 条铁律（mc_no_death 等 v2 字段名）
    for rule_key in ("mc_no_death", "no_ntr", "no_real_politics",
                     "info_anonymization", "fictional_world_safety"):
        _require(rule_key in content,
                 f"writing-constraints: 缺铁律字段 '{rule_key}'（12 条覆盖不完整）")


def validate_knowledge_extraction() -> None:
    """校验 knowledge-extraction.md 含 5 类决策日志触发。"""
    path = REFS_DIR / "knowledge-extraction.md"
    _require(_file_exists(path), "knowledge-extraction: 文件不存在")

    content = _read(path)
    for trig in DECISION_LOG_TRIGGERS:
        _require(trig in content,
                 f"knowledge-extraction: 缺决策日志触发 '{trig}'")


def validate_de_ai_patterns() -> None:
    """校验 de-ai-patterns.md 含 '阶段 B 一次过 vs 重写' 判断矩阵。"""
    path = REFS_DIR / "de-ai-patterns.md"
    _require(_file_exists(path), "de-ai-patterns: 文件不存在")

    content = _read(path)
    _require("阶段 B" in content and ("重写" in content or "一次过" in content),
             "de-ai-patterns: 缺 '阶段 B 一次过 vs 重写' 判断矩阵（v3 新增）")


def validate_v3_marker() -> None:
    """校验 6 个保持型 reference 顶部有 v3 marker。"""
    for fname in MARKER_REFERENCES:
        path = REFS_DIR / fname
        _require(_file_exists(path), f"v3-marker: 缺失 reference '{fname}'")
        content = _read(path)
        _require("v3 标记" in content or "**v3**" in content,
                 f"v3-marker: '{fname}' 缺 v3 标记头部")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的所有 [details] → references/X.md 路径都存在。"""
    if not _file_exists(SKILL_MD):
        return  # skill-md validator already flagged
    content = _read(SKILL_MD)

    # 找所有形如 `references/X.md` 的引用
    refs = re.findall(r"references/([\w-]+\.md)", content)
    for ref in refs:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


def validate_tracking_integration() -> None:
    """校验写作循环读写追踪系统，而非只依赖即时上下文。"""
    path_requirements = {
        SKILL_MD: TRACKING_FILES + ["写前查询包", "写后", "追踪更新"],
        REFS_DIR / "knowledge-extraction.md": TRACKING_FILES + ["追踪更新", "人审"],
        REFS_DIR / "periodic-review.md": TRACKING_FILES + ["追踪系统"],
        REFS_DIR / "subagent-prompt-template.md": ["agent-dispatch", "压缩包"],
    }
    for path, keywords in path_requirements.items():
        _require(_file_exists(path), f"tracking-integration: 文件不存在 {path.name}")
        content = _read(path)
        for kw in keywords:
            _require(kw in content,
                     f"tracking-integration: {path.name} 缺 '{kw}'")


def validate_matrix_gate_integration() -> None:
    """校验写作循环接入情节线/任务矩阵与人审状态门禁。"""
    path_requirements = {
        SKILL_MD: MATRIX_AND_GATE_KEYWORDS,
        REFS_DIR / "3-stage-tdd.md": [
            "workflow_gates.chapters",
            "outline_ready",
            "draft_ready",
            "self_check_passed",
            "human_finalized",
            "knowledge_reviewed",
        ],
        REFS_DIR / "knowledge-extraction.md": [
            "追踪/情节线.md",
            "追踪/写作任务.md",
            "knowledge_reviewed",
            "人审",
        ],
        REFS_DIR / "periodic-review.md": [
            "追踪/情节线.md",
            "追踪/写作任务.md",
            "状态机",
        ],
    }
    for path, keywords in path_requirements.items():
        _require(_file_exists(path), f"matrix-gate: 文件不存在 {path.name}")
        content = _read(path)
        for kw in keywords:
            _require(kw in content,
                     f"matrix-gate: {path.name} 缺 '{kw}'")
        _require(re.search(r"workflow_gates\.chapter(?!s|_)", content) is None,
                 f"matrix-gate: {path.name} 不应继续引用单例 workflow_gates.chapter")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "3-stage-tdd": validate_three_stage_tdd,
    "subagent-template": validate_subagent_template,
    "writing-constraints": validate_writing_constraints,
    "knowledge-extraction": validate_knowledge_extraction,
    "de-ai-patterns": validate_de_ai_patterns,
    "v3-marker": validate_v3_marker,
    "cross-refs": validate_cross_refs,
    "tracking-integration": validate_tracking_integration,
    "matrix-gate": validate_matrix_gate_integration,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="novel-write v3 校验")
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
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
