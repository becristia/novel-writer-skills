---
name: "novel-writer-skills project rules"
description: "Project-level rules for maintaining the novel writer skill pack."
---

## Scope

This repository contains Codex/Claude-compatible skills for Chinese web-novel planning, writing, auditing, and workflow maintenance.

## Human Creative Authority Contract / 人类创作主权契约

These skills are web-novel creation assistants, not an autonomous production line.

- Human authors own every creative decision: premise, platform positioning, character intent, plot direction, final prose, canon, and workflow changes.
- AI may ask questions, propose options, draft text, check consistency, summarize feedback, and prepare review packets.
- AI 不得替作者拍板. When a choice affects canon, stage progress, chapter finalization, knowledge-base entry, config, or skill rules, ask for author approval first.
- 无人审不推进. Do not mark `checks.*_done`, finalize a chapter, move a temporary knowledge entry into the formal knowledge base, or advance `current_phase` without explicit human approval.
- AI may recommend a path, but the artifact should show candidate options and trade-offs instead of silently choosing one.

## Knowledge Base Integration Contract

`知识库/` is the canon system for a novel project, not a scratchpad.

- `知识库/ 是正史`: formal entries under `人物/`, `地点/`, `势力/`, `物品/`, and `概念/` are treated as canon by downstream skills.
- `知识库/暂存区/ 只放待确认提案`: AI writes uncertain or newly extracted changes there as proposals. Human review decides whether they enter canon.
- `_index.md 是检索入口`: skills should read `_index.md` first, then read specific entries only as needed.
- Every formal entry change must update `_index.md` in the same workflow step.
- Every chapter context package must cite the exact entries or pending proposals it used.
- Decisions that change canon direction must use `知识库/决策/决策日志.md`, not ad hoc notes.
- Periodic review may produce cleanup or archive suggestions, but must not delete or archive knowledge entries without explicit human approval.

## Context Layer Contract

Long-form writing must separate durable rules, story canon, chapter inputs, and rolling state.

- `标准层`: skill rules, `novel-config.json`, iron rules, platform expectations, and review thresholds.
- `故事层`: confirmed premise, worldbuilding, formal `知识库/` entries, and decision log.
- `章节层`: current L3 outline, chapter metadata, recent summaries, and the write-before context package.
- `追踪层`: rolling operational state under `追踪/`, including `追踪/当前上下文.md`, `追踪/伏笔.md`, `追踪/时间线.md`, `追踪/角色状态.md`, `追踪/情节线.md`, and `追踪/写作任务.md`.
- Do not mix layers. Temporary extraction proposals go to `知识库/暂存区/`; rolling continuation state goes to `追踪/`; formal canon goes to `知识库/`.
- Chapter drafting must read from all four layers, then write back only proposals and tracking updates. Formal canon still requires human approval.

## Plotline And Task Matrix Contract

`追踪/情节线.md` and `追踪/写作任务.md` are the operational matrix for continuing a long novel.

- `追踪/情节线.md`: track main plots, subplots, relationship arcs, character arcs, and foreshadowing lines by `情节线ID`.
- `追踪/写作任务.md`: track chapter/scene work by `场景任务ID`, status, gate, next action, and responsible owner.
- L3 chapter outlines must cite `情节线ID` and `场景任务ID` when the chapter advances a known line or task.
- Each chapter uses its own Markdown heading and nonempty matrix bindings. Validate every chapter separately and resolve its IDs against the plotline and writing-task matrices.
- novel-write must update task status only as a proposal unless the transition is purely mechanical and non-final. Finalization and knowledge review always require human approval.
- Each writing task has exactly one current status: `planned -> drafting -> self_checked -> human_review -> finalized -> kb_reviewed`.

## Workflow Gate Contract

`进度.json.workflow_gates` is a state machine for review gates, not an automation engine.

- AI 只能建议状态变更; it must not silently advance gates that affect phase completion, chapter finalization, or canon.
- 人审门禁 applies to `human_approved`, `human_finalized`, `knowledge_reviewed`, and any transition that writes `checks.*_done`.
- Stage gates live under `workflow_gates.ideate`, `workflow_gates.design`, and `workflow_gates.structure`; only after human approval may the matching `checks.*_done` and `current_phase` values change.
- Chapter gates live under `workflow_gates.chapters.<场景任务ID>` and follow `chapter_gate_template`; do not use a singleton chapter gate because long novels need per-chapter state.
- Chapter gates are按章节/场景任务ID records and must move through `outline_ready → draft_ready → self_check_passed → human_finalized → knowledge_reviewed`.
- If a gate is blocked, write `blocked_reason` and ask the author for the next decision instead of inventing a workaround.
- Gate flags and `checks.*_done` must be JSON booleans. A chapter gate can pass only after every preceding gate passes; phase completion must agree with `phases.*.status`, human approval, and prerequisite phases.

## Repository Layout

- `skills/<skill-name>/SKILL.md`: Required skill entry file. Keep frontmatter to `name` and `description` only.
- `skills/<skill-name>/references/*.md`: Detailed instructions loaded only when the active workflow needs them.
- `assets/*`: Templates copied into a novel project. Do not store live novel project output here.
- `assets/灵感/`: Inspiration-card template and category placeholders only. Live inspiration cards belong in the novel project root `灵感/`.
- `assets/tracking-*.md`: Templates for project-root `追踪/` files. They are templates only, not live novel state.
- `scripts/validate_*.py`: Static validators for skill and asset consistency.
- `scripts/test_validators.py`: Standard-library regression tests for live project validation; generated fixtures stay under `.tmp/skill-workflow-fixes/` and are cleaned after each run.
- `docs/reviews/<date>-<skill>-audit.md`: Optional human-readable audit reports produced by novel-meta/agent-dispatch. Keep reports repo-scoped; do not put live novel prose here.
- `third_party/<owner>__<repo>/`: Local-only shallow clones for reference research. Treat as read-only; do not edit, validate, or vendor third-party code into this skill pack.
- `.claude-plugin/plugin.json`: Claude plugin metadata.
- `README.md`: User-facing overview and install/use guide.

## Novel Project Output Contract

When these skills are used in a novel project, generated project artifacts live in the novel project root, not in this skill repository:

```text
00-核心概念.md
00-书名简介.md
01-世界观.md
02-人物档案.md
03-力量体系.md
04-物品装备.md
05-人物关系.md
03-大纲/
正文/
摘要/
灵感/
知识库/
追踪/
进度.json
novel-config.json
```

Templates live in `assets/` and are copied or used as references. Do not write live output to `assets/`.

## State Schema Contract

`assets/progress-template.json` is the single source of truth for `进度.json`.

- Read phase status from `phases.<phase>.status`.
- Read phase completion gates from `checks.ideate_done`, `checks.design_done`, and `checks.structure_done`.
- Read current map from `current_map`.
- `current_chapter = 已定稿章节号`; planned outline coverage belongs in `phases.structure.total_chapters_planned` and `追踪/写作任务.md`.
- Read recurring reminders from `triggers.*`.
- Read human-gated workflow state from `workflow_gates.*`; do not create parallel gate fields.
- Do not introduce parallel fields such as `进度.json.ideate_done`, `phase.structure`, or `phase.write`.

## Config Contract

`assets/novel-config-template.json` is the template for project-root `novel-config.json`.

- Skills should refer to the active project file as `novel-config.json`.
- Validators in this repository validate the template file unless explicitly checking a live novel project.
- Use `validate_assets.py --template <type> --file <actual-file>` for an actual config or canon card. Without `--file`, the command checks the repository template only. `validate_novel_project.py --project-root <novel-root>` checks live config, formal cards, gates, and chapter bindings together.
- Iron-rule consumers read numeric IDs from `iron_rules.enabled` and look up `iron_rules.severity` by string ID; `_v2_alias` is descriptive metadata, not a boolean switch.
- Repository skill audits use the skill pack and templates; a live novel project is optional. Only chapter drafting requires live config and progress files.

## Editing Rules

- Keep changes scoped to the requested workflow improvement.
- Update documentation before practice when changing conventions.
- Do not delete files, rewrite history, or run destructive git commands without explicit user approval.
- Do not add auxiliary docs inside individual skill folders unless the file is directly consumed by the skill.
- Keep `SKILL.md` concise; move detailed examples and checklists into `references/`.

## Validation

Run the full validation suite before reporting completion:

```bash
python3 scripts/validate_assets.py --all
python3 scripts/validate_skill_interfaces.py --all
python3 scripts/validate_inspiration_skill.py --all
python3 scripts/validate_novel_ideate_skill.py --all
python3 scripts/validate_novel_design_skill.py --all
python3 scripts/validate_novel_structure_skill.py --all
python3 scripts/validate_agent_dispatch_skill.py --all
python3 scripts/validate_novel_write_skill.py --all
python3 scripts/validate_novel_meta_skill.py --all
python3 -m unittest discover -s scripts -p 'test_*.py'
```

For live novel projects that consume this skill pack, run the read-only project consistency check:

```bash
python3 scripts/validate_novel_project.py --project-root /path/to/novel
```

Also scan for convention drift:

```bash
rg -n -g '!AGENTS.md' -g '!scripts/validate_assets.py' -g '!**/CHANGELOG.md' "进度\\.json\\.(ideate_done|design_done|structure_done)|phase\\.(structure|design|write)|进度\\.json\\.current\\.(map|chapter)|agent_dispatch\\.run|assets/novel-config\\.json|assets/暂存区|assets/03-大纲" .
```
