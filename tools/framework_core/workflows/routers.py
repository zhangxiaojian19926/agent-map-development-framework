"""Render the fifteen workflow routers from the combination manifest."""
import json
from pathlib import Path


DISTRIBUTION = Path(__file__).resolve().parents[3]
COMBINATIONS = Path(__file__).with_name('combinations.json')
CATALOG = Path(__file__).with_name('catalog.json')
GUIDE = DISTRIBUTION / 'docs/guide/from-zero-to-one.md'
FLOWS = DISTRIBUTION / 'skill/flows'
GUIDE_HEADING = '### 每条工作流用到的技能'
MEMBER_GROUPS = ('openspec', 'superpowers', 'matt-pocock', 'llm-wiki', 'project-bootstrap', 'reverse-engineer')


def load_combinations(path=None):
    return json.loads(Path(path or COMBINATIONS).read_text(encoding='utf-8'))


def description_of(flow):
    return '在用户提出「%s」时使用。%s' % (flow['trigger'], flow['purpose'])


def render_skill(flow):
    body = ['---', 'name: ' + flow['id'], 'description: ' + description_of(flow), '---', '',
            '# ' + flow['id'] + ' ' + flow['name'], '']
    for section in flow['sections']:
        body.append('## ' + section['heading'])
        body.append('')
        body.extend(section['lines'])
        body.append('')
    text = '\n'.join(body).rstrip() + '\n'
    return text


def write_routers(root=None):
    """Write skill/flows/flow-01..flow-15 from the manifest."""
    root = Path(root or DISTRIBUTION)
    data = load_combinations(root / 'tools/framework_core/workflows/combinations.json')
    written = []
    for flow in data['flows']:
        path = root / 'skill/flows' / flow['id'] / 'SKILL.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_skill(flow), encoding='utf-8')
        written.append(path)
    return written


def sync_catalog(root=None):
    """Replace each catalog skills array with that flow's mention set."""
    root = Path(root or DISTRIBUTION)
    data = load_combinations(root / 'tools/framework_core/workflows/combinations.json')
    catalog_path = root / 'tools/framework_core/workflows/catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    mentions = {flow['id']: list(flow['mentions']) for flow in data['flows']}
    for item in catalog['flows']:
        if item['id'] in mentions:
            item['skills'] = mentions[item['id']]
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return mentions


def guide_cell(flow):
    if not flow['mentions']:
        return '无'
    return '、'.join('`%s`' % name for name in flow['mentions'])


def splice_guide(text, flows):
    """Replace the skill column of the workflow skill table."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == GUIDE_HEADING:
            start = index
            break
    if start is None:
        raise ValueError('guide skill table missing')
    rows = {flow['id']: guide_cell(flow) for flow in flows}
    replaced = 0
    for index in range(start + 1, len(lines)):
        if lines[index].startswith('## '):
            break
        parts = [part.strip() for part in lines[index].strip().strip('|').split('|')]
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        flow_id = 'flow-%02d' % int(parts[0])
        if flow_id not in rows:
            continue
        lines[index] = '| %s | %s | %s |' % (parts[0], parts[1], rows[flow_id])
        replaced += 1
    if replaced != 15:
        raise ValueError('guide skill rows replaced: %d' % replaced)
    return '\n'.join(lines) + ('\n' if text.endswith('\n') else '')


def sync_guide(root=None):
    root = Path(root or DISTRIBUTION)
    data = load_combinations(root / 'tools/framework_core/workflows/combinations.json')
    path = root / 'docs/guide/from-zero-to-one.md'
    path.write_text(splice_guide(path.read_text(encoding='utf-8'), data['flows']), encoding='utf-8')


def _frontmatter(text):
    if not text.startswith('---\n'):
        return ''
    return text.split('---', 2)[1]


def _guide_mentions(text):
    found = {}
    inside = False
    for line in text.splitlines():
        if line.strip() == GUIDE_HEADING:
            inside = True
            continue
        if inside and line.startswith('## '):
            break
        if not inside:
            continue
        parts = [part.strip() for part in line.strip().strip('|').split('|')]
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        cell = parts[2]
        if cell == '无':
            names = []
        else:
            names = []
            cursor = 0
            while True:
                left = cell.find('`', cursor)
                if left < 0:
                    break
                right = cell.find('`', left + 1)
                if right < 0:
                    break
                names.append(cell[left + 1:right])
                cursor = right + 1
        found['flow-%02d' % int(parts[0])] = names
    return found


def _bare(name):
    return name.split(':')[-1].split('/')[-1]


def distribution_errors(root):
    """Falsifiable checks for routers, triggers, projections and the roster."""
    root = Path(root)
    errors = []
    combo_path = root / 'tools/framework_core/workflows/combinations.json'
    catalog_path = root / 'tools/framework_core/workflows/catalog.json'
    guide_path = root / 'docs/guide/from-zero-to-one.md'
    roster_path = root / 'tools/framework_core/hosts/roster.json'
    for path in (combo_path, catalog_path, guide_path, roster_path):
        if not path.is_file():
            errors.append('router source missing: ' + str(path.relative_to(root)))
    if errors:
        return errors
    data = json.loads(combo_path.read_text(encoding='utf-8'))
    flows = data['flows']
    ids = [flow['id'] for flow in flows]
    expected = ['flow-%02d' % number for number in range(1, 16)]
    if ids != expected:
        missing = [item for item in expected if item not in ids]
        errors.append('router set is not flow-01 to flow-15, missing: ' + ', '.join(missing))
    descriptions = {}
    for flow in flows:
        rendered = render_skill(flow)
        descriptions[flow['id']] = description_of(flow)
        skill = root / 'skill/flows' / flow['id'] / 'SKILL.md'
        if not skill.is_file():
            errors.append('missing router: ' + flow['id'])
            continue
        actual = skill.read_text(encoding='utf-8')
        if actual != rendered:
            errors.append('router body drifted from the combination manifest: ' + flow['id'])
        front = _frontmatter(actual)
        if 'disable-model-invocation: true' in front or 'allow_implicit_invocation: false' in front:
            errors.append('invocation form declared for one host only: ' + flow['id'])
        if len(description_of(flow)) > 1024:
            errors.append('description longer than 1024: ' + flow['id'])
        if actual.count('\n') > 500:
            errors.append('router longer than 500 lines: ' + flow['id'])
        if 'retro' in flow['mentions'] or '`retro`' in actual:
            errors.append('retro is in an automatic combination: ' + flow['id'])
    triggers = {flow['id']: flow['trigger'] for flow in flows}
    for left, trigger in triggers.items():
        for right, text in descriptions.items():
            if left != right and trigger in text:
                errors.append('shared trigger %s between %s and %s' % (trigger, left, right))
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    catalog_skills = {item['id']: [_bare(name) for name in item.get('skills', [])] for item in catalog['flows']}
    guide = _guide_mentions(guide_path.read_text(encoding='utf-8'))
    for flow in flows:
        wanted = list(flow['mentions'])
        if catalog_skills.get(flow['id']) != wanted:
            extra = sorted(set(catalog_skills.get(flow['id'], [])) - set(wanted))
            errors.append('catalog skills differ for %s: %s' % (flow['id'], ', '.join(extra) or 'missing'))
        guided = guide.get(flow['id'], [])
        if guided != wanted:
            extra = sorted(set(guided) - set(wanted))
            if extra:
                errors.append('guide lists a skill outside the combination for %s: %s' % (flow['id'], ', '.join(extra)))
            else:
                errors.append('guide skill column differs for %s' % flow['id'])
    roster = json.loads(roster_path.read_text(encoding='utf-8'))
    errors.extend(_roster_errors(root, roster))
    return errors


def _roster_errors(root, roster):
    errors = []
    hosts = roster.get('hosts') or []
    international = [item for item in hosts if item.get('region') == 'international']
    domestic = [item for item in hosts if item.get('region') == 'domestic']
    if len(international) != 8 or len(domestic) != 5:
        errors.append('roster is not eight international and five domestic hosts')
    allowed = {'DOCUMENTED', 'RECORDED', 'CARRIER_UNKNOWN'}
    for item in hosts:
        for field in ('discovery_evidence', 'hook_evidence'):
            if item.get(field) not in allowed:
                errors.append('invalid evidence grade for %s' % item.get('id'))
        if item.get('discovery_evidence') == 'CARRIER_UNKNOWN' and item.get('discovery_dir'):
            errors.append('%s evidence is CARRIER_UNKNOWN but a discovery path is set' % item['id'])
        if item.get('hook_evidence') == 'CARRIER_UNKNOWN' and item.get('hook_path'):
            errors.append('%s evidence is CARRIER_UNKNOWN but a hook path is set' % item['id'])
        discovery = item.get('discovery_dir')
        if not discovery or item.get('discovery_evidence') == 'CARRIER_UNKNOWN':
            continue
        directory = root / discovery
        if not directory.exists():
            continue
        for skill in directory.glob('*/SKILL.md'):
            name = skill.parent.name
            if name not in ['flow-%02d' % number for number in range(1, 16)]:
                errors.append('member skill projected into %s: %s' % (item['id'], name))
                continue
            canonical = root / 'skill/flows' / name / 'SKILL.md'
            if canonical.is_file() and skill.read_text(encoding='utf-8') != canonical.read_text(encoding='utf-8'):
                errors.append('projected router differs from skill/flows: ' + name)
    return errors
