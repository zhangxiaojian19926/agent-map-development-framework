"""Command parsing and explicit current-invocation authorization."""
import argparse
import json
from pathlib import Path
import sys

from .config import CAPABILITIES, approval_check, build_plan, encoded
from .generation import generation_changes
from .modules import discover, catalog_update, find_candidates, source_files
from .storage import apply_files, owned_changes, read_json, resume_run, safe_path, project_lock, fingerprint
from .readiness import inspect_project
from .workflow import refresh, sync_catalog, save
from .adapters import clone, ensure_openspec
from .hooks import mark_dirty


def parser():
    p = argparse.ArgumentParser(description='Project-scoped development framework')
    p.add_argument('action', choices=['init', 'new', 'prepare', 'intake', 'analyze-request', 'accept-analysis', 'doctor', 'resume', 'refresh', 'module', 'event'])
    p.add_argument('operation', nargs='?', choices=['clone', 'add', 'sync'])
    p.add_argument('--target', required=True)
    p.add_argument('--config')
    p.add_argument('--project-id')
    p.add_argument('--agent', choices=['manual', 'codex', 'current'])
    p.add_argument('--allow', action='append', choices=sorted(CAPABILITIES), default=[])
    p.add_argument('--yes', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--index', action='store_true')
    p.add_argument('--hooks', action='store_true')
    p.add_argument('--openspec', action='store_true')
    p.add_argument('--path')
    p.add_argument('--id')
    p.add_argument('--url')
    p.add_argument('--ref')
    p.add_argument('--approve', action='append', default=[], metavar='ARTIFACT=SHA256')
    p.add_argument('--run-id')
    p.add_argument('--reason', default='git-event')
    p.add_argument('--request', help='Human startup input; current agent supplies the path')
    p.add_argument('--staging', help='Private launch directory outside target and framework')
    p.add_argument('--result', help='Current-session analysis envelope JSON')
    p.add_argument('--ssh-agent', help='Explicit current-user SSH agent socket; requires auth grant')
    return p


def output(result, code=0):
    print(encoded(result), end='')
    return code


def main(argv=None):
    args = parser().parse_args(argv)
    root = Path(args.target).absolute()
    try:
        safe_path(root, '.')
        root = root.resolve()
        if args.action == 'intake':
            from .intake import checked_root, execute_intake, parse_request, plan_intake, save_intake
            root = checked_root(args.target)
            if not args.staging:
                binding = read_json(root, '.framework/local-state/intake.json', {})
                args.staging = binding.get('staging')
                if not args.staging:
                    raise ValueError('MISSING_STAGING: current agent selects an authorized private launch directory')
            staging = checked_root(args.staging)
            input_path = Path(args.request) if args.request else safe_path(staging, 'PROJECT-START.md')
            if input_path.is_symlink() or input_path.stat().st_size > 1024 * 1024:
                raise ValueError('INVALID_REQUEST_FILE')
            text = input_path.read_text(encoding='utf-8')
            grants = set(args.allow)
            saved = read_json(staging, 'request.json')
            default_name = saved['request']['project']['name'] if saved else root.name
            request = parse_request(text, default_name, grants)
            plan = plan_intake(request, root, staging, Path(__file__).resolve().parents[2])
            if args.dry_run:
                return output(plan)
            needed = {'write'} | ({'clone'} if request['modules'] else set())
            if not needed <= grants:
                return output({'status': 'CONSENT_REQUIRED', 'required': sorted(needed - grants)}, 3)
            save_intake(plan, text, grants)
            report = execute_intake(plan, grants, auth={'ssh_agent': args.ssh_agent} if args.ssh_agent else None)
            return output(report, 0 if report['status'] == 'PREPARED' else 5)
        if args.action in ('analyze-request', 'accept-analysis'):
            from .handoff import make_analysis_request, accept_analysis
            if args.dry_run:
                return output({'action': args.action, 'required_capabilities': ['write', 'agent'], 'target': str(root)})
            if args.action == 'analyze-request':
                return output(make_analysis_request(root, read_json(root, 'module-catalog.generated.json', {}), set(args.allow)))
            if not args.result or Path(args.result).stat().st_size > 1024 * 1024:
                raise ValueError('INVALID_RESULT_FILE')
            return output(accept_analysis(root, json.loads(Path(args.result).read_text()), set(args.allow)))
        if args.action == 'doctor':
            report = inspect_project(root)
            return output(report, 0 if report['status'] == 'READY' else 5)
        if args.action == 'event':
            if not safe_path(root, 'framework-project.json').is_file():
                return output({'status': 'NOT_CONFIGURED'}, 5)
            mark_dirty(root, str(root), args.reason)
            return 0
        config_file = Path(args.config) if args.config else root / 'framework-project.json'
        config_before = fingerprint(config_file)
        project_before = fingerprint(safe_path(root, 'framework-project.json'))
        config = json.loads(config_file.read_text()) if config_file.is_file() else {}
        if not isinstance(config, dict):
            raise ValueError('Configuration must be a JSON object')
        if args.action in ('init', 'new', 'prepare'):
            config.setdefault('discovery_roots', ['.'])
        if args.action == 'prepare':
            config.setdefault('agent', 'current')
            config['onboarding_mode'] = 'prepare'
        for key in ('project_id', 'agent'):
            value = getattr(args, key)
            if value:
                config[key] = value
        for key in ('index', 'hooks', 'openspec'):
            if getattr(args, key):
                config[key] = True
        if args.action in ('init', 'prepare') and 'modules' not in config:
            config.setdefault('discovery_roots', ['.'])
            config['modules'] = [{'id': c['id'], 'path': c['path']} for c in find_candidates(root, config['discovery_roots'])]
            if args.action == 'prepare' and not config['modules'] and source_files(root, '.'):
                config['modules'] = [{'id': 'root', 'path': '.'}]
        if args.action in ('init', 'new') and not args.yes and not args.dry_run and sys.stdin.isatty():
            config.setdefault('project_id', input('Project id: ').strip())
            config.setdefault('agent', input('Agent [manual/codex]: ').strip())
        plan = build_plan(root, config, args.action)
        if args.action == 'module':
            if args.operation not in ('add', 'clone', 'sync'):
                raise ValueError('Specify module add/clone/sync')
            if args.operation == 'sync':
                plan['required_capabilities'] = ['write']
            elif not args.path or not args.id:
                raise ValueError('module add/clone require --path and --id')
            if args.operation == 'clone':
                plan['required_capabilities'].append('clone')
        if args.action == 'resume':
            plan['required_capabilities'] = ['write']
        if args.dry_run:
            if args.action in ('init', 'new', 'prepare'):
                try:
                    changes = generation_changes(root, config, Path(__file__).resolve().parents[2], prepare=args.action == 'prepare')
                    plan['files'] = [c['path'] for c in changes]
                    plan['input_hashes'] = {c['path']: c['before_sha256'] for c in changes}
                except ValueError as exc:
                    plan['conflicts'].append(str(exc))
            return output(plan)
        if args.action == 'new':
            approvals = dict(item.split('=', 1) for item in args.approve)
            missing = approval_check(config.get('artifacts', {}), approvals)
            if missing:
                return output({'status': 'NEEDS_DESIGN_APPROVAL', 'missing': missing,
                               'next_actions': ['Review requirements/design/plan, then pass --approve name=SHA256']}, 3)
        grants = set(args.allow)
        missing = set(plan['required_capabilities']) - grants
        if not args.yes and sys.stdin.isatty():
            print(encoded(plan), file=sys.stderr)
            if input('Grant exactly these capabilities? [yes/no] ').strip() == 'yes':
                grants.update(plan['required_capabilities'])
                missing = set()
        if missing:
            return output({'status': 'CONSENT_REQUIRED', 'required': sorted(missing)}, 3)
        with project_lock(root):
            if fingerprint(config_file) != config_before or fingerprint(safe_path(root, 'framework-project.json')) != project_before:
                raise ValueError('CONFLICT: configuration changed after planning')
            return execute(root, args, config, grants, approvals if args.action == 'new' else {})
    except (ValueError, OSError, KeyError, TypeError) as exc:
        conflict = any(word in str(exc) for word in ('CONFLICT', 'LOCKED'))
        approval = 'CONSENT_REQUIRED' in str(exc)
        return output({'status': 'CONFLICT' if conflict else ('CONSENT_REQUIRED' if approval else 'INVALID_INPUT'), 'error': str(exc)}, 3 if conflict or approval else 2)


def execute(root, args, config, grants, approvals):
    """Caller holds the entire operation lock, including external stages."""
    if args.action in ('init', 'new', 'prepare'):
        changes = generation_changes(root, config, Path(__file__).resolve().parents[2], prepare=args.action == 'prepare')
        apply_files(root, changes, 'bootstrap')
    if args.action == 'module' and args.operation == 'sync':
        return output({'status': 'SYNCED', 'catalog': sync_catalog(root, config)})
    if config.get('openspec') and args.action != 'resume':
        ensure_openspec(root, grants)
    if args.action == 'new':
        save(root, {'.framework/local-state/approvals.json': encoded(approvals)}, 'approvals')
    if args.action == 'prepare':
        sync_catalog(root, config)
        report = inspect_project(root)
        return output(report, 0 if report['onboarding'] == 'PREPARED' else 5)
    if args.action == 'resume':
        if not args.run_id:
            raise ValueError('Specify --run-id from .framework/local-state/runs')
        record = resume_run(root, args.run_id, grants)
        return output({'status': record['status'], 'next_actions': ['refresh with current capability grants']})
    if args.action == 'module':
        if args.operation == 'clone':
            result = clone(root, args.url, args.path, args.ref, grants)
            if result['exit_code']:
                return output({'status': 'CLONE_FAILED', 'result': result}, 4)
        if not safe_path(root, args.path).is_dir():
            raise ValueError('MODULE_NOT_FOUND')
        declarations = [m for m in config.get('modules', []) if m['id'] != args.id]
        declarations.append({'id': args.id, 'path': args.path})
        config['modules'] = declarations
        build_plan(root, config, 'module')
        save(root, {'framework-project.json': encoded(config)}, 'registration')
    report = refresh(root, config, grants)
    return output(report, 0 if report['status'] == 'READY' else 5)
