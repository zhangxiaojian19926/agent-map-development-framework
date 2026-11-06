"""Qwen Code CLI adapter: same directory, same judgement, own native decision.

The kernel judgement is host independent: the same project facts give the
same verdict here as in any other host. What differs is the native decision
and what has actually been observed, and nothing is claimed as covered
before a real session records it.
"""
import hashlib
from pathlib import Path

from ..storage import fingerprint, safe_path
from .base import Adapter

DISTRIBUTION = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = 'templates/host/qwen-code'


class QwenCodeAdapter(Adapter):
    """Qwen Code drives the shared gate through a project-level tool hook."""

    host_id = 'qwen-code'
    label = 'Qwen Code CLI'
    write_tools = ('write_file', 'replace', 'edit')
    read_tools = ('read_file', 'glob', 'grep', 'search_file_content', 'list_directory')

    def template_files(self):
        directory = DISTRIBUTION / TEMPLATE_DIR
        if not directory.is_dir():
            return {}
        files = {}
        for path in sorted(directory.glob('*')):
            if path.is_file():
                files['.qwen/' + path.name] = path.read_text(encoding='utf-8')
        return files

    def preview(self, root):
        files = self.template_files()
        conflicts = []
        for rel, content in files.items():
            actual = fingerprint(safe_path(root, rel))
            if actual is not None and actual != hashlib.sha256(content.encode()).hexdigest():
                conflicts.append(rel)
        return {'files': files, 'conflicts': conflicts}

    def verify(self, root):
        files = self.template_files()
        results = []
        for rel, content in files.items():
            actual = fingerprint(safe_path(root, rel))
            expected = hashlib.sha256(content.encode()).hexdigest()
            results.append({'path': rel, 'installed': actual == expected})
        status = 'VERIFIED' if results and all(item['installed'] for item in results) else 'NOT_VERIFIED'
        return {'status': status, 'files': results}

    def encode(self, verdict):
        """A pre-tool decision for the host to apply to this tool call."""
        blocked = verdict['status'] not in ('READY', 'NOT_APPLICABLE')
        decision = 'deny' if blocked else 'allow'
        payload = {
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': decision,
                'permissionDecisionReason': verdict['reason'],
            }
        }
        return payload, 0


ADAPTER = QwenCodeAdapter
