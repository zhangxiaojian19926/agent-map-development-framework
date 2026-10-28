"""Automatic request → profile → approved plan → health → observation orchestration."""
import json
import platform as host_platform
from pathlib import Path
import sys

from .reverse_adapters import (auto_root, behavior_contract, execute_observation, public_summary)
from .reverse_install import install_archive, install_npm, inspect_installed
from .reverse_planner import build_plan, load_catalog, load_lock, tool_spec
from .reverse_request import profile_request, validate_request
from .reverse_v2 import encoded
from .reverse_web import fetch_snapshot, profile_snapshot
from .storage import atomic, safe_path


def host():
    machine = host_platform.machine().lower()
    machine = {'x86_64': 'x64', 'amd64': 'x64', 'aarch64': 'arm64'}.get(machine, machine)
    platform = 'darwin' if sys.platform == 'darwin' else 'linux' if sys.platform.startswith('linux') else sys.platform
    return platform, machine


def plan_path(request_id, plan_sha256):
    return auto_root(request_id) + '/plans/' + plan_sha256 + '.json'


def save_plan(root, plan, request_id):
    rel = plan_path(request_id, plan['plan_sha256'])
    atomic(root, rel, encoded(plan))
    return rel


def missing_grants(plan, grants, remote=False):
    required = {'write', 'reverse'}
    if remote:
        required.add('web-fetch')
    # Browser, network and session grants remain per-observation so static work can complete.
    if any(item['action'] in ('INSTALL', 'REPAIR') for item in plan['tools']):
        required.add('reverse-install')
    return sorted(required - set(grants))


def resolve_tools(root, plan, grants, catalog, lock, platform, machine, opener, runner):
    if any(item['action'] in ('INSTALL', 'REPAIR') for item in plan['tools']) and 'reverse-install' not in grants:
        return None, {'status': 'CONSENT_REQUIRED', 'required': ['reverse-install'], 'toolchain_status': 'BLOCKED'}
    installed = {}
    actions = []
    for item in plan['tools']:
        name = item['tool_id']
        registered = catalog['tools'][name]
        spec = tool_spec(name, catalog, lock, platform)
        if item['action'] == 'INSTALL':
            if registered['installer'] == 'npm':
                result = install_npm(root, name, spec, runner=runner)
            else:
                result = install_archive(root, name, spec, platform, machine, opener=opener, runner=runner)
        elif item['action'] == 'REPAIR':
            if registered['installer'] == 'npm':
                result = install_npm(root, name, spec, runner=runner, repair=True)
            else:
                result = install_archive(root, name, spec, platform, machine, opener=opener, runner=runner, repair=True)
        elif item['action'] == 'REUSE':
            result = {'status': 'INSTALLED', 'action': 'REUSE'}
        else:
            return None, {'status': 'TOOLCHAIN_BLOCKED', 'tool': name, 'reason': item['reason']}
        actions.append({'tool_id': name, 'action': result.get('action', item['action']), 'status': result['status']})
        if result['status'] not in ('INSTALLED', 'READY'):
            return None, {'status': 'INSTALL_FAILED', 'tool': name, 'reason': result['status'],
                          'detail': result, 'actions': actions}
        npm = registered['installer'] == 'npm'
        healthy = inspect_installed(root, name, spec, None if npm else platform, None if npm else machine,
                                    runner=runner,
                                    probe=bool(spec.get('entrypoint')) and spec.get('probe', True))
        if healthy['status'] != 'READY':
            return None, {'status': 'HEALTH_FAILED', 'tool': name, 'reason': healthy['status'],
                          'detail': healthy, 'actions': actions}
        installed[name] = {'version': spec['version'], 'bin': healthy.get('bin'),
                           'install_path': healthy['install_path'], 'receipt': healthy['receipt']}
    return installed, actions


def summarize_observations(records):
    statuses = {record['status'] for record in records}
    if statuses == {'RECORDED'}:
        return 'RECORDED'
    if len(statuses) == 1:
        return next(iter(statuses))
    return 'PARTIAL'


def execute_auto(root, request, grants, approvals=None, dry_run=False, opener=None, runner=None,
                 provider=None, platform=None, machine=None, snapshot=None, resolver=None,
                 product_draft=None):
    approvals = approvals or {}
    grants = set(grants)
    validate_request(request)
    root = Path(root)
    platform, machine = (platform, machine) if platform and machine else host()
    catalog, lock = load_catalog(), load_lock()
    manifest = snapshot
    if request['target']['kind'] == 'url' and manifest is None:
        preparation = profile_request(request)
        if dry_run or 'web-fetch' not in grants:
            preparation['status'] = 'SNAPSHOT_REQUIRED' if dry_run else 'NOT_AUTHORIZED'
            preparation['required_grants'] = [] if 'web-fetch' in grants else ['web-fetch']
            return preparation
        manifest = fetch_snapshot(root, request, grants, opener=opener, resolver=resolver)
        if manifest.get('status') == 'NOT_AUTHORIZED':
            return manifest
    profile = profile_snapshot(root, request, manifest) if manifest else profile_request(request)
    plan = build_plan(root, request, profile, catalog, lock, platform, machine, probe=False)
    product_preview = None
    if product_draft is not None:
        from .product_recon import preview_product_recon
        product_preview = preview_product_recon(product_draft, request, plan)
    if dry_run:
        result = {'status': 'DRY_RUN', 'plan': plan, 'plan_sha256': plan.get('plan_sha256'),
                  'required_grants': plan.get('required_grants', [])}
        if product_preview is not None:
            result['product_recon'] = product_preview
        return result
    if plan['status'] != 'READY':
        return {'status': plan['status'], 'plan': plan, 'toolchain_status': 'BLOCKED',
                'observation_status': 'NOT_RUN', 'runtime_validation': 'NOT_RUN'}
    saved_plan = save_plan(root, plan, request['id'])
    atomic(root, auto_root(request['id']) + '/request.json', encoded(request))
    approved = approvals.get('toolchain')
    if approved is None:
        result = {'status': 'PLAN_APPROVAL_REQUIRED', 'plan': plan, 'plan_sha256': plan['plan_sha256'],
                  'plan_path': saved_plan, 'required_grants': plan['required_grants']}
        if product_preview is not None:
            result['product_recon'] = product_preview
        return result
    if approved != plan['plan_sha256']:
        return {'status': 'PLAN_CONFLICT', 'expected': plan['plan_sha256'], 'approved': approved,
                'plan_path': saved_plan}
    missing = missing_grants(plan, grants, remote=request['target']['kind'] == 'url')
    if missing:
        return {'status': 'CONSENT_REQUIRED', 'required': missing, 'plan_sha256': plan['plan_sha256']}
    current_profile = profile_snapshot(root, request, manifest) if manifest else profile_request(request)
    if current_profile.get('target_sha256') != plan['target'].get('target_sha256'):
        return {'status': 'PLAN_CONFLICT', 'error': 'STALE_TARGET', 'plan_sha256': plan['plan_sha256']}
    tools, installation = resolve_tools(root, plan, grants, catalog, lock, platform, machine, opener, runner)
    if tools is None:
        installation['plan_sha256'] = plan['plan_sha256']
        installation.setdefault('observation_status', 'NOT_RUN')
        installation.setdefault('runtime_validation', 'NOT_RUN')
        return installation
    records = [execute_observation(root, request, plan, observation, grants, tools=tools,
                                   runner=runner, provider=provider, catalog=catalog, manifest=manifest)
               for observation in request['observations']]
    observation_status = summarize_observations(records)
    contract = None
    product_result = None
    if observation_status == 'RECORDED':
        contract = behavior_contract(request, plan, records)
        atomic(root, auto_root(request['id']) + '/behavior-contract.json', encoded(contract))
        if product_draft is not None:
            from .product_recon import generate_product_recon
            product_result = generate_product_recon(root, request, plan, contract, records, product_draft)
    elif product_draft is not None:
        raise ValueError('PRODUCT_RECON_EVIDENCE: behavior contract is not ready')
    if request['evidence']['public']:
        atomic(root, 'docs/project/reverse/' + request['id'] + '.md',
               public_summary(request, plan, records, 'READY',
                              product=product_result['product'] if product_result else None))
    result = {'status': 'READY' if observation_status == 'RECORDED' else 'PARTIAL',
              'plan_sha256': plan['plan_sha256'], 'plan_path': saved_plan,
              'toolchain_status': 'READY', 'installation': installation,
              'observation_status': observation_status, 'runtime_validation': 'NOT_RUN',
              'observations': [{'id': record['id'], 'status': record['status']} for record in records],
              'behavior_contract': contract['schema'] if contract else 'NOT_READY',
              'snapshot_sha256': manifest['snapshot_sha256'] if manifest else None}
    if product_result is not None:
        result['product_recon'] = {key: product_result[key] for key in ('status', 'path', 'sha256')}
    return result


def auto_report(root):
    """Read-only receipt, plan, snapshot and evidence freshness; never probes or repairs."""
    import hashlib
    from .reverse_request import canonical
    from .reverse_v2 import sha_text
    from .reverse_web import load_snapshot
    base = safe_path(root, '.framework/local-state/reverse/auto')
    if not base.is_dir():
        return None
    reports = []
    installs = []
    try:
        state_dir = safe_path(root, '.framework/local-state/reverse/installs')
        if state_dir.is_dir():
            for marker_path in sorted(state_dir.glob('*.json')):
                marker = json.loads(marker_path.read_text(encoding='utf-8'))
                receipt_path = safe_path(root, '.framework/tools/' + marker['name'] + '/' +
                                         marker['version'] + '/install-receipt.json')
                actual = hashlib.sha256(receipt_path.read_bytes()).hexdigest() if receipt_path.is_file() else None
                receipt = json.loads(receipt_path.read_text(encoding='utf-8')) if actual else {}
                healthy = actual == marker.get('receipt_sha256') and receipt.get('status') == 'READY'
                entry = receipt.get('entrypoint')
                if healthy and entry:
                    binary = receipt_path.parent / entry
                    healthy = binary.is_file()
                    if binary.is_symlink():
                        healthy = (entry.startswith('node_modules/.bin/')
                                   and binary.resolve().is_relative_to(receipt_path.parent.resolve())
                                   and binary.resolve().is_file())
                installs.append({'name': marker['name'], 'version': marker['version'],
                                 'status': 'PRESENT' if healthy else 'STALE'})
        for request_dir in sorted(path for path in base.iterdir() if path.is_dir() and not path.is_symlink()):
            records = []
            stale = False
            plans = request_dir / 'plans'
            if plans.is_dir():
                for path in sorted(plans.glob('*.json')):
                    plan = json.loads(path.read_text(encoding='utf-8'))
                    claimed = plan.get('plan_sha256')
                    body = {key: value for key, value in plan.items() if key != 'plan_sha256'}
                    if not claimed or path.stem != claimed or sha_text(canonical(body)) != claimed:
                        stale = True
            snapshots = request_dir / 'snapshots'
            if snapshots.is_dir():
                for snapshot_dir in sorted(path for path in snapshots.iterdir() if path.is_dir()):
                    load_snapshot(root, request_dir.name, snapshot_dir.name)
            request_path = request_dir / 'request.json'
            request = json.loads(request_path.read_text(encoding='utf-8')) if request_path.is_file() else None
            observations = request_dir / 'observations'
            if observations.is_dir():
                for path in sorted(observations.glob('*.json')):
                    record = json.loads(path.read_text(encoding='utf-8'))
                    records.append({'id': record.get('id'), 'status': record.get('status'),
                                    'plan_sha256': record.get('plan_sha256'),
                                    'target_sha256': record.get('target_sha256')})
                    if record.get('raw_path'):
                        raw = safe_path(root, record['raw_path'])
                        if (not raw.is_file()
                                or hashlib.sha256(raw.read_bytes()).hexdigest() != record['raw_sha256']):
                            stale = True
                    if request and request['target']['kind'] == 'file':
                        target = Path(request['target']['path'])
                        if (not target.is_file() or target.is_symlink()
                                or hashlib.sha256(target.read_bytes()).hexdigest() != record['target_sha256']):
                            stale = True
            reports.append({'id': request_dir.name, 'status': 'STALE' if stale else 'PRESENT',
                            'observations': records})
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        reports.append({'id': 'unknown', 'status': 'STALE', 'reason': str(exc), 'observations': []})
    stale = any(item['status'] == 'STALE' for item in reports + installs)
    return {'status': 'STALE' if stale else 'PRESENT', 'requests': reports, 'installs': installs,
            'checked': 'READ_ONLY', 'tool_execution': 'NOT_RUN', 'network': 'NOT_RUN', 'repair': 'NOT_RUN'}
