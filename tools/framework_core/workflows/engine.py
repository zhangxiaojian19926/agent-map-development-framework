"""Stage judgement for one change: does an action carry a valid approval?

The verdict is one published status code. The host keeps its own permission
decision; this gate only reports what the facts support.
"""
import json
from pathlib import Path

from ..config import identity
from .evidence import APPROVAL_SCHEMA, current_facts, verify_signature

REQUEST_SCHEMA = 'workflow-request/v1'
REPORT_SCHEMA = 'workflow-report/v1'
ACTIONS = {
    'read': '只读查看',
    'review': '只读评审',
    'edit_spec': '编辑规格草稿',
    'edit_plan': '编辑实施计划草稿',
    'edit_source': '编辑业务源码',
    'implement': '实施已批准规格',
}
NEEDS_APPROVAL = ('edit_source', 'implement')
PRIVATE_KEY_NOTE = ('签名私钥必须不在代理可读范围内（离线签名，或带口令且口令不进入代理上下文）；'
                    '这一条系统无法机械校验，请自行确认')


def _report(status, action, facts, reason, missing=None, next_actions=None):
    return {
        'schema': REPORT_SCHEMA,
        'operation': 'check',
        'status': status,
        'action': action,
        'reason': reason,
        'missing': missing or [],
        'facts': {'project': facts['project'], 'change': facts['change'], 'files': facts['files']},
        'axes': {
            'flow': {'status': status, 'reason': reason},
            'host': {'status': 'NOT_APPLICABLE', 'reason': '本地判定，未发生宿主工具调用'},
            'delivery': {'status': 'NOT_RUN', 'reason': '本期交付资格未核验'},
        },
        'next_actions': next_actions or [],
    }


def check(root, request, trust_path=None):
    """Judge one action against the current project facts. Writes nothing."""
    if not isinstance(request, dict) or request.get('schema') != REQUEST_SCHEMA:
        raise ValueError('INVALID_REQUEST: schema must be ' + REQUEST_SCHEMA)
    if request.get('operation') != 'check':
        raise ValueError('INVALID_REQUEST: operation must be check')
    action = request.get('action')
    if action not in ACTIONS:
        raise ValueError('INVALID_REQUEST: unknown action ' + str(action))
    change = request.get('change')
    identity(change)
    facts = current_facts(root, change)
    if not facts['files']:
        raise ValueError('INVALID_REQUEST: change has no spec or plan to verify')

    approval = request.get('approval') or {}
    missing = []
    if action in NEEDS_APPROVAL:
        if not approval.get('payload'):
            missing.append('approval.payload')
        if not approval.get('signature'):
            missing.append('approval.signature')
    if missing:
        return _report('NEEDS_DESIGN_APPROVAL', action, facts,
                       reason='缺少可核验批准：' + '、'.join(missing),
                       missing=missing,
                       next_actions=[
                           '由审批人用受信私钥签署载荷，签名负载绑定规格与计划的当前指纹',
                           '把载荷与签名路径放进请求后重新检查',
                       ])
    if action not in NEEDS_APPROVAL:
        return _report('READY', action, facts,
                       reason='%s不需要实现批准' % ACTIONS[action],
                       next_actions=['按已批准流程继续，宿主原生权限仍然独立生效'])

    try:
        verify_signature(approval['payload'], approval['signature'], trust_path)
    except ValueError as exc:
        code = str(exc).split(':', 1)[0]
        if code in ('TRUST_SOURCE_MISSING', 'VERIFIER_MISSING', 'TRUST_SOURCE_MUTABLE'):
            return _report('NOT_VERIFIED', action, facts, reason=str(exc),
                           next_actions=[
                               '把受信公钥放到代理写不进去的系统路径（文件与所在目录对当前用户不可写），或安装 ssh-keygen',
                               '补齐后重新检查，不要绕过受信来源',
                               PRIVATE_KEY_NOTE,
                           ])
        return _report('NEEDS_DESIGN_APPROVAL', action, facts, reason=str(exc),
                       missing=['approval.signature'],
                       next_actions=['请审批人用受信私钥重新签署载荷'])

    payload = json.loads(Path(approval['payload']).read_text(encoding='utf-8'))
    if not isinstance(payload, dict) or payload.get('schema') != APPROVAL_SCHEMA:
        return _report('NOT_VERIFIED', action, facts,
                       reason='批准载荷不符合 ' + APPROVAL_SCHEMA,
                       next_actions=['按 ' + APPROVAL_SCHEMA + ' 重新生成载荷并签署'])
    if payload.get('project') != facts['project']:
        return _report('STALE', action, facts, reason='批准引用来自其他项目',
                       next_actions=['请审批人针对本项目重新签署批准'])
    if payload.get('change') != facts['change']:
        return _report('STALE', action, facts, reason='批准引用来自其他 change',
                       next_actions=['请审批人针对本 change 重新签署批准'])
    if payload.get('files') != facts['files']:
        return _report('STALE', action, facts, reason='已批准的规格或计划内容已改变',
                       next_actions=['内容改变后旧批准失效，请审批人重新签署当前指纹'])
    if action not in (payload.get('scope') or []):
        return _report('NOT_AUTHORIZED', action, facts, reason='动作不在批准范围内',
                       next_actions=['请审批人把该动作写入批准范围后重新签署'])
    return _report('READY', action, facts, reason='批准有效且动作在批准范围内',
                   next_actions=['按已批准范围实施，宿主原生权限仍然独立生效',
                                 PRIVATE_KEY_NOTE])
