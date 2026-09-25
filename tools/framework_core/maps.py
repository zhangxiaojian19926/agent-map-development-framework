"""Validate observations against current source, then render derived views."""
import os
from pathlib import Path
from .config import encoded
from .storage import safe_path, fingerprint

KINDS = {'contains', 'build-dependency', 'runtime-call', 'data-exchange'}


def validate_map(root, catalog, result):
    errors = []
    if not isinstance(result, dict) or set(result) - {'module_summaries', 'relationships', 'uncertainties', 'schema_version', 'source_digest'}:
        return ['UNTRUSTED_OUTPUT']
    if not all(isinstance(result.get(k), list) for k in ('module_summaries', 'relationships', 'uncertainties')):
        return ['INVALID_SCHEMA']
    if len(encoded(result)) > 1024 * 1024 or len(result['relationships']) > 1000:
        return ['OUTPUT_BUDGET_EXCEEDED']
    modules = catalog['modules']
    sources = {p: sha for m in modules.values() for p, sha in m.get('sources', {}).items()}
    ids = set()
    for edge in result['relationships']:
        if not isinstance(edge, dict):
            errors.append('INVALID_EDGE')
            continue
        if edge.get('id') in ids or not isinstance(edge.get('id'), str):
            errors.append('INVALID_EDGE_ID')
        ids.add(edge.get('id'))
        if edge.get('from') not in modules or edge.get('to') not in modules:
            errors.append('UNKNOWN_MODULE')
        if edge.get('kind') not in KINDS or edge.get('provenance') not in ('DECLARED', 'STATIC_SUPPORTED', 'INFERRED'):
            errors.append('INVALID_RELATION')
        if edge.get('runtime_validation') != 'NOT_RUN':
            errors.append('STATIC_IS_NOT_RUNTIME')
        if not isinstance(edge.get('interface'), str) or not edge['interface'].strip():
            errors.append('INVALID_INTERFACE')
        evidence = edge.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            errors.append('MISSING_EVIDENCE')
            continue
        covered = set()
        for item in evidence:
            try:
                rel = item['path']
                p = safe_path(root, rel)
                if rel not in sources or fingerprint(p) != item['sha256'] or sources[rel] != item['sha256']:
                    errors.append('STALE_EVIDENCE')
                elif not item.get('anchor') or item['anchor'] not in p.read_text():
                    errors.append('INVALID_ANCHOR')
                covered.update(mid for mid, m in modules.items() if rel in m.get('sources', {}))
            except (ValueError, OSError, KeyError, TypeError):
                errors.append('INVALID_EVIDENCE')
        if edge.get('provenance') == 'STATIC_SUPPORTED' and not {edge.get('from'), edge.get('to')} <= covered:
            errors.append('BOTH_ENDPOINTS_REQUIRED')
    summary_ids = []
    for item in result['module_summaries']:
        if not isinstance(item, dict) or item.get('id') not in modules or not isinstance(item.get('summary'), str) or not item.get('summary', '').strip():
            errors.append('INVALID_MODULE_SUMMARY')
        else:
            summary_ids.append(item['id'])
    if len(summary_ids) != len(modules) or set(summary_ids) != set(modules):
        errors.append('INCOMPLETE_MODULE_SUMMARIES')
    return errors


def design_mismatches(config, result):
    actual = {(e['from'], e['to'], e['kind']) for e in result['relationships'] if e['provenance'] == 'STATIC_SUPPORTED'}
    return [e for e in config.get('design_relationships', []) if (e['from'], e['to'], e['kind']) not in actual]


def render_map(result):
    lines = ['# Observed relationships', '', 'Static navigation only; runtime NOT_RUN.', '']
    for edge in result['relationships']:
        lines.append('- `{from}` → `{to}`: {kind}; {interface}; {provenance}; runtime NOT_RUN'.format(**edge))
        for evidence in edge['evidence']:
            lines.append('  - `' + evidence['path'] + '` — `' + evidence['anchor'].replace('\n', ' ') + '`')
    if not result['relationships']:
        lines.append('No supported relationships found; this does not prove independence.')
    return '\n'.join(lines) + '\n'


def map_outputs(root, catalog, result):
    outputs = {'docs/project/relationships.generated.json': encoded(result),
               'docs/project/relationships.generated.md': render_map(result)}
    summaries = {m['id']: m['summary'] for m in result['module_summaries']}
    lines = ['# Module map', '']
    for mid, module in sorted(catalog['modules'].items()):
        rel = 'docs/project/modules/' + mid + '.md'
        outputs[rel] = ('# ' + mid + '\n\n' + summaries.get(mid, 'Not analyzed') + '\n\n'
            'Module: `' + module['path'] + '`; state: ' + module['lifecycle'] + '.\n\n'
            '[Project workflow](../../../AGENTS.md). Read any existing module AGENTS before editing.\n'
            'Runtime tests: not discovered/verified; select from the approved implementation plan.\n')
        lines.append('- [' + mid + '](modules/' + mid + '.md): `' + module['path'] + '` — ' + module['presence'])
        if module.get('writable') and module['path'] != '.' and module['presence'] == 'present':
            agent_rel = module['path'] + '/AGENTS.md'
            if not safe_path(root, agent_rel).exists():
                link = os.path.relpath(root / rel, (root / agent_rel).parent)
                outputs[agent_rel] = '# Module entry\n\nRead [' + mid + '](' + link + ') and follow the root workflow.\n'
    outputs['docs/project/module-map.generated.md'] = '\n'.join(lines) + '\n'
    return outputs
