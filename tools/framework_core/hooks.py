"""No-model Git event dispatcher; refuse shared or foreign hook ownership."""
from pathlib import Path
import shlex

from .process import run
from .storage import atomic, safe_path, read_json
from .config import encoded


def hook_plan(repo, project, runner=run):
    repo, project = Path(repo).resolve(), Path(project).resolve()
    values = []
    for flag in ('--git-path=hooks', '--git-common-dir', '--git-dir'):
        # Git spells --git-path with a separate parameter.
        args = ['--git-path', 'hooks'] if flag.startswith('--git-path') else [flag]
        result = runner(['git', '-C', str(repo), 'rev-parse', *args], repo, 15, {})
        if result['exit_code']:
            return {'status': 'NOT_APPLICABLE', 'changes': []}
        p = Path(result['stdout'].strip())
        values.append((repo / p).resolve() if not p.is_absolute() else p.resolve())
    hooks, common, gitdir = values
    worktrees = runner(['git', '-C', str(repo), 'worktree', 'list', '--porcelain'], repo, 15, {})
    if worktrees['exit_code'] or sum(line.startswith('worktree ') for line in worktrees['stdout'].splitlines()) != 1:
        return {'status': 'HOOK_CONFLICT', 'reason': 'shared worktree scope', 'changes': []}
    if common != gitdir or not hooks.is_relative_to(project) or hooks != common / 'hooks':
        return {'status': 'HOOK_CONFLICT', 'reason': 'shared or custom hooks path', 'changes': []}
    changes = []
    for event in ('post-commit', 'post-merge', 'post-checkout'):
        # Native Git CWD is the current repository. Never embed an arbitrary module command.
        target = shlex.quote(str(project))
        script = ('#!/bin/sh\n# agent-map-framework owned hook v1\n'
                  'python3 ' + shlex.quote(str(project / '.agent-framework/tools/framework')) +
                  ' event --target ' + target + ' --reason ' + event +
                  ' >/dev/null 2>&1 || printf "%s\\n" "Framework dirty marker failed; run doctor" >&2\nexit 0\n')
        path = hooks / event
        safe_path(project, path.relative_to(project))
        if path.exists() and path.read_text() != script:
            return {'status': 'HOOK_CONFLICT', 'reason': event, 'changes': []}
        changes.append({'path': path.relative_to(project).as_posix(), 'content': script})
    return {'status': 'READY', 'changes': changes}


def mark_dirty(root, worktree_id, reason):
    rel = '.framework/local-state/dirty.json'
    old = read_json(root, rel, {'reasons': []})
    atomic(root, rel, encoded({'worktree': worktree_id, 'reasons': sorted(set(old['reasons'] + [reason]))}))
