"""agent-dispatch skill 静态校验脚本。

校验 SKILL.md / references/ 与跨 skill 引用 4 项。

用法：
    python scripts/validate_agent_dispatch_skill.py --template <name>
    python scripts/validate_agent_dispatch_skill.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = PROJECT_ROOT / "skills" / "agent-dispatch"
REFS_DIR = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"

# Design §2.3 — 10 段标题按顺序
REQUIRED_SKILL_SECTIONS = [
    "核心理念",
    "整体架构图",
    "入口路由",
    "调用前自检",
    "2 模式子流程概览",
    "与 novel-write / novel-meta 的接口契约",
    "调用频率与触发器",
    "错误处理矩阵",
    "与 superpowers 对应",
    "输出文件",
]

# 2 模式关键词
MODE_KEYWORDS = ["模式 1", "模式 2"]

# 接口契约关键词
INTERFACE_KEYWORDS = ["novel-write", "novel-meta"]

# 每模式特定关键词
WRITE_MODE_KEYWORDS = ["压缩包", "细纲", "摘要", "标题", "上下文隔离"]
AUDIT_MODE_KEYWORDS = ["并行", "4 视角", "合规", "一致", "对齐"]

# 跨 skill 引用 4 项（v0.4 新增）
WRITE_SKILL_MD = PROJECT_ROOT / "skills" / "novel-write" / "SKILL.md"
WRITE_REF_MD = PROJECT_ROOT / "skills" / "novel-write" / "references" / "subagent-prompt-template.md"
META_SKILL_MD = PROJECT_ROOT / "skills" / "novel-meta" / "SKILL.md"
META_REF_MD = PROJECT_ROOT / "skills" / "novel-meta" / "references" / "m4-eval-harness.md"


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


def validate_two_mode_routing() -> None:
    """校验 SKILL.md §3 含 2 模式入口路由。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for keyword in MODE_KEYWORDS:
        _require(keyword in content,
                 f"2mode-routing: 入口路由缺关键词 '{keyword}'")


def validate_interface_contract() -> None:
    """校验 SKILL.md §6 含 novel-write / novel-meta 接口契约。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for keyword in INTERFACE_KEYWORDS:
        _require(keyword in content,
                 f"interface-contract: 接口契约缺关键词 '{keyword}'")


def validate_write_mode() -> None:
    """校验 write-chapter-subagent.md 含 5 关键词。"""
    path = REFS_DIR / "write-chapter-subagent.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in WRITE_MODE_KEYWORDS:
        _require(kw in content,
                 f"write-mode: 缺关键词 '{kw}'")
    for kw in ("必须先通过 novel-write 调用前自检", "情节线ID",
               "场景任务ID", "workflow_gates.chapters"):
        _require(kw in content,
                 f"write-mode: 缺门禁关键词 '{kw}'")


def validate_audit_mode() -> None:
    """校验 parallel-audit-subagent.md 含 5 关键词。"""
    path = REFS_DIR / "parallel-audit-subagent.md"
    if not _file_exists(path):
        return
    content = _read(path)
    for kw in AUDIT_MODE_KEYWORDS:
        _require(kw in content,
                 f"audit-mode: 缺关键词 '{kw}'")


def validate_4stage_check() -> None:
    """校验 2 reference 各含 4 段式关键词。"""
    for ref in ["write-chapter-subagent.md", "parallel-audit-subagent.md"]:
        path = REFS_DIR / ref
        if not _file_exists(path):
            continue
        content = _read(path)
        for kw in ["步骤①", "步骤②", "步骤③", "步骤④"]:
            _require(kw in content,
                     f"4stage-check: {ref} 缺步骤 '{kw}'")


def validate_cross_refs() -> None:
    """校验 SKILL.md 引用的 2 个 reference 都存在。"""
    if not _file_exists(SKILL_MD):
        return
    content = _read(SKILL_MD)

    for ref in ["write-chapter-subagent.md", "parallel-audit-subagent.md"]:
        path = REFS_DIR / ref
        _require(_file_exists(path),
                 f"cross-refs: SKILL.md 引用 'references/{ref}' 不存在")


# === 跨 skill 引用验证（v0.4 新增）===

def validate_cross_write_skill() -> None:
    """校验 novel-write SKILL.md 含 agent-dispatch 引用。"""
    if not _file_exists(WRITE_SKILL_MD):
        return
    content = _read(WRITE_SKILL_MD)
    _require("agent-dispatch" in content,
             "cross-write: novel-write SKILL.md 缺 'agent-dispatch' 引用")


def validate_cross_write_ref() -> None:
    """校验 novel-write subagent-prompt-template.md 含 agent-dispatch 引用。"""
    if not _file_exists(WRITE_REF_MD):
        return
    content = _read(WRITE_REF_MD)
    _require("agent-dispatch" in content,
             "cross-write-ref: novel-write subagent-prompt-template.md 缺 'agent-dispatch' 引用")


def validate_cross_meta_skill() -> None:
    """校验 novel-meta SKILL.md 含 agent-dispatch 引用。"""
    if not _file_exists(META_SKILL_MD):
        return
    content = _read(META_SKILL_MD)
    _require("agent-dispatch" in content,
             "cross-meta: novel-meta SKILL.md 缺 'agent-dispatch' 引用")


def validate_cross_meta_ref() -> None:
    """校验 novel-meta m4-eval-harness.md 含 agent-dispatch 引用。"""
    if not _file_exists(META_REF_MD):
        return
    content = _read(META_REF_MD)
    _require("agent-dispatch" in content,
             "cross-meta-ref: novel-meta m4-eval-harness.md 缺 'agent-dispatch' 引用")


VALIDATORS = {
    "skill-md": validate_skill_md,
    "2mode-routing": validate_two_mode_routing,
    "interface-contract": validate_interface_contract,
    "4stage-check": validate_4stage_check,
    "write-mode": validate_write_mode,
    "audit-mode": validate_audit_mode,
    "cross-refs": validate_cross_refs,
    "cross-write": validate_cross_write_skill,
    "cross-write-ref": validate_cross_write_ref,
    "cross-meta": validate_cross_meta_skill,
    "cross-meta-ref": validate_cross_meta_ref,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="agent-dispatch v0.4 校验")
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
