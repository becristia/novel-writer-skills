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

if __package__:
    from . import validate_assets
else:
    import validate_assets

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

PHASES = ("ideate", "design", "structure", "write")
TASK_GATE_REQUIREMENTS = {
    "drafting": "outline_ready",
    "self_checked": "draft_ready",
    "human_review": "self_check_passed",
    "finalized": "human_finalized",
    "kb_reviewed": "knowledge_reviewed",
}


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


def _object(data: dict, key: str, errors: list[str], label: str = "") -> dict:
    value = data.get(key)
    if not isinstance(value, dict):
        errors.append(f"{label + '.' if label else ''}{key}: missing object")
        return {}
    return value


def _boolean(data: dict, key: str, label: str, errors: list[str]) -> None:
    if type(data.get(key)) is not bool:
        errors.append(f"{label}.{key}: must be a JSON boolean")


def _chapter_gate(gate: dict, label: str, errors: list[str]) -> None:
    flags = REQUIRED_CHAPTER_GATE_FIELDS[:-1]
    for index, field in enumerate(flags):
        _boolean(gate, field, label, errors)
        if gate.get(field) is True:
            for previous in flags[:index]:
                if gate.get(previous) is not True:
                    errors.append(f"{label}.{field}: requires {previous}=true")
    for field in ("chapter_id", "scene_task_id", "status", "blocked_reason", "approved_by", "approved_at"):
        if not isinstance(gate.get(field), str):
            errors.append(f"{label}.{field}: must be a string")
    for field in ("chapter_id", "scene_task_id", "status"):
        if isinstance(gate.get(field), str) and not gate[field].strip():
            errors.append(f"{label}.{field}: must not be empty")


def validate_progress_gates(progress: dict, errors: list[str]) -> None:
    gates = _object(progress, "workflow_gates", errors)
    checks = _object(progress, "checks", errors)
    phases = _object(progress, "phases", errors)

    for index, phase in enumerate(PHASES):
        phase_data = _object(phases, phase, errors, "phases")
        status = phase_data.get("status")
        if not isinstance(status, str) or status not in {"pending", "in_progress", "done"}:
            errors.append(f"phases.{phase}.status: must be pending / in_progress / done")
        if status in ("in_progress", "done"):
            for previous in PHASES[:index]:
                if checks.get(previous + "_done") is not True:
                    errors.append(f"phases.{phase}: requires checks.{previous}_done=true")
        if phase == "write":
            continue
        check = phase + "_done"
        _boolean(checks, check, "checks", errors)
        stage = _object(gates, phase, errors, "workflow_gates")
        _boolean(stage, "human_approved", f"workflow_gates.{phase}", errors)
        if phase == "structure":
            _boolean(stage, "outline_ready", "workflow_gates.structure", errors)
        if checks.get(check) is True or status == "done":
            if checks.get(check) is not True or status != "done":
                errors.append(f"checks.{check}: must agree with phases.{phase}.status=done")
            if stage.get("human_approved") is not True:
                errors.append(f"workflow_gates.{phase}.human_approved: requires true for phase completion")
            if phase == "structure" and stage.get("outline_ready") is not True:
                errors.append("workflow_gates.structure: completion requires outline_ready=true")

    current = progress.get("current_phase")
    if not isinstance(current, str) or current not in PHASES:
        errors.append("current_phase: must be ideate / design / structure / write")
    else:
        for previous in PHASES[:PHASES.index(current)]:
            if checks.get(previous + "_done") is not True:
                errors.append(f"current_phase={current}: requires checks.{previous}_done=true")

    if "chapter" in gates:
        errors.append("workflow_gates: do not use singleton workflow_gates.chapter")

    chapters = gates.get("chapters")
    if not isinstance(chapters, dict):
        errors.append("workflow_gates: chapters must be an object keyed by 场景任务ID")

    template = gates.get("chapter_gate_template")
    if not isinstance(template, dict):
        errors.append("workflow_gates: missing chapter_gate_template")
    else:
        _chapter_gate(template, "workflow_gates.chapter_gate_template", errors)

    if not isinstance(chapters, dict):
        return

    for task_id, gate in chapters.items():
        if not isinstance(gate, dict):
            errors.append(f"workflow_gates.chapters.{task_id}: gate must be an object")
            continue
        scene_task_id = gate.get("scene_task_id")
        if scene_task_id != task_id:
            errors.append(
                f"workflow_gates.chapters.{task_id}: scene_task_id mismatch ({scene_task_id})"
            )
        _chapter_gate(gate, f"workflow_gates.chapters.{task_id}", errors)


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


def _read_matrix(path: Path, id_column: str, prefix: str, columns: tuple[str, ...],
                 errors: list[str]) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    for match in re.finditer(r"(?:^[ \t]*\|[^\n]*\|[ \t]*(?:\n|$))+", _read(path), re.M):
        rows = _table_rows(match.group())
        if not rows or not all(column in rows[0] for column in (id_column, *columns)):
            continue
        header = rows[0]
        records = {}
        for row in rows[1:]:
            if len(row) != len(header):
                errors.append(f"tracking: {path.name} has a malformed matrix row")
                continue
            record = dict(zip(header, row))
            record_id = record[id_column]
            if not record_id:
                continue
            if not re.fullmatch(rf"{prefix}-\d+", record_id):
                errors.append(f"tracking: invalid {id_column} {record_id!r}")
            elif record_id in records:
                errors.append(f"tracking: duplicate {id_column} {record_id}")
            else:
                records[record_id] = record
        return records
    errors.append(f"tracking: {path.name} missing {id_column} matrix header")
    return {}


def validate_writing_tasks(project_root: Path, progress: dict, errors: list[str]) -> dict:
    task_path = project_root / "追踪" / "写作任务.md"
    checks = progress.get("checks")
    phases = progress.get("phases")
    structure_done = isinstance(checks, dict) and checks.get("structure_done") is True
    write = phases.get("write") if isinstance(phases, dict) else None
    write_active = isinstance(write, dict) and write.get("status") == "in_progress"
    if not task_path.is_file():
        if structure_done or write_active or (project_root / "追踪").exists():
            errors.append("tracking: missing 追踪/写作任务.md")
        return {}

    tasks = _read_matrix(task_path, "场景任务ID", "WT", ("当前状态", "情节线ID"), errors)
    gates = progress.get("workflow_gates")
    chapters = gates.get("chapters", {}) if isinstance(gates, dict) else {}
    for task_id, task in tasks.items():
        status = task["当前状态"]
        if status not in ALLOWED_TASK_STATUSES:
            errors.append(
                f"tracking: {task_id} 当前状态 must be one of {sorted(ALLOWED_TASK_STATUSES)}, got {status!r}"
            )
            continue
        required = TASK_GATE_REQUIREMENTS.get(status)
        gate = chapters.get(task_id) if isinstance(chapters, dict) else None
        if required and (not isinstance(gate, dict) or gate.get(required) is not True):
            errors.append(f"tracking: {task_id} status {status} requires {required}=true")
    return tasks


def _binding_ids(content: str, field: str, prefix: str) -> set[str]:
    values = []
    for row in _table_rows(content):
        if len(row) >= 2 and row[0].strip("*` ") == field:
            values.append(row[1])
    values.extend(re.findall(rf"^[ \t]*(?:[-*][ \t]+)?(?:\*\*)?{field}(?:\*\*)?[ \t]*[:：][ \t]*(.*)$",
                             content, re.M))
    return set(re.findall(rf"\b{prefix}-\d+\b", "\n".join(values)))


def validate_outline_bindings(project_root: Path, tasks: dict, plotlines: dict,
                              errors: list[str]) -> None:
    outline_root = project_root / "03-大纲"
    if not outline_root.exists():
        return

    outline_files = sorted(outline_root.rglob("*.md"))
    for path in outline_files:
        if "细纲" not in path.name:
            continue
        content = _read(path)
        rel_path = path.relative_to(project_root)
        headings = list(re.finditer(r"^#{1,6}[ \t]+(第[ \t]*[^\n章]+章[^\n]*)$", content, re.M))
        if not headings:
            errors.append(f"outline: {rel_path} missing chapter headings")
            continue
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
            chapter = content[heading.end():end]
            label = f"outline: {rel_path} {heading.group(1)}"
            plot_ids = _binding_ids(chapter, "情节线ID", "PL")
            task_ids = _binding_ids(chapter, "场景任务ID", "WT")
            for field, ids, matrix in (("情节线ID", plot_ids, plotlines), ("场景任务ID", task_ids, tasks)):
                if not ids:
                    errors.append(f"{label}: missing nonempty {field}")
                for record_id in sorted(ids):
                    if record_id not in matrix:
                        name = "情节线" if field == "情节线ID" else "写作任务"
                        errors.append(f"{label}: {record_id} not found in 追踪/{name}.md")
            for task_id in task_ids & tasks.keys():
                task_plot_ids = set(re.findall(r"\bPL-\d+\b", tasks[task_id]["情节线ID"]))
                if not task_plot_ids or not task_plot_ids <= plot_ids:
                    errors.append(f"{label}: {task_id} plotline binding mismatch")


def validate_live_assets(project_root: Path, errors: list[str]) -> None:
    targets = [("novel-config", project_root / "novel-config.json")]
    for kind, directory in (("character", "人物"), ("location", "地点"),
                            ("faction", "势力"), ("item", "物品"), ("concept", "概念")):
        targets.extend((kind, path) for path in sorted((project_root / "知识库" / directory).rglob("*.md")))
    for kind, path in targets:
        try:
            validate_assets.VALIDATORS[kind](path)
        except (validate_assets.ValidationError, OSError, ValueError) as exc:
            errors.append(f"assets: {path.relative_to(project_root)}: {exc}")


def validate_project(project_root: Path) -> None:
    errors: list[str] = []
    if not project_root.is_dir():
        raise ValidationError(f"project root not found: {project_root}")

    progress = _load_progress(project_root, errors)
    validate_progress_gates(progress, errors)
    validate_live_assets(project_root, errors)
    tasks = validate_writing_tasks(project_root, progress, errors)
    plotlines = _read_matrix(project_root / "追踪" / "情节线.md", "情节线ID", "PL", (), errors)
    for task_id, task in tasks.items():
        ids = set(re.findall(r"\bPL-\d+\b", task["情节线ID"]))
        if not ids or not ids <= plotlines.keys():
            errors.append(f"tracking: {task_id} references missing 情节线ID")
    validate_outline_bindings(project_root, tasks, plotlines, errors)

    if errors:
        raise ValidationError("\n".join(f"- {error}" for error in errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a live novel project.")
    parser.add_argument("--project-root", required=True, type=Path)
    args = parser.parse_args()

    try:
        validate_project(args.project_root.resolve())
    except (ValidationError, OSError, UnicodeError) as exc:
        print(f"FAIL project: {exc}", file=sys.stderr)
        return 1

    print(f"OK project: {args.project_root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
