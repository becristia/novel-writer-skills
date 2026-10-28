"""novel-meta skill 静态校验脚本。

校验 SKILL.md 与 references/ 的 v3 完整性。

用法：
    python scripts/validate_novel_meta_skill.py --template <name>
    python scripts/validate_novel_meta_skill.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "novel-meta"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Design §3.1 — 10 段标题按顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口路由",
    "调用前自检",
    "4 M 子流程概览",
    "M 之间的协作",
    "调用频率与触发器",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
]

# M1 4 关键步骤关键词
M1_KEYWORDS = ["范围评估", "讨论改动", "执行改动", "M4 验证"]

# M2 3 段式关键词
M2_KEYWORDS = ["读当前", "对话", "写入"]

# M3 4 段式关键词
M3_KEYWORDS = ["盘点", "范围", "执行", "同步"]

# M4 stub 关键词
M4_KEYWORDS = ["唯一权威", "agent-dispatch", "parallel-audit-subagent.md", "docs/reviews/"]

# M4 4 视角名
M4_FOUR_LENSES = ["流程合规", "配置一致", "模板对齐", "触发器"]


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


def validate_four_m_routing() -> None:
    """校验 SKILL.md §3 含入口路由表（≥ 7 行）。"""
    if not _file_exists(SKILL_MD):
        return  # skill-md already flagged
    content = _read(SKILL_MD)

    # 段 3 必须含 4 个 M 名 + "novel-meta 是干嘛的"
    for keyword in ["M1", "M2", "M3", "M4", "novel-meta"]:
        _require(keyword in content,
                 f"4m-routing: 入口路由表缺关键词 '{keyword}'")

    # 入口路由表行数：## 入口路由 段内 '\n|' 起始的行 ≥ 7
    section = re.search(r"## 入口路由(.*?)(?=^## |\Z)", content, re.S | re.M)
    _require(section is not None and section.group(1).count("\n|") >= 7,
             "4m-routing: 入口路由表行数 < 7")


def validate_four_m_overview() -> None:
    """校验 SKILL.md §5 含 4 个 ### M1/M2/M3/M4: 标题 + references 引用。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for m in ["M1", "M2", "M3", "M4"]:
        _require(f"### {m}" in content,
                 f"4m-overview: 缺 '### {m}：' 段")

    # 4 个 references 引用
    for ref in ["m1-skill-evolution.md", "m2-config-panel.md",
                "m3-template-governance.md", "m4-eval-harness.md"]:
        _require(ref in content,
                 f"4m-overview: 段 5 缺 'references/{ref}' 外链")


def validate_m1_evolution() -> None:
    """校验 m1-skill-evolution.md 含 4 关键步骤。"""
    path = REFS_DIR / "m1-skill-evolution.md"
    _require(_file_exists(path), "m1-evolution: 文件不存在")

    content = _read(path)
    for kw in M1_KEYWORDS:
        _require(kw in content,
                 f"m1-evolution: 缺关键词 '{kw}'")


def validate_m2_config() -> None:
    """校验 m2-config-panel.md 含 3 段式 + 提及 novel-config。"""
    path = REFS_DIR / "m2-config-panel.md"
    _require(_file_exists(path), "m2-config: 文件不存在")

    content = _read(path)
    for kw in M2_KEYWORDS:
        _require(kw in content,
                 f"m2-config: 缺关键词 '{kw}'")
    _require("novel-config" in content,
             "m2-config: 必须提及 novel-config.json")
    _require("或 0" not in content,
             "m2-config: 0 是零容忍阈值，不应被描述为禁用检测")


def validate_m3_templates() -> None:
    """校验 m3-template-governance.md 含 4 段式 + 提及 assets/。"""
    path = REFS_DIR / "m3-template-governance.md"
    _require(_file_exists(path), "m3-templates: 文件不存在")

    content = _read(path)
    for kw in M3_KEYWORDS:
        _require(kw in content,
                 f"m3-templates: 缺关键词 '{kw}'")
    _require("assets/" in content,
             "m3-templates: 必须提及 assets/")
    for template in (
        "tracking-active-context-template.md",
        "tracking-writing-tasks-template.md",
        "assets/灵感/灵感卡.md",
    ):
        _require(template in content,
                 f"m3-templates: 模板治理清单缺 {template}")
    _require("16 个模板 + 1 个 CHANGELOG" in content,
             "m3-templates: 模板总数说明过期")


def validate_m4_eval() -> None:
    """校验 m4-eval-harness.md 已降为短迁移 stub。"""
    path = REFS_DIR / "m4-eval-harness.md"
    _require(_file_exists(path), "m4-eval: 文件不存在")

    content = _read(path)
    _require(len(content.splitlines()) <= 80,
             "m4-eval: 历史归档 stub 不应超过 80 行")
    for kw in M4_KEYWORDS:
        _require(kw in content,
                 f"m4-eval: 缺关键词 '{kw}'")


def validate_m4_four_lenses() -> None:
    """校验 m4-eval-harness.md 指向 agent-dispatch 维护的 4 视角。"""
    path = REFS_DIR / "m4-eval-harness.md"
    if not _file_exists(path):
        return  # m4-eval flagged
    content = _read(path)
    for lens in M4_FOUR_LENSES:
        _require(lens in content,
                 f"m4-four-lenses: 缺视角 '{lens}'")


def validate_m4_report_path() -> None:
    """校验 m4-eval-harness.md 含报告路径模板。"""
    path = REFS_DIR / "m4-eval-harness.md"
    if not _file_exists(path):
        return
    content = _read(path)
    _require("docs/reviews/" in content and "audit.md" in content,
             "m4-report-path: 缺 'docs/reviews/<date>-<skill>-audit.md' 报告路径模板")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的所有 references/mN-X.md 路径都存在。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for ref in ["m1-skill-evolution.md", "m2-config-panel.md",
                "m3-template-governance.md", "m4-eval-harness.md"]:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "4m-routing": validate_four_m_routing,
    "4m-overview": validate_four_m_overview,
    "m1-evolution": validate_m1_evolution,
    "m2-config": validate_m2_config,
    "m3-templates": validate_m3_templates,
    "m4-eval": validate_m4_eval,
    "m4-four-lenses": validate_m4_four_lenses,
    "m4-report-path": validate_m4_report_path,
    "cross-refs": validate_cross_refs,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="novel-meta v3 校验")
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
