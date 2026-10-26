"""Persistent, explicitly authorized device pilot, recovery and rollout."""
import hashlib
import json
from pathlib import Path

from .storage import atomic, safe_path
from .reverse_v2 import operation_argv, operation_for, state_root


STATE_FILE = 'device-state.json'


def state_path(scope_id):
    return state_root(scope_id) + '/' + STATE_FILE


def load_state(root, scope_id):
    path = safe_path(root, state_path(scope_id))
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None


def save_state(root, scope_id, state):
    atomic(root, state_path(scope_id), json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + '\n')


def validate_backup(backup):
    if not isinstance(backup, dict) or set(backup) != {'path', 'sha256'}:
        raise ValueError('BACKUP_INVALID')
    if not isinstance(backup['path'], str) or not isinstance(backup['sha256'], str):
        raise ValueError('BACKUP_INVALID')
    path = Path(backup['path'])
    if not path.is_file() or path.is_symlink():
        raise ValueError('BACKUP_INVALID')
    if hashlib.sha256(path.read_bytes()).hexdigest() != backup['sha256']:
        raise ValueError('BACKUP_INVALID')


def validate_plan(scope, operations):
    plan = scope['device_plan']
    required = {'action', 'backup', 'operations', 'verify', 'restore', 'rollout'}
    if set(plan) != required or plan['action'] not in ('pilot', 'rollback', 'rollout'):
        raise ValueError('INVALID_DEVICE_PLAN')
    for field, action, read_only in (('operations', 'change', False), ('verify', 'verify', True),
                                     ('restore', 'restore', False)):
        items = plan[field]
        if not isinstance(items, list) or not items:
            raise ValueError('INVALID_DEVICE_PLAN')
        seen = set()
        for item in items:
            if (not isinstance(item, dict) or set(item) != {'id', 'operation'}
                    or not item['id'] or item['id'] in seen):
                raise ValueError('INVALID_DEVICE_PLAN')
            seen.add(item['id'])
            operation_for(operations, item['operation'], action, read_only)
    if not isinstance(plan['rollout'], list):
        raise ValueError('INVALID_DEVICE_PLAN')
    seen = set()
    for item in plan['rollout']:
        if (not isinstance(item, dict) or set(item) != {'device_id', 'baseline_sha256', 'backup'}
                or not item['device_id'] or item['device_id'] in seen):
            raise ValueError('INVALID_DEVICE_PLAN')
        seen.add(item['device_id'])
        validate_backup(item['backup'])
    validate_backup(plan['backup'])


def new_state():
    return {'schema': 'device-change/v1', 'state': 'PROPOSED', 'history': ['PROPOSED'],
            'operations': [], 'rollout': {}}


def transition(root, scope_id, state, value):
    if state['state'] != value:
        state['state'] = value
        state['history'].append(value)
    save_state(root, scope_id, state)


def run_steps(root, scope, device_id, items, runner, operations, state):
    for item in items:
        spec = operation_for(operations, item['operation'],
                             'verify' if items is scope['device_plan']['verify'] else
                             ('restore' if items is scope['device_plan']['restore'] else 'change'),
                             items is scope['device_plan']['verify'])
        argv = operation_argv(spec, device_id)
        result = runner(argv, root, spec['timeout'])
        succeeded = result.get('exit_code', 1) == 0 and not result.get('timed_out') and not result.get('output_limit')
        state['operations'].append({'device_id': device_id, 'id': item['id'],
                                    'operation': item['operation'], 'status': 'OK' if succeeded else 'FAILED'})
        save_state(root, scope['id'], state)
        if not succeeded:
            return False
    return True


def execute_device(root, scope, grants, runner, operations, baseline_status):
    plan = scope.get('device_plan')
    if plan is None:
        return 'NOT_REQUESTED', 'NOT_RUN'
    validate_plan(scope, operations)
    state = load_state(root, scope['id']) or new_state()
    action = plan['action']
    grant = 'device-rollout' if action == 'rollout' else 'device-change'
    if grant not in grants:
        return 'NOT_AUTHORIZED', 'NOT_RUN'
    if baseline_status:
        return baseline_status, 'NOT_RUN'

    if action == 'pilot':
        if state['state'] in ('FAILED', 'ROLLBACK_READY', 'ROLLED_BACK', 'COMPLETE', 'PARTIAL'):
            return state['state'], 'PASS' if state['state'] == 'ROLLBACK_READY' else 'NOT_RUN'
        transition(root, scope['id'], state, 'RECOVERY_READY')
        if not run_steps(root, scope, scope['target']['device_id'], plan['operations'], runner, operations, state):
            transition(root, scope['id'], state, 'FAILED')
            return 'FAILED', 'NOT_RUN'
        transition(root, scope['id'], state, 'PILOT_APPLIED')
        if not run_steps(root, scope, scope['target']['device_id'], plan['verify'], runner, operations, state):
            transition(root, scope['id'], state, 'FAILED')
            return 'FAILED', 'NOT_RUN'
        transition(root, scope['id'], state, 'PILOT_VERIFIED')
        transition(root, scope['id'], state, 'ROLLBACK_READY')
        return 'ROLLBACK_READY', 'PASS'

    if action == 'rollback':
        if state['state'] == 'ROLLED_BACK':
            return 'ROLLED_BACK', 'NOT_RUN'
        if state['state'] != 'ROLLBACK_READY':
            return 'RECOVERY_NOT_READY', 'NOT_RUN'
        if not run_steps(root, scope, scope['target']['device_id'], plan['restore'], runner, operations, state):
            transition(root, scope['id'], state, 'FAILED')
            return 'FAILED', 'NOT_RUN'
        transition(root, scope['id'], state, 'ROLLED_BACK')
        return 'ROLLED_BACK', 'NOT_RUN'

    if state['state'] not in ('ROLLBACK_READY', 'COMPLETE', 'PARTIAL'):
        return 'PILOT_NOT_VERIFIED', 'NOT_RUN'
    transition(root, scope['id'], state, 'ROLLOUT_IN_PROGRESS')
    for item in plan['rollout']:
        device_id = item['device_id']
        previous = state['rollout'].get(device_id, {}).get('status')
        if previous in ('FAILED', 'COMPLETE', 'STALE'):
            continue
        if item['baseline_sha256'] != scope['target']['baseline_sha256']:
            state['rollout'][device_id] = {'status': 'STALE', 'operations': []}
            save_state(root, scope['id'], state)
            continue
        validate_backup(item['backup'])
        target = dict(scope['target'])
        target['device_id'] = device_id
        target['baseline_sha256'] = item['baseline_sha256']
        from .reverse_v2 import check_baseline
        status = check_baseline(root, {'id': scope['id'], 'target': target}, grants, runner, operations)
        if status:
            state['rollout'][device_id] = {'status': status, 'operations': []}
            save_state(root, scope['id'], state)
            continue
        local = {'id': scope['id'], 'device_plan': plan}
        before = len(state['operations'])
        if not run_steps(root, local, device_id, plan['operations'], runner, operations, state):
            state['rollout'][device_id] = {'status': 'FAILED', 'operations': state['operations'][before:]}
            save_state(root, scope['id'], state)
            continue
        if not run_steps(root, local, device_id, plan['verify'], runner, operations, state):
            state['rollout'][device_id] = {'status': 'FAILED', 'operations': state['operations'][before:]}
            save_state(root, scope['id'], state)
            continue
        state['rollout'][device_id] = {'status': 'COMPLETE', 'operations': state['operations'][before:]}
        save_state(root, scope['id'], state)
    statuses = {item['status'] for item in state['rollout'].values()}
    final = 'PARTIAL' if statuses - {'COMPLETE'} else 'COMPLETE'
    transition(root, scope['id'], state, final)
    return final, 'NOT_RUN'
