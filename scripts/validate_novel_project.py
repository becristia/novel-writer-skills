"""Read-only consistency checks for a live novel project using this skill pack.

Usage:
    python3 scripts/validate_novel_project.py --project-root /path/to/novel
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_TASK_STATUSES = {
    "planned",
    "drafting",
    "self_checked",
    "human_review",
    "finalized",
    "kb_reviewed",
}

REQUIRED_CHAPTER_GATE_FIELDS = [
    "outline_ready",
    "draft_ready",
    "self_check_passed",
    "human_finalized",
    "knowledge_reviewed",
    "blocked_reason",
]


class ValidationError(Exception):
    """Project validation failed."""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_progress(project_root: Path, errors: list[str]) -> dict:
    path = project_root / "进度.json"
    if not path.is_file():
        errors.append("progress: missing 进度.json")
        return {}
    try:
        data = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        errors.append(f"progress: 进度.json is not valid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append("progress: 进度.json root must be an object")
        return {}
    return data


def validate_progress_gates(progress: dict, errors: list[str]) -> None:
    gates = progress.get("workflow_gates")
    if not isinstance(gates, dict):
        errors.append("workflow_gates: missing object")
        return

    if "chapter" in gates:
        errors.append("workflow_gates: do not use singleton workflow_gates.chapter")

    chapters = gates.get("chapters")
    if not isinstance(chapters, dict):
        errors.append("workflow_gates: chapters must be an object keyed by 场景任务ID")

    template = gates.get("chapter_gate_template")
    if not isinstance(template, dict):
        errors.append("workflow_gates: missing chapter_gate_template")
    else:
        for field in REQUIRED_CHAPTER_GATE_FIELDS:
            if field not in template:
                errors.append(f"workflow_gates: chapter_gate_template missing {field}")

    if not isinstance(chapters, dict):
        return

    for task_id, gate in chapters.items():
        if not isinstance(gate, dict):
            errors.append(f"workflow_gates.chapters.{task_id}: gate must be an object")
            continue
        scene_task_id = gate.get("scene_task_id")
        if scene_task_id and scene_task_id != task_id:
            errors.append(
                f"workflow_gates.chapters.{task_id}: scene_task_id mismatch ({scene_task_id})"
            )
        for field in REQUIRED_CHAPTER_GATE_FIELDS:
            if field not in gate:
                errors.append(f"workflow_gates.chapters.{task_id}: missing {field}")


def _table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def validate_writing_tasks(project_root: Path, progress: dict, errors: list[str]) -> None:
    task_path = project_root / "追踪" / "写作任务.md"
    structure_done = progress.get("checks", {}).get("structure_done") is True
    write_active = progress.get("phases", {}).get("write", {}).get("status") == "in_progress"
    if not task_path.is_file():
        if structure_done or write_active or (project_root / "追踪").exists():
            errors.append("tracking: missing 追踪/写作任务.md")
        return

    rows = _table_rows(_read(task_path))
    header_index = next(
        (index for index, row in enumerate(rows) if "场景任务ID" in row and "当前状态" in row),
        None,
    )
    if header_index is None:
        errors.append("tracking: 追踪/写作任务.md missing task matrix header")
        return

    header = rows[header_index]
    task_id_index = header.index("场景任务ID")
    status_index = header.index("当前状态")

    for row in rows[header_index + 1:]:
        if len(row) <= max(task_id_index, status_index):
            continue
        task_id = row[task_id_index]
        status = row[status_index]
        if not task_id or task_id == "场景任务ID":
            continue
        matched = [item for item in ALLOWED_TASK_STATUSES if item in status]
        if status not in ALLOWED_TASK_STATUSES:
            errors.append(
                f"tracking: {task_id} 当前状态 must be one of {sorted(ALLOWED_TASK_STATUSES)}, got {status!r}"
            )
            continue
        if len(matched) != 1 or "/" in status or "->" in status:
            errors.append(f"tracking: {task_id} 当前状态 must contain exactly one status")


def validate_outline_bindings(project_root: Path, errors: list[str]) -> None:
    outline_root = project_root / "03-大纲"
    if not outline_root.exists():
        return

    outline_files = sorted(outline_root.rglob("*.md"))
    for path in outline_files:
        if "细纲" not in path.name:
            continue
        content = _read(path)
        if "核心事件" not in content and "章节元数据" not in content:
            continue
        rel_path = path.relative_to(project_root)
        if "情节线ID" not in content:
            errors.append(f"outline: {rel_path} missing 情节线ID")
        if "场景任务ID" not in content:
            errors.append(f"outline: {rel_path} missing 场景任务ID")


def validate_project(project_root: Path) -> None:
    errors: list[str] = []
    if not project_root.is_dir():
        raise ValidationError(f"project root not found: {project_root}")

    progress = _load_progress(project_root, errors)
    if progress:
        validate_progress_gates(progress, errors)
    validate_writing_tasks(project_root, progress, errors)
    validate_outline_bindings(project_root, errors)

    if errors:
        raise ValidationError("\n".join(f"- {error}" for error in errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a live novel project.")
    parser.add_argument("--project-root", required=True, type=Path)
    args = parser.parse_args()

    try:
        validate_project(args.project_root.resolve())
    except ValidationError as exc:
        print(f"FAIL project: {exc}", file=sys.stderr)
        return 1

    print(f"OK project: {args.project_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
