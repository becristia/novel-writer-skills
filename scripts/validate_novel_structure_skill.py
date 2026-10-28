"""novel-structure skill 静态校验脚本。

校验 SKILL.md 与 references/ 的 v3 完整性。

用法：
    python scripts/validate_novel_structure_skill.py --template <name>
    python scripts/validate_novel_structure_skill.py --all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "novel-structure"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Design §2.3 — 10 段标题按顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口路由",
    "调用前自检",
    "3 层顺序循环",
    "3 层之间的衔接",
    "调用频率与触发器",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
]

# 3 reference 文件名
LAYER_REFS = [
    "main-plot-design.md",
    "map-design.md",
    "chapter-outline-design.md",
]

OPENING_REF = "opening-design.md"

# 4 段式关键词（每个 reference 都应含）
FOUR_STAGE_KEYWORDS = ["brainstorming", "spec", "execution", "validation"]

# 每层特定关键词
L1_KEYWORDS = ["主线", "三幕", "关键节点", "卷划分", "伏笔", "情绪曲线", "场景分布"]
L2_KEYWORDS = ["地图", "核心事件", "BOSS", "伏笔", "情绪曲线", "末尾钩子"]
L3_KEYWORDS = ["细纲", "核心事件", "冲突", "爽点", "节奏", "伏笔", "关联词条", "钩子"]
CHAPTER_METADATA_KEYWORDS = [
    "章节元数据",
    "POV",
    "场景地点",
    "故事时间",
    "出场人物",
    "知识库更新标记",
    "追踪更新",
]
PLOTLINE_TASK_KEYWORDS = [
    "情节线ID",
    "场景任务ID",
    "追踪/情节线.md",
    "追踪/写作任务.md",
    "任务状态",
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
    """校验 SKILL.md 含 10 段 + ≤280 行。"""
    _require(_file_exists(SKILL_MD), "skill-md: 文件不存在")

    content = _read(SKILL_MD)
    lines = content.splitlines()
    _require(len(lines) <= 280, f"skill-md: 行数超 280（实际 {len(lines)}）")

    for sec in REQUIRED_SKILL_SECTIONS:
        _require(f"## {sec}" in content, f"skill-md: 缺段 '## {sec}'")


def validate_three_l_routing() -> None:
    """校验 SKILL.md §3 含入口路由表（≥ 8 行）。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    # 段 3 必须含 3 层 + novel-structure 关键词
    for keyword in ["Layer 1", "Layer 2", "Layer 3", "novel-structure"]:
        _require(keyword in content,
                 f"3l-routing: 入口路由表缺关键词 '{keyword}'")


def validate_three_l_overview() -> None:
    """校验 SKILL.md §5 含 Layer 1/2/3 标题 + 3 个 reference 引用。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for layer in ["Layer 1", "Layer 2", "Layer 3"]:
        _require(f"### {layer}" in content,
                 f"3l-overview: 缺 '### {layer}：' 段")

    for ref in LAYER_REFS:
        _require(ref in content,
                 f"3l-overview: 段 5 缺 'references/{ref}' 外链")


def validate_four_stage() -> None:
    """校验 3 reference 各自含 4 段式 4 关键词。"""
    for ref in LAYER_REFS:
        path = REFS_DIR / ref
        if not _file_exists(path):
            continue
        content = _read(path)
        for kw in FOUR_STAGE_KEYWORDS:
            _require(kw in content,
                     f"4stage-check: {ref} 缺 4 段式关键词 '{kw}'")


def validate_l1_main_plot() -> None:
    """校验 main-plot-design.md 含 L1 关键词。"""
    path = REFS_DIR / "main-plot-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in L1_KEYWORDS:
        _require(kw in content,
                 f"l1-main-plot: 缺关键词 '{kw}'")


def validate_l2_map() -> None:
    """校验 map-design.md 含 L2 关键词。"""
    path = REFS_DIR / "map-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in L2_KEYWORDS:
        _require(kw in content,
                 f"l2-map: 缺关键词 '{kw}'")


def validate_l3_chapter_outline() -> None:
    """校验 chapter-outline-design.md 含 L3 关键词。"""
    path = REFS_DIR / "chapter-outline-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in L3_KEYWORDS:
        _require(kw in content,
                 f"l3-chapter-outline: 缺关键词 '{kw}'")


def validate_chapter_metadata_contract() -> None:
    """校验 L3 细纲携带章节级元数据，便于正文与知识库追踪。"""
    path = REFS_DIR / "chapter-outline-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in CHAPTER_METADATA_KEYWORDS:
        _require(kw in content,
                 f"chapter-metadata: 缺关键词 '{kw}'")


def validate_plotline_task_contract() -> None:
    """校验 L3 细纲能写入情节线与场景任务矩阵。"""
    path = REFS_DIR / "chapter-outline-design.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in PLOTLINE_TASK_KEYWORDS:
        _require(kw in content,
                 f"plotline-task: 缺关键词 '{kw}'")


def validate_pacing_check() -> None:
    """校验 3 reference 各自含节奏密度自检段落（含 场景/日常 关键词）。"""
    for ref in LAYER_REFS:
        path = REFS_DIR / ref
        if not _file_exists(path):
            continue
        content = _read(path)
        for kw in ["场景", "日常"]:
            _require(kw in content,
                     f"pacing-check: {ref} 缺节奏密度自检关键词 '{kw}'")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的所有 references/L*.md 路径都存在。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for ref in LAYER_REFS:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


def validate_opening_gate() -> None:
    """Ensure the golden opening guide is part of the main structure flow."""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)
    _require(OPENING_REF in content,
             f"opening-gate: SKILL.md 缺 'references/{OPENING_REF}' 引用")
    _require("前三章" in content and "开篇" in content and "人审" in content,
             "opening-gate: SKILL.md 缺前三章开篇人审闸门")
    _require(_file_exists(REFS_DIR / OPENING_REF),
             f"opening-gate: references/{OPENING_REF} 不存在")


def validate_state_update_wording() -> None:
    """Ensure structure planning does not imply ungated progress writes."""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)
    for forbidden in ("写 spec + 更新进度", "execution（写 spec + 更新进度）"):
        _require(forbidden not in content,
                 f"state-wording: SKILL.md 不应写 '{forbidden}'")
    _require("进度变更提案" in content and "人审后写入" in content,
             "state-wording: SKILL.md 缺结构期进度变更人审口径")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "3l-routing": validate_three_l_routing,
    "3l-overview": validate_three_l_overview,
    "4stage-check": validate_four_stage,
    "l1-main-plot": validate_l1_main_plot,
    "l2-map": validate_l2_map,
    "l3-chapter-outline": validate_l3_chapter_outline,
    "chapter-metadata": validate_chapter_metadata_contract,
    "plotline-task": validate_plotline_task_contract,
    "pacing-check": validate_pacing_check,
    "cross-refs": validate_cross_refs,
    "opening-gate": validate_opening_gate,
    "state-wording": validate_state_update_wording,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="novel-structure v3 校验")
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
