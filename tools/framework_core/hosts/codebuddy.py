"""CodeBuddy adapter: shared read-only subagents only.

CodeBuddy has no project hook and must not receive CODEBUDDY.md, or it
stops treating the project-root AGENTS.md as project memory.
"""
import hashlib

from ..storage import fingerprint, safe_path
from .base import Adapter, shared_agent_files


class CodeBuddyAdapter(Adapter):
    """Install the three shared subagents into .codebuddy/agents/."""

    host_id = 'codebuddy'
    label = 'CodeBuddy'
    requires_hooks = False

    def template_files(self):
        return shared_agent_files('.codebuddy')

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
        status = 'VERIFIED' if results and all(item['installed'] for item in results) else 'STALE'
        return {'status': status, 'files': results}

    def encode(self, verdict):
        """Shared verdict only. This host has no native hook decision."""
        blocked = verdict['status'] not in ('READY', 'NOT_APPLICABLE')
        return {
            'status': verdict['status'],
            'decision': 'deny' if blocked else 'allow',
            'reason': verdict.get('reason'),
        }, 0


ADAPTER = CodeBuddyAdapter
