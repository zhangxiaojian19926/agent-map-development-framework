"""Read-only judgement of unfinished work in a project.

The public shell used to keep this judgement in a maintainer-only script, so
a project that adopted the shell had no way to find out that its finished
changes had never been synced into the spec store or archived. The rules
live here instead, where the runtime payload carries them, and both the
shell's own check and the project-facing check call the same functions.

Nothing here writes, moves, syncs or merges anything.
"""
import json
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


def project_knowledge_base(root):
    """The initialized project KB, or None when the alias is not configured."""
    root = Path(root)
    aliases = root / 'llm-wiki-aliases.json'
    kb = root / 'knowledge' / 'project'
    if not aliases.is_file() or aliases.is_symlink() or not kb.is_dir() or kb.is_symlink():
        return None
    try:
        data = json.loads(aliases.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get('project') != 'knowledge/project':
        return None
    return kb


def _page_detail(root, page):
    if not isinstance(page, dict):
        return 'knowledge receipt page is not an object'
    kind = page.get('artifact_kind')
    source_rel = page.get('source_path')
    digest = page.get('source_sha256')
    page_rel = page.get('path')
    if kind not in ('requirement', 'problem'):
        return 'knowledge receipt page kind is not requirement or problem'
    if not isinstance(source_rel, str) or not isinstance(page_rel, str) or not isinstance(digest, str):
        return 'knowledge receipt page is incomplete'
    if source_rel.startswith('/') or '..' in Path(source_rel).parts:
        return 'knowledge receipt source escapes the project'
    if kind == 'requirement' and not (source_rel.startswith('openspec/specs/') and source_rel.endswith('/spec.md')):
        return 'requirement source is not a synced spec'
    if kind == 'problem' and not source_rel.endswith('/verified-problem.json'):
        return 'problem source is not verified-problem.json'
    try:
        source = safe_path(root, source_rel)
        written = safe_path(root, page_rel)
    except ValueError:
        return 'knowledge receipt path is unsafe'
    if not written.resolve().is_relative_to((root / 'knowledge' / 'project').resolve()):
        return 'knowledge page is outside the initialized knowledge base'
    if fingerprint(source) != digest:
        return 'source_sha256 does not match ' + source_rel
    if not written.is_file():
        return 'missing page ' + page_rel
    if digest not in written.read_text(encoding='utf-8', errors='replace'):
        return 'page does not record source_sha256'
    return None


def knowledge_receipt_detail(root, change, capabilities):
    """Why a finished change cannot yet be archived, or None when the receipt holds."""
    root = Path(root)
    if project_knowledge_base(root) is None:
        return 'NOT_CONFIGURED'
    receipt_path = change / 'knowledge-receipt.json'
    if not receipt_path.is_file():
        return 'missing knowledge-receipt.json'
    try:
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return 'knowledge receipt is not json'
    if not isinstance(receipt, dict) or receipt.get('change') != change.name or receipt.get('alias') != 'project':
        return 'knowledge receipt target is not project'
    pages = receipt.get('pages')
    if not isinstance(pages, list):
        return 'knowledge receipt has no pages'
    for page in pages:
        detail = _page_detail(root, page)
        if detail:
            return detail
    if capabilities:
        sources = {page.get('source_path') for page in pages if page.get('artifact_kind') == 'requirement'}
        missing = ['openspec/specs/%s/spec.md' % cap for cap in capabilities if 'openspec/specs/%s/spec.md' % cap not in sources]
        if missing:
            return 'missing requirement page for ' + ', '.join(missing)
    record_path = change / 'verified-problem.json'
    if record_path.is_file():
        try:
            record = json.loads(record_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return 'verified problem record is not json'
        if isinstance(record, dict) and record.get('conclusion') == 'pass':
            expected = 'openspec/changes/%s/verified-problem.json' % change.name
            matched = any(page.get('artifact_kind') == 'problem' and page.get('source_path') == expected for page in pages)
            if not matched:
                return 'missing problem page'
            marked = receipt.get('problem')
            if isinstance(marked, dict) and marked.get('status') == 'not_applicable':
                return 'not_applicable is invalid when a verified problem passed'
            return None
    marked = receipt.get('problem')
    if not isinstance(marked, dict) or marked.get('status') != 'not_applicable' or not marked.get('reason'):
        return 'problem is not not_applicable'
    return None


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
            detail = knowledge_receipt_detail(root, change, capabilities)
            if detail:
                problem = 'knowledge receipt is not acceptable'
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
