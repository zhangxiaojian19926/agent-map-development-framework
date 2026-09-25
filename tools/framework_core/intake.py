"""Strict human input and private launch state; never execute input text."""
import hashlib
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlsplit

from .config import digest, encoded
from .storage import atomic, project_lock, read_json, safe_path


def module_identity(name):
    if (not isinstance(name, str) or not name or name != name.strip() or
            name.endswith('.') or name in ('.', '..') or
            any(unicodedata.category(c).startswith('C') or c in '/\\<>:"|?*=：' for c in name)):
        raise ValueError('INVALID_NAME')
    normalized = unicodedata.normalize('NFC', name)
    if len(normalized.encode('utf-8')) > 180 or re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', normalized, re.I):
        raise ValueError('INVALID_NAME')
    mid = normalized if re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', normalized) else 'module-' + hashlib.sha256(normalized.encode()).hexdigest()[:12]
    return {'name': name, 'id': mid, 'path': 'modules/' + normalized,
            'collision_key': normalized.casefold()}


def validate_source(url, grants):
    if not isinstance(url, str) or not url or any(c.isspace() or ord(c) < 32 for c in url) or url.startswith('-') or '::' in url:
        raise ValueError('INVALID_SOURCE')
    try:
        parsed = urlsplit(url)
        if parsed.password or (parsed.scheme == 'https' and parsed.username) or parsed.query or parsed.fragment:
            raise ValueError('CREDENTIAL_OR_QUERY_IN_URL')
        if parsed.scheme in ('https', 'ssh') and parsed.hostname and parsed.path not in ('', '/'):
            return url
    except ValueError:
        raise ValueError('INVALID_SOURCE') from None
    if re.fullmatch(r'[\w.-]+@[\w.-]+:[\w./-]+', url):
        return url
    if 'local-clone' in grants and Path(url).is_absolute():
        return url
    raise ValueError('UNSUPPORTED_SOURCE')


def parse_request(text, default_name, grants=frozenset()):
    if not isinstance(text, str) or len(text.encode('utf-8')) > 1024 * 1024:
        raise ValueError('INPUT_BUDGET_EXCEEDED')
    lines = text.splitlines()
    structured = any(line.strip() == '# 工程启动单' for line in lines)
    section, metadata, modules, refs, names, ids = None, {}, [], {}, {}, {}
    saw_modules = False
    for number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or (line.startswith('#') and not line.startswith('## ') and line != '# 工程启动单'):
            continue
        if structured and line == '# 工程启动单':
            continue
        if structured and line in ('## 模块仓库', '## 来源版本'):
            section = line[3:]
            saw_modules |= section == '模块仓库'
            continue
        match = re.fullmatch(r'([^=:：]+?)\s*[=:：]\s*(.*)', line)
        if not match:
            raise ValueError('INVALID_INPUT: line ' + str(number))
        key, value = match.group(1).strip(), match.group(2).strip()
        try:
            if structured and section is None:
                if key not in ('项目', '目标', '仓库') or key in metadata or not value:
                    raise ValueError('INVALID_METADATA')
                metadata[key] = value
                continue
            if section == '来源版本':
                if key in refs or not re.fullmatch(r'(branch|tag|commit):[^\s]+', value):
                    raise ValueError('INVALID_REF')
                kind, ref = value.split(':', 1)
                if ref.startswith('-') or any(c in ref for c in '\\~^:?*[') or '..' in ref or '@{' in ref or ref.endswith(('/', '.')):
                    raise ValueError('INVALID_REF')
                if kind == 'commit' and not re.fullmatch(r'[0-9a-fA-F]{40}|[0-9a-fA-F]{64}', ref):
                    raise ValueError('INVALID_REF')
                refs[key] = {'kind': kind, 'value': ref}
                continue
            module = module_identity(key)
            if module['collision_key'] in names or module['id'].casefold() in ids:
                previous = names.get(module['collision_key'], ids.get(module['id'].casefold()))
                raise ValueError('NAME_CONFLICT: lines ' + str(previous) + ',' + str(number))
            names[module.pop('collision_key')] = number
            ids[module['id'].casefold()] = number
            module.update(source_url=validate_source(value, grants), requested_ref=None)
            modules.append(module)
        except ValueError as exc:
            raise ValueError(str(exc) + ': line ' + str(number)) from None
    by_name = {m['name']: m for m in modules}
    for name, ref in refs.items():
        if name not in by_name:
            raise ValueError('UNKNOWN_REF_MODULE')
        by_name[name]['requested_ref'] = ref
    if not modules and (saw_modules or not metadata.get('目标')):
        raise ValueError('MISSING_MODULES_OR_GOAL')
    if metadata.get('仓库') not in (None, '暂无', '无'):
        raise ValueError('USE_NAMED_MODULE_SECTION')
    module_identity(metadata.get('项目', default_name))
    return {'schema_version': 1, 'mode': 'remote-modules' if modules else 'new',
            'project': {'name': metadata.get('项目', default_name), 'goal': metadata.get('目标', '')},
            'modules': modules, 'input_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}


def checked_root(value):
    path = Path(value).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('SYMLINK_ROOT')
    path = path.resolve()
    if path in (Path('/'), Path.home().resolve()):
        raise ValueError('UNSAFE_TARGET')
    if path.exists() and not path.is_dir():
        raise ValueError('ROOT_NOT_DIRECTORY')
    return path


def plan_intake(request, target, staging, distribution):
    target, staging, distribution = map(checked_root, (target, staging, distribution))
    roots = (target, staging, distribution)
    if any(a.is_relative_to(b) for a in roots for b in roots if a != b) or len(set(roots)) != 3:
        raise ValueError('OVERLAPPING_ROOTS')
    # Private URLs and state never become an installed project artifact.
    plan = {'schema_version': 1, 'request': request, 'input_sha256': request['input_sha256'],
            'target': str(target), 'staging': str(staging), 'distribution': str(distribution)}
    plan['plan_id'] = digest(plan)
    existing = read_json(target, 'framework-project.json', {})
    if existing and existing.get('intake_id') != plan['plan_id']:
        raise ValueError('CONFLICT: already configured project; use its current workflow')
    saved = read_json(staging, 'request.json')
    if saved and saved != plan:
        raise ValueError('SOURCE_CONFLICT: launch request changed; review a new launch location')
    states = read_json(staging, 'acquisition.json', {}).get('modules', {})
    for module in request['modules']:
        path = safe_path(target, module['path'])
        if path.exists() and states.get(module['id'], {}).get('owned') != plan['plan_id']:
            raise ValueError('CONFLICT: unowned module target ' + module['id'])
    return plan


def validate_plan(plan):
    body = {k: v for k, v in plan.items() if k != 'plan_id'}
    if digest(body) != plan.get('plan_id'):
        raise ValueError('STALE_PLAN')
    return plan_intake(plan['request'], plan['target'], plan['staging'], plan['distribution'])


def save_intake(plan, original_text, grants):
    if 'write' not in grants:
        raise ValueError('CONSENT_REQUIRED: write')
    if hashlib.sha256(original_text.encode('utf-8')).hexdigest() != plan['input_sha256']:
        raise ValueError('STALE_INPUT')
    # Reparse even a well-formed forged plan: hashes bind data, not permission.
    parsed = parse_request(original_text, plan['request']['project']['name'], grants)
    if parsed != plan['request']:
        raise ValueError('STALE_PLAN')
    validate_plan(plan)
    staging = Path(plan['staging'])
    with project_lock(staging):
        validate_plan(plan)
        snapshot = safe_path(staging, 'PROJECT-START.md')
        if snapshot.exists() and snapshot.read_text() != original_text:
            raise ValueError('CONFLICT: launch snapshot changed')
        atomic(staging, 'request.json', encoded(plan))
        atomic(staging, 'PROJECT-START.md', original_text)
    return plan


def execute_intake(plan, grants, runner=None, auth=None):
    from .acquisition import acquire_modules
    from .config import build_plan
    from .generation import generation_changes
    from .modules import find_candidates, source_files
    from .process import run
    from .readiness import inspect_project
    from .storage import apply_files
    from .workflow import sync_catalog, save
    if 'write' not in grants:
        raise ValueError('CONSENT_REQUIRED: write')
    validate_plan(plan)
    root = Path(plan['target'])
    request = plan['request']
    existing = read_json(root, 'framework-project.json', {})
    binding = read_json(root, '.framework/local-state/intake.json', {})
    if existing.get('intake_id') == plan['plan_id'] and binding.get('plan_id') == plan['plan_id'] and read_json(root, 'module-catalog.generated.json'):
        # Completed onboarding is not a license to replay an obsolete module list.
        report = inspect_project(root)
        report['status'] = 'PREPARED' if report['onboarding'] == 'PREPARED' else report['status']
        report['next_action'] = 'use-current-project-workflow'
        return report
    acquired = None
    if request['modules']:
        acquired = acquire_modules(plan, grants, runner or run, auth)
        if acquired['status'] != 'COMPLETE':
            return acquired
    with project_lock(root):
        validate_plan(plan)
        config = read_json(root, 'framework-project.json', {})
        if config.get('intake_id') not in (None, plan['plan_id']):
            raise ValueError('CONFLICT: another launch owns this project')
        if config and 'intake_id' not in config:
            raise ValueError('CONFLICT: already configured project; use its refresh workflow')
        if request['modules']:
            declarations = [{k: m[k] for k in ('id', 'name', 'path')} for m in request['modules']]
        else:
            declarations = [{'id': c['id'], 'path': c['path']} for c in find_candidates(root, ['.'])]
            if not declarations and source_files(root, '.'):
                declarations = [{'id': 'root', 'path': '.'}]
        config.update(project_id=module_identity(request['project']['name'])['id'],
                      project_name=request['project']['name'], agent='current',
                      onboarding_mode='prepare', intake_id=plan['plan_id'],
                      modules=declarations, discovery_roots=['.'])
        # Requirements remain private launch data; copying into public facts is a separate decision.
        build_plan(root, config, 'prepare')
        changes = generation_changes(root, config, Path(plan['distribution']), prepare=True)
        apply_files(root, changes, 'intake-prepare')
        save(root, {'.framework/local-state/intake.json': encoded({
            'plan_id': plan['plan_id'], 'staging': plan['staging'], 'distribution': plan['distribution']})}, 'intake-binding')
        sync_catalog(root, config)
        report = inspect_project(root)
        report['status'] = 'PREPARED' if report['onboarding'] == 'PREPARED' else report['status']
        report['next_action'] = 'analyze-request' if any(m.get('sources') for m in read_json(root, 'module-catalog.generated.json')['modules'].values()) else 'requirements-design-review'
        if acquired:
            report['acquisition'] = {mid: {k: s.get(k) for k in ('name', 'path', 'state', 'resolved_commit')} for mid, s in acquired['modules'].items()}
        return report
