"""Behavioral regressions for template and live novel project validation."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import validate_assets as assets
import validate_novel_project as project

ROOT = Path(__file__).resolve().parent.parent


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_parent = ROOT / '.tmp' / 'skill-workflow-fixes'
        cls.created_parent = not cls.fixture_parent.exists()
        cls.fixture_parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if cls.created_parent:
            cls.fixture_parent.rmdir()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=self.fixture_parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.progress = json.loads((ROOT / 'assets/progress-template.json').read_text())
        self.config = json.loads((ROOT / 'assets/novel-config-template.json').read_text())
        self.write_json('进度.json', self.progress)
        self.write_json('novel-config.json', self.config)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def write_json(self, name, data):
        return self.write(name, json.dumps(data, ensure_ascii=False))

    def cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / script), *map(str, args)],
            cwd=self.root, capture_output=True, text=True,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        )

    def ready_project(self):
        for phase in ('ideate', 'design', 'structure'):
            self.progress['checks'][phase + '_done'] = True
            self.progress['phases'][phase]['status'] = 'done'
            self.progress['workflow_gates'][phase]['human_approved'] = True
        self.progress['workflow_gates']['structure']['outline_ready'] = True
        self.progress['current_phase'] = 'write'
        self.progress['phases']['write']['status'] = 'in_progress'
        tasks = []
        outlines = []
        for number in (1, 2):
            task_id = f'WT-{number:03d}'
            gate = deepcopy(self.progress['workflow_gates']['chapter_gate_template'])
            gate.update(scene_task_id=task_id, chapter_id=f'CH-{number:03d}')
            self.progress['workflow_gates']['chapters'][task_id] = gate
            tasks.append(f'| {task_id} | 第{number}章 | PL-001 | planned |')
            outlines.append(
                f'### 第 {number} 章：示例\n\n#### 章节元数据\n\n'
                f'| 字段 | 值 |\n|---|---|\n| 情节线ID | PL-001 |\n'
                f'| 场景任务ID | {task_id} |\n\n核心事件：示例事件\n'
            )
        self.write_json('进度.json', self.progress)
        self.write('追踪/情节线.md', '| 情节线ID | 名称 |\n|---|---|\n| PL-001 | 主线 |\n')
        self.write('追踪/写作任务.md', '| 场景任务ID | 章节 | 情节线ID | 当前状态 |\n|---|---|---|---|\n' + '\n'.join(tasks) + '\n')
        self.outline = self.write('03-大纲/01-地图1-细纲.md', '\n'.join(outlines))

    def assert_project_error(self, message):
        with self.assertRaisesRegex(project.ValidationError, message):
            project.validate_project(self.root)

    def test_repository_config_template_passes(self):
        assets.validate_novel_config()

    def test_initial_project_passes(self):
        project.validate_project(self.root)

    def test_empty_progress_is_rejected(self):
        self.write_json('进度.json', {})
        self.assert_project_error('workflow_gates')

    def test_gate_flags_require_booleans(self):
        self.ready_project()
        for value in ('false', 0, None):
            with self.subTest(value=value):
                self.progress['workflow_gates']['chapters']['WT-001']['outline_ready'] = value
                self.write_json('进度.json', self.progress)
                self.assert_project_error('outline_ready.*boolean')

    def test_chapter_gates_cannot_skip_predecessors(self):
        self.ready_project()
        for field in ('draft_ready', 'self_check_passed', 'human_finalized', 'knowledge_reviewed'):
            with self.subTest(field=field):
                gate = self.progress['workflow_gates']['chapters']['WT-001']
                for flag in project.REQUIRED_CHAPTER_GATE_FIELDS:
                    if flag != 'blocked_reason':
                        gate[flag] = False
                gate[field] = True
                self.write_json('进度.json', self.progress)
                self.assert_project_error('requires')

    def test_every_ordered_chapter_gate_prefix_passes(self):
        self.ready_project()
        gate = self.progress['workflow_gates']['chapters']['WT-001']
        for field in ('outline_ready', 'draft_ready', 'self_check_passed', 'human_finalized', 'knowledge_reviewed'):
            with self.subTest(field=field):
                gate[field] = True
                errors = []
                project.validate_progress_gates(self.progress, errors)
                self.assertEqual(errors, [])

    def test_phase_completion_requires_approval(self):
        self.progress['checks']['ideate_done'] = True
        self.progress['phases']['ideate']['status'] = 'done'
        self.write_json('进度.json', self.progress)
        self.assert_project_error('human_approved')

    def test_completed_phase_requires_matching_check(self):
        self.progress['phases']['ideate']['status'] = 'done'
        self.progress['workflow_gates']['ideate']['human_approved'] = True
        self.write_json('进度.json', self.progress)
        self.assert_project_error('ideate_done')

    def test_phase_and_current_phase_require_predecessors(self):
        self.progress['checks']['structure_done'] = True
        self.progress['phases']['structure']['status'] = 'done'
        self.progress['workflow_gates']['structure'].update(human_approved=True, outline_ready=True)
        self.progress['current_phase'] = 'write'
        self.write_json('进度.json', self.progress)
        self.assert_project_error('requires')

    def test_phase_containers_and_checks_reject_wrong_types(self):
        for key, value in (('checks', []), ('phases', []), ('current_phase', [])):
            with self.subTest(key=key):
                progress = deepcopy(self.progress)
                progress[key] = value
                self.write_json('进度.json', progress)
                self.assert_project_error(key)

    def test_two_chapter_outline_with_valid_matrices_passes(self):
        self.ready_project()
        project.validate_project(self.root)

    def test_each_chapter_requires_its_own_bindings(self):
        self.ready_project()
        self.outline.write_text(self.outline.read_text().replace('| 场景任务ID | WT-002 |', ''))
        self.assert_project_error('第 2 章.*场景任务ID')

    def test_empty_binding_and_unrelated_id_do_not_pass(self):
        self.ready_project()
        self.outline.write_text(self.outline.read_text().replace('| 情节线ID | PL-001 |', '| 情节线ID | |', 1) + '\n备注：PL-001\n')
        self.assert_project_error('第 1 章.*情节线ID')

    def test_standalone_binding_fields_are_supported(self):
        self.ready_project()
        self.outline.write_text(self.outline.read_text().replace('| 情节线ID | PL-001 |', '情节线ID：PL-001'))
        project.validate_project(self.root)

    def test_empty_standalone_binding_cannot_borrow_the_next_line(self):
        self.ready_project()
        self.outline.write_text(self.outline.read_text().replace('| 情节线ID | PL-001 |', '情节线ID：\n备注：PL-001', 1))
        self.assert_project_error('第 1 章.*情节线ID')

    def test_unknown_matrix_ids_are_rejected(self):
        self.ready_project()
        self.outline.write_text(self.outline.read_text().replace('WT-002', 'WT-999'))
        self.assert_project_error('WT-999.*写作任务')

    def test_unknown_plotline_is_rejected(self):
        self.ready_project()
        self.outline.write_text(self.outline.read_text().replace('PL-001', 'PL-999'))
        self.assert_project_error('PL-999.*情节线')

    def test_duplicate_task_ids_are_rejected(self):
        self.ready_project()
        task_path = self.root / '追踪/写作任务.md'
        task_path.write_text(task_path.read_text().replace('WT-002', 'WT-001'))
        self.assert_project_error('duplicate.*WT-001')

    def test_task_and_outline_plotlines_must_agree(self):
        self.ready_project()
        with (self.root / '追踪/情节线.md').open('a') as stream:
            stream.write('| PL-002 | 支线 |\n')
        task_path = self.root / '追踪/写作任务.md'
        task_path.write_text(task_path.read_text().replace('PL-001', 'PL-002'))
        self.assert_project_error('plotline.*mismatch')

    def test_finalized_task_requires_finalized_gate(self):
        self.ready_project()
        task_path = self.root / '追踪/写作任务.md'
        task_path.write_text(task_path.read_text().replace('planned', 'finalized', 1))
        self.assert_project_error('human_finalized')

    def test_live_config_accepts_disabled_rules(self):
        for enabled in ([], [1, 4, 10]):
            with self.subTest(enabled=enabled):
                self.config['iron_rules']['enabled'] = enabled
                self.write_json('novel-config.json', self.config)
                result = self.cli('validate_assets.py', '--template', 'novel-config', '--file', self.root / 'novel-config.json')
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_live_config_rejects_bad_rule_ids_and_severity(self):
        cases = [('enabled', [True]), ('enabled', [1, 1]), ('enabled', [13]), ('severity', {'1': 'ignore'})]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                config = deepcopy(self.config)
                config['iron_rules'][field] = value
                path = self.write_json('novel-config.json', config)
                with self.assertRaises(assets.ValidationError):
                    assets.validate_novel_config(path)

    def test_actual_invalid_config_does_not_fall_back_to_template(self):
        self.config['iron_rules'] = {}
        self.write_json('novel-config.json', self.config)
        result = self.cli('validate_assets.py', '--template', 'novel-config', '--file', self.root / 'novel-config.json')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('iron_rules', result.stderr)
        self.assert_project_error('novel-config')

    def test_config_threshold_type_and_bounds_are_checked(self):
        for field, value in (('min_word_count', '3000'), ('max_word_count', 1)):
            with self.subTest(field=field):
                config = deepcopy(self.config)
                config['chapter_requirements'][field] = value
                path = self.write_json('novel-config.json', config)
                with self.assertRaises(assets.ValidationError):
                    assets.validate_novel_config(path)

    def test_missing_actual_file_is_not_ignored(self):
        result = self.cli('validate_assets.py', '--template', 'character', '--file', self.root / 'missing.md')
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_actual_formal_card_is_checked(self):
        card = (ROOT / 'assets/character-card-template.md').read_text().replace('正式 / 待复核 / 已废弃', '正式')
        path = self.write('知识库/人物/角色.md', card)
        result = self.cli('validate_assets.py', '--template', 'character', '--file', path)
        self.assertEqual(result.returncode, 0, result.stderr)
        path.write_text(card.replace('- **词条ID**：CHAR-001', ''))
        result = self.cli('validate_assets.py', '--template', 'character', '--file', path)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assert_project_error('角色.md')

    def test_all_card_types_check_their_actual_fields(self):
        for kind, field in (('character', '境界'), ('location', '所属区域'),
                            ('faction', '总部'), ('item', '品阶'), ('concept', '所属体系')):
            with self.subTest(kind=kind):
                card = (ROOT / f'assets/{kind}-card-template.md').read_text().replace('正式 / 待复核 / 已废弃', '正式')
                path = self.write(f'{kind}.md', card)
                assets.VALIDATORS[kind](path)
                path.write_text(re.sub(rf'^- \*\*{field}\*\*：.*\n', '', card, flags=re.M))
                with self.assertRaises(assets.ValidationError):
                    assets.VALIDATORS[kind](path)

    def test_invalid_json_is_a_reported_failure(self):
        self.write('进度.json', '{')
        result = self.cli('validate_novel_project.py', '--project-root', self.root)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_file_option_cannot_be_combined_with_all(self):
        result = self.cli('validate_assets.py', '--all', '--file', self.root / 'novel-config.json')
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_validation_is_read_only(self):
        self.ready_project()
        def snapshot():
            return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.root.rglob('*') if path.is_file()}
        before = snapshot()
        result = self.cli('validate_novel_project.py', '--project-root', self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(), before)


if __name__ == '__main__':
    unittest.main()
