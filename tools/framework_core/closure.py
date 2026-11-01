"""Read-only judgement of unfinished work in a project.

The public shell used to keep this judgement in a maintainer-only script, so
a project that adopted the shell had no way to find out that its finished
changes had never been synced into the spec store or archived. The rules
live here instead, where the runtime payload carries them, and both the
shell's own check and the project-facing check call the same functions.

Nothing here writes, moves, syncs or merges anything.
"""
import re
from pathlib import Path

from .maps import validate_map
from .readiness import inspect_project
from .storage import fingerprint, read_json, safe_path


DONE = re.compile(r"^\s*-\s*\[x\]", re.M)
TODO = re.compile(r"^\s*-\s*\[ \]", re.M)


def task_counts(change_dir):
    """Return (done, todo) for a change, or None when it has no task file."""
    tasks = change_dir / 'tasks.md'
    if not tasks.is_file():
        return None
    text = tasks.read_text(encoding='utf-8')
    return len(DONE.findall(text)), len(TODO.findall(text))


def declared_capabilities(change_dir):
    """Capability ids the change declares, from its delta spec paths."""
    specs = change_dir / 'specs'
    if not specs.is_dir():
        return []
    return sorted(p.parent.name for p in specs.glob('*/spec.md'))


def skips_specs(change_dir):
    """True when the change declares that it has no delta specs."""
    meta = change_dir / '.openspec.yaml'
    return meta.is_file() and 'skip_specs' in meta.read_text(encoding='utf-8')


def outstanding_changes(root):
    """Complete changes that are still active, with what is missing."""
    root = Path(root)
    changes = root / 'openspec' / 'changes'
    specs = root / 'openspec' / 'specs'
    findings = []
    if not changes.is_dir():
        return findings
    for change in sorted(changes.iterdir()):
        if not change.is_dir() or change.name == 'archive':
            continue
        counts = task_counts(change)
        if counts is None:
            continue
        done, todo = counts
        if todo or not done:
            continue
        capabilities = declared_capabilities(change)
        unsynced = [c for c in capabilities if not (specs / c / 'spec.md').is_file()]
        if unsynced:
            problem = 'capabilities are not synced into openspec/specs/'
            detail = ', '.join(unsynced)
        else:
            problem = 'is still active and should be archived'
            detail = 'no delta specs' if skips_specs(change) else 'capabilities synced'
        findings.append({
            'change': change.name,
            'tasks': '%d/%d' % (done, done + todo),
            'problem': problem,
            'detail': detail,
        })
    return findings


def map_evidence_problems(root):
    """Map evidence that no longer matches the source it points at.

    The rules match the evidence check in maps.py: an entry is stale when the
    file's hash moved, and its anchor is lost when the hash still matches but
    the quoted text is gone. The two need different repairs, so they are
    reported apart.
    """
    root = Path(root)
    catalog = read_json(root, 'module-catalog.generated.json', {})
    observed = read_json(root, 'docs/project/relationships.generated.json')
    if not observed:
        return []
    problems = []
    for edge in observed.get('relationships', []):
        if not isinstance(edge, dict):
            continue
        for item in edge.get('evidence', []) or []:
            if not isinstance(item, dict) or not item.get('path'):
                continue
            rel = item['path']
            try:
                path = safe_path(root, rel)
            except ValueError:
                problems.append({'kind': 'UNSAFE_PATH', 'detail': rel})
                continue
            if not path.is_file():
                problems.append({'kind': 'MISSING_FILE', 'detail': rel})
                continue
            if fingerprint(path) != item.get('sha256'):
                problems.append({'kind': 'SOURCE_DRIFT', 'detail': rel})
                continue
            anchor = item.get('anchor')
            if not anchor or anchor not in path.read_text(encoding='utf-8', errors='replace'):
                problems.append({'kind': 'LOST_ANCHOR', 'detail': rel})
    if not problems:
        for code in validate_map(root, catalog, observed):
            if code in ('STALE_EVIDENCE', 'INVALID_ANCHOR', 'MISSING_EVIDENCE'):
                problems.append({'kind': code, 'detail': 'reported by the map validator'})
    return problems


def initialization_problems(root):
    """Dimensions in which the project has not finished being taken in."""
    root = Path(root)
    catalog = read_json(root, 'module-catalog.generated.json', {})
    config = read_json(root, 'framework-project.json', {})
    if not catalog or not config:
        # Not a project that adopted the shell at all. Reporting every
        # dimension as missing would be noise, not debt.
        return [{'dimension': 'project', 'status': 'NOT_A_PROJECT',
                 'detail': 'no framework-project.json or module-catalog.generated.json in this directory'}]
    report = inspect_project(root)
    problems = []

    def add(dimension, status, detail):
        problems.append({'dimension': dimension, 'status': status, 'detail': detail})

    if report.get('initialization') != 'COMPLETE':
        add('initialization', report.get('initialization'), 'the project is not fully taken in')
    documentation = report.get('documentation') or {}
    if documentation.get('status') != 'COMPLETE':
        errors = ', '.join(documentation.get('errors') or [])
        add('documentation', documentation.get('status'), errors or 'project documents do not match the current source')
    coverage = report.get('coverage') or {}
    if coverage.get('status') not in ('COMPLETE', 'NOT_APPLICABLE'):
        add('coverage', coverage.get('status'), 'registered sources are not all analysed')
    maps = report.get('maps') or {}
    if maps.get('status') not in ('READY', 'NOT_APPLICABLE'):
        add('maps', maps.get('status'), 'the relationship map is not current')
    return problems
