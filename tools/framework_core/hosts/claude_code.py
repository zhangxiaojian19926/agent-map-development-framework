"""Claude Code CLI adapter: project-level hook, event bridge, native decision."""
import hashlib
import json
from pathlib import Path

from ..storage import fingerprint, safe_path
from .base import Adapter

DISTRIBUTION = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = 'templates/host/claude-code'
HOST_STATE = '.framework/local-state/hosts.json'


class ClaudeCodeAdapter(Adapter):
    """Claude Code drives the shared gate through a project-level PreToolUse hook."""

    host_id = 'claude-code'
    label = 'Claude Code CLI'
    write_tools = ('Edit', 'MultiEdit', 'Write', 'NotebookEdit')
    read_tools = ('Read', 'Glob', 'Grep')
    def template_files(self):
        directory = DISTRIBUTION / TEMPLATE_DIR
        if not directory.is_dir():
            raise ValueError('HOST_TEMPLATE_MISSING: ' + TEMPLATE_DIR)
        files = {}
        for path in sorted(directory.glob('*')):
            if path.is_file():
                files['.claude/' + path.name] = path.read_text(encoding='utf-8')
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
        status = 'VERIFIED' if all(item['installed'] for item in results) else 'STALE'
        return {'status': status, 'files': results}

    def encode(self, verdict):
        """A PreToolUse decision for the host to apply to this tool call."""
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


ADAPTER = ClaudeCodeAdapter


def load_adapter(host_id):
    """The adapter for an installed host id."""
    from .base import load_adapter as loader
    return loader(host_id)
