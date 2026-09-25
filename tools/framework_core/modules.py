"""Bounded observations, distinct module/repository/index identities."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from .config import identity, digest
from .storage import safe_path, fingerprint

EXCLUDED = {'.git', '.framework', '.agent-framework', '.codegraph', '.agents',
            'node_modules', 'dist', 'build', 'coverage', '__pycache__', '.venv', 'venv'}
EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.rs', '.c', '.cpp', '.h', '.java', '.swift'}


def find_candidates(root, discovery_roots, max_depth=4):
    root = Path(root).resolve()
    found = {}
    for rel in discovery_roots:
        base = safe_path(root, rel)
        if not base.is_dir():
            continue
        for current, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
            p = Path(current)
            for name in dirs:
                safe_path(root, (p / name).relative_to(root))
            depth = len(p.relative_to(base).parts)
            if depth >= max_depth:
                dirs[:] = []
            relative = p.relative_to(root).as_posix()
            descriptor = safe_path(root, (p / 'framework-module.json').relative_to(root))
            if descriptor.is_file():
                data = json.loads(descriptor.read_text())
                mid = identity(data.get('id'))
                basis = 'descriptor'
            elif (p / '.git').exists():
                mid = 'root' if relative == '.' else 'module-' + digest(relative)[:10]
                basis = 'git-boundary'
            else:
                continue
            found[relative] = {'id': mid, 'path': relative, 'basis': basis, 'trust': 'discovered'}
    return [found[k] for k in sorted(found)]


def source_files(root, rel, max_depth=12):
    base = safe_path(root, rel)
    found = {}
    if not base.exists():
        return found
    for current, dirs, files in os.walk(base, followlinks=False):
        depth = len(Path(current).relative_to(base).parts)
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        if depth >= max_depth and dirs:
            raise ValueError('SCAN_DEPTH_EXCEEDED: ' + str(Path(current).relative_to(root.resolve())))
        for name in dirs + files:
            path = Path(current) / name
            if path.is_symlink():
                raise ValueError('SYMLINK: ' + str(path.relative_to(root.resolve())))
        # Independent nested repositories are separate candidates, never silently indexed.
        dirs[:] = [d for d in dirs if not (Path(current) / d / '.git').exists()]
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix in EXTENSIONS:
                if path.stat().st_size > 1024 * 1024:
                    raise ValueError('SOURCE_TOO_LARGE: ' + str(path))
                found[path.relative_to(root.resolve()).as_posix()] = fingerprint(path)
                if len(found) > 5000:
                    raise ValueError('SOURCE_BUDGET_EXCEEDED')
    return found


def discover(root, discovery_roots, max_depth=4):
    root = Path(root).resolve()
    observations = []
    for rel in sorted(set(discovery_roots)):
        path = safe_path(root, rel)
        if not path.exists():
            continue
        git = subprocess.run(['git', '-C', str(path), 'rev-parse', '--show-toplevel'],
                             text=True, capture_output=True, timeout=15)
        repo = None
        if git.returncode == 0:
            candidate = Path(git.stdout.strip()).resolve()
            if candidate.is_relative_to(root):
                repo = candidate.relative_to(root).as_posix()
        observations.append({'path': rel, 'git_root': repo,
                             'agents': (path / 'AGENTS.md').is_file(),
                             'sources': source_files(root, rel, max_depth)})
    return observations


def catalog_update(previous, declarations, observations):
    result = {'schema_version': 1, 'modules': {}, 'repos': {}, 'indexes': {}}
    seen = set()
    by_path = {o['path']: o for o in observations}
    for decl in declarations:
        mid = identity(decl['id'])
        if mid in seen:
            raise ValueError('DUPLICATE_ID: ' + mid)
        seen.add(mid)
        old = previous.get('modules', {}).get(mid, {})
        obs = by_path.get(decl['path'])
        repo_root = obs.get('git_root') if obs else old.get('repo_root')
        index_root = repo_root or decl['path']
        rid = 'repo-' + digest(repo_root)[:12] if repo_root else None
        iid = 'index-' + digest(index_root)[:12]
        sources = obs.get('sources', {}) if obs else {}
        history = list(old.get('history', []))
        if old.get('path') and old['path'] != decl['path']:
            history.append(old['path'])
        result['modules'][mid] = dict(decl, presence='present' if obs else 'missing',
            lifecycle='IMPLEMENTED' if sources else ('SCAFFOLDED' if obs else 'PLANNED'),
            repo_id=rid, repo_root=repo_root, index_id=iid, sources=sources, history=history)
        if rid:
            result['repos'][rid] = {'id': rid, 'root': repo_root}
        index = result['indexes'].setdefault(iid, {'id': iid, 'root': index_root, 'modules': [], 'sources': {}})
        index['modules'].append(mid)
        index['sources'].update(sources)
    for mid, old in previous.get('modules', {}).items():
        if mid not in result['modules']:
            result['modules'][mid] = dict(old, presence='missing')
    return result
