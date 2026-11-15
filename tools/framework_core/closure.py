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

# A reusable conclusion must say when it holds and when it must not be used.
# `requirement` is deliberately absent: a requirement is not a conclusion that
# can be recalled outside the change it belongs to.
PAGE_APPLICABILITY = {
    'problem': ('applies_when', 'not_applicable_when'),
    'concept': ('applies_when',),
}
# The page status vocabulary. It is declared by the knowledge schema, not by
# the framework's own status dictionary — those are two different vocabularies.
PAGE_STATUSES = ('approved', 'verified', 'temporary-workaround',
                 'superseded', 'retracted', 'needs-review')
SUPERSEDED = 'superseded'
RETRACTED = 'retracted'
NEEDS_REVIEW = 'needs-review'
VOID_STATUSES = (SUPERSEDED, RETRACTED)
RETRACTION_REASON = 'retraction_reason'
RECEIPT_SCHEMA_V2 = 'knowledge-receipt/v2'
PLACEHOLDER = re.compile(r"^\{\{.*\}\}$")
CONCEPT_SOURCES = ('docs/project/GLOSSARY.md',)


def page_fields(text):
    """Frontmatter key -> raw value for a knowledge page."""
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        item = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if item:
            fields[item.group(1)] = item.group(2).strip()
    return fields


def missing_applicability(fields, kind):
    """Which applicability fields this page kind must declare but does not."""
    required = PAGE_APPLICABILITY.get(kind, ())
    missing = []
    for key in required:
        value = fields.get(key, '')
        if not value or PLACEHOLDER.match(value):
            missing.append(key)
    return missing


def concept_source_allowed(source_rel):
    """A concept page points at the glossary or at a synced capability spec."""
    if source_rel in CONCEPT_SOURCES:
        return True
    return source_rel.startswith('openspec/specs/') and source_rel.endswith('/spec.md')


def knowledge_page_index(root):
    """Every knowledge page in the initialized base: KB-relative path -> frontmatter."""
    kb = root / 'knowledge' / 'project'
    index = {}
    if not kb.is_dir() or kb.is_symlink():
        return index
    for path in sorted(kb.rglob('*.md')):
        try:
            text = path.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        index[path.relative_to(kb).as_posix()] = page_fields(text)
    return index


def page_ref(ref):
    """Normalise a page reference so both spellings point at the same page."""
    ref = (ref or '').strip()
    prefix = 'knowledge/project/'
    if ref.startswith(prefix):
        return ref[len(prefix):]
    return ref


def status_machine_errors(index, scope):
    """A conclusion that was superseded or retracted must be consistent about it."""
    errors = []
    for rel in scope:
        fields = index.get(rel)
        if fields is None:
            continue
        status = fields.get('status', '')
        if status and status not in PAGE_STATUSES:
            errors.append('%s: status is not a known page status: %s' % (rel, status))
            continue
        if status == SUPERSEDED:
            raw = fields.get('superseded_by', '')
            target = page_ref(raw)
            if not raw or PLACEHOLDER.match(raw) or target not in index:
                errors.append('%s: superseded page does not point at an existing successor' % rel)
        if status == RETRACTED:
            reason = fields.get(RETRACTION_REASON, '')
            if not reason or PLACEHOLDER.match(reason):
                errors.append('%s: retracted page states no retraction reason' % rel)
    voided = {rel for rel, fields in index.items() if fields.get('status', '') in VOID_STATUSES}
    for rel, fields in sorted(index.items()):
        if rel in voided:
            continue
        applies = fields.get('applies_when', '')
        for target in sorted(voided):
            if target in applies or page_ref(target) in applies:
                errors.append('%s: applies_when still points at a voided page: %s' % (rel, target))
    return errors


def knowledge_references(root):
    """How often each knowledge page is named by a knowledge receipt."""
    counts = {}
    changes = root / 'openspec' / 'changes'
    if not changes.is_dir():
        return counts
    for receipt_path in sorted(changes.rglob('knowledge-receipt.json')):
        try:
            data = json.loads(receipt_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        for page in data.get('pages') or []:
            if isinstance(page, dict) and page.get('path'):
                ref = page_ref(page['path'])
                counts[ref] = counts.get(ref, 0) + 1
    return counts


def needs_review_downstream(index):
    """For each page under review, the pages that still quote it."""
    downstream = {}
    for rel, fields in sorted(index.items()):
        if fields.get('status', '') != NEEDS_REVIEW:
            continue
        quoted = []
        for other, other_fields in sorted(index.items()):
            if other == rel:
                continue
            applies = other_fields.get('applies_when', '')
            if rel in applies or page_ref(rel) in applies:
                quoted.append(other)
        downstream[rel] = quoted
    return downstream


def receipt_task_ids(change):
    """Task identifiers the change's own task list declares."""
    path = change / 'tasks.md'
    if not path.is_file():
        return set()
    text = path.read_text(encoding='utf-8', errors='replace')
    ids = set()
    for line in text.splitlines():
        item = re.match(r"^\s*-\s*\[[ xX]\]\s*([0-9]+(?:\.[0-9]+)*)\b", line)
        if item:
            ids.add(item.group(1))
    return ids


def _worktree_influence_error(entry, root):
    """file and assertion have to be text in this worktree. The page citation is checked apart."""
    rel = entry.get('file')
    assertion = entry.get('assertion')
    if not isinstance(rel, str) or not rel:
        return ('knowledge receipt influenced entry points at a file that is not in the worktree: '
                + str(rel))
    try:
        path = safe_path(root, rel)
    except ValueError:
        return 'knowledge receipt influenced entry file escapes the project: ' + rel
    if not path.is_file():
        return ('knowledge receipt influenced entry points at a file that is not in the worktree: '
                + rel)
    text = path.read_text(encoding='utf-8', errors='replace')
    if not isinstance(assertion, str) or not assertion or assertion not in text:
        return ('knowledge receipt influenced entry assertion is not in the file: '
                + str(assertion))
    page = entry.get('page')
    if not isinstance(page, str) or not page or page not in text:
        return 'knowledge receipt influenced entry file does not cite the page: ' + str(page)
    return None


def influenced_errors(receipt, pages, change, root):
    """A v2 receipt has to show whether the knowledge actually changed something."""
    if receipt.get('schema') != RECEIPT_SCHEMA_V2:
        return []
    influenced = receipt.get('influenced')
    if isinstance(influenced, dict):
        if influenced.get('status') == 'not_applicable' and influenced.get('reason'):
            return []
        return ['knowledge receipt declares influenced as not applicable without a reason']
    if not isinstance(influenced, list) or not influenced:
        return ['knowledge receipt v2 does not record whether the knowledge took effect']
    known = {page_ref(page.get('path', '')) for page in pages if isinstance(page, dict)}
    tasks = receipt_task_ids(change)
    for entry in influenced:
        if not isinstance(entry, dict):
            return ['knowledge receipt influenced entry is not an object']
        if page_ref(entry.get('page', '')) not in known:
            return ['knowledge receipt influenced entry points at a page that is not in the receipt: '
                    + str(entry.get('page'))]
        if entry.get('task_id') not in tasks:
            return ['knowledge receipt influenced entry points at a task that does not exist: '
                    + str(entry.get('task_id'))]
        mismatch = _worktree_influence_error(entry, root)
        if mismatch:
            return [mismatch]
    return []


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
    if kind not in ('requirement', 'problem', 'concept'):
        return 'knowledge receipt page kind is not requirement, problem or concept'
    if not isinstance(source_rel, str) or not isinstance(page_rel, str) or not isinstance(digest, str):
        return 'knowledge receipt page is incomplete'
    if source_rel.startswith('/') or '..' in Path(source_rel).parts:
        return 'knowledge receipt source escapes the project'
    if kind == 'requirement' and not (source_rel.startswith('openspec/specs/') and source_rel.endswith('/spec.md')):
        return 'requirement source is not a synced spec'
    if kind == 'problem' and not source_rel.endswith('/verified-problem.json'):
        return 'problem source is not verified-problem.json'
    if kind == 'concept' and not concept_source_allowed(source_rel):
        return 'concept source is not the project glossary or a synced spec'
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
    text = written.read_text(encoding='utf-8', errors='replace')
    if digest not in text:
        return 'page does not record source_sha256'
    missing = missing_applicability(page_fields(text), kind)
    if missing:
        return 'page is missing %s: %s' % (kind + ' page applicability', ', '.join(missing))
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
    index = knowledge_page_index(root)
    scope = [page_ref(page.get('path', '')) for page in pages]
    problems = status_machine_errors(index, scope)
    if problems:
        return problems[0]
    influence = influenced_errors(receipt, pages, change, root)
    if influence:
        return influence[0]
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
