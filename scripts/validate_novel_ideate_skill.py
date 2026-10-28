"""novel-ideate skill 静态校验脚本。

校验 SKILL.md 与 references/ 的 v3 完整性。

用法：
    python scripts/validate_novel_ideate_skill.py --template <name>
    python scripts/validate_novel_ideate_skill.py --all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "novel-ideate"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Design §2.3 — 10 段标题按顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口路由",
    "调用前自检",
    "5 步主循环",
    "2 模式处理",
    "调用频率与触发器",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
]

# 5 步主循环步骤名
STEP_KEYWORDS = ["brainstorming", "书名", "简介", "卖点", "人审"]

# 2 模式关键词
TWO_MODE_KEYWORDS = ["种子", "引导"]

# 4 reference 文件名
REFERENCE_FILES = [
    "5-question.md",
    "book-title.md",
    "book-blurb.md",
    "selling-points.md",
]

# 每 reference 特定关键词
QUESTION_KEYWORDS = ["题材", "金手指", "爽点", "读者", "卖点"]
TITLE_KEYWORDS = ["书名", "身份", "动作", "系统", "反差", "悬念", "情感", "意境"]
BLURB_KEYWORDS = ["简介", "钩子", "困境", "冲突", "金手指", "爽点", "卖点"]
POINTS_KEYWORDS = ["卖点", "金手指", "题材", "人设", "剧情", "情感", "世界观"]

# External-project audit: comparable works and market evidence must be explicit.
MARKET_REFERENCE_KEYWORDS = ["对标样本", "扫榜", "拆文", "证据等级", "排行榜不是结论"]


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
    """校验 SKILL.md 含 10 段 + ≤280 行。"""
    _require(_file_exists(SKILL_MD), "skill-md: 文件不存在")

    content = _read(SKILL_MD)
    lines = content.splitlines()
    _require(len(lines) <= 280, f"skill-md: 行数超 280（实际 {len(lines)}）")

    for sec in REQUIRED_SKILL_SECTIONS:
        _require(f"## {sec}" in content, f"skill-md: 缺段 '## {sec}'")


def validate_five_step_cycle() -> None:
    """校验 SKILL.md §5 含 5 步主循环（步骤①-⑤）+ 4 reference 外链。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for step in STEP_KEYWORDS:
        _require(step in content,
                 f"5step-cycle: 5 步主循环缺步骤 '{step}'")

    for ref in REFERENCE_FILES:
        _require(ref in content,
                 f"5step-cycle: 段 5 缺 'references/{ref}' 外链")


def validate_two_mode_handling() -> None:
    """校验 SKILL.md §6 含 2 模式（种子/引导）处理。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for keyword in TWO_MODE_KEYWORDS:
        _require(keyword in content,
                 f"2mode-handling: 2 模式处理缺关键词 '{keyword}'")


def validate_routing() -> None:
    """校验 SKILL.md §3 含入口路由表（≥ 6 行）。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    # 段 3 必须含 5 步 + novel-ideate 关键词
    for keyword in ["5 步", "novel-ideate"]:
        _require(keyword in content,
                 f"3l-routing: 入口路由表缺关键词 '{keyword}'")


def validate_question_keywords() -> None:
    """校验 5-question.md 含 5 关键词。"""
    path = REFS_DIR / "5-question.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in QUESTION_KEYWORDS:
        _require(kw in content,
                 f"5-question: 缺关键词 '{kw}'")


def validate_title_keywords() -> None:
    """校验 book-title.md 含 8 关键词。"""
    path = REFS_DIR / "book-title.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in TITLE_KEYWORDS:
        _require(kw in content,
                 f"book-title: 缺关键词 '{kw}'")


def validate_blurb_keywords() -> None:
    """校验 book-blurb.md 含 7 关键词。"""
    path = REFS_DIR / "book-blurb.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in BLURB_KEYWORDS:
        _require(kw in content,
                 f"book-blurb: 缺关键词 '{kw}'")


def validate_points_keywords() -> None:
    """校验 selling-points.md 含 7 关键词。"""
    path = REFS_DIR / "selling-points.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in POINTS_KEYWORDS:
        _require(kw in content,
                 f"selling-points: 缺关键词 '{kw}'")


def validate_market_reference_gate() -> None:
    """校验构思期含对标/扫榜/拆文证据闸门。"""
    combined = ""
    for rel_path in (
        SKILL_MD,
        REFS_DIR / "5-question.md",
        REFS_DIR / "selling-points.md",
    ):
        if rel_path.is_file():
            combined += "\n" + _read(rel_path)

    for kw in MARKET_REFERENCE_KEYWORDS:
        _require(kw in combined,
                 f"market-reference: 缺关键词 '{kw}'")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的所有 references/*.md 路径都存在。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for ref in REFERENCE_FILES:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "5step-cycle": validate_five_step_cycle,
    "2mode-handling": validate_two_mode_handling,
    "3l-routing": validate_routing,
    "5-question": validate_question_keywords,
    "book-title": validate_title_keywords,
    "book-blurb": validate_blurb_keywords,
    "selling-points": validate_points_keywords,
    "market-reference": validate_market_reference_gate,
    "cross-refs": validate_cross_refs,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="novel-ideate v3 校验")
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
