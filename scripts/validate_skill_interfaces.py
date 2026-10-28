"""Validate Codex/OpenAI-facing skill interface metadata.

Usage:
    python scripts/validate_skill_interfaces.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


class ValidationError(Exception):
    """Interface validation failed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _skill_dirs() -> list[Path]:
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def _frontmatter(content: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", content, re.S)
    _require(match is not None, "frontmatter: missing YAML fence")
    return match.group(1)


def _description_text(frontmatter: str) -> str:
    lines = frontmatter.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("description: |"):
            collected = []
            for following in lines[index + 1:]:
                if re.match(r"^[A-Za-z0-9_-]+:", following):
                    break
                collected.append(following.strip())
            return " ".join(collected).strip()
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


def validate_frontmatter() -> None:
    """Ensure SKILL.md frontmatter only contains name and description."""
    forbidden_description_terms = [
        "v3",
        "v0.",
        "输出",
        "流程",
        "循环",
        "模式",
        "模块",
        "步骤",
        "TDD",
        "4 段式",
        "5 步",
        "管理 4",
    ]
    for skill_dir in _skill_dirs():
        path = skill_dir / "SKILL.md"
        _require(path.is_file(), f"{skill_dir.name}: SKILL.md missing")
        fm = _frontmatter(_read(path))
        keys = re.findall(r"^([A-Za-z0-9_-]+):", fm, re.M)
        _require(keys == ["name", "description"],
                 f"{skill_dir.name}: frontmatter keys must be name,description; got {keys}")
        _require(f"name: {skill_dir.name}" in fm,
                 f"{skill_dir.name}: frontmatter name must match folder")
        description = _description_text(fm)
        _require(description.startswith("Use when "),
                 f"{skill_dir.name}: description must start with 'Use when'")
        for term in forbidden_description_terms:
            _require(term not in description,
                     f"{skill_dir.name}: description must not summarize workflow with '{term}'")
        _require(len(description) <= 500,
                 f"{skill_dir.name}: description should be <= 500 characters")


def validate_openai_yaml() -> None:
    """Ensure each skill has minimal agents/openai.yaml metadata."""
    for skill_dir in _skill_dirs():
        skill_name = skill_dir.name
        path = skill_dir / "agents" / "openai.yaml"
        _require(path.is_file(), f"{skill_name}: missing agents/openai.yaml")
        content = _read(path)

        _require("interface:" in content, f"{skill_name}: missing interface block")
        for key in ("display_name", "short_description", "default_prompt"):
            match = re.search(rf"^\s+{key}:\s+\"(.+)\"\s*$", content, re.M)
            _require(match is not None, f"{skill_name}: missing quoted interface.{key}")
            value = match.group(1)
            _require(0 < len(value) <= 120,
                     f"{skill_name}: interface.{key} is empty or too long")

        short = re.search(r"^\s+short_description:\s+\"(.+)\"\s*$", content, re.M).group(1)
        _require(len(short) <= 64,
                 f"{skill_name}: short_description should be <= 64 characters")

        prompt = re.search(r"^\s+default_prompt:\s+\"(.+)\"\s*$", content, re.M).group(1)
        _require(f"${skill_name}" in prompt,
                 f"{skill_name}: default_prompt must mention ${skill_name}")


def validate_human_authority_contract() -> None:
    """Ensure the skill pack is positioned as human-led creative assistance."""
    root_requirements = {
        "AGENTS.md": ["人类创作主权契约", "AI 不得替作者拍板", "无人审不推进"],
        "README.md": ["网文创作辅助", "人做创作决策", "AI 只做辅助"],
    }
    for rel_path, keywords in root_requirements.items():
        path = PROJECT_ROOT / rel_path
        _require(path.is_file(), f"human-authority: missing {rel_path}")
        content = _read(path)
        for keyword in keywords:
            _require(keyword in content,
                     f"human-authority: {rel_path} 缺 '{keyword}'")

    skill_requirements = {
        "inspiration": ["不自动升级", "用户确认"],
        "novel-ideate": ["人审闸门", "平台定位", "读者承诺"],
        "novel-design": ["人审闸门", "作者确认"],
        "novel-structure": ["人审闸门", "opening-design.md"],
        "novel-write": ["AI 起草/协写", "人审定稿", "不得自动补齐"],
        "agent-dispatch": ["辅助工具", "不能替作者决策"],
        "novel-meta": ["只给建议", "用户确认后执行"],
    }
    for skill_name, keywords in skill_requirements.items():
        path = SKILLS_DIR / skill_name / "SKILL.md"
        _require(path.is_file(), f"human-authority: missing {skill_name}/SKILL.md")
        content = _read(path)
        for keyword in keywords:
            _require(keyword in content,
                     f"human-authority: {skill_name}/SKILL.md 缺 '{keyword}'")


def validate_knowledge_integration_contract() -> None:
    """Ensure knowledge-base state flows consistently across skills."""
    path_requirements = {
        "AGENTS.md": [
            "Knowledge Base Integration Contract",
            "知识库/ 是正史",
            "知识库/暂存区/ 只放待确认提案",
            "_index.md 是检索入口",
        ],
        "README.md": [
            "知识流转",
            "设定草稿 → 人审确认 → 正式词条",
            "写前查询",
            "写后提取",
        ],
        "skills/novel-design/SKILL.md": [
            "知识库正史",
            "正式词条",
            "人审确认",
        ],
        "skills/novel-structure/SKILL.md": [
            "关联词条必须可解析",
            "缺词条",
            "不得跳过",
        ],
        "skills/novel-write/SKILL.md": [
            "写前查询包",
            "写后变更提案",
            "人审入库",
        ],
        "skills/novel-write/references/knowledge-extraction.md": [
            "变更提案",
            "暂存区",
            "人审入库",
            "禁止无人审入库",
        ],
        "skills/novel-write/references/periodic-review.md": [
            "暂存区盘点",
            "不得删除",
            "归档建议",
            "用户确认",
        ],
    }
    for rel_path, keywords in path_requirements.items():
        path = PROJECT_ROOT / rel_path
        _require(path.is_file(), f"knowledge-integration: missing {rel_path}")
        content = _read(path)
        for keyword in keywords:
            _require(keyword in content,
                     f"knowledge-integration: {rel_path} 缺 '{keyword}'")


def validate_context_tracking_contract() -> None:
    """Ensure long-form writing context is layered and traceable."""
    path_requirements = {
        "AGENTS.md": [
            "Context Layer Contract",
            "标准层",
            "故事层",
            "章节层",
            "追踪层",
        ],
        "README.md": [
            "三层上下文",
            "追踪系统",
            "追踪/当前上下文.md",
        ],
        "skills/novel-write/SKILL.md": [
            "追踪/当前上下文.md",
            "追踪/伏笔.md",
            "追踪/时间线.md",
            "追踪/角色状态.md",
        ],
        "skills/agent-dispatch/references/write-chapter-subagent.md": [
            "追踪/当前上下文.md",
            "追踪/伏笔.md",
            "追踪/时间线.md",
            "追踪/角色状态.md",
        ],
    }
    for rel_path, keywords in path_requirements.items():
        path = PROJECT_ROOT / rel_path
        _require(path.is_file(), f"context-tracking: missing {rel_path}")
        content = _read(path)
        for keyword in keywords:
            _require(keyword in content,
                     f"context-tracking: {rel_path} 缺 '{keyword}'")


def validate_workflow_gate_contract() -> None:
    """Ensure workflow status changes remain human-gated."""
    path_requirements = {
        "AGENTS.md": [
            "Workflow Gate Contract",
            "workflow_gates",
            "workflow_gates.chapters",
            "chapter_gate_template",
            "AI 只能建议状态变更",
            "人审门禁",
            "按章节/场景任务ID",
        ],
        "README.md": [
            "状态机与人审门禁",
            "workflow_gates",
            "workflow_gates.chapters",
            "AI 只能建议状态变更",
        ],
        "skills/novel-ideate/SKILL.md": [
            "workflow_gates.ideate",
            "checks.ideate_done",
            "人审闸门",
        ],
        "skills/novel-design/SKILL.md": [
            "workflow_gates.design",
            "checks.design_done",
            "人审闸门",
        ],
        "skills/novel-structure/SKILL.md": [
            "workflow_gates.structure",
            "outline_ready",
            "人审门禁",
            "current_chapter = 已定稿章节号",
        ],
        "skills/novel-write/SKILL.md": [
            "workflow_gates.chapters",
            "场景任务ID",
            "draft_ready",
            "self_check_passed",
            "human_finalized",
            "knowledge_reviewed",
            "current_chapter = 已定稿章节号",
        ],
    }
    for rel_path, keywords in path_requirements.items():
        path = PROJECT_ROOT / rel_path
        _require(path.is_file(), f"workflow-gate: missing {rel_path}")
        content = _read(path)
        for keyword in keywords:
            _require(keyword in content,
                     f"workflow-gate: {rel_path} 缺 '{keyword}'")
        if rel_path in {"AGENTS.md", "README.md", "skills/novel-write/SKILL.md"}:
            _require(re.search(r"workflow_gates\.chapter(?!s|_)", content) is None,
                     f"workflow-gate: {rel_path} 不应继续引用单例 workflow_gates.chapter")


def validate_reference_routing() -> None:
    """Ensure long references tell future agents when to read which section."""
    for path in sorted(SKILLS_DIR.glob("*/references/*.md")):
        lines = _read(path).splitlines()
        if len(lines) <= 100:
            continue
        head = "\n".join(lines[:35])
        _require("## 使用路由" in head or "## 目录" in head,
                 f"reference-routing: {path.relative_to(PROJECT_ROOT)} 超 100 行但前 35 行缺使用路由/目录")


def validate_review_report_contract() -> None:
    """Ensure docs/reviews output is documented as a repository artifact."""
    agents = _read(PROJECT_ROOT / "AGENTS.md")
    _require("docs/reviews/" in agents,
             "review-report: AGENTS.md 缺 docs/reviews/ 路径约定")
    for rel_path in [
        "skills/agent-dispatch/SKILL.md",
        "skills/agent-dispatch/references/parallel-audit-subagent.md",
        "skills/novel-meta/SKILL.md",
        "skills/novel-meta/references/m4-eval-harness.md",
    ]:
        content = _read(PROJECT_ROOT / rel_path)
        _require("docs/reviews/" in content,
                 f"review-report: {rel_path} 缺 docs/reviews/ 引用")


def validate_plugin_metadata() -> None:
    """Ensure marketplace metadata does not imply autonomous production."""
    path = PROJECT_ROOT / ".claude-plugin" / "plugin.json"
    _require(path.is_file(), "plugin-metadata: missing .claude-plugin/plugin.json")
    content = _read(path)
    _require("半自动化" not in content and "自动生产线" not in content,
             "plugin-metadata: plugin description must not imply automation")
    for keyword in ("创作辅助", "人审"):
        _require(keyword in content,
                 f"plugin-metadata: plugin description 缺 '{keyword}'")


VALIDATORS = {
    "frontmatter": validate_frontmatter,
    "openai-yaml": validate_openai_yaml,
    "human-authority": validate_human_authority_contract,
    "knowledge-integration": validate_knowledge_integration_contract,
    "context-tracking": validate_context_tracking_contract,
    "workflow-gate": validate_workflow_gate_contract,
    "reference-routing": validate_reference_routing,
    "review-report": validate_review_report_contract,
    "plugin-metadata": validate_plugin_metadata,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="skill interface metadata validation")
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
