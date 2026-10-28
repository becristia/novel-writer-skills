"""inspiration skill 静态校验脚本。

校验 SKILL.md / references/ 与 6 维度子目录。

用法：
    python scripts/validate_inspiration_skill.py --template <name>
    python scripts/validate_inspiration_skill.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / "skills" / "inspiration"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"
INSPIRATION_ASSETS = PROJECT_ROOT / "assets" / "灵感"
INSPIRATION_CARD = INSPIRATION_ASSETS / "灵感卡.md"

# Design §2.3 — 10 段标题按顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口路由",
    "调用前自检",
    "灵感生命周期",
    "灵感状态迁移",
    "调用频率与触发器",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
]

# 5 步生命周期关键词
STEP_KEYWORDS = ["步骤①", "步骤②", "步骤③", "步骤④", "步骤⑤"]

# 3 态迁移关键词
STATE_KEYWORDS = ["active", "dormant", "promoted"]

# 6 维度分类关键词
SIX_DIM_KEYWORDS = ["人物", "情节", "伏笔", "世界", "金句", "其他"]

# 双人对谈关键词
DIALOGUE_KEYWORDS = ["反驳", "采纳", "反对", "搁置"]

# 与 novel-ideate 弱契约（v0.4 阶段不阻塞）
NOVEL_IDEATE_SKILL_MD = PROJECT_ROOT / "skills" / "novel-ideate" / "SKILL.md"


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


def validate_five_step() -> None:
    """校验 SKILL.md §5 含 5 步生命周期。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)
    for kw in STEP_KEYWORDS:
        _require(kw in content,
                 f"5step: 生命周期缺步骤 '{kw}'")


def validate_state_migration() -> None:
    """校验 SKILL.md §6 含 3 态迁移。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)
    for kw in STATE_KEYWORDS:
        _require(kw in content,
                 f"state-migration: 3 态迁移缺关键词 '{kw}'")


def validate_six_dimensions() -> None:
    """校验 SKILL.md + 灵感分类.md 含 6 维度关键词。"""
    combined = ""
    if _file_exists(SKILL_MD):
        combined += _read(SKILL_MD)
    ref_path = REFS_DIR / "灵感分类.md"
    if _file_exists(ref_path):
        combined += _read(ref_path)

    for kw in SIX_DIM_KEYWORDS:
        _require(kw in combined,
                 f"6-dimensions: 6 维度分类缺关键词 '{kw}'")


def validate_dialogue() -> None:
    """校验 SKILL.md §5 + 双人对谈.md 含对话关键词。"""
    combined = ""
    if _file_exists(SKILL_MD):
        combined += _read(SKILL_MD)
    ref_path = REFS_DIR / "双人对谈.md"
    if _file_exists(ref_path):
        combined += _read(ref_path)

    for kw in DIALOGUE_KEYWORDS:
        _require(kw in combined,
                 f"dialogue: 双人对谈缺关键词 '{kw}'")


def validate_card_template() -> None:
    """校验 assets/灵感/灵感卡.md 含 7 H2 段 + **字段**：值 格式。"""
    _require(_file_exists(INSPIRATION_CARD),
             f"card-template: {INSPIRATION_CARD} 不存在")

    content = _read(INSPIRATION_CARD)
    # 7 H2 段
    h2_count = len(re.findall(r"^## ", content, re.M))
    _require(h2_count == 7,
             f"card-template: 7 H2 段校验失败（实际 {h2_count}）")

    # 至少 1 个 **字段**：值 行
    field_lines = re.findall(r"^\*\*[^*]+\*\*：", content, re.M)
    _require(len(field_lines) >= 1,
             f"card-template: 缺 '**字段**：值' 格式行")


def validate_six_dim_subdirs() -> None:
    """校验 assets/灵感/ 含 6 个维度子目录。"""
    _require(INSPIRATION_ASSETS.is_dir(),
             f"6-dim-subdirs: {INSPIRATION_ASSETS} 不存在")

    for dim in SIX_DIM_KEYWORDS:
        path = INSPIRATION_ASSETS / dim
        _require(path.is_dir(),
                 f"6-dim-subdirs: 子目录 '{dim}/' 不存在")


def validate_novel_ideate_contract() -> None:
    """校验 novel-ideate SKILL.md 含 'inspiration' 引用（v0.4 弱约束，不阻塞）。"""
    if not _file_exists(NOVEL_IDEATE_SKILL_MD):
        return  # novel-ideate 不存在 → 跳过
    content = _read(NOVEL_IDEATE_SKILL_MD)
    # 弱约束：INFO 提示，不 FAIL
    # 实际：仅当含 'inspiration' 字符串时 PASS；否则 WARN
    if "inspiration" not in content:
        # 不 raise，仅 print（避免 FAIL 阻塞 v0.4 阶段）
        print(f"INFO: novel-ideate/SKILL.md 缺 'inspiration' 引用（v0.4 弱约束，可后续 refactor）")


def validate_output_paths() -> None:
    """校验灵感卡 live 输出不写入 assets/ 模板目录。"""
    if not _file_exists(SKILL_MD):
        return
    combined = _read(SKILL_MD)
    for ref in ("灵感分类.md", "双人对谈.md"):
        path = REFS_DIR / ref
        if _file_exists(path):
            combined += "\n" + _read(path)

    forbidden = (
        "写入：assets/灵感",
        "写入 `assets/灵感",
        "写入 assets/灵感",
        "`assets/灵感/<类型>/<灵感简述>.md`",
    )
    for pattern in forbidden:
        _require(pattern not in combined,
                 f"output-paths: live 灵感卡不得写入 assets/（发现 {pattern!r}）")
    _require("项目根 `灵感/" in combined or "项目根目录 `灵感/" in combined,
             "output-paths: 缺项目根 灵感/ 作为 live 输出目录")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的 2 reference 都存在。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for ref in ["灵感分类.md", "双人对谈.md"]:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "5step": validate_five_step,
    "state-migration": validate_state_migration,
    "6-dimensions": validate_six_dimensions,
    "dialogue": validate_dialogue,
    "card-template": validate_card_template,
    "6-dim-subdirs": validate_six_dim_subdirs,
    "novel-ideate-contract": validate_novel_ideate_contract,
    "output-paths": validate_output_paths,
    "cross-refs": validate_cross_refs,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="inspiration v0.4 校验")
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
