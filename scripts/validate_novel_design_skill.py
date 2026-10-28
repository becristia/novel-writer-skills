"""novel-design skill 静态校验脚本。

校验 SKILL.md 与 references/ 的 v3 完整性。

用法：
    python scripts/validate_novel_design_skill.py --template <name>
    python scripts/validate_novel_design_skill.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "novel-design"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Design §2.3 — 10 段标题按顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口路由",
    "调用前自检",
    "5 模块子流程概览",
    "5 模块之间的衔接",
    "调用频率与触发器",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
]

# 5 reference 文件名
MODULE_REFS = [
    "worldbuilding-guide.md",
    "character-design.md",
    "power-system-guide.md",
    "item-design.md",
    "relationship-design.md",
]

# 4 段式关键词（每个 reference 都应含）
FOUR_STAGE_KEYWORDS = ["brainstorming", "spec", "execution", "validation"]

# 每模块特定关键词
M1_KEYWORDS = ["世界观", "地点", "题材", "地理", "历史", "势力"]
M2_KEYWORDS = ["人物", "性格", "背景", "弧光", "能力"]
M3_KEYWORDS = ["力量", "境界", "突破", "限制", "来源"]
M4_KEYWORDS = ["物品", "品阶", "能力", "获得", "限制"]
M5_KEYWORDS = ["关系", "势力", "盟友", "敌对", "规模"]


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


def validate_five_m_routing() -> None:
    """校验 SKILL.md §3 含入口路由表（≥ 11 行）。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    # 段 3 必须含 5 模块 + novel-design 关键词
    for keyword in ["M1", "M2", "M3", "M4", "M5", "novel-design"]:
        _require(keyword in content,
                 f"5m-routing: 入口路由表缺关键词 '{keyword}'")


def validate_five_m_overview() -> None:
    """校验 SKILL.md §5 含 5 个 ### M1/M2/M3/M4/M5: 标题 + 5 个 reference 引用。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for m in ["M1", "M2", "M3", "M4", "M5"]:
        _require(f"### {m}" in content,
                 f"5m-overview: 缺 '### {m}：' 段")

    for ref in MODULE_REFS:
        _require(ref in content,
                 f"5m-overview: 段 5 缺 'references/{ref}' 外链")


def _validate_module_ref(keywords: list, validator_name: str) -> None:
    """通用 reference 校验：含 brainstorming/spec/execution/validation + 模块特定关键词。"""
    ref_name = MODULE_REFS[int(validator_name.split("-")[-1].replace("m", "")) - 1]
    path = REFS_DIR / ref_name
    if not _file_exists(path):
        return  # 5m-validator / 4stage-check separately
    content = _read(path)

    for kw in FOUR_STAGE_KEYWORDS:
        _require(kw in content,
                 f"4stage-check: {ref_name} 缺 4 段式关键词 '{kw}'")


def validate_four_stage() -> None:
    """校验 5 reference 各自含 4 段式 4 关键词。"""
    for ref in MODULE_REFS:
        path = REFS_DIR / ref
        if not _file_exists(path):
            continue
        content = _read(path)
        for kw in FOUR_STAGE_KEYWORDS:
            _require(kw in content,
                     f"4stage-check: {ref} 缺 4 段式关键词 '{kw}'")


def validate_m1_worldbuilding() -> None:
    """校验 worldbuilding-guide.md 含 M1 关键词。"""
    path = REFS_DIR / "worldbuilding-guide.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in M1_KEYWORDS:
        _require(kw in content,
                 f"m1-worldbuilding: 缺关键词 '{kw}'")


def validate_m2_character() -> None:
    """校验 character-design.md 含 M2 关键词。"""
    path = REFS_DIR / "character-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in M2_KEYWORDS:
        _require(kw in content,
                 f"m2-character: 缺关键词 '{kw}'")


def validate_m3_power() -> None:
    """校验 power-system-guide.md 含 M3 关键词。"""
    path = REFS_DIR / "power-system-guide.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in M3_KEYWORDS:
        _require(kw in content,
                 f"m3-power: 缺关键词 '{kw}'")


def validate_m4_item() -> None:
    """校验 item-design.md 含 M4 关键词。"""
    path = REFS_DIR / "item-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in M4_KEYWORDS:
        _require(kw in content,
                 f"m4-item: 缺关键词 '{kw}'")


def validate_m5_relationship() -> None:
    """校验 relationship-design.md 含 M5 关键词。"""
    path = REFS_DIR / "relationship-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in M5_KEYWORDS:
        _require(kw in content,
                 f"m5-relationship: 缺关键词 '{kw}'")


def validate_kb_consistency() -> None:
    """校验 5 reference 各自含知识库路径引用 + 模板同步说明。"""
    for ref in MODULE_REFS:
        path = REFS_DIR / ref
        if not _file_exists(path):
            continue
        content = _read(path)
        _require("知识库/" in content,
                 f"kb-consistency: {ref} 缺'知识库/'路径引用")


def validate_draft_isolation() -> None:
    """校验未人审的设定卡草稿不会写入正式知识库路径。"""
    formal_draft_patterns = {
        "character-design.md": "每人物独立卡 `知识库/人物/X.md`",
        "power-system-guide.md": "每境界/技能卡 `知识库/概念/X.md`",
        "item-design.md": "每物品卡 `知识库/物品/X.md`",
        "relationship-design.md": "每势力卡 `知识库/势力/X.md`",
    }
    for ref, forbidden in formal_draft_patterns.items():
        path = REFS_DIR / ref
        if not _file_exists(path):
            continue
        content = _read(path)
        _require(forbidden not in content,
                 f"draft-isolation: {ref} spec 阶段不得把草稿写入正式知识库路径")
        _require("知识库/暂存区/设计提案" in content,
                 f"draft-isolation: {ref} 缺暂存区设计提案路径")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的所有 references/X-*.md 路径都存在。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for ref in MODULE_REFS:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "5m-routing": validate_five_m_routing,
    "5m-overview": validate_five_m_overview,
    "4stage-check": validate_four_stage,
    "m1-worldbuilding": validate_m1_worldbuilding,
    "m2-character": validate_m2_character,
    "m3-power": validate_m3_power,
    "m4-item": validate_m4_item,
    "m5-relationship": validate_m5_relationship,
    "kb-consistency": validate_kb_consistency,
    "draft-isolation": validate_draft_isolation,
    "cross-refs": validate_cross_refs,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="novel-design v3 校验")
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
